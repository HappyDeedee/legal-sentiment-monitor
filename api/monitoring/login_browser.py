from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .login_state import record_login_window
from .mediacrawler_login import get_mediacrawler_login_capability
from .normalizer import PLATFORM_LABELS
from .platform_status import PROFILE_DIRS, PROJECT_ROOT
from tools.browser_launcher import BrowserLauncher


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
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    record_login_window(command["platform"], process.pid, command["debug_port"], command["profile_path"])
    return {
        **command,
        "pid": process.pid,
        "message": f"已打开{command['platform_label']}登录窗口，请完成登录后关闭该窗口，再回后台刷新状态并运行采集",
    }


def _profile_path(platform: str) -> Path:
    browser_data = Path(os.environ.get("MONITOR_BROWSER_DATA_DIR") or PROJECT_ROOT / "browser_data").resolve()
    return browser_data / PROFILE_DIRS[platform]


def _default_port(platform: str) -> int:
    return {"dy": 9323, "ks": 9324, "xhs": 9325}[platform]
