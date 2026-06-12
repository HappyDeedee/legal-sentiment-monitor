from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .database import DB_PATH, get_ai_config, get_conn, get_email_config, list_jobs, list_reports
from .platform_status import list_platform_status
from .readiness import get_readiness_status
from .scheduler import scheduler_disabled_reason
from .security import KEY_PATH, MONITOR_DATA_DIR


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_TABLES = {
    "monitor_jobs",
    "job_keywords",
    "job_platforms",
    "job_recipients",
    "ai_configs",
    "email_configs",
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
            "project_root": str(PROJECT_ROOT),
            "monitor_data_dir": str(MONITOR_DATA_DIR),
            "database": str(DB_PATH),
            "secret_key": str(KEY_PATH),
        },
    }


def _check_python_project() -> dict[str, Any]:
    required = ["main.py", "api/main.py", "pyproject.toml", "api/monitoring/runner.py"]
    missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
    return _check(
        "project_files",
        "项目文件",
        not missing,
        "项目文件完整" if not missing else "缺少文件：" + "、".join(missing),
    )


def _check_uv_available() -> dict[str, Any]:
    uv_path = shutil.which("uv")
    return _check("uv", "uv 命令", bool(uv_path), f"已找到：{uv_path}" if uv_path else "未找到 uv，请先安装依赖管理工具")


def _check_data_dir() -> dict[str, Any]:
    try:
        MONITOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
        probe = MONITOR_DATA_DIR / ".doctor_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return _check("data_dir", "数据目录", True, f"可读写：{MONITOR_DATA_DIR}")
    except Exception as exc:
        return _check("data_dir", "数据目录", False, f"不可写：{type(exc).__name__}: {exc}")


def _check_secret_key() -> dict[str, Any]:
    if KEY_PATH.exists():
        return _check("secret_key", "加密密钥", True, f"已存在：{KEY_PATH}")
    return _check("secret_key", "加密密钥", False, "尚未生成；保存 AI 或邮件密钥后会创建 secret.key，需纳入备份")


def _check_database() -> dict[str, Any]:
    try:
        with get_conn() as conn:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tables = {row["name"] for row in rows}
        missing = sorted(REQUIRED_TABLES - tables)
        if missing:
            return _check("database", "SQLite 表结构", False, "缺少表：" + "、".join(missing))
        return _check("database", "SQLite 表结构", True, f"表结构完整：{DB_PATH}")
    except Exception as exc:
        return _check("database", "SQLite 表结构", False, f"数据库检查失败：{type(exc).__name__}: {exc}")


def _check_browser_profiles() -> dict[str, Any]:
    platforms = list_platform_status()
    missing = [p["platform_label"] for p in platforms if not p["profile_exists"]]
    needs_login = [p["platform_label"] for p in platforms if p["needs_login"]]
    ok = not missing and not needs_login
    if missing:
        message = "缺少 Profile：" + "、".join(missing)
    elif needs_login:
        message = "可能需要重新登录：" + "、".join(needs_login)
    else:
        message = "三平台 Profile 已发现"
    return _check("browser_profiles", "浏览器登录态", ok, message, {"platforms": platforms})


def _check_ai_config() -> dict[str, Any]:
    cfg = get_ai_config(masked=True)
    fields_complete = bool(cfg.get("base_url") and cfg.get("api_key") and cfg.get("model"))
    tested = cfg.get("last_test_status") == "success"
    if tested and fields_complete:
        message = f"已测试通过：{cfg.get('provider')} / {cfg.get('model')}"
    elif fields_complete:
        message = "字段已填写，但未测试通过"
    else:
        message = "需填写 Base URL、API Key、Model"
    return _check("ai_config", "AI 配置", bool(fields_complete and tested), message)


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
    reports = list_reports(20)
    selftest = [r for r in reports if (r.get("summary") or {}).get("selftest")]
    real = [r for r in reports if not (r.get("summary") or {}).get("selftest")]
    if selftest and real:
        return _check("reports", "报告链路", True, f"已有自测报告和真实报告，最近报告 ID：{reports[0]['id']}")
    if selftest:
        return _check("reports", "报告链路", False, f"已有自测报告 ID：{selftest[0]['id']}，仍缺真实采集报告")
    if real:
        return _check("reports", "报告链路", False, f"已有真实报告 ID：{real[0]['id']}，建议再生成自测报告验证下载链路")
    return _check("reports", "报告链路", False, "尚未生成报告；可先运行 selftest-report")


def _check_scheduler_mode() -> dict[str, Any]:
    reason = scheduler_disabled_reason()
    if reason:
        return _check("scheduler_mode", "调度器模式", False, reason)
    return _check("scheduler_mode", "调度器模式", True, "内置调度器会随 Web 单进程启动")


def _recommendations(checks: list[dict[str, Any]], readiness: dict[str, Any]) -> list[str]:
    failed = {item["key"] for item in checks if not item["ok"]}
    tips: list[str] = []
    if "uv" in failed:
        tips.append("先安装 uv，并在项目目录执行 uv sync。")
    if "data_dir" in failed:
        tips.append("修正 MONITOR_DATA_DIR 权限，确保运行用户可读写。")
    if "secret_key" in failed:
        tips.append("保存一次 AI 或邮件配置生成 secret.key，并把它加入服务器备份。")
    if "browser_profiles" in failed:
        tips.append("按 docs/deployment_runbook.md 重新准备抖音、快手、小红书登录态。")
    if "ai_config" in failed:
        tips.append("在后台 AI 配置页保存并点击测试 AI，必须看到最近测试通过。")
    if "email_config" in failed:
        tips.append("在后台邮件配置页发送测试邮件，确认真实收件箱收到。")
    if "jobs" in failed:
        tips.append("在任务管理页创建并启用至少一个监控任务。")
    if "reports" in failed:
        tips.append("先运行 monitor_cli.bat selftest-report，再运行真实平台任务生成报告。")
    if "scheduler_mode" in failed:
        tips.append("只运行一个 Web 进程承载内置调度器；如果必须多 worker，请设置 MONITOR_DISABLE_SCHEDULER=true 并用外部 cron 调用 monitor_cli.bat run-due。")
    for action in readiness.get("next_actions") or []:
        if action not in tips:
            tips.append(action)
    return tips


def _check(key: str, label: str, ok: bool, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = {"key": key, "label": label, "ok": ok, "message": message}
    if extra:
        data.update(extra)
    return data


def _platform_label(platform: str) -> str:
    return {"dy": "抖音", "ks": "快手", "xhs": "小红书"}.get(platform, platform)
