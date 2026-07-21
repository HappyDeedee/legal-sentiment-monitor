from __future__ import annotations

import hashlib
import json
import os
import re
import threading
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.browser_environment import (
    BrowserEnvironmentPlan,
    BrowserEnvironmentResult,
    validate_safe_runtime_snapshot,
)


REQUEST_ENVIRONMENT_CONTRACT_VERSION = 2
REQUEST_ENVIRONMENT_MAX_BYTES = 16384
REQUEST_RESULT_MAX_BYTES = 131072
REQUEST_DISPATCH_PROOF_LIMIT = 32
DEFAULT_REQUEST_ENVIRONMENT_TTL_SECONDS = 900
REQUEST_BINDING_ENV_NAME = "MONITOR_PLATFORM_REQUEST_BINDING"
REQUEST_RESULT_PATH_ENV_NAME = "MONITOR_PLATFORM_REQUEST_RESULT_PATH"

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_SAFE_PLATFORM_RE = re.compile(r"^[a-z0-9_]{1,32}$")
_PROFILE_KEY_RE = re.compile(r"^\d+/[a-z0-9_]+/acc_\d+$")
_REVISION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_DIGEST_RE = re.compile(r"^[a-f0-9]{64}$")
_BROWSER_FAMILY_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_BROWSER_CHANNEL_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_BROWSER_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+\-]{0,63}$")
_LOCALE_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{2,8})?$")
_TIMEZONE_RE = re.compile(r"^(?:UTC|[A-Za-z_+\-]+(?:/[A-Za-z0-9_+\-]+)+)$")
_ACCEPT_LANGUAGE_RE = re.compile(r"^[A-Za-z0-9,;=.\- ]{1,256}$")
_PROXY_POLICIES = frozenset({"account_bound", "direct"})
_FORBIDDEN_KEYS = frozenset(
    {
        "cookie",
        "cookies",
        "cookie_value",
        "cookie_values",
        "token",
        "tokens",
        "proxy_url",
        "proxy_password",
        "proxy_username",
        "proxy_credentials",
        "profile_path",
        "browser_executable_path",
        "executable_path",
        "cdp_url",
        "cdp_endpoint",
        "websocket_url",
        "signature",
        "signature_material",
        "headers",
        "environment",
        "argv",
    }
)


class PlatformRequestEnvironmentError(ValueError):
    def __init__(self, reason: str, *fields_: str):
        self.reason = reason
        self.fields = tuple(field for field in fields_ if field)
        suffix = f": {', '.join(self.fields)}" if self.fields else ""
        super().__init__(f"{reason}{suffix}")


@dataclass(frozen=True, slots=True)
class PlatformRequestBinding:
    contract_version: int
    workspace_id: int
    account_id: int
    platform: str
    profile_key: str
    resolution_id: str
    attempt_id: str
    run_id: int
    identity_revision: str
    cookie_material_revision: str
    proxy_revision: str
    created_at: str
    expires_at: str

    def __post_init__(self) -> None:
        _validate_binding(self)

    def to_safe_dict(self) -> dict[str, Any]:
        value = asdict(self)
        _reject_forbidden_recursive(value)
        return value

    def assert_request_binding(
        self,
        *,
        account_id: int,
        platform: str,
        profile_key: str,
        resolution_id: str,
        attempt_id: str,
    ) -> None:
        expected = {
            "account_id": self.account_id,
            "platform": self.platform,
            "profile_key": self.profile_key,
            "resolution_id": self.resolution_id,
            "attempt_id": self.attempt_id,
        }
        actual = {
            "account_id": account_id,
            "platform": platform,
            "profile_key": profile_key,
            "resolution_id": resolution_id,
            "attempt_id": attempt_id,
        }
        mismatches = [name for name, value in actual.items() if value != expected[name]]
        if mismatches:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_mismatch",
                *mismatches,
            )


@dataclass(frozen=True, slots=True)
class PlatformRequestEnvironment:
    contract_version: int
    workspace_id: int
    account_id: int
    platform: str
    profile_key: str
    browser_family: str
    browser_source: str
    browser_channel: str
    effective_browser_version: str
    browser_proof_digest: str
    proxy_policy: str
    proxy_id: int | None
    proxy_revision: str
    identity_revision: str
    resolution_id: str
    attempt_id: str
    run_id: int
    browser_platform: str
    locale: str
    timezone: str
    user_agent: str
    accept_language: str
    screen_width: int
    screen_height: int
    viewport_width: int
    viewport_height: int
    device_scale_factor: float
    is_mobile: bool
    has_touch: bool
    cookie_material_revision: str
    created_at: str
    expires_at: str
    fallback_used: bool

    def __post_init__(self) -> None:
        _validate_environment(self)

    def to_safe_dict(self) -> dict[str, Any]:
        value = asdict(self)
        _reject_forbidden_recursive(value)
        return value

    def assert_request_binding(
        self,
        *,
        account_id: int,
        platform: str,
        profile_key: str,
        resolution_id: str,
        attempt_id: str,
        proxy_revision: str,
        identity_revision: str,
        cookie_material_revision: str,
    ) -> None:
        expected = {
            "account_id": self.account_id,
            "platform": self.platform,
            "profile_key": self.profile_key,
            "resolution_id": self.resolution_id,
            "attempt_id": self.attempt_id,
            "proxy_revision": self.proxy_revision,
            "identity_revision": self.identity_revision,
            "cookie_material_revision": self.cookie_material_revision,
        }
        actual = {
            "account_id": account_id,
            "platform": platform,
            "profile_key": profile_key,
            "resolution_id": resolution_id,
            "attempt_id": attempt_id,
            "proxy_revision": proxy_revision,
            "identity_revision": identity_revision,
            "cookie_material_revision": cookie_material_revision,
        }
        mismatches = [name for name, value in actual.items() if value != expected[name]]
        if mismatches:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_mismatch",
                *mismatches,
            )

    def assert_active(self, *, now: datetime | None = None) -> None:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        created = _parse_datetime(self.created_at, "created_at")
        expires = _parse_datetime(self.expires_at, "expires_at")
        if created > current + timedelta(seconds=60):
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_invalid",
                "created_at",
            )
        if expires <= current:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_expired",
                "expires_at",
            )


_cached_binding: PlatformRequestBinding | None = None
_binding_cache_lock = threading.Lock()
_request_result_lock = threading.Lock()


def build_platform_request_binding(
    plan: BrowserEnvironmentPlan,
    *,
    run_id: int,
    identity_revision: str,
    cookie_material_revision: str,
    proxy_revision: str,
    created_at: str | None = None,
    expires_at: str | None = None,
    ttl_seconds: int = DEFAULT_REQUEST_ENVIRONMENT_TTL_SECONDS,
) -> PlatformRequestBinding:
    if not isinstance(plan, BrowserEnvironmentPlan):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "browser_plan",
        )
    if plan.action != "crawl":
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            "action",
        )
    created = _parse_datetime(
        created_at or datetime.now(timezone.utc).isoformat(),
        "created_at",
    )
    if expires_at is None:
        if type(ttl_seconds) is not int or ttl_seconds <= 0 or ttl_seconds > 86400:
            _invalid("ttl_seconds")
        expires = created + timedelta(seconds=ttl_seconds)
    else:
        expires = _parse_datetime(expires_at, "expires_at")
    if expires <= created:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_expired",
            "expires_at",
        )
    return PlatformRequestBinding(
        contract_version=REQUEST_ENVIRONMENT_CONTRACT_VERSION,
        workspace_id=plan.workspace_id,
        account_id=plan.account_id,
        platform=plan.platform,
        profile_key=plan.profile_key,
        resolution_id=plan.resolution_id,
        attempt_id=plan.attempt_id,
        run_id=run_id,
        identity_revision=identity_revision,
        cookie_material_revision=cookie_material_revision,
        proxy_revision=proxy_revision,
        created_at=created.isoformat(),
        expires_at=expires.isoformat(),
    )


def platform_request_binding_to_json(binding: PlatformRequestBinding) -> str:
    if not isinstance(binding, PlatformRequestBinding):
        _invalid("binding")
    payload = json.dumps(
        binding.to_safe_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if len(payload.encode("utf-8")) > REQUEST_ENVIRONMENT_MAX_BYTES:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            "binding_size",
        )
    return payload


def platform_request_binding_from_json(payload: str) -> PlatformRequestBinding:
    value = _parse_json_object(payload, "binding")
    expected = {field.name for field in fields(PlatformRequestBinding)}
    if set(value) != expected:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "binding_fields",
        )
    _reject_forbidden_recursive(value)
    try:
        return PlatformRequestBinding(**value)
    except PlatformRequestEnvironmentError:
        raise
    except (TypeError, ValueError) as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "binding",
        ) from exc


def request_binding_from_environment(
    *,
    required: bool = False,
) -> PlatformRequestBinding | None:
    global _cached_binding
    with _binding_cache_lock:
        if _cached_binding is not None:
            return _cached_binding
        payload = os.environ.pop(REQUEST_BINDING_ENV_NAME, "")
        if not payload:
            if required:
                raise PlatformRequestEnvironmentError(
                    "platform_request_environment_missing",
                    "binding",
                )
            return None
        _cached_binding = platform_request_binding_from_json(payload)
        return _cached_binding


def reset_platform_request_environment_cache_for_tests() -> None:
    global _cached_binding
    with _binding_cache_lock:
        _cached_binding = None


def build_platform_request_environment_from_binding(
    plan: BrowserEnvironmentPlan,
    result: BrowserEnvironmentResult,
    binding: PlatformRequestBinding,
) -> PlatformRequestEnvironment:
    if not isinstance(binding, PlatformRequestBinding):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "binding",
        )
    checks = {
        "workspace_id": (binding.workspace_id, plan.workspace_id),
        "account_id": (binding.account_id, plan.account_id),
        "platform": (binding.platform, plan.platform),
        "profile_key": (binding.profile_key, plan.profile_key),
        "resolution_id": (binding.resolution_id, plan.resolution_id),
        "attempt_id": (binding.attempt_id, plan.attempt_id),
    }
    mismatches = [name for name, (actual, expected) in checks.items() if actual != expected]
    if mismatches:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            *mismatches,
        )
    return build_platform_request_environment(
        plan,
        result,
        run_id=binding.run_id,
        identity_revision=binding.identity_revision,
        cookie_material_revision=binding.cookie_material_revision,
        proxy_revision=binding.proxy_revision,
        created_at=binding.created_at,
        expires_at=binding.expires_at,
    )


def establish_platform_request_environment(
    plan: BrowserEnvironmentPlan,
    result: BrowserEnvironmentResult,
) -> PlatformRequestEnvironment:
    binding = request_binding_from_environment(required=True)
    if binding is None:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "binding",
        )
    environment = build_platform_request_environment_from_binding(plan, result, binding)
    environment.assert_active()
    write_platform_request_environment(environment)
    return environment


def build_platform_request_environment(
    plan: BrowserEnvironmentPlan,
    result: BrowserEnvironmentResult,
    *,
    run_id: int,
    identity_revision: str,
    cookie_material_revision: str,
    proxy_revision: str | None = None,
    browser_channel: str | None = None,
    created_at: str | None = None,
    expires_at: str | None = None,
    ttl_seconds: int = DEFAULT_REQUEST_ENVIRONMENT_TTL_SECONDS,
) -> PlatformRequestEnvironment:
    if not isinstance(plan, BrowserEnvironmentPlan):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "browser_plan",
        )
    if not isinstance(result, BrowserEnvironmentResult):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "browser_result",
        )
    snapshot = validate_safe_runtime_snapshot(result.snapshot)
    _validate_provider_binding(plan, result, snapshot)

    created = _parse_datetime(created_at or snapshot["validated_at"], "created_at")
    if expires_at is None:
        if type(ttl_seconds) is not int or ttl_seconds <= 0 or ttl_seconds > 86400:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_invalid",
                "ttl_seconds",
            )
        expires = created + timedelta(seconds=ttl_seconds)
    else:
        expires = _parse_datetime(expires_at, "expires_at")
    if expires <= created:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_expired",
            "expires_at",
        )

    safe_snapshot = _browser_proof_payload(snapshot)
    browser_proof_digest = _digest(safe_snapshot)
    resolved_proxy_revision = proxy_revision or _digest(
        {
            "policy": snapshot["proxy"]["policy"],
            "proxy_id": snapshot["proxy"]["proxy_id"],
            "region": snapshot["proxy"]["region"],
            "effect_proof": snapshot["proxy"]["effect_proof"],
        },
        prefix="proxy-",
    )
    resolved_browser_channel = browser_channel or _browser_channel(plan, snapshot)

    return PlatformRequestEnvironment(
        contract_version=REQUEST_ENVIRONMENT_CONTRACT_VERSION,
        workspace_id=plan.workspace_id,
        account_id=plan.account_id,
        platform=plan.platform,
        profile_key=plan.profile_key,
        browser_family=str(snapshot["browser"]["family"]),
        browser_source=str(snapshot["browser"]["source"]),
        browser_channel=resolved_browser_channel,
        effective_browser_version=str(snapshot["browser"]["version"]),
        browser_proof_digest=browser_proof_digest,
        proxy_policy=str(snapshot["proxy"]["policy"]),
        proxy_id=snapshot["proxy"]["proxy_id"],
        proxy_revision=resolved_proxy_revision,
        identity_revision=identity_revision,
        resolution_id=plan.resolution_id,
        attempt_id=plan.attempt_id,
        run_id=run_id,
        browser_platform=plan.browser_platform,
        locale=str(snapshot["effective"]["locale"]),
        timezone=str(snapshot["effective"]["timezone"]),
        user_agent=str(snapshot["effective"]["user_agent"]),
        accept_language=str(snapshot["effective"]["accept_language"]),
        screen_width=int(snapshot["effective"]["screen_width"]),
        screen_height=int(snapshot["effective"]["screen_height"]),
        viewport_width=int(snapshot["effective"]["viewport_width"]),
        viewport_height=int(snapshot["effective"]["viewport_height"]),
        device_scale_factor=float(snapshot["effective"]["device_scale_factor"]),
        is_mobile=bool(snapshot["effective"]["is_mobile"]),
        has_touch=bool(snapshot["effective"]["has_touch"]),
        cookie_material_revision=cookie_material_revision,
        created_at=created.isoformat(),
        expires_at=expires.isoformat(),
        fallback_used=False,
    )


def platform_request_environment_to_json(
    environment: PlatformRequestEnvironment,
) -> str:
    if not isinstance(environment, PlatformRequestEnvironment):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "environment",
        )
    payload = json.dumps(
        environment.to_safe_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if len(payload.encode("utf-8")) > REQUEST_ENVIRONMENT_MAX_BYTES:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            "environment_size",
        )
    return payload


def platform_request_environment_from_json(payload: str) -> PlatformRequestEnvironment:
    value = _parse_json_object(payload, "environment")
    expected = {field.name for field in fields(PlatformRequestEnvironment)}
    if set(value) != expected:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "environment_fields",
        )
    _reject_forbidden_recursive(value)
    try:
        return PlatformRequestEnvironment(**value)
    except PlatformRequestEnvironmentError:
        raise
    except (TypeError, ValueError) as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "environment",
        ) from exc


def write_platform_request_environment(
    environment: PlatformRequestEnvironment,
) -> None:
    destination_value = os.environ.get(REQUEST_RESULT_PATH_ENV_NAME, "")
    if not destination_value:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "result_path",
        )
    destination = Path(destination_value).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = platform_request_environment_to_json(environment)
    _write_atomic(destination, payload)


def append_platform_request_dispatch_proof(
    environment: PlatformRequestEnvironment,
    proof: dict[str, Any],
) -> None:
    destination_value = os.environ.get(REQUEST_RESULT_PATH_ENV_NAME, "")
    if not destination_value:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "result_path",
        )
    destination = Path(destination_value).resolve()
    with _request_result_lock:
        stored_environment, stored_proofs = read_platform_request_result(destination)
        if stored_environment != environment:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_mismatch",
                "dispatch_environment",
            )
        validated = _validate_dispatch_proof(proof, environment)
        if stored_proofs and validated["request_index"] <= stored_proofs[-1]["request_index"]:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_mismatch",
                "request_index",
            )
        next_proofs = [*stored_proofs, validated]
        if len(next_proofs) > REQUEST_DISPATCH_PROOF_LIMIT:
            next_proofs = [next_proofs[0], *next_proofs[-(REQUEST_DISPATCH_PROOF_LIMIT - 1):]]
        payload = json.dumps(
            {
                "environment": environment.to_safe_dict(),
                "dispatch_proofs": next_proofs,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        if len(payload.encode("utf-8")) > REQUEST_RESULT_MAX_BYTES:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_unsafe",
                "result_size",
            )
        _write_atomic(destination, payload)


def read_platform_request_result(
    path: Path,
) -> tuple[PlatformRequestEnvironment, list[dict[str, Any]]]:
    destination = Path(path).resolve()
    try:
        payload = destination.read_text(encoding="utf-8")
    except OSError as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_missing",
            "result",
        ) from exc
    if len(payload.encode("utf-8")) > REQUEST_RESULT_MAX_BYTES:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            "result_size",
        )
    try:
        value = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            "result",
        ) from exc
    if not isinstance(value, dict):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            "result",
        )
    if set(value) == {"environment", "dispatch_proofs"}:
        environment = platform_request_environment_from_json(
            json.dumps(value["environment"], ensure_ascii=False)
        )
        raw_proofs = value["dispatch_proofs"]
        if not isinstance(raw_proofs, list) or len(raw_proofs) > REQUEST_DISPATCH_PROOF_LIMIT:
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_unsafe",
                "dispatch_proofs",
            )
        proofs = [_validate_dispatch_proof(item, environment) for item in raw_proofs]
        indexes = [item["request_index"] for item in proofs]
        if indexes != sorted(set(indexes)):
            raise PlatformRequestEnvironmentError(
                "platform_request_environment_mismatch",
                "request_index",
            )
        return environment, proofs
    return platform_request_environment_from_json(payload), []


def read_platform_request_environment(path: Path) -> PlatformRequestEnvironment:
    environment, _ = read_platform_request_result(path)
    return environment


def _write_atomic(destination: Path, payload: str) -> None:
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def _validate_dispatch_proof(
    proof: Any,
    environment: PlatformRequestEnvironment,
) -> dict[str, Any]:
    expected_fields = {
        "contract_version",
        "workspace_id",
        "account_id",
        "platform",
        "profile_key",
        "resolution_id",
        "attempt_id",
        "run_id",
        "identity_revision",
        "cookie_material_revision",
        "proxy_revision",
        "cookie_digest",
        "user_agent_digest",
        "client_hints_digest",
        "proxy_digest",
        "request_index",
        "method",
        "target_digest",
        "body_digest",
        "request_header_digest",
        "signer_input_digest",
        "signer_output_digest",
        "signed",
        "response_status",
        "dispatched_at",
    }
    if not isinstance(proof, dict) or set(proof) != expected_fields:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            "dispatch_proof_fields",
        )
    _reject_forbidden_recursive(proof, "dispatch_proof")
    binding_fields = (
        "contract_version",
        "workspace_id",
        "account_id",
        "platform",
        "profile_key",
        "resolution_id",
        "attempt_id",
        "run_id",
        "identity_revision",
        "cookie_material_revision",
        "proxy_revision",
    )
    mismatches = [
        name for name in binding_fields if proof.get(name) != getattr(environment, name)
    ]
    if mismatches:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            *mismatches,
        )
    for name in (
        "cookie_digest",
        "user_agent_digest",
        "client_hints_digest",
        "proxy_digest",
        "target_digest",
        "body_digest",
        "request_header_digest",
        "signer_input_digest",
        "signer_output_digest",
    ):
        if not _DIGEST_RE.fullmatch(str(proof.get(name) or "")):
            _invalid(name)
    if type(proof["request_index"]) is not int or not 1 <= proof["request_index"] <= 10000:
        _invalid("request_index")
    if proof["method"] not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        _invalid("method")
    if type(proof["signed"]) is not bool:
        _invalid("signed")
    if type(proof["response_status"]) is not int or not 100 <= proof["response_status"] <= 599:
        _invalid("response_status")
    dispatched = _parse_datetime(str(proof["dispatched_at"]), "dispatched_at")
    created = _parse_datetime(environment.created_at, "created_at")
    expires = _parse_datetime(environment.expires_at, "expires_at")
    if dispatched < created - timedelta(seconds=1) or dispatched > expires:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            "dispatched_at",
        )
    return dict(proof)


def _validate_provider_binding(
    plan: BrowserEnvironmentPlan,
    result: BrowserEnvironmentResult,
    snapshot: dict[str, Any],
) -> None:
    if not result.ok or not snapshot["ok"]:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_provider_failed",
            "browser_result",
        )
    if snapshot["fallback_used"]:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_fallback",
            "fallback_used",
        )
    if plan.action != "crawl" or snapshot["action"] != "crawl":
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            "action",
        )
    checks = {
        "workspace_id": (snapshot["account"]["workspace_id"], plan.workspace_id),
        "account_id": (snapshot["account"]["account_id"], plan.account_id),
        "platform": (snapshot["account"]["platform"], plan.platform),
        "profile_key": (snapshot["profile"]["profile_key"], plan.profile_key),
        "resolution_id": (snapshot["resolution_id"], plan.resolution_id),
        "attempt_id": (snapshot["attempt_id"], plan.attempt_id),
        "browser_family": (snapshot["browser"]["family"], plan.browser_family),
        "browser_source": (snapshot["browser"]["source"], plan.browser_source),
        "proxy_policy": (snapshot["proxy"]["policy"], plan.proxy_policy),
        "proxy_id": (snapshot["proxy"]["proxy_id"], plan.proxy_id),
        "proxy_region": (snapshot["proxy"]["region"], plan.proxy_region),
        "user_agent": (snapshot["effective"]["user_agent"], plan.user_agent),
        "timezone": (snapshot["effective"]["timezone"], plan.timezone),
        "locale": (snapshot["effective"]["locale"], plan.locale),
        "accept_language": (
            snapshot["effective"]["accept_language"],
            plan.accept_language,
        ),
    }
    mismatches = [name for name, (actual, expected) in checks.items() if actual != expected]
    if mismatches:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_mismatch",
            *mismatches,
        )
    if plan.proxy_policy == "account_bound" and snapshot["proxy"]["effect_proof"] != "passed":
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_proxy_unverified",
            "proxy_effect",
        )
    if plan.proxy_policy == "direct" and snapshot["proxy"]["effect_proof"] != "not_applicable":
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_proxy_unverified",
            "proxy_effect",
        )


def _validate_environment(environment: PlatformRequestEnvironment) -> None:
    if environment.contract_version != REQUEST_ENVIRONMENT_CONTRACT_VERSION:
        _invalid("contract_version")
    _positive_int(environment.workspace_id, "workspace_id")
    _positive_int(environment.account_id, "account_id")
    _positive_int(environment.run_id, "run_id")
    if not _SAFE_PLATFORM_RE.fullmatch(environment.platform):
        _invalid("platform")
    if not _PROFILE_KEY_RE.fullmatch(environment.profile_key):
        _invalid("profile_key")
    if not _BROWSER_FAMILY_RE.fullmatch(environment.browser_family):
        _invalid("browser_family")
    if not _SAFE_ID_RE.fullmatch(environment.browser_source):
        _invalid("browser_source")
    if not _BROWSER_CHANNEL_RE.fullmatch(environment.browser_channel):
        _invalid("browser_channel")
    if not _BROWSER_VERSION_RE.fullmatch(environment.effective_browser_version):
        _invalid("effective_browser_version")
    if not _DIGEST_RE.fullmatch(environment.browser_proof_digest):
        _invalid("browser_proof_digest")
    if environment.proxy_policy not in _PROXY_POLICIES:
        _invalid("proxy_policy")
    if environment.proxy_policy == "account_bound":
        _positive_int(environment.proxy_id, "proxy_id")
    elif environment.proxy_id is not None:
        _invalid("proxy_id")
    for name in (
        "proxy_revision",
        "identity_revision",
        "resolution_id",
        "attempt_id",
        "cookie_material_revision",
    ):
        if not _REVISION_RE.fullmatch(str(getattr(environment, name))):
            _invalid(name)
    if not _SAFE_ID_RE.fullmatch(environment.browser_platform):
        _invalid("browser_platform")
    if not _LOCALE_RE.fullmatch(environment.locale):
        _invalid("locale")
    if not _TIMEZONE_RE.fullmatch(environment.timezone):
        _invalid("timezone")
    if not isinstance(environment.user_agent, str) or not environment.user_agent or len(environment.user_agent) > 512:
        _invalid("user_agent")
    if not _ACCEPT_LANGUAGE_RE.fullmatch(environment.accept_language):
        _invalid("accept_language")
    for name in ("screen_width", "screen_height", "viewport_width", "viewport_height"):
        _positive_int(getattr(environment, name), name)
    if environment.viewport_width > environment.screen_width:
        _invalid("viewport_width")
    if environment.viewport_height > environment.screen_height:
        _invalid("viewport_height")
    if (
        isinstance(environment.device_scale_factor, bool)
        or not isinstance(environment.device_scale_factor, (int, float))
        or environment.device_scale_factor <= 0
    ):
        _invalid("device_scale_factor")
    if type(environment.is_mobile) is not bool:
        _invalid("is_mobile")
    if type(environment.has_touch) is not bool:
        _invalid("has_touch")
    if environment.fallback_used is not False:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_fallback",
            "fallback_used",
        )
    created = _parse_datetime(environment.created_at, "created_at")
    expires = _parse_datetime(environment.expires_at, "expires_at")
    if expires <= created:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_expired",
            "expires_at",
        )
    _reject_forbidden_recursive(asdict(environment))


def _validate_binding(binding: PlatformRequestBinding) -> None:
    if binding.contract_version != REQUEST_ENVIRONMENT_CONTRACT_VERSION:
        _invalid("contract_version")
    _positive_int(binding.workspace_id, "workspace_id")
    _positive_int(binding.account_id, "account_id")
    _positive_int(binding.run_id, "run_id")
    if not _SAFE_PLATFORM_RE.fullmatch(binding.platform):
        _invalid("platform")
    if not _PROFILE_KEY_RE.fullmatch(binding.profile_key):
        _invalid("profile_key")
    for name in (
        "resolution_id",
        "attempt_id",
        "identity_revision",
        "cookie_material_revision",
        "proxy_revision",
    ):
        if not _REVISION_RE.fullmatch(str(getattr(binding, name))):
            _invalid(name)
    created = _parse_datetime(binding.created_at, "created_at")
    expires = _parse_datetime(binding.expires_at, "expires_at")
    if expires <= created:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_expired",
            "expires_at",
        )
    _reject_forbidden_recursive(asdict(binding))


def _browser_proof_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": snapshot["contract_version"],
        "resolution_id": snapshot["resolution_id"],
        "attempt_id": snapshot["attempt_id"],
        "account": snapshot["account"],
        "browser": snapshot["browser"],
        "profile": snapshot["profile"],
        "proxy": snapshot["proxy"],
        "effective": snapshot["effective"],
        "provider": snapshot["provider"],
        "fallback_used": snapshot["fallback_used"],
        "validated_at": snapshot["validated_at"],
    }


def _browser_channel(
    plan: BrowserEnvironmentPlan,
    snapshot: dict[str, Any],
) -> str:
    source = str(snapshot["browser"]["source"])
    if source == "system_edge":
        return "edge"
    if source == "system_chrome":
        return "chrome"
    if source in {"playwright_bundled", "system_chromium"}:
        return "chromium"
    if source in {"explicit", "system_managed"}:
        executable = str(plan.browser_executable_path).lower().replace("/", "\\")
        if "msedge" in executable or "\\microsoft edge" in executable or "\\microsoft\\edge" in executable:
            return "edge"
        if "chromium" in executable:
            return "chromium"
        if "chrome" in executable:
            return "chrome"
        return "managed"
    return str(plan.provider_name or "playwright")


def _digest(value: Any, *, prefix: str = "") -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"{prefix}{digest}" if prefix else digest


def _parse_json_object(payload: str, field_name: str) -> dict[str, Any]:
    if (
        not isinstance(payload, str)
        or not payload
        or len(payload.encode("utf-8")) > REQUEST_ENVIRONMENT_MAX_BYTES
    ):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            field_name,
        )
    try:
        value = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            field_name,
        ) from exc
    if not isinstance(value, dict):
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_unsafe",
            field_name,
        )
    return value


def _parse_datetime(value: str, field_name: str) -> datetime:
    if not isinstance(value, str) or not value or len(value) > 64:
        _invalid(field_name)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PlatformRequestEnvironmentError(
            "platform_request_environment_invalid",
            field_name,
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _positive_int(value: Any, field_name: str) -> None:
    if type(value) is not int or value <= 0:
        _invalid(field_name)


def _reject_forbidden_recursive(value: Any, path: str = "environment") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in _FORBIDDEN_KEYS:
                raise PlatformRequestEnvironmentError(
                    "platform_request_environment_unsafe",
                    f"{path}.{key}",
                )
            _reject_forbidden_recursive(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_forbidden_recursive(item, f"{path}.{index}")


def _invalid(field_name: str) -> None:
    raise PlatformRequestEnvironmentError(
        "platform_request_environment_invalid",
        field_name,
    )
