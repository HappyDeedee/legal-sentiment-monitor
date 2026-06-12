from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .database import create_run, get_conn, save_job
from .reporting import create_report, update_report_email_status
from .runner import evaluate_new_contents, ingest_outputs


async def create_sample_report() -> dict[str, Any]:
    _mark_existing_selftest_jobs_internal()
    job = save_job(
        {
            "law_firm_name": "MVP自测律所",
            "aliases": ["MVP自测"],
            "exclude_words": ["招聘"],
            "keywords": ["MVP自测律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
            "is_internal": True,
        }
    )
    run_id = create_run(job["id"])
    now_ts = int(datetime.now(timezone.utc).timestamp())
    contents = [
        {
            "aweme_id": f"selftest_negative_{run_id}",
            "title": "MVP自测律所避雷：收费沟通争议",
            "desc": "样例内容：用户投诉沟通慢、收费不透明。此内容用于本地报告链路自测。",
            "aweme_url": f"https://example.com/selftest/video/{run_id}",
            "cover_url": "https://example.com/selftest/cover.jpg",
            "create_time": now_ts,
        },
        {
            "aweme_id": f"selftest_excluded_{run_id}",
            "title": "MVP自测律所招聘信息",
            "desc": "样例内容：招聘信息应该被排除词过滤。",
            "create_time": now_ts,
        },
    ]
    ingested = ingest_outputs(job, run_id, "dy", contents, [])
    eval_summary = await evaluate_new_contents(job, run_id, ingested["content_db_ids"])
    summary = {
        "platforms": ["dy"],
        "keywords": job["keywords"],
        "raw_contents": ingested["raw_contents"],
        "filtered_contents": ingested["filtered_contents"],
        "excluded_contents": ingested["excluded_contents"],
        "new_contents": ingested["new_contents"],
        "negative_count": eval_summary["negative_count"],
        "high_count": eval_summary["high_count"],
        "failed_platforms": [],
        "platform_results": {"dy": ingested},
        "duration_seconds": 0,
        "email_status": "skipped",
        "email_error": "本地自测不发送邮件",
        "selftest": True,
    }
    report = create_report(run_id, job, summary)
    update_report_email_status(report["id"], "skipped", "本地自测不发送邮件")
    with get_conn() as conn:
        conn.execute(
            "UPDATE crawl_runs SET status=?, finished_at=?, summary=?, error_message=? WHERE id=?",
            ("selftest", datetime.now(timezone.utc).isoformat(), __import__("json").dumps(summary, ensure_ascii=False), None, run_id),
        )
    return {"job": job, "run_id": run_id, "summary": summary, "report": report}


def _mark_existing_selftest_jobs_internal() -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE monitor_jobs SET is_internal=1 WHERE law_firm_name=?",
            ("MVP自测律所",),
        )
