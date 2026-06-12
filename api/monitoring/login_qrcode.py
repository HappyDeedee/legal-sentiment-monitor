from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from tools import utils

from .login_browser import PLATFORM_LOGIN_URLS, build_login_browser_command
from .normalizer import PLATFORM_LABELS
from .security import redact_sensitive


QR_SELECTORS = {
    "dy": {
        "url": "https://www.douyin.com/",
        "selector": "xpath=//div[@id='animate_qrcode_container']//img",
        "prepare": "douyin",
    },
    "ks": {
        "url": "https://www.kuaishou.com/",
        "selector": "xpath=//div[@class='qrcode-img']//img",
        "prepare": "kuaishou",
    },
    "xhs": {
        "url": "https://www.xiaohongshu.com/explore",
        "selector": "xpath=//img[@class='qrcode-img']",
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
    timeout = int(timeout_ms or os.environ.get("MONITOR_LOGIN_QR_TIMEOUT_MS") or 20000)
    headless = str(os.environ.get("MONITOR_LOGIN_QR_HEADLESS") or "true").lower() not in {"0", "false", "no"}
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
        await page.goto(QR_SELECTORS[platform]["url"], wait_until="domcontentloaded", timeout=timeout)
        await _prepare_login_page(platform, page, timeout)
        qr_image = await utils.find_login_qrcode(page, QR_SELECTORS[platform]["selector"])
        if not qr_image:
            await _close_context(playwright, context)
            return _failure(platform, command, "没有在页面中找到登录二维码，请使用登录窗口兜底。")
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
        return _failure(platform, command, f"{type(exc).__name__}: {redact_sensitive(str(exc))}")


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


async def _prepare_login_page(platform: str, page: Page, timeout: int) -> None:
    if platform == "dy":
        try:
            await page.wait_for_selector("xpath=//div[@id='login-panel-new']", timeout=min(timeout, 8000))
        except Exception:
            login_button = page.locator("xpath=//p[text() = '登录']").first
            if await login_button.count():
                await login_button.click(timeout=5000)
    elif platform == "ks":
        login_button = page.locator("xpath=//p[text()='登录']").first
        if await login_button.count():
            await login_button.click(timeout=5000)
    elif platform == "xhs":
        try:
            await page.wait_for_selector(QR_SELECTORS[platform]["selector"], timeout=5000)
        except Exception:
            login_button = page.locator("xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button").first
            if await login_button.count():
                await login_button.click(timeout=5000)


def _as_data_url(qr_image: str) -> str:
    if qr_image.startswith("data:image"):
        return qr_image
    return "data:image/png;base64," + qr_image


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
