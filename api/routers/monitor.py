from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

from ..monitoring import ai
from ..monitoring.ai import DEFAULT_PROMPT
from ..monitoring.database import (
    MONITOR_DATA_DIR,
    cancel_run,
    cancel_running_runs_for_job,
    create_login_session,
    delete_job,
    delete_ai_key_profile,
    delete_email_template,
    delete_login_session,
    delete_proxy_profile,
    delete_social_account,
    expire_login_sessions_for_account,
    get_dashboard_summary,
    get_ai_config,
    get_email_config,
    get_active_ai_key_profile,
    get_active_email_template,
    get_job,
    get_login_session,
    get_platform_login_config,
    get_report,
    get_run,
    get_social_account,
    has_running_run_for_job,
    init_db,
    list_jobs,
    list_leads,
    list_ai_key_profiles,
    list_email_templates,
    list_login_sessions,
    list_platform_login_configs,
    list_proxy_profiles,
    list_reports,
    list_runs,
    list_social_accounts,
    mark_ai_test_result,
    mark_email_test_result,
    render_email_template_preview,
    save_ai_config,
    save_ai_key_profile,
    save_email_config,
    save_email_template,
    save_job,
    save_platform_login_config,
    save_proxy_profile,
    save_social_account,
    set_active_ai_key_profile,
    set_job_enabled,
    set_job_schedule_state,
    update_login_session_status,
)
from ..monitoring.mailer import send_test_email
from ..monitoring.doctor import run_doctor
from ..monitoring.login_browser import build_login_browser_command, open_login_browser_with_command
from ..monitoring.login_qrcode import (
    close_qrcode_login_session,
    poll_qrcode_login_session,
    start_qrcode_login_session_with_profile,
)
from ..monitoring.platform_status import list_platform_status
from ..monitoring.preflight import build_job_preflight
from ..monitoring.readiness import get_readiness_status
from ..monitoring.reporting import resend_report_email
from ..monitoring.scheduler import launch_job, next_run_at, running_job_ids, scheduler_status, stop_job
from ..monitoring.security import redact_sensitive
from ..monitoring.selftest import create_sample_report


router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.get("/health")
async def health():
    init_db()
    return {"status": "ok"}


@router.get("/jobs")
async def jobs():
    init_db()
    return {"jobs": list_jobs()}


@router.post("/jobs/refresh-schedule")
async def refresh_jobs_schedule():
    init_db()
    refreshed = []
    for job in list_jobs():
        _refresh_job_schedule_state(job)
        updated = get_job(job["id"])
        if updated:
            refreshed.append(updated)
    return {"jobs": refreshed}


@router.get("/platform-status")
async def platform_status():
    init_db()
    return {"platforms": list_platform_status()}


@router.post("/platform-status/{platform}/login-browser")
async def platform_login_browser(platform: str, payload: dict[str, Any] | None = None):
    try:
        command = _login_browser_command_for_payload(platform, payload or {})
        return open_login_browser_with_command(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.get("/platform-login-configs")
async def platform_login_configs():
    init_db()
    return {"configs": list_platform_login_configs(masked=True)}


@router.get("/platform-login-configs/{platform}")
async def platform_login_config(platform: str):
    init_db()
    try:
        return {"config": get_platform_login_config(platform, masked=True)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/platform-login-configs/{platform}")
async def update_platform_login_config(platform: str, payload: dict[str, Any]):
    init_db()
    try:
        return {"config": save_platform_login_config(platform, payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.get("/readiness")
async def readiness():
    init_db()
    return get_readiness_status()


@router.get("/scheduler-status")
async def monitor_scheduler_status():
    return scheduler_status()


@router.get("/doctor")
async def doctor():
    init_db()
    return run_doctor()


@router.get("/dashboard")
async def dashboard():
    init_db()
    return {"summary": get_dashboard_summary(), "readiness": get_readiness_status(), "scheduler": scheduler_status()}


@router.post("/jobs")
async def create_job(payload: dict[str, Any]):
    try:
        job = save_job(payload)
        _refresh_job_schedule_state(job)
        return {"job": get_job(job["id"])}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/jobs/{job_id}")
async def update_job(job_id: int, payload: dict[str, Any]):
    try:
        job = save_job(payload, job_id)
        _refresh_job_schedule_state(job)
        return {"job": get_job(job["id"])}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: int):
    if job_id in running_job_ids() or has_running_run_for_job(job_id):
        raise HTTPException(status_code=409, detail="任务正在运行，请先停止后再删除")
    delete_job(job_id)
    return {"ok": True}


@router.post("/jobs/{job_id}/run")
async def run_job_now(job_id: int):
    if not get_job(job_id):
        raise HTTPException(status_code=404, detail="job not found")
    try:
        return launch_job(job_id, source="manual")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.post("/jobs/{job_id}/stop")
async def stop_job_now(job_id: int):
    result = stop_job(job_id)
    if not result.get("stopped") and has_running_run_for_job(job_id):
        cancelled = cancel_running_runs_for_job(job_id, "服务中没有找到活跃任务，已将残留运行记录标记为停止")
        return {"stopped": True, "status": "cancelled_stale_run", "job_id": job_id, "cancelled_runs": cancelled}
    if not result.get("stopped"):
        raise HTTPException(status_code=404, detail="任务当前没有在运行")
    return result


@router.get("/jobs/{job_id}/preflight")
async def job_preflight(job_id: int):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return {"preflight": build_job_preflight(job, running_job_ids())}


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: int):
    if not get_job(job_id):
        raise HTTPException(status_code=404, detail="job not found")
    set_job_enabled(job_id, False)
    _refresh_job_schedule_state(get_job(job_id))
    return {"ok": True}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: int):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    preflight_job = {**job, "enabled": True}
    preflight = build_job_preflight(preflight_job, running_job_ids())
    if preflight["blockers"]:
        raise HTTPException(status_code=400, detail="启用前检查未通过：" + "；".join(preflight["blockers"]))
    set_job_enabled(job_id, True)
    refreshed = get_job(job_id)
    _refresh_job_schedule_state(refreshed)
    return {"ok": True, "job": get_job(job_id), "preflight": preflight}


@router.get("/ai-config")
async def ai_config():
    init_db()
    return {"config": get_ai_config(masked=True), "default_prompt": DEFAULT_PROMPT}


@router.put("/ai-config")
async def update_ai_config(payload: dict[str, Any]):
    try:
        return {"config": save_ai_config(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/ai-config/test")
async def test_ai_config(payload: dict[str, Any] | None = None):
    payload = payload or {}
    test_targets_saved_config = not payload
    try:
        if ai.ai_api_disabled():
            raise ValueError("AI API 已通过 MONITOR_SKIP_AI_API 临时关闭；请使用离线自检，关闭该开关后再做真实测试 AI")
        if payload:
            save_ai_config(payload)
            test_targets_saved_config = True
        result = await ai.test_ai({})
        config = mark_ai_test_result(True)
        return {"result": result, "config": config}
    except ValueError as exc:
        if test_targets_saved_config:
            mark_ai_test_result(False, str(exc))
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))
    except Exception as exc:
        message = redact_sensitive(f"{type(exc).__name__}: {exc}")
        if test_targets_saved_config:
            mark_ai_test_result(False, message)
        raise HTTPException(status_code=400, detail=message)


@router.post("/ai-config/offline-check")
async def ai_config_offline_check(payload: dict[str, Any] | None = None):
    try:
        return {"result": ai.offline_check(payload or {})}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.get("/ai-profiles")
async def ai_profiles():
    init_db()
    return {"profiles": list_ai_key_profiles(masked=True), "active": get_active_ai_key_profile(masked=True)}


@router.post("/ai-profiles")
async def create_ai_profile(payload: dict[str, Any]):
    try:
        return {"profile": save_ai_key_profile(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.put("/ai-profiles/{profile_id}")
async def update_ai_profile(profile_id: int, payload: dict[str, Any]):
    try:
        return {"profile": save_ai_key_profile(payload, profile_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.post("/ai-profiles/{profile_id}/activate")
async def activate_ai_profile(profile_id: int):
    try:
        return {"profile": set_active_ai_key_profile(profile_id)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/ai-profiles/{profile_id}")
async def remove_ai_profile(profile_id: int):
    delete_ai_key_profile(profile_id)
    return {"ok": True}


@router.get("/email-config")
async def email_config():
    init_db()
    return {"config": get_email_config(masked=True)}


@router.put("/email-config")
async def update_email_config(payload: dict[str, Any]):
    try:
        return {"config": save_email_config(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/email-config/test")
async def test_email(payload: dict[str, Any] | None = None):
    config_saved = False
    try:
        save_email_config(payload or {})
        config_saved = True
        send_test_email({})
        config = mark_email_test_result(True)
        return {"ok": True, "config": config}
    except ValueError as exc:
        if config_saved:
            mark_email_test_result(False, str(exc))
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))
    except Exception as exc:
        message = redact_sensitive(f"{type(exc).__name__}: {exc}")
        if config_saved:
            mark_email_test_result(False, message)
        raise HTTPException(status_code=400, detail=message)


@router.get("/email-templates")
async def email_templates():
    init_db()
    return {"templates": list_email_templates(), "active": get_active_email_template()}


@router.post("/email-templates")
async def create_email_template(payload: dict[str, Any]):
    try:
        return {"template": save_email_template(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/email-templates/{template_id}")
async def update_email_template(template_id: int, payload: dict[str, Any]):
    try:
        return {"template": save_email_template(payload, template_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/email-templates/{template_id}")
async def remove_email_template(template_id: int):
    delete_email_template(template_id)
    return {"ok": True}


@router.post("/email-templates/preview")
async def email_template_preview(payload: dict[str, Any] | None = None):
    return {"preview": render_email_template_preview(payload or {})}


@router.get("/social-accounts")
async def social_accounts():
    init_db()
    return {"accounts": list_social_accounts()}


@router.post("/social-accounts")
async def create_social_account(payload: dict[str, Any]):
    try:
        return {"account": save_social_account(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/social-accounts/{account_id}")
async def update_social_account(account_id: int, payload: dict[str, Any]):
    try:
        return {"account": save_social_account(payload, account_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/social-accounts/{account_id}")
async def remove_social_account(account_id: int):
    delete_social_account(account_id)
    return {"ok": True}


@router.get("/login-sessions")
async def login_sessions(limit: int = Query(20, ge=0, le=200)):
    init_db()
    return {"sessions": list_login_sessions(limit)}


@router.post("/login-sessions")
async def create_platform_login_session(payload: dict[str, Any]):
    init_db()
    platform = payload.get("platform")
    try:
        command = _login_browser_command_for_payload(str(platform), payload)
        account = get_social_account(int(payload.get("account_id") or 0)) if payload.get("account_id") else None
        expired_session_ids = expire_login_sessions_for_account(
            int(account["id"]) if account else None,
            str(platform),
            str(command.get("profile_path") or ""),
        )
        for expired_session_id in expired_session_ids:
            await close_qrcode_login_session(expired_session_id)
        session = create_login_session(
            {
                "platform": platform,
                "account_id": payload.get("account_id"),
                "login_url": command["login_url"],
                "profile_path": command["profile_path"],
                "message": "正在生成登录二维码。",
            }
        )
        qr_result = await start_qrcode_login_session_with_profile(int(session["id"]), str(platform), command)
        if qr_result.get("already_logged_in"):
            session = update_login_session_status(
                int(session["id"]),
                "success",
                str(qr_result.get("message") or "当前 Profile 已经登录"),
            )
        elif qr_result.get("ok"):
            session = update_login_session_status(
                int(session["id"]),
                "waiting_qrcode",
                str(qr_result.get("message") or "请扫码登录"),
                str(qr_result.get("qr_image") or ""),
            )
        else:
            session = update_login_session_status(
                int(session["id"]),
                "waiting_manual_browser",
                str(qr_result.get("message") or "二维码生成失败，请使用登录窗口兜底"),
            )
        return {
            "session": session,
            "capabilities": {
                "qr_image_supported": bool(session.get("qr_image")),
                "manual_browser_fallback": True,
                "polling_supported": True,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.get("/login-sessions/{session_id}")
async def login_session(session_id: int):
    init_db()
    session = get_login_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="login session not found")
    platform = session.get("platform")
    qr_poll = await poll_qrcode_login_session(session_id)
    if qr_poll.get("success"):
        session = update_login_session_status(session_id, "success", str(qr_poll.get("message") or "登录成功"))
    elif qr_poll.get("expired"):
        session = update_login_session_status(session_id, "expired", str(qr_poll.get("message") or "二维码已过期"))
    elif qr_poll.get("active") and session.get("status") != "waiting_qrcode":
        session = update_login_session_status(session_id, "waiting_qrcode", str(qr_poll.get("message") or "等待扫码"))
    elif qr_poll.get("message") and session.get("status") == "waiting_qrcode":
        session = {**session, "message": qr_poll.get("message")}
    statuses = {item["platform"]: item for item in list_platform_status()}
    platform_status = statuses.get(platform) or {}
    status = session.get("status") or "waiting_manual_browser"
    if platform_status.get("login_ready"):
        status = "success"
    elif platform_status.get("login_window_open"):
        status = "waiting_manual_browser"
    return {
        "session": {**session, "status": status},
        "platform_status": platform_status,
        "capabilities": {
            "qr_image_supported": bool(session.get("qr_image")),
            "manual_browser_fallback": True,
            "polling_supported": True,
        },
    }


@router.delete("/login-sessions/{session_id}")
async def remove_login_session(session_id: int):
    await close_qrcode_login_session(session_id)
    delete_login_session(session_id)
    return {"ok": True}


@router.get("/proxies")
async def proxies():
    init_db()
    return {"proxies": list_proxy_profiles(masked=True)}


@router.post("/proxies")
async def create_proxy(payload: dict[str, Any]):
    try:
        return {"proxy": save_proxy_profile(payload)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.put("/proxies/{proxy_id}")
async def update_proxy(proxy_id: int, payload: dict[str, Any]):
    try:
        return {"proxy": save_proxy_profile(payload, proxy_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.delete("/proxies/{proxy_id}")
async def remove_proxy(proxy_id: int):
    delete_proxy_profile(proxy_id)
    return {"ok": True}


@router.get("/runs")
async def runs(limit: int = Query(100, ge=0, le=1000)):
    init_db()
    return {"runs": list_runs(limit), "running_job_ids": running_job_ids()}


@router.post("/runs/{run_id}/stop")
async def stop_run_now(run_id: int):
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    if run.get("status") != "running":
        raise HTTPException(status_code=400, detail="这条运行记录已经结束")
    job_id = run.get("job_id")
    if not job_id:
        if cancel_run(run_id, "这条运行记录没有可停止的任务 ID，已标记为停止"):
            return {"stopped": True, "status": "cancelled_stale_run", "run_id": run_id}
        raise HTTPException(status_code=400, detail="这条运行记录没有可停止的任务 ID")
    result = stop_job(int(job_id))
    if not result.get("stopped") and cancel_run(run_id, "服务中没有找到活跃任务，已将残留运行记录标记为停止"):
        return {"stopped": True, "status": "cancelled_stale_run", "run_id": run_id, "job_id": int(job_id)}
    if not result.get("stopped"):
        raise HTTPException(status_code=404, detail="任务当前没有在运行")
    return result


@router.get("/runs/{run_id}/logs")
async def run_logs(run_id: int):
    run_root = MONITOR_DATA_DIR / "runs"
    logs = []
    for path in run_root.glob(f"**/run_{run_id}_*/**/crawler.log"):
        content = redact_sensitive(path.read_text(encoding="utf-8", errors="ignore"))[-20000:]
        logs.append({"path": str(path), "content": content})
    return {"logs": logs}


@router.get("/reports")
async def reports(
    limit: int = 100,
    law_firm: str = "",
    platform: str = "",
    risk: str = Query("", description="high|negative|none"),
    date_from: str = "",
    date_to: str = "",
):
    init_db()
    items = list_reports(_query_limit(limit))
    if law_firm:
        items = [r for r in items if law_firm.strip() in (r.get("law_firm_name") or "")]
    if platform:
        items = [
            r
            for r in items
            if platform in (r.get("summary") or {}).get("platform_results", {})
            or platform in (r.get("summary") or {}).get("platforms", [])
        ]
    if risk == "high":
        items = [r for r in items if int((r.get("summary") or {}).get("high_count") or 0) > 0]
    elif risk == "negative":
        items = [r for r in items if int((r.get("summary") or {}).get("negative_count") or 0) > 0]
    elif risk == "pending":
        items = [r for r in items if int((r.get("summary") or {}).get("pending_review_count") or 0) > 0]
    elif risk == "none":
        items = [
            r
            for r in items
            if int((r.get("summary") or {}).get("negative_count") or 0) == 0
            and int((r.get("summary") or {}).get("pending_review_count") or 0) == 0
        ]
    if date_from:
        items = [r for r in items if (r.get("created_at") or "")[:10] >= date_from]
    if date_to:
        items = [r for r in items if (r.get("created_at") or "")[:10] <= date_to]
    return {"reports": items}


@router.get("/leads")
async def leads(
    limit: int = 100,
    law_firm: str = "",
    platform: str = "",
    risk: str = Query("", description="high|negative|pending|none"),
    date_from: str = "",
    date_to: str = "",
    run_id: int | None = None,
    report_id: int | None = None,
):
    init_db()
    target_run_id = run_id
    if report_id:
        report = get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="report not found")
        target_run_id = int(report["run_id"])
    items = list_leads(0 if target_run_id else _query_limit(limit))
    if target_run_id:
        items = [item for item in items if int(item.get("run_id") or 0) == int(target_run_id)]
    if law_firm:
        items = [item for item in items if law_firm.strip() in (item.get("law_firm_name") or "")]
    if platform:
        items = [item for item in items if item.get("platform") == platform]
    if risk == "high":
        items = [item for item in items if item.get("is_related") and item.get("is_negative") and item.get("risk_level") == "high"]
    elif risk == "negative":
        items = [item for item in items if item.get("is_related") and item.get("is_negative")]
    elif risk == "pending":
        items = [item for item in items if item.get("eval_status") == "pending_review"]
    elif risk == "none":
        items = [
            item
            for item in items
            if item.get("eval_status") != "pending_review"
            and not (item.get("is_related") and item.get("is_negative"))
        ]
    if date_from:
        items = [item for item in items if (item.get("first_seen_at") or "")[:10] >= date_from]
    if date_to:
        items = [item for item in items if (item.get("first_seen_at") or "")[:10] <= date_to]
    return {"leads": items}


@router.post("/reports/selftest")
async def report_selftest():
    try:
        return {"result": await create_sample_report()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")


@router.get("/reports/{report_id}")
async def report_detail(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    html_path = _safe_report_path(report["html_path"])
    report["html"] = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    return {"report": report}


@router.post("/reports/{report_id}/resend-email")
async def report_resend_email(report_id: int):
    try:
        ok, error, report = resend_report_email(report_id)
        return {"ok": ok, "error": redact_sensitive(error), "report": report}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.get("/reports/{report_id}/download")
async def report_download(report_id: int, type: str = "excel"):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    key = {"excel": "excel_path", "markdown": "markdown_path", "html": "html_path"}.get(type)
    if not key:
        raise HTTPException(status_code=400, detail="unsupported report type")
    path = _safe_report_path(report[key])
    if not path.exists():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, filename=path.name, media_type=_report_download_media_type(type, path))


@router.get("/page", response_class=HTMLResponse)
async def monitor_page():
    page = Path(__file__).resolve().parents[1] / "monitor_web" / "index.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="monitor page not found")
    return HTMLResponse(page.read_text(encoding="utf-8"))


def _refresh_job_schedule_state(job: dict[str, Any] | None) -> None:
    if not job:
        return
    set_job_schedule_state(job["id"], next_run_at(job) if job.get("enabled") else None)


def _login_browser_command_for_payload(platform: str, payload: dict[str, Any]) -> dict[str, Any]:
    command = build_login_browser_command(platform)
    account_id = payload.get("account_id")
    if not account_id:
        return command
    account = get_social_account(int(account_id))
    if not account:
        raise ValueError("account not found")
    if account.get("platform") != platform:
        raise ValueError("account platform does not match login platform")
    if account.get("profile_path"):
        command = {**command, "profile_path": str(account["profile_path"])}
    return command


def _report_download_media_type(report_type: str, path: Path) -> str:
    if report_type == "excel" or path.suffix.lower() == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if report_type == "markdown" or path.suffix.lower() == ".md":
        return "text/markdown"
    if report_type == "html" or path.suffix.lower() == ".html":
        return "text/html"
    return "application/octet-stream"


def _query_limit(value: Any, default: int = 100, maximum: int = 5000) -> int:
    try:
        return min(maximum, max(0, int(value)))
    except (TypeError, ValueError):
        return default


def _safe_report_path(value: str) -> Path:
    path = Path(value)
    try:
        path.resolve().relative_to((MONITOR_DATA_DIR / "reports").resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="invalid report path")
    return path
