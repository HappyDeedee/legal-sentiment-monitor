from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from .database import (
    MONITOR_DATA_DIR,
    apply_lead_status_fields,
    email_send_window_key,
    get_job,
    get_report,
    get_conn,
    record_email_delivery_log,
    effective_email_template_provenance,
    report_job_snapshot,
    report_job_snapshot_json,
    try_record_email_delivery_log,
    update_email_delivery_log_status,
    utc_now,
)
from .mailer import REAL_EMAIL_BLOCKED_MESSAGE, resolve_report_recipients, send_report
from .normalizer import PLATFORM_LABELS
from .security import customer_safe_text, customer_safe_url, redact_sensitive


REPORT_DIR = MONITOR_DATA_DIR / "reports"
MEDIA_LINK_REDACTED_LABEL = "媒体链接已脱敏"


def create_report(run_id: int, job: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = REPORT_DIR / f"job_{job['id']}_run_{run_id}_{stamp}"
    records = _load_report_records(run_id)
    summary.update(_record_lead_count_summary(records))
    html_text = render_html(job, summary, records)
    md_text = render_markdown(job, summary, records)
    html_path = base.with_suffix(".html")
    md_path = base.with_suffix(".md")
    xlsx_path = base.with_suffix(".xlsx")
    html_path.write_text(html_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    write_excel(xlsx_path, records)
    snapshot_json = report_job_snapshot_json(job)
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO reports (
                workspace_id, run_id, job_id, html_path, markdown_path, excel_path,
                job_snapshot_json, summary, created_by, updated_by, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(job.get("workspace_id") or 1),
                run_id,
                job["id"],
                str(html_path),
                str(md_path),
                str(xlsx_path),
                snapshot_json,
                json.dumps(summary, ensure_ascii=False),
                job.get("created_by"),
                job.get("created_by"),
                utc_now(),
            ),
        )
        report_id = int(cur.lastrowid)
    return {
        "id": report_id,
        "run_id": run_id,
        "job_id": job["id"],
        "law_firm_name": job.get("law_firm_name", ""),
        "job_snapshot": report_job_snapshot(job),
        "job_snapshot_json": snapshot_json,
        "summary": summary,
        "html_path": str(html_path),
        "markdown_path": str(md_path),
        "excel_path": str(xlsx_path),
        "records": records,
    }


def _record_lead_count_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "lead_total_count": len(records),
        "pending_review_count": sum(1 for item in records if item.get("lead_status") == "pending_review"),
        "negative_count": sum(1 for item in records if item.get("lead_status") in {"high_risk", "suspected_negative"}),
        "high_count": sum(1 for item in records if item.get("lead_status") == "high_risk"),
        "unrelated_count": sum(1 for item in records if item.get("lead_status") == "unrelated"),
        "no_risk_count": sum(1 for item in records if item.get("lead_status") == "no_risk"),
        "unevaluated_count": sum(1 for item in records if item.get("lead_status") in {"unevaluated", "limited_context"}),
        "limited_context_count": sum(1 for item in records if item.get("lead_status") == "limited_context"),
    }


def update_report_email_status(report_id: int, status: str, error: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE reports SET email_status=?, email_error=? WHERE id=?",
            (status, redact_sensitive(error), report_id),
        )


def send_report_with_delivery_log(
    job: dict[str, Any],
    report: dict[str, Any],
    *,
    send_type: str = "auto",
    actor: dict[str, Any] | None = None,
    sent_at: datetime | None = None,
    allow_real_send: bool | None = None,
) -> tuple[bool, str | None, dict[str, Any], dict[str, Any] | None]:
    send_at = sent_at or datetime.now(timezone.utc)
    if send_type == "manual_resend":
        return _send_report_manual_resend(job, report, actor, send_at, allow_real_send=allow_real_send)
    if send_type != "auto":
        raise ValueError("invalid email send type")
    return _send_report_auto(job, report, send_at)


def resend_report_email(report_id: int, actor: dict[str, Any] | None = None, *, allow_real_send: bool | None = None) -> tuple[bool, str | None, dict[str, Any]]:
    report = get_report(report_id)
    if not report:
        raise ValueError("report not found")
    job = get_job(int(report.get("job_id") or 0)) or {
        "id": report.get("job_id"),
        "law_firm_name": report.get("law_firm_name") or "",
        "recipients": [],
    }
    ok, error, _refreshed_report, _log = send_report_with_delivery_log(job, report, send_type="manual_resend", actor=actor, allow_real_send=allow_real_send)
    refreshed = get_report(report_id) or report
    return ok, error, refreshed


def _send_report_auto(job: dict[str, Any], report: dict[str, Any], send_at: datetime) -> tuple[bool, str | None, dict[str, Any], dict[str, Any] | None]:
    window_key = email_send_window_key(int(job.get("id") or report.get("job_id") or 0), str(job.get("frequency") or "daily"), send_at)
    delivery_meta = _delivery_metadata(job, trigger_source="scheduler_auto")
    pending = try_record_email_delivery_log(
        {
            "workspace_id": job.get("workspace_id") or report.get("workspace_id"),
            "job_id": job.get("id") or report.get("job_id"),
            "report_id": report.get("id"),
            "send_window_key": window_key,
            "send_type": "auto",
            "sent_at": send_at.isoformat(),
            "status": "pending",
            **delivery_meta,
        }
    )
    if pending is None:
        message = "同一任务和发送窗口已存在自动邮件交付记录，已跳过重复发送"
        record_email_delivery_log(
            {
                "workspace_id": job.get("workspace_id") or report.get("workspace_id"),
                "job_id": job.get("id") or report.get("job_id"),
                "report_id": report.get("id"),
                "send_window_key": window_key,
                "send_type": "auto",
                "sent_at": send_at.isoformat(),
                "status": "skipped",
                "error_message": message,
                **delivery_meta,
            }
        )
        update_report_email_status(int(report["id"]), "skipped", message)
        refreshed = get_report(int(report["id"])) or report
        return False, message, refreshed, None
    ok, error = send_report(job, report)
    safe_error = redact_sensitive(error)
    status = "sent" if ok else _delivery_failure_status(error)
    log = update_email_delivery_log_status(int(pending["id"]), status, safe_error, send_at.isoformat())
    update_report_email_status(int(report["id"]), status, safe_error)
    refreshed = get_report(int(report["id"])) or report
    return ok, safe_error, refreshed, log


def _send_report_manual_resend(
    job: dict[str, Any],
    report: dict[str, Any],
    actor: dict[str, Any] | None,
    send_at: datetime,
    *,
    allow_real_send: bool | None = None,
) -> tuple[bool, str | None, dict[str, Any], dict[str, Any]]:
    delivery_meta = _delivery_metadata(job, trigger_source="manual_resend")
    ok, error = send_report(job, report, allow_real_send=allow_real_send)
    safe_error = redact_sensitive(error)
    status = "sent" if ok else _delivery_failure_status(error)
    log = record_email_delivery_log(
        {
            "workspace_id": job.get("workspace_id") or report.get("workspace_id"),
            "job_id": job.get("id") or report.get("job_id"),
            "report_id": report.get("id"),
            "send_window_key": email_send_window_key(int(job.get("id") or report.get("job_id") or 0), str(job.get("frequency") or "daily"), send_at),
            "send_type": "manual_resend",
            "sent_by": (actor or {}).get("id"),
            "sent_at": send_at.isoformat(),
            "status": status,
            "error_message": safe_error,
            **delivery_meta,
        }
    )
    update_report_email_status(int(report["id"]), status, safe_error)
    refreshed = get_report(int(report["id"])) or report
    return ok, safe_error, refreshed, log


def _delivery_recipients(job: dict[str, Any]) -> list[str]:
    recipients = job.get("recipients") or []
    if recipients:
        return [str(item).strip() for item in recipients if str(item).strip()]
    return []


def _delivery_metadata(job: dict[str, Any], *, trigger_source: str) -> dict[str, Any]:
    recipients = _delivery_recipients(job)
    effective_recipients, effective_source = resolve_report_recipients(job)
    template = effective_email_template_provenance(job)
    return {
        "recipients": recipients,
        "trigger_source": trigger_source,
        "effective_recipients": effective_recipients,
        "effective_recipient_source": effective_source,
        "email_template_id": template.get("id"),
        "email_template_name": template.get("name") or "",
        "email_template_source": template.get("source") or "",
        "email_subject_template": template.get("subject_template") or "",
    }


def _delivery_failure_status(error: str | None) -> str:
    return "skipped" if error == REAL_EMAIL_BLOCKED_MESSAGE else "failed"


def render_html(job: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    risk_records = [
        r
        for r in records
        if r.get("lead_status") in {"high_risk", "suspected_negative"}
    ]
    review_records = [r for r in records if r.get("lead_status") == "pending_review"]
    unevaluated_records = [r for r in records if r.get("lead_status") in {"unevaluated", "limited_context"}]
    high_count = sum(1 for r in risk_records if r["risk_level"] == "high")
    law_firm_name = customer_safe_text(job["law_firm_name"])
    title = f"【律所舆情日报】{law_firm_name} - {datetime.now().date()}"
    cards = "".join(
        f"<div class='card'><div class='num'>{n}</div><div>{html.escape(label)}</div></div>"
        for label, n in [
            ("新增内容", summary.get("new_contents", 0)),
            ("疑似负面", len(risk_records)),
            ("高风险", high_count),
            ("待人工复核", len(review_records)),
            ("未评估/上下文有限", len(unevaluated_records)),
            ("失败平台", len(summary.get("failed_platforms", []))),
        ]
    )
    platform_summary = _render_platform_summary_html(summary)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for rec in risk_records + review_records + unevaluated_records:
        grouped.setdefault(rec["platform"], []).append(rec)
    sections = ""
    if not risk_records and not review_records and not unevaluated_records:
        sections = "<p class='empty'>本次未发现新增疑似负面线索。</p>"
    else:
        for platform, items in grouped.items():
            body = "".join(_render_record(item) for item in items)
            sections += f"<h2>{html.escape(PLATFORM_LABELS.get(platform, platform))}</h2>{body}"
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
body{{font-family:Arial,'Microsoft YaHei',sans-serif;color:#1f2937;line-height:1.6;background:#f8fafc;padding:24px}}
.wrap{{max-width:920px;margin:auto;background:#fff;border:1px solid #e5e7eb;padding:24px}}
h1{{font-size:22px;margin:0 0 16px}}h2{{font-size:18px;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-top:24px}}
.cards{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}.card{{border:1px solid #e5e7eb;padding:12px 16px;min-width:120px;background:#fafafa}}
.num{{font-size:24px;font-weight:700}}.item{{border:1px solid #e5e7eb;margin:12px 0;padding:14px;border-left:4px solid #f59e0b}}
.risk-high{{border-left-color:#dc2626}}.risk-medium{{border-left-color:#f59e0b}}.risk-low{{border-left-color:#2563eb}}
.meta{{color:#64748b;font-size:13px}}.evidence{{background:#f8fafc;border-left:3px solid #cbd5e1;padding:8px;margin-top:8px}}
.empty{{padding:20px;background:#f0fdf4;border:1px solid #bbf7d0}}.warn{{color:#b45309}}.platforms{{border:1px solid #e5e7eb;border-collapse:collapse;width:100%;margin:12px 0}}.platforms th,.platforms td{{border:1px solid #e5e7eb;padding:8px;text-align:left;font-size:13px}}a{{color:#2563eb}}
</style></head><body><div class="wrap">
<h1>{html.escape(title)}</h1>
<p>律所：{html.escape(law_firm_name)}</p>
<div class="cards">{cards}</div>
{platform_summary}
{sections}
<p class="meta">说明：AI 结果仅用于舆情线索筛查，不代表事实认定，请人工复核。</p>
</div></body></html>"""


def render_markdown(job: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    risks = [r for r in records if r.get("lead_status") in {"high_risk", "suspected_negative"}]
    reviews = [r for r in records if r.get("lead_status") == "pending_review"]
    unevaluated = [r for r in records if r.get("lead_status") in {"unevaluated", "limited_context"}]
    lines = [
        f"# 【律所舆情日报】{customer_safe_text(job['law_firm_name'])} - {datetime.now().date()}",
        "",
        f"- 新增内容：{summary.get('new_contents', 0)}",
        f"- 疑似负面：{summary.get('negative_count', 0)}",
        f"- 高风险：{summary.get('high_count', 0)}",
        f"- 待人工复核：{len(reviews)}",
        f"- 未评估/上下文有限：{len(unevaluated)}",
        "",
        "## 平台采集状态",
        "",
        *_platform_summary_markdown_lines(summary),
        "",
    ]
    if not risks and not reviews and not unevaluated:
        lines.append("本次未发现新增疑似负面线索。")
    for rec in risks + reviews + unevaluated:
        content_url = _safe_report_content_url(rec.get("content_url"))
        cover_label = _safe_report_media_url(rec.get("cover_url"))
        lines.extend(
            [
                f"## {customer_safe_text(rec['title'] or content_url)}",
                f"- 平台：{PLATFORM_LABELS.get(rec['platform'], rec['platform'])}",
                f"- 风险：{rec['risk_level']}",
                f"- 状态：{rec.get('lead_status_label') or ('待人工复核' if rec.get('eval_status') == 'pending_review' else 'AI 已判断')}",
                f"- 链接：{content_url}",
                f"- 封面：{cover_label}",
                f"- 理由：{customer_safe_text(rec['reason'])}",
                f"- 证据：{customer_safe_text('；'.join(rec['evidence_quotes']))}",
                "",
            ]
        )
    lines.append("> AI 结果仅用于舆情线索筛查，不代表事实认定，请人工复核。")
    return "\n".join(lines)


def write_excel(path: Path, records: list[dict[str, Any]]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "风险线索"
    headers = ["平台", "状态", "风险等级", "标题", "链接", "封面链接", "作者", "关键词", "AI理由", "证据原文"]
    ws.append(headers)
    for rec in records:
        if rec.get("lead_status") not in {"high_risk", "suspected_negative", "pending_review", "unevaluated", "limited_context"}:
            continue
        ws.append(
            [
                PLATFORM_LABELS.get(rec["platform"], rec["platform"]),
                rec.get("lead_status_label") or ("待人工复核" if rec.get("eval_status") == "pending_review" else "AI 已判断"),
                rec["risk_level"],
                customer_safe_text(rec["title"]),
                _safe_report_content_url(rec["content_url"]),
                _safe_report_media_url(rec["cover_url"]),
                rec["author_name"],
                rec["source_keyword"],
                customer_safe_text(rec["reason"]),
                customer_safe_text("；".join(rec["evidence_quotes"])),
            ]
        )
    wb.save(path)


def _render_platform_summary_html(summary: dict[str, Any]) -> str:
    rows = _platform_summary_rows(summary)
    if not rows:
        return ""
    body = "".join(
        "<tr>"
        f"<td>{html.escape(row['platform_label'])}</td>"
        f"<td>{html.escape(row['status_label'])}</td>"
        f"<td>{row['raw_contents']}</td>"
        f"<td>{row['new_contents']}</td>"
        f"<td>{html.escape(row['proxy_label'])}</td>"
        f"<td>{html.escape(customer_safe_text(row['error']))}</td>"
        "</tr>"
        for row in rows
    )
    return (
        "<h2>平台采集状态</h2>"
        "<table class='platforms'><thead><tr><th>平台</th><th>状态</th><th>采集数</th><th>新增数</th><th>代理</th><th>说明</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )


def _platform_summary_markdown_lines(summary: dict[str, Any]) -> list[str]:
    rows = _platform_summary_rows(summary)
    if not rows:
        return ["- 暂无平台采集状态。"]
    return [
        f"- {row['platform_label']}：{row['status_label']}，采集 {row['raw_contents']}，新增 {row['new_contents']}"
        + (f"，代理：{row['proxy_label']}" if row["proxy_label"] else "")
        + (f"，说明：{customer_safe_text(row['error'])}" if row["error"] else "")
        for row in rows
    ]


def _platform_summary_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    platforms = summary.get("platforms") or list((summary.get("platform_results") or {}).keys())
    platform_results = summary.get("platform_results") or {}
    failed = set(summary.get("failed_platforms") or [])
    rows: list[dict[str, Any]] = []
    for platform in platforms:
        result = platform_results.get(platform) if isinstance(platform_results.get(platform), dict) else {}
        is_failed = platform in failed or result.get("status") == "failed"
        rows.append(
            {
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "status_label": "失败" if is_failed else "成功",
                "raw_contents": int(result.get("raw_contents") or 0),
                "new_contents": int(result.get("new_contents") or 0),
                "proxy_label": _format_proxy_label(result.get("proxy")),
                "error": customer_safe_text(str(result.get("error") or "")),
            }
        )
    return rows


def _format_proxy_label(proxy: Any) -> str:
    if not isinstance(proxy, dict):
        return ""
    parts = [
        str(proxy.get("proxy_name") or "").strip(),
        str(proxy.get("provider") or "").strip(),
    ]
    label = " / ".join(part for part in parts if part)
    if proxy.get("proxy_id"):
        label = f"{label} #{proxy['proxy_id']}" if label else f"#{proxy['proxy_id']}"
    return redact_sensitive(label)


def _load_report_records(run_id: int) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT c.*, e.status AS eval_status, e.is_related, e.is_negative, e.risk_level,
                   e.id AS evaluation_id, e.reason, e.evidence_quotes, e.recommended_action,
                   r.status AS run_status
            FROM raw_contents c
            LEFT JOIN crawl_runs r ON r.id = c.run_id
            LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
            WHERE c.run_id=?
            ORDER BY
              CASE e.risk_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END,
              c.id DESC
            """,
            (run_id,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["evidence_quotes"] = json.loads(item.get("evidence_quotes") or "[]")
        except json.JSONDecodeError:
            item["evidence_quotes"] = []
        item["is_negative"] = bool(item.get("is_negative"))
        item["is_related"] = bool(item.get("is_related"))
        for key in ("title", "description", "author_name", "source_keyword", "reason", "recommended_action"):
            item[key] = customer_safe_text(item.get(key))
        item["evidence_quotes"] = [customer_safe_text(str(q)) for q in item.get("evidence_quotes", [])]
        apply_lead_status_fields(item)
        result.append(item)
    return result


def _render_record(item: dict[str, Any]) -> str:
    risk = html.escape(item.get("risk_level") or "low")
    evidence = "".join(f"<div class='evidence'>{html.escape(customer_safe_text(str(q)))}</div>" for q in item.get("evidence_quotes", []))
    safe_content_url = _safe_report_content_url(item.get("content_url"))
    safe_cover = _safe_report_media_url(item.get("cover_url"))
    title = html.escape(customer_safe_text(item.get("title") or safe_content_url or "无标题"))
    url = html.escape(safe_content_url)
    cover_label = html.escape(safe_cover)
    review_badge = f" | 状态：{html.escape(customer_safe_text(item.get('lead_status_label') or 'AI 已判断'))}"
    cover = f'<p class="meta">封面：{cover_label}</p>' if cover_label else ""
    return f"""<div class="item risk-{risk}">
<h3>{title}</h3>
<div class="meta">风险：{risk}{review_badge} | 作者：{html.escape(customer_safe_text(item.get('author_name') or ''))} | 关键词：{html.escape(customer_safe_text(item.get('source_keyword') or ''))}</div>
<p><a href="{url}">{url}</a></p>
{cover}
<p>{html.escape(customer_safe_text(item.get('reason') or ''))}</p>
{evidence}
</div>"""


def _safe_report_content_url(value: Any) -> str:
    return customer_safe_url(value, redact_query=True)


def _safe_report_media_url(value: Any) -> str:
    return customer_safe_url(value, redact_query=True, redacted_label=MEDIA_LINK_REDACTED_LABEL)
