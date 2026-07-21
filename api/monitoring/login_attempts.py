from __future__ import annotations

import asyncio
from pathlib import Path
import weakref

from .database import expire_login_sessions_for_account, supersede_social_account_identity_login
from .login_browser import close_login_browser_session
from .login_qrcode import close_qrcode_login_session
from .login_state import login_window_status, record_login_window_reconciliation


_METHOD_LABELS = {
    "qrcode": "扫码登录",
    "browser": "浏览器登录",
    "cookie": "Cookie 登录",
}
_ACCOUNT_LOGIN_START_LOCKS: weakref.WeakValueDictionary[int, asyncio.Lock] = weakref.WeakValueDictionary()


def account_login_start_lock(account_id: int) -> asyncio.Lock:
    key = int(account_id)
    lock = _ACCOUNT_LOGIN_START_LOCKS.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _ACCOUNT_LOGIN_START_LOCKS[key] = lock
    return lock


async def supersede_account_login_attempts(
    account_id: int | None,
    platform: str,
    *,
    profile_key: str = "",
    profile_path: str = "",
    new_method: str,
    include_browser_sync: bool = True,
) -> list[int]:
    """Make one account's newest login method authoritative before it starts."""

    method_label = _METHOD_LABELS.get(str(new_method), "新的登录方式")
    switch_message = f"已切换到{method_label}，本次旧登录会话已结束。"
    cancelled_browser_sessions: list[int] = []
    if include_browser_sync and account_id:
        from .login_browser_sync import cancel_active_browser_cookie_syncs_for_account

        cancelled_browser_sessions = await cancel_active_browser_cookie_syncs_for_account(int(account_id))

    if account_id:
        await _supersede_visible_login_browser(
            int(account_id),
            str(platform),
            profile_key=str(profile_key or ""),
            profile_path=str(profile_path or ""),
            message=switch_message,
        )
    expired_session_ids = expire_login_sessions_for_account(
        account_id,
        str(platform),
        profile_path,
        profile_key,
        message=switch_message,
    )
    for session_id in expired_session_ids:
        await close_qrcode_login_session(int(session_id))
    if account_id:
        supersede_social_account_identity_login(
            int(account_id),
            trigger_source=f"login_method_switch:{str(new_method or 'unknown')}",
        )
    return sorted(set(cancelled_browser_sessions + expired_session_ids))


async def _supersede_visible_login_browser(
    account_id: int,
    platform: str,
    *,
    profile_key: str,
    profile_path: str,
    message: str,
) -> None:
    window = login_window_status(platform)
    if not window.get("opened_at") or not _window_matches_profile(window, profile_key, profile_path):
        return
    expected_pid = int(window.get("pid") or 0)
    if window.get("is_open"):
        try:
            result = await close_login_browser_session(
                platform,
                int(window.get("debug_port") or 0),
                expected_pid=expected_pid,
            )
        except Exception as exc:
            refreshed = login_window_status(platform)
            if refreshed.get("is_open") and int(refreshed.get("pid") or 0) == expected_pid:
                raise ValueError("旧登录窗口仍在运行，请关闭后重试。") from exc
        else:
            if not result.get("process_matched") or not result.get("close_requested"):
                raise ValueError("旧登录窗口归属校验失败，请关闭后重试。")
        await _wait_for_visible_login_browser_close(platform, expected_pid)
        refreshed = login_window_status(platform)
        if refreshed.get("is_open") and int(refreshed.get("pid") or 0) == expected_pid:
            raise ValueError("旧登录窗口仍在运行，请关闭后重试。")
    record_login_window_reconciliation(
        platform,
        str(window.get("opened_at") or ""),
        account_id,
        "failed",
        message,
    )


async def _wait_for_visible_login_browser_close(platform: str, expected_pid: int) -> None:
    deadline = asyncio.get_running_loop().time() + 6.0
    while asyncio.get_running_loop().time() < deadline:
        window = login_window_status(platform)
        if not window.get("is_open") or int(window.get("pid") or 0) != int(expected_pid):
            return
        await asyncio.sleep(0.2)


def _window_matches_profile(window: dict, profile_key: str, profile_path: str) -> bool:
    window_key = str(window.get("profile_key") or "").strip()
    expected_key = str(profile_key or "").strip()
    if window_key and expected_key:
        return window_key == expected_key
    window_path = str(window.get("profile_path") or "").strip()
    expected_path = str(profile_path or "").strip()
    if not window_path or not expected_path:
        return False
    try:
        return Path(window_path).resolve() == Path(expected_path).resolve()
    except OSError:
        return window_path == expected_path
