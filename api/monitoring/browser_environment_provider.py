from __future__ import annotations

import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

from tools.browser_environment import (
    BrowserEnvironmentError,
    BrowserEnvironmentPlan,
    BrowserEnvironmentResult,
    validate_safe_runtime_snapshot,
)

from .account_environment import account_profile_environment
from .account_identity import AccountIdentityError, validate_account_identity


_MANAGED_STATES = frozenset({"generated", "validated", "login_in_progress", "locked", "active"})
_LOCKED_STATES = frozenset({"locked", "active"})
_GENERATED_MARKER = "mediacrawler_account_identity"
_CHROME_VERSION_RE = re.compile(r"(?:Chrome|CriOS)/(\d+(?:\.\d+){0,3})")


def resolve_account_browser_environment(
    account: Mapping[str, Any],
    *,
    action: str,
    trigger_source: str,
    headless: bool,
    launch_mode: str,
    proxy: Mapping[str, Any] | None = None,
    task_proxy_id: int | None = None,
    playwright_executable_path: str,
    diagnostic: bool = False,
) -> BrowserEnvironmentPlan:
    value = dict(account)
    state = str(value.get("identity_state") or "draft")
    if value.get("requires_relogin") or state == "requires_relogin":
        raise AccountIdentityError("account_identity_requires_relogin", "identity_state")
    if state == "resetting":
        raise AccountIdentityError("account_identity_login_conflict", "identity_state")
    if state not in _MANAGED_STATES or value.get("identity_generator_name") != _GENERATED_MARKER:
        raise AccountIdentityError("account_identity_missing", "identity_state")

    account_proxy_id = _optional_positive_int(value.get("proxy_id"))
    requested_task_proxy_id = _optional_positive_int(task_proxy_id)
    differing_locked_override = (
        requested_task_proxy_id
        if state in _LOCKED_STATES and requested_task_proxy_id != account_proxy_id
        else None
    )
    if differing_locked_override is not None:
        raise AccountIdentityError("account_identity_locked_proxy_override", "proxy_id")

    proxy_value, proxy_policy, proxy_url = _resolve_proxy(value, proxy)
    validated = validate_account_identity(
        value,
        bound_proxy_exists=(account_proxy_id is None or proxy_value is not None),
        task_proxy_id=None,
    )

    if diagnostic and state in _LOCKED_STATES:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "browser_source")
    browser_path, browser_source = _resolve_executable(
        playwright_executable_path=playwright_executable_path,
        diagnostic=diagnostic,
    )

    profile_key = str(validated.get("profile_key") or "").strip()
    if not profile_key:
        raise AccountIdentityError("account_identity_requires_relogin", "profile_key")
    try:
        profile = account_profile_environment({**validated, "profile_key": profile_key})
    except ValueError as exc:
        raise AccountIdentityError("account_identity_requires_relogin", "profile_key") from exc
    if str(profile.get("profile_key") or "") != profile_key:
        raise AccountIdentityError("account_identity_requires_relogin", "profile_key")

    profile_mode = "ephemeral_cookie_validation" if action == "cookie_validation" else "persistent"
    if action == "cookie_validation" and launch_mode != "ephemeral_cookie_validation":
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "launch_mode")

    browser_version_match = _CHROME_VERSION_RE.search(str(validated.get("user_agent") or ""))
    browser_version = browser_version_match.group(1) if browser_version_match else "unknown"
    return BrowserEnvironmentPlan(
        contract_version=1,
        resolution_id=f"resolution-{uuid.uuid4().hex}",
        attempt_id=f"attempt-{uuid.uuid4().hex}",
        action=action,
        trigger_source=trigger_source,
        workspace_id=int(validated["workspace_id"]),
        account_id=int(validated["id"]),
        platform=str(validated["platform"]).lower(),
        identity_state=state,
        identity_template=str(validated["identity_template"]),
        browser_executable_path=browser_path,
        browser_family="chromium",
        browser_source=browser_source,
        browser_version=browser_version,
        profile_key=profile_key,
        profile_path=str(profile["runtime_path"]),
        profile_mode=profile_mode,
        proxy_policy=proxy_policy,
        proxy_id=account_proxy_id,
        proxy_region=str(validated["proxy_region_snapshot"]),
        proxy_url=proxy_url,
        browser_platform=str(validated["browser_platform"]),
        user_agent=str(validated["user_agent"]),
        timezone=str(validated["timezone"]),
        locale=str(validated["locale"]),
        accept_language=str(validated["accept_language"]),
        screen_width=int(validated["screen_width"]),
        screen_height=int(validated["screen_height"]),
        viewport_width=int(validated["viewport_width"]),
        viewport_height=int(validated["viewport_height"]),
        device_scale_factor=float(validated["device_scale_factor"]),
        is_mobile=bool(validated["is_mobile"]),
        has_touch=bool(validated["has_touch"]),
        provider_name="playwright",
        launch_mode=launch_mode,
        headless=headless,
    )


def is_legacy_draft_account(account: Mapping[str, Any]) -> bool:
    return (
        str(account.get("identity_state") or "draft") == "draft"
        and str(account.get("identity_generator_name") or "") != _GENERATED_MARKER
    )


def persist_account_browser_environment_result(
    account_id: int,
    plan: BrowserEnvironmentPlan,
    result: BrowserEnvironmentResult,
) -> dict[str, Any]:
    from .database import update_social_account_identity_runtime_snapshot

    snapshot = validate_safe_runtime_snapshot(result.snapshot)
    account_snapshot = snapshot["account"]
    if (
        int(account_id) != plan.account_id
        or account_snapshot["account_id"] != plan.account_id
        or account_snapshot["workspace_id"] != plan.workspace_id
        or account_snapshot["platform"] != plan.platform
        or snapshot["resolution_id"] != plan.resolution_id
        or snapshot["attempt_id"] != plan.attempt_id
        or snapshot["action"] != plan.action
    ):
        raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "result")
    return update_social_account_identity_runtime_snapshot(account_id, snapshot)


def safe_browser_environment_summary(snapshot_json: str) -> dict[str, Any]:
    if not isinstance(snapshot_json, str) or not snapshot_json or len(snapshot_json.encode("utf-8")) > 65536:
        return {}
    try:
        parsed = json.loads(snapshot_json)
        snapshot = validate_safe_runtime_snapshot(parsed)
    except (TypeError, ValueError):
        return {}
    return {
        "provider": {
            "name": snapshot["provider"]["name"],
            "mode": snapshot["provider"]["mode"],
        },
        "browser": {
            "family": snapshot["browser"]["family"],
            "version": snapshot["browser"]["version"],
            "source": snapshot["browser"]["source"],
        },
        "profile": {
            "profile_key": snapshot["profile"]["profile_key"],
            "mode": snapshot["profile"]["mode"],
        },
        "proxy": {
            "policy": snapshot["proxy"]["policy"],
            "effect_proof": snapshot["proxy"]["effect_proof"],
        },
        "status": {
            "ok": snapshot["ok"],
            "reason": snapshot["reason"],
            "validated_at": snapshot["validated_at"],
            "fallback_used": snapshot["fallback_used"],
            "unsupported_field_count": len(snapshot["unsupported_fields"]),
            "mismatch_fields": [item["field"] for item in snapshot["mismatch_evidence"]],
        },
    }


def _resolve_proxy(
    account: Mapping[str, Any],
    proxy: Mapping[str, Any] | None,
) -> tuple[dict[str, Any] | None, str, str]:
    account_proxy_id = _optional_positive_int(account.get("proxy_id"))
    if account_proxy_id is None:
        return None, "direct", ""
    if not proxy:
        raise AccountIdentityError("account_identity_missing", "proxy_id")
    value = dict(proxy)
    if (
        _optional_positive_int(value.get("id")) != account_proxy_id
        or _optional_positive_int(value.get("workspace_id")) != int(account.get("workspace_id") or 0)
        or str(value.get("status") or "") != "active"
    ):
        raise AccountIdentityError("account_identity_missing", "proxy_id")
    proxy_url = str(value.get("proxy_url") or "").strip()
    if not proxy_url:
        raise AccountIdentityError("account_identity_missing", "proxy_id")
    probe_url = str(os.environ.get("MONITOR_BROWSER_PROXY_PROBE_URL") or "").strip()
    if not probe_url or not _valid_http_url(probe_url):
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "proxy_probe")
    return value, "account_bound", proxy_url


def _resolve_executable(*, playwright_executable_path: str, diagnostic: bool) -> tuple[str, str]:
    explicit = str(os.environ.get("MONITOR_BROWSER_EXECUTABLE") or "").strip().strip('"')
    candidate = explicit or str(playwright_executable_path or "").strip().strip('"')
    source = "explicit" if explicit else ("diagnostic_auto_detect" if diagnostic else "playwright_bundled")
    if not candidate:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "browser_executable")
    path = Path(candidate).expanduser().resolve()
    if not path.is_file():
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "browser_executable")
    return str(path), source


def _optional_positive_int(value: Any) -> int | None:
    if value in (None, "", 0):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AccountIdentityError("account_identity_contradiction", "proxy_id") from exc
    if parsed <= 0:
        raise AccountIdentityError("account_identity_contradiction", "proxy_id")
    return parsed


def _valid_http_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
