from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
from types import MappingProxyType
from typing import Any, Mapping

from .security import load_or_create_secret_key


IDENTITY_GENERATOR_NAME = "mediacrawler_account_identity"
IDENTITY_GENERATOR_VERSION = "1.1"
IDENTITY_ENVIRONMENT_VERSION = "v2"
IDENTITY_SEED_DOMAIN = b"MediaCrawler/account-identity/seed/v1"

IDENTITY_STATE_DRAFT = "draft"
IDENTITY_STATE_GENERATED = "generated"
IDENTITY_STATE_VALIDATED = "validated"
IDENTITY_STATE_LOGIN_IN_PROGRESS = "login_in_progress"
IDENTITY_STATE_LOCKED = "locked"
IDENTITY_STATE_ACTIVE = "active"
IDENTITY_STATE_REQUIRES_RELOGIN = "requires_relogin"
IDENTITY_STATE_RESETTING = "resetting"
IDENTITY_STATES = frozenset(
    {
        IDENTITY_STATE_DRAFT,
        IDENTITY_STATE_GENERATED,
        IDENTITY_STATE_VALIDATED,
        IDENTITY_STATE_LOGIN_IN_PROGRESS,
        IDENTITY_STATE_LOCKED,
        IDENTITY_STATE_ACTIVE,
        IDENTITY_STATE_REQUIRES_RELOGIN,
        IDENTITY_STATE_RESETTING,
    }
)
IDENTITY_LOCKED_STATES = frozenset({IDENTITY_STATE_LOCKED, IDENTITY_STATE_ACTIVE})
IDENTITY_PRELOGIN_STATES = frozenset(
    {IDENTITY_STATE_DRAFT, IDENTITY_STATE_GENERATED, IDENTITY_STATE_VALIDATED}
)

TEMPLATE_FAMILY_AUTO = "auto"
TEMPLATE_FAMILIES = {
    TEMPLATE_FAMILY_AUTO,
    "windows_chrome_desktop",
    "mac_chrome_desktop",
    "android_chrome",
}

_WINDOWS_CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.6533.17 Safari/537.36"
)


def _template(**values: Any) -> Mapping[str, Any]:
    return MappingProxyType(values)


IDENTITY_TEMPLATE_CATALOG: tuple[Mapping[str, Any], ...] = (
    _template(
        identity_template="CN_WIN_CHROME_1920",
        region="CN_MAINLAND",
        family="windows_chrome_desktop",
        browser_platform="windows",
        user_agent=_WINDOWS_CHROME_UA,
        screen_width=1920,
        screen_height=1080,
        viewport_width=1920,
        viewport_height=963,
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        timezone="Asia/Shanghai",
        locale="zh-CN",
        accept_language="zh-CN",
    ),
    _template(
        identity_template="CN_WIN_CHROME_1536",
        region="CN_MAINLAND",
        family="windows_chrome_desktop",
        browser_platform="windows",
        user_agent=_WINDOWS_CHROME_UA,
        screen_width=1536,
        screen_height=864,
        viewport_width=1536,
        viewport_height=768,
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        timezone="Asia/Shanghai",
        locale="zh-CN",
        accept_language="zh-CN",
    ),
    _template(
        identity_template="CN_MAC_CHROME_1440",
        region="CN_MAINLAND",
        family="mac_chrome_desktop",
        browser_platform="macos",
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/127.0.6533.17 Safari/537.36"
        ),
        screen_width=1440,
        screen_height=900,
        viewport_width=1440,
        viewport_height=789,
        device_scale_factor=2,
        is_mobile=False,
        has_touch=False,
        timezone="Asia/Shanghai",
        locale="zh-CN",
        accept_language="zh-CN",
    ),
    _template(
        identity_template="CN_ANDROID_CHROME",
        region="CN_MAINLAND",
        family="android_chrome",
        browser_platform="android",
        user_agent=(
            "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/127.0.6533.17 Mobile Safari/537.36"
        ),
        screen_width=1080,
        screen_height=2400,
        viewport_width=412,
        viewport_height=915,
        device_scale_factor=2.625,
        is_mobile=True,
        has_touch=True,
        timezone="Asia/Shanghai",
        locale="zh-CN",
        accept_language="zh-CN",
    ),
    _template(
        identity_template="HK_DESKTOP_CHROME",
        region="HK",
        family="windows_chrome_desktop",
        browser_platform="windows",
        user_agent=_WINDOWS_CHROME_UA,
        screen_width=1920,
        screen_height=1080,
        viewport_width=1920,
        viewport_height=963,
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        timezone="Asia/Hong_Kong",
        locale="zh-HK",
        accept_language="zh-HK",
    ),
    _template(
        identity_template="SG_DESKTOP_CHROME",
        region="SG",
        family="windows_chrome_desktop",
        browser_platform="windows",
        user_agent=_WINDOWS_CHROME_UA,
        screen_width=1440,
        screen_height=900,
        viewport_width=1440,
        viewport_height=789,
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
        timezone="Asia/Singapore",
        locale="en-SG",
        accept_language="en-SG",
    ),
)

IDENTITY_TEMPLATE_BY_NAME = MappingProxyType(
    {str(item["identity_template"]): item for item in IDENTITY_TEMPLATE_CATALOG}
)


def identity_template_family(identity_template: Any) -> str:
    template = IDENTITY_TEMPLATE_BY_NAME.get(str(identity_template or ""))
    return str(template["family"]) if template else TEMPLATE_FAMILY_AUTO

GENERATOR_OWNED_FIELDS = (
    "environment_region",
    "browser_platform",
    "identity_template",
    "fingerprint_seed",
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
    "identity_generator_name",
    "identity_generator_version",
    "identity_environment_version",
    "proxy_region_snapshot",
)

_CATALOG_IDENTITY_FIELDS = (
    "browser_platform",
    "user_agent",
    "screen_width",
    "screen_height",
    "viewport_width",
    "viewport_height",
    "device_scale_factor",
    "is_mobile",
    "has_touch",
    "timezone",
    "locale",
    "accept_language",
)


class AccountIdentityError(ValueError):
    def __init__(self, reason: str, *fields: str):
        self.reason = reason
        self.fields = tuple(field for field in fields if field)
        suffix = f": {', '.join(self.fields)}" if self.fields else ""
        super().__init__(f"{reason}{suffix}")


def resolve_account_identity_seed_salt(seed_salt: bytes | str | None = None) -> bytes:
    if seed_salt is not None:
        resolved = seed_salt.encode("utf-8") if isinstance(seed_salt, str) else bytes(seed_salt)
    else:
        configured = os.environ.get("MONITOR_ACCOUNT_IDENTITY_SEED_SALT")
        if configured:
            resolved = configured.encode("utf-8")
        else:
            try:
                deployment_key = base64.urlsafe_b64decode(load_or_create_secret_key())
            except (ValueError, TypeError) as exc:
                raise AccountIdentityError("account_identity_missing", "seed_salt") from exc
            if len(deployment_key) != 32:
                raise AccountIdentityError("account_identity_missing", "seed_salt")
            resolved = hmac.new(deployment_key, IDENTITY_SEED_DOMAIN, hashlib.sha256).digest()
    if not resolved:
        raise AccountIdentityError("account_identity_missing", "seed_salt")
    return resolved


def generate_account_identity(
    *,
    workspace_id: int,
    platform: str,
    account_id: int,
    proxy_region_snapshot: str = "CN_MAINLAND",
    template_family: str = TEMPLATE_FAMILY_AUTO,
    seed_salt: bytes | str | None = None,
) -> dict[str, Any]:
    workspace = _positive_int(workspace_id, "workspace_id")
    account = _positive_int(account_id, "account_id")
    platform_value = _canonical_component(platform, "platform", lower=True)
    region = _canonical_component(proxy_region_snapshot or "CN_MAINLAND", "proxy_region_snapshot").upper()
    family = _canonical_component(template_family or TEMPLATE_FAMILY_AUTO, "identity_template_family", lower=True)
    if family not in TEMPLATE_FAMILIES:
        raise AccountIdentityError("account_identity_contradiction", "identity_template_family")

    candidates = [item for item in IDENTITY_TEMPLATE_CATALOG if item["region"] == region]
    if family != TEMPLATE_FAMILY_AUTO:
        candidates = [item for item in candidates if item["family"] == family]
    if not candidates:
        raise AccountIdentityError(
            "account_identity_contradiction",
            "proxy_region_snapshot",
            "identity_template_family",
        )

    salt = resolve_account_identity_seed_salt(seed_salt)
    selection_input = f"{workspace}|{platform_value}|{account}|{region}|{family}".encode("utf-8")
    selection_seed = hmac.new(salt, selection_input, hashlib.sha256).hexdigest()[:32]
    selected = candidates[int(selection_seed[:8], 16) % len(candidates)]
    template_name = str(selected["identity_template"])
    identity_input = f"{workspace}|{platform_value}|{account}|{region}|{template_name}".encode("utf-8")
    fingerprint_seed = hmac.new(salt, identity_input, hashlib.sha256).hexdigest()[:32]

    generated = {field: selected[field] for field in _CATALOG_IDENTITY_FIELDS}
    generated.update(
        {
            "environment_region": region,
            "identity_template": template_name,
            "fingerprint_seed": fingerprint_seed,
            "identity_generator_name": IDENTITY_GENERATOR_NAME,
            "identity_generator_version": IDENTITY_GENERATOR_VERSION,
            "identity_environment_version": IDENTITY_ENVIRONMENT_VERSION,
            "proxy_region_snapshot": region,
        }
    )
    return generated


def validate_account_identity(
    account: Mapping[str, Any],
    *,
    bound_proxy_exists: bool | None = None,
    task_proxy_id: int | None = None,
    seed_salt: bytes | str | None = None,
) -> dict[str, Any]:
    value = dict(account)
    if value.get("requires_relogin"):
        raise AccountIdentityError("account_identity_requires_relogin", "identity_state")

    missing = [field for field in GENERATOR_OWNED_FIELDS if _is_missing(value.get(field))]
    if missing:
        raise AccountIdentityError("account_identity_missing", *missing)

    state = str(value.get("identity_state") or "")
    if state in {"locked", "active"} and task_proxy_id is not None:
        raise AccountIdentityError("account_identity_locked_proxy_override", "proxy_id")
    if value.get("proxy_id") not in (None, "", 0) and bound_proxy_exists is not True:
        raise AccountIdentityError("account_identity_missing", "proxy_id")
    if value.get("identity_generator_name") != IDENTITY_GENERATOR_NAME:
        raise AccountIdentityError("account_identity_contradiction", "identity_generator_name")
    stale_version_fields = tuple(
        field
        for field, expected in (
            ("identity_generator_version", IDENTITY_GENERATOR_VERSION),
            ("identity_environment_version", IDENTITY_ENVIRONMENT_VERSION),
        )
        if value.get(field) != expected
    )
    if stale_version_fields:
        raise AccountIdentityError("account_identity_requires_relogin", *stale_version_fields)

    template_name = str(value.get("identity_template") or "")
    template = IDENTITY_TEMPLATE_BY_NAME.get(template_name)
    if template is None:
        raise AccountIdentityError("account_identity_contradiction", "identity_template")

    contradictions: list[str] = []
    region = str(value.get("proxy_region_snapshot") or "")
    if region != template["region"] or value.get("environment_region") != region:
        contradictions.extend(("environment_region", "proxy_region_snapshot"))
    for field in _CATALOG_IDENTITY_FIELDS:
        if value.get(field) != template[field]:
            contradictions.append(field)
    if not re.fullmatch(r"[0-9a-f]{32}", str(value.get("fingerprint_seed") or "")):
        contradictions.append("fingerprint_seed")
    context_missing = [field for field in ("id", "workspace_id", "platform") if _is_missing(value.get(field))]
    if context_missing:
        raise AccountIdentityError("account_identity_missing", *context_missing)
    workspace_id = _positive_int(value.get("workspace_id"), "workspace_id")
    account_id = _positive_int(value.get("id"), "id")
    platform = _canonical_component(value.get("platform"), "platform", lower=True)
    expected_seed = hmac.new(
        resolve_account_identity_seed_salt(seed_salt),
        f"{workspace_id}|{platform}|{account_id}|{region}|{template_name}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:32]
    if value.get("fingerprint_seed") != expected_seed:
        contradictions.append("fingerprint_seed")
    if _positive_number(value.get("device_scale_factor")) is None:
        contradictions.append("device_scale_factor")
    if _positive_int_or_none(value.get("viewport_width")) is None or _positive_int_or_none(value.get("viewport_height")) is None:
        contradictions.extend(("viewport_width", "viewport_height"))
    if int(value.get("viewport_width") or 0) > int(value.get("screen_width") or 0):
        contradictions.append("viewport_width")
    if int(value.get("viewport_height") or 0) > int(value.get("screen_height") or 0):
        contradictions.append("viewport_height")
    if contradictions:
        raise AccountIdentityError("account_identity_contradiction", *dict.fromkeys(contradictions))
    return value


def _canonical_component(value: Any, field: str, *, lower: bool = False) -> str:
    result = str(value or "").strip()
    if not result or "|" in result or "\n" in result or "\r" in result:
        raise AccountIdentityError("account_identity_contradiction", field)
    return result.lower() if lower else result


def _positive_int(value: Any, field: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise AccountIdentityError("account_identity_contradiction", field) from exc
    if result <= 0:
        raise AccountIdentityError("account_identity_contradiction", field)
    return result


def _positive_int_or_none(value: Any) -> int | None:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _positive_number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result > 0 else None


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())
