from __future__ import annotations

from typing import Any


LOGIN_STATE_PREPARING = "preparing"
LOGIN_STATE_WAITING_QRCODE = "waiting_qrcode"
LOGIN_STATE_WAITING_SCAN = "waiting_scan"
LOGIN_STATE_WAITING_CONFIRM = "waiting_confirm"
LOGIN_STATE_SUCCESS = "success"
LOGIN_STATE_NEEDS_VERIFICATION = "needs_verification"
LOGIN_STATE_QRCODE_FAILED = "qrcode_failed"
LOGIN_STATE_TIMEOUT = "timeout"
LOGIN_STATE_PLATFORM_ERROR = "platform_error"


STRUCTURED_LOGIN_STATES = {
    LOGIN_STATE_PREPARING,
    LOGIN_STATE_WAITING_QRCODE,
    LOGIN_STATE_WAITING_SCAN,
    LOGIN_STATE_WAITING_CONFIRM,
    LOGIN_STATE_SUCCESS,
    LOGIN_STATE_NEEDS_VERIFICATION,
    LOGIN_STATE_QRCODE_FAILED,
    LOGIN_STATE_TIMEOUT,
    LOGIN_STATE_PLATFORM_ERROR,
}

LEGACY_LOGIN_STATE_ALIASES = {
    "waiting_manual_browser": LOGIN_STATE_QRCODE_FAILED,
    "waiting_verification": LOGIN_STATE_NEEDS_VERIFICATION,
    "scanned": LOGIN_STATE_WAITING_CONFIRM,
    "expired": LOGIN_STATE_TIMEOUT,
    "failed": LOGIN_STATE_PLATFORM_ERROR,
}

PENDING_LOGIN_STATES = {
    LOGIN_STATE_PREPARING,
    LOGIN_STATE_WAITING_QRCODE,
    LOGIN_STATE_WAITING_SCAN,
    LOGIN_STATE_WAITING_CONFIRM,
    LOGIN_STATE_NEEDS_VERIFICATION,
}

TERMINAL_LOGIN_STATES = {
    LOGIN_STATE_SUCCESS,
    LOGIN_STATE_QRCODE_FAILED,
    LOGIN_STATE_TIMEOUT,
    LOGIN_STATE_PLATFORM_ERROR,
}


def normalize_login_state(status: Any) -> str:
    value = str(status or "").strip()
    if value in STRUCTURED_LOGIN_STATES:
        return value
    return LEGACY_LOGIN_STATE_ALIASES.get(value, LOGIN_STATE_PREPARING)


def is_pending_login_state(status: Any) -> bool:
    return normalize_login_state(status) in PENDING_LOGIN_STATES


def is_terminal_login_state(status: Any) -> bool:
    return normalize_login_state(status) in TERMINAL_LOGIN_STATES
