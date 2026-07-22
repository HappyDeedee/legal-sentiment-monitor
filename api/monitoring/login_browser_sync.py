"""Feature-gated, exact-context browser Cookie acquisition for CR-112 C.2."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from playwright.async_api import async_playwright

from tools.browser_environment import (
    BrowserEnvironmentError,
    ManagedBrowserProcess,
    close_managed_browser_session,
    launch_managed_browser_context,
    managed_browser_cleanup_timeout_seconds,
    managed_browser_processes,
    prepare_managed_page,
    verify_managed_page,
)

from .account_check import (
    _client_cookie_urls,
    _detect_simple_verification,
    _extract_platform_identity,
    _login_baseline,
    _verify_collectable_login,
)
from .browser_environment_provider import resolve_account_browser_environment
from .account_identity import AccountIdentityError
from .cookie_material import CookieMaterialError, canonicalize_cookie_records
from .database import (
    bind_browser_sync_login_session,
    create_browser_sync_login_session,
    get_account_profile_promotion,
    get_login_session,
    get_proxy_profile,
    get_social_account,
    list_login_sessions,
    record_audit_log,
    update_login_session_status,
)
from .login_qrcode import _is_logged_in, close_qrcode_login_session
from .login_attempts import account_login_start_lock, supersede_account_login_attempts
from .login_status import (
    LOGIN_STATE_NEEDS_VERIFICATION,
    LOGIN_STATE_PLATFORM_ERROR,
    LOGIN_STATE_PREPARING,
    LOGIN_STATE_QRCODE_FAILED,
    LOGIN_STATE_TIMEOUT,
    LOGIN_STATE_WAITING_CONFIRM,
    PENDING_LOGIN_STATES,
    normalize_login_state,
)
from .mediacrawler_login import SUPPORTED_MONITOR_PLATFORMS, get_mediacrawler_login_capability
from .profile_promotion import (
    BrowserRunner,
    ProfilePromotionError,
    default_profile_browser_runner,
    profile_promotion_paths,
    promote_cookie_to_profile,
    reset_candidate_profile_for_cookie_injection,
)


COOKIE_SYNC_FLAG = "MONITOR_BROWSER_COOKIE_SYNC_ENABLED"
COOKIE_SYNC_TIMEOUT_ENV = "MONITOR_BROWSER_COOKIE_SYNC_TIMEOUT_SECONDS"
DEFAULT_COOKIE_SYNC_TIMEOUT_SECONDS = 600
MIN_COOKIE_SYNC_TIMEOUT_SECONDS = 60
MAX_COOKIE_SYNC_TIMEOUT_SECONDS = 1800
DEFAULT_BROWSER_SYNC_STAGE_TIMEOUT_SECONDS = 30.0
DEFAULT_BROWSER_SYNC_CLEANUP_TIMEOUT_SECONDS = 5.0


logger = logging.getLogger(__name__)


class BrowserSyncError(ProfilePromotionError):
    def __init__(self, reason: str, message: str = "") -> None:
        self.message = message or reason
        super().__init__(reason)


@dataclass
class BrowserSyncHandle:
    session_id: int
    account_id: int
    profile_key: str
    platform: str
    actor_id: int | None
    acquisition_generation: int
    created_at: datetime
    workspace_id: int = 1
    task: asyncio.Task[Any] | None = None
    playwright: Any | None = None
    context: Any | None = None
    page: Any | None = None
    promotion_id: int | None = None
    provider_resolution_id: str = ""
    browser_attempt_id: str = ""
    owned_processes: tuple[ManagedBrowserProcess, ...] = ()
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    ready_event: asyncio.Event = field(default_factory=asyncio.Event)
    finalized: bool = False
    stage: str = "创建浏览器同步会话"


ACTIVE_BROWSER_SYNC_SESSIONS: dict[int, BrowserSyncHandle] = {}


def browser_cookie_sync_enabled() -> bool:
    value = os.environ.get(COOKIE_SYNC_FLAG, "")
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def browser_cookie_sync_available() -> bool:
    return browser_cookie_sync_enabled() and os.name == "nt"


def browser_cookie_sync_timeout_seconds() -> int:
    try:
        value = int(os.environ.get(COOKIE_SYNC_TIMEOUT_ENV) or DEFAULT_COOKIE_SYNC_TIMEOUT_SECONDS)
    except (TypeError, ValueError):
        value = DEFAULT_COOKIE_SYNC_TIMEOUT_SECONDS
    return max(MIN_COOKIE_SYNC_TIMEOUT_SECONDS, min(MAX_COOKIE_SYNC_TIMEOUT_SECONDS, value))


async def start_browser_cookie_sync(
    account_id: int,
    actor_id: int | None,
    workspace_id: int,
) -> dict[str, Any]:
    account = _workspace_account(int(account_id), workspace_id)
    if not browser_cookie_sync_enabled():
        raise BrowserSyncError("browser_sync_disabled", "浏览器自动同步当前未启用。")
    if os.name != "nt":
        raise BrowserSyncError("browser_sync_unsupported_host", "浏览器自动同步当前仅支持 Windows 本机。")
    platform = str(account.get("platform") or "").strip().lower()
    if platform not in SUPPORTED_MONITOR_PLATFORMS:
        raise BrowserSyncError("browser_sync_platform_unsupported", "当前平台暂不支持浏览器自动同步。")
    profile_key = str(account.get("profile_key") or "").strip()
    if not profile_key:
        raise BrowserSyncError("account_profile_missing", "账号环境尚未准备完成。")
    async with account_login_start_lock(int(account_id)):
        return await _start_browser_cookie_sync_locked(account, actor_id, workspace_id)


async def _start_browser_cookie_sync_locked(
    account: dict[str, Any],
    actor_id: int | None,
    workspace_id: int,
) -> dict[str, Any]:
    account_id = int(account["id"])
    platform = str(account.get("platform") or "").strip().lower()
    profile_key = str(account.get("profile_key") or "").strip()
    await cancel_active_browser_cookie_syncs_for_account(account_id)
    for handle in ACTIVE_BROWSER_SYNC_SESSIONS.values():
        if handle.account_id == account_id and not handle.finalized:
            raise BrowserSyncError("browser_sync_account_busy", "旧浏览器登录仍在安全清理，请稍后重试。")
    await supersede_account_login_attempts(
        account_id,
        platform,
        profile_key=profile_key,
        profile_path=str(account.get("profile_path") or ""),
        new_method="browser",
        include_browser_sync=False,
    )

    session = create_browser_sync_login_session(account_id, actor_id)
    for superseded_session_id in session.pop("superseded_session_ids", []):
        await close_qrcode_login_session(int(superseded_session_id))
    session_id = int(session["id"])
    handle = BrowserSyncHandle(
        session_id=session_id,
        account_id=account_id,
        profile_key=profile_key,
        platform=platform,
        actor_id=actor_id,
        acquisition_generation=int(session.get("acquisition_generation") or 1),
        created_at=_parse_datetime(session.get("created_at")) or datetime.now(timezone.utc),
        workspace_id=int(workspace_id),
    )
    ACTIVE_BROWSER_SYNC_SESSIONS[session_id] = handle
    try:
        handle.task = asyncio.create_task(_run_browser_cookie_sync(handle))
    except Exception:
        ACTIVE_BROWSER_SYNC_SESSIONS.pop(session_id, None)
        _set_session_status(session_id, LOGIN_STATE_PLATFORM_ERROR, "浏览器同步任务未能启动。")
        raise BrowserSyncError("browser_sync_start_failed", "浏览器同步任务未能启动。")
    return browser_sync_session_view(session_id)


async def get_browser_cookie_sync_status(
    session_id: int,
    workspace_id: int,
    account_id: int | None = None,
) -> dict[str, Any]:
    session = get_login_session(int(session_id))
    if not session:
        raise BrowserSyncError("login_session_not_found", "登录会话不存在。")
    if str(session.get("cookie_source") or "") != "browser_sync":
        raise BrowserSyncError("browser_sync_session_mismatch", "登录会话不是浏览器同步会话。")
    if account_id is not None and int(session.get("account_id") or 0) != int(account_id):
        raise BrowserSyncError("browser_sync_session_mismatch", "登录会话与账号不匹配。")
    _workspace_account(int(session.get("account_id") or 0), workspace_id)
    return browser_sync_session_view(int(session_id))


async def cancel_browser_cookie_sync(
    session_id: int,
    workspace_id: int,
    account_id: int | None = None,
) -> dict[str, Any]:
    session = get_login_session(int(session_id))
    if not session:
        raise BrowserSyncError("login_session_not_found", "登录会话不存在。")
    if str(session.get("cookie_source") or "") != "browser_sync":
        raise BrowserSyncError("browser_sync_session_mismatch", "登录会话不是浏览器同步会话。")
    if account_id is not None and int(session.get("account_id") or 0) != int(account_id):
        raise BrowserSyncError("browser_sync_session_mismatch", "登录会话与账号不匹配。")
    _workspace_account(int(session.get("account_id") or 0), workspace_id)
    handle = ACTIVE_BROWSER_SYNC_SESSIONS.get(int(session_id))
    if handle and handle.task and not handle.task.done():
        handle.cancel_event.set()
        try:
            await asyncio.wait_for(asyncio.shield(handle.task), timeout=12)
        except asyncio.TimeoutError:
            _set_session_status(int(session_id), LOGIN_STATE_WAITING_CONFIRM, "取消请求已收到，正在安全完成登录态切换。")
    elif normalize_login_state(session.get("status")) in PENDING_LOGIN_STATES:
        _set_session_status(int(session_id), LOGIN_STATE_QRCODE_FAILED, "浏览器同步已取消。")
    return browser_sync_session_view(int(session_id))


async def cancel_active_browser_cookie_syncs_for_account(account_id: int) -> list[int]:
    """Request cancellation and wait for active browser-sync work to release the Profile."""

    handles = [
        handle
        for handle in ACTIVE_BROWSER_SYNC_SESSIONS.values()
        if handle.account_id == int(account_id) and not handle.finalized
    ]
    for handle in handles:
        handle.cancel_event.set()
    for handle in handles:
        if not handle.task or handle.task.done():
            continue
        try:
            await asyncio.wait_for(asyncio.shield(handle.task), timeout=12)
        except asyncio.TimeoutError:
            _set_session_status(
                handle.session_id,
                LOGIN_STATE_WAITING_CONFIRM,
                "正在安全结束旧浏览器登录，请稍后重试。",
            )
    return [handle.session_id for handle in handles]


def recover_browser_cookie_sync_sessions() -> list[int]:
    """Close pending browser-sync records left by a service restart."""

    recovered: list[int] = []
    for session in list_login_sessions(limit=500):
        session_id = int(session.get("id") or 0)
        if (
            not session_id
            or str(session.get("cookie_source") or "") != "browser_sync"
            or normalize_login_state(session.get("status")) not in PENDING_LOGIN_STATES
            or session_id in ACTIVE_BROWSER_SYNC_SESSIONS
        ):
            continue
        _set_session_status(session_id, LOGIN_STATE_PLATFORM_ERROR, "服务已重启，原浏览器同步会话已结束，请重新发起。")
        recovered.append(session_id)
    return recovered


def browser_sync_session_view(session_id: int) -> dict[str, Any]:
    session = get_login_session(int(session_id))
    if not session:
        raise BrowserSyncError("login_session_not_found", "登录会话不存在。")
    view = {
        key: session.get(key)
        for key in (
            "id",
            "account_id",
            "platform",
            "status",
            "message",
            "created_at",
            "updated_at",
            "expires_at",
            "cookie_source",
            "profile_promotion_id",
            "acquisition_generation",
            "provider_resolution_id",
            "browser_attempt_id",
        )
    }
    handle = ACTIVE_BROWSER_SYNC_SESSIONS.get(int(session_id))
    view["active"] = bool(handle and not handle.finalized and handle.task and not handle.task.done())
    view["browser_open"] = bool(handle and handle.context is not None and handle.page is not None)
    view["cancel_requested"] = bool(handle and handle.cancel_event.is_set())
    view["stage"] = str(handle.stage if handle else "")
    return view


async def _run_browser_cookie_sync(handle: BrowserSyncHandle) -> None:
    terminal_result = "failed"
    terminal_reason = "browser_sync_failed"
    try:
        account = _workspace_account(handle.account_id, handle.workspace_id)
        if str(account.get("profile_key") or "") != handle.profile_key:
            raise BrowserSyncError("browser_sync_account_changed", "账号环境已变化，请重新发起浏览器同步。")
        handle.playwright = await _run_browser_sync_stage(
            handle,
            "启动浏览器组件",
            "正在启动浏览器组件。",
            async_playwright().start(),
        )
        provider_plan = await _run_browser_sync_stage(
            handle,
            "解析账号浏览器环境",
            "正在解析账号浏览器环境。",
            asyncio.to_thread(_resolve_provider_plan, account, handle.playwright),
        )
        handle.provider_resolution_id = str(provider_plan.resolution_id)
        handle.browser_attempt_id = str(provider_plan.attempt_id)
        bound = await _run_browser_sync_stage(
            handle,
            "绑定账号登录会话",
            "正在绑定账号登录会话。",
            asyncio.to_thread(
                bind_browser_sync_login_session,
                handle.session_id,
                account_id=handle.account_id,
                profile_key=handle.profile_key,
                acquisition_generation=handle.acquisition_generation,
                provider_resolution_id=handle.provider_resolution_id,
                browser_attempt_id=handle.browser_attempt_id,
            ),
        )
        _assert_session_binding(handle, bound, provider_plan, require_promotion=False)
        runner = _build_browser_sync_runner(handle, provider_plan)
        await promote_cookie_to_profile(
            handle.account_id,
            None,
            cookie_source="browser_sync",
            login_session_id=handle.session_id,
            actor_id=handle.actor_id,
            acquisition_generation=handle.acquisition_generation,
            provider_plan=provider_plan,
            browser_runner=runner,
        )
        terminal_result = "success"
        terminal_reason = ""
    except asyncio.CancelledError:
        terminal_result = "interrupted"
        terminal_reason = "browser_sync_interrupted"
        _set_session_status(handle.session_id, LOGIN_STATE_PLATFORM_ERROR, "浏览器同步任务已中断。")
        raise
    except BrowserSyncError as exc:
        terminal_reason = exc.reason
        terminal_result = "cancelled" if "cancel" in exc.reason else "failed"
        _set_session_status(handle.session_id, _status_for_reason(exc.reason), exc.message)
    except ProfilePromotionError as exc:
        terminal_reason = exc.reason
        message = _message_for_reason(exc.reason)
        if exc.reason in {"profile_validation_stage_timeout", "profile_validation_cleanup_timeout"}:
            message = f"登录态保存超时（阶段：{handle.stage}），原登录态已保留，请重新发起。"
        _set_session_status(handle.session_id, _status_for_reason(exc.reason), message)
    except (BrowserEnvironmentError, AccountIdentityError) as exc:
        terminal_reason = str(getattr(exc, "reason", "browser_sync_failed"))
        _set_session_status(handle.session_id, LOGIN_STATE_PLATFORM_ERROR, _message_for_reason(getattr(exc, "reason", "browser_sync_failed")))
    except Exception:
        terminal_reason = "browser_sync_unexpected_failure"
        _set_session_status(
            handle.session_id,
            LOGIN_STATE_PLATFORM_ERROR,
            f"浏览器同步失败（阶段：{handle.stage}），请重新发起。",
        )
    finally:
        try:
            await _close_handle_browser(handle)
        except BrowserEnvironmentError as exc:
            terminal_result = "failed"
            terminal_reason = exc.reason
            _set_session_status(handle.session_id, LOGIN_STATE_PLATFORM_ERROR, "登录浏览器清理失败，请重新发起。")
        _record_browser_sync_terminal(handle, terminal_result, terminal_reason)
        handle.finalized = True
        ACTIVE_BROWSER_SYNC_SESSIONS.pop(handle.session_id, None)


def _resolve_provider_plan(account: Mapping[str, Any], playwright: Any):
    proxy = get_proxy_profile(int(account["proxy_id"]), masked=False) if account.get("proxy_id") else None
    return resolve_account_browser_environment(
        account,
        action="login_check",
        trigger_source="browser_cookie_sync",
        headless=False,
        launch_mode="persistent_launch",
        proxy=proxy,
        playwright_executable_path=str(playwright.chromium.executable_path),
    )


def _build_browser_sync_runner(handle: BrowserSyncHandle, provider_plan: Any) -> BrowserRunner:
    default_runner = default_profile_browser_runner(handle.platform, handle.playwright)
    phase = 0

    async def run(plan: Any, injected_records: Any) -> dict[str, Any]:
        nonlocal phase
        phase += 1
        if phase == 1 and injected_records is None:
            return await _acquire_and_inject_candidate(handle, plan, default_runner)
        if phase == 1:
            raise ProfilePromotionError("profile_cookie_capture_missing")
        _set_browser_sync_stage(
            handle,
            "复检活动 Profile",
            "登录态已切换，正在复检活动 Profile。",
            status=LOGIN_STATE_WAITING_CONFIRM,
        )
        return await default_runner(replace(plan, headless=True), injected_records)

    return run


async def _acquire_and_inject_candidate(handle: BrowserSyncHandle, plan: Any, default_runner: BrowserRunner) -> dict[str, Any]:
    _assert_live_binding(handle, plan, require_context=False)
    session = get_login_session(handle.session_id) or {}
    promotion_id = int(session.get("profile_promotion_id") or 0)
    promotion = get_account_profile_promotion(promotion_id)
    if not promotion:
        raise ProfilePromotionError("profile_promotion_session_mismatch")
    handle.promotion_id = promotion_id
    paths = profile_promotion_paths(
        account_id=handle.account_id,
        profile_key=handle.profile_key,
        promotion_id=promotion_id,
    )
    if Path(plan.profile_path).resolve() != paths.candidate.resolve():
        raise BrowserSyncError("browser_sync_profile_mismatch", "浏览器登录会话与候选 Profile 不一致。")
    acquisition_context = None
    acquisition_browser = None
    try:
        acquisition_plan = replace(plan, trigger_source="browser_sync_acquisition", headless=False)
        managed_session = await _run_browser_sync_stage(
            handle,
            "启动账号登录窗口",
            "正在启动账号登录窗口。",
            launch_managed_browser_context(handle.playwright, acquisition_plan),
        )
        acquisition_context = managed_session.context
        acquisition_browser = managed_session.browser
        handle.owned_processes = managed_browser_processes(acquisition_context)
        if os.name == "nt" and not handle.owned_processes:
            raise BrowserSyncError(
                "browser_sync_process_ownership_unavailable",
                "登录浏览器进程归属校验失败，请重新发起。",
            )
        page = acquisition_context.pages[0] if acquisition_context.pages else await _run_browser_sync_stage(
            handle,
            "创建平台登录页面",
            "正在创建平台登录页面。",
            acquisition_context.new_page(),
        )
        page.set_default_timeout(15000)
        await _run_browser_sync_stage(
            handle,
            "注入账号浏览器环境",
            "正在注入账号浏览器环境。",
            prepare_managed_page(acquisition_context, page),
        )
        await _run_browser_sync_stage(
            handle,
            "打开平台登录页",
            "正在打开平台登录页。",
            page.goto(str(get_mediacrawler_login_capability(handle.platform).get("login_url") or ""), wait_until="domcontentloaded", timeout=15000),
        )
        provider_result = await _run_browser_sync_stage(
            handle,
            "校验账号浏览器环境",
            "正在校验账号浏览器环境。",
            verify_managed_page(acquisition_context, page),
        )
        if provider_result is None or not provider_result.ok:
            raise BrowserSyncError(
                "account_identity_snapshot_mismatch",
                _browser_environment_mismatch_message(provider_result),
            )
        baseline = await _run_browser_sync_stage(
            handle,
            "读取已有登录态",
            "正在读取已有登录态。",
            _login_baseline(handle.platform, acquisition_context),
        )
        handle.context = acquisition_context
        handle.page = page
        handle.ready_event.set()
        handle.stage = "等待平台登录"
        _set_session_status(handle.session_id, LOGIN_STATE_WAITING_CONFIRM, "登录窗口已打开，请在窗口中完成平台登录。")
        deadline = time.monotonic() + browser_cookie_sync_timeout_seconds()
        identity: dict[str, Any] = {}
        while True:
            _require_browser_sync_waiting(handle, acquisition_context, page, deadline)
            logged_in = await _run_browser_sync_waiting_probe(
                handle,
                _is_logged_in(handle.platform, acquisition_context, page, baseline),
                "检测平台登录状态",
            )
            if logged_in is None:
                await asyncio.sleep(0.8)
                continue
            if logged_in:
                verified = await _run_browser_sync_waiting_probe(
                    handle,
                    _verify_collectable_login(handle.platform, acquisition_context, page, 15000, baseline),
                    "校验平台登录状态",
                )
                if verified is None:
                    await asyncio.sleep(0.8)
                    continue
                if verified.get("ok"):
                    captured_identity = await _run_browser_sync_waiting_probe(
                        handle,
                        _extract_platform_identity(handle.platform, page),
                        "读取平台账号身份",
                    )
                    if captured_identity is None:
                        await asyncio.sleep(0.8)
                        continue
                    identity = captured_identity
                    break
                _set_session_status(handle.session_id, LOGIN_STATE_NEEDS_VERIFICATION, "平台登录已变化，正在等待完成平台验证。")
            else:
                verification_message = await _detect_simple_verification(page)
                if verification_message:
                    _set_session_status(handle.session_id, LOGIN_STATE_NEEDS_VERIFICATION, verification_message)
                else:
                    _set_session_status(handle.session_id, LOGIN_STATE_WAITING_CONFIRM, "请在浏览器窗口中完成登录，系统会自动确认。")
            await asyncio.sleep(0.8)
        _assert_live_binding(handle, plan, expected_context=acquisition_context)
        _set_browser_sync_stage(
            handle,
            "保存平台登录态",
            "平台登录已确认，正在保存账号登录状态。",
            status=LOGIN_STATE_WAITING_CONFIRM,
        )
        raw_cookies = await _run_browser_sync_probe(
            acquisition_context.cookies(_client_cookie_urls(handle.platform)),
            "读取平台 Cookie",
        )
        records = canonicalize_cookie_records(handle.platform, _playwright_cookie_records(raw_cookies))
    finally:
        owned_processes = handle.owned_processes
        handle.context = None
        handle.page = None
        handle.owned_processes = ()
        await _close_context_and_browser(acquisition_context, acquisition_browser, owned_processes)
    if handle.cancel_event.is_set():
        raise BrowserSyncError("browser_sync_cancelled", "浏览器同步已取消。")
    _assert_live_binding(handle, plan, require_context=False)
    reset_candidate_profile_for_cookie_injection(paths, promotion)
    _set_browser_sync_stage(
        handle,
        "验证候选 Profile",
        "Cookie 已读取，正在验证候选 Profile。",
        status=LOGIN_STATE_WAITING_CONFIRM,
    )
    candidate_result = await default_runner(replace(plan, headless=True), records)
    if handle.cancel_event.is_set():
        raise BrowserSyncError("browser_sync_cancelled", "浏览器同步已取消。")
    if candidate_result.get("ok") is not True:
        return candidate_result
    return {**candidate_result, "identity": identity, "cookie_records": records}


def _require_browser_sync_waiting(
    handle: BrowserSyncHandle,
    context: Any,
    page: Any,
    deadline: float,
) -> None:
    if handle.cancel_event.is_set():
        raise BrowserSyncError("browser_sync_cancelled", "浏览器同步已取消。")
    if page.is_closed() or not context.pages:
        raise BrowserSyncError("browser_sync_browser_closed", "登录窗口已关闭，浏览器同步未完成。")
    if time.monotonic() >= deadline:
        raise BrowserSyncError("browser_sync_timeout", "浏览器登录等待超时，请重新发起。")


def _playwright_cookie_records(raw_cookies: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_cookies, list):
        raise CookieMaterialError("cookie_payload_invalid", "records")
    records: list[dict[str, Any]] = []
    for raw in raw_cookies:
        if not isinstance(raw, Mapping):
            raise CookieMaterialError("cookie_payload_invalid", "records")
        if raw.get("partitionKey") is not None or raw.get("partition_key") is not None:
            raise CookieMaterialError("cookie_attribute_unsupported", "partition_key")
        name = raw.get("name")
        if not isinstance(name, str) or not name or any(char in name for char in ("\x00", "\r", "\n")):
            continue
        domain = str(raw.get("domain") or "")
        item: dict[str, Any] = {
            "name": name,
            "value": raw.get("value"),
            "domain": domain,
            "path": raw.get("path") or "/",
            "http_only": raw.get("httpOnly", False),
            "secure": raw.get("secure", False),
            "same_site": raw.get("sameSite") or "Lax",
            "host_only": not domain.startswith("."),
        }
        if raw.get("expires") is not None and float(raw.get("expires")) >= 0:
            item["expires"] = raw.get("expires")
        records.append(item)
    return records


def _assert_session_binding(
    handle: BrowserSyncHandle,
    session: Mapping[str, Any],
    plan: Any,
    *,
    require_promotion: bool = True,
) -> None:
    session_promotion_id = int(session.get("profile_promotion_id") or 0)
    if (
        int(session.get("account_id") or 0) != handle.account_id
        or str(session.get("profile_key") or "") != handle.profile_key
        or str(session.get("platform") or "") != handle.platform
        or int(session.get("acquisition_generation") or 0) != handle.acquisition_generation
        or str(session.get("provider_resolution_id") or "") != handle.provider_resolution_id
        or str(session.get("browser_attempt_id") or "") != handle.browser_attempt_id
        or str(session.get("cookie_source") or "") != "browser_sync"
        or (require_promotion and not session_promotion_id)
        or (handle.promotion_id is not None and session_promotion_id != int(handle.promotion_id))
        or int(plan.account_id) != handle.account_id
        or str(plan.profile_key) != handle.profile_key
        or str(plan.platform) != handle.platform
        or str(plan.resolution_id) != handle.provider_resolution_id
        or str(plan.attempt_id) != handle.browser_attempt_id
    ):
        raise BrowserSyncError("browser_sync_binding_mismatch", "浏览器登录会话与账号环境不一致。")


def _assert_live_binding(
    handle: BrowserSyncHandle,
    plan: Any,
    *,
    require_context: bool = True,
    expected_context: Any | None = None,
) -> None:
    session = get_login_session(handle.session_id)
    if not session:
        raise BrowserSyncError("browser_sync_session_stale", "浏览器登录会话已失效。")
    if ACTIVE_BROWSER_SYNC_SESSIONS.get(handle.session_id) is not handle or handle.finalized:
        raise BrowserSyncError("browser_sync_session_stale", "浏览器登录会话已失效。")
    if require_context and (handle.context is None or handle.page is None or handle.page.is_closed()):
        raise BrowserSyncError("browser_sync_context_closed", "浏览器登录窗口已关闭。")
    if expected_context is not None and (
        handle.context is not expected_context
        or handle.page is None
        or getattr(handle.page, "context", None) is not expected_context
    ):
        raise BrowserSyncError("browser_sync_context_mismatch", "浏览器登录上下文已变化。")
    _assert_session_binding(handle, session, plan)


async def _close_handle_browser(handle: BrowserSyncHandle) -> None:
    owned_processes = handle.owned_processes
    handle.owned_processes = ()
    cleanup_error: BrowserEnvironmentError | None = None
    try:
        await _close_context_and_browser(handle.context, None, owned_processes)
    except BrowserEnvironmentError as exc:
        cleanup_error = exc
    finally:
        handle.context = None
        handle.page = None
        if handle.playwright is not None:
            await _bounded_browser_sync_cleanup(handle.playwright.stop())
            handle.playwright = None
    if cleanup_error is not None:
        raise cleanup_error


async def _close_context_and_browser(
    context: Any,
    browser: Any,
    owned_processes: tuple[ManagedBrowserProcess, ...] = (),
) -> None:
    await close_managed_browser_session(context, browser, owned_processes)


async def _run_browser_sync_stage(
    handle: BrowserSyncHandle,
    stage: str,
    message: str,
    awaitable: Any,
) -> Any:
    _set_browser_sync_stage(handle, stage, message)
    return await _run_browser_sync_probe(awaitable, stage)


async def _run_browser_sync_probe(awaitable: Any, stage: str) -> Any:
    task = asyncio.ensure_future(awaitable)
    try:
        done, _ = await asyncio.wait({task}, timeout=_browser_sync_stage_timeout_seconds())
        if done:
            return task.result()
        await _cancel_and_drain_browser_sync_task(task)
        raise BrowserSyncError(
            "browser_sync_stage_timeout",
            f"浏览器登录超时（阶段：{stage}），请重新发起。",
        )
    except asyncio.CancelledError:
        await _cancel_and_drain_browser_sync_task(task)
        raise


async def _run_browser_sync_waiting_probe(
    handle: BrowserSyncHandle,
    awaitable: Any,
    stage: str,
) -> Any | None:
    try:
        return await _run_browser_sync_probe(awaitable, stage)
    except BrowserSyncError as exc:
        if exc.reason != "browser_sync_stage_timeout":
            raise
        _set_session_status(
            handle.session_id,
            LOGIN_STATE_WAITING_CONFIRM,
            f"平台响应较慢（阶段：{stage}），登录窗口保持打开，请继续完成登录。",
        )
        return None


def _set_browser_sync_stage(
    handle: BrowserSyncHandle,
    stage: str,
    message: str,
    *,
    status: str = LOGIN_STATE_PREPARING,
) -> None:
    handle.stage = stage
    logger.info(
        "browser_sync_stage session_id=%s account_id=%s platform=%s stage=%s",
        handle.session_id,
        handle.account_id,
        handle.platform,
        stage,
    )
    _set_session_status(handle.session_id, status, message)


def _browser_sync_stage_timeout_seconds() -> float:
    try:
        return max(
            0.05,
            min(
                120.0,
                float(
                    os.environ.get("MONITOR_BROWSER_SYNC_STAGE_TIMEOUT_SECONDS")
                    or DEFAULT_BROWSER_SYNC_STAGE_TIMEOUT_SECONDS
                ),
            ),
        )
    except (TypeError, ValueError):
        return DEFAULT_BROWSER_SYNC_STAGE_TIMEOUT_SECONDS


def _browser_sync_cleanup_timeout_seconds() -> float:
    try:
        return max(
            0.05,
            min(
                30.0,
                float(
                    os.environ.get("MONITOR_BROWSER_SYNC_CLEANUP_TIMEOUT_SECONDS")
                    or DEFAULT_BROWSER_SYNC_CLEANUP_TIMEOUT_SECONDS
                ),
            ),
        )
    except (TypeError, ValueError):
        return DEFAULT_BROWSER_SYNC_CLEANUP_TIMEOUT_SECONDS


def _browser_sync_managed_cleanup_timeout_seconds() -> float:
    return max(
        _browser_sync_cleanup_timeout_seconds(),
        managed_browser_cleanup_timeout_seconds(),
    )


async def _bounded_browser_sync_cleanup(awaitable: Any) -> None:
    task = asyncio.ensure_future(awaitable)
    done, _ = await asyncio.wait({task}, timeout=_browser_sync_cleanup_timeout_seconds())
    if done:
        try:
            task.result()
        except Exception:
            pass
        return
    task.cancel()
    task.add_done_callback(_consume_browser_sync_task_result)


async def _cancel_and_drain_browser_sync_task(task: asyncio.Task[Any]) -> None:
    task.cancel()
    done, _ = await asyncio.wait(
        {task},
        timeout=_browser_sync_managed_cleanup_timeout_seconds(),
    )
    if done:
        _consume_browser_sync_task_result(task)
    else:
        task.add_done_callback(_consume_browser_sync_task_result)


def _consume_browser_sync_task_result(task: asyncio.Future[Any]) -> None:
    try:
        task.result()
    except BaseException:
        pass


def _set_session_status(session_id: int, status: str, message: str) -> None:
    try:
        update_login_session_status(int(session_id), status, str(message)[:240])
    except Exception:
        pass


def _record_browser_sync_terminal(handle: BrowserSyncHandle, result: str, reason: str) -> None:
    try:
        record_audit_log(
            "browser_sync_session_finished",
            "social_account",
            handle.account_id,
            {
                "login_session_id": handle.session_id,
                "profile_promotion_id": handle.promotion_id,
                "profile_key_hash": hashlib.sha256(handle.profile_key.encode("utf-8")).hexdigest(),
                "platform": handle.platform,
                "acquisition_generation": handle.acquisition_generation,
                "provider_resolution_id": handle.provider_resolution_id,
                "browser_attempt_id": handle.browser_attempt_id,
                "result": str(result or "failed")[:32],
                "reason": str(reason or "")[:96],
            },
            user_id=handle.actor_id,
            workspace_id=handle.workspace_id,
        )
    except Exception:
        pass


def _status_for_reason(reason: str) -> str:
    value = str(reason or "")
    if "timeout" in value:
        return LOGIN_STATE_TIMEOUT
    if "cancel" in value or "closed" in value:
        return LOGIN_STATE_QRCODE_FAILED
    return LOGIN_STATE_PLATFORM_ERROR


def _workspace_account(account_id: int, workspace_id: int) -> dict[str, Any]:
    account = get_social_account(int(account_id), masked=False)
    if not account or int(account.get("workspace_id") or 0) != int(workspace_id):
        raise BrowserSyncError("account_not_found", "账号不存在。")
    return account


def _message_for_reason(reason: str) -> str:
    messages = {
        "profile_promotion_account_busy": "账号正在被其他登录或采集操作使用，请稍后重试。",
        "profile_promotion_cleanup_pending": "账号上一次登录环境仍在清理，请稍后重试。",
        "account_identity_snapshot_mismatch": "浏览器账号环境校验未通过，请重新登录。",
        "profile_candidate_validation_failed": "新登录态验证未通过，原登录态已保留。",
        "profile_active_recheck_failed": "新登录态切换后的验活未通过，原登录态已保留。",
        "profile_validation_stage_timeout": "登录态保存超时，原登录态已保留，请重新发起。",
        "profile_validation_cleanup_timeout": "登录态清理超时，原登录态已保留并停止继续使用，请重启服务后检查账号。",
        "profile_cookie_capture_missing": "没有取得有效 Cookie，原登录态已保留。",
        "profile_promotion_cancelled": "浏览器同步已取消，原登录态已保留。",
        "profile_promotion_failed": "登录态保存失败，原登录态已保留。",
    }
    return messages.get(str(reason or ""), "浏览器同步失败，请重新发起。")


def _browser_environment_mismatch_message(result: Any) -> str:
    labels = {
        "user_agent": "User-Agent",
        "timezone": "时区",
        "locale": "语言区域",
        "accept_language": "首选语言",
        "screen_width": "屏幕宽度",
        "screen_height": "屏幕高度",
        "viewport_width": "视口宽度",
        "viewport_height": "视口高度",
        "device_scale_factor": "显示缩放",
        "is_mobile": "移动设备类型",
        "has_touch": "触控能力",
    }
    snapshot = getattr(result, "snapshot", {}) if result is not None else {}
    evidence = snapshot.get("mismatch_evidence", []) if isinstance(snapshot, Mapping) else []
    fields: list[str] = []
    if isinstance(evidence, list):
        for item in evidence:
            field = str(item.get("field") or "") if isinstance(item, Mapping) else ""
            label = labels.get(field)
            if label and label not in fields:
                fields.append(label)
            if len(fields) >= 6:
                break
    detail = f"（不一致：{'、'.join(fields)}）" if fields else ""
    return f"浏览器账号环境校验未通过{detail}，登录窗口已关闭，请重新发起。"


def _parse_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
