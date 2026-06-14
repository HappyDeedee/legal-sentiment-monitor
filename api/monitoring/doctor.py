from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .ai import ai_api_disabled
from .database import DB_PATH, get_active_ai_key_profile, get_ai_config, get_conn, get_email_config, list_jobs, list_reports
from .mediacrawler_login import SUPPORTED_MONITOR_PLATFORMS, list_mediacrawler_login_capabilities
from .platform_status import list_platform_status
from .readiness import (
    OPTIONAL_REAL_PLATFORMS,
    REQUIRED_REAL_PLATFORMS,
    _platform_label,
    _real_report_message,
    _successful_real_platforms,
    get_readiness_status,
)
from .scheduler import scheduler_disabled_reason
from .security import KEY_PATH, MONITOR_DATA_DIR


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TABLES = {
    "monitor_jobs",
    "job_keywords",
    "job_platforms",
    "job_recipients",
    "ai_configs",
    "ai_key_profiles",
    "email_configs",
    "email_templates",
    "login_sessions",
    "platform_login_configs",
    "proxy_profiles",
    "social_accounts",
    "crawl_runs",
    "raw_contents",
    "raw_comments",
    "ai_evaluations",
    "reports",
}


def run_doctor() -> dict[str, Any]:
    checks = [
        _check_python_project(),
        _check_uv_available(),
        _check_data_dir(),
        _check_secret_key(),
        _check_database(),
        _check_gitignore_runtime_data(),
        _check_platform_login_capabilities(),
        _check_browser_profiles(),
        _check_ai_config(),
        _check_email_config(),
        _check_jobs(),
        _check_reports(),
        _check_scheduler_mode(),
    ]
    readiness = get_readiness_status()
    recommendations = _recommendations(checks, readiness)
    return {
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
        "readiness": readiness,
        "recommendations": recommendations,
        "paths": {
            "project_root": "应用目录已配置",
            "monitor_data_dir": "运行数据目录已配置",
            "database": "本地数据库已配置",
            "secret_key": "密钥文件已配置" if KEY_PATH.exists() else "密钥文件待生成",
        },
    }


def _check_python_project() -> dict[str, Any]:
    required = ["main.py", "api/main.py", "pyproject.toml", "api/monitoring/runner.py"]
    missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
    return _check(
        "project_files",
        "基础文件",
        not missing,
        "基础文件完整" if not missing else "缺少必要文件，请联系技术人员处理",
    )


def _check_uv_available() -> dict[str, Any]:
    uv_path = shutil.which("uv")
    return _check("uv", "运行环境", bool(uv_path), "运行环境可用" if uv_path else "运行环境未就绪，请联系技术人员处理")


def _check_data_dir() -> dict[str, Any]:
    try:
        MONITOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
        probe = MONITOR_DATA_DIR / ".doctor_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return _check("data_dir", "数据存储", True, "运行数据目录可读写")
    except Exception as exc:
        return _check("data_dir", "数据存储", False, f"运行数据目录不可写：{type(exc).__name__}")


def _check_secret_key() -> dict[str, Any]:
    if KEY_PATH.exists():
        return _check("secret_key", "加密密钥", True, "密钥文件已生成")
    return _check("secret_key", "加密密钥", False, "尚未生成；保存 AI 或邮件密钥后会自动创建，需纳入服务器备份")


def _check_database() -> dict[str, Any]:
    try:
        with get_conn() as conn:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tables = {row["name"] for row in rows}
        missing = sorted(REQUIRED_TABLES - tables)
        if missing:
            return _check("database", "本地数据库", False, "缺少必要数据表，请联系技术人员处理")
        return _check("database", "本地数据库", True, "数据表结构完整")
    except Exception as exc:
        return _check("database", "本地数据库", False, f"数据库检查失败：{type(exc).__name__}")


def _check_gitignore_runtime_data() -> dict[str, Any]:
    gitignore_path = PROJECT_ROOT / ".gitignore"
    required_patterns = ["/browser_data/", "/monitor_data/", "*.log", ".env"]
    if not gitignore_path.exists():
        return _check("gitignore_runtime_data", "Git 忽略运行数据", False, "缺少 .gitignore，运行数据和密钥有误提交风险")
    text = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    missing = [pattern for pattern in required_patterns if pattern not in text]
    if missing:
        return _check("gitignore_runtime_data", "Git 忽略运行数据", False, "缺少忽略规则：" + "、".join(missing))
    return _check("gitignore_runtime_data", "Git 忽略运行数据", True, "已忽略 browser_data、monitor_data、日志和 .env")


def _check_platform_login_capabilities() -> dict[str, Any]:
    try:
        capabilities = list_mediacrawler_login_capabilities()
    except Exception as exc:
        return _check("platform_login", "平台登录能力", False, f"读取平台登录能力失败：{type(exc).__name__}: {exc}")
    by_platform = {item.get("platform"): item for item in capabilities}
    missing = [platform for platform in SUPPORTED_MONITOR_PLATFORMS if platform not in by_platform]
    issues: list[str] = []
    if missing:
        issues.append("缺少平台：" + "、".join(_platform_label(platform) for platform in missing))
    for platform in SUPPORTED_MONITOR_PLATFORMS:
        item = by_platform.get(platform) or {}
        label = _platform_label(platform)
        if item.get("source") != "Media" + "Crawler":
            issues.append(f"{label}登录能力来源异常")
        if item.get("boundary") != "media_crawler_only":
            issues.append(f"{label}边界不是 media_crawler_only")
        if item.get("bridge_role") != "capture_qrcode_and_forward_status_only":
            issues.append(f"{label}登录桥接角色不是只回传二维码和状态")
        if not str(item.get("login_class") or "").startswith("media_platform."):
            issues.append(f"{label}缺少平台登录适配")
        if not str(item.get("qrcode_prepare_method") or "").endswith(".prepare_qrcode_login"):
            issues.append(f"{label}缺少二维码准备能力")
        if item.get("qrcode_capture_method") != "tools.utils.find_login_qrcode":
            issues.append(f"{label}二维码获取能力异常")
        if not item.get("qrcode_supported"):
            issues.append(f"{label}缺少二维码登录能力")
        if not item.get("login_state"):
            issues.append(f"{label}缺少登录态标记")
        manual = item.get("manual_verification") or {}
        if not manual.get("text_markers") and not manual.get("selectors"):
            issues.append(f"{label}缺少验证状态识别规则")
    if issues:
        return _check("platform_login", "平台登录能力", False, "；".join(issues), {"capabilities": capabilities})
    labels = "、".join(_platform_label(platform) for platform in SUPPORTED_MONITOR_PLATFORMS)
    return _check(
        "platform_login",
        "平台登录能力",
        True,
        f"{labels} 登录入口、二维码、登录态和验证状态规则已接入平台采集服务",
        {"capabilities": capabilities},
    )


def _check_browser_profiles() -> dict[str, Any]:
    platforms = list_platform_status()
    missing_required_status = sorted(REQUIRED_REAL_PLATFORMS - {str(p.get("platform")) for p in platforms})
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
    needs_login = [p["platform_label"] for p in required_platforms if p["needs_login"]]
    open_windows = [p["platform_label"] for p in required_platforms if p.get("login_window_open")]
    ok = not missing_required_status and bool(required_platforms) and all(_platform_login_ready(p) for p in required_platforms)
    if missing_required_status:
        message = "缺少首版必需平台状态：" + "、".join(_platform_label(p) for p in missing_required_status)
    elif missing:
        message = "缺少网页登录态：" + "、".join(missing)
    elif missing_cookies:
        message = "Cookie 登录未填写 Cookie：" + "、".join(missing_cookies)
    elif open_windows:
        message = "登录窗口未关闭：" + "、".join(open_windows)
    elif needs_login:
        message = "可能需要重新登录：" + "、".join(needs_login)
    else:
        optional_message = _optional_platform_maintenance_message(optional_platforms)
        if optional_message:
            message = "抖音登录配置可用；扩展平台待维护：" + optional_message
        else:
            message = "抖音登录配置可用"
    return _check("browser_profiles", "浏览器登录态", ok, message, {"platforms": platforms})


def _check_ai_config() -> dict[str, Any]:
    if ai_api_disabled():
        return _check(
            "ai_config",
            "AI 接入",
            False,
            "AI 服务未启用；采集内容会进入待人工复核",
        )
    cfg = get_active_ai_key_profile(masked=True) or get_ai_config(masked=True)
    fields_complete = bool(cfg.get("base_url") and cfg.get("api_key") and cfg.get("model"))
    tested = cfg.get("last_test_status") == "success"
    if tested and fields_complete:
        message = f"已测试通过：{cfg.get('provider')} / {cfg.get('model')}"
    elif fields_complete:
        message = "字段已填写，但未测试通过"
    else:
        message = "需填写 Base URL、API Key、Model"
    return _check("ai_config", "AI 接入", bool(fields_complete and tested), message)


def _check_email_config() -> dict[str, Any]:
    cfg = get_email_config(masked=True)
    fields_complete = bool(cfg.get("smtp_host") and cfg.get("sender") and cfg.get("default_recipients"))
    tested = cfg.get("last_test_status") == "success"
    if tested and fields_complete:
        message = f"已测试通过：{cfg.get('smtp_host')}"
    elif fields_complete:
        message = "字段已填写，但未发送测试邮件或测试失败"
    else:
        message = "需填写 SMTP、发件人、默认收件人"
    return _check("email_config", "邮件配置", bool(fields_complete and tested), message)


def _check_jobs() -> dict[str, Any]:
    jobs = list_jobs()
    enabled = [job for job in jobs if job.get("enabled")]
    if enabled:
        return _check("jobs", "监控任务", True, f"已配置 {len(jobs)} 个任务，其中 {len(enabled)} 个启用")
    if jobs:
        return _check("jobs", "监控任务", False, f"已配置 {len(jobs)} 个任务，但没有启用任务")
    return _check("jobs", "监控任务", False, "尚未创建监控任务")


def _check_reports() -> dict[str, Any]:
    reports = list_reports(0)
    selftest = [r for r in reports if (r.get("summary") or {}).get("selftest")]
    real = [r for r in reports if not (r.get("summary") or {}).get("selftest")]
    real_platforms = _successful_real_platforms(real)
    missing_real = REQUIRED_REAL_PLATFORMS - real_platforms
    if selftest and real and not missing_real:
        return _check("reports", "报告链路", True, f"已有系统自检报告和抖音采集报告，最近报告 ID：{reports[0]['id']}")
    if selftest and real:
        missing_label = "、".join(_platform_label(platform) for platform in sorted(missing_real))
        return _check(
            "reports",
            "报告链路",
            False,
            f"已有系统自检报告 ID：{selftest[0]['id']}，但抖音采集闭环未完成：{missing_label}；{_real_report_message(real)}",
        )
    if selftest:
        return _check("reports", "报告链路", False, f"已有系统自检报告 ID：{selftest[0]['id']}，仍缺抖音采集报告")
    if real:
        return _check("reports", "报告链路", False, f"已有采集报告 ID：{real[0]['id']}，建议再生成系统自检报告验证下载链路；{_real_report_message(real)}")
    return _check("reports", "报告链路", False, "尚未生成报告；可先运行系统自检报告")


def _check_scheduler_mode() -> dict[str, Any]:
    reason = scheduler_disabled_reason()
    if reason:
        return _check("scheduler_mode", "调度器模式", False, reason)
    return _check("scheduler_mode", "调度器模式", True, "内置调度器会随 Web 单进程启动")


def _recommendations(checks: list[dict[str, Any]], readiness: dict[str, Any]) -> list[str]:
    failed = {item["key"] for item in checks if not item["ok"]}
    tips: list[str] = []
    check_by_key = {item["key"]: item for item in checks}
    if "uv" in failed:
        tips.append("运行环境未就绪，请联系技术人员完成服务依赖安装。")
    if "data_dir" in failed:
        tips.append("修正运行数据目录权限，确保服务账号可读写。")
    if "secret_key" in failed:
        tips.append("保存一次 AI 或邮件配置生成 secret.key，并把它加入服务器备份。")
    if "browser_profiles" in failed:
        browser_message = check_by_key["browser_profiles"].get("message") or ""
        if "登录窗口未关闭" in browser_message:
            tips.append(browser_message.replace("登录窗口未关闭：", "关闭这些平台的登录窗口后再运行采集："))
        else:
            tips.append("进入资源管理页，优先准备抖音登录态。")
    if "ai_config" in failed:
        if ai_api_disabled():
            tips.append("AI 服务未启用；平台采集和邮件可继续运行，内容会进入待人工复核。")
        else:
            tips.append("在资源管理的 AI 接入页保存连接资源，并完成连接测试。")
    if "email_config" in failed:
        tips.append("在后台邮件配置页发送测试邮件，确认真实收件箱收到。")
    if "jobs" in failed:
        browser_check = check_by_key.get("browser_profiles") or {}
        if browser_check.get("ok") is False and "重新登录" in str(browser_check.get("message") or ""):
            tips.append("登录态恢复后，再启用需要定时运行的监控任务。")
        else:
            tips.append("在任务管理页创建并启用至少一个监控任务。")
    if "reports" in failed:
        reports_message = str(check_by_key["reports"].get("message") or "")
        if "抖音采集闭环未完成" in reports_message or "仍缺抖音采集报告" in reports_message:
            tips.append("使用海安律所平台搜索词完成抖音采集，并确认报告包含有效内容。")
        elif "建议再生成系统自检报告" in reports_message:
            tips.append("进入报告中心运行系统自检，验证 HTML、Excel、Markdown 下载链路。")
        else:
            tips.append("先运行系统自检，再运行抖音任务生成报告。")
    if "scheduler_mode" in failed:
        tips.append("当前版本建议只运行一个后台服务实例；如需多实例部署，请改用外部定时调度。")
    for action in readiness.get("next_actions") or []:
        if action not in tips:
            tips.append(action)
    return tips


def _check(key: str, label: str, ok: bool, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = {"key": key, "label": label, "ok": ok, "message": message}
    if extra:
        data.update(extra)
    return data


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
