from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.request import urlopen

from .browser_selection import (
    BrowserSelection,
    BrowserSelectionError,
    resolve_browser_selection,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BIND_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
LOCAL_BROWSER_HOST = "127.0.0.1"
MANUAL_BROWSER_INSTALL_COMMAND = "uv run playwright install chromium"
DEFAULT_BROWSER_INSTALL_TIMEOUT_SECONDS = 300.0
WINDOWS_LOCAL_LOGIN_DEFAULTS = {
    "MONITOR_BROWSER_COOKIE_SYNC_ENABLED": "true",
    "MONITOR_ALLOW_LOCAL_LOGIN_WINDOW": "true",
    "MONITOR_LOGIN_QR_HEADLESS": "false",
}


@dataclass(frozen=True)
class LaunchPlan:
    bind_host: str
    port: int
    probe_url: str
    browser_url: str
    command: list[str]


def build_launch_plan(bind_host: str | None, port: int, browser_url: str | None = None) -> LaunchPlan:
    normalized_host = _normalize_host(bind_host)
    normalized_port = int(port)
    probe_host = _probe_host(normalized_host)
    browser_override = (browser_url or "").strip()
    browser_destination = browser_override or _build_url(probe_host, normalized_port, "/monitor")
    return LaunchPlan(
        bind_host=normalized_host,
        port=normalized_port,
        probe_url=_build_url(probe_host, normalized_port, "/api/health"),
        browser_url=browser_destination,
        command=[sys.executable, "-m", "uvicorn", "api.main:app", "--host", normalized_host, "--port", str(normalized_port)],
    )


def start_oneclick(
    bind_host: str | None,
    port: int,
    browser_url: str | None = None,
    health_timeout_seconds: float = 45.0,
    *,
    foreground: bool = False,
) -> LaunchPlan:
    plan = build_launch_plan(bind_host, port, browser_url)
    env = apply_windows_local_login_defaults(os.environ) if os.name == "nt" else dict(os.environ)
    env["MONITOR_HOST"] = plan.bind_host
    env["MONITOR_PORT"] = str(plan.port)
    if browser_url:
        env["MONITOR_BROWSER_URL"] = browser_url
    process = subprocess.Popen(
        plan.command,
        cwd=ROOT,
        env=env,
        stdout=None if foreground else subprocess.DEVNULL,
        stderr=None if foreground else subprocess.DEVNULL,
        text=True,
        **_popen_kwargs(foreground=foreground),
    )
    try:
        _wait_for_health(plan.probe_url, process, health_timeout_seconds)
        webbrowser.open(plan.browser_url)
        if foreground:
            try:
                process.wait()
            except KeyboardInterrupt:
                _terminate(process)
            if process.returncode not in {None, 0}:
                raise RuntimeError(f"service exited with code {process.returncode}")
        return plan
    except Exception:
        _terminate(process)
        raise


def apply_windows_local_login_defaults(env: Mapping[str, str]) -> dict[str, str]:
    prepared = dict(env)
    for key, value in WINDOWS_LOCAL_LOGIN_DEFAULTS.items():
        if not str(prepared.get(key) or "").strip():
            prepared[key] = value
    return prepared


def ensure_oneclick_browser(install_timeout_seconds: float | None = None) -> Path:
    try:
        selection = _resolve_local_browser_selection()
    except BrowserSelectionError as exc:
        if exc.reason != "playwright_missing":
            raise RuntimeError(str(exc)) from exc
    except Exception as exc:
        raise RuntimeError(
            f"检查 Playwright Chromium 失败，请执行：{MANUAL_BROWSER_INSTALL_COMMAND}"
        ) from exc
    else:
        return selection.executable_path

    print(
        "未检测到可用的本机浏览器，正在自动下载安装 Playwright Chromium。",
        flush=True,
    )

    try:
        timeout_seconds = _positive_timeout(
            install_timeout_seconds,
            "MONITOR_BROWSER_INSTALL_TIMEOUT_SECONDS",
            DEFAULT_BROWSER_INSTALL_TIMEOUT_SECONDS,
        )
        process = subprocess.Popen(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            cwd=ROOT,
        )
        try:
            returncode = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            _terminate(process)
            raise
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Playwright Chromium 安装超过 {timeout_seconds:g} 秒，请检查网络或代理后重新运行一键启动。"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"Playwright Chromium 安装失败，请检查环境后执行：{MANUAL_BROWSER_INSTALL_COMMAND}"
        ) from exc
    if returncode != 0:
        raise RuntimeError(
            f"Playwright Chromium 安装失败，请检查网络或代理后执行：{MANUAL_BROWSER_INSTALL_COMMAND}"
        )

    try:
        selection = _resolve_local_browser_selection()
    except BrowserSelectionError as exc:
        raise RuntimeError(
            f"安装后检查 Playwright Chromium 失败，请执行：{MANUAL_BROWSER_INSTALL_COMMAND}"
        ) from exc
    return selection.executable_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Windows one-click launcher for /monitor")
    parser.add_argument("--host", default=os.environ.get("MONITOR_HOST", DEFAULT_BIND_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MONITOR_PORT", DEFAULT_PORT)))
    parser.add_argument("--browser-url", default=os.environ.get("MONITOR_BROWSER_URL"))
    parser.add_argument("--health-timeout-seconds", type=float, default=float(os.environ.get("MONITOR_STARTUP_HEALTH_TIMEOUT_SECONDS", 45.0)))
    parser.add_argument(
        "--browser-install-timeout-seconds",
        type=float,
        default=float(
            os.environ.get(
                "MONITOR_BROWSER_INSTALL_TIMEOUT_SECONDS",
                DEFAULT_BROWSER_INSTALL_TIMEOUT_SECONDS,
            )
        ),
    )
    parser.add_argument("--browser-preflight-only", action="store_true")
    parser.add_argument("--foreground", action="store_true")
    args = parser.parse_args(argv)

    try:
        browser_path = ensure_oneclick_browser(args.browser_install_timeout_seconds)
        if args.browser_preflight_only:
            print(f"浏览器预检通过: {browser_path.name}")
            return 0
        plan = start_oneclick(
            args.host,
            args.port,
            args.browser_url,
            args.health_timeout_seconds,
            foreground=args.foreground,
        )
    except Exception as exc:
        print(f"启动失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"服务绑定: {plan.bind_host}:{plan.port}")
    print(f"健康检查: {plan.probe_url}")
    print(f"浏览器地址: {plan.browser_url}")
    return 0


def _playwright_chromium_executable_path() -> Path:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        return Path(playwright.chromium.executable_path).expanduser().resolve()


def _resolve_local_browser_selection() -> BrowserSelection:
    return resolve_browser_selection(
        _playwright_chromium_executable_path(),
        allow_system=True,
        persist=True,
    )


def _wait_for_health(probe_url: str, process: subprocess.Popen[str], health_timeout_seconds: float) -> None:
    deadline = time.monotonic() + health_timeout_seconds
    observed_process_id = 0
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"service exited early with code {process.returncode}")
        try:
            with urlopen(probe_url, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
                observed_process_id = int(payload.get("process_id") or 0)
                if payload.get("status") == "ok" and _service_process_matches(process.pid, observed_process_id):
                    return
        except Exception:
            time.sleep(0.5)
            continue
        time.sleep(0.5)
    if observed_process_id > 0:
        raise RuntimeError(
            f"service health process mismatch: launcher={process.pid}, service={observed_process_id}"
        )
    raise RuntimeError("service did not become healthy")


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _service_process_matches(root_pid: int, observed_pid: int) -> bool:
    if int(root_pid) == int(observed_pid):
        return True
    if os.name != "nt" or int(observed_pid) <= 0:
        return False
    try:
        from tools.browser_environment import windows_process_is_descendant

        return windows_process_is_descendant(int(root_pid), int(observed_pid))
    except Exception:
        return False


def _normalize_host(host: str | None) -> str:
    normalized = (host or DEFAULT_BIND_HOST).strip()
    return normalized or DEFAULT_BIND_HOST


def _probe_host(bind_host: str) -> str:
    return LOCAL_BROWSER_HOST if bind_host in {"", "0.0.0.0", "::"} else bind_host


def _build_url(host: str, port: int, path: str) -> str:
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{port}{path}"


def _positive_timeout(value: float | None, name: str, default: float) -> float:
    normalized = default if value is None else float(value)
    if normalized <= 0:
        raise RuntimeError(f"{name} 必须大于 0。")
    return normalized


def _popen_kwargs(*, foreground: bool = False) -> dict[str, object]:
    if os.name != "nt" or foreground:
        return {}
    creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return {"creationflags": creationflags} if creationflags else {}


if __name__ == "__main__":
    raise SystemExit(main())
