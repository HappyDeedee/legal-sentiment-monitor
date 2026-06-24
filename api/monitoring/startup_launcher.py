from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BIND_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
LOCAL_BROWSER_HOST = "127.0.0.1"


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


def start_oneclick(bind_host: str | None, port: int, browser_url: str | None = None, health_timeout_seconds: float = 45.0) -> LaunchPlan:
    plan = build_launch_plan(bind_host, port, browser_url)
    env = os.environ.copy()
    env["MONITOR_HOST"] = plan.bind_host
    env["MONITOR_PORT"] = str(plan.port)
    if browser_url:
        env["MONITOR_BROWSER_URL"] = browser_url
    process = subprocess.Popen(
        plan.command,
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        **_popen_kwargs(),
    )
    try:
        _wait_for_health(plan.probe_url, process, health_timeout_seconds)
        webbrowser.open(plan.browser_url)
        return plan
    except Exception:
        _terminate(process)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Windows one-click launcher for /monitor")
    parser.add_argument("--host", default=os.environ.get("MONITOR_HOST", DEFAULT_BIND_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MONITOR_PORT", DEFAULT_PORT)))
    parser.add_argument("--browser-url", default=os.environ.get("MONITOR_BROWSER_URL"))
    parser.add_argument("--health-timeout-seconds", type=float, default=float(os.environ.get("MONITOR_STARTUP_HEALTH_TIMEOUT_SECONDS", 45.0)))
    args = parser.parse_args(argv)

    try:
        plan = start_oneclick(args.host, args.port, args.browser_url, args.health_timeout_seconds)
    except Exception as exc:
        print(f"启动失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"服务绑定: {plan.bind_host}:{plan.port}")
    print(f"健康检查: {plan.probe_url}")
    print(f"浏览器地址: {plan.browser_url}")
    return 0


def _wait_for_health(probe_url: str, process: subprocess.Popen[str], health_timeout_seconds: float) -> None:
    deadline = time.monotonic() + health_timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"service exited early with code {process.returncode}")
        try:
            with urlopen(probe_url, timeout=2) as response:
                if "ok" in response.read().decode("utf-8"):
                    return
        except Exception:
            time.sleep(0.5)
            continue
        time.sleep(0.5)
    raise RuntimeError("service did not become healthy")


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _normalize_host(host: str | None) -> str:
    normalized = (host or DEFAULT_BIND_HOST).strip()
    return normalized or DEFAULT_BIND_HOST


def _probe_host(bind_host: str) -> str:
    return LOCAL_BROWSER_HOST if bind_host in {"", "0.0.0.0", "::"} else bind_host


def _build_url(host: str, port: int, path: str) -> str:
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    return f"http://{host}:{port}{path}"


def _popen_kwargs() -> dict[str, object]:
    if os.name != "nt":
        return {}
    creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return {"creationflags": creationflags} if creationflags else {}


if __name__ == "__main__":
    raise SystemExit(main())
