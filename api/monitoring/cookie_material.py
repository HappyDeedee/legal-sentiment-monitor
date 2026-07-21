"""Canonical Cookie material used by the CR-112 profile promotion path.

The module deliberately keeps Cookie values in memory only. Callers must not
place the returned records in logs, audit details, URLs, or subprocess
arguments.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from typing import Any


COOKIE_PROTOCOL_VERSION = 1
COOKIE_LOGIN_HYDRATION_WAIT_MS = 3000
MAX_COOKIE_RECORDS = 256
MAX_COOKIE_RECORD_BYTES = 8192
MAX_COOKIE_PAYLOAD_BYTES = 1048576

_PLATFORM_COOKIE_ROOTS: dict[str, tuple[str, ...]] = {
    "dy": ("douyin.com",),
    "ks": ("kuaishou.com",),
    "xhs": ("xiaohongshu.com", "rednote.com"),
}
_RECORD_KEYS = frozenset(
    {
        "name",
        "value",
        "domain",
        "path",
        "expires",
        "http_only",
        "secure",
        "same_site",
        "host_only",
        "partition_key",
    }
)
_RECORD_ALIASES = {
    "httpOnly": "http_only",
    "sameSite": "same_site",
    "hostOnly": "host_only",
    "partitionKey": "partition_key",
}


class CookieMaterialError(ValueError):
    """A bounded, customer-safe Cookie material validation error."""

    def __init__(self, reason: str, field: str = "") -> None:
        self.reason = reason
        self.field = field
        suffix = f": {field}" if field else ""
        super().__init__(f"{reason}{suffix}")


def platform_cookie_roots(platform: str) -> tuple[str, ...]:
    key = str(platform or "").strip().lower()
    roots = _PLATFORM_COOKIE_ROOTS.get(key)
    if not roots:
        raise CookieMaterialError("cookie_platform_unsupported", "platform")
    return roots


def parse_manual_cookie_material(platform: str, cookie_header: str) -> list[dict[str, Any]]:
    """Parse a plain Cookie header into the same canonical record model."""

    if not isinstance(cookie_header, str) or not cookie_header.strip():
        raise CookieMaterialError("cookie_missing", "value")
    default_domain = f".{platform_cookie_roots(platform)[0]}"
    records: list[dict[str, Any]] = []
    for part in cookie_header.split(";"):
        item = part.strip()
        if not item:
            continue
        if "=" not in item:
            raise CookieMaterialError("cookie_malformed", "header")
        name, value = item.split("=", 1)
        if not name.strip():
            raise CookieMaterialError("cookie_malformed", "name")
        records.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": default_domain,
                "path": "/",
                "http_only": False,
                "secure": False,
                "same_site": "Lax",
                "host_only": False,
            }
        )
    if not records:
        raise CookieMaterialError("cookie_missing", "value")
    return canonicalize_cookie_records(platform, records)


def canonicalize_cookie_records(
    platform: str,
    records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Validate and normalize structured Cookie records without losing scope."""

    roots = platform_cookie_roots(platform)
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        raise CookieMaterialError("cookie_payload_invalid", "records")
    if len(records) == 0:
        raise CookieMaterialError("cookie_missing", "records")
    if len(records) > MAX_COOKIE_RECORDS:
        raise CookieMaterialError("cookie_payload_too_many_records", "records")

    canonical: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str | None]] = set()
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            raise CookieMaterialError("cookie_record_invalid", f"records[{index}]")
        normalized_input = _normalize_record_keys(raw)
        unknown = set(normalized_input) - _RECORD_KEYS
        if unknown:
            if "partition_key" in unknown or "partition_key" in normalized_input:
                raise CookieMaterialError("cookie_attribute_unsupported", f"records[{index}].partition_key")
            raise CookieMaterialError("cookie_attribute_unsupported", f"records[{index}]")
        if "partition_key" in normalized_input:
            raise CookieMaterialError("cookie_attribute_unsupported", f"records[{index}].partition_key")
        for required in ("name", "value", "domain", "path"):
            if required not in normalized_input:
                raise CookieMaterialError("cookie_required_attribute", f"records[{index}].{required}")

        name = _text(normalized_input["name"], "cookie_name", f"records[{index}].name")
        value = _text(normalized_input["value"], "cookie_value", f"records[{index}].value", allow_empty=True)
        domain, host_only = _normalize_domain(
            normalized_input["domain"],
            roots,
            f"records[{index}].domain",
        )
        path = _normalize_path(normalized_input["path"], f"records[{index}].path")
        explicit_host_only = normalized_input.get("host_only")
        if explicit_host_only is not None:
            if type(explicit_host_only) is not bool:
                raise CookieMaterialError("cookie_attribute_invalid", f"records[{index}].host_only")
            if explicit_host_only != host_only:
                raise CookieMaterialError("cookie_scope_mismatch", f"records[{index}].host_only")

        expires = _normalize_expires(normalized_input.get("expires"), f"records[{index}].expires")
        http_only = _normalize_bool(normalized_input.get("http_only", False), f"records[{index}].http_only")
        secure = _normalize_bool(normalized_input.get("secure", False), f"records[{index}].secure")
        same_site = _normalize_same_site(normalized_input.get("same_site", "Lax"), f"records[{index}].same_site")
        item: dict[str, Any] = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
            "http_only": http_only,
            "secure": secure,
            "same_site": same_site,
            "host_only": host_only,
        }
        if expires is not None:
            item["expires"] = expires
        record_bytes = _serialized_bytes(item)
        if record_bytes > MAX_COOKIE_RECORD_BYTES:
            raise CookieMaterialError("cookie_record_too_large", f"records[{index}]")
        key = (name, domain, path, None)
        if key in seen:
            raise CookieMaterialError("cookie_duplicate_scope", f"records[{index}]")
        seen.add(key)
        canonical.append(item)

    payload_bytes = _serialized_bytes({"version": COOKIE_PROTOCOL_VERSION, "records": canonical})
    if payload_bytes > MAX_COOKIE_PAYLOAD_BYTES:
        raise CookieMaterialError("cookie_payload_too_large", "records")
    return canonical


def serialize_cookie_material(platform: str, records: Sequence[Mapping[str, Any]]) -> str:
    canonical = canonicalize_cookie_records(platform, records)
    payload = {
        "version": COOKIE_PROTOCOL_VERSION,
        "records": canonical,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > MAX_COOKIE_PAYLOAD_BYTES:
        raise CookieMaterialError("cookie_payload_too_large", "records")
    return serialized


def deserialize_cookie_material(platform: str, stored: str | Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(stored, Sequence) and not isinstance(stored, (str, bytes, bytearray)):
        return canonicalize_cookie_records(platform, stored)
    if not isinstance(stored, str) or not stored.strip():
        raise CookieMaterialError("cookie_missing", "value")
    text = stored.strip()
    try:
        parsed = json.loads(text)
    except (TypeError, ValueError, json.JSONDecodeError):
        return parse_manual_cookie_material(platform, text)
    if isinstance(parsed, dict):
        if parsed.get("version") != COOKIE_PROTOCOL_VERSION or "records" not in parsed:
            raise CookieMaterialError("cookie_protocol_unsupported", "version")
        parsed = parsed["records"]
    if not isinstance(parsed, list):
        raise CookieMaterialError("cookie_payload_invalid", "records")
    return canonicalize_cookie_records(platform, parsed)


def to_playwright_cookie_items(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    # Records have already passed the platform validator before this adapter is called.
    result: list[dict[str, Any]] = []
    for record in records:
        item: dict[str, Any] = {
            "name": str(record["name"]),
            "value": str(record["value"]),
            "domain": str(record["domain"]),
            "path": str(record["path"]),
            "httpOnly": bool(record.get("http_only", False)),
            "secure": bool(record.get("secure", False)),
            "sameSite": str(record.get("same_site") or "Lax"),
        }
        if "expires" in record:
            item["expires"] = record["expires"]
        result.append(item)
    return result


def cookie_header(records: Sequence[Mapping[str, Any]]) -> str:
    """Build a transient request header; callers must not persist or log it."""

    return "; ".join(f"{record['name']}={record['value']}" for record in records)


def _normalize_record_keys(raw: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in raw.items():
        normalized = _RECORD_ALIASES.get(str(key), str(key))
        if normalized in result:
            raise CookieMaterialError("cookie_attribute_duplicate", normalized)
        result[normalized] = value
    return result


def _normalize_domain(value: Any, roots: tuple[str, ...], field: str) -> tuple[str, bool]:
    domain = _text(value, "cookie_domain_invalid", field).lower().rstrip(".")
    if not domain or "/" in domain or ":" in domain or "@" in domain or " " in domain:
        raise CookieMaterialError("cookie_domain_invalid", field)
    host_only = not domain.startswith(".")
    bare = domain[1:] if domain.startswith(".") else domain
    if any(bare == root or bare.endswith(f".{root}") for root in roots) is False:
        raise CookieMaterialError("cookie_domain_not_allowed", field)
    return (bare if host_only else f".{bare}"), host_only


def _normalize_path(value: Any, field: str) -> str:
    path = _text(value, "cookie_path_invalid", field)
    if not path.startswith("/") or "\x00" in path or "\r" in path or "\n" in path or len(path) > 4096:
        raise CookieMaterialError("cookie_path_invalid", field)
    return path


def _normalize_expires(value: Any, field: str) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise CookieMaterialError("cookie_attribute_invalid", field)
    number = float(value)
    if number < -1:
        raise CookieMaterialError("cookie_attribute_invalid", field)
    return int(value) if number.is_integer() else number


def _normalize_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        raise CookieMaterialError("cookie_attribute_invalid", field)
    return value


def _normalize_same_site(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise CookieMaterialError("cookie_attribute_invalid", field)
    normalized = value.strip().lower()
    mapping = {"strict": "Strict", "lax": "Lax", "none": "None"}
    if normalized not in mapping:
        raise CookieMaterialError("cookie_attribute_invalid", field)
    return mapping[normalized]


def _text(value: Any, reason: str, field: str, *, allow_empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not value and not allow_empty)
        or "\x00" in value
        or "\r" in value
        or "\n" in value
    ):
        raise CookieMaterialError(reason, field)
    return value


def _serialized_bytes(value: Any) -> int:
    try:
        return len(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    except (TypeError, ValueError) as exc:
        raise CookieMaterialError("cookie_payload_invalid", "records") from exc
