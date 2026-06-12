from __future__ import annotations

from typing import Any

from .database import get_ai_config, get_email_config, list_reports
from .platform_status import list_platform_status


REQUIRED_REAL_PLATFORMS = {"dy", "ks", "xhs"}


def get_readiness_status() -> dict[str, Any]:
    platforms = list_platform_status()
    ai_config = get_ai_config(masked=True)
    email_config = get_email_config(masked=True)
    reports = list_reports(200)
    selftest_reports = [report for report in reports if (report.get("summary") or {}).get("selftest")]
    real_reports = [report for report in reports if not (report.get("summary") or {}).get("selftest")]
    real_platforms = _successful_real_platforms(real_reports)
    empty_real_platforms = _empty_real_platforms(real_reports) - real_platforms
    checks = [
        _check("platform_profiles", "三平台浏览器 Profile", all(p["profile_exists"] for p in platforms), _platform_message(platforms)),
        _check("ai_config", "AI 配置", _ai_ready(ai_config), _ai_message(ai_config)),
        _check("email_config", "邮件配置", _email_ready(email_config), _email_message(email_config)),
        _check("selftest_report", "自测报告链路", bool(selftest_reports), _selftest_message(selftest_reports)),
        _check("real_report", "三平台真实采集", _real_report_ready(real_reports), _real_report_message(real_reports)),
    ]
    return {
        "ready": all(check["ok"] for check in checks),
        "checks": checks,
        "platforms": platforms,
        "real_platforms": sorted(real_platforms),
        "missing_real_platforms": sorted(REQUIRED_REAL_PLATFORMS - real_platforms),
        "empty_real_platforms": sorted(empty_real_platforms),
        "latest_selftest_report_id": selftest_reports[0]["id"] if selftest_reports else None,
        "latest_real_report_id": real_reports[0]["id"] if real_reports else None,
    }


def _check(key: str, label: str, ok: bool, message: str) -> dict[str, Any]:
    return {"key": key, "label": label, "ok": ok, "message": message}


def _platform_message(platforms: list[dict[str, Any]]) -> str:
    missing = [p["platform_label"] for p in platforms if not p["profile_exists"]]
    needs_login = [p["platform_label"] for p in platforms if p["needs_login"]]
    if missing:
        return "缺少 Profile：" + "、".join(missing)
    if needs_login:
        return "可能需要重新登录：" + "、".join(needs_login)
    return "已发现抖音、快手、小红书 Profile"


def _ai_ready(config: dict[str, Any]) -> bool:
    return _ai_fields_complete(config) and config.get("last_test_status") == "success"


def _ai_message(config: dict[str, Any]) -> str:
    if not _ai_fields_complete(config):
        return "需填写 Base URL、API Key、Model，并点击测试 AI"
    if config.get("last_test_status") == "success":
        return f"最近测试通过：{config.get('provider')} / {config.get('model')}（{_format_time(config.get('last_test_at'))}）"
    if config.get("last_test_status") == "failed":
        return "最近测试失败：" + (config.get("last_test_error") or "请检查 AI 配置")
    return "配置已填写，但还未完成测试"


def _email_ready(config: dict[str, Any]) -> bool:
    return _email_fields_complete(config) and config.get("last_test_status") == "success"


def _email_message(config: dict[str, Any]) -> str:
    if not _email_fields_complete(config):
        return "需填写 SMTP、发件人、收件人，并点击测试邮件"
    if config.get("last_test_status") == "success":
        return f"最近测试通过：{config.get('smtp_host')}（{_format_time(config.get('last_test_at'))}）"
    if config.get("last_test_status") == "failed":
        return "最近测试失败：" + (config.get("last_test_error") or "请检查 SMTP 配置")
    return "配置已填写，但还未完成测试邮件发送"


def _ai_fields_complete(config: dict[str, Any]) -> bool:
    return bool(config.get("base_url") and config.get("api_key") and config.get("model"))


def _email_fields_complete(config: dict[str, Any]) -> bool:
    return bool(config.get("smtp_host") and config.get("sender") and config.get("default_recipients"))


def _format_time(value: Any) -> str:
    text = str(value or "")
    if not text:
        return "时间未知"
    return text.replace("T", " ")[:19]


def _selftest_message(reports: list[dict[str, Any]]) -> str:
    if reports:
        return f"最近自测报告 ID：{reports[0]['id']}"
    return "可在报告中心点击“生成自测报告”验证报告链路"


def _real_report_message(reports: list[dict[str, Any]]) -> str:
    if not reports:
        return "尚未完成真实平台采集报告"
    successful = _successful_real_platforms(reports)
    missing = REQUIRED_REAL_PLATFORMS - successful
    if missing:
        empty = _empty_real_platforms(reports) - successful
        parts = []
        if empty:
            parts.append("已运行但未采到内容：" + "、".join(_platform_label(p) for p in sorted(empty)))
        not_run = missing - empty
        if not_run:
            parts.append("还需完成真实采集：" + "、".join(_platform_label(p) for p in sorted(not_run)))
        return "；".join(parts) if parts else "还需完成真实采集：" + "、".join(_platform_label(p) for p in sorted(missing))
    return f"三平台均已完成真实采集，最近真实报告 ID：{reports[0]['id']}"


def _real_report_ready(reports: list[dict[str, Any]]) -> bool:
    return REQUIRED_REAL_PLATFORMS <= _successful_real_platforms(reports)


def _successful_real_platforms(reports: list[dict[str, Any]]) -> set[str]:
    successful: set[str] = set()
    for report in reports:
        summary = report.get("summary") or {}
        failed = set(summary.get("failed_platforms") or [])
        platform_results = summary.get("platform_results") or {}
        for platform in REQUIRED_REAL_PLATFORMS:
            result = platform_results.get(platform)
            if platform in failed or not isinstance(result, dict):
                continue
            if result.get("status") == "success" and _platform_result_has_content(result):
                successful.add(platform)
    return successful


def _empty_real_platforms(reports: list[dict[str, Any]]) -> set[str]:
    empty: set[str] = set()
    for report in reports:
        summary = report.get("summary") or {}
        failed = set(summary.get("failed_platforms") or [])
        platform_results = summary.get("platform_results") or {}
        for platform in REQUIRED_REAL_PLATFORMS:
            result = platform_results.get(platform)
            if platform in failed or not isinstance(result, dict):
                continue
            if result.get("status") == "success" and not _platform_result_has_content(result):
                empty.add(platform)
    return empty


def _platform_result_has_content(result: dict[str, Any]) -> bool:
    for key in ("raw_contents", "filtered_contents", "new_contents"):
        try:
            if int(result.get(key) or 0) > 0:
                return True
        except (TypeError, ValueError):
            continue
    return False


def _platform_label(platform: str) -> str:
    return {"dy": "抖音", "ks": "快手", "xhs": "小红书"}.get(platform, platform)
