from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response

from ..monitoring.auth import SESSION_COOKIE_NAME
from ..monitoring.auth_context import menu_permissions_for_role, require_authenticated_user, require_role
from ..monitoring.database import (
    authenticate_user,
    create_user_session,
    invalidate_user_session,
    list_users,
    save_user,
)
from ..monitoring.security import customer_safe_text, redact_sensitive


router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login(payload: dict[str, Any], request: Request, response: Response):
    user = authenticate_user(payload.get("email"), payload.get("password"))
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token, session = create_user_session(
        int(user["id"]),
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
    )
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return {"user": _session_user(user), "session": {"expires_at": session.get("expires_at")}}


@router.post("/auth/logout")
async def logout(
    response: Response,
    user: dict[str, Any] = Depends(require_authenticated_user),
    monitor_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    invalidate_user_session(monitor_session)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True, "user_id": user.get("id")}


@router.get("/auth/session")
async def session(user: dict[str, Any] = Depends(require_authenticated_user)):
    return {"user": _session_user(user)}


@router.get("/users")
async def users(admin: dict[str, Any] = Depends(require_role("administrator"))):
    return {"users": [_public_user(user) for user in list_users()], "actor": _session_user(admin)}


@router.post("/users")
async def create_user(payload: dict[str, Any], admin: dict[str, Any] = Depends(require_role("administrator"))):
    try:
        user = save_user(payload, actor_id=int(admin["id"]))
        return {"user": _public_user(user)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


@router.patch("/users/{user_id}")
async def update_user(user_id: int, payload: dict[str, Any], admin: dict[str, Any] = Depends(require_role("administrator"))):
    try:
        user = save_user(payload, user_id=user_id, actor_id=int(admin["id"]))
        return {"user": _public_user(user)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=redact_sensitive(str(exc)))


def _session_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_id": user.get("id"),
        "email": customer_safe_text(user.get("email")),
        "display_name": customer_safe_text(user.get("display_name")),
        "role": user.get("role"),
        "workspace_id": user.get("workspace_id"),
        "menu_permissions": menu_permissions_for_role(str(user.get("role") or "")),
    }


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user.get("id"),
        "workspace_id": user.get("workspace_id"),
        "email": customer_safe_text(user.get("email")),
        "display_name": customer_safe_text(user.get("display_name")),
        "role": user.get("role"),
        "status": user.get("status"),
        "last_login_at": user.get("last_login_at"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at"),
    }
