from __future__ import annotations

from typing import Any

from .database import get_ai_config, get_email_config, has_job_template_placeholders
from .platform_status import list_platform_status


PLATFORM_LABELS = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}


def build_job_preflight(job: dict[str, Any], running_jobs: list[int] | None = None) -> dict[str, Any]:
    running_set = {int(item) for item in (running_jobs or [])}
    job_id = int(job.get("id") or 0)
    checks = [
        _check(
            "running_state",
            "运行状态",
            "blocking" if job_id in running_set else "ok",
            "该任务正在运行，请等待本轮结束" if job_id in running_set else "当前没有同任务运行中",
        ),
        _check(
            "job_enabled",
            "定时状态",
            "ok" if job.get("enabled") else "warning",
            "任务已启用，会按频率自动运行" if job.get("enabled") else "任务已暂停；仍可手动运行，但不会定时触发",
        ),
        _check(
            "keywords",
            "关键词",
            "ok" if job.get("keywords") else "blocking",
            "已配置关键词" if job.get("keywords") else "未配置关键词",
        ),
        _check(
            "platforms",
            "采集平台",
            "ok" if job.get("platforms") else "blocking",
            "已选择：" + _format_platforms(job.get("platforms") or []) if job.get("platforms") else "未选择平台",
        ),
        _template_placeholder_check(job),
        _platform_profile_check(job),
        _ai_config_check(),
        _email_config_check(job),
    ]
    blockers = [item["message"] for item in checks if item["severity"] == "blocking"]
    warnings = [item["message"] for item in checks if item["severity"] == "warning"]
    return {
        "can_run": not blockers,
        "ready": not blockers and not warnings,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
    }


def _template_placeholder_check(job: dict[str, Any]) -> dict[str, Any]:
    if has_job_template_placeholders(job):
        return _check("template_placeholders", "任务内容", "blocking", "请先把验收模板里的律所名称和关键词改成真实内容")
    return _check("template_placeholders", "任务内容", "ok", "任务内容已替换为真实律所和关键词")


def _platform_profile_check(job: dict[str, Any]) -> dict[str, Any]:
    selected = set(job.get("platforms") or [])
    statuses = {item["platform"]: item for item in list_platform_status()}
    missing = []
    missing_cookie = []
    needs_login = []
    open_windows = []
    for platform in selected:
        status = statuses.get(platform)
        if not status:
            missing.append(platform)
            continue
        if status.get("login_type") == "cookie" and not status.get("has_cookies"):
            missing_cookie.append(platform)
        elif status.get("login_window_open"):
            open_windows.append(platform)
        elif status.get("needs_login"):
            needs_login.append(platform)
    if missing:
        return _check("platform_profiles", "平台登录态", "warning", "缺少平台状态：" + _format_platforms(missing))
    if missing_cookie:
        return _check("platform_profiles", "平台登录态", "warning", "Cookie 登录未填写 Cookie：" + _format_platforms(missing_cookie))
    if open_windows:
        return _check("platform_profiles", "平台登录态", "blocking", "请先关闭登录窗口再运行采集：" + _format_platforms(open_windows))
    if needs_login:
        return _check("platform_profiles", "平台登录态", "blocking", "请先重新登录再运行采集：" + _format_platforms(needs_login))
    return _check("platform_profiles", "平台登录态", "ok", "所选平台登录配置可用")


def _ai_config_check() -> dict[str, Any]:
    cfg = get_ai_config(masked=True)
    complete = bool(cfg.get("base_url") and cfg.get("api_key") and cfg.get("model"))
    if not complete:
        return _check("ai_config", "AI 配置", "warning", "AI 未配置完整；本轮会生成报告，但内容会进入待人工复核")
    if cfg.get("last_test_status") != "success":
        return _check("ai_config", "AI 配置", "warning", "AI 配置未测试通过；建议先测试 AI")
    return _check("ai_config", "AI 配置", "ok", "AI 最近测试通过")


def _email_config_check(job: dict[str, Any]) -> dict[str, Any]:
    cfg = get_email_config(masked=True)
    recipients = job.get("recipients") or cfg.get("default_recipients") or []
    if not recipients:
        return _check("email_config", "邮件配置", "warning", "未配置收件人；报告会生成，但不会发出日报")
    complete = bool(cfg.get("smtp_host") and cfg.get("sender"))
    if not complete:
        return _check("email_config", "邮件配置", "warning", "SMTP 未配置完整；报告会生成，但邮件发送会失败")
    if cfg.get("last_test_status") != "success":
        return _check("email_config", "邮件配置", "warning", "邮件配置未测试通过；建议先发送测试邮件")
    return _check("email_config", "邮件配置", "ok", "邮件最近测试通过")


def _check(key: str, label: str, severity: str, message: str) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "severity": severity,
        "ok": severity == "ok",
        "message": message,
    }


def _format_platforms(platforms: list[str] | set[str]) -> str:
    return " / ".join(PLATFORM_LABELS.get(platform, platform) for platform in sorted(platforms))
