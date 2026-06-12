from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .database import create_run, get_conn, mark_selftest_jobs_internal, save_job
from .reporting import create_report, update_report_email_status
from .runner import ingest_outputs


async def create_sample_report() -> dict[str, Any]:
    mark_selftest_jobs_internal()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": ["海安律师事务所", "海安律师"],
            "exclude_words": ["招聘"],
            "keywords": ["海安律所避雷", "海安律所退费", "海安律所投诉"],
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
            "title": "海安律所避雷：收费沟通争议",
            "desc": "样例内容：用户投诉沟通慢、收费不透明。此内容用于本地报告链路自测。",
            "aweme_url": f"https://example.com/selftest/video/{run_id}",
            "cover_url": "https://example.com/selftest/cover.jpg",
            "create_time": now_ts,
        },
        {
            "aweme_id": f"selftest_excluded_{run_id}",
            "title": "海安律所招聘信息",
            "desc": "样例内容：招聘信息应该被排除词过滤。",
            "create_time": now_ts,
        },
    ]
    ingested = ingest_outputs(job, run_id, "dy", contents, [])
    eval_summary = _save_pending_review_evaluations(run_id, ingested["content_db_ids"])
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
            ("selftest", datetime.now(timezone.utc).isoformat(), json.dumps(summary, ensure_ascii=False), None, run_id),
        )
    return {"job": job, "run_id": run_id, "summary": summary, "report": report}


def _save_pending_review_evaluations(run_id: int, content_ids: list[int]) -> dict[str, int]:
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                "SELECT id, title, description FROM raw_contents WHERE id IN (%s)" % ",".join("?" for _ in content_ids),
                content_ids,
            ).fetchall()
        ] if content_ids else []
        for row in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO ai_evaluations (
                    raw_content_id, run_id, status, is_related, is_negative, risk_level, reason,
                    evidence_quotes, recommended_action, raw_response, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    run_id,
                    "pending_review",
                    1,
                    0,
                    "low",
                    "本地自测不调用真实 AI，固定标记为待人工复核",
                    json.dumps([row.get("title") or row.get("description") or ""], ensure_ascii=False),
                    "请确认报告预览、Excel、Markdown 下载链路正常。",
                    "",
                    now,
                ),
            )
    return {"negative_count": 0, "high_count": 0}
