from __future__ import annotations

import inspect
from typing import Any

import config
from media_platform.douyin.login import DouYinLogin
from media_platform.kuaishou.login import KuaishouLogin
from media_platform.xhs.login import XiaoHongShuLogin
from tenacity import RetryError, stop_after_attempt, wait_fixed


SUPPORTED_MONITOR_PLATFORMS = ("dy", "ks", "xhs")
PRODUCT_LOGIN_TYPES = ("qrcode", "cookie")

LOGIN_TYPE_LABELS = {
    "qrcode": "网页登录态 / 扫码",
    "phone": "手机号",
    "cookie": "Cookie",
}

MEDIACRAWLER_LOGIN_CLASSES = {
    "dy": DouYinLogin,
    "ks": KuaishouLogin,
    "xhs": XiaoHongShuLogin,
}

PLATFORM_LOGIN_TYPES = {
    platform: tuple(getattr(login_class, "SUPPORTED_LOGIN_TYPES", ("qrcode", "cookie")))
    for platform, login_class in MEDIACRAWLER_LOGIN_CLASSES.items()
}


def get_mediacrawler_login_capability(platform: str) -> dict[str, Any]:
    """Return the platform login capability exposed by MediaCrawler itself."""

    login_class = MEDIACRAWLER_LOGIN_CLASSES.get(platform)
    if not login_class:
        raise ValueError("unsupported platform")
    login_url = str(getattr(login_class, "LOGIN_URL", ""))
    if platform == "xhs" and getattr(config, "XHS_INTERNATIONAL", False):
        login_url = "https://www.rednote.com"
    mediacrawler_supported_login_types = tuple(getattr(login_class, "SUPPORTED_LOGIN_TYPES", ("qrcode", "cookie")))
    supported_login_types = tuple(
        login_type
        for login_type in PRODUCT_LOGIN_TYPES
        if login_type in mediacrawler_supported_login_types
    )
    return {
        "platform": platform,
        "source": "MediaCrawler",
        "boundary": "media_crawler_only",
        "captcha_policy": "report_only",
        "login_engine": "MediaCrawler platform login class",
        "login_class": f"{login_class.__module__}.{login_class.__name__}",
        "bridge_role": "capture_qrcode_and_forward_status_only",
        "qrcode_capture_method": str(getattr(login_class, "QRCODE_CAPTURE_METHOD", "tools.utils.find_login_qrcode")),
        "qrcode_prepare_method": f"{login_class.__name__}.prepare_qrcode_login",
        "qrcode_flow_steps": list(getattr(login_class, "QRCODE_FLOW_STEPS", ()) or ()),
        "crawler_cli_login_argument": "--lt",
        "login_url": login_url,
        "login_button_selector": str(getattr(login_class, "LOGIN_BUTTON_SELECTOR", "")),
        "login_dialog_selector": str(getattr(login_class, "LOGIN_DIALOG_SELECTOR", "")),
        "qrcode_selector": str(getattr(login_class, "QRCODE_SELECTOR", "")),
        "login_state": _login_state_markers(login_class),
        "manual_verification": _manual_verification_markers(login_class),
        "mediacrawler_supported_login_types": list(mediacrawler_supported_login_types),
        "supported_login_types": list(supported_login_types),
        "supported_login_type_labels": {
            login_type: LOGIN_TYPE_LABELS.get(login_type, login_type) for login_type in supported_login_types
        },
        "phone_supported": False,
        "mediacrawler_phone_supported": "phone" in mediacrawler_supported_login_types,
        "cookie_supported": "cookie" in supported_login_types,
        "qrcode_supported": "qrcode" in supported_login_types and bool(getattr(login_class, "QRCODE_SELECTOR", "")),
        "integration_note": "后台只包装 MediaCrawler 已有登录方式；验证码、滑块、短信只回传状态，不自动绕过。",
        "unsupported_behaviors": [
            "不实现独立平台登录爬虫",
            "不绕过滑块、图形验证码或短信验证码",
            "不新增 MediaCrawler 未支持的 login_type",
        ],
    }


def list_mediacrawler_login_capabilities() -> list[dict[str, Any]]:
    return [get_mediacrawler_login_capability(platform) for platform in SUPPORTED_MONITOR_PLATFORMS]


async def call_mediacrawler_check_login_state(
    platform: str,
    browser_context: Any,
    context_page: Any,
    login_baseline: str = "",
) -> bool:
    """Run MediaCrawler's own login-state check once for UI polling/account checks."""

    login_class = MEDIACRAWLER_LOGIN_CLASSES.get(platform)
    if not login_class:
        return False
    login_adapter = login_class("qrcode", browser_context, context_page)
    check_login_state = getattr(login_adapter, "check_login_state", None)
    if not check_login_state:
        return False
    checker = (
        check_login_state.retry_with(stop=stop_after_attempt(1), wait=wait_fixed(0))
        if hasattr(check_login_state, "retry_with")
        else check_login_state
    )
    try:
        params = inspect.signature(check_login_state).parameters
        if len(params) >= 1:
            return bool(await checker(login_baseline))
        return bool(await checker())
    except RetryError:
        return False
    except Exception:
        return False


def _login_state_markers(login_class: Any) -> dict[str, Any]:
    return {
        "cookie_rules": dict(getattr(login_class, "LOGIN_STATE_COOKIE_RULES", {}) or {}),
        "local_storage_rules": dict(getattr(login_class, "LOGIN_STATE_LOCAL_STORAGE_RULES", {}) or {}),
        "session_cookie": str(getattr(login_class, "LOGIN_STATE_SESSION_COOKIE", "") or ""),
        "profile_selector": str(getattr(login_class, "LOGIN_STATE_PROFILE_SELECTOR", "") or ""),
        "anonymous_selector": str(getattr(login_class, "LOGIN_STATE_ANONYMOUS_SELECTOR", "") or ""),
    }


def _manual_verification_markers(login_class: Any) -> dict[str, Any]:
    text_markers = getattr(login_class, "MANUAL_VERIFICATION_TEXT_MARKERS", {}) or {}
    selector_markers = getattr(login_class, "MANUAL_VERIFICATION_SELECTORS", {}) or {}
    return {
        "url_markers": list(getattr(login_class, "MANUAL_VERIFICATION_URL_MARKERS", ()) or ()),
        "labels": dict(getattr(login_class, "MANUAL_VERIFICATION_LABELS", {}) or {}),
        "text_markers": {
            str(verification_type): list(markers or ())
            for verification_type, markers in dict(text_markers).items()
        },
        "selectors": {
            str(verification_type): list(selectors or ())
            for verification_type, selectors in dict(selector_markers).items()
        },
    }
