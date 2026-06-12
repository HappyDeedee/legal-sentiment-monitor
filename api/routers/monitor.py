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
    delete_job,
    get_ai_config,
    get_email_config,
    get_job,
    get_platform_login_config,
    get_report,
    get_run,
    has_running_run_for_job,
    init_db,
    list_jobs,
    list_leads,
    list_platform_login_configs,
    list_reports,
    list_runs,
    mark_ai_test_result,
    mark_email_test_result,
    save_ai_config,
    save_email_config,
    save_job,
    save_platform_login_config,
    set_job_enabled,
    set_job_schedule_state,
)
from ..monitoring.mailer import send_test_email
from ..monitoring.doctor import run_doctor
from ..monitoring.login_browser import open_login_browser
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
async def platform_login_browser(platform: str):
    try:
        return open_login_browser(platform)
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
    if not get_job(job_id):
        raise HTTPException(status_code=404, detail="job not found")
    set_job_enabled(job_id, True)
    _refresh_job_schedule_state(get_job(job_id))
    return {"ok": True}


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
