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
from tools.httpx_util import make_async_client

from .login_browser import PLATFORM_LOGIN_URLS, build_login_browser_command
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


QR_SELECTORS = {
    "dy": {
        "url": "https://www.douyin.com/",
        "selector": "xpath=//div[@id='animate_qrcode_container']//img",
        "selectors": [
            "xpath=//div[@id='animate_qrcode_container']//img",
            "xpath=//div[contains(@id,'qrcode') or contains(@class,'qrcode') or contains(@class,'qr-code')]//img",
            "img[src^='data:image']",
            "img[src*='qrcode'], img[src*='qrCode'], img[src*='qr_code'], img[src*='qr']",
            "canvas",
        ],
        "containers": [
            "xpath=//div[@id='animate_qrcode_container']",
            "xpath=//div[contains(@id,'qrcode') or contains(@class,'qrcode') or contains(@class,'qr-code')]",
        ],
        "prepare": "douyin",
    },
    "ks": {
        "url": "https://www.kuaishou.com/?isHome=1",
        "selector": "xpath=//div[contains(@class,'qrcode-img')]//img",
        "selectors": [
            "xpath=//div[contains(@class,'qrcode-img')]//img",
            "xpath=//div[contains(@class,'qrcode') or contains(@class,'qr-code')]//img",
            "img[src^='data:image']",
            "img[src*='qrcode'], img[src*='qrCode'], img[src*='qr_code'], img[src*='qr']",
            "canvas",
        ],
        "containers": [
            "xpath=//div[contains(@class,'qrcode-img')]",
            "xpath=//div[contains(@class,'qrcode') or contains(@class,'qr-code')]",
        ],
        "prepare": "kuaishou",
    },
    "xhs": {
        "url": "https://www.xiaohongshu.com/explore",
        "selector": "xpath=//img[@class='qrcode-img']",
        "selectors": [
            "xpath=//img[contains(@class,'qrcode-img')]",
            "xpath=//div[contains(@class,'qrcode')]//img",
            "img[src^='data:image']",
            "img[src*='qrcode'], img[src*='qrCode'], img[src*='qr_code'], img[src*='qr']",
            "canvas",
        ],
        "containers": [
            "xpath=//div[contains(@class,'qrcode')]",
            "xpath=//div[contains(@class,'login-container')]//div[contains(@class,'left')]",
        ],
        "prepare": "xhs",
    },
}


@dataclass
class LoginSessionHandle:
    platform: str
    playwright: Playwright
    context: BrowserContext
    page: Page
    profile_path: str
    created_at: datetime


ACTIVE_LOGIN_SESSIONS: dict[int, LoginSessionHandle] = {}


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
            headless=headless,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(timeout)
        await _install_stealth_hooks(page)
        await page.goto(QR_SELECTORS[platform]["url"], wait_until="domcontentloaded", timeout=timeout)
        await _prepare_login_page(platform, page, timeout)

        if await _is_logged_in(platform, context, page):
            await _close_context(playwright, context)
            return {
                "ok": True,
                "already_logged_in": True,
                "platform": platform,
                "platform_label": PLATFORM_LABELS.get(platform, platform),
                "qr_image": "",
                "login_url": PLATFORM_LOGIN_URLS[platform],
                "profile_path": command["profile_path"],
                "message": "当前 Profile 已经登录，不需要重新扫码。",
            }

        qr_image = await _find_login_qrcode(page, platform, timeout)
        if not qr_image:
            details = await _describe_qrcode_failure(page, platform)
            await _close_context(playwright, context)
            return _failure(platform, command, f"没有在页面中找到登录二维码，请使用登录窗口兜底。{details}")
        ACTIVE_LOGIN_SESSIONS[int(session_id)] = LoginSessionHandle(
            platform=platform,
            playwright=playwright,
            context=context,
            page=page,
            profile_path=command["profile_path"],
            created_at=datetime.now(timezone.utc),
        )
        return {
            "ok": True,
            "platform": platform,
            "platform_label": PLATFORM_LABELS.get(platform, platform),
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
        success = await _is_logged_in(handle.platform, handle.context, handle.page)
        if success:
            await close_qrcode_login_session(session_id)
            return {"active": False, "success": True, "message": "登录成功，Profile 已保存。"}
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


async def _prepare_login_page(platform: str, page: Page, timeout: int) -> None:
    if platform == "dy":
        try:
            await page.wait_for_selector("xpath=//div[@id='login-panel-new']", timeout=min(timeout, 8000))
        except Exception:
            await _click_first_visible(
                page,
                [
                    "xpath=//p[normalize-space() = '登录']",
                    "xpath=//*[self::button or self::div or self::span or self::p][normalize-space() = '登录']",
                    "button:has-text('登录')",
                    "text=登录",
                ],
                timeout=5000,
            )
        await _click_first_visible(page, ["text=扫码登录", "text=二维码登录"], timeout=1200)
    elif platform == "ks":
        await _click_first_visible(
            page,
            [
                "xpath=//p[normalize-space()='登录']",
                "xpath=//*[self::button or self::div or self::span or self::p][normalize-space()='登录']",
                "button:has-text('登录')",
                "text=登录",
            ],
            timeout=5000,
        )
        await _click_first_visible(page, ["text=扫码登录", "text=二维码登录"], timeout=1200)
    elif platform == "xhs":
        try:
            await page.wait_for_selector(QR_SELECTORS[platform]["selector"], timeout=5000)
        except Exception:
            await _click_first_visible(
                page,
                [
                    "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button",
                    "button:has-text('登录')",
                    "text=登录",
                ],
                timeout=5000,
            )
        await _click_first_visible(page, ["text=扫码登录", "text=二维码登录"], timeout=1200)


async def _install_stealth_hooks(page: Page) -> None:
    try:
        await page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """
        )
    except Exception:
        pass


async def _click_first_visible(page: Page, selectors: list[str], timeout: int = 3000) -> bool:
    deadline = max(500, timeout)
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if await locator.count() and await locator.is_visible(timeout=min(deadline, 1000)):
                await locator.click(timeout=deadline)
                await page.wait_for_timeout(600)
                return True
        except Exception:
            continue
    return False


async def _find_login_qrcode(page: Page, platform: str, timeout: int) -> str:
    config = QR_SELECTORS[platform]
    selectors = list(dict.fromkeys([config["selector"], *config.get("selectors", [])]))
    per_selector_timeout = max(1200, min(5000, int(timeout / max(1, len(selectors)))))
    for selector in selectors:
        image = await _image_from_selector(page, selector, per_selector_timeout)
        if image:
            return image
    for selector in config.get("containers", []):
        image = await _screenshot_from_selector(page, selector, per_selector_timeout)
        if image:
            return image
    return ""


async def _image_from_selector(page: Page, selector: str, timeout: int = 2000) -> str:
    try:
        element = await page.wait_for_selector(selector, state="visible", timeout=timeout)
        if not element:
            return ""
        image = await _image_from_element(page, element)
        if image:
            return image
        return await _element_screenshot_data_url(element)
    except Exception:
        return ""


async def _screenshot_from_selector(page: Page, selector: str, timeout: int = 2000) -> str:
    try:
        element = await page.wait_for_selector(selector, state="visible", timeout=timeout)
        if not element:
            return ""
        return await _element_screenshot_data_url(element)
    except Exception:
        return ""


async def _image_from_element(page: Page, element: Any) -> str:
    for source in await _image_sources(page, element):
        data_url = await _image_source_to_data_url(page, source)
        if data_url:
            return data_url
    return ""


async def _image_sources(page: Page, element: Any) -> list[str]:
    sources: list[str] = []
    for attr in ("src", "currentSrc", "data-src"):
        try:
            value = await element.get_attribute(attr)
            if value:
                sources.append(value)
        except Exception:
            continue
    try:
        value = await element.evaluate(
            """el => {
                const style = window.getComputedStyle(el);
                const bg = style && style.backgroundImage ? style.backgroundImage : '';
                const match = bg.match(/url\\(["']?(.*?)["']?\\)/);
                return el.currentSrc || el.src || el.getAttribute('src') || el.getAttribute('data-src') || (match ? match[1] : '');
            }"""
        )
        if value:
            sources.append(str(value))
    except Exception:
        pass
    cleaned = []
    for source in sources:
        source = str(source).strip()
        if source and source not in cleaned and not source.startswith("JSHandle@"):
            cleaned.append(source)
    return cleaned


async def _image_source_to_data_url(page: Page, source: str) -> str:
    if not source:
        return ""
    if source.startswith("data:image"):
        return source
    if source.startswith("blob:"):
        return await _blob_to_data_url(page, source)
    source = await _absolute_url(page, source)
    if source.startswith("http://") or source.startswith("https://"):
        return await _fetch_image_data_url(page, source)
    return ""


async def _absolute_url(page: Page, source: str) -> str:
    if source.startswith("//"):
        return "https:" + source
    if source.startswith("http://") or source.startswith("https://") or source.startswith("data:image") or source.startswith("blob:"):
        return source
    try:
        return await page.evaluate("(src) => new URL(src, location.href).toString()", source)
    except Exception:
        return source


async def _blob_to_data_url(page: Page, source: str) -> str:
    try:
        return await page.evaluate(
            """async (src) => {
                const response = await fetch(src);
                const blob = await response.blob();
                const buffer = await blob.arrayBuffer();
                let binary = '';
                const bytes = new Uint8Array(buffer);
                for (let i = 0; i < bytes.byteLength; i += 1) binary += String.fromCharCode(bytes[i]);
                return `data:${blob.type || 'image/png'};base64,${btoa(binary)}`;
            }""",
            source,
        )
    except Exception:
        return ""


async def _fetch_image_data_url(page: Page, source: str) -> str:
    try:
        user_agent = await page.evaluate("() => navigator.userAgent")
    except Exception:
        user_agent = utils.get_user_agent()
    try:
        response = await page.context.request.get(source, headers={"User-Agent": user_agent})
        if response.ok:
            content_type = response.headers.get("content-type") or "image/png"
            return _bytes_to_data_url(await response.body(), content_type)
    except Exception:
        pass
    try:
        async with make_async_client(follow_redirects=True) as client:
            response = await client.get(source, headers={"User-Agent": user_agent})
            if response.status_code == 200:
                return _bytes_to_data_url(response.content, response.headers.get("content-type") or "image/png")
    except Exception:
        pass
    return ""


async def _element_screenshot_data_url(element: Any) -> str:
    try:
        screenshot = await element.screenshot()
        return _bytes_to_data_url(screenshot, "image/png")
    except Exception:
        return ""


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
    return str(os.environ.get("MONITOR_LOGIN_QR_HEADLESS") or "false").lower() not in {"0", "false", "no"}


def _failure(platform: str, command: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "qr_image": "",
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


async def _is_logged_in(platform: str, context: BrowserContext, page: Page) -> bool:
    cookies = await context.cookies()
    cookie_dict = {item.get("name"): item.get("value") for item in cookies}
    if platform == "dy":
        if cookie_dict.get("LOGIN_STATUS") == "1":
            return True
        for candidate in context.pages:
            try:
                local_storage = await candidate.evaluate("() => window.localStorage")
                if local_storage.get("HasUserLogin") == "1":
                    return True
            except Exception:
                continue
    if platform == "ks":
        return bool(cookie_dict.get("passToken"))
    if platform == "xhs":
        if cookie_dict.get("web_session"):
            return True
        try:
            return await page.is_visible("xpath=//a[contains(@href, '/user/profile/')]//span[text()='我']", timeout=500)
        except Exception:
            return False
    return False


def _session_expired(handle: LoginSessionHandle) -> bool:
    ttl_seconds = int(os.environ.get("MONITOR_LOGIN_QR_TTL_SECONDS") or 180)
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
