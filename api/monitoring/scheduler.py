from __future__ import annotations

import asyncio
import os
from datetime import datetime, time, timedelta
from typing import Any

from .database import get_job, get_runtime_setting_value, has_job_template_placeholders, list_jobs, record_skipped_run, recover_stale_runs_and_locks, set_job_schedule_state
from .preflight import build_job_preflight
from .profile_promotion import cleanup_profile_promotion_artifacts
from .runner import clear_stop_request, request_stop_job, run_job


_scheduler_task: asyncio.Task | None = None
_apscheduler = None
_running_jobs: set[int] = set()
_job_tasks: dict[int, asyncio.Task] = {}


async def start_scheduler() -> None:
    global _scheduler_task, _apscheduler
    recover_stale_runs_and_locks("startup_recovery")
    if scheduler_disabled_reason():
        return
    tick_seconds = _scheduler_tick_seconds()
    if _apscheduler is not None:
        return
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        _apscheduler = AsyncIOScheduler()
        _apscheduler.add_job(tick, "interval", seconds=tick_seconds, id="monitor_tick", max_instances=1, coalesce=True)
        _apscheduler.start()
        await tick()
        return
    except Exception:
        _apscheduler = None

    if _scheduler_task and not _scheduler_task.done():
        return
    _scheduler_task = asyncio.create_task(_loop())


async def _loop() -> None:
    while True:
        try:
            await tick()
        except Exception:
            pass
        await asyncio.sleep(_scheduler_tick_seconds())


async def tick() -> None:
    recover_stale_runs_and_locks("scheduler_recovery")
    await asyncio.to_thread(cleanup_profile_promotion_artifacts)
    now = datetime.now()
    for job in list_jobs():
        if not job.get("enabled"):
            set_job_schedule_state(job["id"], None)
            continue
        if job["id"] in _running_jobs:
            continue
        set_job_schedule_state(job["id"], next_run_at(job, now))
        if not _is_due(job, now):
            continue
        if has_job_template_placeholders(job):
            record_skipped_run(job["id"], "请先把测试数据模板里的律所名称和平台搜索词改成真实内容", _skip_summary(job, "template_placeholders"))
            continue
        preflight = build_job_preflight(job, running_job_ids())
        if preflight["blockers"]:
            record_skipped_run(job["id"], "运行前检查未通过：" + "；".join(preflight["blockers"]), _skip_summary(job, "preflight_blocked", preflight))
            continue
        try:
            launch_job(job["id"], source="scheduler")
        except ValueError:
            continue


def launch_job(job_id: int, source: str = "manual") -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    if has_job_template_placeholders(job):
        raise ValueError("请先把测试数据模板里的律所名称和平台搜索词改成真实内容")
    if job_id in _running_jobs:
        return {"started": False, "status": "already_running", "job_id": job_id}
    clear_stop_request(job_id)
    _running_jobs.add(job_id)
    set_job_schedule_state(job_id, None)
    _job_tasks[job_id] = asyncio.create_task(_run_and_release(job_id, source=source))
    return {"started": True, "status": "queued", "job_id": job_id, "source": source}


def running_job_ids() -> list[int]:
    _cleanup_finished_job_tasks()
    return sorted(_running_jobs)


def running_jobs_detail() -> list[dict[str, Any]]:
    details = []
    for job_id in running_job_ids():
        job = get_job(job_id)
        task = _job_tasks.get(job_id)
        details.append(
            {
                "job_id": job_id,
                "law_firm_name": job.get("law_firm_name") if job else "",
                "job_deleted": not bool(job),
                "task_done": bool(task and task.done()),
                "task_cancelled": bool(task and task.cancelled()),
            }
        )
    return details


def stop_job(job_id: int) -> dict[str, Any]:
    _cleanup_finished_job_tasks()
    if job_id not in _running_jobs:
        return {"stopped": False, "status": "not_running", "job_id": job_id}
    process_count = request_stop_job(job_id)
    return {
        "stopped": True,
        "status": "stopping",
        "job_id": job_id,
        "terminated_processes": process_count,
    }


def scheduler_status() -> dict[str, Any]:
    disabled_reason = scheduler_disabled_reason()
    tick_seconds = _scheduler_tick_seconds()
    return {
        "enabled": not bool(disabled_reason),
        "mode": "disabled" if disabled_reason else "internal",
        "message": disabled_reason or f"内置调度器已启用，会每 {tick_seconds} 秒检查到期任务",
        "tick_seconds": tick_seconds,
        "running_job_ids": running_job_ids(),
        "running_jobs": running_jobs_detail(),
    }


def scheduler_disabled_reason() -> str:
    if _scheduler_disabled_setting():
        return "运行策略已暂停自动调度，内置调度器不会启动"
    workers = os.environ.get("WEB_CONCURRENCY") or os.environ.get("UVICORN_WORKERS")
    try:
        worker_count = int(workers) if workers else 1
    except ValueError:
        worker_count = 1
    if worker_count > 1:
        return "检测到多 worker 配置，MVP 内置调度器要求单进程"
    return ""


def _scheduler_tick_seconds() -> int:
    return max(10, _runtime_setting_int("scheduler_tick_seconds", 60))


def _scheduler_disabled_setting() -> bool:
    try:
        return bool(get_runtime_setting_value("scheduler_disabled"))
    except Exception:
        return os.environ.get("MONITOR_DISABLE_SCHEDULER", "").lower() in {"1", "true", "yes"}


def _runtime_setting_int(key: str, default: int) -> int:
    try:
        return int(get_runtime_setting_value(key))
    except Exception:
        env_map = {"scheduler_tick_seconds": "MONITOR_SCHEDULER_TICK_SECONDS"}
        env_value = os.environ.get(env_map.get(key, ""))
        try:
            return int(env_value) if env_value not in (None, "") else default
        except ValueError:
            return default


async def _run_and_release(job_id: int, source: str = "manual") -> None:
    try:
        await run_job(job_id, source=source)
    except Exception:
        # run_job already writes the failure into crawl_runs; keep background
        # tasks from leaking unhandled exceptions into the server loop.
        pass
    finally:
        _running_jobs.discard(job_id)
        _job_tasks.pop(job_id, None)
        job = get_job(job_id)
        if job and job.get("enabled"):
            set_job_schedule_state(job_id, next_run_at(job, datetime.now()))
        elif job:
            set_job_schedule_state(job_id, None)


def _cleanup_finished_job_tasks() -> None:
    for job_id, task in list(_job_tasks.items()):
        if task.done():
            _running_jobs.discard(job_id)
            _job_tasks.pop(job_id, None)


def _skip_summary(job: dict[str, Any], skip_type: str, preflight: dict[str, Any] | None = None) -> dict[str, Any]:
    summary = {
        "job_id": job.get("id"),
        "law_firm_name": job.get("law_firm_name") or "",
        "platforms": job.get("platforms", []),
        "keywords": job.get("keywords", []),
        "skip_type": skip_type,
        "source": "scheduler",
    }
    if preflight:
        summary["preflight"] = preflight
    return summary


def _is_due(job: dict, now: datetime) -> bool:
    frequency = job.get("frequency") or "daily"
    email_time = job.get("email_time") or "09:00"
    anchor = _today_anchor(now, email_time)
    last_run = job.get("last_run_at")
    parsed_last_run = _parse_last_run(last_run)
    if frequency == "6h":
        return _interval_due(parsed_last_run, now, anchor, timedelta(hours=6))
    if frequency == "12h":
        return _interval_due(parsed_last_run, now, anchor, timedelta(hours=12))
    if frequency == "cron":
        return _cron_due(job.get("cron_expr"), parsed_last_run, now, anchor)
    if parsed_last_run and parsed_last_run.astimezone().date() == now.date():
        return False
    return now >= anchor


def next_run_at(job: dict, now: datetime | None = None) -> str | None:
    if not job.get("enabled", True):
        return None
    now = now or datetime.now()
    frequency = job.get("frequency") or "daily"
    email_time = job.get("email_time") or "09:00"
    anchor = _today_anchor(now, email_time)
    last_run = _parse_last_run(job.get("last_run_at"))
    if frequency == "6h":
        return _next_interval_run(last_run, now, anchor, timedelta(hours=6)).isoformat()
    if frequency == "12h":
        return _next_interval_run(last_run, now, anchor, timedelta(hours=12)).isoformat()
    if frequency == "cron":
        return _next_cron_run(job.get("cron_expr"), last_run, now, anchor).isoformat()
    if last_run and _to_local_naive(last_run).date() == now.date():
        return (anchor + timedelta(days=1)).isoformat()
    if now < anchor:
        return anchor.isoformat()
    return now.isoformat()


def _interval_due(last_run: datetime | None, now: datetime, anchor: datetime, interval: timedelta) -> bool:
    if not last_run:
        return now >= anchor
    return now - last_run.astimezone().replace(tzinfo=None) >= interval


def _next_interval_run(last_run: datetime | None, now: datetime, anchor: datetime, interval: timedelta) -> datetime:
    if not last_run:
        return anchor if now < anchor else now
    candidate = _to_local_naive(last_run) + interval
    if candidate < anchor:
        candidate = anchor
    return candidate if candidate > now else now


def _cron_due(cron_expr: str | None, last_run: datetime | None, now: datetime, anchor: datetime) -> bool:
    if not cron_expr:
        return now >= anchor and (not last_run or last_run.astimezone().date() != now.date())
    try:
        from apscheduler.triggers.cron import CronTrigger

        trigger = CronTrigger.from_crontab(cron_expr)
        if last_run:
            previous = _to_local_naive(last_run)
            next_fire = trigger.get_next_fire_time(previous, previous)
        else:
            today_start = datetime.combine(now.date(), time.min)
            next_fire = trigger.get_next_fire_time(None, today_start)
        return bool(next_fire and _to_local_naive(next_fire) <= now)
    except Exception:
        return now >= anchor and (not last_run or last_run.astimezone().date() != now.date())


def _next_cron_run(cron_expr: str | None, last_run: datetime | None, now: datetime, anchor: datetime) -> datetime:
    if not cron_expr:
        if last_run and _to_local_naive(last_run).date() == now.date():
            return anchor + timedelta(days=1)
        return anchor if now < anchor else now
    try:
        from apscheduler.triggers.cron import CronTrigger

        trigger = CronTrigger.from_crontab(cron_expr)
        start = _to_local_naive(last_run) if last_run else now
        next_fire = trigger.get_next_fire_time(start, now)
        return _to_local_naive(next_fire) if next_fire else now
    except Exception:
        return anchor if now < anchor else now


def _today_anchor(now: datetime, email_time: str) -> datetime:
    try:
        hour, minute = [int(v) for v in email_time.split(":", 1)]
        anchor_time = time(hour=hour, minute=minute)
    except Exception:
        anchor_time = time(hour=9, minute=0)
    return datetime.combine(now.date(), anchor_time)


def _parse_last_run(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _to_local_naive(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone().replace(tzinfo=None)
    return value
