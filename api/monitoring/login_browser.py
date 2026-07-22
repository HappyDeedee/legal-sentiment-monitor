from __future__ import annotations

import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

from .login_state import record_login_window
from .mediacrawler_login import get_mediacrawler_login_capability
from .normalizer import PLATFORM_LABELS
from .platform_status import PROFILE_DIRS, PROJECT_ROOT
from tools.browser_launcher import BrowserLauncher
from tools.browser_environment import BrowserEnvironmentPlan


logger = logging.getLogger(__name__)


class LoginBrowserProbeError(RuntimeError):
    def __init__(self, stage: str) -> None:
        self.stage = stage
        self.message = f"登录窗口状态检测超时（阶段：{stage}）。"
        super().__init__(self.message)


PLATFORM_LOGIN_URLS = {
    platform: get_mediacrawler_login_capability(platform)["login_url"]
    for platform in PROFILE_DIRS
}


def build_login_browser_command(platform: str, debug_port: int | None = None) -> dict[str, Any]:
    if platform not in PROFILE_DIRS:
        raise ValueError("unsupported platform")
    launcher = BrowserLauncher()
    browser_paths = launcher.detect_browser_paths()
    if not browser_paths:
        raise ValueError("未找到 Chrome 或 Edge 浏览器")
    profile_path = _profile_path(platform)
    profile_path.mkdir(parents=True, exist_ok=True)
    port = int(debug_port or os.environ.get(f"MONITOR_LOGIN_DEBUG_PORT_{platform.upper()}") or _default_port(platform))
    return {
        "browser_path": browser_paths[0],
        "profile_path": str(profile_path),
        "debug_port": port,
        "login_url": PLATFORM_LOGIN_URLS[platform],
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "login_capability_source": "平台采集服务",
    }


def build_managed_login_browser_command(
    plan: BrowserEnvironmentPlan,
    debug_port: int | None = None,
) -> dict[str, Any]:
    platform = plan.platform
    if platform not in PROFILE_DIRS:
        raise ValueError("unsupported platform")
    port = int(debug_port or os.environ.get(f"MONITOR_LOGIN_DEBUG_PORT_{platform.upper()}") or _default_port(platform))
    return {
        "browser_path": plan.browser_executable_path,
        "profile_path": plan.profile_path,
        "profile_key": plan.profile_key,
        "debug_port": port,
        "login_url": PLATFORM_LOGIN_URLS[platform],
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "login_capability_source": "平台采集服务",
        "account_id": plan.account_id,
        "proxy_id": plan.proxy_id,
        "proxy_url": plan.proxy_url,
        "user_agent": plan.user_agent,
        "timezone": plan.timezone,
        "locale": plan.locale,
        "accept_language": plan.accept_language,
        "screen_width": plan.screen_width,
        "screen_height": plan.screen_height,
        "viewport_width": plan.viewport_width,
        "viewport_height": plan.viewport_height,
        "device_scale_factor": plan.device_scale_factor,
        "is_mobile": plan.is_mobile,
        "has_touch": plan.has_touch,
        "_browser_environment_plan": plan,
    }


def open_login_browser(platform: str) -> dict[str, Any]:
    command = build_login_browser_command(platform)
    return open_login_browser_with_command(command)


def open_login_browser_with_command(command: dict[str, Any]) -> dict[str, Any]:
    Path(command["profile_path"]).mkdir(parents=True, exist_ok=True)
    args = [
        command["browser_path"],
        f"--remote-debugging-port={command['debug_port']}",
        "--remote-debugging-address=127.0.0.1",
        "--no-first-run",
        "--no-default-browser-check",
        "--start-maximized",
        f"--user-data-dir={command['profile_path']}",
        command["login_url"],
    ]
    if command.get("user_agent"):
        args.insert(-1, f"--user-agent={command['user_agent']}")
    if command.get("locale"):
        args.insert(-1, f"--lang={command['locale']}")
    if command.get("viewport_width") and command.get("viewport_height"):
        args.insert(-1, f"--window-size={int(command['viewport_width'])},{int(command['viewport_height'])}")
    if command.get("device_scale_factor"):
        args.insert(-1, f"--force-device-scale-factor={float(command['device_scale_factor'])}")
    if command.get("proxy_url"):
        args.insert(-1, f"--proxy-server={command['proxy_url']}")
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    record_login_window(
        command["platform"],
        process.pid,
        command["debug_port"],
        command["profile_path"],
        str(command.get("profile_key") or ""),
    )
    public_command = {
        key: value
        for key, value in command.items()
        if key
        not in {
            "_browser_environment_plan",
            "browser_path",
            "proxy_url",
            "user_agent",
            "timezone",
            "locale",
            "accept_language",
            "screen_width",
            "screen_height",
            "viewport_width",
            "viewport_height",
            "device_scale_factor",
            "is_mobile",
            "has_touch",
        }
    }
    return {
        **public_command,
        "pid": process.pid,
        "message": f"已打开{command['platform_label']}登录窗口，请完成登录后关闭该窗口，再回后台刷新状态并运行采集",
    }


async def probe_login_browser_session(
    platform: str,
    debug_port: int,
    *,
    expected_pid: int,
    close_when_logged_in: bool = False,
    timeout_ms: int = 4000,
) -> dict[str, Any]:
    if platform not in PLATFORM_LOGIN_URLS:
        raise ValueError("unsupported platform")
    port = int(debug_port)
    if not 1 <= port <= 65535:
        raise ValueError("invalid debug port")
    process_id = int(expected_pid)
    if process_id <= 0:
        raise ValueError("invalid browser process")

    stage_state = {"stage": "启动浏览器检测组件"}
    playwright = await _run_login_browser_step(
        async_playwright().start(),
        stage_state["stage"],
        platform,
        timeout_ms,
    )
    session = None
    try:
        stage_state["stage"] = "连接登录窗口"
        browser = await _run_login_browser_step(
            playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}",
                timeout=max(1000, int(timeout_ms)),
            ),
            stage_state["stage"],
            platform,
            timeout_ms,
        )
        stage_state["stage"] = "校验登录窗口进程"
        session = await _run_login_browser_step(
            browser.new_browser_cdp_session(),
            stage_state["stage"],
            platform,
            timeout_ms,
        )
        process_matched = await _run_login_browser_step(
            _browser_process_matches(session, process_id),
            stage_state["stage"],
            platform,
            timeout_ms,
        )
        if not process_matched:
            return {
                "connected": True,
                "process_matched": False,
                "logged_in": False,
                "close_requested": False,
            }
        stage_state["stage"] = "定位平台登录页"
        page = _login_browser_page(browser.contexts, platform)
        if page is None:
            return {
                "connected": True,
                "process_matched": True,
                "logged_in": False,
                "close_requested": False,
            }
        page.set_default_timeout(max(1000, int(timeout_ms)))
        from .login_qrcode import _is_logged_in

        stage_state["stage"] = "检测平台登录状态"
        logged_in = bool(
            await _run_login_browser_step(
                _is_logged_in(platform, page.context, page),
                stage_state["stage"],
                platform,
                timeout_ms,
            )
        )
        close_requested = False
        if logged_in and close_when_logged_in:
            stage_state["stage"] = "关闭已登录窗口"
            try:
                await _run_login_browser_step(
                    session.send("Browser.close"),
                    stage_state["stage"],
                    platform,
                    timeout_ms,
                )
                close_requested = True
            except LoginBrowserProbeError:
                raise
            except Exception:
                close_requested = not browser.is_connected()
        return {
            "connected": True,
            "process_matched": True,
            "logged_in": logged_in,
            "close_requested": close_requested,
        }
    finally:
        if session is not None:
            await _bounded_login_browser_cleanup(session.detach())
        await _bounded_login_browser_cleanup(playwright.stop())


async def close_login_browser_session(
    platform: str,
    debug_port: int,
    *,
    expected_pid: int,
    timeout_ms: int = 4000,
) -> dict[str, bool]:
    """Close only the visible login browser whose CDP process matches our record."""

    if platform not in PLATFORM_LOGIN_URLS:
        raise ValueError("unsupported platform")
    port = int(debug_port)
    if not 1 <= port <= 65535:
        raise ValueError("invalid debug port")
    process_id = int(expected_pid)
    if process_id <= 0:
        raise ValueError("invalid browser process")

    playwright = await _run_login_browser_step(
        async_playwright().start(),
        "启动浏览器检测组件",
        platform,
        timeout_ms,
    )
    session = None
    try:
        browser = await _run_login_browser_step(
            playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{port}",
                timeout=max(1000, int(timeout_ms)),
            ),
            "连接登录窗口",
            platform,
            timeout_ms,
        )
        session = await _run_login_browser_step(
            browser.new_browser_cdp_session(),
            "校验登录窗口进程",
            platform,
            timeout_ms,
        )
        process_matched = await _run_login_browser_step(
            _browser_process_matches(session, process_id),
            "校验登录窗口进程",
            platform,
            timeout_ms,
        )
        if not process_matched:
            return {
                "connected": True,
                "process_matched": False,
                "logged_in": False,
                "close_requested": False,
            }
        try:
            await _run_login_browser_step(
                session.send("Browser.close"),
                "关闭登录窗口",
                platform,
                timeout_ms,
            )
            close_requested = True
        except LoginBrowserProbeError:
            raise
        except Exception:
            close_requested = not browser.is_connected()
        return {
            "connected": True,
            "process_matched": True,
            "logged_in": False,
            "close_requested": close_requested,
        }
    finally:
        if session is not None:
            await _bounded_login_browser_cleanup(session.detach())
        await _bounded_login_browser_cleanup(playwright.stop())


def _login_browser_page(contexts: list[Any], platform: str):
    login_host = str(urlsplit(PLATFORM_LOGIN_URLS[platform]).hostname or "").lower()
    base_domain = ".".join(login_host.split(".")[-2:])
    pages = [page for context in contexts for page in context.pages if not page.is_closed()]
    for page in reversed(pages):
        host = str(urlsplit(str(page.url or "")).hostname or "").lower()
        if host == base_domain or host.endswith(f".{base_domain}"):
            return page
    return None


async def _browser_process_matches(session: Any, expected_pid: int) -> bool:
    try:
        result = await session.send("SystemInfo.getProcessInfo")
    except Exception:
        return False
    process_info = result.get("processInfo") if isinstance(result, dict) else None
    if not isinstance(process_info, list):
        return False
    for item in process_info:
        if not isinstance(item, dict) or str(item.get("type") or "").lower() != "browser":
            continue
        try:
            return int(item.get("id")) == int(expected_pid)
        except (TypeError, ValueError):
            return False
    return False


async def _run_login_browser_step(
    awaitable: Any,
    stage: str,
    platform: str,
    timeout_ms: int,
) -> Any:
    logger.info("login_browser_probe_stage platform=%s stage=%s", platform, stage)
    task = asyncio.ensure_future(awaitable)
    timeout_seconds = _login_browser_step_timeout_seconds(timeout_ms)
    try:
        done, _ = await asyncio.wait({task}, timeout=timeout_seconds)
        if done:
            return task.result()
        task.cancel()
        task.add_done_callback(_consume_login_browser_task_result)
        raise LoginBrowserProbeError(stage)
    except asyncio.CancelledError:
        task.cancel()
        task.add_done_callback(_consume_login_browser_task_result)
        raise


def _login_browser_step_timeout_seconds(timeout_ms: int) -> float:
    override = str(os.environ.get("MONITOR_LOGIN_BROWSER_PROBE_STEP_TIMEOUT_SECONDS") or "").strip()
    try:
        value = float(override) if override else float(timeout_ms) / 1000 + 1.0
    except (TypeError, ValueError):
        value = float(timeout_ms) / 1000 + 1.0
    return max(0.05, min(30.0, value))


async def _bounded_login_browser_cleanup(awaitable: Any) -> None:
    task = asyncio.ensure_future(awaitable)
    done, _ = await asyncio.wait({task}, timeout=_login_browser_cleanup_timeout_seconds())
    if done:
        try:
            task.result()
        except Exception:
            pass
        return
    task.cancel()
    task.add_done_callback(_consume_login_browser_task_result)


def _login_browser_cleanup_timeout_seconds() -> float:
    try:
        return max(
            0.05,
            min(
                30.0,
                float(os.environ.get("MONITOR_LOGIN_BROWSER_CLEANUP_TIMEOUT_SECONDS") or "5"),
            ),
        )
    except (TypeError, ValueError):
        return 5.0


def _consume_login_browser_task_result(task: asyncio.Future[Any]) -> None:
    try:
        task.result()
    except BaseException:
        pass


def _profile_path(platform: str) -> Path:
    browser_data = Path(os.environ.get("MONITOR_BROWSER_DATA_DIR") or PROJECT_ROOT / "browser_data").resolve()
    return browser_data / PROFILE_DIRS[platform]


def _default_port(platform: str) -> int:
    return {"dy": 9323, "ks": 9324, "xhs": 9325}[platform]
