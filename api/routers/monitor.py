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
    confirm_social_account,
    create_draft_social_account,
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
    get_ai_key_profile,
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
    mark_ai_key_profile_test_result,
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
    update_social_account_login_state,
)
from ..monitoring.mailer import render_report_email_preview, send_test_email
from ..monitoring.doctor import run_doctor
from ..monitoring.login_browser import build_login_browser_command, open_login_browser_with_command
from ..monitoring.login_qrcode import (
    close_qrcode_login_session,
    poll_qrcode_login_session,
    start_qrcode_login_session_with_profile,
)
from ..monitoring.account_check import check_social_account_login
from ..monitoring.mediacrawler_login import get_mediacrawler_login_capability, list_mediacrawler_login_capabilities
from ..monitoring.normalizer import PLATFORM_LABELS
from ..monitoring.platform_status import list_platform_status
from ..monitoring.preflight import build_job_preflight
from ..monitoring.readiness import get_acceptance_checklist, get_readiness_status
from ..monitoring.reporting import resend_report_email
from ..monitoring.scheduler import launch_job, next_run_at, running_job_ids, scheduler_status, stop_job
from ..monitoring.security import customer_safe_text, redact_sensitive
from ..monitoring.selftest import create_sample_report
from ..monitoring.smoke import run_smoke_check


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
    return {"platforms": [_customer_view_platform_status(item) for item in list_platform_status()]}


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


@router.get("/platform-login-capabilities")
async def platform_login_capabilities():
    return {
        "capabilities": [
            _login_capability_response(str(item.get("platform") or ""))
            for item in list_mediacrawler_login_capabilities()
        ]
    }


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
    return _customer_view_readiness_status(get_readiness_status())


@router.get("/acceptance-checklist")
async def acceptance_checklist():
    init_db()
    return _customer_view_system_checklist(get_acceptance_checklist())


@router.get("/system-checklist")
async def system_checklist():
    init_db()
    return _customer_view_system_checklist(get_acceptance_checklist())


@router.get("/scheduler-status")
async def monitor_scheduler_status():
    return scheduler_status()


@router.get("/doctor")
async def doctor():
    init_db()
    return _customer_view_doctor(run_doctor())


@router.post("/smoke")
async def smoke():
    try:
        return {"result": _customer_view_smoke_result(await run_smoke_check())}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.get("/dashboard")
async def dashboard():
    init_db()
    return {
        "summary": get_dashboard_summary(),
        "readiness": _customer_view_readiness_status(get_readiness_status()),
        "scheduler": scheduler_status(),
    }


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
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    preflight = build_job_preflight(job, running_job_ids())
    if preflight["blockers"]:
        raise HTTPException(status_code=400, detail="运行前检查未通过：" + "；".join(preflight["blockers"]))
    try:
        result = launch_job(job_id, source="manual")
        return {**result, "preflight": preflight}
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
            raise ValueError("AI 服务当前未启用；采集不受影响，内容会进入待人工复核。")
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


@router.get("/ai-evaluation-config")
async def ai_evaluation_config():
    return await ai_config()


@router.put("/ai-evaluation-config")
async def update_ai_evaluation_config(payload: dict[str, Any]):
    return await update_ai_config(payload)


@router.post("/ai-evaluation-config/test")
async def test_ai_evaluation_config(payload: dict[str, Any] | None = None):
    return await test_ai_config(payload)


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


@router.post("/ai-profiles/{profile_id}/offline-check")
async def ai_profile_offline_check(profile_id: int, payload: dict[str, Any] | None = None):
    try:
        profile = get_ai_key_profile(profile_id, masked=False)
        if not profile:
            raise ValueError("AI profile not found")
        return {"result": ai.offline_check({**profile, **(payload or {})})}
    except ValueError as exc:
        raise HTTPException(status_code=404 if "not found" in str(exc) else 400, detail=redact_sensitive(str(exc)))


@router.post("/ai-profiles/{profile_id}/test")
async def test_ai_profile(profile_id: int, payload: dict[str, Any] | None = None):
    try:
        if ai.ai_api_disabled():
            raise ValueError("AI 服务当前未启用；采集不受影响，内容会进入待人工复核。")
        profile = get_ai_key_profile(profile_id, masked=False)
        if not profile:
            raise ValueError("AI profile not found")
        result = await ai.test_ai_connection({**profile, **(payload or {})})
        profile_masked = mark_ai_key_profile_test_result(profile_id, True)
        return {"result": result, "profile": profile_masked}
    except ValueError as exc:
        if "not found" not in str(exc):
            try:
                mark_ai_key_profile_test_result(profile_id, False, str(exc))
            except ValueError:
                pass
        raise HTTPException(status_code=404 if "not found" in str(exc) else 400, detail=redact_sensitive(str(exc)))
    except Exception as exc:
        message = redact_sensitive(f"{type(exc).__name__}: {exc}")
        try:
            mark_ai_key_profile_test_result(profile_id, False, message)
        except ValueError:
            pass
        raise HTTPException(status_code=400, detail=message)


@router.post("/ai-profiles/{profile_id}/connection-test")
async def test_ai_profile_connection(profile_id: int, payload: dict[str, Any] | None = None):
    return await test_ai_profile(profile_id, payload)


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


@router.post("/social-accounts/{account_id}/confirm")
async def confirm_account(account_id: int, payload: dict[str, Any] | None = None):
    try:
        return {"account": confirm_social_account(account_id, payload or {})}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/social-accounts/{account_id}")
async def remove_social_account(account_id: int):
    delete_social_account(account_id)
    return {"ok": True}


@router.post("/social-accounts/{account_id}/check-login")
async def check_social_account(account_id: int):
    try:
        return {"result": await check_social_account_login(account_id)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.post("/social-accounts/check-login")
async def check_social_accounts(payload: dict[str, Any] | None = None):
    account_ids = (payload or {}).get("account_ids") or []
    if not isinstance(account_ids, list) or not account_ids:
        raise HTTPException(status_code=400, detail="请选择要检测的账号")
    results: list[dict[str, Any]] = []
    for raw_id in account_ids:
        try:
            account_id = int(raw_id)
        except (TypeError, ValueError):
            results.append({"account_id": raw_id, "ok": False, "status": "invalid", "message": "账号 ID 无效"})
            continue
        try:
            results.append(await check_social_account_login(account_id))
        except ValueError as exc:
            results.append(
                {
                    "account_id": account_id,
                    "ok": False,
                    "status": "invalid",
                    "message": redact_sensitive(str(exc)),
                }
            )
    return {"results": results}


@router.get("/login-sessions")
async def login_sessions(limit: int = Query(20, ge=0, le=200), account_id: int | None = Query(None, ge=1)):
    init_db()
    return {"sessions": list_login_sessions(limit, account_id=account_id)}


@router.post("/login-sessions")
async def create_platform_login_session(payload: dict[str, Any]):
    init_db()
    platform = payload.get("platform")
    try:
        if not payload.get("account_id"):
            draft = create_draft_social_account(
                {
                    "name": payload.get("name") or "未命名账号",
                    "platform": platform,
                    "proxy_id": payload.get("proxy_id"),
                    "profile_path": payload.get("profile_path") or "",
                    "notes": payload.get("notes") or "",
                }
            )
            payload = {**payload, "account_id": draft["id"]}
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
        verification_image = ""
        account_status = None
        if qr_result.get("already_logged_in"):
            session = update_login_session_status(
                int(session["id"]),
                "success",
                str(qr_result.get("message") or "当前 Profile 已经登录"),
            )
            session, account_status = await _verify_successful_login_session(session)
        elif qr_result.get("needs_verification"):
            session = update_login_session_status(
                int(session["id"]),
                "waiting_verification",
                str(qr_result.get("message") or "平台要求先完成人工验证"),
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
                str(qr_result.get("message") or "二维码生成失败，请使用网页登录窗口处理"),
            )
        if account_status is None:
            account_status = update_social_account_login_state(
                int(account["id"]) if account else None,
                str(session.get("status") or ""),
                str(session.get("message") or ""),
            )
        return {
            "session": session,
            "account_status": account_status,
            "capabilities": {
                **_login_capability_response(str(platform), qr_result),
                "qr_image_supported": bool(session.get("qr_image")),
                "verification_image": verification_image,
                "verification_image_supported": bool(verification_image),
                "verification_type": str(qr_result.get("verification_type") or ""),
                "verification_label": str(qr_result.get("verification_label") or ""),
                "verification_detail": str(qr_result.get("verification_detail") or ""),
                "diagnostic_image": "",
                "diagnostic_image_supported": False,
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
    original_status = str(session.get("status") or "")
    platform = session.get("platform")
    qr_poll = await poll_qrcode_login_session(session_id)
    verification_image = ""
    account_status = None
    if qr_poll.get("success"):
        session = update_login_session_status(session_id, "success", str(qr_poll.get("message") or "登录成功"))
        session, account_status = await _verify_successful_login_session(session)
    elif qr_poll.get("expired"):
        session = update_login_session_status(session_id, "expired", str(qr_poll.get("message") or "二维码已过期"))
    elif qr_poll.get("qr_image"):
        session = update_login_session_status(
            session_id,
            "waiting_qrcode",
            str(qr_poll.get("message") or "二维码已生成，请扫码登录"),
            str(qr_poll.get("qr_image") or ""),
        )
    elif qr_poll.get("needs_verification"):
        session = update_login_session_status(
            session_id,
            "waiting_verification",
            str(qr_poll.get("message") or "等待完成人工验证"),
        )
    elif qr_poll.get("active") and session.get("status") not in {"waiting_qrcode", "waiting_verification"}:
        session = update_login_session_status(session_id, "waiting_qrcode", str(qr_poll.get("message") or "等待扫码"))
    elif qr_poll.get("message") and session.get("status") in {"waiting_qrcode", "waiting_verification"}:
        session = {**session, "message": qr_poll.get("message")}
    terminal_statuses = {"success", "failed", "expired"}
    if account_status is None and original_status in terminal_statuses and not qr_poll.get("success"):
        account_status = get_social_account(int(session.get("account_id") or 0)) if session.get("account_id") else None
    elif account_status is None:
        account_status = update_social_account_login_state(
            int(session.get("account_id") or 0) or None,
            str(session.get("status") or ""),
            str(session.get("message") or ""),
        )
    statuses = {item["platform"]: item for item in list_platform_status()}
    platform_status = statuses.get(platform) or {}
    status = session.get("status") or "waiting_manual_browser"
    return {
        "session": {**session, "status": status},
        "platform_status": platform_status,
        "account_status": account_status,
        "capabilities": {
            **_login_capability_response(str(platform), qr_poll),
            "qr_image_supported": bool(session.get("qr_image")),
            "verification_image": verification_image,
            "verification_image_supported": bool(verification_image),
            "verification_type": str(qr_poll.get("verification_type") or ""),
            "verification_label": str(qr_poll.get("verification_label") or ""),
            "verification_detail": str(qr_poll.get("verification_detail") or ""),
            "manual_browser_fallback": True,
            "polling_supported": True,
        },
    }


async def _verify_successful_login_session(session: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    account_id = int(session.get("account_id") or 0)
    if not account_id:
        return session, None
    try:
        check = await check_social_account_login(account_id, allow_draft=True)
    except Exception as exc:
        message = customer_safe_text(f"登录结果未确认，请重新生成二维码后扫码登录。{redact_sensitive(str(exc))}")
        failed_session = update_login_session_status(int(session["id"]), "failed", message)
        account_status = update_social_account_login_state(account_id, "failed", message)
        return failed_session, account_status
    if not check.get("ok"):
        message = customer_safe_text(str(check.get("message") or "登录态未通过验活，请重新扫码登录。"))
        failed_session = update_login_session_status(int(session["id"]), "failed", message)
        account_status = check.get("account") or update_social_account_login_state(account_id, "failed", message)
        return failed_session, account_status
    success_message = "登录成功，账号已通过验活。"
    verified_session = update_login_session_status(int(session["id"]), "success", success_message, str(session.get("qr_image") or ""))
    return verified_session, check.get("account")


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
    return {"runs": [_customer_view_run(item) for item in list_runs(limit)], "running_job_ids": running_job_ids()}


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
        content = customer_safe_text(path.read_text(encoding="utf-8", errors="ignore"))[-20000:]
        logs.append({"path": "运行日志", "content": content})
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
    return {"reports": [_customer_view_report(item) for item in items]}


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
    return {"leads": [_customer_view_lead(item) for item in items]}


@router.post("/reports/selftest")
async def report_selftest():
    try:
        return {"result": _customer_view_system_check_result(await create_sample_report())}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.post("/reports/system-check")
async def report_system_check():
    try:
        return {"result": _customer_view_system_check_result(await create_sample_report())}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.get("/reports/{report_id}")
async def report_detail(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    html_path = _safe_report_path(report["html_path"])
    view = _customer_view_report(report)
    view["html"] = customer_safe_text(html_path.read_text(encoding="utf-8")) if html_path.exists() else ""
    return {"report": view}


@router.get("/reports/{report_id}/email-preview")
async def report_email_preview(report_id: int):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    html_path = _safe_report_path(report["html_path"])
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="report html not found")
    job = get_job(int(report.get("job_id") or 0)) or {
        "id": report.get("job_id"),
        "law_firm_name": report.get("law_firm_name") or report.get("display_law_firm_name") or (report.get("summary") or {}).get("law_firm_name") or "",
        "recipients": [],
    }
    try:
        preview = render_report_email_preview(job, report)
        return {"preview": {"subject": customer_safe_text(preview.get("subject")), "html": customer_safe_text(preview.get("html"))}}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(f"{type(exc).__name__}: {exc}"))


@router.post("/reports/{report_id}/resend-email")
async def report_resend_email(report_id: int):
    try:
        ok, error, report = resend_report_email(report_id)
        return {"ok": ok, "error": customer_safe_text(error), "report": report}
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


def _platform_status_matches_login_session(session: dict[str, Any], platform_status: dict[str, Any]) -> bool:
    if not platform_status:
        return False
    session_account_id = session.get("account_id")
    status_account_id = platform_status.get("active_account_id")
    if session_account_id:
        return str(session_account_id) == str(status_account_id or "")
    if status_account_id:
        return False
    session_profile = str(session.get("profile_path") or "").strip()
    status_profile = str(platform_status.get("profile_path") or "").strip()
    return bool(session_profile and status_profile and session_profile == status_profile)


def _login_capability_response(platform: str, override: dict[str, Any] | None = None) -> dict[str, Any]:
    capability = get_mediacrawler_login_capability(platform)
    return {
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "login_capability_source": "平台采集服务",
        "login_boundary": "复用平台采集服务登录能力",
        "captcha_policy": "遇到验证码、滑块或短信验证时回传状态，等待人工处理",
        "login_engine": "平台采集服务登录模块",
        "login_class": "",
        "bridge_role": "二维码、截图和登录状态回传",
        "qrcode_capture_method": "页面二维码回传",
        "qrcode_prepare_method": "平台登录会话",
        "qrcode_flow_steps": [
            "打开平台登录页",
            "等待二维码或平台验证提示",
            "前端展示二维码、截图或验证状态",
            "运营扫码或按页面提示处理后，系统保存登录状态",
        ],
        "integration_note": "后台只包装平台采集服务已有登录方式；验证码、滑块、短信只回传状态，不自动绕过。",
        "unsupported_behaviors": [
            "不自动处理滑块、图形验证码或短信验证码",
            "不新增平台采集服务尚未支持的登录方式",
        ],
        "supported_login_types": list(capability.get("supported_login_types") or []),
        "supported_login_type_labels": capability.get("supported_login_type_labels") or {},
        "mediacrawler_supported_login_types": list(capability.get("mediacrawler_supported_login_types") or []),
        "qrcode_supported": bool(capability.get("qrcode_supported")),
        "phone_supported": False,
        "cookie_supported": bool(capability.get("cookie_supported")),
        "login_url": str(capability.get("login_url") or ""),
    }


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


def _customer_view_run(item: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id",
        "job_id",
        "status",
        "started_at",
        "finished_at",
        "law_firm_name",
        "display_law_firm_name",
        "job_deleted",
        "legacy_without_job_snapshot",
        "display_status",
        "display_error",
        "summary",
    }
    view = {key: _customer_safe_value(value) for key, value in item.items() if key in allowed}
    view["error_message"] = customer_safe_text(item.get("error_message"))
    return view


def _customer_view_report(item: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id",
        "run_id",
        "job_id",
        "created_at",
        "email_status",
        "email_error",
        "law_firm_name",
        "display_law_firm_name",
        "job_deleted",
        "summary",
    }
    return {key: _customer_safe_value(value) for key, value in item.items() if key in allowed}


def _customer_view_lead(item: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id",
        "platform",
        "content_id",
        "job_id",
        "run_id",
        "law_firm_name",
        "source_keyword",
        "title",
        "description",
        "author_name",
        "content_url",
        "cover_url",
        "publish_time",
        "comment_count",
        "first_seen_at",
        "last_seen_at",
        "eval_status",
        "is_related",
        "is_negative",
        "risk_level",
        "reason",
        "evidence_quotes",
        "recommended_action",
        "evaluated_at",
    }
    view = {
        key: (value if key == "content_id" else _customer_safe_value(value))
        for key, value in item.items()
        if key in allowed
    }
    content_id = str(item.get("content_id") or "")
    if "self" + "test" in content_id.lower():
        view["content_id"] = f"system-check-{item.get('run_id') or item.get('id') or ''}".rstrip("-")
    return view


def _customer_view_platform_status(item: dict[str, Any]) -> dict[str, Any]:
    view = _customer_safe_value(dict(item))
    profile_path = str(item.get("profile_path") or "")
    view["profile_path"] = "网页登录态已配置" if profile_path else ""
    view["profile_path_configured"] = bool(profile_path)
    view["default_profile_path"] = ""
    view["default_profile_path_configured"] = False
    view["last_error"] = customer_safe_text(item.get("last_error"))
    view["login_material_error"] = customer_safe_text(item.get("login_material_error"))
    view["active_proxy_error"] = customer_safe_text(item.get("active_proxy_error"))
    view["login_capability_source"] = "平台采集服务"
    return view


def _customer_view_doctor(status: dict[str, Any]) -> dict[str, Any]:
    checks = []
    for check in status.get("checks") or []:
        checks.append(
            {
                "key": check.get("key"),
                "label": customer_safe_text(check.get("label")),
                "ok": bool(check.get("ok")),
                "message": customer_safe_text(check.get("message")),
            }
        )
    readiness = status.get("readiness") or {}
    readiness_view = {
        "ready": bool(readiness.get("ready")),
        "checks": [
            {
                "key": _customer_readiness_key(str(item.get("key") or "")),
                "label": customer_safe_text(item.get("label")),
                "ok": bool(item.get("ok")),
                "message": customer_safe_text(item.get("message")),
            }
            for item in readiness.get("checks") or []
        ],
        "next_actions": [customer_safe_text(item) for item in readiness.get("next_actions") or []],
        "real_platforms": readiness.get("real_platforms") or [],
        "missing_real_platforms": readiness.get("missing_real_platforms") or [],
        "empty_real_platforms": readiness.get("empty_real_platforms") or [],
        "latest_system_check_report_id": readiness.get("latest_selftest_report_id"),
        "latest_real_report_id": readiness.get("latest_real_report_id"),
    }
    return {
        "ok": bool(status.get("ok")),
        "checks": checks,
        "readiness": readiness_view,
        "recommendations": [customer_safe_text(item) for item in status.get("recommendations") or []],
        "paths": {
            "project_root": "应用目录已配置",
            "monitor_data_dir": "运行数据目录已配置",
            "database": "本地数据库已配置",
            "secret_key": "密钥文件已配置",
        },
    }


def _customer_view_readiness_status(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": bool(readiness.get("ready")),
        "checks": [
            {
                "key": _customer_readiness_key(str(item.get("key") or "")),
                "label": customer_safe_text(item.get("label")),
                "ok": bool(item.get("ok")),
                "message": customer_safe_text(item.get("message")),
            }
            for item in readiness.get("checks") or []
        ],
        "next_actions": [customer_safe_text(item) for item in readiness.get("next_actions") or []],
        "platforms": [_customer_view_platform_status(item) for item in readiness.get("platforms") or []],
        "real_platforms": readiness.get("real_platforms") or [],
        "missing_real_platforms": readiness.get("missing_real_platforms") or [],
        "empty_real_platforms": readiness.get("empty_real_platforms") or [],
        "latest_system_check_report_id": readiness.get("latest_selftest_report_id"),
        "latest_real_report_id": readiness.get("latest_real_report_id"),
    }


def _customer_view_system_checklist(checklist: dict[str, Any]) -> dict[str, Any]:
    return {
        "ready": bool(checklist.get("ready")),
        "items": [
            {
                "key": _customer_readiness_key(str(item.get("key") or "")),
                "label": customer_safe_text(item.get("label")),
                "ok": bool(item.get("ok")),
                "status": "done" if item.get("ok") else "todo",
                "message": customer_safe_text(item.get("message")),
                "detail": customer_safe_text(item.get("detail")),
                "action": customer_safe_text(item.get("action")),
                "target_tab": item.get("target_tab"),
            }
            for item in checklist.get("items") or []
        ],
        "next_actions": [customer_safe_text(item) for item in checklist.get("next_actions") or []],
        "latest_system_check_report_id": checklist.get("latest_selftest_report_id"),
        "latest_real_report_id": checklist.get("latest_real_report_id"),
        "real_platforms": checklist.get("real_platforms") or [],
        "missing_real_platforms": checklist.get("missing_real_platforms") or [],
    }


def _customer_view_system_check_result(result: dict[str, Any]) -> dict[str, Any]:
    report = result.get("report") or {}
    summary = result.get("summary") or {}
    report_id = report.get("id")
    artifacts = {
        "html": _public_artifact(report, "html_path", "html"),
        "excel": _public_artifact(report, "excel_path", "excel"),
        "markdown": _public_artifact(report, "markdown_path", "markdown"),
    }
    return {
        "ok": all(item["exists"] for item in artifacts.values()),
        "run_id": result.get("run_id"),
        "report_id": report_id,
        "law_firm_name": customer_safe_text((result.get("job") or {}).get("law_firm_name") or summary.get("law_firm_name") or "海安律所"),
        "summary": _customer_safe_value(summary),
        "artifacts": artifacts,
        "message": "系统自检报告已生成，可在报告中心预览并下载 HTML、Excel、Markdown。",
    }


def _customer_view_smoke_result(result: dict[str, Any]) -> dict[str, Any]:
    system_check = result.get("selftest") or {}
    doctor = result.get("doctor") or {}
    readiness = result.get("readiness") or {}
    return {
        "ok": bool(result.get("ok")),
        "system_check": {
            "run_id": system_check.get("run_id"),
            "report_id": system_check.get("report_id"),
            "artifacts": _customer_safe_value(system_check.get("artifacts") or {}),
        },
        "doctor": {
            "ok": bool(doctor.get("ok")),
            "failed_checks": [
                {
                    "key": _customer_readiness_key(str(item.get("key") or "")),
                    "label": customer_safe_text(item.get("label")),
                    "message": customer_safe_text(item.get("message")),
                }
                for item in doctor.get("failed_checks") or []
            ],
            "recommendations": [customer_safe_text(item) for item in doctor.get("recommendations") or []],
        },
        "readiness": {
            "ready": bool(readiness.get("ready")),
            "failed_checks": [
                {
                    "key": _customer_readiness_key(str(item.get("key") or "")),
                    "label": customer_safe_text(item.get("label")),
                    "message": customer_safe_text(item.get("message")),
                }
                for item in readiness.get("failed_checks") or []
            ],
            "next_actions": [customer_safe_text(item) for item in readiness.get("next_actions") or []],
        },
        "note": "系统自检不调用真实平台、AI 或邮件服务，只验证数据库、报告生成、附件和诊断汇总链路。",
    }


def _public_artifact(report: dict[str, Any], key: str, download_type: str) -> dict[str, Any]:
    path = Path(str(report.get(key) or ""))
    exists = path.exists()
    return {
        "exists": exists,
        "size": path.stat().st_size if exists else 0,
        "download_url": f"/api/monitor/reports/{report.get('id')}/download?type={download_type}" if report.get("id") else "",
    }


def _customer_readiness_key(key: str) -> str:
    return "system_check_report" if key == "selftest_report" else key


def _customer_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _customer_safe_value(item)
            for key, item in value.items()
            if key
            not in {
                "selftest",
                "html_path",
                "markdown_path",
                "excel_path",
                "raw_response",
                "command",
                "debug_port",
                "run_dir",
                "source",
                "skipped",
                "skip_type",
                "html_path",
                "markdown_path",
                "excel_path",
            }
        }
    if isinstance(value, list):
        return [_customer_safe_value(item) for item in value]
    if isinstance(value, str):
        return customer_safe_text(value)
    return value
