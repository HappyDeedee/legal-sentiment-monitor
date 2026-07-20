from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse

from ..monitoring.auth import SESSION_COOKIE_NAME
from ..monitoring.auth_context import require_role
from ..monitoring.database import get_social_account, get_user_for_session_token, record_audit_log
from ..monitoring.login_browser_sync import (
    BrowserSyncError,
    browser_cookie_sync_available,
    cancel_browser_cookie_sync,
    get_browser_cookie_sync_status,
    start_browser_cookie_sync,
)


router = APIRouter(prefix="/monitor", tags=["monitor-browser-sync"])
AdminUser = Depends(require_role("administrator"))

_NO_STORE_HEADERS = {
    "Cache-Control": "no-store, private",
    "Pragma": "no-cache",
    "Expires": "0",
}
@router.post("/social-accounts/{account_id}/browser-sync", status_code=202)
async def start_browser_sync_route(
    account_id: int,
    payload: dict[str, Any] | None = None,
    admin: dict[str, Any] = AdminUser,
):
    if payload:
        raise HTTPException(status_code=400, detail="浏览器同步不接受外部参数")
    if not browser_cookie_sync_available():
        raise HTTPException(status_code=409, detail="浏览器自动同步当前未启用或当前电脑不支持")
    try:
        session = await start_browser_cookie_sync(
            account_id,
            int(admin.get("id") or 0) or None,
            int(admin.get("workspace_id") or 1),
        )
        return {"session": session}
    except BrowserSyncError as exc:
        raise HTTPException(status_code=_status_code(exc.reason), detail=exc.message)


@router.get("/browser-sync/login-sessions/{session_id}")
async def browser_sync_status_route(session_id: int, admin: dict[str, Any] = AdminUser):
    try:
        return {
            "session": await get_browser_cookie_sync_status(
                session_id,
                int(admin.get("workspace_id") or 1),
            )
        }
    except BrowserSyncError as exc:
        raise HTTPException(status_code=_status_code(exc.reason), detail=exc.message)


@router.post("/browser-sync/login-sessions/{session_id}/cancel")
async def browser_sync_cancel_route(session_id: int, admin: dict[str, Any] = AdminUser):
    try:
        return {
            "session": await cancel_browser_cookie_sync(
                session_id,
                int(admin.get("workspace_id") or 1),
            )
        }
    except BrowserSyncError as exc:
        raise HTTPException(status_code=_status_code(exc.reason), detail=exc.message)


@router.post("/social-accounts/{account_id}/cookie-reveal")
async def reveal_social_account_cookie(
    account_id: str,
    monitor_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    """Reveal one account's encrypted Cookie only after an explicit admin POST."""

    user = get_user_for_session_token(monitor_session)
    if not user:
        return _no_store_error(401, "missing or expired session")
    try:
        parsed_account_id = int(account_id)
    except (TypeError, ValueError):
        return _no_store_error(400, "invalid account id")
    if parsed_account_id <= 0:
        return _no_store_error(400, "invalid account id")
    if user.get("role") != "administrator":
        _record_cookie_reveal_audit(user, parsed_account_id, "denied")
        return _no_store_error(403, "permission denied")
    if not browser_cookie_sync_available():
        return _no_store_error(409, "浏览器自动同步当前未启用或当前电脑不支持")
    account = get_social_account(parsed_account_id, masked=False)
    if not account or int(account.get("workspace_id") or 0) != int(user.get("workspace_id") or 1):
        _record_cookie_reveal_audit(user, parsed_account_id, "missing")
        return _no_store_error(404, "account not found")
    cookies = str(account.get("cookies") or "")
    if not cookies:
        _record_cookie_reveal_audit(user, parsed_account_id, "empty")
        return _no_store_error(409, "该账号没有可查看的 Cookie")
    _record_cookie_reveal_audit(user, parsed_account_id, "success")
    return JSONResponse(
        content={
            "account_id": parsed_account_id,
            "platform": str(account.get("platform") or ""),
            "cookie_source": str(account.get("cookie_source") or ""),
            "cookies": cookies,
        },
        headers=_NO_STORE_HEADERS,
    )


def _record_cookie_reveal_audit(user: dict[str, Any], account_id: int, result: str) -> None:
    try:
        record_audit_log(
            "reveal_social_account_cookie",
            "social_account",
            account_id,
            {"result": result},
            user_id=int(user.get("id") or 0) or None,
            workspace_id=int(user.get("workspace_id") or 1),
        )
    except Exception:
        pass


def _no_store_error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(content={"detail": detail}, status_code=status_code, headers=_NO_STORE_HEADERS)


def _status_code(reason: str) -> int:
    if reason in {"account_not_found", "login_session_not_found"}:
        return 404
    if reason.endswith("disabled") or reason.endswith("unsupported_host"):
        return 409
    if reason.endswith("invalid") or reason.endswith("mismatch") or reason == "browser_sync_session_stale":
        return 400
    if "busy" in reason or "conflict" in reason:
        return 409
    return 422
