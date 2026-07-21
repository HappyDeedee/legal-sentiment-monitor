from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from tools.platform_request_environment import (
    PlatformRequestBinding,
    request_binding_from_environment,
)


CRAWLER_ATTEMPT_RESULT_ENV_NAME = "MONITOR_CRAWLER_ATTEMPT_RESULT_PATH"
CRAWLER_RETRY_ORDINAL_ENV_NAME = "MONITOR_CRAWLER_RETRY_ORDINAL"
CRAWLER_ATTEMPT_RESULT_CONTRACT_VERSION = 1
CRAWLER_ATTEMPT_RESULT_MAX_BYTES = 16384
CRAWLER_ATTEMPT_FAILURE_EXIT_CODE = 43

CRAWLER_FAILURE_CATEGORIES = frozenset(
    {
        "login_required",
        "second_verification",
        "captcha_or_human_verification",
        "rate_limited",
        "proxy_or_ip_blocked",
        "signature_mismatch",
        "cookie_invalid",
        "browser_environment_mismatch",
        "account_identity_mismatch",
        "transient_network",
        "platform_protocol_changed",
        "timeout",
        "cancelled",
        "process_crashed",
    }
)
_TERMINAL_STATUSES = frozenset(
    {"success", "failed", "timeout", "cancelled", "process_crashed"}
)
_SAFE_REASON_RE = re.compile(r"^[a-z][a-z0-9_]{0,95}$")


class CrawlerAttemptResultError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CrawlerFailureClassification:
    category: str
    reason_code: str

    def __post_init__(self) -> None:
        _validate_category(self.category)
        _validate_reason_code(self.reason_code)


class CrawlerAttemptFailure(RuntimeError):
    def __init__(
        self,
        category: str,
        reason_code: str,
        *,
        result: CrawlerAttemptResult | None = None,
    ) -> None:
        _validate_category(category)
        _validate_reason_code(reason_code)
        self.category = category
        self.reason_code = reason_code
        self.result = result
        super().__init__(f"crawler_attempt_failed:{category}:{reason_code}")

    @property
    def retryable(self) -> bool:
        return is_retryable_crawler_category(self.category)


@dataclass(frozen=True, slots=True)
class CrawlerAttemptResult:
    contract_version: int
    status: str
    category: str
    reason_code: str
    retryable: bool
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
    retry_ordinal: int
    recorded_at: str

    def __post_init__(self) -> None:
        if self.contract_version != CRAWLER_ATTEMPT_RESULT_CONTRACT_VERSION:
            raise CrawlerAttemptResultError("crawler attempt result version mismatch")
        if self.status not in _TERMINAL_STATUSES:
            raise CrawlerAttemptResultError("crawler attempt result status invalid")
        if self.status == "success":
            if self.category or self.retryable:
                raise CrawlerAttemptResultError("crawler attempt success result invalid")
        else:
            _validate_category(self.category)
            expected_status = _status_for_category(self.category)
            if self.status != expected_status:
                raise CrawlerAttemptResultError("crawler attempt result status mismatch")
            if self.retryable != is_retryable_crawler_category(self.category):
                raise CrawlerAttemptResultError("crawler attempt retry policy mismatch")
        _validate_reason_code(self.reason_code)
        if type(self.retry_ordinal) is not int or not 1 <= self.retry_ordinal <= 100:
            raise CrawlerAttemptResultError("crawler attempt retry ordinal invalid")
        _parse_datetime(self.recorded_at, "recorded_at")
        if type(self.workspace_id) is not int or self.workspace_id <= 0:
            raise CrawlerAttemptResultError("crawler attempt workspace binding invalid")
        if type(self.account_id) is not int or self.account_id <= 0:
            raise CrawlerAttemptResultError("crawler attempt account binding invalid")
        if type(self.run_id) is not int or self.run_id <= 0:
            raise CrawlerAttemptResultError("crawler attempt run binding invalid")
        for name in (
            "platform",
            "profile_key",
            "resolution_id",
            "attempt_id",
            "identity_revision",
            "cookie_material_revision",
            "proxy_revision",
        ):
            value = str(getattr(self, name) or "")
            if not value or len(value) > 256:
                raise CrawlerAttemptResultError(
                    f"crawler attempt {name} binding invalid"
                )

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


def is_retryable_crawler_category(category: str) -> bool:
    return category == "transient_network"


def classify_crawler_exception(exc: BaseException) -> CrawlerFailureClassification:
    if isinstance(exc, CrawlerAttemptFailure):
        return CrawlerFailureClassification(exc.category, exc.reason_code)
    if isinstance(exc, asyncio.CancelledError):
        return CrawlerFailureClassification("cancelled", "asyncio_cancelled")

    class_name = type(exc).__name__
    module_name = type(exc).__module__
    message = str(exc).lower()
    reason = str(getattr(exc, "reason", "") or "").lower()

    if class_name == "ProfileLoginRequired":
        return CrawlerFailureClassification("login_required", "profile_login_required")
    if class_name == "AccountIdentityError" or reason.startswith("account_identity_"):
        return CrawlerFailureClassification(
            "account_identity_mismatch",
            "account_identity_mismatch",
        )
    if class_name == "BrowserEnvironmentError":
        return CrawlerFailureClassification(
            "browser_environment_mismatch",
            "browser_environment_mismatch",
        )
    if class_name == "PlatformRequestEnvironmentError":
        return CrawlerFailureClassification(
            "browser_environment_mismatch",
            "request_environment_mismatch",
        )
    if class_name in {
        "ManagedRequestIdentityError",
        "ManagedDouyinRequestIdentityError",
        "XhsRequestIdentityError",
        "DouyinRequestIdentityError",
    }:
        if _contains_any(message, "signed", "signature", "a_bogus", "mstoken", "verifyfp"):
            return CrawlerFailureClassification(
                "signature_mismatch",
                "managed_request_signature_mismatch",
            )
        if "cookie" in message:
            return CrawlerFailureClassification(
                "cookie_invalid",
                "managed_request_cookie_mismatch",
            )
        return CrawlerFailureClassification(
            "browser_environment_mismatch",
            "managed_request_environment_mismatch",
        )
    if class_name == "ManagedProxyEnvironmentError" or class_name == "IPBlockError":
        return CrawlerFailureClassification(
            "proxy_or_ip_blocked",
            "managed_proxy_or_ip_blocked",
        )
    if isinstance(exc, httpx.TimeoutException):
        return CrawlerFailureClassification("timeout", "httpx_request_timeout")
    if isinstance(exc, httpx.TransportError):
        return CrawlerFailureClassification(
            "transient_network",
            "httpx_transport_error",
        )
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return CrawlerFailureClassification("timeout", "attempt_timeout")

    if _contains_any(
        message,
        "second verification",
        "secondary verification",
        "二次验证",
        "二验",
    ):
        return CrawlerFailureClassification(
            "second_verification",
            "platform_second_verification",
        )
    if _contains_any(message, "captcha", "human verification", "滑块", "验证码"):
        return CrawlerFailureClassification(
            "captcha_or_human_verification",
            "platform_human_verification",
        )
    if _contains_any(message, "rate limit", "too many requests", "频率限制", "限流"):
        return CrawlerFailureClassification("rate_limited", "platform_rate_limited")
    if _contains_any(message, "proxy blocked", "ip blocked", "account blocked", "代理封禁"):
        return CrawlerFailureClassification(
            "proxy_or_ip_blocked",
            "platform_proxy_or_ip_blocked",
        )
    if _contains_any(message, "signature", "a_bogus", "signed request", "签名"):
        return CrawlerFailureClassification(
            "signature_mismatch",
            "platform_signature_mismatch",
        )
    if _contains_any(message, "cookie invalid", "invalid cookie", "cookie expired"):
        return CrawlerFailureClassification("cookie_invalid", "platform_cookie_invalid")
    if _contains_any(
        message,
        "login required",
        "requires_relogin",
        "not logged",
        "未登录",
        "登录态失效",
    ):
        return CrawlerFailureClassification("login_required", "platform_login_required")
    if _contains_any(
        message,
        "response schema",
        "protocol changed",
        "invalid response",
        "unexpected response",
    ) or class_name in {"DataFetchError", "JSONDecodeError", "KeyError"}:
        return CrawlerFailureClassification(
            "platform_protocol_changed",
            "platform_protocol_changed",
        )
    if module_name.startswith("playwright"):
        return CrawlerFailureClassification(
            "browser_environment_mismatch",
            "browser_runtime_error",
        )
    return CrawlerFailureClassification("process_crashed", "unclassified_child_error")


def build_crawler_attempt_result(
    binding: PlatformRequestBinding,
    *,
    status: str,
    category: str = "",
    reason_code: str,
    retry_ordinal: int,
    recorded_at: str | None = None,
) -> CrawlerAttemptResult:
    if not isinstance(binding, PlatformRequestBinding):
        raise CrawlerAttemptResultError("crawler attempt binding invalid")
    retryable = is_retryable_crawler_category(category) if category else False
    return CrawlerAttemptResult(
        contract_version=CRAWLER_ATTEMPT_RESULT_CONTRACT_VERSION,
        status=status,
        category=category,
        reason_code=reason_code,
        retryable=retryable,
        workspace_id=binding.workspace_id,
        account_id=binding.account_id,
        platform=binding.platform,
        profile_key=binding.profile_key,
        resolution_id=binding.resolution_id,
        attempt_id=binding.attempt_id,
        run_id=binding.run_id,
        identity_revision=binding.identity_revision,
        cookie_material_revision=binding.cookie_material_revision,
        proxy_revision=binding.proxy_revision,
        retry_ordinal=retry_ordinal,
        recorded_at=recorded_at or datetime.now(timezone.utc).isoformat(),
    )


def write_crawler_attempt_result(
    destination: Path,
    result: CrawlerAttemptResult,
) -> None:
    if not isinstance(result, CrawlerAttemptResult):
        raise CrawlerAttemptResultError("crawler attempt result invalid")
    path = Path(destination).resolve()
    payload = json.dumps(
        result.to_safe_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if len(payload.encode("utf-8")) > CRAWLER_ATTEMPT_RESULT_MAX_BYTES:
        raise CrawlerAttemptResultError("crawler attempt result too large")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def read_crawler_attempt_result(
    source: Path,
    *,
    expected_binding: PlatformRequestBinding,
    expected_retry_ordinal: int,
    child_started_at: datetime,
) -> CrawlerAttemptResult:
    path = Path(source).resolve()
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CrawlerAttemptResultError("crawler attempt result missing") from exc
    if len(payload.encode("utf-8")) > CRAWLER_ATTEMPT_RESULT_MAX_BYTES:
        raise CrawlerAttemptResultError("crawler attempt result too large")
    try:
        value = json.loads(payload)
    except (TypeError, ValueError) as exc:
        raise CrawlerAttemptResultError("crawler attempt result malformed") from exc
    expected_fields = {field.name for field in fields(CrawlerAttemptResult)}
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise CrawlerAttemptResultError("crawler attempt result fields invalid")
    try:
        result = CrawlerAttemptResult(**value)
    except (TypeError, ValueError) as exc:
        raise CrawlerAttemptResultError("crawler attempt result invalid") from exc
    binding_fields = (
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
    if any(
        getattr(result, name) != getattr(expected_binding, name)
        for name in binding_fields
    ) or result.retry_ordinal != expected_retry_ordinal:
        raise CrawlerAttemptResultError("crawler attempt result binding mismatch")
    started = child_started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    recorded = _parse_datetime(result.recorded_at, "recorded_at")
    now = datetime.now(timezone.utc)
    if recorded < started.astimezone(timezone.utc) - timedelta(seconds=1):
        raise CrawlerAttemptResultError("crawler attempt result stale")
    if recorded > now + timedelta(seconds=60):
        raise CrawlerAttemptResultError("crawler attempt result timestamp invalid")
    return result


def record_current_crawler_attempt_result(
    *,
    status: str,
    category: str = "",
    reason_code: str,
) -> CrawlerAttemptResult | None:
    destination_value = os.environ.pop(CRAWLER_ATTEMPT_RESULT_ENV_NAME, "")
    retry_value = os.environ.pop(CRAWLER_RETRY_ORDINAL_ENV_NAME, "")
    if not destination_value:
        return None
    try:
        retry_ordinal = int(retry_value)
    except (TypeError, ValueError) as exc:
        raise CrawlerAttemptResultError("crawler attempt retry ordinal missing") from exc
    binding = request_binding_from_environment(required=True)
    if binding is None:
        raise CrawlerAttemptResultError("crawler attempt binding missing")
    result = build_crawler_attempt_result(
        binding,
        status=status,
        category=category,
        reason_code=reason_code,
        retry_ordinal=retry_ordinal,
    )
    write_crawler_attempt_result(Path(destination_value), result)
    return result


def record_current_crawler_exception(
    exc: BaseException,
) -> CrawlerFailureClassification | None:
    if not os.environ.get(CRAWLER_ATTEMPT_RESULT_ENV_NAME):
        return None
    classified = classify_crawler_exception(exc)
    record_current_crawler_attempt_result(
        status=_status_for_category(classified.category),
        category=classified.category,
        reason_code=classified.reason_code,
    )
    return classified


def _status_for_category(category: str) -> str:
    if category == "cancelled":
        return "cancelled"
    if category == "timeout":
        return "timeout"
    if category == "process_crashed":
        return "process_crashed"
    return "failed"


def _validate_category(category: str) -> None:
    if category not in CRAWLER_FAILURE_CATEGORIES:
        raise CrawlerAttemptResultError("crawler attempt failure category invalid")


def _validate_reason_code(reason_code: str) -> None:
    if not _SAFE_REASON_RE.fullmatch(str(reason_code or "")):
        raise CrawlerAttemptResultError("crawler attempt reason code invalid")


def _contains_any(value: str, *markers: str) -> bool:
    return any(marker in value for marker in markers)


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise CrawlerAttemptResultError(
            f"crawler attempt {field} timestamp invalid"
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
