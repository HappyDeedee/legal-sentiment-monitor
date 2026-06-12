from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .database import list_runs
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIRS = {
    "dy": "cdp_dy_user_data_dir",
    "ks": "cdp_ks_user_data_dir",
    "xhs": "cdp_xhs_user_data_dir",
}
LOGIN_MARKERS = ("登录态", "未登录", "扫码", "no login", "login failed", "login state result: false")


def list_platform_status(project_root: Path | None = None, recent_runs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    root = project_root or PROJECT_ROOT
    browser_data = Path(os.environ.get("MONITOR_BROWSER_DATA_DIR") or root / "browser_data").resolve()
    last_errors = _latest_platform_errors(recent_runs)
    statuses: list[dict[str, Any]] = []
    for platform, dirname in PROFILE_DIRS.items():
        profile_path = browser_data / dirname
        latest_file = _latest_profile_file(profile_path)
        error = last_errors.get(platform, "")
        statuses.append(
            {
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "profile_path": str(profile_path),
                "profile_exists": profile_path.exists(),
                "profile_last_modified": _format_mtime(latest_file or profile_path),
                "last_error": error,
                "needs_login": (not profile_path.exists()) or _looks_like_login_error(error),
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


def _format_mtime(path: Path) -> str | None:
    try:
        if not path.exists():
            return None
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    except OSError:
        return None


def _latest_platform_errors(recent_runs: list[dict[str, Any]] | None = None) -> dict[str, str]:
    errors: dict[str, str] = {}
    for run in recent_runs if recent_runs is not None else list_runs(50):
        summary = run.get("summary") or {}
        platform_results = summary.get("platform_results") or {}
        for platform, result in platform_results.items():
            if platform in errors:
                continue
            error = result.get("error") if isinstance(result, dict) else ""
            if error:
                errors[platform] = redact_sensitive(str(error))
        if len(errors) >= len(PROFILE_DIRS):
            break
    return errors


def _looks_like_login_error(error: str) -> bool:
    lower = (error or "").lower()
    return any(marker.lower() in lower for marker in LOGIN_MARKERS)
