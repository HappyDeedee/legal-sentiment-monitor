from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = Path(os.environ.get("MONITOR_DATA_DIR") or ROOT / "monitor_data").resolve()
DEFAULT_DATABASE = DEFAULT_DATA_DIR / "monitor.sqlite"
DEFAULT_GATES = [
    "database_backup_required",
    "artifact_email_backup_required",
    "explicit_operator_approval_required",
    "rollback_plan_required",
]
ARTIFACT_PATTERN = re.compile(r"job_(?P<job_id>\d+)_run_(?P<run_id>\d+)_")


def build_orphan_email_evidence_review(
    *,
    database: str | Path | None = None,
    delivery_log_id: int | None = None,
    job_id: int | None = None,
    report_id: int | None = None,
    artifact_root: str | Path | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Return a read-only dry-run review of email delivery evidence."""

    database_path = Path(database or DEFAULT_DATABASE).resolve()
    artifact_base = Path(artifact_root).resolve() if artifact_root else database_path.parent / "reports"
    logs = _load_delivery_logs(
        database_path,
        delivery_log_id=delivery_log_id,
        job_id=job_id,
        report_id=report_id,
        limit=limit,
    )
    items = [_review_log(database_path, artifact_base, log) for log in logs]
    return {
        "mode": "dry_run",
        "database": str(database_path),
        "artifact_root": str(artifact_base),
        "filters": {
            "delivery_log_id": delivery_log_id,
            "job_id": job_id,
            "report_id": report_id,
            "limit": limit,
        },
        "count": len(items),
        "mutations_attempted": 0,
        "mutation_policy": "review-only; no delete, annotate, repair, or rewrite path is implemented",
        "required_before_any_mutation": list(DEFAULT_GATES),
        "items": items,
    }


def _load_delivery_logs(
    database_path: Path,
    *,
    delivery_log_id: int | None,
    job_id: int | None,
    report_id: int | None,
    limit: int,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if delivery_log_id is not None:
        clauses.append("id=?")
        params.append(int(delivery_log_id))
    if job_id is not None:
        clauses.append("job_id=?")
        params.append(int(job_id))
    if report_id is not None:
        clauses.append("report_id=?")
        params.append(int(report_id))
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM email_delivery_logs {where} ORDER BY id DESC"
    safe_limit = max(1, min(int(limit or 50), 500))
    if delivery_log_id is None:
        sql += " LIMIT ?"
        params.append(safe_limit)
    with _readonly_conn(database_path) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def _review_log(database_path: Path, artifact_root: Path, log: dict[str, Any]) -> dict[str, Any]:
    log_job_id = _safe_int(log.get("job_id"))
    log_report_id = _safe_int(log.get("report_id"))
    with _readonly_conn(database_path) as conn:
        job = _fetch_one(conn, "SELECT id, workspace_id, law_firm_name, created_by FROM monitor_jobs WHERE id=?", log_job_id)
        report = _fetch_one(conn, "SELECT * FROM reports WHERE id=?", log_report_id)
        run = _fetch_run(conn, report, artifact_root, log_job_id)
    artifacts = _artifact_evidence(report, artifact_root, log_job_id)
    classification, secondary = _classify(log, job, report, run, artifacts)
    return {
        "delivery_log": {
            "id": _safe_int(log.get("id")),
            "workspace_id": _safe_int(log.get("workspace_id")),
            "job_id": log_job_id,
            "report_id": log_report_id,
            "send_type": str(log.get("send_type") or ""),
            "status": str(log.get("status") or ""),
            "sent_at": log.get("sent_at"),
            "created_at": log.get("created_at"),
            "send_window_key": str(log.get("send_window_key") or ""),
        },
        "exists": {
            "job": bool(job),
            "report": bool(report),
            "run": bool(run),
        },
        "resolved": {
            "job": job or None,
            "report": _report_summary(report),
            "run": run or None,
        },
        "artifacts": artifacts,
        "classification": classification,
        "secondary_classifications": secondary,
        "required_before_any_mutation": list(DEFAULT_GATES),
        "dry_run": {
            "mutations_attempted": 0,
            "proposed_effect": "review_only_no_changes",
            "rollback_path": (
                "No rollback is needed for this dry-run. Any future mutation must first restore "
                "from the recorded database backup and artifact/email backup if the result is wrong."
            ),
        },
    }


def _fetch_run(
    conn: sqlite3.Connection,
    report: dict[str, Any] | None,
    artifact_root: Path,
    job_id: int | None,
) -> dict[str, Any] | None:
    run_id = _safe_int((report or {}).get("run_id"))
    if not run_id:
        for path in _scan_artifact_paths(artifact_root, job_id):
            match = ARTIFACT_PATTERN.search(path.name)
            if match:
                run_id = _safe_int(match.group("run_id"))
                break
    if not run_id:
        return None
    return _fetch_one(conn, "SELECT id, job_id, status, started_at, finished_at FROM crawl_runs WHERE id=?", run_id)


def _artifact_evidence(report: dict[str, Any] | None, artifact_root: Path, job_id: int | None) -> dict[str, Any]:
    candidates: list[Path] = []
    for key in ("html_path", "markdown_path", "excel_path"):
        value = (report or {}).get(key)
        if value:
            candidates.append(_resolve_path(value))
    candidates.extend(_scan_artifact_paths(artifact_root, job_id))
    seen: set[str] = set()
    items = []
    for path in candidates:
        marker = str(path)
        if marker in seen:
            continue
        seen.add(marker)
        exists = path.exists()
        items.append(
            {
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists and path.is_file() else None,
            }
        )
    return {
        "count": len(items),
        "existing_count": sum(1 for item in items if item["exists"]),
        "items": items,
    }


def _classify(
    log: dict[str, Any],
    job: dict[str, Any] | None,
    report: dict[str, Any] | None,
    run: dict[str, Any] | None,
    artifacts: dict[str, Any],
) -> tuple[str, list[str]]:
    secondary: list[str] = []
    has_job_id = bool(_safe_int(log.get("job_id")))
    has_report_id = bool(_safe_int(log.get("report_id")))
    missing_owner = (has_job_id and not job) or (has_report_id and not report)
    if missing_owner:
        if not report and artifacts["existing_count"]:
            secondary.append("detached_report_artifacts")
        if not run:
            secondary.append("limited_context")
        return "orphan_delivery_log", secondary
    if report and artifacts["count"] and artifacts["existing_count"] < artifacts["count"]:
        return "limited_context", secondary
    if not has_job_id or not has_report_id:
        return "limited_context", secondary
    return "normal", secondary


def _readonly_conn(database_path: Path) -> sqlite3.Connection:
    if not database_path.exists():
        raise FileNotFoundError(f"database not found: {database_path}")
    uri = database_path.as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _fetch_one(conn: sqlite3.Connection, sql: str, value: int | None) -> dict[str, Any] | None:
    if not value:
        return None
    row = conn.execute(sql, (int(value),)).fetchone()
    return dict(row) if row else None


def _scan_artifact_paths(artifact_root: Path, job_id: int | None) -> list[Path]:
    if not job_id or not artifact_root.exists():
        return []
    return sorted(path.resolve() for path in artifact_root.glob(f"job_{int(job_id)}_run_*.*") if path.is_file())


def _resolve_path(value: str | Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path.resolve()
    return (ROOT / path).resolve()


def _report_summary(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if not report:
        return None
    return {
        "id": _safe_int(report.get("id")),
        "workspace_id": _safe_int(report.get("workspace_id")),
        "run_id": _safe_int(report.get("run_id")),
        "job_id": _safe_int(report.get("job_id")),
        "created_at": report.get("created_at"),
        "email_status": report.get("email_status"),
    }


def _safe_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _render_text(review: dict[str, Any]) -> str:
    lines = [
        "Orphan email evidence dry-run review",
        f"mode: {review['mode']}",
        f"database: {review['database']}",
        f"artifact_root: {review['artifact_root']}",
        f"mutations_attempted: {review['mutations_attempted']}",
        "required_before_any_mutation: " + ", ".join(review["required_before_any_mutation"]),
        f"items: {review['count']}",
    ]
    for item in review["items"]:
        log = item["delivery_log"]
        lines.extend(
            [
                "",
                f"- delivery_log_id={log['id']} job_id={log['job_id']} report_id={log['report_id']}",
                f"  status={log['status']} send_type={log['send_type']} sent_at={log['sent_at']}",
                f"  exists: job={item['exists']['job']} report={item['exists']['report']} run={item['exists']['run']}",
                f"  classification={item['classification']}",
                f"  secondary={', '.join(item['secondary_classifications']) or '-'}",
                f"  artifacts_existing={item['artifacts']['existing_count']}/{item['artifacts']['count']}",
                f"  dry_run_effect={item['dry_run']['proposed_effect']}",
            ]
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run review for orphan email delivery evidence.")
    parser.add_argument("--database", default=str(DEFAULT_DATABASE), help="Path to monitor.sqlite")
    parser.add_argument("--delivery-log-id", type=int, default=None)
    parser.add_argument("--job-id", type=int, default=None)
    parser.add_argument("--report-id", type=int, default=None)
    parser.add_argument("--artifact-root", default=None, help="Report artifact directory; defaults to database parent / reports")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args(argv)
    review = build_orphan_email_evidence_review(
        database=args.database,
        delivery_log_id=args.delivery_log_id,
        job_id=args.job_id,
        report_id=args.report_id,
        artifact_root=args.artifact_root,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(_render_text(review))
    return 0


if __name__ == "__main__":
    sys.exit(main())
