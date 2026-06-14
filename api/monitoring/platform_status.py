from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .database import get_platform_login_config, latest_successful_login_session_at, list_runs, list_social_accounts
from .login_state import login_window_status
from .normalizer import PLATFORM_LABELS
from .security import customer_safe_text, redact_sensitive


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIRS = {
    "dy": "cdp_dy_user_data_dir",
    "ks": "cdp_ks_user_data_dir",
    "xhs": "cdp_xhs_user_data_dir",
}
LOGIN_MARKERS = ("登录态", "未登录", "扫码", "no login", "login failed", "login state result: false")
LOGIN_WINDOW_MARKERS = ("登录窗口未关闭",)


def list_platform_status(project_root: Path | None = None, recent_runs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    root = project_root or PROJECT_ROOT
    browser_data = Path(os.environ.get("MONITOR_BROWSER_DATA_DIR") or root / "browser_data").resolve()
    last_errors = _latest_platform_errors(recent_runs)
    active_accounts = _active_accounts_by_platform(root if project_root is not None else None)
    statuses: list[dict[str, Any]] = []
    for platform, dirname in PROFILE_DIRS.items():
        default_profile_path = browser_data / dirname
        active_account = active_accounts.get(platform) or {}
        effective_profile_path = Path(active_account.get("profile_path") or default_profile_path)
        latest_file = _latest_profile_file(effective_profile_path)
        error_info = last_errors.get(platform) or {}
        error = str(error_info.get("error") or "")
        error_at = _parse_time(error_info.get("at"))
        profile_mtime = _mtime(latest_file or effective_profile_path)
        login_window = login_window_status(platform)
        login_config = get_platform_login_config(platform, masked=True)
        login_config_updated_at = _parse_time(login_config.get("updated_at"))
        successful_login_at = _parse_time(latest_successful_login_session_at(platform))
        refreshed_by_login_window = _profile_updated_after_login_window(profile_mtime, login_window)
        stale_error = bool(
            error_at
            and (
                (login_config_updated_at and login_config_updated_at > error_at)
                or (successful_login_at and successful_login_at > error_at)
                or (refreshed_by_login_window and profile_mtime and profile_mtime > error_at)
            )
        )
        closed_login_window_error = _looks_like_login_window_error(error) and not login_window.get("is_open")
        effective_error = "" if stale_error or closed_login_window_error else error
        login_type = login_config.get("login_type") or "qrcode"
        if login_type not in {"qrcode", "cookie"}:
            login_type = "qrcode"
        has_cookie_login = login_type == "cookie" and login_config.get("has_cookies")
        profile_exists = effective_profile_path.exists()
        default_profile_exists = default_profile_path.exists()
        material_ready, material_error = _login_material_state(login_type, profile_exists, bool(has_cookie_login))
        needs_login = _needs_platform_login(profile_exists, bool(has_cookie_login), effective_error, login_type)
        statuses.append(
            {
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "login_type": login_type,
                "login_type_label": customer_safe_text(login_config.get("login_type_label") or login_type),
                "login_capability_source": login_config.get("login_capability_source") or "平台采集服务",
                "supported_login_types": login_config.get("supported_login_types") or ["qrcode", "cookie"],
                "unsupported_reason": customer_safe_text(login_config.get("unsupported_reason") or ""),
                "has_cookies": bool(login_config.get("has_cookies")),
                "profile_path": str(effective_profile_path),
                "profile_exists": profile_exists,
                "default_profile_path": str(default_profile_path),
                "default_profile_exists": default_profile_exists,
                "active_account_id": active_account.get("id"),
                "active_account_name": active_account.get("name") or "",
                "using_account_profile": bool(active_account.get("profile_path")),
                "active_proxy_id": active_account.get("proxy_id"),
                "active_proxy_name": active_account.get("proxy_name") or "",
                "active_proxy_status": active_account.get("proxy_status") or "",
                "active_proxy_error": active_account.get("proxy_last_error") or "",
                "profile_last_modified": _format_time(profile_mtime),
                "last_error": customer_safe_text(effective_error),
                "login_material_ready": material_ready,
                "login_material_error": customer_safe_text(material_error),
                "needs_login": needs_login,
                "login_ready": material_ready and not needs_login and not login_window.get("is_open"),
                "login_window_open": bool(login_window.get("is_open")),
                "login_window_pid": login_window.get("pid"),
            }
        )
    return statuses


def _active_accounts_by_platform(scope_root: Path | None = None) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for account in list_social_accounts():
        platform = account.get("platform")
        if platform in result:
            continue
        if account.get("status") != "active":
            continue
        profile_path = str(account.get("profile_path") or "").strip()
        if not profile_path:
            continue
        if scope_root and not _path_is_within(Path(profile_path), scope_root):
            continue
        result[str(platform)] = account
    return result


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _latest_profile_file(profile_path: Path) -> Path | None:
    if not profile_path.exists():
        return None
    latest: Path | None = None
    latest_mtime = -1.0
    try:
        iterator = profile_path.rglob("*")
        for path in iterator:
            try:
                if not path.is_file():
                    continue
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if latest is None or mtime > latest_mtime:
                latest = path
                latest_mtime = mtime
    except OSError:
        return latest
    return latest


def _mtime(path: Path) -> datetime | None:
    try:
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    except OSError:
        return None


def _format_time(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _profile_updated_after_login_window(profile_mtime: datetime | None, login_window: dict[str, Any]) -> bool:
    if not profile_mtime:
        return False
    opened_at = _parse_time(login_window.get("opened_at"))
    closed_at = _parse_time(login_window.get("closed_at"))
    if not opened_at:
        return False
    if login_window.get("is_open"):
        return False
    if profile_mtime <= opened_at:
        return False
    if closed_at and profile_mtime > closed_at + timedelta(seconds=30):
        return False
    return True


def _parse_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _latest_platform_errors(recent_runs: list[dict[str, Any]] | None = None) -> dict[str, dict[str, str]]:
    errors: dict[str, dict[str, str]] = {}
    for run in recent_runs if recent_runs is not None else list_runs(50):
        summary = run.get("summary") or {}
        platform_results = summary.get("platform_results") or {}
        run_time = run.get("finished_at") or run.get("started_at") or ""
        for platform, result in platform_results.items():
            if platform in errors:
                continue
            error = result.get("error") if isinstance(result, dict) else ""
            if error:
                errors[platform] = {"error": redact_sensitive(str(error)), "at": str(run_time)}
        if len(errors) >= len(PROFILE_DIRS):
            break
    return errors


def _looks_like_login_error(error: str) -> bool:
    lower = (error or "").lower()
    return any(marker.lower() in lower for marker in LOGIN_MARKERS)


def _looks_like_login_window_error(error: str) -> bool:
    lower = (error or "").lower()
    return any(marker.lower() in lower for marker in LOGIN_WINDOW_MARKERS)


def _login_material_state(login_type: str, profile_exists: bool, has_cookie_login: bool) -> tuple[bool, str]:
    if login_type == "cookie":
        return (True, "") if has_cookie_login else (False, "Cookie 登录未填写 Cookie")
    return (True, "") if profile_exists else (False, "网页登录态未准备")


def _needs_platform_login(profile_exists: bool, has_cookie_login: bool, error: str, login_type: str) -> bool:
    if _looks_like_login_error(error):
        return True
    return not _login_material_state(login_type, profile_exists, has_cookie_login)[0]
