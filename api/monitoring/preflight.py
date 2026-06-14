from __future__ import annotations

from typing import Any

from .ai import ai_api_disabled
from .database import (
    get_active_ai_key_profile,
    get_ai_config,
    get_email_config,
    get_ai_key_profile,
    get_email_template,
    get_proxy_profile,
    get_social_account,
    has_job_template_placeholders,
    list_social_accounts,
)
from .platform_status import list_platform_status
from .login_state import login_window_status
from .security import redact_sensitive


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
            "平台搜索词",
            "ok" if job.get("keywords") else "blocking",
            "已配置平台搜索词" if job.get("keywords") else "未配置平台搜索词",
        ),
        _check(
            "platforms",
            "采集平台",
            "ok" if job.get("platforms") else "blocking",
            "已选择：" + _format_platforms(job.get("platforms") or []) if job.get("platforms") else "未选择平台",
        ),
        _template_placeholder_check(job),
        _advanced_collect_check(job),
        _platform_profile_check(job),
        _proxy_binding_check(job),
        _ai_config_check(job),
        _email_config_check(job),
        _email_template_check(job),
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
        return _check("template_placeholders", "任务内容", "blocking", "请先把测试数据模板里的律所名称和平台搜索词改成真实内容")
    return _check("template_placeholders", "任务内容", "ok", "任务内容已替换为真实律所和平台搜索词")


def _advanced_collect_check(job: dict[str, Any]) -> dict[str, Any]:
    target_type = str(job.get("target_type") or "search")
    platforms = set(job.get("platforms") or [])
    output_mode = str(job.get("output_mode") or "internal")
    blockers: list[str] = []
    warnings: list[str] = []
    if target_type in {"detail", "creator"}:
        if not job.get("keywords"):
            blockers.append("指定内容或用户主页模式需要填写平台可识别的链接或 ID")
        if len(platforms) > 1:
            blockers.append("指定内容或用户主页模式第一版建议一次只选择一个平台")
        warnings.append("指定内容链接/用户主页会复用平台采集服务能力，链接或 ID 格式不匹配时会返回空结果")
    if target_type != "search" and "ks" in platforms:
        warnings.append("快手指定内容/用户主页能力依赖底层平台支持，第一版建议先使用关键词搜索")
    if blockers:
        return _check("advanced_collect", "高级采集", "blocking", "；".join(blockers + warnings))
    if output_mode != "internal":
        warnings.append("系统仍会写入内部数据仓库；JSON/Excel 归档为额外产物")
    if not warnings:
        return _check("advanced_collect", "高级采集", "ok", "高级采集配置可用")
    return _check("advanced_collect", "高级采集", "warning", "；".join(warnings))


def _platform_profile_check(job: dict[str, Any]) -> dict[str, Any]:
    selected = set(job.get("platforms") or [])
    account_id = _safe_int(job.get("account_id"))
    if account_id:
        return _bound_account_profile_check(account_id, selected)
    statuses = {item["platform"]: item for item in list_platform_status()}
    missing = []
    missing_cookie = []
    missing_profile = []
    needs_login = []
    open_windows = []
    for platform in selected:
        status = statuses.get(platform)
        if not status:
            missing.append(platform)
            continue
        if status.get("login_type") == "cookie" and not status.get("has_cookies"):
            missing_cookie.append(platform)
        elif status.get("login_type") != "cookie" and not status.get("profile_exists"):
            missing_profile.append(platform)
        elif status.get("login_window_open"):
            open_windows.append(platform)
        elif status.get("needs_login"):
            needs_login.append(platform)
    if missing:
        return _check("platform_profiles", "平台登录态", "warning", "缺少平台状态：" + _format_platforms(missing))
    if missing_cookie:
        return _check("platform_profiles", "平台登录态", "blocking", "请先为这些平台账号保存 Cookie：" + _format_platforms(missing_cookie))
    if missing_profile:
        return _check("platform_profiles", "平台登录态", "blocking", "请先重新登录" + _format_platforms(missing_profile) + "账号")
    if open_windows:
        return _check("platform_profiles", "平台登录态", "blocking", "请先关闭登录窗口再运行采集：" + _format_platforms(open_windows))
    if needs_login:
        return _check("platform_profiles", "平台登录态", "blocking", "请先重新登录再运行采集：" + _format_platforms(needs_login))
    return _check("platform_profiles", "平台登录态", "ok", "所选平台登录配置可用")


def _bound_account_profile_check(account_id: int, selected: set[str]) -> dict[str, Any]:
    account = get_social_account(account_id)
    if not account:
        return _check("platform_profiles", "平台登录态", "blocking", "任务绑定的账号已不存在，请重新选择账号")
    platform = str(account.get("platform") or "")
    platform_label = PLATFORM_LABELS.get(platform, platform)
    account_name = str(account.get("name") or f"{platform_label}账号")
    if platform not in selected:
        return _check("platform_profiles", "平台登录态", "blocking", f"任务绑定账号 {account_name} 属于{platform_label}，但任务未选择该平台")
    if account.get("status") != "active":
        return _check("platform_profiles", "平台登录态", "blocking", f"任务绑定账号 {account_name} 当前不可用，请在平台账号中处理")
    login_type = str(account.get("login_type") or "qrcode")
    if login_type == "cookie" and not account.get("has_cookies"):
        return _check("platform_profiles", "平台登录态", "blocking", f"任务绑定账号 {account_name} 未保存 Cookie，请先在平台账号中保存")
    if login_type not in {"qrcode", "cookie"}:
        return _check("platform_profiles", "平台登录态", "blocking", "当前版本暂未开放手机号登录，请使用扫码或 Cookie 登录")
    if login_type == "qrcode" and not account.get("profile_path"):
        return _check("platform_profiles", "平台登录态", "warning", f"任务绑定账号 {account_name} 未准备网页登录态，请先发起网页登录")
    status = login_window_status(platform)
    if status.get("is_open"):
        return _check("platform_profiles", "平台登录态", "blocking", f"请先关闭{platform_label}登录窗口再运行采集")
    return _check("platform_profiles", "平台登录态", "ok", f"任务绑定账号 {account_name} 可用于本轮采集")


def _proxy_binding_check(job: dict[str, Any]) -> dict[str, Any]:
    selected = set(job.get("platforms") or [])
    blockers: list[str] = []
    warnings: list[str] = []
    accounts = _candidate_accounts_for_job(job)
    explicit_proxy = _safe_int(job.get("proxy_id"))
    if explicit_proxy:
        proxy = get_proxy_profile(explicit_proxy, masked=False)
        if not proxy:
            blockers.append("任务绑定的代理不存在")
        else:
            _append_proxy_messages("任务绑定代理", str(proxy.get("name") or f"#{proxy.get('id')}"), proxy, blockers, warnings)
    for account in accounts:
        platform = str(account.get("platform") or "")
        if platform not in selected or account.get("status") != "active" or not account.get("proxy_id"):
            continue
        platform_label = PLATFORM_LABELS.get(platform, platform)
        account_name = str(account.get("name") or f"{platform_label}账号")
        if explicit_proxy:
            continue
        proxy = get_proxy_profile(int(account["proxy_id"]), masked=False)
        if not proxy:
            blockers.append(f"{platform_label}账号 {account_name} 绑定的代理不存在")
            continue
        proxy_name = str(proxy.get("name") or f"#{proxy.get('id')}")
        _append_proxy_messages(f"{platform_label}账号 {account_name} 绑定代理", proxy_name, proxy, blockers, warnings)
    if blockers:
        return _check("proxy_bindings", "代理绑定", "blocking", "；".join(blockers))
    if warnings:
        return _check("proxy_bindings", "代理绑定", "warning", "；".join(warnings))
    return _check("proxy_bindings", "代理绑定", "ok", "账号绑定代理检查通过")


def _candidate_accounts_for_job(job: dict[str, Any]) -> list[dict[str, Any]]:
    account_id = _safe_int(job.get("account_id"))
    if not account_id:
        return list_social_accounts()
    account = get_social_account(account_id)
    return [account] if account else []


def _append_proxy_messages(prefix: str, proxy_name: str, proxy: dict[str, Any], blockers: list[str], warnings: list[str]) -> None:
    proxy_status = str(proxy.get("status") or "standby")
    proxy_url = str(proxy.get("proxy_url") or "").strip()
    if proxy_status == "disabled":
        blockers.append(f"{prefix}已停用：{proxy_name}")
    if not proxy_url:
        blockers.append(f"{prefix}未填写 URL：{proxy_name}")
    if proxy_status in {"standby", "limited"}:
        warnings.append(f"{prefix}状态为{_pool_status_label(proxy_status)}：{proxy_name}")
    if proxy.get("last_error"):
        warnings.append(f"{prefix}最近有错误：" + redact_sensitive(str(proxy.get("last_error") or ""))[:160])


def _ai_config_check(job: dict[str, Any]) -> dict[str, Any]:
    if ai_api_disabled():
        return _check("ai_config", "AI 接入", "warning", "AI 服务未启用；本轮采集和报告会继续，内容会进入待人工复核")
    cfg = _job_ai_profile(job)
    if job.get("ai_profile_id") and not cfg:
        return _check("ai_config", "AI 接入", "warning", "任务绑定的 AI 接入已不存在；本轮会回退到当前默认配置或进入待人工复核")
    cfg = cfg or get_active_ai_key_profile(masked=True) or get_ai_config(masked=True)
    cfg_label = "任务绑定 AI 接入" if job.get("ai_profile_id") else ("默认 AI 接入" if cfg.get("name") else "AI 接入")
    complete = bool(cfg.get("base_url") and cfg.get("api_key") and cfg.get("model"))
    if not complete:
        return _check("ai_config", "AI 接入", "warning", f"{cfg_label}未配置完整；本轮会生成报告，但内容会进入待人工复核")
    if cfg.get("last_test_status") != "success":
        return _check("ai_config", "AI 接入", "warning", f"{cfg_label}未测试通过；建议先完成连接测试")
    return _check("ai_config", "AI 接入", "ok", f"{cfg_label}最近测试通过")


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


def _job_ai_profile(job: dict[str, Any]) -> dict[str, Any] | None:
    profile_id = job.get("ai_profile_id")
    if not profile_id:
        return None
    try:
        return get_ai_key_profile(int(profile_id), masked=True)
    except (TypeError, ValueError):
        return None


def _email_template_check(job: dict[str, Any]) -> dict[str, Any]:
    template_id = job.get("email_template_id")
    if not template_id:
        return _check("email_template", "邮件模板", "ok", "使用当前启用邮件模板")
    try:
        template = get_email_template(int(template_id))
    except (TypeError, ValueError):
        template = None
    if not template:
        return _check("email_template", "邮件模板", "warning", "任务绑定的邮件模板已不存在；本轮会回退到当前启用模板")
    if not str(template.get("html_template") or "").strip():
        return _check("email_template", "邮件模板", "warning", "任务绑定的邮件模板未填写 HTML；本轮会使用报告默认正文")
    return _check("email_template", "邮件模板", "ok", "任务绑定邮件模板可用")


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


def _pool_status_label(status: str) -> str:
    return {"active": "可用", "standby": "待机", "limited": "受限", "disabled": "停用"}.get(status, status)


def _safe_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None
