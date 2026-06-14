from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .security import MONITOR_DATA_DIR


ACCOUNT_PROFILE_ROOT = Path(
    os.environ.get("MONITOR_ACCOUNT_PROFILE_ROOT")
    or MONITOR_DATA_DIR / "account_profiles"
).resolve()

_PROFILE_KEY_PATTERN = re.compile(r"^\d+/[a-z0-9_]+/acc_\d+$")
_PLATFORM_PATTERN = re.compile(r"^[a-z0-9_]+$")


def default_account_profile_key(workspace_id: int | None, platform: str, account_id: int | None) -> str:
    workspace = int(workspace_id or 1)
    account = int(account_id or 0)
    normalized_platform = _normalize_platform(platform)
    return f"{workspace}/{normalized_platform}/acc_{account}"


def resolve_account_profile_path(profile_key: str, root: Path | None = None) -> Path:
    key = str(profile_key or "").strip().replace("\\", "/")
    if not _PROFILE_KEY_PATTERN.fullmatch(key):
        raise ValueError("invalid account profile key")
    base = (root or ACCOUNT_PROFILE_ROOT).resolve()
    resolved = (base / Path(*key.split("/"))).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError("invalid account profile key") from exc
    return resolved


def account_profile_environment(account: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    profile_key = str(account.get("profile_key") or "").strip()
    if not profile_key:
        profile_key = default_account_profile_key(
            _safe_int(account.get("workspace_id")),
            str(account.get("platform") or ""),
            _safe_int(account.get("id")),
        )
    runtime_path = resolve_account_profile_path(profile_key, root=root)
    return {
        "profile_key": profile_key,
        "runtime_path": str(runtime_path),
        "profile_path": str(runtime_path),
        "profile_configured": True,
    }


def _normalize_platform(platform: str) -> str:
    value = str(platform or "").strip().lower()
    if not _PLATFORM_PATTERN.fullmatch(value):
        raise ValueError("invalid platform")
    return value


def _safe_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None
