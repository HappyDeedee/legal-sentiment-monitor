from __future__ import annotations

from typing import Any

from fastapi import Cookie, Depends, HTTPException, status

from .auth import SESSION_COOKIE_NAME
from .database import get_user_for_session_token


ADMIN_ONLY_MENUS = {
    "platform_accounts",
    "proxy_resources",
    "ai_access",
    "users_permissions",
    "ai_rules",
    "mail_config",
    "mail_templates",
    "runtime_strategy",
    "system_diagnostics",
}
NORMAL_USER_MENUS = {"overview", "monitoring", "run_center", "report_center"}


def menu_permissions_for_role(role: str) -> dict[str, bool]:
    menus = {key: True for key in NORMAL_USER_MENUS}
    for key in ADMIN_ONLY_MENUS:
        menus[key] = role == "administrator"
    return menus


def is_administrator(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") == "administrator")


def is_normal_user(user: dict[str, Any] | None) -> bool:
    return bool(user and user.get("role") == "normal")


async def require_authenticated_user(
    monitor_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, Any]:
    user = get_user_for_session_token(monitor_session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing or expired session")
    return user


def require_role(*roles: str):
    async def dependency(user: dict[str, Any] = Depends(require_authenticated_user)) -> dict[str, Any]:
        if user.get("role") not in set(roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        return user

    return dependency
