from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from typing import Any, Sequence

from .database import get_job, has_job_template_placeholders, init_db, list_jobs, record_skipped_run, set_job_schedule_state
from .doctor import run_doctor
from .preflight import build_job_preflight
from .readiness import get_readiness_status
from .runner import run_job
from .scheduler import _is_due, next_run_at
from .security import redact_sensitive
from .selftest import create_sample_report
from .smoke import run_smoke_check


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = asyncio.run(_run_command(args))
    except Exception as exc:
        _print_json({"ok": False, "error": redact_sensitive(f"{type(exc).__name__}: {exc}")})
        return 1
    _print_json(result)
    if isinstance(result, dict) and result.get("failed"):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="legal-sentiment-monitor command line tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("readiness", help="print deployment readiness status")
    subparsers.add_parser("doctor", help="run local deployment diagnostics")
    subparsers.add_parser("selftest-report", help="generate a local self-test report")
    subparsers.add_parser("smoke", help="run local smoke checks and generate a self-test report")
    subparsers.add_parser("list-jobs", help="list visible monitor jobs")

    run_job_parser = subparsers.add_parser("run-job", help="run one monitor job immediately")
    run_job_parser.add_argument("job_id", type=int)

    subparsers.add_parser("run-due", help="run enabled jobs that are due now")
    return parser


async def _run_command(args: argparse.Namespace) -> dict[str, Any]:
    init_db()
    if args.command == "readiness":
        return get_readiness_status()
    if args.command == "doctor":
        return run_doctor()
    if args.command == "selftest-report":
        return await create_sample_report()
    if args.command == "smoke":
        return await run_smoke_check()
    if args.command == "list-jobs":
        return {"jobs": list_jobs()}
    if args.command == "run-job":
        return await run_one_job(args.job_id)
    if args.command == "run-due":
        return await run_due_jobs()
    raise ValueError(f"unsupported command: {args.command}")


async def run_one_job(job_id: int) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    preflight = build_job_preflight(job, [])
    if preflight["blockers"]:
        reason = "运行前检查未通过：" + "；".join(preflight["blockers"])
        run_id = record_skipped_run(job_id, reason, _skip_summary(job, "preflight_blocked", preflight, source="cli"))
        _refresh_schedule_state(job_id)
        return {"ok": False, "failed": 1, "ran": 0, "skipped": 1, "results": [{"job_id": job_id, "run_id": run_id, "status": "skipped", "reason": reason, "preflight": preflight}]}
    result = await run_job(job_id)
    _refresh_schedule_state(job_id)
    return {"ok": True, "ran": 1, "results": [{"job_id": job_id, "status": result.get("status"), "result": result}]}


async def run_due_jobs(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now()
    results: list[dict[str, Any]] = []
    for job in list_jobs():
        job_id = int(job["id"])
        if not job.get("enabled"):
            set_job_schedule_state(job_id, None)
            continue
        set_job_schedule_state(job_id, next_run_at(job, now))
        if not _is_due(job, now):
            continue
        if has_job_template_placeholders(job):
            reason = "请先把测试数据模板里的律所名称和平台搜索词改成真实内容"
            run_id = record_skipped_run(job_id, reason, _skip_summary(job, "template_placeholders", source="cli"))
            results.append({"job_id": job_id, "run_id": run_id, "status": "skipped", "reason": reason})
            continue
        preflight = build_job_preflight(job, [])
        if preflight["blockers"]:
            reason = "运行前检查未通过：" + "；".join(preflight["blockers"])
            run_id = record_skipped_run(job_id, reason, _skip_summary(job, "preflight_blocked", preflight, source="cli"))
            results.append({"job_id": job_id, "run_id": run_id, "status": "skipped", "reason": reason, "preflight": preflight})
            continue
        try:
            result = await run_job(job_id)
            results.append({"job_id": job_id, "status": result.get("status"), "result": result})
        except Exception as exc:
            results.append({"job_id": job_id, "status": "failed", "error": redact_sensitive(f"{type(exc).__name__}: {exc}")})
        finally:
            _refresh_schedule_state(job_id)
    failed = [item for item in results if item.get("status") in {"failed", "partial_failed"}]
    ran = [item for item in results if item.get("status") not in {"already_running", "skipped"}]
    skipped = [item for item in results if item.get("status") in {"already_running", "skipped"}]
    return {"ok": not failed, "ran": len(ran), "skipped": len(skipped), "failed": len(failed), "results": results}


def _refresh_schedule_state(job_id: int) -> None:
    refreshed = get_job(job_id)
    if refreshed and refreshed.get("enabled"):
        set_job_schedule_state(job_id, next_run_at(refreshed, datetime.now()))
    elif refreshed:
        set_job_schedule_state(job_id, None)


def _skip_summary(job: dict[str, Any], skip_type: str, preflight: dict[str, Any] | None = None, source: str = "cli") -> dict[str, Any]:
    summary = {
        "job_id": job.get("id"),
        "law_firm_name": job.get("law_firm_name") or "",
        "platforms": job.get("platforms", []),
        "keywords": job.get("keywords", []),
        "skip_type": skip_type,
        "source": source,
    }
    if preflight:
        summary["preflight"] = preflight
    return summary


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
