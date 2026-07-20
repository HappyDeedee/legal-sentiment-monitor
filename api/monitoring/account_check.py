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
from tools.browser_environment import (
    BrowserEnvironmentError,
    browser_environment_failure_result,
    launch_managed_browser_context,
    verify_managed_page,
)
from tools.browser_launcher import BrowserLauncher

from .account_identity import AccountIdentityError
from .browser_environment_provider import (
    persist_account_browser_environment_result,
    resolve_account_browser_environment,
)
from .database import (
    complete_social_account_identity_login,
    get_conn,
    get_proxy_profile,
    get_social_account,
    prepare_social_account_identity_login,
    update_social_account_check_state,
)
from .mediacrawler_login import call_mediacrawler_check_login_state, get_mediacrawler_login_capability
from .normalizer import PLATFORM_LABELS
from .security import customer_safe_text, redact_sensitive
from .account_environment import account_profile_environment
from .cookie_material import deserialize_cookie_material, to_playwright_cookie_items
from .profile_promotion import recover_profile_promotions


MEDIACRAWLER_CLIENT_CLASSES = {
    "dy": DouYinClient,
    "ks": KuaiShouClient,
    "xhs": XiaoHongShuClient,
}


async def check_social_account_login(
    account_id: int,
    timeout_ms: int = 15000,
    allow_draft: bool = False,
    identity_prepared: bool = False,
    actor_id: int | None = None,
) -> dict[str, Any]:
    await asyncio.to_thread(recover_profile_promotions, account_id)
    account = get_social_account(account_id, masked=False)
    if not account:
        raise ValueError("account not found")
    if account.get("is_draft") and not allow_draft:
        raise ValueError("draft account cannot be checked")
    platform = str(account.get("platform") or "")
    login_type = str(account.get("login_type") or "qrcode")
    platform_label = PLATFORM_LABELS.get(platform, platform)
    if login_type == "cookie":
        trigger_source = "cookie_validation"
    elif identity_prepared and allow_draft:
        trigger_source = "qrcode_login"
    else:
        trigger_source = "profile_validation"
    prepare_social_account_identity_login(
        account_id,
        trigger_source=trigger_source,
        user_id=actor_id,
        allow_prepared_validation=identity_prepared,
    )
    account = get_social_account(account_id, masked=False) or account
    try:
        if login_type == "cookie" and int(account.get("profile_runtime_version") or 0) < 1:
            result = await _check_cookie_account(account, timeout_ms)
        else:
            result = await _check_profile_account(account, timeout_ms)
        provider_plan = result.pop("_browser_environment_plan", None)
        provider_result = result.pop("_browser_environment_result", None)
        result.pop("_browser_session_closed", None)
        if provider_plan is not None or provider_result is not None:
            if provider_plan is None or provider_result is None:
                raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "direct_result")
            persist_account_browser_environment_result(account_id, provider_plan, provider_result)
            if not provider_result.ok:
                result = {
                    **result,
                    "ok": False,
                    "status": provider_result.reason,
                    "message": "浏览器账号环境校验未通过，请重试或重新登录。",
                }
    except Exception:
        complete_social_account_identity_login(
            account_id,
            ok=False,
            trigger_source=trigger_source,
            failure_reason="account_check_failed",
            user_id=actor_id,
        )
        raise
    ok = bool(result.get("ok"))
    message = str(result.get("message") or ("登录态有效" if ok else "登录态无效"))
    complete_social_account_identity_login(
        account_id,
        ok=ok,
        trigger_source=trigger_source,
        lock_reason=(
            "cookie_validation_success"
            if login_type == "cookie"
            else (
                "qrcode_login_success"
                if trigger_source == "qrcode_login"
                else "profile_validation_success"
            )
        ),
        failure_reason=str(result.get("status") or message),
        user_id=actor_id,
    )
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
    profile_path = Path(str(account_profile_environment(account).get("runtime_path") or ""))
    if not str(profile_path).strip() or not profile_path.exists():
        legacy_hint = _legacy_profile_path_hint(account, profile_path)
        if legacy_hint:
            return _result(False, legacy_hint, "missing_profile")
        return _result(False, "未找到该账号的网页登录态，请重新扫码登录。", "missing_profile")
    capability = get_mediacrawler_login_capability(platform)
    playwright = None
    context = None
    plan = None
    provider_result = None
    result: dict[str, Any] | None = None
    session_closed = False
    try:
        playwright = await async_playwright().start()
        plan = _resolve_account_plan(
            account,
            action="login_check",
            trigger_source="profile_validation",
            launch_mode="persistent_launch",
            playwright_executable_path=str(playwright.chromium.executable_path),
        )
        session = await launch_managed_browser_context(playwright, plan)
        context = session.context
        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(timeout_ms)
        await page.goto(str(capability.get("login_url") or ""), wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_timeout(1200)
        provider_result = await verify_managed_page(context, page)
        if provider_result is None or not provider_result.ok:
            result = _result(False, "浏览器账号环境校验未通过，请重新登录。", "provider_mismatch")
            return {
                **result,
                "_browser_environment_plan": plan,
                "_browser_environment_result": provider_result,
                "_browser_session_closed": False,
            }
        login_baseline = await _login_baseline(platform, context)
        verified = await _verify_collectable_login(platform, context, page, timeout_ms, login_baseline)
        if verified.get("ok"):
            identity = await _extract_platform_identity(platform, page)
            result = _result(True, "登录态有效，可供采集任务使用。", "valid", identity)
        else:
            verification = await _detect_simple_verification(page)
            if verification:
                result = _result(False, verification, "needs_verification")
            elif verified.get("status") == "client_check_failed":
                result = _result(False, str(verified.get("message") or ""), "client_check_failed")
            else:
                result = _result(False, "登录态无效或已失效，请重新扫码登录。", "invalid")
    except BrowserEnvironmentError as exc:
        if plan is None:
            raise
        provider_result = getattr(exc, "browser_environment_result", None) or browser_environment_failure_result(
            plan,
            exc.reason,
            proxy_effect="failed" if plan.proxy_policy == "account_bound" else "not_applicable",
        )
        result = _result(False, "浏览器账号环境校验失败，请重试或重新登录。", exc.reason)
    except AccountIdentityError:
        raise
    except Exception as exc:
        if plan is not None:
            provider_result = browser_environment_failure_result(
                plan,
                "account_identity_provider_browser_crashed",
                proxy_effect="failed" if plan.proxy_policy == "account_bound" else "not_applicable",
            )
        result = _result(False, _friendly_error(exc), "check_failed")
    finally:
        if context:
            try:
                await context.close()
                session_closed = True
            except Exception:
                pass
        if playwright:
            try:
                await playwright.stop()
            except Exception:
                pass
    return {
        **(result or _result(False, "登录态检测失败。", "check_failed")),
        "_browser_environment_plan": plan,
        "_browser_environment_result": provider_result,
        "_browser_session_closed": session_closed,
    }


async def _check_cookie_account(account: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    platform = str(account.get("platform") or "")
    cookies = str(account.get("cookies") or "").strip()
    if not cookies:
        return _result(False, "该账号未保存 Cookie，请先在账号详情中保存 Cookie。", "missing_cookie")
    capability = get_mediacrawler_login_capability(platform)
    playwright = None
    browser = None
    context = None
    plan = None
    provider_result = None
    result: dict[str, Any] | None = None
    session_closed = False
    try:
        playwright = await async_playwright().start()
        plan = _resolve_account_plan(
            account,
            action="cookie_validation",
            trigger_source="cookie_validation",
            launch_mode="ephemeral_cookie_validation",
            playwright_executable_path=str(playwright.chromium.executable_path),
        )
        session = await launch_managed_browser_context(playwright, plan)
        browser = session.browser
        context = session.context
        await context.add_cookies(_cookie_items(platform, cookies))
        page = await context.new_page()
        page.set_default_timeout(timeout_ms)
        await page.goto(str(capability.get("login_url") or ""), wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_timeout(1200)
        provider_result = await verify_managed_page(context, page)
        if provider_result is None or not provider_result.ok:
            result = _result(False, "浏览器账号环境校验未通过，请重新保存 Cookie。", "provider_mismatch")
            return {
                **result,
                "_browser_environment_plan": plan,
                "_browser_environment_result": provider_result,
                "_browser_session_closed": False,
            }
        login_baseline = await _login_baseline(platform, context)
        verified = await _verify_collectable_login(platform, context, page, timeout_ms, login_baseline)
        if verified.get("ok"):
            identity = await _extract_platform_identity(platform, page)
            result = _result(True, "Cookie 登录态有效，可供采集任务使用。", "valid", identity)
        else:
            verification = await _detect_simple_verification(page)
            if verification:
                result = _result(False, verification, "needs_verification")
            elif verified.get("status") == "client_check_failed":
                result = _result(False, "Cookie 页面状态存在，但采集前验活未通过，请重新保存 Cookie 后再检测。", "client_check_failed")
            else:
                result = _result(False, "Cookie 登录态无效或已失效，请重新保存 Cookie。", "invalid")
    except BrowserEnvironmentError as exc:
        if plan is None:
            raise
        provider_result = getattr(exc, "browser_environment_result", None) or browser_environment_failure_result(
            plan,
            exc.reason,
            proxy_effect="failed" if plan.proxy_policy == "account_bound" else "not_applicable",
        )
        result = _result(False, "浏览器账号环境校验失败，请重试或重新保存 Cookie。", exc.reason)
    except AccountIdentityError:
        raise
    except Exception as exc:
        if plan is not None:
            provider_result = browser_environment_failure_result(
                plan,
                "account_identity_provider_browser_crashed",
                proxy_effect="failed" if plan.proxy_policy == "account_bound" else "not_applicable",
            )
        result = _result(False, _friendly_error(exc), "check_failed")
    finally:
        if context:
            try:
                await context.close()
                session_closed = True
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
    return {
        **(result or _result(False, "Cookie 登录态检测失败。", "check_failed")),
        "_browser_environment_plan": plan,
        "_browser_environment_result": provider_result,
        "_browser_session_closed": session_closed,
    }


def _resolve_account_plan(
    account: dict[str, Any],
    *,
    action: str,
    trigger_source: str,
    launch_mode: str,
    playwright_executable_path: str,
):
    proxy = get_proxy_profile(int(account["proxy_id"]), masked=False) if account.get("proxy_id") else None
    return resolve_account_browser_environment(
        account,
        action=action,
        trigger_source=trigger_source,
        headless=True,
        launch_mode=launch_mode,
        proxy=proxy,
        playwright_executable_path=playwright_executable_path,
    )


def _cookie_items(platform: str, cookie_str: str) -> list[dict[str, Any]]:
    return to_playwright_cookie_items(deserialize_cookie_material(platform, cookie_str))


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


def _legacy_profile_path_hint(account: dict[str, Any], runtime_path: Path) -> str:
    if str(account.get("platform") or "") != "xhs":
        return ""
    legacy_path_text = _raw_profile_path(int(account.get("id") or 0))
    if not legacy_path_text:
        return ""
    try:
        legacy_path = Path(legacy_path_text).resolve()
        current_path = runtime_path.resolve()
    except Exception:
        return ""
    if legacy_path == current_path or not legacy_path.exists():
        return ""
    return "该小红书账号存在旧版网页登录态目录，但当前账号环境需要使用新的 Profile，请重新扫码登录后再检测。"


def _raw_profile_path(account_id: int) -> str:
    if not account_id:
        return ""
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT profile_path FROM social_accounts WHERE id=?", (account_id,)).fetchone()
    except Exception:
        return ""
    return str(row["profile_path"] or "") if row else ""


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
