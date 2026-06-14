from __future__ import annotations

import base64
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from tools import utils

from .login_browser import PLATFORM_LOGIN_URLS, build_login_browser_command
from .mediacrawler_login import (
    MEDIACRAWLER_LOGIN_CLASSES,
    SUPPORTED_MONITOR_PLATFORMS,
    call_mediacrawler_check_login_state,
    get_mediacrawler_login_capability,
)
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


@dataclass
class LoginSessionHandle:
    platform: str
    playwright: Playwright
    context: BrowserContext
    page: Page
    profile_path: str
    created_at: datetime
    login_baseline: str = ""


ACTIVE_LOGIN_SESSIONS: dict[int, LoginSessionHandle] = {}


MANUAL_VERIFICATION_MESSAGE = (
    "平台在二维码前要求完成额外验证。"
    "请先按页面提示人工处理，不要关闭登录会话，系统会继续轮询二维码或登录状态。"
)


# Keep the Web QR bridge aligned with MediaCrawler's platform login flows.
# The bridge only keeps the browser session alive and serializes the QR image.
MEDIACRAWLER_LOGIN_FLOWS = {
    platform: get_mediacrawler_login_capability(platform)
    for platform in SUPPORTED_MONITOR_PLATFORMS
}

QR_SELECTORS = {
    platform: {
        "url": flow["login_url"],
        "selector": flow["qrcode_selector"],
        "login_button_selector": flow.get("login_button_selector") or "",
        "login_dialog_selector": flow.get("login_dialog_selector") or "",
    }
    for platform, flow in MEDIACRAWLER_LOGIN_FLOWS.items()
}


async def start_qrcode_login_session(session_id: int, platform: str, timeout_ms: int | None = None) -> dict[str, Any]:
    """Start a browser-backed QR login session and keep it alive for polling."""

    await close_qrcode_login_session(session_id)
    if platform not in QR_SELECTORS:
        raise ValueError("unsupported platform")
    command = build_login_browser_command(platform)
    return await start_qrcode_login_session_with_profile(session_id, platform, command, timeout_ms)


async def start_qrcode_login_session_with_profile(
    session_id: int,
    platform: str,
    command: dict[str, Any],
    timeout_ms: int | None = None,
) -> dict[str, Any]:
    """Start a QR login session using an explicit browser/profile command."""

    await close_qrcode_login_session(session_id)
    await close_qrcode_login_sessions_for_profile(command.get("profile_path") or "", except_session_id=session_id)
    if platform not in QR_SELECTORS:
        raise ValueError("unsupported platform")
    capability = MEDIACRAWLER_LOGIN_FLOWS[platform]
    timeout = int(timeout_ms or os.environ.get("MONITOR_LOGIN_QR_TIMEOUT_MS") or 20000)
    headless = _login_qr_headless()
    playwright: Playwright | None = None
    context: BrowserContext | None = None
    try:
        playwright = await async_playwright().start()
        profile_path = Path(command["profile_path"])
        profile_path.mkdir(parents=True, exist_ok=True)
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            executable_path=command["browser_path"],
            accept_downloads=True,
            headless=headless,
            viewport={"width": 1920, "height": 1080},
            user_agent=utils.get_user_agent(),
        )
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(timeout)
        await page.goto(QR_SELECTORS[platform]["url"], wait_until="domcontentloaded", timeout=timeout)
        login_adapter = _build_mediacrawler_login_adapter(platform, context, page)
        await _prepare_login_page(platform, page, timeout, login_adapter)
        login_baseline = await _login_baseline(platform, context)

        if await _is_logged_in(platform, context, page, login_baseline):
            await _close_context(playwright, context)
            return {
                "ok": True,
                "already_logged_in": True,
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "login_capability_source": "平台采集服务",
                "login_boundary": "复用平台采集服务登录能力",
                "captcha_policy": "遇到验证码、滑块或短信验证时回传状态，等待人工处理",
                "qr_image": "",
                "login_url": PLATFORM_LOGIN_URLS[platform],
                "profile_path": command["profile_path"],
                "message": "当前 Profile 已经登录，不需要重新扫码。",
            }

        qr_image = await _find_login_qrcode(page, platform, timeout, login_adapter)
        if not qr_image:
            verification = await _detect_manual_verification(platform, page)
            if verification.get("needs_verification"):
                return await _manual_verification_response(
                    session_id,
                    platform,
                    command,
                    playwright,
                    context,
                    page,
                    login_baseline,
                    verification,
                )
            details = await _describe_qrcode_failure(page, platform)
            await _close_context(playwright, context)
            return _failure(
                platform,
                command,
                f"没有在页面中找到登录二维码，请使用网页登录窗口处理。{details}",
            )
        ACTIVE_LOGIN_SESSIONS[int(session_id)] = LoginSessionHandle(
            platform=platform,
            playwright=playwright,
            context=context,
            page=page,
            profile_path=command["profile_path"],
            created_at=datetime.now(timezone.utc),
            login_baseline=login_baseline,
        )
        return {
            "ok": True,
            "platform": platform,
            "platform_label": PLATFORM_LABELS.get(platform, platform),
            "login_capability_source": "平台采集服务",
            "login_boundary": "复用平台采集服务登录能力",
            "captcha_policy": "遇到验证码、滑块或短信验证时回传状态，等待人工处理",
            "qr_image": _as_data_url(qr_image),
            "login_url": PLATFORM_LOGIN_URLS[platform],
            "profile_path": command["profile_path"],
            "message": "请使用手机扫码登录。扫码成功后系统会自动保存登录状态。",
        }
    except Exception as exc:
        await _close_context(playwright, context)
        return _failure(platform, command, _brief_exception_message(exc))


async def poll_qrcode_login_session(session_id: int) -> dict[str, Any]:
    handle = ACTIVE_LOGIN_SESSIONS.get(int(session_id))
    if not handle:
        return {"active": False, "success": False, "message": "二维码浏览器会话不在运行，请重新生成二维码或打开登录窗口。"}
    if _session_expired(handle):
        await close_qrcode_login_session(session_id)
        return {"active": False, "success": False, "expired": True, "message": "二维码已过期，请重新生成。"}
    try:
        success = await _is_logged_in(handle.platform, handle.context, handle.page, handle.login_baseline)
        if success:
            await close_qrcode_login_session(session_id)
            return {"active": False, "success": True, "message": "登录成功，Profile 已保存。"}
        login_adapter = _build_mediacrawler_login_adapter(handle.platform, handle.context, handle.page)
        qr_image = await _find_login_qrcode(handle.page, handle.platform, 5000, login_adapter)
        if qr_image:
            return {
                "active": True,
                "success": False,
                "qr_image": _as_data_url(qr_image),
                "message": "二维码已生成，请扫码登录。",
            }
        try:
            await _prepare_login_page(handle.platform, handle.page, 5000, login_adapter)
        except Exception:
            pass
        qr_image = await _find_login_qrcode(
            handle.page,
            handle.platform,
            3000,
            _build_mediacrawler_login_adapter(handle.platform, handle.context, handle.page),
        )
        if qr_image:
            return {
                "active": True,
                "success": False,
                "qr_image": _as_data_url(qr_image),
                "message": "二维码已生成，请扫码登录。",
            }
        verification = await _detect_manual_verification(handle.platform, handle.page)
        if verification.get("needs_verification"):
            return await _manual_verification_poll_response(handle, verification)
        return {"active": True, "success": False, "message": "等待扫码确认。"}
    except Exception as exc:
        return {"active": True, "success": False, "message": redact_sensitive(f"{type(exc).__name__}: {exc}")}


async def close_qrcode_login_session(session_id: int) -> None:
    handle = ACTIVE_LOGIN_SESSIONS.pop(int(session_id), None)
    if not handle:
        return
    await _close_context(handle.playwright, handle.context)


async def close_qrcode_login_sessions_for_profile(profile_path: str, except_session_id: int | None = None) -> None:
    if not profile_path:
        return
    target = str(Path(profile_path).resolve()).lower()
    session_ids = [
        session_id
        for session_id, handle in ACTIVE_LOGIN_SESSIONS.items()
        if session_id != except_session_id and str(Path(handle.profile_path).resolve()).lower() == target
    ]
    for session_id in session_ids:
        await close_qrcode_login_session(session_id)


async def _manual_verification_response(
    session_id: int,
    platform: str,
    command: dict[str, Any],
    playwright: Playwright,
    context: BrowserContext,
    page: Page,
    login_baseline: str,
    verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capability = MEDIACRAWLER_LOGIN_FLOWS[platform]
    ACTIVE_LOGIN_SESSIONS[int(session_id)] = LoginSessionHandle(
        platform=platform,
        playwright=playwright,
        context=context,
        page=page,
        profile_path=command["profile_path"],
        created_at=datetime.now(timezone.utc),
        login_baseline=login_baseline,
    )
    return {
        "ok": True,
        "needs_verification": True,
        "verification_type": (verification or {}).get("verification_type") or "manual",
        "verification_label": (verification or {}).get("verification_label") or "平台验证",
        "verification_detail": (verification or {}).get("verification_detail") or "",
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "login_capability_source": "平台采集服务",
        "login_boundary": "复用平台采集服务登录能力",
        "captcha_policy": "遇到验证码、滑块或短信验证时回传状态，等待人工处理",
        "qr_image": "",
        "verification_image": "",
        "login_url": PLATFORM_LOGIN_URLS[platform],
        "profile_path": command["profile_path"],
        "message": _verification_message(verification or {}),
    }


async def _manual_verification_poll_response(handle: LoginSessionHandle, verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "active": True,
        "success": False,
        "needs_verification": True,
        "verification_type": verification.get("verification_type") or "manual",
        "verification_label": verification.get("verification_label") or "平台验证",
        "verification_detail": verification.get("verification_detail") or "",
        "verification_image": "",
        "message": _verification_message(verification),
    }


def _build_mediacrawler_login_adapter(platform: str, context: BrowserContext, page: Page) -> Any:
    login_class = MEDIACRAWLER_LOGIN_CLASSES.get(platform)
    if not login_class:
        raise ValueError("unsupported platform")
    return login_class("qrcode", context, page)


async def _prepare_login_page(platform: str, page: Page, timeout: int, login_adapter: Any | None = None) -> None:
    if await _selector_visible(page, QR_SELECTORS[platform]["selector"], timeout=1000):
        return
    if login_adapter and hasattr(login_adapter, "prepare_qrcode_login"):
        await login_adapter.prepare_qrcode_login(timeout)
        return
    if await _needs_manual_verification(platform, page):
        return
    dialog_selector = QR_SELECTORS[platform].get("login_dialog_selector") or ""
    if dialog_selector and await _selector_visible(page, dialog_selector, timeout=min(timeout, 8000)):
        return
    login_button_selector = QR_SELECTORS[platform].get("login_button_selector") or ""
    if login_button_selector:
        await page.locator(login_button_selector).click(timeout=min(timeout, 5000))
        await page.wait_for_timeout(600)


async def _selector_visible(page: Page, selector: str, timeout: int = 1000) -> bool:
    try:
        await page.wait_for_selector(selector, state="visible", timeout=timeout)
        return True
    except Exception:
        return False


async def _find_login_qrcode(page: Page, platform: str, timeout: int, login_adapter: Any | None = None) -> str:
    config = QR_SELECTORS[platform]
    selector = str(config["selector"])
    media_crawler_image = await _find_qrcode_with_mediacrawler_adapter(login_adapter)
    if media_crawler_image:
        return media_crawler_image
    media_crawler_image = await _find_qrcode_with_mediacrawler_util(page, selector)
    if media_crawler_image:
        return media_crawler_image
    candidate_image = await _find_visible_qrcode_candidate_screenshot(page, platform)
    if candidate_image:
        return candidate_image
    return ""


async def _needs_manual_verification(platform: str, page: Page) -> bool:
    """Detect platform-side slider/captcha gates before QR login appears."""

    return bool((await _detect_manual_verification(platform, page)).get("needs_verification"))


async def _detect_manual_verification(platform: str, page: Page) -> dict[str, Any]:
    """Detect platform-side manual gates and expose a UI-readable reason."""

    verification_config = _manual_verification_config(platform)
    if not verification_config:
        return {"needs_verification": False}
    try:
        page_url = str(page.url or "").lower()
        if any(str(marker).lower() in page_url for marker in verification_config.get("url_markers", [])):
            return _verification_result(
                "captcha",
                _verification_label(verification_config, "captcha"),
                "当前页面地址显示进入了验证/风控中间页",
            )
    except Exception:
        pass
    try:
        visible_text = await page.locator("body").inner_text(timeout=1000)
        lower_text = visible_text.lower()
        for verification_type, markers in dict(verification_config.get("text_markers") or {}).items():
            matched = next((str(marker) for marker in markers if str(marker).lower() in lower_text), "")
            if matched:
                return _verification_result(
                    verification_type,
                    _verification_label(verification_config, verification_type),
                    _compact_visible_text(visible_text, matched),
                )
    except Exception:
        pass
    for verification_type, selectors in dict(verification_config.get("selectors") or {}).items():
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if await locator.count() and await locator.is_visible(timeout=500):
                    return _verification_result(
                        verification_type,
                        _verification_label(verification_config, verification_type),
                        f"页面存在验证相关元素：{selector}",
                    )
            except Exception:
                continue
    return {"needs_verification": False}


def _manual_verification_config(platform: str) -> dict[str, Any]:
    return dict((MEDIACRAWLER_LOGIN_FLOWS.get(platform) or {}).get("manual_verification") or {})


def _verification_label(verification_config: dict[str, Any], verification_type: str) -> str:
    labels = dict(verification_config.get("labels") or {})
    return str(labels.get(verification_type) or labels.get("manual") or "平台验证")


async def _page_screenshot_data_url(page: Page) -> str:
    try:
        screenshot = await page.screenshot(full_page=False)
        return _bytes_to_data_url(screenshot, "image/png")
    except Exception:
        return ""


def _verification_result(verification_type: str, label: str, detail: str) -> dict[str, Any]:
    return {
        "needs_verification": True,
        "verification_type": verification_type,
        "verification_label": label,
        "verification_detail": redact_sensitive(detail),
    }


def _verification_message(verification: dict[str, Any]) -> str:
    label = verification.get("verification_label") or "平台验证"
    detail = verification.get("verification_detail") or ""
    message = f"平台要求先完成{label}，当前不会自动处理验证码。请按页面提示人工处理后刷新登录状态。"
    if detail:
        message += f" 页面提示：{detail}"
    return message


def _compact_visible_text(visible_text: str, matched: str) -> str:
    text = re.sub(r"\s+", " ", str(visible_text or "")).strip()
    if not text:
        return matched
    index = text.lower().find(matched.lower())
    if index < 0:
        return text[:180]
    start = max(0, index - 60)
    end = min(len(text), index + 120)
    return text[start:end]


async def _find_qrcode_with_mediacrawler_util(page: Page, selector: str) -> str:
    try:
        image = await utils.find_login_qrcode(page, selector=selector)
    except Exception:
        return ""
    if _valid_qrcode_image_source(image):
        return str(image)
    return ""


async def _find_qrcode_with_mediacrawler_adapter(login_adapter: Any | None) -> str:
    if not login_adapter or not hasattr(login_adapter, "capture_qrcode"):
        return ""
    try:
        image = await login_adapter.capture_qrcode()
    except Exception:
        return ""
    if _valid_qrcode_image_source(image):
        return str(image)
    return ""


async def _find_visible_qrcode_candidate_screenshot(page: Page, platform: str) -> str:
    """Fallback for platform QR DOM changes while keeping the MediaCrawler login flow."""

    selectors = _qrcode_candidate_selectors(platform)
    for selector in selectors:
        try:
            locator = page.locator(selector)
            count = min(await locator.count(), 12)
        except Exception:
            continue
        for index in range(count):
            item = locator.nth(index)
            try:
                if not await item.is_visible(timeout=300):
                    continue
                box = await item.bounding_box()
                if not _looks_like_qrcode_box(box):
                    continue
                screenshot = await item.screenshot()
            except Exception:
                continue
            image = base64.b64encode(screenshot).decode("utf-8")
            if _valid_qrcode_image_source(image):
                return image
    return ""


def _qrcode_candidate_selectors(platform: str) -> list[str]:
    selectors = [
        str(QR_SELECTORS.get(platform, {}).get("selector") or ""),
        "img.qrcode-img",
        "img[class*='qrcode']",
        "img[class*='qr-code']",
        "img[src*='qr']",
        "img[src*='qrcode']",
        "[class*='qrcode'] img",
        "[class*='qr-code'] img",
        "[class*='qr'] img",
        "canvas[class*='qrcode']",
        "[class*='qrcode'] canvas",
    ]
    if platform == "xhs":
        selectors.extend(
            [
                ".login-container img",
                ".login-modal img",
                "[class*='login'] img",
            ]
        )
    result: list[str] = []
    for selector in selectors:
        if selector and selector not in result:
            result.append(selector)
    return result


def _looks_like_qrcode_box(box: dict[str, Any] | None) -> bool:
    if not box:
        return False
    width = float(box.get("width") or 0)
    height = float(box.get("height") or 0)
    if width < 80 or height < 80 or width > 420 or height > 420:
        return False
    ratio = width / height if height else 0
    return 0.65 <= ratio <= 1.35


def _valid_qrcode_image_source(image: Any) -> bool:
    source = str(image or "").strip()
    if not source or source.startswith("JSHandle@"):
        return False
    return source.startswith(("data:image", "http://", "https://", "//")) or bool(re.fullmatch(r"[A-Za-z0-9+/=\s]+", source))


def _bytes_to_data_url(content: bytes, content_type: str = "image/png") -> str:
    if not content:
        return ""
    content_type = (content_type or "image/png").split(";")[0]
    if not content_type.startswith("image/"):
        content_type = "image/png"
    return f"data:{content_type};base64,{base64.b64encode(content).decode('utf-8')}"


async def _describe_qrcode_failure(page: Page, platform: str) -> str:
    try:
        title = await page.title()
    except Exception:
        title = ""
    try:
        images = await page.locator("img").evaluate_all(
            """imgs => imgs.slice(0, 8).map((img, index) => ({
                index,
                className: img.className || '',
                id: img.id || '',
                src: (img.currentSrc || img.src || img.getAttribute('src') || '').slice(0, 100)
            }))"""
        )
    except Exception:
        images = []
    compact_images = []
    for item in images or []:
        src = re.sub(r"(token|ticket|session|key|code)=([^&]+)", r"\1=***", str(item.get("src") or ""))
        compact_images.append(f"{item.get('index')}:{item.get('id') or item.get('className') or 'img'}:{src}")
    page_hint = f" 当前页面：{redact_sensitive(page.url)}"
    title_hint = f"；标题：{redact_sensitive(title)}" if title else ""
    image_hint = f"；已发现图片节点：{' | '.join(compact_images[:5])}" if compact_images else "；页面没有可见图片节点"
    platform_hint = f"；平台：{PLATFORM_LABELS.get(platform, platform)}"
    return platform_hint + page_hint + title_hint + image_hint


def _as_data_url(qr_image: str) -> str:
    if qr_image.startswith("data:image"):
        return qr_image
    return "data:image/png;base64," + qr_image


def _login_qr_headless() -> bool:
    return str(os.environ.get("MONITOR_LOGIN_QR_HEADLESS") or "true").lower() not in {"0", "false", "no"}


def _failure(platform: str, command: dict[str, Any], message: str, diagnostic_image: str = "") -> dict[str, Any]:
    capability = MEDIACRAWLER_LOGIN_FLOWS.get(platform) or {}
    return {
        "ok": False,
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "login_capability_source": "平台采集服务",
        "login_boundary": "复用平台采集服务登录能力",
        "captcha_policy": "遇到验证码、滑块或短信验证时回传状态，等待人工处理",
        "qr_image": "",
        "diagnostic_image": diagnostic_image,
        "login_url": PLATFORM_LOGIN_URLS.get(platform, ""),
        "profile_path": command.get("profile_path") or "",
        "message": redact_sensitive(message),
    }


def _brief_exception_message(exc: Exception) -> str:
    raw = redact_sensitive(str(exc))
    first_line = next((line.strip() for line in raw.splitlines() if line.strip()), "")
    if "Target page, context or browser has been closed" in raw:
        first_line = "浏览器会话被关闭或 Profile 正被占用，请稍后重试。"
    return f"{type(exc).__name__}: {first_line or '登录浏览器启动失败'}"


async def _login_baseline(platform: str, context: BrowserContext) -> str:
    session_cookie = str((MEDIACRAWLER_LOGIN_FLOWS.get(platform) or {}).get("login_state", {}).get("session_cookie") or "")
    if not session_cookie:
        return ""
    cookie_dict = await _cookie_dict(context)
    return str(cookie_dict.get(session_cookie) or "")


async def _cookie_dict(context: BrowserContext) -> dict[str, Any]:
    cookies = await context.cookies()
    return {item.get("name"): item.get("value") for item in cookies}


async def _is_logged_in(platform: str, context: BrowserContext, page: Page, login_baseline: str = "") -> bool:
    login_state = (MEDIACRAWLER_LOGIN_FLOWS.get(platform) or {}).get("login_state", {}) or {}
    anonymous_selector = str(login_state.get("anonymous_selector") or "")
    if anonymous_selector:
        try:
            if await page.is_visible(anonymous_selector, timeout=500):
                return False
        except Exception:
            pass

    if await call_mediacrawler_check_login_state(platform, context, page, login_baseline):
        return True

    profile_selector = str(login_state.get("profile_selector") or "")
    if profile_selector:
        try:
            if await page.is_visible(profile_selector, timeout=500):
                return True
        except Exception:
            pass

    cookie_dict = await _cookie_dict(context)
    for key, expected in dict(login_state.get("cookie_rules") or {}).items():
        value = cookie_dict.get(key)
        if expected is None:
            if value:
                return True
        elif str(value or "") == str(expected):
            return True
    session_cookie = str(login_state.get("session_cookie") or "")
    if session_cookie:
        current_session = str(cookie_dict.get(session_cookie) or "")
        if current_session and current_session != login_baseline:
            return True
    local_storage_rules = dict(login_state.get("local_storage_rules") or {})
    if local_storage_rules:
        for candidate in context.pages:
            try:
                local_storage = await candidate.evaluate("() => window.localStorage")
                if all(str(local_storage.get(key, "")) == str(expected) for key, expected in local_storage_rules.items()):
                    return True
            except Exception:
                continue
    return False


def _session_expired(handle: LoginSessionHandle) -> bool:
    ttl_seconds = int(os.environ.get("MONITOR_LOGIN_QR_TTL_SECONDS") or 600)
    return datetime.now(timezone.utc) - handle.created_at > timedelta(seconds=ttl_seconds)


async def _close_context(playwright: Playwright | None, context: BrowserContext | None) -> None:
    if context:
        try:
            await context.close()
        except Exception:
            pass
    if playwright:
        try:
            await playwright.stop()
        except Exception:
            pass
