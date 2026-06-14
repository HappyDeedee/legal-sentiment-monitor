from __future__ import annotations

from typing import Any

from .ai import ai_api_disabled
from .database import get_active_ai_key_profile, get_ai_config, get_email_config, list_reports
from .platform_status import list_platform_status
from .security import customer_safe_text


REQUIRED_REAL_PLATFORMS = {"dy"}
OPTIONAL_REAL_PLATFORMS = {"ks", "xhs"}


def get_readiness_status() -> dict[str, Any]:
    platforms = list_platform_status()
    ai_config = get_active_ai_key_profile(masked=True) or get_ai_config(masked=True)
    email_config = get_email_config(masked=True)
    reports = list_reports(0)
    selftest_reports = [report for report in reports if (report.get("summary") or {}).get("selftest")]
    real_reports = [report for report in reports if not (report.get("summary") or {}).get("selftest")]
    real_platforms = _successful_real_platforms(real_reports)
    empty_real_platforms = _empty_real_platforms(real_reports) - real_platforms
    checks = [
        _check("platform_profiles", "平台登录配置", _platform_profiles_ready(platforms), _platform_message(platforms)),
        _check("ai_config", "AI 接入", _ai_ready(ai_config), _ai_message(ai_config)),
        _check("email_config", "邮件配置", _email_ready(email_config), _email_message(email_config)),
        _check("selftest_report", "系统自检报告链路", bool(selftest_reports), _selftest_message(selftest_reports)),
        _check("real_report", "抖音采集报告", _real_report_ready(real_reports), _real_report_message(real_reports)),
    ]
    return {
        "ready": all(check["ok"] for check in checks),
        "checks": checks,
        "next_actions": _next_actions(checks, platforms, real_platforms, empty_real_platforms),
        "platforms": platforms,
        "real_platforms": sorted(real_platforms),
        "missing_real_platforms": sorted(REQUIRED_REAL_PLATFORMS - real_platforms),
        "empty_real_platforms": sorted(empty_real_platforms),
        "latest_selftest_report_id": selftest_reports[0]["id"] if selftest_reports else None,
        "latest_real_report_id": real_reports[0]["id"] if real_reports else None,
    }


def get_acceptance_checklist() -> dict[str, Any]:
    readiness = get_readiness_status()
    checks_by_key = {check["key"]: check for check in readiness.get("checks", [])}
    platforms = readiness.get("platforms") or []
    required_platforms = _required_platform_items(platforms)
    platform_names = {
        "needs_login": "、".join(p["platform_label"] for p in required_platforms if p.get("needs_login")),
        "open_windows": "、".join(p["platform_label"] for p in required_platforms if p.get("login_window_open")),
        "missing_real": "、".join(_platform_label(p) for p in readiness.get("missing_real_platforms") or []),
    }
    items = [
        _acceptance_item(
            "platform_login",
            "平台登录态",
            checks_by_key.get("platform_profiles"),
            "accounts",
            "优先完成抖音账号登录；快手、小红书作为后续扩展资源预留。",
            platform_names["needs_login"] or platform_names["open_windows"] or "平台登录态可用",
        ),
        _acceptance_item(
            "ai_profile",
            "AI 接入连接测试",
            checks_by_key.get("ai_config"),
            "ai",
            "配置 OpenAI Compatible 或 Anthropic，并完成连接测试。",
            checks_by_key.get("ai_config", {}).get("message", ""),
        ),
        _acceptance_item(
            "email_smtp",
            "SMTP 测试邮件",
            checks_by_key.get("email_config"),
            "email",
            "填写 SMTP、发件人、默认收件人，发送测试邮件并确认收件箱收到。",
            checks_by_key.get("email_config", {}).get("message", ""),
        ),
        _acceptance_item(
            "selftest_report",
            "系统自检报告链路",
            checks_by_key.get("selftest_report"),
            "reports",
            "生成系统自检报告，确认 HTML、Excel、Markdown 可预览或下载。",
            checks_by_key.get("selftest_report", {}).get("message", ""),
        ),
        _acceptance_item(
            "real_three_platform_report",
            "抖音采集报告",
            checks_by_key.get("real_report"),
            "jobs",
            "使用海安律所避雷、海安律所退费、海安律所投诉优先完成抖音采集闭环。",
            platform_names["missing_real"] or checks_by_key.get("real_report", {}).get("message", ""),
        ),
    ]
    return {
        "ready": all(item["ok"] for item in items),
        "items": items,
        "next_actions": readiness.get("next_actions") or [],
        "latest_selftest_report_id": readiness.get("latest_selftest_report_id"),
        "latest_real_report_id": readiness.get("latest_real_report_id"),
        "real_platforms": readiness.get("real_platforms") or [],
        "missing_real_platforms": readiness.get("missing_real_platforms") or [],
    }


def _acceptance_item(
    key: str,
    label: str,
    check: dict[str, Any] | None,
    target_tab: str,
    action: str,
    detail: str,
) -> dict[str, Any]:
    check = check or {}
    return {
        "key": key,
        "label": label,
        "ok": bool(check.get("ok")),
        "status": "done" if check.get("ok") else "todo",
        "message": check.get("message") or detail,
        "detail": detail,
        "action": action,
        "target_tab": target_tab,
    }


def _check(key: str, label: str, ok: bool, message: str) -> dict[str, Any]:
    return {"key": key, "label": label, "ok": ok, "message": message}


def _next_actions(
    checks: list[dict[str, Any]],
    platforms: list[dict[str, Any]],
    real_platforms: set[str],
    empty_real_platforms: set[str],
) -> list[str]:
    failed = {check["key"] for check in checks if not check["ok"]}
    actions: list[str] = []
    required_platforms = _required_platform_items(platforms)
    optional_platforms = _optional_platform_items(platforms)
    missing_profiles = [
        p["platform_label"]
        for p in required_platforms
        if p.get("login_type") != "cookie" and not p.get("profile_exists")
    ]
    missing_cookies = [
        p["platform_label"]
        for p in required_platforms
        if p.get("login_type") == "cookie" and not p.get("has_cookies")
    ]
    open_windows = [p["platform_label"] for p in required_platforms if p.get("login_window_open")]
    needs_login = [p["platform_label"] for p in required_platforms if p.get("needs_login")]
    missing_required_status = sorted(REQUIRED_REAL_PLATFORMS - {str(p.get("platform")) for p in platforms})
    if missing_required_status:
        actions.append("进入资源管理页，补充首版必需平台状态：" + "、".join(_platform_label(p) for p in missing_required_status))
    if missing_profiles:
        actions.append("进入账号登录页，分别打开并登录：" + "、".join(missing_profiles))
    if missing_cookies:
        actions.append("进入账号登录页，为 Cookie 登录平台补充 Cookie：" + "、".join(missing_cookies))
    if open_windows:
        actions.append("关闭这些平台的登录窗口后再运行采集：" + "、".join(open_windows))
    elif needs_login:
        actions.append("进入账号登录页，重新登录并关闭窗口：" + "、".join(needs_login))
    optional_message = _optional_platform_maintenance_message(optional_platforms)
    if optional_message:
        actions.append("扩展平台资源可后续维护：" + optional_message)
    if "ai_config" in failed:
        if ai_api_disabled():
            actions.append("AI 服务未启用；平台采集和邮件可继续运行，内容会进入待人工复核。")
        else:
            actions.append("进入资源管理的 AI 接入页，保存连接资源并完成连接测试。")
    if "email_config" in failed:
        actions.append("进入邮件配置页，填写 SMTP 和收件人并发送测试邮件。")
    if "selftest_report" in failed:
        actions.append("进入报告中心，点击生成系统自检报告，验证 HTML、Excel、Markdown 链路。")
    missing_real = REQUIRED_REAL_PLATFORMS - real_platforms
    if missing_real:
        empty = missing_real & empty_real_platforms
        if empty:
            actions.append("这些平台已运行但未采到内容，请换真实可搜索关键词后重跑：" + "、".join(_platform_label(p) for p in sorted(empty)))
        not_run = missing_real - empty
        if not_run:
            actions.append("创建或编辑监控任务，优先完成这些平台采集：" + "、".join(_platform_label(p) for p in sorted(not_run)))
    return actions


def _platform_message(platforms: list[dict[str, Any]]) -> str:
    missing_required_status = sorted(REQUIRED_REAL_PLATFORMS - {str(p.get("platform")) for p in platforms})
    if missing_required_status:
        return "缺少首版必需平台状态：" + "、".join(_platform_label(p) for p in missing_required_status)
    required_platforms = _required_platform_items(platforms)
    optional_platforms = _optional_platform_items(platforms)
    missing = [
        p["platform_label"]
        for p in required_platforms
        if p.get("login_type") != "cookie" and not p["profile_exists"]
    ]
    missing_cookies = [
        p["platform_label"]
        for p in required_platforms
        if p.get("login_type") == "cookie" and not p.get("has_cookies")
    ]
    open_windows = [p["platform_label"] for p in required_platforms if p.get("login_window_open")]
    needs_login = [p["platform_label"] for p in required_platforms if p["needs_login"]]
    if missing:
        return "缺少网页登录态：" + "、".join(missing)
    if missing_cookies:
        return "Cookie 登录未填写 Cookie：" + "、".join(missing_cookies)
    if open_windows:
        return "登录窗口未关闭：" + "、".join(open_windows)
    if needs_login:
        return "可能需要重新登录：" + "、".join(needs_login)
    optional_message = _optional_platform_maintenance_message(optional_platforms)
    if optional_message:
        return "抖音登录配置可用；扩展平台待维护：" + optional_message
    return "抖音登录配置可用"


def _platform_profiles_ready(platforms: list[dict[str, Any]]) -> bool:
    found = {str(p.get("platform")) for p in platforms}
    if not REQUIRED_REAL_PLATFORMS <= found:
        return False
    required_platforms = _required_platform_items(platforms)
    return bool(required_platforms) and all(_platform_login_ready(p) for p in required_platforms)


def _required_platform_items(platforms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in platforms if str(p.get("platform") or "") in REQUIRED_REAL_PLATFORMS]


def _optional_platform_items(platforms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [p for p in platforms if str(p.get("platform") or "") in OPTIONAL_REAL_PLATFORMS]


def _platform_login_ready(platform: dict[str, Any]) -> bool:
    if "login_ready" in platform:
        return bool(platform.get("login_ready"))
    material_ready = bool(platform.get("login_material_ready", platform.get("profile_exists")))
    return material_ready and not platform.get("needs_login") and not platform.get("login_window_open")


def _optional_platform_maintenance_message(platforms: list[dict[str, Any]]) -> str:
    issues: list[str] = []
    for platform in platforms:
        label = platform.get("platform_label") or _platform_label(str(platform.get("platform") or ""))
        if platform.get("login_type") == "cookie" and not platform.get("has_cookies"):
            issues.append(f"{label} Cookie 待补充")
        elif platform.get("login_type") != "cookie" and not platform.get("profile_exists"):
            issues.append(f"{label}网页登录态待准备")
        elif platform.get("login_window_open"):
            issues.append(f"{label}登录窗口待关闭")
        elif platform.get("needs_login"):
            issues.append(f"{label}可能需要重新登录")
    return "、".join(issues)


def _ai_ready(config: dict[str, Any]) -> bool:
    if ai_api_disabled():
        return False
    return _ai_fields_complete(config) and config.get("last_test_status") == "success"


def _ai_message(config: dict[str, Any]) -> str:
    if ai_api_disabled():
        return "AI 服务未启用；采集内容会进入待人工复核"
    if not _ai_fields_complete(config):
        return "需填写 Base URL、API Key、Model，并完成连接测试"
    if config.get("last_test_status") == "success":
        return f"最近测试通过：{config.get('provider')} / {config.get('model')}（{_format_time(config.get('last_test_at'))}）"
    if config.get("last_test_status") == "failed":
        return "最近测试失败：" + customer_safe_text(config.get("last_test_error") or "请检查 AI 配置")
    return "配置已填写，但还未完成连接测试"


def _email_ready(config: dict[str, Any]) -> bool:
    return _email_fields_complete(config) and config.get("last_test_status") == "success"


def _email_message(config: dict[str, Any]) -> str:
    if not _email_fields_complete(config):
        return "需填写 SMTP、发件人、收件人，并点击测试邮件"
    if config.get("last_test_status") == "success":
        return f"最近测试通过：{config.get('smtp_host')}（{_format_time(config.get('last_test_at'))}）"
    if config.get("last_test_status") == "failed":
        return "最近测试失败：" + customer_safe_text(config.get("last_test_error") or "请检查 SMTP 配置")
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
        return f"最近系统自检报告 ID：{reports[0]['id']}"
    return "可在报告中心点击“生成系统自检报告”验证报告链路"


def _real_report_message(reports: list[dict[str, Any]]) -> str:
    if not reports:
        return "尚未完成抖音采集报告"
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
    return f"抖音采集闭环已完成，最近报告 ID：{reports[0]['id']}"


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
