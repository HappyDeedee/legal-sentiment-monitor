from __future__ import annotations

import copy
import importlib.metadata
import json
import os
import re
import threading
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


PLAN_ENV_NAME = "MONITOR_BROWSER_ENVIRONMENT_PLAN"
RESULT_PATH_ENV_NAME = "MONITOR_BROWSER_ENVIRONMENT_RESULT_PATH"
PLAN_MAX_BYTES = 8192
SNAPSHOT_MAX_BYTES = 65536

_ACTIONS = frozenset({"qr_login", "cookie_validation", "login_check", "crawl"})
_IDENTITY_STATES = frozenset(
    {
        "draft",
        "generated",
        "validated",
        "login_in_progress",
        "locked",
        "active",
        "requires_relogin",
        "resetting",
    }
)
_BROWSER_SOURCES = frozenset(
    {"explicit", "playwright_bundled", "system_managed", "diagnostic_auto_detect"}
)
_PROFILE_MODES = frozenset({"persistent", "ephemeral_cookie_validation"})
_PROXY_POLICIES = frozenset({"account_bound", "direct"})
_LAUNCH_MODES = frozenset(
    {"persistent_launch", "ephemeral_cookie_validation", "cdp_launch"}
)
_EFFECT_PROOFS = frozenset({"pending", "passed", "not_applicable", "failed"})
_UNSUPPORTED_FIELDS = frozenset(
    {
        "canvas",
        "webgl",
        "fonts",
        "plugins",
        "extensions",
        "long_history",
        "novnc",
        "provider_fingerprint_internals",
    }
)
_FORBIDDEN_KEYS = frozenset(
    {
        "cookie",
        "cookies",
        "cookie_value",
        "cookie_values",
        "proxy_url",
        "proxy_credentials",
        "proxy_password",
        "proxy_username",
        "profile_path",
        "profile_runtime_path",
        "browser_executable_path",
        "executable_path",
        "cdp_url",
        "websocket_url",
        "ws_url",
        "debug_port",
        "novnc_token",
        "command",
        "command_line",
        "environment",
        "environment_dump",
        "fingerprint_seed",
        "probe_url",
        "external_ip",
        "exception",
        "raw_exception",
    }
)
_REQUESTED_FIELDS = frozenset(
    {
        "identity_template",
        "browser_platform",
        "user_agent",
        "timezone",
        "locale",
        "accept_language",
        "screen_width",
        "screen_height",
        "viewport_width",
        "viewport_height",
        "device_scale_factor",
        "is_mobile",
        "has_touch",
        "proxy_region_snapshot",
    }
)
_EFFECTIVE_FIELDS = frozenset(
    {
        "user_agent",
        "timezone",
        "locale",
        "accept_language",
        "screen_width",
        "screen_height",
        "viewport_width",
        "viewport_height",
        "device_scale_factor",
        "is_mobile",
        "has_touch",
        "proxy_region_snapshot",
    }
)
_MISMATCH_FIELDS = _REQUESTED_FIELDS | frozenset(
    {
        "browser_family",
        "browser_version",
        "browser_source",
        "provider_mode",
        "profile_key",
        "proxy_effect",
    }
)
_PROBE_FIELDS = frozenset(
    {
        "navigator_user_agent",
        "navigator_language",
        "navigator_languages",
        "timezone",
        "screen_width",
        "screen_height",
        "viewport_width",
        "viewport_height",
        "device_scale_factor",
        "max_touch_points",
        "is_mobile",
        "webdriver",
    }
)
_PLAN_PROXY_ENV_NAMES = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_SOURCE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_SAFE_PLATFORM_RE = re.compile(r"^[a-z0-9_]{1,32}$")
_PROFILE_KEY_RE = re.compile(r"^\d+/[a-z0-9_]+/acc_\d+$")
_TEMPLATE_RE = re.compile(r"^[A-Z0-9_]{1,64}$")
_REGION_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,31}$")
_LOCALE_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{2,8})?$")
_TIMEZONE_RE = re.compile(r"^(?:UTC|[A-Za-z_+\-]+(?:/[A-Za-z0-9_+\-]+)+)$")
_ACCEPT_LANGUAGE_RE = re.compile(r"^[A-Za-z0-9,;=.\- ]{1,256}$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+\-]{0,63}$")
_ABSOLUTE_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|/)")
_URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


class BrowserEnvironmentError(ValueError):
    def __init__(self, reason: str, *fields_: str):
        self.reason = reason
        self.fields = tuple(field for field in fields_ if field)
        suffix = f": {', '.join(self.fields)}" if self.fields else ""
        super().__init__(f"{reason}{suffix}")


@dataclass(frozen=True)
class BrowserEnvironmentPlan:
    contract_version: int
    resolution_id: str
    attempt_id: str
    action: str
    trigger_source: str
    workspace_id: int
    account_id: int
    platform: str
    identity_state: str
    identity_template: str
    browser_executable_path: str
    browser_family: str
    browser_source: str
    browser_version: str
    profile_key: str
    profile_path: str
    profile_mode: str
    proxy_policy: str
    proxy_id: int | None
    proxy_region: str
    proxy_url: str
    browser_platform: str
    user_agent: str
    timezone: str
    locale: str
    accept_language: str
    screen_width: int
    screen_height: int
    viewport_width: int
    viewport_height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool
    provider_name: str
    launch_mode: str
    headless: bool

    def __post_init__(self) -> None:
        _validate_plan(self)


@dataclass(frozen=True)
class BrowserEnvironmentResult:
    ok: bool
    reason: str
    snapshot: dict[str, Any]

    def __post_init__(self) -> None:
        if type(self.ok) is not bool:
            raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "ok")
        snapshot = validate_safe_runtime_snapshot(self.snapshot)
        if snapshot["ok"] is not self.ok or snapshot["reason"] != self.reason:
            raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "result")
        object.__setattr__(self, "snapshot", snapshot)


@dataclass(frozen=True)
class ManagedBrowserSession:
    browser: Any | None
    context: Any
    plan: BrowserEnvironmentPlan


_cached_plan: BrowserEnvironmentPlan | None = None
_cache_lock = threading.Lock()
_CONTEXT_PLAN_ATTR = "_monitor_browser_environment_plan"
_CONTEXT_RUNTIME_ATTR = "_monitor_browser_environment_runtime"
_PAGE_PREPARED_ATTR = "_monitor_browser_environment_prepared"


def browser_environment_plan_to_json(plan: BrowserEnvironmentPlan) -> str:
    _validate_plan(plan)
    payload = json.dumps(asdict(plan), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(payload.encode("utf-8")) > PLAN_MAX_BYTES:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan_size")
    return payload


def browser_environment_plan_from_json(payload: str) -> BrowserEnvironmentPlan:
    if not isinstance(payload, str) or not payload or len(payload.encode("utf-8")) > PLAN_MAX_BYTES:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan")
    try:
        value = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan") from exc
    if not isinstance(value, dict):
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan")
    expected = {field.name for field in fields(BrowserEnvironmentPlan)}
    if set(value) != expected:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan_fields")
    try:
        return BrowserEnvironmentPlan(**value)
    except BrowserEnvironmentError:
        raise
    except (TypeError, ValueError) as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan") from exc


def plan_from_environment(required: bool = False) -> BrowserEnvironmentPlan | None:
    global _cached_plan
    with _cache_lock:
        if _cached_plan is not None:
            return _cached_plan
        payload = os.environ.pop(PLAN_ENV_NAME, "")
        if not payload:
            if required:
                raise BrowserEnvironmentError("account_identity_provider_unsupported", "plan")
            return None
        try:
            plan = browser_environment_plan_from_json(payload)
        finally:
            for name in _PLAN_PROXY_ENV_NAMES:
                os.environ.pop(name, None)
        _cached_plan = plan
        return plan


def current_managed_plan() -> BrowserEnvironmentPlan | None:
    return plan_from_environment(required=False)


def reset_browser_environment_cache_for_tests() -> None:
    global _cached_plan
    with _cache_lock:
        _cached_plan = None


def browser_context_options(plan: BrowserEnvironmentPlan) -> dict[str, Any]:
    _validate_plan(plan)
    options: dict[str, Any] = {
        "executable_path": plan.browser_executable_path,
        "headless": plan.headless,
        "user_agent": plan.user_agent,
        "timezone_id": plan.timezone,
        "locale": plan.locale,
        "extra_http_headers": {"Accept-Language": plan.accept_language},
        "viewport": {"width": plan.viewport_width, "height": plan.viewport_height},
        "screen": {"width": plan.screen_width, "height": plan.screen_height},
        "device_scale_factor": plan.device_scale_factor,
        "is_mobile": plan.is_mobile,
        "has_touch": plan.has_touch,
    }
    if plan.profile_mode == "persistent":
        options["user_data_dir"] = plan.profile_path
    proxy, _ = _proxy_formats(plan)
    if proxy:
        options["proxy"] = proxy
    ordered_keys = (
        "user_data_dir",
        "executable_path",
        "headless",
        "proxy",
        "user_agent",
        "timezone_id",
        "locale",
        "extra_http_headers",
        "viewport",
        "screen",
        "device_scale_factor",
        "is_mobile",
        "has_touch",
    )
    return {key: options[key] for key in ordered_keys if key in options}


def managed_proxy_formats() -> tuple[dict[str, Any] | None, str | None]:
    plan = current_managed_plan()
    return _proxy_formats(plan) if plan else (None, None)


async def launch_managed_browser_context(playwright: Any, plan: BrowserEnvironmentPlan) -> ManagedBrowserSession:
    _validate_plan(plan)
    options = browser_context_options(plan)
    browser = None
    context = None
    try:
        if plan.profile_mode == "persistent":
            Path(plan.profile_path).mkdir(parents=True, exist_ok=True)
            context = await playwright.chromium.launch_persistent_context(
                **options,
                accept_downloads=True,
            )
        else:
            launch_options = {
                key: options[key]
                for key in ("executable_path", "headless", "proxy")
                if key in options
            }
            context_options = {
                key: value
                for key, value in options.items()
                if key not in {"user_data_dir", "executable_path", "headless", "proxy"}
            }
            browser = await playwright.chromium.launch(**launch_options)
            context = await browser.new_context(**context_options, accept_downloads=True)
        bind_managed_context(context, plan)
        await prove_managed_proxy(context, plan)
        return ManagedBrowserSession(browser=browser, context=context, plan=plan)
    except BrowserEnvironmentError as exc:
        if not hasattr(exc, "browser_environment_result"):
            effect = "failed" if plan.proxy_policy == "account_bound" else "not_applicable"
            exc.browser_environment_result = browser_environment_failure_result(
                plan,
                exc.reason,
                proxy_effect=effect,
            )
        await _close_failed_launch(browser, context)
        raise
    except Exception as exc:
        failure = BrowserEnvironmentError("account_identity_provider_browser_crashed", "browser")
        effect = "failed" if plan.proxy_policy == "account_bound" else "not_applicable"
        failure.browser_environment_result = browser_environment_failure_result(
            plan,
            failure.reason,
            proxy_effect=effect,
        )
        await _close_failed_launch(browser, context)
        raise failure from exc


async def verify_managed_page(context: Any, page: Any) -> BrowserEnvironmentResult | None:
    plan = _context_plan(context) or current_managed_plan()
    if plan is None:
        return None
    if plan.launch_mode == "cdp_launch" and not _page_is_prepared(page, plan):
        failure = BrowserEnvironmentError("account_identity_provider_unsupported", "cdp_page_unprepared")
        runtime = _context_runtime_state(context)
        failure.browser_environment_result = browser_environment_failure_result(
            plan,
            failure.reason,
            proxy_effect=str(runtime.get("proxy_effect_proof") or "failed"),
        )
        write_browser_environment_result(failure.browser_environment_result)
        raise failure
    try:
        probes = await page.evaluate(
            """() => ({
              user_agent: String(navigator.userAgent || ''),
              timezone: String(Intl.DateTimeFormat().resolvedOptions().timeZone || ''),
              language: String(navigator.language || ''),
              languages: Array.from(navigator.languages || []).map(String),
              screen_width: Number(window.screen.width),
              screen_height: Number(window.screen.height),
              viewport_width: Number(window.innerWidth),
              viewport_height: Number(window.innerHeight),
              device_scale_factor: Number(window.devicePixelRatio),
              max_touch_points: Number(navigator.maxTouchPoints || 0),
              is_mobile: Boolean(/Mobi|Android/i.test(navigator.userAgent || '')),
              webdriver: Boolean(navigator.webdriver)
            })"""
        )
        if not isinstance(probes, dict):
            raise TypeError("invalid probe result")
        runtime = _context_runtime_state(context)
        accept_language = str(runtime.get("accept_language") or "")
        browser = getattr(context, "browser", None)
        browser_version = str(getattr(browser, "version", "") or "")
        if not browser_version:
            raise TypeError("missing browser version")
        effective = {
            "user_agent": str(probes.get("user_agent") or ""),
            "timezone": str(probes.get("timezone") or ""),
            "locale": str(probes.get("language") or ""),
            "accept_language": accept_language,
            "screen_width": _strict_probe_int(probes.get("screen_width")),
            "screen_height": _strict_probe_int(probes.get("screen_height")),
            "viewport_width": _strict_probe_int(probes.get("viewport_width")),
            "viewport_height": _strict_probe_int(probes.get("viewport_height")),
            "device_scale_factor": _strict_probe_number(probes.get("device_scale_factor")),
            "is_mobile": _strict_probe_bool(probes.get("is_mobile")),
            "has_touch": _strict_probe_int(probes.get("max_touch_points"), allow_zero=True) > 0,
            "proxy_region_snapshot": plan.proxy_region,
        }
        requested = _requested_snapshot(plan)
        effective_languages = [str(item) for item in probes.get("languages", [])]
        comparisons = (
            ("user_agent", plan.user_agent, effective["user_agent"]),
            ("timezone", plan.timezone, effective["timezone"]),
            ("locale", plan.locale, effective["locale"]),
            ("accept_language", plan.accept_language, effective["accept_language"]),
            ("screen_width", plan.screen_width, effective["screen_width"]),
            ("screen_height", plan.screen_height, effective["screen_height"]),
            ("viewport_width", plan.viewport_width, effective["viewport_width"]),
            ("viewport_height", plan.viewport_height, effective["viewport_height"]),
            ("device_scale_factor", float(plan.device_scale_factor), float(effective["device_scale_factor"])),
            ("has_touch", plan.has_touch, effective["has_touch"]),
            ("is_mobile", plan.is_mobile, effective["is_mobile"]),
            ("browser_version", plan.browser_version, browser_version),
        )
        mismatch_evidence = [
            {"field": field_name, "requested": requested_value, "effective": effective_value}
            for field_name, requested_value, effective_value in comparisons
            if requested_value != effective_value
        ]
        expected_languages = _accept_language_tags(plan.accept_language)
        if effective_languages != expected_languages and not any(
            item["field"] == "accept_language" for item in mismatch_evidence
        ):
            mismatch_evidence.append(
                {
                    "field": "accept_language",
                    "requested": plan.accept_language,
                    "effective": ",".join(effective_languages),
                }
            )
        ok = not mismatch_evidence
        snapshot = {
            "contract_version": 1,
            "resolution_id": plan.resolution_id,
            "attempt_id": plan.attempt_id,
            "action": plan.action,
            "trigger_source": plan.trigger_source,
            "account": {
                "workspace_id": plan.workspace_id,
                "account_id": plan.account_id,
                "platform": plan.platform,
                "identity_state": plan.identity_state,
            },
            "browser": {
                "family": plan.browser_family,
                "version": browser_version,
                "source": plan.browser_source,
            },
            "profile": {"profile_key": plan.profile_key, "mode": plan.profile_mode},
            "proxy": {
                "policy": plan.proxy_policy,
                "proxy_id": plan.proxy_id,
                "region": plan.proxy_region,
                "effect_proof": str(runtime.get("proxy_effect_proof") or ""),
            },
            "requested": requested,
            "effective": effective,
            "provider": {
                "name": plan.provider_name,
                "mode": plan.launch_mode,
                "version": _playwright_version(),
            },
            "probes": {
                "navigator_user_agent": effective["user_agent"],
                "navigator_language": effective["locale"],
                "navigator_languages": effective_languages,
                "timezone": effective["timezone"],
                "screen_width": effective["screen_width"],
                "screen_height": effective["screen_height"],
                "viewport_width": effective["viewport_width"],
                "viewport_height": effective["viewport_height"],
                "device_scale_factor": effective["device_scale_factor"],
                "max_touch_points": _strict_probe_int(probes.get("max_touch_points"), allow_zero=True),
                "is_mobile": effective["is_mobile"],
                "webdriver": _strict_probe_bool(probes.get("webdriver")),
            },
            "unsupported_fields": ["canvas", "webgl", "fonts", "plugins"],
            "mismatch_evidence": mismatch_evidence,
            "fallback_used": False,
            "ok": ok,
            "reason": "" if ok else "account_identity_snapshot_mismatch",
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = BrowserEnvironmentResult(ok=ok, reason=snapshot["reason"], snapshot=snapshot)
        write_browser_environment_result(result)
        return result
    except BrowserEnvironmentError:
        raise
    except Exception as exc:
        failure = BrowserEnvironmentError("account_identity_provider_browser_crashed", "page")
        runtime = _context_runtime_state(context)
        failure.browser_environment_result = browser_environment_failure_result(
            plan,
            failure.reason,
            proxy_effect=str(runtime.get("proxy_effect_proof") or "failed"),
        )
        raise failure from exc


def browser_environment_failure_result(
    plan: BrowserEnvironmentPlan,
    reason: str,
    *,
    proxy_effect: str,
) -> BrowserEnvironmentResult:
    snapshot = {
        "contract_version": 1,
        "resolution_id": plan.resolution_id,
        "attempt_id": plan.attempt_id,
        "action": plan.action,
        "trigger_source": plan.trigger_source,
        "account": {
            "workspace_id": plan.workspace_id,
            "account_id": plan.account_id,
            "platform": plan.platform,
            "identity_state": plan.identity_state,
        },
        "browser": {
            "family": plan.browser_family,
            "version": plan.browser_version,
            "source": plan.browser_source,
        },
        "profile": {"profile_key": plan.profile_key, "mode": plan.profile_mode},
        "proxy": {
            "policy": plan.proxy_policy,
            "proxy_id": plan.proxy_id,
            "region": plan.proxy_region,
            "effect_proof": proxy_effect,
        },
        "requested": _requested_snapshot(plan),
        "effective": {},
        "provider": {
            "name": plan.provider_name,
            "mode": plan.launch_mode,
            "version": _playwright_version(),
        },
        "probes": {},
        "unsupported_fields": ["canvas", "webgl", "fonts", "plugins"],
        "mismatch_evidence": [],
        "fallback_used": False,
        "ok": False,
        "reason": reason,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    return BrowserEnvironmentResult(ok=False, reason=reason, snapshot=snapshot)


def bind_managed_context(
    context: Any,
    plan: BrowserEnvironmentPlan | None = None,
) -> BrowserEnvironmentPlan | None:
    resolved = plan or current_managed_plan()
    if resolved is None:
        return None
    _bind_context_plan(context, resolved)
    _attach_accept_language_recorder(context)
    return resolved


async def prove_managed_proxy(
    context: Any,
    plan: BrowserEnvironmentPlan | None = None,
) -> None:
    resolved = plan or _context_plan(context) or current_managed_plan()
    if resolved is None:
        return
    try:
        await _prove_managed_proxy(context, resolved)
    except BrowserEnvironmentError as exc:
        if not hasattr(exc, "browser_environment_result"):
            exc.browser_environment_result = browser_environment_failure_result(
                resolved,
                exc.reason,
                proxy_effect="failed" if resolved.proxy_policy == "account_bound" else "not_applicable",
            )
        write_browser_environment_result(exc.browser_environment_result)
        raise


async def prepare_managed_page(context: Any, page: Any) -> None:
    plan = _context_plan(context) or current_managed_plan()
    if plan is None:
        return
    if _page_is_prepared(page, plan):
        return
    if plan.launch_mode != "cdp_launch":
        _mark_page_prepared(page, plan)
        return
    commands = (
        (
            "Emulation.setUserAgentOverride",
            {
                "userAgent": plan.user_agent,
                "acceptLanguage": plan.accept_language,
                "platform": plan.browser_platform,
            },
        ),
        ("Emulation.setTimezoneOverride", {"timezoneId": plan.timezone}),
        ("Emulation.setLocaleOverride", {"locale": plan.locale}),
        (
            "Emulation.setDeviceMetricsOverride",
            {
                "width": plan.viewport_width,
                "height": plan.viewport_height,
                "deviceScaleFactor": plan.device_scale_factor,
                "mobile": plan.is_mobile,
                "screenWidth": plan.screen_width,
                "screenHeight": plan.screen_height,
            },
        ),
        ("Emulation.setTouchEmulationEnabled", {"enabled": plan.has_touch}),
    )
    try:
        session = await context.new_cdp_session(page)
        for method, params in commands:
            await session.send(method, params)
        _mark_page_prepared(page, plan)
    except Exception as exc:
        failure = BrowserEnvironmentError("account_identity_provider_unsupported", "cdp_page_prepare")
        runtime = _context_runtime_state(context)
        failure.browser_environment_result = browser_environment_failure_result(
            plan,
            failure.reason,
            proxy_effect=str(runtime.get("proxy_effect_proof") or "failed"),
        )
        write_browser_environment_result(failure.browser_environment_result)
        raise failure from exc


def validate_safe_runtime_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "snapshot")
    try:
        encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "snapshot") from exc
    if len(encoded.encode("utf-8")) > SNAPSHOT_MAX_BYTES:
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "snapshot_size")
    _reject_forbidden_recursive(snapshot)

    required_top = {
        "contract_version",
        "resolution_id",
        "attempt_id",
        "action",
        "trigger_source",
        "account",
        "browser",
        "profile",
        "proxy",
        "requested",
        "effective",
        "provider",
        "probes",
        "unsupported_fields",
        "mismatch_evidence",
        "fallback_used",
        "ok",
        "reason",
        "validated_at",
    }
    _require_exact_keys(snapshot, required_top, "snapshot")
    if type(snapshot["fallback_used"]) is not bool or type(snapshot["ok"]) is not bool:
        _unsafe("status")
    if snapshot["contract_version"] != 1 or type(snapshot["contract_version"]) is not int:
        _unsafe("contract_version")
    _safe_id(snapshot["resolution_id"], "resolution_id")
    _safe_id(snapshot["attempt_id"], "attempt_id")
    if snapshot["action"] not in _ACTIONS:
        _unsafe("action")
    _safe_source(snapshot["trigger_source"], "trigger_source")

    account = _mapping(snapshot["account"], "account")
    _require_exact_keys(account, {"workspace_id", "account_id", "platform", "identity_state"}, "account")
    _positive_int(account["workspace_id"], "account.workspace_id")
    _positive_int(account["account_id"], "account.account_id")
    if not isinstance(account["platform"], str) or not _SAFE_PLATFORM_RE.fullmatch(account["platform"]):
        _unsafe("account.platform")
    if account["identity_state"] not in _IDENTITY_STATES:
        _unsafe("account.identity_state")

    browser = _mapping(snapshot["browser"], "browser")
    _require_exact_keys(browser, {"family", "version", "source"}, "browser")
    if browser["family"] != "chromium":
        _unsafe("browser.family")
    _version(browser["version"], "browser.version")
    if browser["source"] not in _BROWSER_SOURCES:
        _unsafe("browser.source")

    profile = _mapping(snapshot["profile"], "profile")
    _require_exact_keys(profile, {"profile_key", "mode"}, "profile")
    if not isinstance(profile["profile_key"], str) or not _PROFILE_KEY_RE.fullmatch(profile["profile_key"]):
        _unsafe("profile.profile_key")
    if profile["mode"] not in _PROFILE_MODES:
        _unsafe("profile.mode")

    proxy = _mapping(snapshot["proxy"], "proxy")
    _require_exact_keys(proxy, {"policy", "proxy_id", "region", "effect_proof"}, "proxy")
    if proxy["policy"] not in _PROXY_POLICIES:
        _unsafe("proxy.policy")
    if proxy["policy"] == "account_bound":
        _positive_int(proxy["proxy_id"], "proxy.proxy_id")
        if proxy["effect_proof"] not in {"pending", "passed", "failed"}:
            _unsafe("proxy.effect_proof")
    else:
        if proxy["proxy_id"] is not None or proxy["effect_proof"] != "not_applicable":
            _unsafe("proxy")
    _region(proxy["region"], "proxy.region")

    requested = _mapping(snapshot["requested"], "requested")
    effective = _mapping(snapshot["effective"], "effective")
    _require_exact_keys(requested, _REQUESTED_FIELDS, "requested")
    if snapshot["ok"] or effective:
        _require_exact_keys(effective, _EFFECTIVE_FIELDS, "effective")
    for field_name, value in requested.items():
        _validate_field_scalar(field_name, value, f"requested.{field_name}")
    for field_name, value in effective.items():
        _validate_field_scalar(field_name, value, f"effective.{field_name}")

    provider = _mapping(snapshot["provider"], "provider")
    _require_exact_keys(provider, {"name", "mode", "version"}, "provider")
    if provider["name"] != "playwright" or provider["mode"] not in _LAUNCH_MODES:
        _unsafe("provider")
    _version(provider["version"], "provider.version")

    probes = _mapping(snapshot["probes"], "probes")
    if snapshot["ok"] or probes:
        _require_exact_keys(probes, _PROBE_FIELDS, "probes")
        _validate_probe_values(probes)

    unsupported = snapshot["unsupported_fields"]
    if (
        not isinstance(unsupported, list)
        or len(unsupported) > len(_UNSUPPORTED_FIELDS)
        or len(unsupported) != len(set(unsupported))
        or any(item not in _UNSUPPORTED_FIELDS for item in unsupported)
    ):
        _unsafe("unsupported_fields")

    mismatches = snapshot["mismatch_evidence"]
    if not isinstance(mismatches, list) or len(mismatches) > 32:
        _unsafe("mismatch_evidence")
    for index, mismatch in enumerate(mismatches):
        item = _mapping(mismatch, f"mismatch_evidence.{index}")
        _require_exact_keys(item, {"field", "requested", "effective"}, f"mismatch_evidence.{index}")
        field_name = item["field"]
        if field_name not in _MISMATCH_FIELDS:
            _unsafe(f"mismatch_evidence.{index}.field")
        _validate_field_scalar(field_name, item["requested"], f"mismatch_evidence.{index}.requested")
        _validate_field_scalar(field_name, item["effective"], f"mismatch_evidence.{index}.effective")

    reason = snapshot["reason"]
    if not isinstance(reason, str) or len(reason) > 96:
        _unsafe("reason")
    if reason and not re.fullmatch(r"account_identity_[a-z0-9_]+", reason):
        _unsafe("reason")
    if snapshot["ok"] and (reason or mismatches):
        raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "status")
    if not snapshot["ok"] and not reason:
        raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "status")
    _iso_datetime(snapshot["validated_at"], "validated_at")
    return copy.deepcopy(snapshot)


def browser_environment_result_from_json(payload: str) -> BrowserEnvironmentResult:
    if not isinstance(payload, str) or not payload or len(payload.encode("utf-8")) > SNAPSHOT_MAX_BYTES:
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "result")
    try:
        value = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "result") from exc
    if not isinstance(value, dict) or set(value) != {"ok", "reason", "snapshot"}:
        raise BrowserEnvironmentError("account_identity_snapshot_unsafe", "result")
    return BrowserEnvironmentResult(**value)


def write_browser_environment_result(result: BrowserEnvironmentResult) -> None:
    validated = BrowserEnvironmentResult(result.ok, result.reason, result.snapshot)
    destination_value = os.environ.get(RESULT_PATH_ENV_NAME, "")
    if not destination_value:
        return
    destination = Path(destination_value).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(validated), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    temp_path = destination.with_name(f"{destination.name}.tmp.{os.getpid()}")
    temp_path.write_text(payload, encoding="utf-8")
    os.replace(temp_path, destination)


def _bind_context_plan(context: Any, plan: BrowserEnvironmentPlan) -> None:
    runtime = {
        "accept_language": "",
        "proxy_effect_proof": "pending" if plan.proxy_policy == "account_bound" else "not_applicable",
    }
    try:
        setattr(context, _CONTEXT_PLAN_ATTR, plan)
        setattr(context, _CONTEXT_RUNTIME_ATTR, runtime)
        setattr(context, "_monitor_proxy_effect_proof", runtime["proxy_effect_proof"])
    except Exception as exc:
        raise BrowserEnvironmentError(
            "account_identity_provider_unsupported",
            "context_binding",
        ) from exc


def _context_plan(context: Any) -> BrowserEnvironmentPlan | None:
    plan = getattr(context, _CONTEXT_PLAN_ATTR, None)
    if plan is None:
        return None
    if not isinstance(plan, BrowserEnvironmentPlan):
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "context_binding")
    return plan


def _context_runtime_state(context: Any) -> dict[str, Any]:
    runtime = getattr(context, _CONTEXT_RUNTIME_ATTR, None)
    if not isinstance(runtime, dict):
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "context_binding")
    return runtime


def _page_is_prepared(page: Any, plan: BrowserEnvironmentPlan) -> bool:
    return getattr(page, _PAGE_PREPARED_ATTR, None) == (plan.resolution_id, plan.attempt_id)


def _mark_page_prepared(page: Any, plan: BrowserEnvironmentPlan) -> None:
    try:
        setattr(page, _PAGE_PREPARED_ATTR, (plan.resolution_id, plan.attempt_id))
    except Exception as exc:
        raise BrowserEnvironmentError(
            "account_identity_provider_unsupported",
            "cdp_page_binding",
        ) from exc


def _attach_accept_language_recorder(context: Any) -> None:
    def record(request: Any) -> None:
        headers = getattr(request, "headers", {})
        if not isinstance(headers, dict):
            return
        value = next(
            (str(item) for key, item in headers.items() if str(key).lower() == "accept-language"),
            "",
        )
        if value:
            _context_runtime_state(context)["accept_language"] = value

    try:
        context.on("request", record)
    except Exception as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "request_headers") from exc


async def _prove_managed_proxy(context: Any, plan: BrowserEnvironmentPlan) -> None:
    if plan.proxy_policy == "direct":
        _set_proxy_effect(context, "not_applicable")
        return
    probe_url = str(os.environ.get("MONITOR_BROWSER_PROXY_PROBE_URL") or "").strip()
    if not probe_url or not _URI_SCHEME_RE.match(probe_url):
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "proxy_probe")
    timeout = _proxy_probe_timeout_ms()
    page = None
    try:
        page = await context.new_page()
        response = await page.goto(
            probe_url,
            wait_until="domcontentloaded",
            timeout=timeout,
        )
        if response is None or not bool(getattr(response, "ok", False)):
            raise BrowserEnvironmentError("account_identity_proxy_proof_failed", "proxy_probe")
        body = await response.json()
        if not isinstance(body, dict) or not isinstance(body.get("region"), str):
            raise BrowserEnvironmentError("account_identity_proxy_proof_failed", "proxy_probe")
        if body["region"] != plan.proxy_region:
            raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "proxy_region_snapshot")
        _set_proxy_effect(context, "passed")
    except BrowserEnvironmentError:
        _set_proxy_effect(context, "failed")
        raise
    except Exception as exc:
        _set_proxy_effect(context, "failed")
        raise BrowserEnvironmentError("account_identity_proxy_proof_failed", "proxy_probe") from exc
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:
                pass


def _set_proxy_effect(context: Any, value: str) -> None:
    _context_runtime_state(context)["proxy_effect_proof"] = value
    try:
        setattr(context, "_monitor_proxy_effect_proof", value)
    except (AttributeError, TypeError):
        pass


def _proxy_probe_timeout_ms() -> int:
    raw = str(os.environ.get("MONITOR_BROWSER_PROXY_PROBE_TIMEOUT_MS") or "30000").strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "proxy_probe_timeout") from exc
    if not 1 <= value <= 120000:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "proxy_probe_timeout")
    return value


async def _close_failed_launch(browser: Any, context: Any) -> None:
    if context is not None:
        try:
            await context.close()
        except Exception:
            pass
    if browser is not None:
        try:
            await browser.close()
        except Exception:
            pass


def _requested_snapshot(plan: BrowserEnvironmentPlan) -> dict[str, Any]:
    return {
        "identity_template": plan.identity_template,
        "browser_platform": plan.browser_platform,
        "user_agent": plan.user_agent,
        "timezone": plan.timezone,
        "locale": plan.locale,
        "accept_language": plan.accept_language,
        "screen_width": plan.screen_width,
        "screen_height": plan.screen_height,
        "viewport_width": plan.viewport_width,
        "viewport_height": plan.viewport_height,
        "device_scale_factor": float(plan.device_scale_factor),
        "is_mobile": plan.is_mobile,
        "has_touch": plan.has_touch,
        "proxy_region_snapshot": plan.proxy_region,
    }


def _playwright_version() -> str:
    try:
        return importlib.metadata.version("playwright")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _accept_language_tags(value: str) -> list[str]:
    return [part.split(";", 1)[0].strip() for part in value.split(",") if part.split(";", 1)[0].strip()]


def _strict_probe_int(value: Any, *, allow_zero: bool = False) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1):
        raise TypeError("invalid integer probe")
    return value


def _strict_probe_number(value: Any) -> float:
    if type(value) not in {int, float} or isinstance(value, bool) or float(value) <= 0:
        raise TypeError("invalid numeric probe")
    return float(value)


def _strict_probe_bool(value: Any) -> bool:
    if type(value) is not bool:
        raise TypeError("invalid boolean probe")
    return value


def _validate_plan(plan: BrowserEnvironmentPlan) -> None:
    if plan.contract_version != 1 or type(plan.contract_version) is not int:
        _provider_unsupported("contract_version")
    _safe_id(plan.resolution_id, "resolution_id", provider_error=True)
    _safe_id(plan.attempt_id, "attempt_id", provider_error=True)
    if plan.action not in _ACTIONS:
        _provider_unsupported("action")
    _safe_source(plan.trigger_source, "trigger_source", provider_error=True)
    _positive_int(plan.workspace_id, "workspace_id", provider_error=True)
    _positive_int(plan.account_id, "account_id", provider_error=True)
    if not isinstance(plan.platform, str) or not _SAFE_PLATFORM_RE.fullmatch(plan.platform):
        _provider_unsupported("platform")
    if plan.identity_state not in _IDENTITY_STATES:
        _provider_unsupported("identity_state")
    if not isinstance(plan.identity_template, str) or not _TEMPLATE_RE.fullmatch(plan.identity_template):
        _provider_unsupported("identity_template")
    for field_name in ("browser_executable_path", "profile_path"):
        value = getattr(plan, field_name)
        if not isinstance(value, str) or not value.strip() or "\x00" in value:
            _provider_unsupported(field_name)
    if plan.browser_family != "chromium" or plan.browser_source not in _BROWSER_SOURCES:
        _provider_unsupported("browser")
    _version(plan.browser_version, "browser_version", provider_error=True)
    if not isinstance(plan.profile_key, str) or not _PROFILE_KEY_RE.fullmatch(plan.profile_key):
        _provider_unsupported("profile_key")
    if plan.profile_mode not in _PROFILE_MODES or plan.proxy_policy not in _PROXY_POLICIES:
        _provider_unsupported("mode")
    _region(plan.proxy_region, "proxy_region", provider_error=True)
    if plan.proxy_policy == "account_bound":
        _positive_int(plan.proxy_id, "proxy_id", provider_error=True)
        _parse_proxy_url(plan.proxy_url)
    elif plan.proxy_id is not None or plan.proxy_url:
        _provider_unsupported("proxy")
    if plan.browser_platform not in {"windows", "macos", "android"}:
        _provider_unsupported("browser_platform")
    for field_name in ("user_agent", "timezone", "locale", "accept_language"):
        _validate_field_scalar(field_name, getattr(plan, field_name), field_name, provider_error=True)
    for field_name in ("screen_width", "screen_height", "viewport_width", "viewport_height"):
        _positive_int(getattr(plan, field_name), field_name, provider_error=True)
    if plan.viewport_width > plan.screen_width or plan.viewport_height > plan.screen_height:
        _provider_unsupported("viewport")
    _positive_number(plan.device_scale_factor, "device_scale_factor", provider_error=True)
    if type(plan.is_mobile) is not bool or type(plan.has_touch) is not bool or type(plan.headless) is not bool:
        _provider_unsupported("boolean")
    if plan.provider_name != "playwright" or plan.launch_mode not in _LAUNCH_MODES:
        _provider_unsupported("provider")
    if plan.action == "cookie_validation":
        if plan.profile_mode != "ephemeral_cookie_validation" or plan.launch_mode != "ephemeral_cookie_validation":
            _provider_unsupported("cookie_validation_mode")
    elif plan.profile_mode != "persistent":
        _provider_unsupported("profile_mode")


def _proxy_formats(plan: BrowserEnvironmentPlan) -> tuple[dict[str, Any] | None, str | None]:
    if plan.proxy_policy == "direct":
        return None, None
    parsed = _parse_proxy_url(plan.proxy_url)
    host = parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    server = f"{parsed.scheme}://{host}"
    if parsed.port:
        server += f":{parsed.port}"
    proxy: dict[str, Any] = {"server": server}
    if parsed.username is not None:
        proxy["username"] = unquote(parsed.username)
    if parsed.password is not None:
        proxy["password"] = unquote(parsed.password)
    return proxy, plan.proxy_url


def _parse_proxy_url(value: str):
    if not isinstance(value, str) or len(value) > 2048 or "\x00" in value:
        _provider_unsupported("proxy_url")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "proxy_url") from exc
    if parsed.scheme not in {"http", "https", "socks5"} or not parsed.hostname or port is None:
        _provider_unsupported("proxy_url")
    return parsed


def _validate_probe_values(probes: dict[str, Any]) -> None:
    _validate_field_scalar("user_agent", probes["navigator_user_agent"], "probes.navigator_user_agent")
    _validate_field_scalar("locale", probes["navigator_language"], "probes.navigator_language")
    languages = probes["navigator_languages"]
    if not isinstance(languages, list) or not languages or len(languages) > 10:
        _unsafe("probes.navigator_languages")
    for value in languages:
        _validate_field_scalar("locale", value, "probes.navigator_languages")
    _validate_field_scalar("timezone", probes["timezone"], "probes.timezone")
    for field_name in ("screen_width", "screen_height", "viewport_width", "viewport_height"):
        _validate_field_scalar(field_name, probes[field_name], f"probes.{field_name}")
    _validate_field_scalar("device_scale_factor", probes["device_scale_factor"], "probes.device_scale_factor")
    if type(probes["max_touch_points"]) is not int or probes["max_touch_points"] < 0:
        _unsafe("probes.max_touch_points")
    if type(probes["is_mobile"]) is not bool or type(probes["webdriver"]) is not bool:
        _unsafe("probes.boolean")


def _validate_field_scalar(field_name: str, value: Any, path: str, *, provider_error: bool = False) -> None:
    fail = _provider_unsupported if provider_error else _unsafe
    if field_name in {"screen_width", "screen_height", "viewport_width", "viewport_height"}:
        if type(value) is not int or value <= 0 or value > 20000:
            fail(path)
        return
    if field_name == "device_scale_factor":
        if type(value) not in {int, float} or isinstance(value, bool) or not 0 < float(value) <= 10:
            fail(path)
        return
    if field_name in {"is_mobile", "has_touch"}:
        if type(value) is not bool:
            fail(path)
        return
    if not isinstance(value, str) or not value or len(value) > (1024 if field_name == "user_agent" else 256):
        fail(path)
        return
    if "\x00" in value or "\r" in value or "\n" in value or _URI_SCHEME_RE.match(value) or _ABSOLUTE_PATH_RE.match(value):
        fail(path)
        return
    valid = True
    if field_name == "identity_template":
        valid = bool(_TEMPLATE_RE.fullmatch(value))
    elif field_name == "browser_platform":
        valid = value in {"windows", "macos", "android"}
    elif field_name == "timezone":
        valid = bool(_TIMEZONE_RE.fullmatch(value))
    elif field_name == "locale":
        valid = bool(_LOCALE_RE.fullmatch(value))
    elif field_name == "accept_language":
        valid = bool(_ACCEPT_LANGUAGE_RE.fullmatch(value))
    elif field_name == "proxy_region_snapshot":
        valid = bool(_REGION_RE.fullmatch(value))
    elif field_name == "browser_family":
        valid = value == "chromium"
    elif field_name == "browser_version":
        valid = bool(_VERSION_RE.fullmatch(value))
    elif field_name == "browser_source":
        valid = value in _BROWSER_SOURCES
    elif field_name == "provider_mode":
        valid = value in _LAUNCH_MODES
    elif field_name == "profile_key":
        valid = bool(_PROFILE_KEY_RE.fullmatch(value))
    elif field_name == "proxy_effect":
        valid = value in _EFFECT_PROOFS
    if not valid:
        fail(path)


def _reject_forbidden_recursive(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                _unsafe(path)
            normalized = key.strip().lower().replace("-", "_")
            if normalized in _FORBIDDEN_KEYS:
                _unsafe(f"{path}.{key}")
            _reject_forbidden_recursive(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_recursive(item, f"{path}.{index}")
    elif isinstance(value, str):
        if "\x00" in value or _URI_SCHEME_RE.match(value) or _ABSOLUTE_PATH_RE.match(value):
            _unsafe(path)
    elif value is not None and type(value) not in {bool, int, float}:
        _unsafe(path)


def _require_exact_keys(value: dict[str, Any], expected: set[str] | frozenset[str], path: str) -> None:
    if set(value) != set(expected):
        _unsafe(path)


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _unsafe(path)
    return value


def _safe_id(value: Any, path: str, *, provider_error: bool = False) -> None:
    if not isinstance(value, str) or not _SAFE_ID_RE.fullmatch(value):
        (_provider_unsupported if provider_error else _unsafe)(path)


def _safe_source(value: Any, path: str, *, provider_error: bool = False) -> None:
    if not isinstance(value, str) or not _SAFE_SOURCE_RE.fullmatch(value):
        (_provider_unsupported if provider_error else _unsafe)(path)


def _version(value: Any, path: str, *, provider_error: bool = False) -> None:
    if not isinstance(value, str) or not _VERSION_RE.fullmatch(value):
        (_provider_unsupported if provider_error else _unsafe)(path)


def _region(value: Any, path: str, *, provider_error: bool = False) -> None:
    if not isinstance(value, str) or not _REGION_RE.fullmatch(value):
        (_provider_unsupported if provider_error else _unsafe)(path)


def _positive_int(value: Any, path: str, *, provider_error: bool = False) -> int:
    if type(value) is not int or value <= 0:
        (_provider_unsupported if provider_error else _unsafe)(path)
    return value


def _positive_number(value: Any, path: str, *, provider_error: bool = False) -> float:
    if type(value) not in {int, float} or isinstance(value, bool) or float(value) <= 0:
        (_provider_unsupported if provider_error else _unsafe)(path)
    return float(value)


def _iso_datetime(value: Any, path: str) -> None:
    if not isinstance(value, str) or len(value) > 64:
        _unsafe(path)
    try:
        from datetime import datetime

        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _unsafe(path)
        return
    if parsed.tzinfo is None:
        _unsafe(path)


def _unsafe(path: str) -> None:
    raise BrowserEnvironmentError("account_identity_snapshot_unsafe", path)


def _provider_unsupported(path: str) -> None:
    raise BrowserEnvironmentError("account_identity_provider_unsupported", path)
