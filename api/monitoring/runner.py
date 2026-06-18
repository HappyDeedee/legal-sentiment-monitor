from __future__ import annotations

import asyncio
import json
import os
import subprocess
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .ai import (
    _build_trace_snapshot,
    _job_ai_config,
    evaluate_content,
)
from .database import (
    acquire_account_lock,
    acquire_proxy_lock,
    create_run,
    save_ai_evaluation_trace,
    finish_run,
    get_conn,
    get_job,
    get_platform_login_config,
    get_proxy_profile,
    get_runtime_setting_value,
    get_social_account,
    list_social_accounts,
    release_account_lock,
    release_proxy_locks,
    release_run_resource_locks,
    set_run_resource_bindings,
    update_run_summary,
    utc_now,
)
from .normalizer import (
    collect_platform_outputs,
    douyin_publish_time_type,
    in_time_window,
    normalize_comment,
    normalize_content,
)
from .platform_status import list_platform_status
from .reporting import create_report, send_report_with_delivery_log
from .security import MONITOR_DATA_DIR, redact_sensitive


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = MONITOR_DATA_DIR / "runs"
LOCKS_DIR = MONITOR_DATA_DIR / "locks"
GLOBAL_SEMAPHORES: dict[int, asyncio.Semaphore] = {}
PLATFORM_SEMAPHORES: dict[tuple[str, int], asyncio.Semaphore] = {}
PLATFORM_DEBUG_PORTS = {"dy": 9223, "ks": 9224, "xhs": 9225}
JOB_LOCK_TTL_SECONDS = int(os.environ.get("MONITOR_JOB_LOCK_TTL_SECONDS") or 21600)
DEFAULT_CRAWLER_MAX_RETRIES = 1
DEFAULT_CRAWLER_RETRY_DELAY_SECONDS = 3.0
DEFAULT_AI_ITEM_TIMEOUT_SECONDS = 120
DEFAULT_AI_ITEM_RETRY_COUNT = 1
CRAWLER_PROGRESS_POLL_SECONDS = 2.0
STOP_REQUESTS: set[int] = set()
RUN_PROCESSES: dict[int, set[subprocess.Popen]] = defaultdict(set)
PROCESS_LOCK = threading.Lock()


class CrawlerStopped(Exception):
    """Raised when an operator requests the current job to stop."""


class CrawlerTimedOut(Exception):
    """Raised when the run-level deadline is reached."""


def clear_stop_request(job_id: int) -> None:
    with PROCESS_LOCK:
        STOP_REQUESTS.discard(int(job_id))
        RUN_PROCESSES.pop(int(job_id), None)


def request_stop_job(job_id: int) -> int:
    job_id = int(job_id)
    with PROCESS_LOCK:
        STOP_REQUESTS.add(job_id)
        processes = list(RUN_PROCESSES.get(job_id, set()))
    stopped = 0
    for process in processes:
        if _terminate_process(process):
            stopped += 1
    return stopped


def is_stop_requested(job_id: int) -> bool:
    with PROCESS_LOCK:
        return int(job_id) in STOP_REQUESTS


def _runtime_setting_int(key: str, default: int) -> int:
    try:
        return int(get_runtime_setting_value(key))
    except Exception:
        env_map = {
            "crawler_timeout_seconds": "MONITOR_CRAWLER_TIMEOUT_SECONDS",
            "crawler_retry_count": "MONITOR_CRAWLER_MAX_RETRIES",
            "crawler_retry_delay_seconds": "MONITOR_CRAWLER_RETRY_DELAY_SECONDS",
            "ai_item_timeout_seconds": "MONITOR_AI_ITEM_TIMEOUT_SECONDS",
            "ai_item_retry_count": "MONITOR_AI_ITEM_RETRY_COUNT",
            "stale_run_heartbeat_grace_seconds": "MONITOR_STALE_RUN_HEARTBEAT_GRACE_SECONDS",
            "global_crawl_concurrency": "MONITOR_GLOBAL_CRAWL_CONCURRENCY",
            "lock_cleanup_buffer_seconds": "MONITOR_LOCK_CLEANUP_BUFFER_SECONDS",
            "per_platform_concurrency.dy": "MONITOR_PLATFORM_CONCURRENCY_DY",
            "per_platform_concurrency.xhs": "MONITOR_PLATFORM_CONCURRENCY_XHS",
            "per_platform_concurrency.ks": "MONITOR_PLATFORM_CONCURRENCY_KS",
        }
        env_value = os.environ.get(env_map.get(key, ""))
        try:
            return int(env_value) if env_value not in (None, "") else default
        except ValueError:
            return default


def _global_crawl_semaphore() -> asyncio.Semaphore:
    concurrency = max(1, _runtime_setting_int("global_crawl_concurrency", 2))
    if concurrency not in GLOBAL_SEMAPHORES:
        GLOBAL_SEMAPHORES[concurrency] = asyncio.Semaphore(concurrency)
    return GLOBAL_SEMAPHORES[concurrency]


def _platform_crawl_semaphore(platform: str) -> asyncio.Semaphore:
    key = f"per_platform_concurrency.{platform}"
    concurrency = max(1, _runtime_setting_int(key, 1))
    cache_key = (platform, concurrency)
    if cache_key not in PLATFORM_SEMAPHORES:
        PLATFORM_SEMAPHORES[cache_key] = asyncio.Semaphore(concurrency)
    return PLATFORM_SEMAPHORES[cache_key]


async def run_job(job_id: int, source: str = "manual") -> dict[str, Any]:
    lock_path = _acquire_job_lock(job_id)
    if lock_path is None:
        return {"run_id": None, "status": "already_running", "summary": {"job_id": job_id}, "report": None}
    try:
        return await _run_job_locked(job_id, source=source)
    finally:
        _release_job_lock(lock_path)
        clear_stop_request(job_id)


async def _run_job_locked(job_id: int, source: str = "manual") -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    summary: dict[str, Any] = {
        "job_id": job_id,
        "law_firm_name": job.get("law_firm_name") or "",
        "platforms": job.get("platforms", []),
        "keywords": job.get("keywords", []),
        "recipients": job.get("recipients", []),
        "raw_contents": 0,
        "filtered_contents": 0,
        "excluded_contents": 0,
        "new_contents": 0,
        "negative_count": 0,
        "high_count": 0,
        "pending_review_count": 0,
        "failed_platforms": [],
        "cancelled_platforms": [],
        "platform_results": {},
        "source": source,
        "phase_7_1_lifecycle": True,
    }
    timeout_seconds = _runtime_setting_int("crawler_timeout_seconds", 900)
    started_at = datetime.now(timezone.utc)
    deadline_at = started_at + timedelta(seconds=timeout_seconds)
    summary["timeout_seconds"] = timeout_seconds
    summary["deadline_at"] = deadline_at.isoformat()
    run_id = create_run(job_id, summary, timeout_seconds=timeout_seconds)
    run_dir = RUNS_DIR / f"job_{job_id}" / f"run_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary["run_dir"] = str(run_dir)
    _mark_phase(run_id, summary, "preparing", last_safe_result={"job_id": job_id, "source": source})
    try:
        _raise_if_stop_requested(job_id)
        _mark_phase(run_id, summary, "collecting", last_safe_result={"platforms": job.get("platforms", [])})
        tasks = [run_platform(job, run_id, platform, run_dir) for platform in job.get("platforms", [])]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        content_ids_for_eval: list[int] = []
        stopped = is_stop_requested(job_id)
        timed_out = False
        timeout_reason = ""
        for platform, result in zip(job.get("platforms", []), results):
            if isinstance(result, CrawlerStopped):
                stopped = True
                summary["cancelled_platforms"].append(platform)
                summary["platform_results"][platform] = {"status": "cancelled", "error": redact_sensitive(str(result))}
                continue
            if isinstance(result, CrawlerTimedOut):
                error = redact_sensitive(str(result))
                timed_out = True
                timeout_reason = timeout_reason or error
                summary["failed_platforms"].append(platform)
                summary["platform_results"][platform] = {"status": "timeout", "error": error}
                continue
            if isinstance(result, Exception):
                error = redact_sensitive(str(result))
                summary["failed_platforms"].append(platform)
                summary["platform_results"][platform] = {"status": "failed", "error": error}
                continue
            summary["platform_results"][platform] = result
            summary["raw_contents"] += result.get("raw_contents", 0)
            summary["filtered_contents"] += result.get("filtered_contents", 0)
            summary["excluded_contents"] += result.get("excluded_contents", 0)
            summary["new_contents"] += result.get("new_contents", 0)
            content_ids_for_eval.extend(result.get("content_db_ids", []))
        _sync_progress_from_stored_summary(run_id, summary, finalize=not timed_out and not stopped)
        _mark_phase(run_id, summary, "collected", last_safe_result={"new_contents": summary["new_contents"], "failed_platforms": summary["failed_platforms"]})

        if timed_out:
            raise CrawlerTimedOut(timeout_reason or _timeout_message(run_id))

        if stopped:
            summary["cancelled"] = True
            summary["duration_seconds"] = _run_duration_seconds(run_id)
            finish_run(run_id, "cancelled", summary, "任务已手动停止")
            _touch_job_last_run(job_id)
            return {"run_id": run_id, "status": "cancelled", "summary": summary, "report": None}

        _raise_if_stop_requested(job_id)
        _raise_if_deadline_passed(run_id)
        _mark_phase(run_id, summary, "ai_evaluating", last_safe_result={"total_candidates": len(content_ids_for_eval)})
        eval_summary = await evaluate_new_contents(job, run_id, content_ids_for_eval)
        summary.update(eval_summary)
        _raise_if_stop_requested(job_id)
        _raise_if_deadline_passed(run_id)
        _mark_phase(run_id, summary, "report_generating", last_safe_result={"ai_progress": summary.get("ai_progress")})
        report = create_report(run_id, job, summary)
        _mark_phase(run_id, summary, "email_sending", last_safe_result={"report_id": report.get("id")})
        ok, error, refreshed_report, delivery_log = send_report_with_delivery_log(job, report, send_type="auto")
        error = redact_sensitive(error)
        report = refreshed_report
        summary["email_status"] = report.get("email_status") or ("sent" if ok else "failed")
        if delivery_log:
            summary["email_delivery_log_id"] = delivery_log.get("id")
            summary["email_send_window_key"] = delivery_log.get("send_window_key")
        if error:
            summary["email_error"] = error
        final_status = "partial_failed" if summary["failed_platforms"] else "success"
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        _mark_phase(run_id, summary, f"terminal:{final_status}", persist=False)
        finish_run(run_id, final_status, summary)
        _touch_job_last_run(job_id)
        return {"run_id": run_id, "status": final_status, "summary": summary, "report": report}
    except CrawlerStopped as exc:
        summary["cancelled"] = True
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        _mark_phase(run_id, summary, "terminal:cancelled", last_error=str(exc), persist=False)
        finish_run(run_id, "cancelled", summary, redact_sensitive(str(exc)))
        _touch_job_last_run(job_id)
        return {"run_id": run_id, "status": "cancelled", "summary": summary, "report": None}
    except CrawlerTimedOut as exc:
        summary["timeout"] = True
        summary["timeout_reason"] = redact_sensitive(str(exc))
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        report = None
        try:
            _apply_unresolved_ai_fallback_summary(run_id, summary, content_ids_for_eval, "timeout")
            _mark_phase(run_id, summary, "report_generating_after_timeout", last_safe_result={"new_contents": summary.get("new_contents", 0)})
            report = create_report(run_id, job, summary)
            _mark_phase(run_id, summary, "email_sending_after_timeout", last_safe_result={"report_id": report.get("id")})
            ok, error, refreshed_report, delivery_log = send_report_with_delivery_log(job, report, send_type="auto")
            error = redact_sensitive(error)
            report = refreshed_report
            summary["email_status"] = report.get("email_status") or ("sent" if ok else "failed")
            if delivery_log:
                summary["email_delivery_log_id"] = delivery_log.get("id")
                summary["email_send_window_key"] = delivery_log.get("send_window_key")
            if error:
                summary["email_error"] = error
        except Exception as report_exc:
            summary["email_status"] = "failed"
            summary["email_error"] = redact_sensitive(f"超时后报告生成或发送失败：{type(report_exc).__name__}")
            _mark_phase(run_id, summary, "timeout_report_failed", last_error=f"{type(report_exc).__name__}: {report_exc}", persist=False)
        _mark_phase(run_id, summary, "terminal:timeout", persist=False)
        finish_run(run_id, "timeout", summary, summary["timeout_reason"], summary["timeout_reason"])
        _touch_job_last_run(job_id)
        return {"run_id": run_id, "status": "timeout", "summary": summary, "report": report}
    except asyncio.CancelledError:
        request_stop_job(job_id)
        summary["cancelled"] = True
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        _mark_phase(run_id, summary, "terminal:cancelled", last_error="asyncio.CancelledError", persist=False)
        finish_run(run_id, "cancelled", summary, "任务已取消")
        _touch_job_last_run(job_id)
        raise
    except Exception as exc:
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        report = None
        if _safe_int(summary.get("new_contents")):
            try:
                _apply_unresolved_ai_fallback_summary(run_id, summary, content_ids_for_eval, "partial_failure")
                _mark_phase(run_id, summary, "report_generating_after_failure", last_error=f"{type(exc).__name__}: {exc}")
                report = create_report(run_id, job, summary)
                _mark_phase(run_id, summary, "email_sending_after_failure", last_safe_result={"report_id": report.get("id")})
                ok, error, refreshed_report, delivery_log = send_report_with_delivery_log(job, report, send_type="auto")
                error = redact_sensitive(error)
                report = refreshed_report
                summary["email_status"] = report.get("email_status") or ("sent" if ok else "failed")
                if delivery_log:
                    summary["email_delivery_log_id"] = delivery_log.get("id")
                    summary["email_send_window_key"] = delivery_log.get("send_window_key")
                if error:
                    summary["email_error"] = error
                _mark_phase(run_id, summary, "terminal:partial_failed", last_error=f"{type(exc).__name__}: {exc}", persist=False)
                finish_run(run_id, "partial_failed", summary, f"{type(exc).__name__}: {redact_sensitive(str(exc))}")
                _touch_job_last_run(job_id)
                return {"run_id": run_id, "status": "partial_failed", "summary": summary, "report": report}
            except Exception as report_exc:
                summary["report_error"] = redact_sensitive(f"{type(report_exc).__name__}: {report_exc}")
        _mark_phase(run_id, summary, "terminal:failed", last_error=f"{type(exc).__name__}: {exc}", persist=False)
        finish_run(run_id, "failed", summary, f"{type(exc).__name__}: {redact_sensitive(str(exc))}")
        _touch_job_last_run(job_id)
        raise
    finally:
        release_run_resource_locks(run_id)


async def run_platform(job: dict[str, Any], run_id: int, platform: str, run_dir: Path) -> dict[str, Any]:
    _raise_if_stop_requested(job["id"])
    _raise_if_deadline_passed(run_id)
    async with _global_crawl_semaphore():
        async with _platform_crawl_semaphore(platform):
            _raise_if_stop_requested(job["id"])
            _raise_if_deadline_passed(run_id)
            _ensure_login_window_closed(platform)
            account_binding = _resolve_platform_account_binding(platform, job)
            lock_expires_at = _lock_expires_at(run_id)
            account_lock_acquired = False
            proxy_lock_acquired = False
            platform_root = run_dir / platform
            platform_root.mkdir(parents=True, exist_ok=True)
            max_retries = _crawler_max_retries()
            total_attempts = max_retries + 1
            last_error = ""
            try:
                if account_binding and account_binding.get("account_id"):
                    account_lock_acquired = acquire_account_lock(int(account_binding["account_id"]), run_id, lock_expires_at)
                    if not account_lock_acquired:
                        raise RuntimeError("账号网页登录态正在被其他任务使用，请等待本轮结束后重试")
                else:
                    account_lock_acquired = True
                if account_binding and account_binding.get("proxy_id"):
                    proxy_lock_acquired = acquire_proxy_lock(
                        int(account_binding["proxy_id"]),
                        run_id,
                        lock_expires_at,
                        _safe_int(job.get("workspace_id")),
                    )
                    if not proxy_lock_acquired:
                        raise RuntimeError("代理资源已达到并发上限，请等待其他任务结束后重试")
                else:
                    proxy_lock_acquired = True
                if account_binding:
                    set_run_resource_bindings(
                        run_id,
                        _safe_int(account_binding.get("account_id")),
                        _safe_int(account_binding.get("proxy_id")),
                    )
                for attempt in range(1, total_attempts + 1):
                    attempt_out = _attempt_output_dir(platform_root, attempt, total_attempts)
                    attempt_out.mkdir(parents=True, exist_ok=True)
                    try:
                        _raise_if_stop_requested(job["id"])
                        attempt_timeout = _remaining_run_seconds(run_id)
                        attempt_job = {**job, "_crawler_timeout_seconds": attempt_timeout, "_run_id": run_id}
                        _update_collection_progress(run_id, platform, attempt_out, phase="collecting")
                        await asyncio.to_thread(_run_crawler_attempt, attempt_job, platform, attempt_out, account_binding)
                        _raise_if_stop_requested(job["id"])
                        _raise_if_deadline_passed(run_id)
                        _update_collection_progress(run_id, platform, attempt_out, phase="ingesting")
                        contents, comments = collect_platform_outputs(attempt_out, platform)
                        result = ingest_outputs(job, run_id, platform, contents, comments)
                        _finalize_collection_progress(run_id, platform, result)
                        result["attempts"] = attempt
                        result["max_retries"] = max_retries
                        result["timeout_seconds"] = _run_timeout_seconds(run_id)
                        result["deadline_at"] = _run_deadline_at(run_id)
                        if account_binding:
                            result["account"] = _account_summary(account_binding)
                        if account_binding and account_binding.get("proxy_id"):
                            result["proxy"] = _proxy_summary(account_binding)
                        return result
                    except CrawlerStopped as exc:
                        _update_collection_progress(run_id, platform, attempt_out, phase="collecting", error=str(exc))
                        raise
                    except CrawlerTimedOut as exc:
                        _update_collection_progress(run_id, platform, attempt_out, phase="collecting", error=str(exc))
                        raise
                    except RuntimeError as exc:
                        last_error = redact_sensitive(str(exc))
                        _update_collection_progress(run_id, platform, attempt_out, phase="collecting", error=last_error)
                        if not _should_retry_crawler_error(last_error) or attempt >= total_attempts:
                            break
                        _raise_if_stop_requested(job["id"])
                        _raise_if_deadline_passed(run_id)
                        await asyncio.sleep(_crawler_retry_delay_seconds())
                        _raise_if_deadline_passed(run_id)
                raise RuntimeError(f"MediaCrawler failed after {attempt} attempt(s): {last_error}")
            finally:
                if account_binding and account_binding.get("account_id") and account_lock_acquired:
                    release_account_lock(int(account_binding["account_id"]), run_id)
                if account_binding and account_binding.get("proxy_id") and proxy_lock_acquired:
                    release_proxy_locks(run_id, int(account_binding["proxy_id"]))


def _run_crawler_attempt(
    job: dict[str, Any],
    platform: str,
    out_dir: Path,
    account_binding: dict[str, Any] | None = None,
) -> None:
    _raise_if_stop_requested(job["id"])
    run_id = _safe_int(job.get("_run_id"))
    cmd = _build_crawler_cmd(job, platform, out_dir, account_binding)
    env = _build_crawler_env(account_binding)
    log_path = out_dir / "crawler.log"
    timeout_seconds = max(1, _safe_int(job.get("_crawler_timeout_seconds")) or _runtime_setting_int("crawler_timeout_seconds", 900))
    process: subprocess.Popen | None = None
    try:
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        log_lines = [redact_sensitive("Starting crawler: " + " ".join(cmd))]
        if account_binding and account_binding.get("profile_path"):
            log_lines.append(
                "[monitor] Account profile enabled: "
                + redact_sensitive(f"{account_binding.get('account_name') or '-'} {account_binding.get('profile_key') or ''}")
            )
        if account_binding and account_binding.get("proxy_id"):
            log_lines.append(
                "[monitor] Proxy enabled: "
                + redact_sensitive(
                    f"{account_binding.get('proxy_name') or '-'} "
                    f"({account_binding.get('provider') or '-'}) "
                    f"{account_binding.get('proxy_url') or ''}"
                )
            )
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8", errors="ignore")
        with log_path.open("a", encoding="utf-8", errors="ignore") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
            _register_process(job["id"], process)
            deadline = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)
            while True:
                _raise_if_stop_requested(job["id"])
                try:
                    process.wait(timeout=CRAWLER_PROGRESS_POLL_SECONDS if run_id else timeout_seconds)
                    break
                except subprocess.TimeoutExpired as exc:
                    if run_id:
                        _update_collection_progress(run_id, platform, out_dir, phase="collecting")
                    if datetime.now(timezone.utc) < deadline:
                        continue
                    _terminate_process(process)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        pass
                    log_file.write(f"\n[monitor] MediaCrawler timed out after {timeout_seconds}s\n")
                    log_file.flush()
                    if run_id:
                        _update_collection_progress(
                            run_id,
                            platform,
                            out_dir,
                            phase="collecting",
                            error=f"timeout after {timeout_seconds}s",
                        )
                    raise CrawlerTimedOut(f"任务达到系统运行时间上限，已停止未完成的采集进程；see {log_path}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CrawlerTimedOut(f"任务达到系统运行时间上限，已停止未完成的采集进程；see {log_path}") from exc
    except RuntimeError:
        raise
    except Exception as exc:
        if isinstance(exc, (CrawlerStopped, CrawlerTimedOut)):
            raise
        safe_error = redact_sensitive(f"{type(exc).__name__}: {exc}")
        log_path.write_text(safe_error, encoding="utf-8", errors="ignore")
        raise RuntimeError(f"MediaCrawler failed to start: {safe_error}; see {log_path}") from exc
    finally:
        if process:
            _unregister_process(job["id"], process)
    raw_log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    log_text = redact_sensitive(raw_log_text)
    if log_text != raw_log_text:
        log_path.write_text(log_text, encoding="utf-8", errors="ignore")
    if is_stop_requested(job["id"]):
        if run_id:
            _update_collection_progress(run_id, platform, out_dir, phase="collecting", error="stopped")
        raise CrawlerStopped(f"任务已手动停止；see {log_path}")
    if process.returncode != 0:
        hint = "；检测到登录态失效，请先重新登录该平台账号" if _looks_like_login_required(log_text) else ""
        if run_id:
            _update_collection_progress(run_id, platform, out_dir, phase="collecting", error=f"exit {process.returncode}")
        raise RuntimeError(f"MediaCrawler exited with {process.returncode}{hint}; see {log_path}")


def _ensure_login_window_closed(platform: str) -> None:
    statuses = {item["platform"]: item for item in list_platform_status()}
    status = statuses.get(platform) or {}
    if status.get("login_window_open"):
        label = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}.get(platform, platform)
        raise RuntimeError(f"{label}登录窗口未关闭，请关闭窗口后再运行采集")


def _update_collection_progress(
    run_id: int,
    platform: str,
    out_dir: Path,
    *,
    phase: str,
    error: str | None = None,
) -> dict[str, Any]:
    snapshot = _collection_progress_snapshot(platform, out_dir)
    if error:
        snapshot["last_error"] = redact_sensitive(error)
    snapshot["updated_at"] = utc_now()
    with get_conn() as conn:
        row = conn.execute("SELECT summary FROM crawl_runs WHERE id=? AND status='running'", (run_id,)).fetchone()
        if not row:
            return {}
        try:
            summary = json.loads(row["summary"] or "{}")
        except (TypeError, ValueError):
            summary = {}
        if not isinstance(summary, dict):
            summary = {}
        collection_progress = summary.get("collection_progress") if isinstance(summary.get("collection_progress"), dict) else {}
        platforms = collection_progress.get("platforms") if isinstance(collection_progress.get("platforms"), dict) else {}
        previous = platforms.get(platform) if isinstance(platforms.get(platform), dict) else {}
        if (_safe_int(snapshot.get("raw_items_seen")) or 0) < (_safe_int(previous.get("raw_items_seen")) or 0):
            snapshot["raw_items_seen"] = _safe_int(previous.get("raw_items_seen")) or 0
        if (_safe_int(snapshot.get("comment_items_seen")) or 0) < (_safe_int(previous.get("comment_items_seen")) or 0):
            snapshot["comment_items_seen"] = _safe_int(previous.get("comment_items_seen")) or 0
        if (_safe_int(snapshot.get("files_seen")) or 0) < (_safe_int(previous.get("files_seen")) or 0):
            snapshot["files_seen"] = _safe_int(previous.get("files_seen")) or 0
        platforms[platform] = snapshot
        total_raw = sum(_safe_int(item.get("raw_items_seen")) or 0 for item in platforms.values() if isinstance(item, dict))
        total_comments = sum(_safe_int(item.get("comment_items_seen")) or 0 for item in platforms.values() if isinstance(item, dict))
        malformed = sum(_safe_int(item.get("malformed_files")) or 0 for item in platforms.values() if isinstance(item, dict))
        now = utc_now()
        summary.update(
            {
                "phase_19b_progress": True,
                "phase": phase,
                "progress_updated_at": now,
                "progress_message": f"{platform} 临时采集进度：已观察到 {total_raw} 条内容输出",
                "collection_progress": {
                    "provisional": True,
                    "final": False,
                    "raw_items_seen": total_raw,
                    "comment_items_seen": total_comments,
                    "malformed_files": malformed,
                    "updated_at": now,
                    "platforms": platforms,
                },
            }
        )
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_summary(summary), ensure_ascii=False), run_id),
        )
    return summary


def _finalize_collection_progress(run_id: int, platform: str, result: dict[str, Any]) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT summary FROM crawl_runs WHERE id=? AND status='running'", (run_id,)).fetchone()
        if not row:
            return {}
        try:
            summary = json.loads(row["summary"] or "{}")
        except (TypeError, ValueError):
            summary = {}
        if not isinstance(summary, dict):
            summary = {}
        collection_progress = summary.get("collection_progress") if isinstance(summary.get("collection_progress"), dict) else {}
        platforms = collection_progress.get("platforms") if isinstance(collection_progress.get("platforms"), dict) else {}
        previous = platforms.get(platform) if isinstance(platforms.get(platform), dict) else {}
        finalized = {
            **previous,
            "platform": platform,
            "provisional": False,
            "final": True,
            "final_raw_contents": _safe_int(result.get("raw_contents")) or 0,
            "final_filtered_contents": _safe_int(result.get("filtered_contents")) or 0,
            "final_excluded_contents": _safe_int(result.get("excluded_contents")) or 0,
            "final_new_contents": _safe_int(result.get("new_contents")) or 0,
            "updated_at": utc_now(),
        }
        platforms[platform] = finalized
        summary["collection_progress"] = {
            **collection_progress,
            "provisional": True,
            "final": False,
            "platforms": platforms,
            "updated_at": finalized["updated_at"],
        }
        summary["progress_updated_at"] = finalized["updated_at"]
        summary["progress_message"] = f"{platform} 已完成入库统计：新增 {finalized['final_new_contents']} 条"
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_summary(summary), ensure_ascii=False), run_id),
        )
    return summary


def _sync_progress_from_stored_summary(run_id: int, summary: dict[str, Any], *, finalize: bool = False) -> None:
    with get_conn() as conn:
        row = conn.execute("SELECT summary FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    if not row:
        return
    try:
        stored = json.loads(row["summary"] or "{}")
    except (TypeError, ValueError):
        stored = {}
    if not isinstance(stored, dict):
        return
    for key in ("collection_progress", "progress_message", "progress_updated_at", "phase_19b_progress"):
        if key in stored:
            summary[key] = stored[key]
    progress = summary.get("collection_progress")
    if isinstance(progress, dict):
        if not finalize:
            return
        progress["provisional"] = False
        progress["final"] = True
        progress["final_raw_contents"] = _safe_int(summary.get("raw_contents")) or 0
        progress["final_filtered_contents"] = _safe_int(summary.get("filtered_contents")) or 0
        progress["final_excluded_contents"] = _safe_int(summary.get("excluded_contents")) or 0
        progress["final_new_contents"] = _safe_int(summary.get("new_contents")) or 0
        progress["updated_at"] = utc_now()
        for item in (progress.get("platforms") or {}).values():
            if isinstance(item, dict) and item.get("final"):
                continue
            if isinstance(item, dict):
                item["provisional"] = False
        summary["collection_progress"] = progress


def _collection_progress_snapshot(platform: str, out_dir: Path) -> dict[str, Any]:
    contents, content_errors = _safe_collect_progress_items(out_dir, platform, "contents")
    comments, comment_errors = _safe_collect_progress_items(out_dir, platform, "comments")
    return {
        "platform": platform,
        "provisional": True,
        "final": False,
        "raw_items_seen": len(contents),
        "comment_items_seen": len(comments),
        "files_seen": content_errors["files_seen"] + comment_errors["files_seen"],
        "empty_files": content_errors["empty_files"] + comment_errors["empty_files"],
        "malformed_files": content_errors["malformed_files"] + comment_errors["malformed_files"],
        "missing_output": content_errors["files_seen"] + comment_errors["files_seen"] == 0,
    }


def _safe_collect_progress_items(out_dir: Path, platform: str, item_type: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    output_names = [platform]
    canonical = {"dy": "douyin", "ks": "kuaishou", "xhs": "xhs"}.get(platform)
    if canonical and canonical not in output_names:
        output_names.insert(0, canonical)
    candidate_roots = []
    for name in output_names:
        candidate_roots.append(out_dir / name)
    candidate_roots.append(out_dir)
    patterns = [
        ("json", f"*_{item_type}_*.json"),
        ("jsonl", f"*_{item_type}_*.jsonl"),
    ]
    items: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    stats = {"files_seen": 0, "empty_files": 0, "malformed_files": 0}
    for root in candidate_roots:
        for folder, pattern in patterns:
            target_dir = root / folder
            if not target_dir.exists():
                continue
            for path in target_dir.glob(pattern):
                stats["files_seen"] += 1
                try:
                    if path.stat().st_size == 0:
                        stats["empty_files"] += 1
                        continue
                except OSError:
                    stats["malformed_files"] += 1
                    continue
                parsed, malformed = _read_progress_file(path, folder)
                if malformed:
                    stats["malformed_files"] += 1
                if not parsed:
                    continue
                for item in parsed:
                    key = _progress_item_key(item_type, platform, item)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    items.append(item)
    return items, stats


def _read_progress_file(path: Path, folder: str) -> tuple[list[dict[str, Any]], bool]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return [], True
    if not text.strip():
        return [], False
    if folder == "jsonl":
        items: list[dict[str, Any]] = []
        malformed = False
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                malformed = True
                continue
            if isinstance(data, dict):
                items.append(data)
            else:
                malformed = True
        return items, malformed
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [], True
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)], False
    if isinstance(data, dict):
        return [data], False
    return [], True


def _progress_item_key(item_type: str, platform: str, item: dict[str, Any]) -> str:
    if item_type == "comments":
        key = item.get("comment_id") or item.get("cid") or item.get("id")
    elif platform == "dy":
        key = item.get("aweme_id") or item.get("content_id") or item.get("id")
    elif platform == "ks":
        key = item.get("video_id") or item.get("content_id") or item.get("id")
    elif platform == "xhs":
        key = item.get("note_id") or item.get("content_id") or item.get("id")
    else:
        key = item.get("content_id") or item.get("id")
    if key:
        return f"{item_type}:{platform}:{key}"
    return f"{item_type}:{platform}:{json.dumps(item, ensure_ascii=False, sort_keys=True)[:500]}"


def ingest_outputs(
    job: dict[str, Any],
    run_id: int,
    platform: str,
    contents: list[dict[str, Any]],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized_contents = [c for c in (normalize_content(platform, item, job) for item in contents) if c]
    time_filtered_contents = [c for c in normalized_contents if in_time_window(c, job)]
    filtered_contents = [c for c in time_filtered_contents if not _matches_exclude_words(c, job)]
    normalized_comments = [c for c in (normalize_comment(platform, item) for item in comments) if c]
    content_db_ids: list[int] = []
    now = utc_now()
    with get_conn() as conn:
        for item in filtered_contents:
            existing = conn.execute(
                "SELECT id FROM raw_contents WHERE job_id=? AND platform=? AND content_id=?",
                (job["id"], item["platform"], item["content_id"]),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE raw_contents SET last_seen_at=? WHERE id=?",
                    (now, existing["id"]),
                )
                continue
            cur = conn.execute(
                """
                INSERT INTO raw_contents (
                    workspace_id, platform, content_id, job_id, run_id, law_firm_name, source_keyword, title,
                    description, author_name, content_url, cover_url, publish_time, comment_count,
                    raw_json, first_seen_at, last_seen_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(job.get("workspace_id") or 1),
                    item["platform"],
                    item["content_id"],
                    job["id"],
                    run_id,
                    item["law_firm_name"],
                    item["source_keyword"],
                    item["title"],
                    item["description"],
                    item["author_name"],
                    item["content_url"],
                    item["cover_url"],
                    item["publish_time"],
                    item["comment_count"],
                    item["raw_json"],
                    now,
                    now,
                    job.get("created_by"),
                    job.get("created_by"),
                ),
            )
            content_db_ids.append(int(cur.lastrowid))
        for comment in normalized_comments:
            conn.execute(
                """
                INSERT OR IGNORE INTO raw_comments (
                    workspace_id, platform, comment_id, content_id, content, author_name, create_time,
                    raw_json, first_seen_at, created_by, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    int(job.get("workspace_id") or 1),
                    comment["platform"],
                    comment["comment_id"],
                    comment["content_id"],
                    comment["content"],
                    comment["author_name"],
                    comment["create_time"],
                    comment["raw_json"],
                    now,
                    job.get("created_by"),
                    job.get("created_by"),
                ),
            )
    return {
        "status": "success",
        "raw_contents": len(normalized_contents),
        "filtered_contents": len(filtered_contents),
        "excluded_contents": len(time_filtered_contents) - len(filtered_contents),
        "new_contents": len(content_db_ids),
        "content_db_ids": content_db_ids,
    }


async def evaluate_new_contents(job: dict[str, Any], run_id: int, content_ids: list[int]) -> dict[str, Any]:
    negative_count = 0
    high_count = 0
    pending_review_count = 0
    successful_count = 0
    fallback_count = 0
    unresolved_count = 0
    with get_conn() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM raw_contents WHERE id IN (%s)" % ",".join("?" for _ in content_ids),
                content_ids,
            ).fetchall()
        ] if content_ids else []
    ai_progress = {
        "total_candidates": len(rows),
        "successful_evaluations": 0,
        "failed_fallback_evaluations": 0,
        "pending_review_items": 0,
        "manual_review_count": 0,
        "negative_count": 0,
        "high_count": 0,
        "unresolved_items": len(rows),
        "evaluated_items": 0,
        "final": False,
    }
    _merge_ai_progress_summary(
        run_id,
        ai_progress,
        negative_count=negative_count,
        high_count=high_count,
        pending_review_count=pending_review_count,
    )
    for index, row in enumerate(rows, start=1):
        _raise_if_stop_requested(int(job.get("id") or 0))
        _raise_if_deadline_passed(run_id)
        comments = _load_comments(row["platform"], row["content_id"])
        evaluation = await _evaluate_content_with_fallback(job, run_id, row, comments)
        if evaluation["status"] == "pending_review":
            pending_review_count += 1
            fallback_count += 1
        else:
            successful_count += 1
        is_related_negative = bool(
            evaluation["status"] != "pending_review"
            and evaluation["is_related"]
            and evaluation["is_negative"]
        )
        if is_related_negative:
            negative_count += 1
        if is_related_negative and evaluation["risk_level"] == "high":
            high_count += 1
        _save_evaluation(row["id"], run_id, evaluation)
        unresolved_count = max(0, len(rows) - index)
        ai_progress = {
            "total_candidates": len(rows),
            "successful_evaluations": successful_count,
            "failed_fallback_evaluations": fallback_count,
            "pending_review_items": pending_review_count,
            "manual_review_count": pending_review_count,
            "negative_count": negative_count,
            "high_count": high_count,
            "unresolved_items": unresolved_count,
            "evaluated_items": index,
            "final": False,
        }
        _merge_ai_progress_summary(
            run_id,
            ai_progress,
            negative_count=negative_count,
            high_count=high_count,
            pending_review_count=pending_review_count,
            last_content_id=row.get("content_id"),
        )
    final_progress = {
        "total_candidates": len(rows),
        "successful_evaluations": successful_count,
        "failed_fallback_evaluations": fallback_count,
        "pending_review_items": pending_review_count,
        "manual_review_count": pending_review_count,
        "negative_count": negative_count,
        "high_count": high_count,
        "unresolved_items": unresolved_count,
        "evaluated_items": len(rows),
        "final": True,
    }
    _merge_ai_progress_summary(
        run_id,
        final_progress,
        negative_count=negative_count,
        high_count=high_count,
        pending_review_count=pending_review_count,
        final=True,
    )
    return {
        "negative_count": negative_count,
        "high_count": high_count,
        "pending_review_count": pending_review_count,
        "ai_total_candidates": len(rows),
        "ai_successful_evaluations": successful_count,
        "ai_failed_fallback_evaluations": fallback_count,
        "ai_pending_review_items": pending_review_count,
        "ai_unresolved_items": unresolved_count,
        "ai_progress": final_progress,
        "ai_progress_final": True,
    }


AI_PROGRESS_COUNT_KEYS = {
    "total_candidates",
    "successful_evaluations",
    "failed_fallback_evaluations",
    "pending_review_items",
    "manual_review_count",
    "negative_count",
    "high_count",
    "evaluated_items",
    "limited_context_items",
}


def _merge_ai_progress_summary(
    run_id: int,
    progress: dict[str, Any],
    *,
    negative_count: int | None = None,
    high_count: int | None = None,
    pending_review_count: int | None = None,
    last_content_id: Any | None = None,
    final: bool = False,
) -> dict[str, Any]:
    now = utc_now()
    with get_conn() as conn:
        row = conn.execute("SELECT summary FROM crawl_runs WHERE id=? AND status='running'", (run_id,)).fetchone()
        if not row:
            return {}
        try:
            summary = json.loads(row["summary"] or "{}")
        except (TypeError, ValueError):
            summary = {}
        if not isinstance(summary, dict):
            summary = {}
        existing = summary.get("ai_progress") if isinstance(summary.get("ai_progress"), dict) else {}
        if summary.get("ai_progress_final") or existing.get("final"):
            return summary
        merged_progress = _monotonic_ai_progress(existing, progress, final=final)
        summary.update(
            {
                "phase_7_1_lifecycle": True,
                "phase_19c_progress": True,
                "phase": "ai_evaluating",
                "progress_updated_at": now,
                "progress_message": _ai_progress_message(merged_progress),
                "ai_progress": merged_progress,
            }
        )
        if last_content_id is not None:
            summary["last_safe_result"] = _redact_summary({"content_id": last_content_id, "ai_progress": merged_progress})
        if negative_count is not None:
            summary["negative_count"] = int(negative_count or 0)
        if high_count is not None:
            summary["high_count"] = int(high_count or 0)
        if pending_review_count is not None:
            summary["pending_review_count"] = int(pending_review_count or 0)
        if final:
            summary["ai_progress_final"] = True
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_summary(summary), ensure_ascii=False), run_id),
        )
    return summary


def _monotonic_ai_progress(existing: dict[str, Any], progress: dict[str, Any], *, final: bool) -> dict[str, Any]:
    merged = dict(progress or {})
    if final:
        merged["final"] = True
        return merged
    for key in AI_PROGRESS_COUNT_KEYS:
        incoming = _safe_int(merged.get(key))
        previous = _safe_int(existing.get(key))
        if previous is not None and (incoming is None or incoming < previous):
            merged[key] = previous
    incoming_unresolved = _safe_int(merged.get("unresolved_items"))
    previous_unresolved = _safe_int(existing.get("unresolved_items"))
    if previous_unresolved is not None and (incoming_unresolved is None or incoming_unresolved > previous_unresolved):
        merged["unresolved_items"] = previous_unresolved
    merged["final"] = False
    return merged


def _ai_progress_message(progress: dict[str, Any]) -> str:
    evaluated = _safe_int(progress.get("evaluated_items")) or 0
    total = _safe_int(progress.get("total_candidates")) or 0
    negative = _safe_int(progress.get("negative_count")) or 0
    high = _safe_int(progress.get("high_count")) or 0
    manual = _safe_int(progress.get("manual_review_count") or progress.get("pending_review_items")) or 0
    state = "已完成" if progress.get("final") else "进行中"
    return f"AI 评估{state}：{evaluated}/{total}，疑似负面 {negative}，高风险 {high}，待人工复核 {manual}"


def _save_evaluation(content_db_id: int, run_id: int, evaluation: dict[str, Any]) -> None:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT OR REPLACE INTO ai_evaluations (
                workspace_id, raw_content_id, run_id, status, is_related, is_negative, risk_level, reason,
                evidence_quotes, recommended_action, raw_response, created_at, created_by, updated_by
            ) VALUES (
                (SELECT workspace_id FROM raw_contents WHERE id=?),
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                (SELECT created_by FROM raw_contents WHERE id=?),
                (SELECT created_by FROM raw_contents WHERE id=?)
            )
            """,
            (
                content_db_id,
                content_db_id,
                run_id,
                evaluation["status"],
                1 if evaluation["is_related"] else 0,
                1 if evaluation["is_negative"] else 0,
                evaluation["risk_level"],
                evaluation["reason"],
                json.dumps(evaluation.get("evidence_quotes", []), ensure_ascii=False),
                evaluation["recommended_action"],
                redact_sensitive(evaluation.get("raw_response", "")),
                utc_now(),
                content_db_id,
                content_db_id,
            ),
        )
        evaluation_id = int(cur.lastrowid or 0)
    trace = evaluation.get("_ai_trace")
    if isinstance(trace, dict):
        trace_payload = dict(trace)
        trace_payload["ai_evaluation_id"] = evaluation_id or None
        trace_payload["run_id"] = run_id
        trace_payload["raw_content_id"] = content_db_id
        trace_payload["status"] = str(evaluation.get("status") or trace_payload.get("status") or "pending_review")
        trace_payload["finished_at"] = trace_payload.get("finished_at") or utc_now()
        try:
            save_ai_evaluation_trace(trace_payload)
        except Exception:
            pass


async def _evaluate_content_with_fallback(
    job: dict[str, Any],
    run_id: int,
    content: dict[str, Any],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    max_attempts = max(1, _ai_item_retry_count() + 1)
    last_error = ""
    cfg = _job_ai_config(job)
    prompt = cfg.get("prompt") or ""
    for attempt in range(1, max_attempts + 1):
        attempt_started_at = utc_now()
        attempt_started_perf = time.perf_counter()
        _raise_if_deadline_passed(run_id)
        try:
            timeout_seconds = _ai_item_timeout_seconds(run_id)
            evaluation = await asyncio.wait_for(evaluate_content(job, content, comments), timeout=timeout_seconds)
            if not isinstance(evaluation.get("_ai_trace"), dict):
                evaluation["_ai_trace"] = _build_trace_snapshot(
                    job,
                    content,
                    comments,
                    cfg=cfg,
                    prompt=prompt,
                    status=str(evaluation.get("status") or "pending_review"),
                    started_at=attempt_started_at,
                    start_time=attempt_started_perf,
                    parsed_result=dict(evaluation),
                    response_snapshot=evaluation.get("raw_response") or "",
                )
            evaluation["_ai_trace"]["attempt_index"] = attempt
            return _normalize_evaluation_result(evaluation, content)
        except CrawlerTimedOut:
            raise
        except asyncio.CancelledError as exc:
            task = asyncio.current_task()
            if task and task.cancelling():
                raise
            last_error = f"CancelledError: {redact_sensitive(str(exc))}"
            fallback = _pending_review_evaluation(f"AI 评估失败，已转人工复核：{last_error}", content)
            fallback["_ai_trace"] = _build_trace_snapshot(
                job,
                content,
                comments,
                cfg=cfg,
                prompt=prompt,
                status="pending_review",
                started_at=attempt_started_at,
                start_time=attempt_started_perf,
                error_message=last_error,
                parsed_result=dict(fallback),
            )
            fallback["_ai_trace"]["attempt_index"] = attempt
            _merge_run_summary(
                run_id,
                {
                    "phase_7_1_lifecycle": True,
                    "phase": "ai_evaluating",
                    "retry_state": "running" if attempt < max_attempts else "exhausted",
                    "last_error": last_error,
                    "progress_updated_at": utc_now(),
                },
            )
            if attempt < max_attempts:
                continue
            return fallback
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {redact_sensitive(str(exc))}"
            fallback = _pending_review_evaluation(f"AI 评估失败，已转人工复核：{last_error}", content)
            fallback["_ai_trace"] = _build_trace_snapshot(
                job,
                content,
                comments,
                cfg=cfg,
                prompt=prompt,
                status="pending_review",
                started_at=attempt_started_at,
                start_time=attempt_started_perf,
                error_message=last_error,
                parsed_result=dict(fallback),
            )
            fallback["_ai_trace"]["attempt_index"] = attempt
            _merge_run_summary(
                run_id,
                {
                    "phase_7_1_lifecycle": True,
                    "phase": "ai_evaluating",
                    "retry_state": "running" if attempt < max_attempts else "exhausted",
                    "last_error": last_error,
                    "progress_updated_at": utc_now(),
                },
            )
            if attempt < max_attempts:
                continue
            return fallback
    fallback = _pending_review_evaluation(f"AI 评估失败，已转人工复核：{last_error}", content)
    fallback["_ai_trace"] = _build_trace_snapshot(
        job,
        content,
        comments,
        cfg=cfg,
        prompt=prompt,
        status="pending_review",
        started_at=utc_now(),
        error_message=last_error,
        parsed_result=dict(fallback),
    )
    fallback["_ai_trace"]["attempt_index"] = max_attempts
    return fallback


def _normalize_evaluation_result(evaluation: dict[str, Any], content: dict[str, Any]) -> dict[str, Any]:
    try:
        status = str(evaluation.get("status") or "")
        if status not in {"ok", "pending_review"}:
            raise ValueError("invalid evaluation status")
        result = {
            "status": status,
            "is_related": bool(evaluation.get("is_related")),
            "is_negative": bool(evaluation.get("is_negative")),
            "risk_level": str(evaluation.get("risk_level") or "low"),
            "reason": str(evaluation.get("reason") or ""),
            "evidence_quotes": list(evaluation.get("evidence_quotes") or []),
            "recommended_action": str(evaluation.get("recommended_action") or ""),
            "raw_response": str(evaluation.get("raw_response") or ""),
        }
        if isinstance(evaluation.get("_ai_trace"), dict):
            result["_ai_trace"] = evaluation["_ai_trace"]
        return result
    except Exception as exc:
        fallback = _pending_review_evaluation(f"AI 返回结构无效，已转人工复核：{type(exc).__name__}", content)
        fallback["_ai_trace"] = {
            "status": "pending_review",
            "error_message": f"AI 返回结构无效，已转人工复核：{type(exc).__name__}",
            "input_payload": {"content_id": content.get("content_id")},
            "request_snapshot": {},
            "response_snapshot": "",
            "parsed_result": dict(fallback),
            "attempt_index": 1,
        }
        return fallback


def _pending_review_evaluation(reason: str, content: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "pending_review",
        "is_related": True,
        "is_negative": False,
        "risk_level": "low",
        "reason": redact_sensitive(reason),
        "evidence_quotes": [str(content.get("title") or content.get("description") or "")[:200]],
        "recommended_action": "人工复核",
        "raw_response": "",
    }


def _apply_unresolved_ai_fallback_summary(run_id: int, summary: dict[str, Any], content_ids: list[int], cause: str) -> int:
    unique_content_ids = [int(content_id) for content_id in dict.fromkeys(content_ids or []) if _safe_int(content_id)]
    known_candidates = len(unique_content_ids)
    fallback_created = _mark_unresolved_candidates_pending_review(run_id, unique_content_ids)
    unresolved_after = max(0, known_candidates - _count_ai_evaluations_for_run(run_id, unique_content_ids))
    limited_context_left = 0
    if not known_candidates and _safe_int(summary.get("new_contents")):
        limited_context_left = _safe_int(summary.get("new_contents")) or 0
    if fallback_created:
        summary["pending_review_count"] = int(summary.get("pending_review_count") or 0) + fallback_created
        summary["ai_failed_fallback_evaluations"] = int(summary.get("ai_failed_fallback_evaluations") or 0) + fallback_created
        summary["ai_pending_review_items"] = int(summary.get("ai_pending_review_items") or 0) + fallback_created
    summary["ai_unresolved_items"] = unresolved_after
    summary["ai_limited_context_items"] = limited_context_left
    summary["ai_finalization_fallback"] = {
        "cause": cause,
        "known_unresolved_candidate_ids": known_candidates,
        "pending_review_rows_created": fallback_created,
        "unresolved_candidates_remaining": unresolved_after,
        "limited_context_rows_left_unchanged": limited_context_left,
    }
    summary["ai_progress"] = {
        "total_candidates": known_candidates,
        "successful_evaluations": int(summary.get("ai_successful_evaluations") or 0),
        "failed_fallback_evaluations": int(summary.get("ai_failed_fallback_evaluations") or 0),
        "pending_review_items": int(summary.get("pending_review_count") or 0),
        "manual_review_count": int(summary.get("pending_review_count") or 0),
        "negative_count": int(summary.get("negative_count") or 0),
        "high_count": int(summary.get("high_count") or 0),
        "unresolved_items": unresolved_after,
        "limited_context_items": limited_context_left,
        "evaluated_items": max(0, known_candidates - unresolved_after),
        "final": True,
    }
    _merge_run_summary(
        run_id,
        {
            "phase_7_2_lifecycle": True,
            "phase_19c_progress": True,
            "ai_progress": summary["ai_progress"],
            "ai_finalization_fallback": summary["ai_finalization_fallback"],
            "pending_review_count": summary.get("pending_review_count"),
            "negative_count": summary.get("negative_count", 0),
            "high_count": summary.get("high_count", 0),
            "ai_failed_fallback_evaluations": summary.get("ai_failed_fallback_evaluations", 0),
            "ai_pending_review_items": summary.get("ai_pending_review_items", 0),
            "ai_unresolved_items": unresolved_after,
            "ai_limited_context_items": limited_context_left,
            "ai_progress_final": True,
            "progress_updated_at": utc_now(),
        },
    )
    return fallback_created


def _mark_unresolved_candidates_pending_review(run_id: int, content_ids: list[int]) -> int:
    if not content_ids:
        return 0
    placeholders = ",".join("?" for _ in content_ids)
    with get_conn() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                f"""
                SELECT rc.*
                FROM raw_contents rc
                LEFT JOIN ai_evaluations ev ON ev.raw_content_id=rc.id AND ev.run_id=?
                WHERE rc.id IN ({placeholders})
                  AND ev.id IS NULL
                """,
                [run_id, *content_ids],
            ).fetchall()
        ]
    for row in rows:
        _save_evaluation(
            int(row["id"]),
            run_id,
            _pending_review_evaluation("AI 评估未完成，已在运行收尾时转人工复核", row),
        )
    return len(rows)


def _count_ai_evaluations_for_run(run_id: int, content_ids: list[int]) -> int:
    if not content_ids:
        return 0
    placeholders = ",".join("?" for _ in content_ids)
    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT COUNT(*) AS n
            FROM ai_evaluations
            WHERE raw_content_id IN ({placeholders})
              AND (run_id=? OR run_id IS NULL)
            """,
            [*content_ids, run_id],
        ).fetchone()
    return int(row["n"] or 0) if row else 0


def _merge_run_summary(run_id: int, updates: dict[str, Any]) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT summary FROM crawl_runs WHERE id=? AND status='running'", (run_id,)).fetchone()
        if not row:
            return {}
        try:
            summary = json.loads(row["summary"] or "{}")
        except (TypeError, ValueError):
            summary = {}
        if not isinstance(summary, dict):
            summary = {}
        summary.update(updates)
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_summary(summary), ensure_ascii=False), run_id),
        )
    return summary


def _redact_summary(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _redact_summary(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_summary(item) for item in value]
    if isinstance(value, str):
        return redact_sensitive(value)
    return value


def _load_comments(platform: str, content_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM raw_comments WHERE platform=? AND content_id=? ORDER BY id LIMIT 20",
                (platform, content_id),
            ).fetchall()
        ]


def _build_crawler_cmd(
    job: dict[str, Any],
    platform: str,
    out_dir: Path,
    account_binding: dict[str, Any] | None = None,
) -> list[str]:
    headless = os.environ.get("MONITOR_CRAWLER_HEADLESS", "true").lower() not in {"0", "false", "no"}
    connect_existing = os.environ.get("MONITOR_CDP_CONNECT_EXISTING", "false").lower() in {"1", "true", "yes"}
    debug_port = os.environ.get(f"MONITOR_CDP_DEBUG_PORT_{platform.upper()}") or os.environ.get("MONITOR_CDP_DEBUG_PORT")
    debug_port = debug_port or str(PLATFORM_DEBUG_PORTS.get(platform, 9223))
    login_config = get_platform_login_config(platform, masked=False)
    login_type = (account_binding or {}).get("login_type") or login_config.get("login_type") or "qrcode"
    if login_type not in {"qrcode", "cookie"}:
        login_type = "qrcode"
    target_type = str(job.get("target_type") or "search")
    output_mode = str(job.get("output_mode") or "internal")
    save_option = "excel" if output_mode == "excel" else "json"
    max_items = _job_int(job, "max_items", 50)
    max_pages = _job_int(job, "max_pages", 1)
    start_page = _job_int(job, "start_page", 1)
    crawler_max_items = max(max_items, max_pages * 10)
    cmd = [
        "uv",
        "run",
        "python",
        "main.py",
        "--platform",
        platform,
        "--lt",
        login_type,
        "--type",
        target_type,
        "--save_data_option",
        save_option,
        "--start",
        str(start_page),
        "--keywords",
        ",".join(job.get("keywords", [])),
        "--get_comment",
        "true" if job.get("enable_comments") else "false",
        "--get_sub_comment",
        "true" if job.get("enable_sub_comments") else "false",
        "--headless",
        "true" if headless else "false",
        "--save_data_path",
        str(out_dir),
        "--max_concurrency_num",
        "1",
        "--crawler_max_notes_count",
        str(crawler_max_items),
    ]
    if target_type == "detail":
        cmd.extend(["--specified_id", ",".join(job.get("keywords", []))])
    if target_type == "creator":
        cmd.extend(["--creator_id", ",".join(job.get("keywords", []))])
    if login_type == "cookie":
        cookies = (account_binding or {}).get("cookies") or login_config.get("cookies") or ""
        if not cookies:
            raise ValueError(f"{platform} Cookie 登录未配置 Cookie")
        cmd.extend(["--cookies", cookies])
    if platform == "dy":
        cmd.extend(["--publish_time_type", str(douyin_publish_time_type(job))])
    if platform == "xhs":
        cmd.extend(["--sort_type", "time_descending"])
    cmd.extend(
        [
            "--cdp_connect_existing",
            "true" if connect_existing else "false",
            "--cdp_debug_port",
            str(debug_port),
        ]
    )
    return cmd


def _job_int(job: dict[str, Any], key: str, default: int) -> int:
    try:
        return max(1, int(job.get(key) or default))
    except (TypeError, ValueError):
        return default


def _build_crawler_env(account_binding: dict[str, Any] | None = None) -> dict[str, str]:
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    if not account_binding:
        return env
    profile_path = str(account_binding.get("profile_path") or "").strip()
    platform = str(account_binding.get("platform") or "").strip()
    if profile_path:
        env["MONITOR_CDP_USER_DATA_DIR"] = profile_path
        if platform:
            env[f"MONITOR_CDP_USER_DATA_DIR_{platform.upper()}"] = profile_path
        env["MONITOR_ACTIVE_ACCOUNT_ID"] = str(account_binding.get("account_id") or "")
        env["MONITOR_ACTIVE_ACCOUNT_NAME"] = str(account_binding.get("account_name") or "")
    proxy_url = str(account_binding.get("proxy_url") or "").strip()
    if proxy_url:
        env.update(
            {
                "HTTP_PROXY": proxy_url,
                "HTTPS_PROXY": proxy_url,
                "ALL_PROXY": proxy_url,
                "http_proxy": proxy_url,
                "https_proxy": proxy_url,
                "all_proxy": proxy_url,
                "MONITOR_ACTIVE_PROXY_ID": str(account_binding.get("proxy_id") or ""),
                "MONITOR_ACTIVE_PROXY_NAME": str(account_binding.get("proxy_name") or ""),
            }
        )
    return env


def _resolve_platform_account_binding(platform: str, job: dict[str, Any] | None = None) -> dict[str, Any] | None:
    job = job or {}
    explicit_account_id = _safe_int(job.get("account_id"))
    explicit_proxy_id = _safe_int(job.get("proxy_id"))
    accounts: list[dict[str, Any]] = []
    if explicit_account_id:
        account = get_social_account(explicit_account_id, masked=False)
        if account:
            accounts.append(account)
    else:
        accounts.extend(list_social_accounts(masked=False))
    for account in accounts:
        if account.get("is_draft"):
            continue
        if account.get("platform") != platform:
            continue
        if account.get("status") != "active":
            continue
        binding: dict[str, Any] = {
            "account_id": account.get("id"),
            "account_name": account.get("name") or "",
            "platform": platform,
            "login_type": account.get("login_type") or "qrcode",
            "cookies": account.get("cookies") or "",
            "profile_key": account.get("profile_key") or "",
            "profile_configured": bool(account.get("profile_configured")),
            "profile_path": account.get("profile_path") or "",
        }
        proxy_id = explicit_proxy_id or account.get("proxy_id")
        if proxy_id:
            proxy = get_proxy_profile(int(proxy_id), masked=False)
            if proxy and proxy.get("status") == "active" and proxy.get("proxy_url"):
                binding.update(
                    {
                        "proxy_id": proxy.get("id"),
                        "proxy_name": proxy.get("name") or "",
                        "provider": proxy.get("provider") or "",
                        "proxy_url": proxy.get("proxy_url") or "",
                    }
                )
        if binding.get("profile_path") or binding.get("proxy_id") or binding.get("cookies"):
            return binding
    if explicit_proxy_id:
        proxy = get_proxy_profile(explicit_proxy_id, masked=False)
        if proxy and proxy.get("status") == "active" and proxy.get("proxy_url"):
            return {
                "account_id": None,
                "account_name": "",
                "platform": platform,
                "profile_path": "",
                "proxy_id": proxy.get("id"),
                "proxy_name": proxy.get("name") or "",
                "provider": proxy.get("provider") or "",
                "proxy_url": proxy.get("proxy_url") or "",
            }
    return None


def _resolve_platform_proxy_binding(platform: str, job: dict[str, Any] | None = None) -> dict[str, Any] | None:
    binding = _resolve_platform_account_binding(platform, job)
    return binding if binding and binding.get("proxy_id") else None


def _safe_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _account_summary(account_binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": account_binding.get("account_id"),
        "account_name": account_binding.get("account_name") or "",
        "platform": account_binding.get("platform") or "",
        "profile_key": str(account_binding.get("profile_key") or ""),
        "profile_configured": bool(account_binding.get("profile_path") or account_binding.get("profile_configured")),
    }


def _proxy_summary(proxy_binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": proxy_binding.get("account_id"),
        "account_name": proxy_binding.get("account_name") or "",
        "proxy_id": proxy_binding.get("proxy_id"),
        "proxy_name": proxy_binding.get("proxy_name") or "",
        "provider": proxy_binding.get("provider") or "",
        "proxy_url": redact_sensitive(str(proxy_binding.get("proxy_url") or "")),
    }


def _touch_job_last_run(job_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE monitor_jobs SET last_run_at=?, updated_at=? WHERE id=?",
            (utc_now(), utc_now(), job_id),
        )


def _mark_phase(
    run_id: int,
    summary: dict[str, Any],
    phase: str,
    *,
    last_safe_result: Any | None = None,
    last_error: str | None = None,
    persist: bool = True,
) -> None:
    now = utc_now()
    summary["phase_7_1_lifecycle"] = True
    if summary.get("phase") != phase:
        summary["phase_started_at"] = now
    summary["phase"] = phase
    summary["progress_updated_at"] = now
    if last_safe_result is not None:
        summary["last_safe_result"] = _redact_summary(last_safe_result)
    if last_error:
        summary["last_error"] = redact_sensitive(last_error)
    if persist:
        update_run_summary(run_id, summary)


def _ai_item_timeout_seconds(run_id: int) -> int:
    configured = max(1, _runtime_setting_int("ai_item_timeout_seconds", DEFAULT_AI_ITEM_TIMEOUT_SECONDS))
    remaining = _remaining_run_seconds(run_id)
    return max(1, min(configured, remaining))


def _ai_item_retry_count() -> int:
    return max(0, _runtime_setting_int("ai_item_retry_count", DEFAULT_AI_ITEM_RETRY_COUNT))


def _matches_exclude_words(content: dict[str, Any], job: dict[str, Any]) -> bool:
    exclude_words = [str(word).strip().lower() for word in job.get("exclude_words", []) if str(word).strip()]
    if not exclude_words:
        return False
    haystack = " ".join(
        str(content.get(key) or "")
        for key in ("title", "description", "source_keyword", "author_name")
    ).lower()
    return any(word in haystack for word in exclude_words)


def _run_duration_seconds(run_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT started_at FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    if not row or not row["started_at"]:
        return 0
    try:
        started = datetime.fromisoformat(str(row["started_at"]).replace("Z", "+00:00"))
        now = datetime.fromisoformat(utc_now())
        return max(0, int((now - started).total_seconds()))
    except ValueError:
        return 0


def _run_timeout_seconds(run_id: int) -> int | None:
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT timeout_seconds FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    except Exception:
        return None
    return _safe_int(row["timeout_seconds"]) if row else None


def _run_deadline_at(run_id: int) -> str:
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT deadline_at FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    except Exception:
        return ""
    return str(row["deadline_at"] or "") if row else ""


def _lock_expires_at(run_id: int) -> str:
    raw_deadline = _run_deadline_at(run_id)
    deadline = _parse_run_deadline(run_id)
    if not deadline:
        return raw_deadline
    return (deadline + timedelta(seconds=max(60, _runtime_setting_int("lock_cleanup_buffer_seconds", 300)))).isoformat()


def _remaining_run_seconds(run_id: int) -> int:
    deadline = _parse_run_deadline(run_id)
    if not deadline:
        return _runtime_setting_int("crawler_timeout_seconds", 900)
    remaining = int((deadline - datetime.now(timezone.utc)).total_seconds())
    if remaining <= 0:
        raise CrawlerTimedOut(_timeout_message(run_id))
    return max(1, remaining)


def _raise_if_deadline_passed(run_id: int) -> None:
    deadline = _parse_run_deadline(run_id)
    if deadline and datetime.now(timezone.utc) >= deadline:
        raise CrawlerTimedOut(_timeout_message(run_id))


def _parse_run_deadline(run_id: int) -> datetime | None:
    raw_deadline = _run_deadline_at(run_id)
    if not raw_deadline:
        return None
    try:
        parsed = datetime.fromisoformat(raw_deadline.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _timeout_message(run_id: int) -> str:
    timeout_seconds = _run_timeout_seconds(run_id)
    if timeout_seconds:
        return f"任务达到系统运行时间上限（{timeout_seconds} 秒），已停止未完成的采集进程"
    return "任务达到系统运行时间上限，已停止未完成的采集进程"


def _looks_like_login_required(log_text: str) -> bool:
    lower = log_text.lower()
    markers = [
        "no login",
        "login failed",
        "begin login",
        "login state result: false",
        "qrcode",
        "登录",
        "未登录",
        "扫码",
    ]
    return any(marker in lower for marker in markers)


def _crawler_max_retries() -> int:
    return max(0, _runtime_setting_int("crawler_retry_count", DEFAULT_CRAWLER_MAX_RETRIES))


def _crawler_retry_delay_seconds() -> float:
    return max(0.0, float(_runtime_setting_int("crawler_retry_delay_seconds", int(DEFAULT_CRAWLER_RETRY_DELAY_SECONDS))))


def _should_retry_crawler_error(error: str) -> bool:
    if _looks_like_login_required(error) or "登录窗口未关闭" in error:
        return False
    return True


def _attempt_output_dir(platform_root: Path, attempt: int, total_attempts: int) -> Path:
    if total_attempts <= 1:
        return platform_root
    return platform_root / f"attempt_{attempt}"


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def _raise_if_stop_requested(job_id: int) -> None:
    if is_stop_requested(job_id):
        raise CrawlerStopped("任务已手动停止")


def _register_process(job_id: int, process: subprocess.Popen) -> None:
    with PROCESS_LOCK:
        RUN_PROCESSES[int(job_id)].add(process)


def _unregister_process(job_id: int, process: subprocess.Popen) -> None:
    with PROCESS_LOCK:
        processes = RUN_PROCESSES.get(int(job_id))
        if not processes:
            return
        processes.discard(process)
        if not processes:
            RUN_PROCESSES.pop(int(job_id), None)


def _terminate_process(process: subprocess.Popen) -> bool:
    if process.poll() is not None:
        return False
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            process.terminate()
        return True
    except Exception:
        try:
            process.kill()
            return True
        except Exception:
            return False


def _acquire_job_lock(job_id: int) -> Path | None:
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCKS_DIR / f"job_{job_id}.lock"
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if _job_lock_is_expired(lock_path):
            _release_job_lock(lock_path)
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except OSError:
                return None
        else:
            return None
    except OSError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"job_id": job_id, "created_at": utc_now()}, ensure_ascii=False))
    return lock_path


def _release_job_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def _job_lock_is_expired(lock_path: Path) -> bool:
    try:
        raw = json.loads(lock_path.read_text(encoding="utf-8") or "{}")
        created_at = raw.get("created_at")
        created = datetime.fromisoformat(str(created_at).replace("Z", "+00:00")) if created_at else None
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            return (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).total_seconds() > JOB_LOCK_TTL_SECONDS
    except Exception:
        pass
    try:
        age = datetime.now(timezone.utc).timestamp() - lock_path.stat().st_mtime
        return age > JOB_LOCK_TTL_SECONDS
    except OSError:
        return True
