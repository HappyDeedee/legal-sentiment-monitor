from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping

from tools.platform_request_environment import (
    PlatformRequestEnvironment,
    PlatformRequestEnvironmentError,
)


class XhsRequestIdentityError(RuntimeError):
    """A Xiaohongshu request does not match its frozen account environment."""


_CANONICAL_HEADER_NAMES = {
    "accept-language": "Accept-Language",
    "cookie": "Cookie",
    "sec-ch-ua": "sec-ch-ua",
    "sec-ch-ua-mobile": "sec-ch-ua-mobile",
    "sec-ch-ua-platform": "sec-ch-ua-platform",
    "user-agent": "User-Agent",
}


@dataclass(frozen=True, slots=True)
class XhsRequestIdentity:
    environment: PlatformRequestEnvironment
    cookie_header: str
    cookie_items: tuple[tuple[str, str], ...]
    header_items: tuple[tuple[str, str], ...]
    proxy_url: str | None
    cookie_digest: str
    user_agent_digest: str
    client_hints_digest: str
    proxy_digest: str

    @property
    def cookie_dict(self) -> dict[str, str]:
        return dict(self.cookie_items)

    @property
    def headers(self) -> dict[str, str]:
        return dict(self.header_items)

    def assert_runtime(
        self,
        *,
        headers: Mapping[str, Any],
        proxy_url: str | None,
    ) -> None:
        actual = _canonical_headers(headers)
        for name, value in self.headers.items():
            if actual.get(name) != value:
                raise XhsRequestIdentityError(
                    f"XHS managed request {name.lower()} mismatch"
                )
        if _normalized_proxy(proxy_url) != _normalized_proxy(self.proxy_url):
            raise XhsRequestIdentityError("XHS managed request proxy mismatch")

    def to_safe_dict(self) -> dict[str, Any]:
        environment = self.environment
        return {
            "contract_version": environment.contract_version,
            "workspace_id": environment.workspace_id,
            "account_id": environment.account_id,
            "platform": environment.platform,
            "profile_key": environment.profile_key,
            "resolution_id": environment.resolution_id,
            "attempt_id": environment.attempt_id,
            "run_id": environment.run_id,
            "identity_revision": environment.identity_revision,
            "cookie_material_revision": environment.cookie_material_revision,
            "proxy_revision": environment.proxy_revision,
            "cookie_digest": self.cookie_digest,
            "user_agent_digest": self.user_agent_digest,
            "client_hints_digest": self.client_hints_digest,
            "proxy_digest": self.proxy_digest,
        }


def build_xhs_request_identity(
    *,
    environment: PlatformRequestEnvironment,
    cookie_header: str,
    cookie_dict: Mapping[str, Any],
    headers: Mapping[str, Any],
    proxy_url: str | None,
) -> XhsRequestIdentity:
    if environment.platform != "xhs":
        raise XhsRequestIdentityError("XHS managed request platform mismatch")
    try:
        environment.assert_active()
    except PlatformRequestEnvironmentError as exc:
        raise XhsRequestIdentityError("XHS managed request environment is inactive") from exc

    parsed_cookie = _parse_cookie_header(cookie_header)
    supplied_cookie = {str(name): str(value) for name, value in cookie_dict.items()}
    if parsed_cookie != supplied_cookie:
        raise XhsRequestIdentityError("XHS managed request cookie sources mismatch")
    if not parsed_cookie.get("a1"):
        raise XhsRequestIdentityError("XHS managed request a1 is missing")
    if not parsed_cookie.get("web_session"):
        raise XhsRequestIdentityError("XHS managed request web_session is missing")

    canonical_headers = _canonical_headers(headers)
    if canonical_headers.get("Cookie") != cookie_header:
        raise XhsRequestIdentityError("XHS managed request cookie header mismatch")
    if canonical_headers.get("User-Agent") != environment.user_agent:
        raise XhsRequestIdentityError("XHS managed request user-agent mismatch")
    if canonical_headers.get("Accept-Language") != environment.accept_language:
        raise XhsRequestIdentityError("XHS managed request accept-language mismatch")

    sec_ch_ua = canonical_headers.get("sec-ch-ua", "")
    expected_major = _browser_major(environment.effective_browser_version)
    advertised_majors = set(re.findall(r'v="(\d+)"', sec_ch_ua))
    if not sec_ch_ua or expected_major not in advertised_majors:
        raise XhsRequestIdentityError("XHS managed request sec-ch-ua mismatch")

    normalized_proxy = _normalized_proxy(proxy_url)
    if environment.proxy_policy == "direct" and normalized_proxy:
        raise XhsRequestIdentityError("XHS managed request proxy mismatch")
    if environment.proxy_policy == "account_bound" and not normalized_proxy:
        raise XhsRequestIdentityError("XHS managed request proxy is missing")

    return XhsRequestIdentity(
        environment=environment,
        cookie_header=cookie_header,
        cookie_items=tuple(sorted(parsed_cookie.items())),
        header_items=tuple(canonical_headers.items()),
        proxy_url=normalized_proxy or None,
        cookie_digest=safe_digest(parsed_cookie),
        user_agent_digest=safe_digest(environment.user_agent),
        client_hints_digest=safe_digest(
            {
                "sec_ch_ua": sec_ch_ua,
                "sec_ch_ua_mobile": canonical_headers.get("sec-ch-ua-mobile", ""),
                "sec_ch_ua_platform": canonical_headers.get("sec-ch-ua-platform", ""),
            }
        ),
        proxy_digest=safe_digest(normalized_proxy or "direct"),
    )


def build_xhs_sec_ch_ua(environment: PlatformRequestEnvironment) -> str:
    major = _browser_major(environment.effective_browser_version)
    if environment.browser_channel == "chrome":
        return f'"Google Chrome";v="{major}", "Chromium";v="{major}", "Not.A/Brand";v="99"'
    if environment.browser_channel == "edge":
        return f'"Microsoft Edge";v="{major}", "Chromium";v="{major}", "Not.A/Brand";v="99"'
    return f'"Chromium";v="{major}", "Not.A/Brand";v="99"'


def safe_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _canonical_headers(headers: Mapping[str, Any]) -> dict[str, str]:
    canonical: dict[str, str] = {}
    seen: set[str] = set()
    for raw_name, raw_value in headers.items():
        lowered = str(raw_name).strip().lower()
        if not lowered or lowered in seen:
            raise XhsRequestIdentityError("XHS managed request duplicate header")
        seen.add(lowered)
        name = _CANONICAL_HEADER_NAMES.get(lowered, str(raw_name))
        canonical[name] = str(raw_value)
    return canonical


def _parse_cookie_header(cookie_header: str) -> dict[str, str]:
    if not isinstance(cookie_header, str) or not cookie_header.strip():
        raise XhsRequestIdentityError("XHS managed request cookie is missing")
    parsed: dict[str, str] = {}
    for part in cookie_header.split(";"):
        token = part.strip()
        if not token or "=" not in token:
            raise XhsRequestIdentityError("XHS managed request cookie is malformed")
        name, value = token.split("=", 1)
        name = name.strip()
        if not name or name in parsed:
            raise XhsRequestIdentityError("XHS managed request cookie is ambiguous")
        parsed[name] = value.strip()
    return parsed


def _browser_major(version: str) -> str:
    match = re.match(r"(\d+)", str(version))
    if not match:
        raise XhsRequestIdentityError("XHS managed request browser version is invalid")
    return match.group(1)


def _normalized_proxy(proxy_url: str | None) -> str:
    return str(proxy_url or "").strip()
