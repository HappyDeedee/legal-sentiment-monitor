from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from .database import get_active_email_template, get_email_config, get_email_template, validate_port, validate_recipients
from .normalizer import PLATFORM_LABELS
from .security import customer_safe_text


def send_report(job: dict[str, Any], report: dict[str, Any]) -> tuple[bool, str | None]:
    cfg = get_email_config(masked=False)
    recipients = job.get("recipients") or cfg.get("default_recipients") or []
    if not recipients:
        return False, "未配置收件人"
    if not cfg.get("smtp_host") or not cfg.get("sender"):
        return False, "SMTP 配置未完成"
    try:
        template = _job_email_template(job)
        subject_template = (template or {}).get("subject_template") or cfg.get("subject_template") or "【律所舆情日报】{law_firm_name} - {date}"
        values = _template_values(job, report, "")
        subject = customer_safe_text(_safe_format(subject_template, values))
        msg = build_report_email(cfg, recipients, subject, report, job)
        _smtp_send(cfg, msg)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def build_report_email(
    cfg: dict[str, Any],
    recipients: list[str],
    subject: str,
    report: dict[str, Any],
    job: dict[str, Any] | None = None,
) -> EmailMessage:
    html_body = customer_safe_text(Path(report["html_path"]).read_text(encoding="utf-8"))
    template = _job_email_template(job or {})
    if template and template.get("html_template"):
        html_body = customer_safe_text(_safe_format(template["html_template"], _template_values(job or {}, report, html_body)))
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg["sender"]
    msg["To"] = ", ".join(recipients)
    msg.set_content("请使用支持 HTML 的邮件客户端查看舆情日报。")
    msg.add_alternative(html_body, subtype="html")
    for key in ("excel_path", "markdown_path"):
        path = Path(report[key])
        if path.exists():
            maintype, subtype = _attachment_mime(path)
            msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    return msg


def render_report_email_preview(job: dict[str, Any], report: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, str]:
    cfg = cfg or get_email_config(masked=False)
    template = _job_email_template(job)
    subject_template = (template or {}).get("subject_template") or cfg.get("subject_template") or "【律所舆情日报】{law_firm_name} - {date}"
    subject = customer_safe_text(_safe_format(subject_template, _template_values(job, report, "")))
    sender = cfg.get("sender") or "preview@example.com"
    msg = build_report_email({"sender": sender}, ["preview@example.com"], subject, report, job)
    return {"subject": subject, "html": _email_html_body(msg)}


def _job_email_template(job: dict[str, Any]) -> dict[str, Any] | None:
    template_id = job.get("email_template_id")
    if template_id:
        try:
            template = get_email_template(int(template_id))
        except (TypeError, ValueError):
            template = None
        if template:
            return template
    return get_active_email_template()


def _template_values(job: dict[str, Any], report: dict[str, Any], report_html: str) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    law_firm_name = (
        job.get("law_firm_name")
        or report.get("law_firm_name")
        or report.get("display_law_firm_name")
        or summary.get("law_firm_name")
        or ""
    )
    platforms = summary.get("platforms") or list((summary.get("platform_results") or {}).keys())
    return {
        "law_firm_name": customer_safe_text(law_firm_name),
        "date": __import__("datetime").date.today().isoformat(),
        "new_contents": summary.get("new_contents", 0),
        "negative_count": summary.get("negative_count", 0),
        "high_count": summary.get("high_count", 0),
        "pending_review_count": summary.get("pending_review_count", 0),
        "platforms": " / ".join(PLATFORM_LABELS.get(platform, platform) for platform in platforms),
        "report_html": report_html,
        "report_body": report_html,
    }


def _safe_format(template: str, values: dict[str, Any]) -> str:
    try:
        return (template or "").format_map(_FormatDict(values))
    except Exception:
        return template or ""


class _FormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _attachment_mime(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if suffix == ".md":
        return "text", "markdown"
    if suffix == ".html":
        return "text", "html"
    return "application", "octet-stream"


def _email_html_body(msg: EmailMessage) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()
    return ""


def send_test_email(payload: dict[str, Any] | None = None) -> None:
    cfg = _merge_test_config(payload or {})
    target = (payload or {}).get("target") or (cfg.get("default_recipients") or [None])[0]
    if not target:
        raise ValueError("未配置测试收件人")
    validate_recipients([str(target)])
    if not cfg.get("smtp_host") or not cfg.get("sender"):
        raise ValueError("SMTP 配置未完成")
    msg = EmailMessage()
    msg["Subject"] = "律所舆情运营系统测试邮件"
    msg["From"] = cfg["sender"]
    msg["To"] = target
    msg.set_content("测试邮件发送成功。")
    _smtp_send(cfg, msg)


def _smtp_send(cfg: dict[str, Any], msg: EmailMessage) -> None:
    port = int(cfg.get("smtp_port") or 465)
    encryption = cfg.get("encryption") or "ssl"
    if encryption == "ssl":
        client = smtplib.SMTP_SSL(cfg["smtp_host"], port, timeout=30)
    else:
        client = smtplib.SMTP(cfg["smtp_host"], port, timeout=30)
    try:
        if encryption == "starttls":
            client.starttls()
        if cfg.get("username"):
            client.login(cfg["username"], cfg.get("password") or "")
        client.send_message(msg)
    finally:
        client.quit()


def _merge_test_config(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = get_email_config(masked=False)
    for key in (
        "smtp_host",
        "smtp_port",
        "encryption",
        "sender",
        "username",
        "password",
        "subject_template",
        "default_recipients",
    ):
        value = payload.get(key)
        if value not in (None, ""):
            cfg[key] = value
    cfg["smtp_port"] = validate_port(cfg.get("smtp_port") or 465)
    if cfg.get("encryption") not in {"ssl", "starttls", "none"}:
        raise ValueError("invalid email encryption")
    validate_recipients([str(e).strip() for e in cfg.get("default_recipients", []) if str(e).strip()])
    return cfg
