from __future__ import annotations

import json
import os
import ctypes
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .security import MONITOR_DATA_DIR


LOGIN_STATE_DIR = MONITOR_DATA_DIR / "login_windows"
RECENT_CLOSED_TTL_SECONDS = 3600


def record_login_window(platform: str, pid: int, debug_port: int, profile_path: str) -> dict[str, Any]:
    LOGIN_STATE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "platform": platform,
        "pid": int(pid),
        "debug_port": int(debug_port),
        "profile_path": profile_path,
        "opened_at": datetime.now(timezone.utc).isoformat(),
    }
    _state_path(platform).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def login_window_status(platform: str) -> dict[str, Any]:
    data = _read_state(platform)
    if not data:
        return {"is_open": False}
    pid = _coerce_pid(data.get("pid"))
    is_open = bool(pid and _pid_exists(pid))
    if not is_open:
        closed_at = data.get("closed_at") or datetime.now(timezone.utc).isoformat()
        if _closed_state_expired(closed_at):
            _state_path(platform).unlink(missing_ok=True)
            return {"is_open": False, "pid": None, "debug_port": None, "opened_at": None}
        if data.get("pid") is not None:
            data = {**data, "pid": None, "closed_at": closed_at}
            _state_path(platform).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return {
            "is_open": False,
            "pid": None,
            "debug_port": data.get("debug_port"),
            "opened_at": data.get("opened_at"),
            "closed_at": data.get("closed_at") or closed_at,
            "profile_path": data.get("profile_path"),
        }
    return {
        "is_open": is_open,
        "pid": pid,
        "debug_port": data.get("debug_port"),
        "opened_at": data.get("opened_at"),
        "closed_at": data.get("closed_at"),
        "profile_path": data.get("profile_path"),
    }


def _read_state(platform: str) -> dict[str, Any]:
    path = _state_path(platform)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _state_path(platform: str) -> Path:
    return LOGIN_STATE_DIR / f"{platform}.json"


def _coerce_pid(value: Any) -> int | None:
    try:
        pid = int(value)
    except (TypeError, ValueError):
        return None
    return pid if pid > 0 else None


def _closed_state_expired(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    try:
        closed_at = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    if closed_at.tzinfo is None:
        closed_at = closed_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - closed_at.astimezone(timezone.utc) > timedelta(seconds=RECENT_CLOSED_TTL_SECONDS)


def _pid_exists(pid: int) -> bool:
    if os.name == "nt":
        return _windows_pid_exists(pid)
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _windows_pid_exists(pid: int) -> bool:
    process_query_limited_information = 0x1000
    handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, int(pid))
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        still_active = 259
        return exit_code.value == still_active
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)
