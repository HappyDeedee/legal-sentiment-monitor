from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import re

from media_platform.douyin.client import DouYinClient
from media_platform.kuaishou.client import KuaiShouClient
from media_platform.xhs.client import XiaoHongShuClient
from playwright.async_api import Page, async_playwright

from tools import utils
from tools.browser_launcher import BrowserLauncher

from .database import get_social_account, update_social_account_check_state
from .mediacrawler_login import call_mediacrawler_check_login_state, get_mediacrawler_login_capability
from .normalizer import PLATFORM_LABELS
from .security import customer_safe_text, redact_sensitive


COOKIE_DOMAINS = {
    "dy": ".douyin.com",
    "ks": ".kuaishou.com",
    "xhs": ".xiaohongshu.com",
}

MEDIACRAWLER_CLIENT_CLASSES = {
    "dy": DouYinClient,
    "ks": KuaiShouClient,
    "xhs": XiaoHongShuClient,
}


async def check_social_account_login(account_id: int, timeout_ms: int = 15000, allow_draft: bool = False) -> dict[str, Any]:
    account = get_social_account(account_id, masked=False)
    if not account:
        raise ValueError("account not found")
    if account.get("is_draft") and not allow_draft:
        raise ValueError("draft account cannot be checked")
    platform = str(account.get("platform") or "")
    login_type = str(account.get("login_type") or "qrcode")
    platform_label = PLATFORM_LABELS.get(platform, platform)
    if login_type == "cookie":
        result = await _check_cookie_account(account, timeout_ms)
    else:
        result = await _check_profile_account(account, timeout_ms)
    ok = bool(result.get("ok"))
    message = str(result.get("message") or ("登录态有效" if ok else "登录态无效"))
    updated = update_social_account_check_state(
        int(account_id),
        ok=ok,
        message=message,
        status="active" if ok else "limited",
        identity=result.get("identity") if ok else None,
    )
    return {
        **result,
        "account_id": account_id,
        "account_name": account.get("name") or "",
        "platform": platform,
        "platform_label": platform_label,
        "login_type": login_type,
        "account": updated,
    }


async def _check_profile_account(account: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    platform = str(account.get("platform") or "")
    profile_path = Path(str(account.get("profile_path") or ""))
    if not str(profile_path).strip() or not profile_path.exists():
        return _result(False, "未找到该账号的网页登录态，请重新扫码登录。", "missing_profile")
    browser_path = _browser_path()
    capability = get_mediacrawler_login_capability(platform)
    playwright = None
    context = None
    try:
        playwright = await async_playwright().start()
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            executable_path=browser_path,
            accept_downloads=True,
            headless=True,
            viewport={"width": 1920, "height": 1080},
            user_agent=utils.get_user_agent(),
        )
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(timeout_ms)
        await page.goto(str(capability.get("login_url") or ""), wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_timeout(1200)
        login_baseline = await _login_baseline(platform, context)
        verified = await _verify_collectable_login(platform, context, page, timeout_ms, login_baseline)
        if verified.get("ok"):
            identity = await _extract_platform_identity(platform, page)
            return _result(True, "登录态有效，可供采集任务使用。", "valid", identity)
        verification = await _detect_simple_verification(page)
        if verification:
            return _result(False, verification, "needs_verification")
        if verified.get("status") == "client_check_failed":
            return _result(False, str(verified.get("message") or ""), "client_check_failed")
        return _result(False, "登录态无效或已失效，请重新扫码登录。", "invalid")
    except Exception as exc:
        return _result(False, _friendly_error(exc), "check_failed")
    finally:
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


async def _check_cookie_account(account: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    platform = str(account.get("platform") or "")
    cookies = str(account.get("cookies") or "").strip()
    if not cookies:
        return _result(False, "该账号未保存 Cookie，请先在账号详情中保存 Cookie。", "missing_cookie")
    browser_path = _browser_path()
    capability = get_mediacrawler_login_capability(platform)
    playwright = None
    browser = None
    context = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(executable_path=browser_path, headless=True)
        context = await browser.new_context(user_agent=utils.get_user_agent(), viewport={"width": 1920, "height": 1080})
        await context.add_cookies(_cookie_items(platform, cookies))
        page = await context.new_page()
        page.set_default_timeout(timeout_ms)
        await page.goto(str(capability.get("login_url") or ""), wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_timeout(1200)
        login_baseline = await _login_baseline(platform, context)
        verified = await _verify_collectable_login(platform, context, page, timeout_ms, login_baseline)
        if verified.get("ok"):
            identity = await _extract_platform_identity(platform, page)
            return _result(True, "Cookie 登录态有效，可供采集任务使用。", "valid", identity)
        verification = await _detect_simple_verification(page)
        if verification:
            return _result(False, verification, "needs_verification")
        if verified.get("status") == "client_check_failed":
            return _result(False, "Cookie 页面状态存在，但采集前验活未通过，请重新保存 Cookie 后再检测。", "client_check_failed")
        return _result(False, "Cookie 登录态无效或已失效，请重新保存 Cookie。", "invalid")
    except Exception as exc:
        return _result(False, _friendly_error(exc), "check_failed")
    finally:
        if context:
            try:
                await context.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        if playwright:
            try:
                await playwright.stop()
            except Exception:
                pass


def _cookie_items(platform: str, cookie_str: str) -> list[dict[str, str]]:
    domain = COOKIE_DOMAINS.get(platform) or ""
    result = []
    for name, value in utils.convert_str_cookie_to_dict(cookie_str).items():
        result.append({"name": name, "value": value, "domain": domain, "path": "/"})
    return result


async def _verify_collectable_login(
    platform: str,
    context,
    page: Page,
    timeout_ms: int,
    login_baseline: str = "",
) -> dict[str, Any]:
    login_state_ok = await call_mediacrawler_check_login_state(platform, context, page, login_baseline)
    client_check = await _check_mediacrawler_client_pong(platform, context, page, timeout_ms)
    if client_check.get("ok"):
        return {"ok": True, "status": "valid", "message": "登录态有效，可供采集任务使用。"}
    if login_state_ok:
        message = str(client_check.get("message") or "")
        detail = f" {message}" if message else ""
        return {
            "ok": False,
            "status": "client_check_failed",
            "message": customer_safe_text(f"平台页面显示已登录，但采集前验活未通过，请重新登录后再检测。{detail}"),
        }
    return {"ok": False, "status": "invalid", "message": str(client_check.get("message") or "")}


async def _check_mediacrawler_client_pong(platform: str, context, page: Page, timeout_ms: int) -> dict[str, Any]:
    client_class = MEDIACRAWLER_CLIENT_CLASSES.get(platform)
    if not client_class:
        return {"ok": False, "message": "暂不支持该平台账号验活。"}
    try:
        client = await _build_mediacrawler_client(platform, context, page)
        timeout_seconds = max(3.0, min(20.0, float(timeout_ms or 15000) / 1000))
        if platform == "dy":
            ok = await asyncio.wait_for(client.pong(browser_context=context), timeout=timeout_seconds)
        else:
            ok = await asyncio.wait_for(client.pong(), timeout=timeout_seconds)
        return {"ok": bool(ok), "message": "" if ok else "采集前验活未通过。"}
    except Exception as exc:
        return {"ok": False, "message": _friendly_error(exc)}


async def _build_mediacrawler_client(platform: str, context, page: Page):
    cookie_urls = _client_cookie_urls(platform)
    cookie_str, cookie_dict = await utils.convert_browser_context_cookies(context, urls=cookie_urls)
    user_agent = await _page_user_agent(page)
    if platform == "dy":
        return DouYinClient(
            headers={
                "User-Agent": user_agent,
                "Cookie": cookie_str,
                "Host": "www.douyin.com",
                "Origin": "https://www.douyin.com/",
                "Referer": "https://www.douyin.com/",
                "Content-Type": "application/json;charset=UTF-8",
            },
            playwright_page=page,
            cookie_dict=cookie_dict,
        )
    if platform == "ks":
        return KuaiShouClient(
            headers={
                "User-Agent": user_agent,
                "Cookie": cookie_str,
                "Origin": "https://www.kuaishou.com",
                "Referer": "https://www.kuaishou.com",
                "Content-Type": "application/json;charset=UTF-8",
            },
            playwright_page=page,
            cookie_dict=cookie_dict,
        )
    if platform == "xhs":
        login_url = str(get_mediacrawler_login_capability(platform).get("login_url") or "https://www.xiaohongshu.com")
        return XiaoHongShuClient(
            headers={
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json;charset=UTF-8",
                "origin": login_url,
                "pragma": "no-cache",
                "referer": f"{login_url}/",
                "user-agent": user_agent,
                "Cookie": cookie_str,
            },
            playwright_page=page,
            cookie_dict=cookie_dict,
        )
    raise ValueError("unsupported platform")


def _client_cookie_urls(platform: str) -> list[str]:
    if platform == "dy":
        return [
            "https://douyin.com",
            "https://www.douyin.com",
            "https://creator.douyin.com",
            "https://douhot.douyin.com",
            "https://live.douyin.com",
        ]
    if platform == "ks":
        return ["https://www.kuaishou.com"]
    if platform == "xhs":
        return [str(get_mediacrawler_login_capability(platform).get("login_url") or "https://www.xiaohongshu.com")]
    return []


async def _page_user_agent(page: Page) -> str:
    try:
        return str(await page.evaluate("() => navigator.userAgent") or utils.get_user_agent())
    except Exception:
        return utils.get_user_agent()


async def _login_baseline(platform: str, context) -> str:
    session_cookie = str((get_mediacrawler_login_capability(platform).get("login_state") or {}).get("session_cookie") or "")
    if not session_cookie:
        return ""
    cookies = await context.cookies()
    for cookie in cookies:
        if cookie.get("name") == session_cookie:
            return str(cookie.get("value") or "")
    return ""


async def _detect_simple_verification(page) -> str:
    try:
        text = await page.locator("body").inner_text(timeout=1000)
    except Exception:
        text = ""
    compact = " ".join(str(text or "").split())
    markers = [
        ("滑块", "平台要求完成滑块验证，请在账号详情中重新发起登录并按页面提示处理。"),
        ("短信验证码", "平台要求完成短信验证码，请按页面提示处理后重新检测。"),
        ("请输入验证码", "平台要求完成验证码，请按页面提示处理后重新检测。"),
        ("安全验证", "平台要求完成安全验证，请按页面提示处理后重新检测。"),
        ("captcha", "平台要求完成安全验证，请按页面提示处理后重新检测。"),
        ("verify", "平台要求完成安全验证，请按页面提示处理后重新检测。"),
    ]
    lower = compact.lower()
    for marker, message in markers:
        if marker.lower() in lower:
            return message
    return ""


def _browser_path() -> str:
    launcher = BrowserLauncher()
    browser_paths = launcher.detect_browser_paths()
    if not browser_paths:
        raise ValueError("未找到 Chrome 或 Edge 浏览器")
    return browser_paths[0]


def _friendly_error(exc: Exception) -> str:
    text = redact_sensitive(str(exc))
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if "locked" in text.lower() or "being used" in text.lower() or "ProcessSingleton" in text:
        return "该账号登录态正在被其他浏览器会话占用，请关闭相关窗口后重试。"
    if "Target page, context or browser has been closed" in text:
        return "浏览器会话被关闭，请重新检测。"
    return customer_safe_text(f"{type(exc).__name__}: {first or '登录态检测失败'}")


async def _extract_platform_identity(platform: str, page: Page) -> dict[str, str]:
    if platform == "dy":
        return await _extract_douyin_identity(page)
    if platform == "xhs":
        return await _extract_xhs_identity(page)
    if platform == "ks":
        return await _extract_kuaishou_identity(page)
    return _empty_identity()


async def _extract_douyin_identity(page: Page) -> dict[str, str]:
    try:
        await page.wait_for_timeout(1200)
        data = await page.evaluate(
            """() => {
              const clean = value => String(value || '').trim().replace(/\\s+/g, ' ');
              const links = Array.from(document.querySelectorAll('a[href*="/user/self"]')).map(a => ({
                text: clean(a.innerText || a.textContent || a.getAttribute('aria-label') || ''),
                href: a.href
              }));
              const blocked = new Set(['', '我的', '我的预约', '发布视频/图文', '视频管理', '作品数据', '创作者中心', '创作者学习中心']);
              const nickname = (links.find(item => item.text && !blocked.has(item.text) && !item.text.startsWith('我的')) || {}).text || '';
              const homeUrl = (links.find(item => item.href) || {}).href || '';
              const avatar = (Array.from(document.querySelectorAll('img')).map(img => img.currentSrc || img.src || '')
                .find(src => /avatar|aweme-avatar/i.test(src)) || '');
              return { nickname, homeUrl, avatar };
            }"""
        )
    except Exception:
        data = {}
    nickname = _clean_identity_text(data.get("nickname") if isinstance(data, dict) else "")
    avatar = _safe_identity_url(data.get("avatar") if isinstance(data, dict) else "")
    home_url = _safe_identity_url(data.get("homeUrl") if isinstance(data, dict) else "")
    return {
        "platform_account_id": "",
        "platform_account_name": nickname,
        "platform_avatar_url": avatar,
        "platform_home_url": home_url,
    }


async def _extract_xhs_identity(page: Page) -> dict[str, str]:
    try:
        data = await page.evaluate(
            """() => {
              const clean = value => String(value || '').trim().replace(/\\s+/g, ' ');
              const links = Array.from(document.querySelectorAll('a[href*="/user/profile/"]')).map(a => ({
                text: clean(a.innerText || a.textContent || a.getAttribute('aria-label') || ''),
                href: a.href
              }));
              const own = links.find(item => item.text === '我') || links.find(item => /channel_type=web_profile_board|from=me|self/i.test(item.href)) || {};
              const avatar = (Array.from(document.querySelectorAll('img')).map(img => img.currentSrc || img.src || '')
                .find(src => /avatar/i.test(src) && !/author-avatar/i.test(src)) || '');
              return { text: own.text || '', homeUrl: own.href || '', avatar };
            }"""
        )
    except Exception:
        data = {}
    home_url = _safe_identity_url(data.get("homeUrl") if isinstance(data, dict) else "")
    account_id = _extract_path_id(home_url, r"/user/profile/([^?/#]+)")
    nickname = _clean_identity_text(data.get("text") if isinstance(data, dict) else "")
    if nickname == "我":
        nickname = ""
    return {
        "platform_account_id": account_id,
        "platform_account_name": nickname,
        "platform_avatar_url": _safe_identity_url(data.get("avatar") if isinstance(data, dict) else ""),
        "platform_home_url": home_url,
    }


async def _extract_kuaishou_identity(page: Page) -> dict[str, str]:
    try:
        data = await page.evaluate(
            """() => {
              const clean = value => String(value || '').trim().replace(/\\s+/g, ' ');
              const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                text: clean(a.innerText || a.textContent || a.getAttribute('aria-label') || ''),
                href: a.href
              })).filter(item => /profile|user|my|me/i.test(item.href));
              const candidate = links.find(item => item.text && !['我的', '个人主页'].includes(item.text)) || links[0] || {};
              const avatar = (Array.from(document.querySelectorAll('img')).map(img => img.currentSrc || img.src || '')
                .find(src => /avatar|head/i.test(src)) || '');
              return { nickname: candidate.text || '', homeUrl: candidate.href || '', avatar };
            }"""
        )
    except Exception:
        data = {}
    return {
        "platform_account_id": _extract_path_id(str((data or {}).get("homeUrl") or ""), r"/user/([^?/#]+)"),
        "platform_account_name": _clean_identity_text((data or {}).get("nickname") or ""),
        "platform_avatar_url": _safe_identity_url((data or {}).get("avatar") or ""),
        "platform_home_url": _safe_identity_url((data or {}).get("homeUrl") or ""),
    }


def _extract_path_id(url: str, pattern: str) -> str:
    match = re.search(pattern, str(url or ""))
    return match.group(1)[:240] if match else ""


def _clean_identity_text(value: Any) -> str:
    return " ".join(str(value or "").split())[:240]


def _safe_identity_url(value: Any) -> str:
    url = str(value or "").strip()
    if not url.startswith(("http://", "https://")):
        return ""
    return redact_sensitive(url)[:1000]


def _empty_identity() -> dict[str, str]:
    return {
        "platform_account_id": "",
        "platform_account_name": "",
        "platform_avatar_url": "",
        "platform_home_url": "",
    }


def _result(ok: bool, message: str, status: str, identity: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": ok, "status": status, "message": customer_safe_text(message), "identity": identity or {}}
