from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .database import get_platform_login_config, list_runs
from .login_state import login_window_status
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


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
    statuses: list[dict[str, Any]] = []
    for platform, dirname in PROFILE_DIRS.items():
        profile_path = browser_data / dirname
        latest_file = _latest_profile_file(profile_path)
        error_info = last_errors.get(platform) or {}
        error = str(error_info.get("error") or "")
        error_at = _parse_time(error_info.get("at"))
        profile_mtime = _mtime(latest_file or profile_path)
        login_window = login_window_status(platform)
        login_config = get_platform_login_config(platform, masked=True)
        login_config_updated_at = _parse_time(login_config.get("updated_at"))
        stale_error = bool(
            error_at
            and ((profile_mtime and profile_mtime > error_at) or (login_config_updated_at and login_config_updated_at > error_at))
        )
        closed_login_window_error = _looks_like_login_window_error(error) and not login_window.get("is_open")
        effective_error = "" if stale_error or closed_login_window_error else error
        login_type = login_config.get("login_type") or "qrcode"
        has_cookie_login = login_type == "cookie" and login_config.get("has_cookies")
        needs_login = _needs_platform_login(profile_path.exists(), has_cookie_login, effective_error)
        statuses.append(
            {
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "login_type": login_type,
                "login_type_label": login_config.get("login_type_label") or login_type,
                "supported_login_types": login_config.get("supported_login_types") or ["qrcode", "cookie"],
                "has_cookies": bool(login_config.get("has_cookies")),
                "profile_path": str(profile_path),
                "profile_exists": profile_path.exists(),
                "profile_last_modified": _format_time(profile_mtime),
                "last_error": effective_error,
                "needs_login": needs_login,
                "login_ready": not needs_login and not login_window.get("is_open"),
                "login_window_open": bool(login_window.get("is_open")),
                "login_window_pid": login_window.get("pid"),
            }
        )
    return statuses


def _latest_profile_file(profile_path: Path) -> Path | None:
    if not profile_path.exists():
        return None
    latest: Path | None = None
    for path in profile_path.rglob("*"):
        if not path.is_file():
            continue
        if latest is None or path.stat().st_mtime > latest.stat().st_mtime:
            latest = path
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


def _needs_platform_login(profile_exists: bool, has_cookie_login: bool, error: str) -> bool:
    if _looks_like_login_error(error):
        return True
    return not (profile_exists or has_cookie_login)
