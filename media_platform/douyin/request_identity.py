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


class DouyinRequestIdentityError(RuntimeError):
    """A Douyin request does not match its frozen account environment."""


_CANONICAL_HEADER_NAMES = {
    "accept-language": "Accept-Language",
    "cookie": "Cookie",
    "sec-ch-ua": "sec-ch-ua",
    "sec-ch-ua-mobile": "sec-ch-ua-mobile",
    "sec-ch-ua-platform": "sec-ch-ua-platform",
    "user-agent": "User-Agent",
}
_BOUND_HEADER_NAMES = (
    "Accept-Language",
    "Cookie",
    "User-Agent",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
)


@dataclass(frozen=True, slots=True)
class DouyinRequestIdentity:
    environment: PlatformRequestEnvironment
    cookie_header: str
    cookie_items: tuple[tuple[str, str], ...]
    header_items: tuple[tuple[str, str], ...]
    proxy_url: str | None
    ms_token: str
    ttwid: str
    verify_fp: str
    web_id: str
    common_param_items: tuple[tuple[str, str], ...]
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

    @property
    def common_params(self) -> dict[str, str]:
        return dict(self.common_param_items)

    def assert_runtime(
        self,
        *,
        headers: Mapping[str, Any],
        proxy_url: str | None,
    ) -> None:
        actual = _canonical_headers(headers)
        expected = self.headers
        for name in _BOUND_HEADER_NAMES:
            value = expected.get(name)
            if actual.get(name) != value:
                raise DouyinRequestIdentityError(
                    f"Douyin managed request {name.lower()} mismatch"
                )
        if _normalized_proxy(proxy_url) != _normalized_proxy(self.proxy_url):
            raise DouyinRequestIdentityError("Douyin managed request proxy mismatch")

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


async def capture_douyin_page_snapshot(page: Any) -> dict[str, Any]:
    if page is None or not callable(getattr(page, "evaluate", None)):
        raise DouyinRequestIdentityError("Douyin managed request Page is missing")
    try:
        value = await page.evaluate(
            """() => {
              let tokenCache = {};
              try {
                tokenCache = JSON.parse(localStorage.getItem('__tea_cache_tokens_6383') || '{}');
              } catch (_) {
                tokenCache = {};
              }
              const userAgentData = navigator.userAgentData || {};
              return {
                navigator_user_agent: String(navigator.userAgent || ''),
                navigator_platform: String(navigator.platform || ''),
                ua_brands: Array.from(userAgentData.brands || []).map(
                  item => [String(item.brand || ''), String(item.version || '')]
                ),
                ua_platform: String(userAgentData.platform || ''),
                ua_mobile: Boolean(userAgentData.mobile),
                hardware_concurrency: Number(navigator.hardwareConcurrency || 0),
                device_memory: Number(navigator.deviceMemory || 0),
                screen_width: Number(screen.width),
                screen_height: Number(screen.height),
                viewport_width: Number(innerWidth),
                viewport_height: Number(innerHeight),
                ms_token: String(localStorage.getItem('xmst') || ''),
                web_id: String(tokenCache.web_id || '')
              };
            }"""
        )
    except Exception as exc:
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile snapshot failed"
        ) from exc
    return _normalize_page_snapshot(value)


def build_douyin_request_identity(
    *,
    environment: PlatformRequestEnvironment,
    cookie_header: str,
    cookie_dict: Mapping[str, Any],
    headers: Mapping[str, Any],
    proxy_url: str | None,
    page_snapshot: Mapping[str, Any],
) -> DouyinRequestIdentity:
    if environment.platform != "dy":
        raise DouyinRequestIdentityError("Douyin managed request platform mismatch")
    try:
        environment.assert_active()
    except PlatformRequestEnvironmentError as exc:
        raise DouyinRequestIdentityError(
            "Douyin managed request environment is inactive"
        ) from exc

    parsed_cookie = _parse_cookie_header(cookie_header)
    supplied_cookie = {str(name): str(value) for name, value in cookie_dict.items()}
    if parsed_cookie != supplied_cookie:
        raise DouyinRequestIdentityError(
            "Douyin managed request cookie sources mismatch"
        )
    ttwid = str(parsed_cookie.get("ttwid") or "").strip()
    if not ttwid:
        raise DouyinRequestIdentityError("Douyin managed request ttwid is missing")
    verify_fp = str(parsed_cookie.get("s_v_web_id") or "").strip()
    if not verify_fp:
        raise DouyinRequestIdentityError("Douyin managed request verifyFp is missing")

    snapshot = _normalize_page_snapshot(page_snapshot)
    ms_token = str(snapshot["ms_token"] or "").strip()
    if not ms_token:
        raise DouyinRequestIdentityError("Douyin managed request msToken is missing")
    web_id = str(snapshot["web_id"] or "").strip()
    if not re.fullmatch(r"\d{19}", web_id):
        raise DouyinRequestIdentityError("Douyin managed request webid is missing")

    canonical_headers = _canonical_headers(headers)
    if canonical_headers.get("Cookie") != cookie_header:
        raise DouyinRequestIdentityError(
            "Douyin managed request cookie header mismatch"
        )
    if canonical_headers.get("User-Agent") != environment.user_agent:
        raise DouyinRequestIdentityError(
            "Douyin managed request user-agent mismatch"
        )
    if snapshot["navigator_user_agent"] != environment.user_agent:
        raise DouyinRequestIdentityError(
            "Douyin managed request navigator user-agent mismatch"
        )
    if canonical_headers.get("Accept-Language") != environment.accept_language:
        raise DouyinRequestIdentityError(
            "Douyin managed request accept-language mismatch"
        )

    expected_screen = (
        environment.screen_width,
        environment.screen_height,
        environment.viewport_width,
        environment.viewport_height,
    )
    actual_screen = (
        snapshot["screen_width"],
        snapshot["screen_height"],
        snapshot["viewport_width"],
        snapshot["viewport_height"],
    )
    if actual_screen != expected_screen:
        raise DouyinRequestIdentityError("Douyin managed request screen mismatch")
    if bool(snapshot["ua_mobile"]) != environment.is_mobile:
        raise DouyinRequestIdentityError("Douyin managed request mobile flag mismatch")
    if environment.browser_platform != "windows":
        raise DouyinRequestIdentityError(
            "Douyin managed request browser platform is unsupported"
        )
    if snapshot["navigator_platform"] != "Win32" or snapshot["ua_platform"] != "Windows":
        raise DouyinRequestIdentityError(
            "Douyin managed request browser platform mismatch"
        )

    expected_client_hints = build_douyin_client_hints(environment, snapshot)
    for name, value in expected_client_hints.items():
        if canonical_headers.get(name) != value:
            raise DouyinRequestIdentityError(
                f"Douyin managed request {name} mismatch"
            )

    normalized_proxy = _normalized_proxy(proxy_url)
    if environment.proxy_policy == "direct" and normalized_proxy:
        raise DouyinRequestIdentityError("Douyin managed request proxy mismatch")
    if environment.proxy_policy == "account_bound" and not normalized_proxy:
        raise DouyinRequestIdentityError("Douyin managed request proxy is missing")

    common_params = _common_params(environment, snapshot, ms_token, web_id)
    token_digest = safe_digest(
        {
            "ms_token": ms_token,
            "ttwid": ttwid,
            "verify_fp": verify_fp,
            "web_id": web_id,
        }
    )
    return DouyinRequestIdentity(
        environment=environment,
        cookie_header=cookie_header,
        cookie_items=tuple(sorted(parsed_cookie.items())),
        header_items=tuple(canonical_headers.items()),
        proxy_url=normalized_proxy or None,
        ms_token=ms_token,
        ttwid=ttwid,
        verify_fp=verify_fp,
        web_id=web_id,
        common_param_items=tuple(common_params.items()),
        cookie_digest=safe_digest(parsed_cookie),
        user_agent_digest=safe_digest(environment.user_agent),
        client_hints_digest=safe_digest(
            {
                **expected_client_hints,
                "hardware_concurrency": snapshot["hardware_concurrency"],
                "device_memory": snapshot["device_memory"],
                "token_digest": token_digest,
            }
        ),
        proxy_digest=safe_digest(normalized_proxy or "direct"),
    )


def safe_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def build_douyin_client_hints(
    environment: PlatformRequestEnvironment,
    page_snapshot: Mapping[str, Any],
) -> dict[str, str]:
    snapshot = _normalize_page_snapshot(page_snapshot)
    return {
        "sec-ch-ua": _sec_ch_ua(snapshot["ua_brands"], environment),
        "sec-ch-ua-mobile": "?1" if environment.is_mobile else "?0",
        "sec-ch-ua-platform": '"Windows"',
    }


def _common_params(
    environment: PlatformRequestEnvironment,
    snapshot: Mapping[str, Any],
    ms_token: str,
    web_id: str,
) -> dict[str, str]:
    channel_names = {
        "chrome": "Chrome",
        "edge": "Edge",
        "chromium": "Chromium",
    }
    browser_name = channel_names.get(environment.browser_channel)
    if browser_name is None:
        raise DouyinRequestIdentityError(
            "Douyin managed request browser channel is unsupported"
        )
    return {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "version_code": "190600",
        "version_name": "19.6.0",
        "update_version_code": "170400",
        "pc_client_type": "1",
        "cookie_enabled": "true",
        "browser_language": environment.locale,
        "browser_platform": str(snapshot["navigator_platform"]),
        "browser_name": browser_name,
        "browser_version": environment.effective_browser_version,
        "browser_online": "true",
        "engine_name": "Blink",
        "os_name": "Windows",
        "os_version": "10",
        "cpu_core_num": str(snapshot["hardware_concurrency"]),
        "device_memory": str(snapshot["device_memory"]),
        "engine_version": environment.effective_browser_version,
        "platform": "PC",
        "screen_width": str(environment.screen_width),
        "screen_height": str(environment.screen_height),
        "effective_type": "4g",
        "round_trip_time": "50",
        "webid": web_id,
        "msToken": ms_token,
    }


def _normalize_page_snapshot(value: Mapping[str, Any] | Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile snapshot is invalid"
        )
    required = {
        "navigator_user_agent",
        "navigator_platform",
        "ua_brands",
        "ua_platform",
        "ua_mobile",
        "hardware_concurrency",
        "device_memory",
        "screen_width",
        "screen_height",
        "viewport_width",
        "viewport_height",
        "ms_token",
        "web_id",
    }
    if not required.issubset(value):
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile snapshot is incomplete"
        )
    result = {name: value[name] for name in required}
    if type(result["ua_mobile"]) is not bool:
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile mobile flag is invalid"
        )
    for name in (
        "hardware_concurrency",
        "device_memory",
        "screen_width",
        "screen_height",
        "viewport_width",
        "viewport_height",
    ):
        raw = result[name]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or raw <= 0:
            raise DouyinRequestIdentityError(
                f"Douyin managed request Profile {name} is invalid"
            )
        result[name] = int(raw)
    brands: list[tuple[str, str]] = []
    raw_brands = result["ua_brands"]
    if not isinstance(raw_brands, (list, tuple)):
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile UA brands are invalid"
        )
    for item in raw_brands:
        if isinstance(item, Mapping):
            brand = str(item.get("brand") or "")
            version = str(item.get("version") or "")
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            brand, version = str(item[0]), str(item[1])
        else:
            raise DouyinRequestIdentityError(
                "Douyin managed request Profile UA brands are invalid"
            )
        if not brand or not re.fullmatch(r"\d{1,3}", version):
            raise DouyinRequestIdentityError(
                "Douyin managed request Profile UA brands are invalid"
            )
        brands.append((brand, version))
    result["ua_brands"] = tuple(brands)
    for name in (
        "navigator_user_agent",
        "navigator_platform",
        "ua_platform",
        "ms_token",
        "web_id",
    ):
        result[name] = str(result[name] or "")
    return result


def _sec_ch_ua(
    brands: tuple[tuple[str, str], ...],
    environment: PlatformRequestEnvironment,
) -> str:
    major = str(environment.effective_browser_version).split(".", 1)[0]
    if not any(version == major and "chrom" in brand.lower() for brand, version in brands):
        raise DouyinRequestIdentityError(
            "Douyin managed request Profile UA brands mismatch"
        )
    return ", ".join(
        f'"{brand.replace(chr(34), "")}";v="{version}"'
        for brand, version in brands
    )


def _canonical_headers(headers: Mapping[str, Any]) -> dict[str, str]:
    canonical: dict[str, str] = {}
    seen: set[str] = set()
    for raw_name, raw_value in headers.items():
        lowered = str(raw_name).strip().lower()
        if not lowered or lowered in seen:
            raise DouyinRequestIdentityError(
                "Douyin managed request duplicate header"
            )
        seen.add(lowered)
        canonical[_CANONICAL_HEADER_NAMES.get(lowered, str(raw_name))] = str(
            raw_value
        )
    return canonical


def _parse_cookie_header(cookie_header: str) -> dict[str, str]:
    if not isinstance(cookie_header, str) or not cookie_header.strip():
        raise DouyinRequestIdentityError("Douyin managed request cookie is missing")
    parsed: dict[str, str] = {}
    for part in cookie_header.split(";"):
        token = part.strip()
        if not token or "=" not in token:
            raise DouyinRequestIdentityError(
                "Douyin managed request cookie is malformed"
            )
        name, value = token.split("=", 1)
        name = name.strip()
        if not name or name in parsed:
            raise DouyinRequestIdentityError(
                "Douyin managed request cookie is ambiguous"
            )
        parsed[name] = value.strip()
    return parsed


def _normalized_proxy(proxy_url: str | None) -> str:
    return str(proxy_url or "").strip()
