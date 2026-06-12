from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from .database import MONITOR_DATA_DIR, get_job, get_report, get_conn, utc_now
from .mailer import send_report
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


REPORT_DIR = MONITOR_DATA_DIR / "reports"


def create_report(run_id: int, job: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = REPORT_DIR / f"job_{job['id']}_run_{run_id}_{stamp}"
    records = _load_report_records(run_id)
    html_text = render_html(job, summary, records)
    md_text = render_markdown(job, summary, records)
    html_path = base.with_suffix(".html")
    md_path = base.with_suffix(".md")
    xlsx_path = base.with_suffix(".xlsx")
    html_path.write_text(html_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    write_excel(xlsx_path, records)
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO reports (run_id, job_id, html_path, markdown_path, excel_path, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                job["id"],
                str(html_path),
                str(md_path),
                str(xlsx_path),
                json.dumps(summary, ensure_ascii=False),
                utc_now(),
            ),
        )
        report_id = int(cur.lastrowid)
    return {
        "id": report_id,
        "run_id": run_id,
        "job_id": job["id"],
        "law_firm_name": job.get("law_firm_name", ""),
        "summary": summary,
        "html_path": str(html_path),
        "markdown_path": str(md_path),
        "excel_path": str(xlsx_path),
        "records": records,
    }


def update_report_email_status(report_id: int, status: str, error: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE reports SET email_status=?, email_error=? WHERE id=?",
            (status, redact_sensitive(error), report_id),
        )


def resend_report_email(report_id: int) -> tuple[bool, str | None, dict[str, Any]]:
    report = get_report(report_id)
    if not report:
        raise ValueError("report not found")
    job = get_job(int(report.get("job_id") or 0)) or {
        "id": report.get("job_id"),
        "law_firm_name": report.get("law_firm_name") or "",
        "recipients": [],
    }
    ok, error = send_report(job, report)
    update_report_email_status(report_id, "sent" if ok else "failed", error)
    refreshed = get_report(report_id) or report
    return ok, error, refreshed


def render_html(job: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    risk_records = [
        r
        for r in records
        if r["risk_level"] in {"high", "medium", "low"} and r["is_related"] and r["is_negative"]
    ]
    review_records = [r for r in records if r.get("eval_status") == "pending_review"]
    high_count = sum(1 for r in risk_records if r["risk_level"] == "high")
    title = f"【律所舆情日报】{job['law_firm_name']} - {datetime.now().date()}"
    cards = "".join(
        f"<div class='card'><div class='num'>{n}</div><div>{html.escape(label)}</div></div>"
        for label, n in [
            ("新增内容", summary.get("new_contents", 0)),
            ("疑似负面", len(risk_records)),
            ("高风险", high_count),
            ("待人工复核", len(review_records)),
            ("失败平台", len(summary.get("failed_platforms", []))),
        ]
    )
    platform_summary = _render_platform_summary_html(summary)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for rec in risk_records + review_records:
        grouped.setdefault(rec["platform"], []).append(rec)
    sections = ""
    if not risk_records and not review_records:
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
<p>监控对象：{html.escape(job['law_firm_name'])}</p>
<div class="cards">{cards}</div>
{platform_summary}
{sections}
<p class="meta">说明：AI 结果仅用于舆情线索筛查，不代表事实认定，请人工复核。</p>
</div></body></html>"""


def render_markdown(job: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    risks = [r for r in records if r["is_related"] and r["is_negative"]]
    reviews = [r for r in records if r.get("eval_status") == "pending_review"]
    lines = [
        f"# 【律所舆情日报】{job['law_firm_name']} - {datetime.now().date()}",
        "",
        f"- 新增内容：{summary.get('new_contents', 0)}",
        f"- 疑似负面：{summary.get('negative_count', 0)}",
        f"- 高风险：{summary.get('high_count', 0)}",
        f"- 待人工复核：{len(reviews)}",
        "",
        "## 平台采集状态",
        "",
        *_platform_summary_markdown_lines(summary),
        "",
    ]
    if not risks and not reviews:
        lines.append("本次未发现新增疑似负面线索。")
    for rec in risks + reviews:
        lines.extend(
            [
                f"## {rec['title'] or rec['content_url']}",
                f"- 平台：{PLATFORM_LABELS.get(rec['platform'], rec['platform'])}",
                f"- 风险：{rec['risk_level']}",
                f"- 状态：{'待人工复核' if rec.get('eval_status') == 'pending_review' else 'AI 已判断'}",
                f"- 链接：{rec['content_url']}",
                f"- 封面：{rec['cover_url'] or ''}",
                f"- 理由：{rec['reason']}",
                f"- 证据：{'；'.join(rec['evidence_quotes'])}",
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
        if not (rec["is_related"] and rec["is_negative"]) and rec.get("eval_status") != "pending_review":
            continue
        ws.append(
            [
                PLATFORM_LABELS.get(rec["platform"], rec["platform"]),
                "待人工复核" if rec.get("eval_status") == "pending_review" else "AI 已判断",
                rec["risk_level"],
                rec["title"],
                rec["content_url"],
                rec["cover_url"],
                rec["author_name"],
                rec["source_keyword"],
                rec["reason"],
                "；".join(rec["evidence_quotes"]),
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
        f"<td>{html.escape(row['error'])}</td>"
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
        + (f"，说明：{row['error']}" if row["error"] else "")
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
                "error": redact_sensitive(str(result.get("error") or "")),
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
                   e.reason, e.evidence_quotes, e.recommended_action
            FROM raw_contents c
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
        result.append(item)
    return result


def _render_record(item: dict[str, Any]) -> str:
    risk = html.escape(item.get("risk_level") or "low")
    evidence = "".join(f"<div class='evidence'>{html.escape(str(q))}</div>" for q in item.get("evidence_quotes", []))
    title = html.escape(item.get("title") or item.get("content_url") or "无标题")
    url = html.escape(item.get("content_url") or "")
    cover_url = html.escape(item.get("cover_url") or "")
    review_badge = " | 状态：待人工复核" if item.get("eval_status") == "pending_review" else ""
    cover = f'<p class="meta">封面：<a href="{cover_url}">{cover_url}</a></p>' if cover_url else ""
    return f"""<div class="item risk-{risk}">
<h3>{title}</h3>
<div class="meta">风险：{risk}{review_badge} | 作者：{html.escape(item.get('author_name') or '')} | 关键词：{html.escape(item.get('source_keyword') or '')}</div>
<p><a href="{url}">{url}</a></p>
{cover}
<p>{html.escape(item.get('reason') or '')}</p>
{evidence}
</div>"""
