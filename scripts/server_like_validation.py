from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run server-like validation for Legal Sentiment Monitor.")
    parser.add_argument("--data-dir", default="", help="Persistent validation data directory. Defaults to a temp dir.")
    parser.add_argument("--keep-data", action="store_true", help="Do not delete the temporary validation data directory.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve() if args.data_dir else Path(tempfile.mkdtemp(prefix="lsm-server-like-")).resolve()
    browser_dir = data_dir / "browser_data"
    account_profile_root = data_dir / "account_profiles"
    data_dir.mkdir(parents=True, exist_ok=True)
    browser_dir.mkdir(parents=True, exist_ok=True)
    account_profile_root.mkdir(parents=True, exist_ok=True)
    port = args.port or _free_port(args.host)
    base_url = f"http://{args.host}:{port}"
    email = "admin@example.com"
    password = "phase8-Admin-pass-123"

    env = os.environ.copy()
    env.update(
        {
            "MONITOR_HOST": args.host,
            "MONITOR_PORT": str(port),
            "MONITOR_DATA_DIR": str(data_dir),
            "MONITOR_BROWSER_DATA_DIR": str(browser_dir),
            "MONITOR_ACCOUNT_PROFILE_ROOT": str(account_profile_root),
            "MONITOR_ADMIN_EMAIL": email,
            "MONITOR_ADMIN_PASSWORD": password,
            "MONITOR_ADMIN_DISPLAY_NAME": "Phase 8 Admin",
            "MONITOR_LOGIN_QR_HEADLESS": "true",
            "MONITOR_ALLOW_LOCAL_LOGIN_WINDOW": "false",
            "MONITOR_CRAWLER_HEADLESS": "true",
            "MONITOR_DISABLE_SCHEDULER": "true",
            "MONITOR_SKIP_AI_API": "true",
        }
    )

    results: list[dict[str, Any]] = []
    process: subprocess.Popen[str] | None = None
    try:
        process = _start_service(env, args.host, port, data_dir / "uvicorn-1.log")
        _wait_for_health(base_url)
        _verify_monitor_page(base_url)
        jar = CookieJar()
        _login(base_url, jar, email, password)
        _record(results, "service_web_ui_reachable", True, "service started and /monitor returned HTML")
        _record(results, "admin_login", True, "bootstrap administrator logged in over HTTP")
        _assert_local_login_disabled(base_url, jar, results)
        account_ids = _create_same_platform_accounts(base_url, jar)
        _record(results, "same_platform_profiles_separate", account_ids[0] != account_ids[1], f"created accounts {account_ids}")
        _verify_profile_paths(data_dir, account_profile_root, account_ids, results)
        _verify_locks(env, account_ids[0], results)
        _stop_service(process)
        process = None
        process = _start_service(env, args.host, port, data_dir / "uvicorn-2.log")
        _wait_for_health(base_url)
        jar = CookieJar()
        _login(base_url, jar, email, password)
        accounts_after = _api(base_url, "GET", "/api/monitor/social-accounts", jar=jar)["accounts"]
        persisted_ids = {int(item["id"]) for item in accounts_after}
        _record(
            results,
            "profile_metadata_survives_restart",
            set(account_ids) <= persisted_ids,
            "social account profile metadata persisted after service restart",
        )
        _record(results, "local_chrome_not_required_for_validation", True, "validation used HTTP service and headless browser check only")
        _verify_headless_browser(results)
        print(json.dumps({"ok": all(item["ok"] for item in results), "data_dir": str(data_dir), "checks": results}, ensure_ascii=False, indent=2))
        return 0 if all(item["ok"] for item in results) else 1
    except Exception as exc:
        _record(results, "server_like_validation_exception", False, f"{type(exc).__name__}: {exc}")
        print(json.dumps({"ok": False, "data_dir": str(data_dir), "checks": results}, ensure_ascii=False, indent=2))
        return 1
    finally:
        if process:
            _stop_service(process)
        if not args.data_dir and not args.keep_data:
            shutil.rmtree(data_dir, ignore_errors=True)


def _start_service(env: dict[str, str], host: str, port: int, log_path: Path) -> subprocess.Popen[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8", errors="ignore")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", host, "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process


def _stop_service(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)


def _wait_for_health(base_url: str, timeout: float = 45.0) -> None:
    deadline = time.time() + timeout
    last_error = ""
    while time.time() < deadline:
        try:
            data = _request_json(base_url + "/api/health")
            if data.get("status") == "ok":
                return
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.5)
    raise RuntimeError(f"service did not become healthy: {last_error}")


def _verify_monitor_page(base_url: str) -> None:
    html = _request_text(base_url + "/monitor")
    if "律所舆情监控系统" not in html and "Legal Sentiment" not in html:
        raise RuntimeError("/monitor did not return the monitor console HTML")


def _login(base_url: str, jar: "CookieJar", email: str, password: str) -> None:
    response = _api(base_url, "POST", "/api/auth/login", {"email": email, "password": password}, jar)
    if response.get("user", {}).get("role") != "administrator":
        raise RuntimeError("administrator login did not return administrator role")


def _assert_local_login_disabled(base_url: str, jar: "CookieJar", results: list[dict[str, Any]]) -> None:
    capabilities = _api(base_url, "GET", "/api/monitor/platform-login-capabilities", jar=jar)["capabilities"]
    local_disabled = all(item.get("local_login_window_allowed") is False for item in capabilities)
    server_qr_primary = all(item.get("primary_login_flow") == "server_qrcode" for item in capabilities)
    qrcode_status_supported = all(item.get("qrcode_supported") is True for item in capabilities)
    try:
        _api(base_url, "POST", "/api/monitor/platform-status/dy/login-browser", {}, jar)
        endpoint_blocked = False
    except HttpError as exc:
        endpoint_blocked = exc.status == 403 and "网页登录二维码" in exc.body
    _record(
        results,
        "web_qrcode_login_flow_available",
        server_qr_primary and qrcode_status_supported,
        "login capabilities expose server_qrcode as the primary web flow",
    )
    _record(results, "production_local_login_disabled", local_disabled and endpoint_blocked, "local-window login is hidden by capabilities and blocked by API")


def _create_same_platform_accounts(base_url: str, jar: "CookieJar") -> list[int]:
    first = _api(
        base_url,
        "POST",
        "/api/monitor/social-accounts",
        {"name": "Phase8 Douyin A", "platform": "dy", "login_type": "qrcode", "status": "standby"},
        jar,
    )["account"]
    second = _api(
        base_url,
        "POST",
        "/api/monitor/social-accounts",
        {"name": "Phase8 Douyin B", "platform": "dy", "login_type": "qrcode", "status": "standby"},
        jar,
    )["account"]
    if first["profile_key"] == second["profile_key"]:
        raise RuntimeError("same-platform accounts reused a profile key")
    return [int(first["id"]), int(second["id"])]


def _verify_profile_paths(data_dir: Path, profile_root: Path, account_ids: list[int], results: list[dict[str, Any]]) -> None:
    db_path = data_dir / "monitor.sqlite"
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, profile_key, profile_path FROM social_accounts WHERE id IN (?, ?) ORDER BY id",
            tuple(account_ids),
        ).fetchall()
    expected = [profile_root / "1" / "dy" / f"acc_{account_id}" for account_id in account_ids]
    actual = [Path(row["profile_path"]) for row in rows]
    profile_keys = [row["profile_key"] for row in rows]
    ok = actual == expected and profile_keys == [f"1/dy/acc_{account_id}" for account_id in account_ids]
    _record(results, "profile_key_runtime_paths", ok, "profile paths use persistent account profile root")


def _verify_locks(env: dict[str, str], account_id: int, results: list[dict[str, Any]]) -> None:
    code = f"""
import json
from api.monitoring.database import (
    acquire_account_lock,
    acquire_proxy_lock,
    create_run,
    get_run,
    init_db,
    release_run_resource_locks,
    save_job,
    save_proxy_profile,
)

init_db()
run_ids = []
try:
    job = save_job({{
        "law_firm_name": "Phase8 Lock Test",
        "keywords": ["Phase8 Lock Test"],
        "platforms": ["dy"],
        "recipients": [],
    }})
    run1 = create_run(job["id"], timeout_seconds=120)
    run2 = create_run(job["id"], timeout_seconds=120)
    run_ids.extend([run1, run2])
    deadline = get_run(run1)["deadline_at"]
    account_first = acquire_account_lock({account_id}, run1, deadline)
    account_second = acquire_account_lock({account_id}, run2, deadline)
    proxy = save_proxy_profile({{
        "name": "phase8 single concurrency proxy",
        "provider": "manual",
        "proxy_url": "http://user:pass@127.0.0.1:8081",
        "status": "active",
        "max_concurrency": 1,
    }})
    proxy_first = acquire_proxy_lock(proxy["id"], run1, deadline)
    proxy_second = acquire_proxy_lock(proxy["id"], run2, deadline)
    print(json.dumps({{
        "account_first": account_first,
        "account_second": account_second,
        "proxy_first": proxy_first,
        "proxy_second": proxy_second,
    }}))
finally:
    for run_id in run_ids:
        release_run_resource_locks(run_id)
"""
    completed = subprocess.run(
        ["uv", "run", "python", "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-500:]
        _record(results, "account_profile_lock_limit", False, detail)
        _record(results, "proxy_lock_table_available", False, detail)
        return
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    _record(
        results,
        "account_profile_lock_limit",
        bool(payload.get("account_first")) and not bool(payload.get("account_second")),
        "same account/profile cannot be locked twice through runtime lock API",
    )
    _record(
        results,
        "proxy_lock_table_available",
        bool(payload.get("proxy_first")) and not bool(payload.get("proxy_second")),
        "proxy concurrency is enforced through runtime lock API and resource_locks",
    )


def _verify_headless_browser(results: list[dict[str, Any]]) -> None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("about:blank")
            browser.close()
        _record(results, "server_headless_browser_available", True, "Playwright Chromium launched headless")
    except Exception as exc:
        _record(results, "server_headless_browser_available", False, f"{type(exc).__name__}: {exc}")


def _api(base_url: str, method: str, path: str, payload: dict[str, Any] | None = None, jar: "CookieJar" | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if jar:
        cookie = jar.header()
        if cookie:
            headers["Cookie"] = cookie
    req = request.Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=15) as res:
            if jar:
                jar.update(res.headers.get_all("Set-Cookie") or [])
            raw = res.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise HttpError(exc.code, body) from exc


def _request_json(url: str) -> dict[str, Any]:
    with request.urlopen(url, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


def _request_text(url: str) -> str:
    with request.urlopen(url, timeout=5) as res:
        return res.read().decode("utf-8", errors="ignore")


def _free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _record(results: list[dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    results.append({"name": name, "ok": bool(ok), "detail": detail})


class HttpError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class CookieJar:
    def __init__(self) -> None:
        self.cookies: dict[str, str] = {}

    def update(self, values: list[str]) -> None:
        for value in values:
            first = value.split(";", 1)[0]
            if "=" not in first:
                continue
            key, raw = first.split("=", 1)
            self.cookies[key] = raw

    def header(self) -> str:
        return "; ".join(f"{key}={value}" for key, value in self.cookies.items())


if __name__ == "__main__":
    sys.exit(main())
