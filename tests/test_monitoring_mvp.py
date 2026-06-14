from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException

from api.monitoring.ai import _build_endpoint, _parse_json, _validate_ai_output, build_evaluation_payload, test_ai as run_ai_config_test
from api.monitoring.ai import DEFAULT_PROMPT
from api.monitoring.database import create_login_session, create_run, expire_login_sessions_for_account, finish_run, get_active_ai_key_profile, get_ai_config, get_conn, get_dashboard_summary, get_email_config, get_job, get_login_session, get_platform_login_config, get_report, get_run, get_social_account, init_db, list_ai_key_profiles, list_ai_rule_profiles, list_email_templates, list_jobs, list_leads, list_login_sessions, list_platform_login_configs, list_proxy_profiles, list_reports, list_runs, list_social_accounts, mark_selftest_jobs_internal, record_skipped_run, render_email_template_preview, save_ai_config, save_ai_key_profile, save_ai_rule_profile, save_email_config, save_email_template, save_job, save_platform_login_config, save_proxy_profile, save_social_account, set_active_ai_key_profile, set_active_ai_rule_profile, update_social_account_check_state
from api.monitoring.mediacrawler_login import get_mediacrawler_login_capability
from api.monitoring.login_browser import build_login_browser_command, open_login_browser, open_login_browser_with_command
import api.monitoring.account_check as account_check_module
import api.monitoring.login_qrcode as login_qrcode_module
import api.monitoring.mediacrawler_login as mediacrawler_login_module
from api.monitoring.login_state import login_window_status, record_login_window
from api.monitoring.mailer import build_report_email, render_report_email_preview, send_test_email
from api.monitoring.normalizer import collect_platform_outputs, in_time_window, normalize_content, parse_jsonl_file, resolve_window
from api.monitoring.platform_status import list_platform_status
from api.monitoring.preflight import build_job_preflight
from api.monitoring.readiness import get_readiness_status
from api.monitoring.reporting import create_report, resend_report_email
from api.monitoring.security import redact_sensitive
from api.monitoring.selftest import create_sample_report
from api.monitoring.smoke import run_smoke_check
from api.monitoring.cli import run_due_jobs
from api.monitoring.doctor import run_doctor
from cmd_arg import parse_cmd as parse_mediacrawler_cmd
from api.routers import monitor as monitor_router
import api.monitoring.cli as cli_module
import api.monitoring.ai as ai_module
import api.monitoring.readiness as readiness_module
import api.monitoring.runner as runner_module
import api.monitoring.scheduler as scheduler_module
from api.monitoring.runner import evaluate_new_contents, ingest_outputs
from api.monitoring.runner import run_job as run_monitor_job
from api.monitoring.scheduler import _is_due, next_run_at, scheduler_disabled_reason, scheduler_status
from tools.cdp_browser import resolve_cdp_user_data_dir


@pytest.fixture(autouse=True)
def _clear_ai_skip_env(monkeypatch):
    monkeypatch.delenv("MONITOR_SKIP_AI_API", raising=False)


def test_root_entry_redirects_to_monitor_admin():
    from api import main as api_main

    response = asyncio.run(api_main.serve_frontend())

    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/monitor"


def test_environment_check_returns_customer_safe_text(monkeypatch):
    from api import main as api_main

    class Result:
        returncode = 0
        stdout = "internal details"
        stderr = ""

    monkeypatch.setattr("api.main.subprocess.run", lambda *args, **kwargs: Result())

    result = asyncio.run(api_main.check_environment())
    visible = json.dumps(result, ensure_ascii=False)

    assert result["success"] is True
    assert result["message"] == "采集运行环境可用"
    assert result["output"] == "运行环境检查通过"
    for forbidden in ["MediaCrawler", "uv run", "main.py", "CLI"]:
        assert forbidden not in visible


def test_ai_endpoint_builder_handles_v1_and_full_paths():
    assert _build_endpoint("https://api.openai.com", "/v1/chat/completions") == "https://api.openai.com/v1/chat/completions"
    assert _build_endpoint("https://api.openai.com/v1", "/v1/chat/completions") == "https://api.openai.com/v1/chat/completions"
    assert _build_endpoint("https://api.openai.com/v1/chat/completions", "/v1/chat/completions") == "https://api.openai.com/v1/chat/completions"


def test_scheduler_cron_waits_until_today_fire_time_for_new_jobs():
    base = {"frequency": "cron", "cron_expr": "0 9 * * *", "email_time": "09:00", "last_run_at": None}
    assert _is_due(base, datetime(2026, 6, 11, 8, 0, 0)) is False
    assert _is_due(base, datetime(2026, 6, 11, 9, 0, 0)) is True


def test_scheduler_interval_uses_last_run_spacing():
    recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    old = (datetime.now(timezone.utc) - timedelta(hours=7)).isoformat()
    assert _is_due({"frequency": "6h", "email_time": "00:00", "last_run_at": recent}, datetime.now()) is False
    assert _is_due({"frequency": "6h", "email_time": "00:00", "last_run_at": old}, datetime.now()) is True


def test_scheduler_next_run_at_is_visible_for_jobs():
    now = datetime(2026, 6, 12, 8, 0, 0)
    assert next_run_at({"enabled": False, "frequency": "daily", "email_time": "09:00"}, now) is None
    assert next_run_at({"enabled": True, "frequency": "daily", "email_time": "09:00", "last_run_at": None}, now).startswith("2026-06-12T09:00:00")
    assert next_run_at(
        {
            "enabled": True,
            "frequency": "daily",
            "email_time": "09:00",
            "last_run_at": "2026-06-12T09:01:00+00:00",
        },
        datetime(2026, 6, 12, 10, 0, 0),
    ).startswith("2026-06-13T09:00:00")
    assert next_run_at(
        {
            "enabled": True,
            "frequency": "6h",
            "email_time": "00:00",
            "last_run_at": "2026-06-12T06:00:00",
        },
        datetime(2026, 6, 12, 8, 0, 0),
    ).startswith("2026-06-12T12:00:00")


def test_custom_window_and_millisecond_timestamps():
    start, end = resolve_window({"time_window_type": "custom", "custom_start": "2026-06-10", "custom_end": "2026-06-11"})
    assert start.isoformat().startswith("2026-06-10T00:00:00")
    assert end.isoformat().startswith("2026-06-11T23:59:59")
    publish_ms = int(datetime(2026, 6, 11, 12, tzinfo=timezone.utc).timestamp() * 1000)
    assert in_time_window({"publish_time": publish_ms}, {"time_window_type": "custom", "custom_start": "2026-06-11", "custom_end": "2026-06-11"})


def test_platform_normalization_keeps_cover_and_keyword():
    job = {"law_firm_name": "测试律所", "keywords": ["测试律所避雷"]}
    xhs = normalize_content(
        "xhs",
        {
            "note_id": "x1",
            "title": "测试律所避雷",
            "desc": "退费争议",
            "note_url": "https://example.com/xhs",
            "image_list": '[{"url":"https://example.com/cover.jpg"}]',
            "time": 1781180000,
        },
        job,
    )
    assert xhs
    assert xhs["cover_url"] == "https://example.com/cover.jpg"
    assert xhs["source_keyword"] == "测试律所避雷"


def test_collect_platform_outputs_supports_json_and_jsonl(tmp_path):
    json_dir = tmp_path / "douyin" / "json"
    jsonl_dir = tmp_path / "douyin" / "jsonl"
    json_dir.mkdir(parents=True)
    jsonl_dir.mkdir(parents=True)
    (json_dir / "search_contents_2026-06-12.json").write_text('[{"aweme_id":"json_1"}]', encoding="utf-8")
    (jsonl_dir / "search_contents_2026-06-12.jsonl").write_text('{"aweme_id":"jsonl_1"}\nnot-json\n{"aweme_id":"jsonl_2"}\n', encoding="utf-8")
    (jsonl_dir / "search_comments_2026-06-12.jsonl").write_text('{"comment_id":"c1","aweme_id":"jsonl_1"}\n', encoding="utf-8")

    contents, comments = collect_platform_outputs(tmp_path, "dy")

    assert [item["aweme_id"] for item in contents] == ["json_1", "jsonl_1", "jsonl_2"]
    assert parse_jsonl_file(jsonl_dir / "search_contents_2026-06-12.jsonl")[0]["aweme_id"] == "jsonl_1"
    assert comments[0]["comment_id"] == "c1"


def test_platform_status_reports_profile_and_login_error(tmp_path):
    profile = tmp_path / "browser_data" / "cdp_dy_user_data_dir"
    profile.mkdir(parents=True)
    state = profile / "state"
    state.write_text("ok", encoding="utf-8")
    profile_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    run_time = datetime.now(timezone.utc)
    os.utime(state, (profile_time.timestamp(), profile_time.timestamp()))
    statuses = list_platform_status(
        tmp_path,
        [
            {
                "finished_at": run_time.isoformat(),
                "summary": {
                    "platform_results": {
                        "dy": {"error": "MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号"}
                    }
                }
            }
        ],
    )
    dy = next(item for item in statuses if item["platform"] == "dy")
    ks = next(item for item in statuses if item["platform"] == "ks")
    assert dy["profile_exists"] is True
    assert dy["needs_login"] is True
    assert ks["profile_exists"] is False


def test_platform_status_ignores_login_error_older_than_successful_login_session(tmp_path):
    init_db()
    snapshot = _snapshot_table("login_sessions")
    profile = tmp_path / "browser_data" / "cdp_dy_user_data_dir"
    profile.mkdir(parents=True)
    state = profile / "state"
    state.write_text("ok", encoding="utf-8")
    error_time = datetime(2026, 6, 12, 9, 0, tzinfo=timezone.utc)
    try:
        session = create_login_session(
            {
                "platform": "dy",
                "login_url": "https://www.douyin.com/",
                "profile_path": str(profile),
            }
        )
        monitor_router.update_login_session_status(
            int(session["id"]),
            "success",
            "登录成功，Profile 已保存。",
        )
        with get_conn() as conn:
            conn.execute(
                "UPDATE login_sessions SET updated_at=? WHERE id=?",
                ((error_time + timedelta(minutes=10)).isoformat(), session["id"]),
            )

        statuses = list_platform_status(
            tmp_path,
            [
                {
                    "finished_at": error_time.isoformat(),
                    "summary": {
                        "platform_results": {
                            "dy": {"error": "MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号"}
                        }
                    },
                }
            ],
        )
    finally:
        _restore_table("login_sessions", snapshot)
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["profile_exists"] is True
    assert dy["needs_login"] is False
    assert dy["last_error"] == ""


def test_platform_status_keeps_fresh_login_error_when_browser_profile_was_touched(tmp_path):
    profile = tmp_path / "browser_data" / "cdp_ks_user_data_dir"
    profile.mkdir(parents=True)
    state = profile / "state"
    state.write_text("browser touched during failed login", encoding="utf-8")
    error_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    touched_time = error_time + timedelta(seconds=5)
    os.utime(state, (touched_time.timestamp(), touched_time.timestamp()))

    statuses = list_platform_status(
        tmp_path,
        [
            {
                "finished_at": error_time.isoformat(),
                "summary": {
                    "platform_results": {
                        "ks": {
                            "error": "MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号"
                        }
                    }
                },
            }
        ],
    )
    ks = next(item for item in statuses if item["platform"] == "ks")

    assert ks["profile_exists"] is True
    assert ks["needs_login"] is True
    assert "登录态失效" in ks["last_error"]


def test_platform_status_ignores_login_error_older_than_cookie_config(tmp_path, monkeypatch):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        save_platform_login_config("dy", {"login_type": "cookie", "cookies": "sessionid=secret-cookie"})
        with get_conn() as conn:
            conn.execute(
                "UPDATE platform_login_configs SET updated_at=? WHERE platform='dy'",
                ("2026-06-12T09:10:00+00:00",),
            )
        statuses = list_platform_status(
            tmp_path,
            [
                {
                    "finished_at": "2026-06-12T09:00:00+00:00",
                    "summary": {
                        "platform_results": {
                            "dy": {"error": "MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号"}
                        }
                    },
                }
            ],
        )
    finally:
        _restore_table("platform_login_configs", snapshot)

    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["login_type"] == "cookie"
    assert dy["has_cookies"] is True
    assert dy["profile_exists"] is False
    assert dy["needs_login"] is False
    assert dy["last_error"] == ""


def test_platform_status_ignores_legacy_phone_login_config(tmp_path):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO platform_login_configs (platform, login_type, cookies_encrypted, login_phone_encrypted, updated_at)
                VALUES ('xhs', 'phone', '', '', ?)
                ON CONFLICT(platform) DO UPDATE SET login_type='phone', login_phone_encrypted='', updated_at=excluded.updated_at
                """,
                ("2026-06-13T08:00:00+00:00",),
            )
        statuses = list_platform_status(tmp_path, [])
    finally:
        _restore_table("platform_login_configs", snapshot)

    xhs = next(item for item in statuses if item["platform"] == "xhs")

    assert xhs["login_type"] == "qrcode"
    assert "has_login_phone" not in xhs
    assert "login_phone" not in xhs
    assert xhs["login_material_ready"] is False
    assert "网页登录态" in xhs["login_material_error"]
    assert xhs["needs_login"] is True
    assert xhs["login_ready"] is False


def test_platform_status_clears_closed_login_window_error(tmp_path, monkeypatch):
    profile = tmp_path / "browser_data" / "cdp_dy_user_data_dir"
    profile.mkdir(parents=True)
    (profile / "state").write_text("ok", encoding="utf-8")
    monkeypatch.setattr("api.monitoring.platform_status.login_window_status", lambda platform: {"is_open": False})
    statuses = list_platform_status(
        tmp_path,
        [
            {
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "platform_results": {
                        "dy": {"error": "抖音登录窗口未关闭，请关闭窗口后再运行采集"}
                    }
                },
            }
        ],
    )
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["last_error"] == ""
    assert dy["needs_login"] is False


def test_platform_status_reports_open_login_window(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    (browser_data / "cdp_dy_user_data_dir").mkdir(parents=True)
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))
    monkeypatch.setattr("api.monitoring.login_state.LOGIN_STATE_DIR", tmp_path / "login_windows")
    monkeypatch.setattr("api.monitoring.login_state._pid_exists", lambda pid: pid == 12345)
    record_login_window("dy", 12345, 9323, str(browser_data / "cdp_dy_user_data_dir"))

    dy = next(item for item in list_platform_status(tmp_path, []) if item["platform"] == "dy")

    assert dy["login_window_open"] is True
    assert dy["login_window_pid"] == 12345


def test_login_window_status_removes_stale_pid_record(tmp_path, monkeypatch):
    monkeypatch.setattr("api.monitoring.login_state.LOGIN_STATE_DIR", tmp_path / "login_windows")
    monkeypatch.setattr("api.monitoring.login_state._pid_exists", lambda pid: False)
    record_login_window("dy", 12345, 9323, str(tmp_path / "profile"))

    status = login_window_status("dy")

    assert status["is_open"] is False
    assert status["pid"] is None
    assert status["opened_at"]
    assert status["closed_at"]
    assert (tmp_path / "login_windows" / "dy.json").exists()


def test_platform_status_clears_login_error_after_closed_login_window_profile_update(tmp_path, monkeypatch):
    login_state_dir = tmp_path / "login_windows"
    monkeypatch.setattr("api.monitoring.login_state.LOGIN_STATE_DIR", login_state_dir)
    monkeypatch.setattr("api.monitoring.platform_status.LOGIN_STATE_DIR", login_state_dir, raising=False)
    monkeypatch.setattr("api.monitoring.login_state._pid_exists", lambda pid: False)
    browser_data = tmp_path / "browser_data"
    profile = browser_data / "cdp_ks_user_data_dir"
    profile.mkdir(parents=True)
    state = profile / "state"
    state.write_text("manual login refreshed profile", encoding="utf-8")
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))
    error_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    opened_at = error_time + timedelta(minutes=1)
    refreshed_at = opened_at + timedelta(minutes=1)
    closed_at = refreshed_at + timedelta(minutes=1)
    os.utime(state, (refreshed_at.timestamp(), refreshed_at.timestamp()))
    login_state_dir.mkdir(parents=True)
    (login_state_dir / "ks.json").write_text(
        json.dumps(
            {
                "platform": "ks",
                "pid": 12345,
                "debug_port": 9324,
                "profile_path": str(profile),
                "opened_at": opened_at.isoformat(),
                "closed_at": closed_at.isoformat(),
            }
        ),
        encoding="utf-8",
    )

    statuses = list_platform_status(
        tmp_path,
        [
            {
                "finished_at": error_time.isoformat(),
                "summary": {
                    "platform_results": {
                        "ks": {"error": "MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号"}
                    }
                },
            }
        ],
    )
    ks = next(item for item in statuses if item["platform"] == "ks")

    assert ks["profile_exists"] is True
    assert ks["needs_login"] is False
    assert ks["last_error"] == ""


def test_platform_status_supports_custom_browser_data_dir(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    (browser_data / "cdp_dy_user_data_dir").mkdir(parents=True)
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))

    statuses = list_platform_status(tmp_path, [])
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["profile_path"] == str((browser_data / "cdp_dy_user_data_dir").resolve())
    assert dy["profile_exists"] is True


def test_platform_status_uses_active_account_profile_when_present(tmp_path):
    init_db()
    snapshot = _snapshot_table("social_accounts")
    account_profile = tmp_path / "account_profile"
    account_profile.mkdir(parents=True)
    (account_profile / "state").write_text("ok", encoding="utf-8")
    try:
        account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(account_profile),
            }
        )

        statuses = list_platform_status(tmp_path, [])
    finally:
        _restore_table("social_accounts", snapshot)
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["profile_path"] == str(account_profile)
    assert dy["profile_exists"] is True
    assert dy["using_account_profile"] is True
    assert dy["active_account_id"] == account["id"]
    assert dy["active_account_name"] == "海安律所抖音采集号"


def test_cdp_browser_uses_same_custom_profile_root_as_status(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))

    expected = browser_data / "cdp_dy_user_data_dir"

    assert Path(resolve_cdp_user_data_dir("dy")) == expected
    dy_status = next(item for item in list_platform_status(tmp_path, []) if item["platform"] == "dy")
    assert dy_status["profile_path"] == str(expected.resolve())


def test_cdp_browser_can_use_explicit_account_profile(tmp_path, monkeypatch):
    account_profile = tmp_path / "account_profiles" / "dy_1"
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(tmp_path / "platform_profiles"))
    monkeypatch.setenv("MONITOR_CDP_USER_DATA_DIR_DY", str(account_profile))

    assert Path(resolve_cdp_user_data_dir("dy")) == account_profile


def test_login_browser_command_uses_monitor_profile_root(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    fake_browser = tmp_path / "chrome.exe"
    fake_browser.write_text("", encoding="utf-8")
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))
    monkeypatch.setattr("api.monitoring.login_browser.BrowserLauncher.detect_browser_paths", lambda self: [str(fake_browser)])

    command = build_login_browser_command("xhs")

    assert command["profile_path"] == str((browser_data / "cdp_xhs_user_data_dir").resolve())
    assert command["debug_port"] == 9325
    assert command["login_url"].startswith("https://www.xiaohongshu.com")


def test_login_browser_message_reminds_to_close_window(tmp_path, monkeypatch):
    fake_browser = tmp_path / "chrome.exe"
    fake_browser.write_text("", encoding="utf-8")
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(tmp_path / "profiles"))
    monkeypatch.setattr("api.monitoring.login_state.LOGIN_STATE_DIR", tmp_path / "login_windows")
    monkeypatch.setattr("api.monitoring.login_state._pid_exists", lambda pid: pid == 12345)
    monkeypatch.setattr("api.monitoring.login_browser.BrowserLauncher.detect_browser_paths", lambda self: [str(fake_browser)])

    class FakeProcess:
        pid = 12345

    monkeypatch.setattr("api.monitoring.login_browser.subprocess.Popen", lambda *args, **kwargs: FakeProcess())

    result = open_login_browser("dy")

    assert result["pid"] == 12345
    assert login_window_status("dy")["pid"] == 12345
    assert "关闭该窗口" in result["message"]
    assert "运行采集" in result["message"]


def test_login_browser_route_can_use_social_account_profile(tmp_path, monkeypatch):
    init_db()
    snapshots = {
        "social_accounts": _snapshot_table("social_accounts"),
    }
    fake_browser = tmp_path / "chrome.exe"
    fake_browser.write_text("", encoding="utf-8")
    seen: dict[str, Any] = {}
    try:
        account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "standby",
                "profile_path": str(tmp_path / "account_profile"),
            }
        )
        monkeypatch.setattr("api.monitoring.login_browser.BrowserLauncher.detect_browser_paths", lambda self: [str(fake_browser)])

        def fake_open_login_browser_with_command(command):
            seen["profile_path"] = command["profile_path"]
            return {**command, "pid": 12345, "message": "ok"}

        monkeypatch.setattr(monitor_router, "open_login_browser_with_command", fake_open_login_browser_with_command)

        result = asyncio.run(monitor_router.platform_login_browser("dy", {"account_id": account["id"]}))

        assert result["pid"] == 12345
        assert seen["profile_path"] == str(tmp_path / "account_profile")
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_browser_command_supports_per_platform_port_env(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    fake_browser = tmp_path / "chrome.exe"
    fake_browser.write_text("", encoding="utf-8")
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))
    monkeypatch.setenv("MONITOR_LOGIN_DEBUG_PORT_DY", "19323")
    monkeypatch.setattr("api.monitoring.login_browser.BrowserLauncher.detect_browser_paths", lambda self: [str(fake_browser)])

    command = build_login_browser_command("dy")

    assert command["debug_port"] == 19323
    assert command["profile_path"] == str((browser_data / "cdp_dy_user_data_dir").resolve())


def test_job_validation_rejects_operator_input_errors():
    base = {
        "law_firm_name": "校验测试律所",
        "keywords": ["校验测试律所避雷"],
        "platforms": ["dy"],
        "enable_comments": False,
        "time_window_type": "recent_1d",
        "frequency": "daily",
        "email_time": "09:00",
        "enabled": True,
    }
    with pytest.raises(ValueError, match="invalid recipient email"):
        save_job({**base, "recipients": ["bad-email"]})
    with pytest.raises(ValueError, match="cron_expr is required"):
        save_job({**base, "recipients": [], "frequency": "cron", "cron_expr": ""})
    with pytest.raises(ValueError, match="custom_start must be before custom_end"):
        save_job(
            {
                **base,
                "recipients": [],
                "time_window_type": "custom",
                "custom_start": "2026-06-12",
                "custom_end": "2026-06-11",
            }
        )
    with pytest.raises(ValueError, match="email_time must be HH:MM"):
        save_job({**base, "recipients": [], "email_time": "25:00"})
    with pytest.raises(ValueError, match="测试数据模板"):
        save_job({**base, "law_firm_name": "请改成目标律所名称", "recipients": []})
    with pytest.raises(ValueError, match="测试数据模板"):
        save_job({**base, "keywords": ["目标律所避雷"], "recipients": []})


def test_job_advanced_collect_config_persists_and_validates(tmp_path):
    init_db()
    snapshots = {
        "monitor_jobs": _snapshot_table("monitor_jobs"),
        "job_keywords": _snapshot_table("job_keywords"),
        "job_platforms": _snapshot_table("job_platforms"),
        "job_recipients": _snapshot_table("job_recipients"),
        "ai_key_profiles": _snapshot_table("ai_key_profiles"),
        "email_templates": _snapshot_table("email_templates"),
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    try:
        profile = save_ai_key_profile(
            {
                "name": "海安 AI 接入",
                "provider": "openai",
                "base_url": "https://example.com",
                "api_key": "sk-test-advanced",
                "model": "test-model",
            }
        )
        template = save_email_template({"name": "海安日报模板", "subject_template": "日报 {law_firm_name}", "html_template": "{report_body}"})
        proxy = save_proxy_profile({"name": "华东代理", "provider": "manual", "proxy_url": "http://user:pass@127.0.0.1:8081"})
        account = save_social_account({"name": "抖音采集号", "platform": "dy", "status": "active", "proxy_id": proxy["id"]})
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": ["海安律师事务所"],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": True,
                "enable_sub_comments": True,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "target_type": "detail",
                "max_pages": 3,
                "max_items": 12,
                "start_page": 2,
                "output_mode": "excel",
                "browser_mode": "profile",
                "ai_profile_id": profile["id"],
                "email_template_id": template["id"],
                "account_id": account["id"],
                "proxy_id": proxy["id"],
            }
        )
        stored = get_job(job["id"])
        cmd = runner_module._build_crawler_cmd(stored, "dy", tmp_path)

        assert stored["enable_sub_comments"] is True
        assert stored["target_type"] == "detail"
        assert stored["max_pages"] == 3
        assert stored["max_items"] == 12
        assert stored["start_page"] == 2
        assert stored["output_mode"] == "excel"
        assert stored["browser_mode"] == "profile"
        assert stored["ai_profile_id"] == profile["id"]
        assert stored["email_template_id"] == template["id"]
        assert stored["account_id"] == account["id"]
        assert stored["proxy_id"] == proxy["id"]
        assert _cmd_value(cmd, "--type") == "detail"
        assert _cmd_value(cmd, "--save_data_option") == "excel"
        assert _cmd_value(cmd, "--start") == "2"
        assert _cmd_value(cmd, "--get_sub_comment") == "true"
        assert _cmd_value(cmd, "--crawler_max_notes_count") == "30"
        assert _cmd_value(cmd, "--specified_id") == "海安律所避雷"

        for patch, message in [
            ({"target_type": "bad"}, "target_type must be one of"),
            ({"output_mode": "bad"}, "output_mode must be one of"),
            ({"browser_mode": "bad"}, "browser_mode must be one of"),
            ({"max_pages": 0}, "max_pages must be between"),
            ({"account_id": 99999999}, "social account not found"),
        ]:
            with pytest.raises(ValueError, match=message):
                save_job({**stored, **patch, "recipients": ["target@example.com"]}, stored["id"])
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_runner_command_maps_creator_mode_to_platform_user_collection(tmp_path):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        cmd = runner_module._build_crawler_cmd(
            {
                "keywords": ["MS4wLjABAAAAhaian"],
                "enable_comments": False,
                "enable_sub_comments": False,
                "time_window_type": "recent_1d",
                "target_type": "creator",
                "max_pages": 1,
                "max_items": 8,
                "start_page": 1,
                "output_mode": "internal",
            },
            "dy",
            tmp_path,
        )
    finally:
        _restore_table("platform_login_configs", snapshot)

    assert _cmd_value(cmd, "--type") == "creator"
    assert _cmd_value(cmd, "--save_data_option") == "json"
    assert _cmd_value(cmd, "--crawler_max_notes_count") == "10"
    assert _cmd_value(cmd, "--creator_id") == "MS4wLjABAAAAhaian"
    assert "--specified_id" not in cmd


def test_ai_and_email_config_validation_rejects_bad_inputs():
    init_db()
    with pytest.raises(ValueError, match="invalid AI provider"):
        save_ai_config({"provider": "bad", "temperature": 0})
    with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
        save_ai_config({"provider": "openai", "temperature": 9})
    with pytest.raises(ValueError, match="smtp_port must be between 1 and 65535"):
        save_email_config({"smtp_port": 70000})
    with pytest.raises(ValueError, match="invalid email encryption"):
        save_email_config({"encryption": "tls"})
    with pytest.raises(ValueError, match="invalid recipient email"):
        save_email_config({"default_recipients": ["bad-email"]})


def test_platform_login_config_defaults_masking_and_validation():
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        configs = list_platform_login_configs()
        dy = next(item for item in configs if item["platform"] == "dy")
        ks = next(item for item in configs if item["platform"] == "ks")

        assert dy["login_type"] == "qrcode"
        assert dy["supported_login_types"] == ["qrcode", "cookie"]
        assert "phone" not in ks["supported_login_types"]
        assert dy["login_capability_source"] == "平台采集服务"
        assert "暂未开放手机号登录" in ks["unsupported_reason"]

        saved = save_platform_login_config("dy", {"login_type": "cookie", "cookies": "sessionid=secret-cookie"})
        raw = get_platform_login_config("dy", masked=False)

        assert saved["login_type"] == "cookie"
        assert saved["has_cookies"] is True
        assert "secret-cookie" not in saved["cookies"]
        assert raw["cookies"] == "sessionid=secret-cookie"

        with pytest.raises(ValueError, match="暂未开放手机号登录"):
            save_platform_login_config("ks", {"login_type": "phone"})
        with pytest.raises(ValueError, match="Cookie 登录需要先填写 Cookie"):
            save_platform_login_config("xhs", {"login_type": "cookie"})
        with pytest.raises(ValueError, match="暂未开放手机号登录"):
            save_platform_login_config("dy", {"login_type": "phone", "clear_login_phone": True})
        with pytest.raises(ValueError, match="unsupported platform"):
            save_platform_login_config("wb", {"login_type": "qrcode"})
    finally:
        _restore_table("platform_login_configs", snapshot)


def test_runner_command_uses_platform_login_config_for_cookie_mode(tmp_path):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        save_platform_login_config("dy", {"login_type": "cookie", "cookies": "sessionid=secret-cookie"})
        cmd = runner_module._build_crawler_cmd(
            {"keywords": ["海安律所避雷"], "enable_comments": False, "time_window_type": "recent_1d"},
            "dy",
            tmp_path,
        )
    finally:
        _restore_table("platform_login_configs", snapshot)

    assert _cmd_value(cmd, "--lt") == "cookie"
    assert _cmd_value(cmd, "--cookies") == "sessionid=secret-cookie"


def test_runner_command_uses_bound_account_cookie_login_parameter(tmp_path):
    init_db()
    snapshot = _snapshot_table("social_accounts")
    try:
        account = save_social_account(
            {
                "name": "海安律所小红书采集号",
                "platform": "xhs",
                "login_type": "cookie",
                "status": "active",
                "cookies": "web_session=account-cookie",
            }
        )
        cmd = runner_module._build_crawler_cmd(
            {"keywords": ["海安律所退费"], "enable_comments": False, "time_window_type": "recent_1d"},
            "xhs",
            tmp_path,
            {"login_type": account["login_type"], "cookies": "web_session=account-cookie"},
        )
    finally:
        _restore_table("social_accounts", snapshot)

    assert _cmd_value(cmd, "--lt") == "cookie"
    assert _cmd_value(cmd, "--cookies") == "web_session=account-cookie"


def test_runner_command_defaults_to_qrcode_login(tmp_path):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        cmd = runner_module._build_crawler_cmd(
            {"keywords": ["海安律所避雷"], "enable_comments": False, "time_window_type": "recent_1d"},
            "xhs",
            tmp_path,
        )
    finally:
        _restore_table("platform_login_configs", snapshot)

    assert _cmd_value(cmd, "--lt") == "qrcode"
    assert "--cookies" not in cmd


def test_mediacrawler_cli_accepts_login_phone(monkeypatch):
    import config

    original = getattr(config, "LOGIN_PHONE", "")
    try:
        result = asyncio.run(
            parse_mediacrawler_cmd(
                [
                    "--platform",
                    "xhs",
                    "--lt",
                    "phone",
                    "--type",
                    "search",
                    "--keywords",
                    "海安律所投诉",
                    "--login_phone",
                    "13800138000",
                ]
            )
        )

        assert result.login_phone == "13800138000"
        assert config.LOGIN_PHONE == "13800138000"
    finally:
        config.LOGIN_PHONE = original


def test_runner_injects_bound_active_proxy_without_leaking_secret(tmp_path):
    init_db()
    snapshots = {
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    try:
        proxy = save_proxy_profile(
            {
                "name": "华东采集代理",
                "provider": "manual",
                "proxy_url": "http://user:pass@127.0.0.1:8081",
                "status": "active",
                "max_concurrency": 1,
            }
        )
        account = save_social_account(
            {
                "name": "抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "proxy_id": proxy["id"],
            }
        )
        binding = runner_module._resolve_platform_proxy_binding("dy")
        env = runner_module._build_crawler_env(binding)
        summary = runner_module._proxy_summary(binding)
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)

    assert binding["account_id"] == account["id"]
    assert env["HTTP_PROXY"] == "http://user:pass@127.0.0.1:8081"
    assert env["HTTPS_PROXY"] == "http://user:pass@127.0.0.1:8081"
    assert env["MONITOR_ACTIVE_PROXY_ID"] == str(proxy["id"])
    assert summary["proxy_id"] == proxy["id"]
    assert "user:pass" not in summary["proxy_url"]
    assert "[REDACTED]" in summary["proxy_url"]


def test_runner_injects_active_account_profile_for_cdp(tmp_path):
    init_db()
    snapshot = _snapshot_table("social_accounts")
    try:
        account = save_social_account(
            {
                "name": "抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(tmp_path / "dy_account_profile"),
            }
        )
        binding = runner_module._resolve_platform_account_binding("dy")
        env = runner_module._build_crawler_env(binding)
        summary = runner_module._account_summary(binding)
    finally:
        _restore_table("social_accounts", snapshot)

    assert binding["account_id"] == account["id"]
    assert binding["profile_path"] == str(tmp_path / "dy_account_profile")
    assert env["MONITOR_CDP_USER_DATA_DIR"] == str(tmp_path / "dy_account_profile")
    assert env["MONITOR_CDP_USER_DATA_DIR_DY"] == str(tmp_path / "dy_account_profile")
    assert env["MONITOR_ACTIVE_ACCOUNT_ID"] == str(account["id"])
    assert summary["account_name"] == "抖音采集号"


def test_crawler_command_uses_platform_search_terms_only(tmp_path):
    init_db()
    snapshot = _snapshot_table("platform_login_configs")
    try:
        job = {
            "law_firm_name": "海安律所",
            "aliases": ["海安律师事务所", "海安律师"],
            "exclude_words": ["招聘", "广告合作"],
            "keywords": ["海安律所避雷", "海安律所退费", "海安律所投诉"],
            "enable_comments": False,
            "enable_sub_comments": False,
            "time_window_type": "recent_1d",
            "target_type": "search",
            "max_pages": 1,
            "max_items": 20,
            "start_page": 1,
            "output_mode": "internal",
        }
        cmd = runner_module._build_crawler_cmd(job, "dy", tmp_path)
    finally:
        _restore_table("platform_login_configs", snapshot)

    assert _cmd_value(cmd, "--keywords") == "海安律所避雷,海安律所退费,海安律所投诉"
    command_text = " ".join(cmd)
    assert "海安律师事务所" not in command_text
    assert "海安律师" not in command_text
    assert "招聘" not in command_text
    assert "广告合作" not in command_text


def test_runner_prefers_job_bound_account_and_proxy(tmp_path):
    init_db()
    snapshots = {
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    try:
        account_proxy = save_proxy_profile(
            {
                "name": "账号默认代理",
                "provider": "manual",
                "proxy_url": "http://account:pass@127.0.0.1:8081",
                "status": "active",
                "max_concurrency": 1,
            }
        )
        job_proxy = save_proxy_profile(
            {
                "name": "任务指定代理",
                "provider": "manual",
                "proxy_url": "http://job:pass@127.0.0.1:8082",
                "status": "active",
                "max_concurrency": 1,
            }
        )
        fallback_account = save_social_account(
            {
                "name": "抖音备用号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(tmp_path / "fallback_profile"),
            }
        )
        bound_account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(tmp_path / "bound_profile"),
                "proxy_id": account_proxy["id"],
            }
        )
        binding = runner_module._resolve_platform_account_binding(
            "dy",
            {"account_id": bound_account["id"], "proxy_id": job_proxy["id"]},
        )
        env = runner_module._build_crawler_env(binding)
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)

    assert fallback_account["id"] != bound_account["id"]
    assert binding["account_id"] == bound_account["id"]
    assert binding["profile_path"] == str(tmp_path / "bound_profile")
    assert binding["proxy_id"] == job_proxy["id"]
    assert env["HTTP_PROXY"] == "http://job:pass@127.0.0.1:8082"


def test_ai_and_email_test_paths_reuse_config_validation():
    init_db()
    with pytest.raises(ValueError, match="invalid AI provider"):
        asyncio.run(run_ai_config_test({"provider": "bad", "base_url": "https://example.com", "api_key": "sk-test", "model": "m"}))
    with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
        asyncio.run(run_ai_config_test({"provider": "openai", "base_url": "https://example.com", "api_key": "sk-test", "model": "m", "temperature": 9}))
    with pytest.raises(ValueError, match="smtp_port must be between 1 and 65535"):
        send_test_email({"smtp_port": 70000, "smtp_host": "smtp.example.com", "sender": "a@example.com", "default_recipients": ["b@example.com"]})
    with pytest.raises(ValueError, match="invalid email encryption"):
        send_test_email({"encryption": "tls", "smtp_host": "smtp.example.com", "sender": "a@example.com", "default_recipients": ["b@example.com"]})
    with pytest.raises(ValueError, match="invalid recipient email"):
        send_test_email({"smtp_host": "smtp.example.com", "sender": "a@example.com", "target": "bad-email"})


def test_report_email_uses_specific_attachment_mime_types(tmp_path):
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<h1>日报</h1>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")

    msg = build_report_email(
        {"sender": "sender@example.com"},
        ["target@example.com"],
        "测试日报",
        {"html_path": str(html_path), "excel_path": str(xlsx_path), "markdown_path": str(md_path)},
    )
    attachment_types = [part.get_content_type() for part in msg.iter_attachments()]

    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in attachment_types
    assert "text/markdown" in attachment_types
    assert msg["To"] == "target@example.com"


def test_active_email_template_uses_report_summary_values(tmp_path):
    init_db()
    snapshot = _snapshot_table("email_templates")
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<article>真实报告正文</article>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")
    try:
        save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name} {negative_count}",
                "html_template": "<main>{law_firm_name}|{new_contents}|{negative_count}|{high_count}|{pending_review_count}|{platforms}|{report_html}</main>",
                "is_active": True,
            }
        )
        msg = build_report_email(
            {"sender": "sender@example.com"},
            ["target@example.com"],
            "测试日报",
            {
                "law_firm_name": "海安律所",
                "summary": {
                    "law_firm_name": "海安律所",
                    "new_contents": 9,
                    "negative_count": 3,
                    "high_count": 1,
                    "pending_review_count": 2,
                    "platforms": ["dy", "ks", "xhs"],
                },
                "html_path": str(html_path),
                "excel_path": str(xlsx_path),
                "markdown_path": str(md_path),
            },
        )
        html_body = _email_html_body(msg)
    finally:
        _restore_table("email_templates", snapshot)

    assert "海安律所|9|3|1|2|抖音 / 快手 / 小红书" in html_body
    assert "真实报告正文" in html_body


def test_active_email_template_uses_job_values_for_html_body(tmp_path):
    init_db()
    snapshot = _snapshot_table("email_templates")
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<article>正文</article>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")
    try:
        save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name}",
                "html_template": "<main>{law_firm_name}|{platforms}|{report_html}</main>",
                "is_active": True,
            }
        )
        msg = build_report_email(
            {"sender": "sender@example.com"},
            ["target@example.com"],
            "测试日报",
            {
                "summary": {"platforms": ["dy", "xhs"]},
                "html_path": str(html_path),
                "excel_path": str(xlsx_path),
                "markdown_path": str(md_path),
            },
            {"law_firm_name": "海安律所"},
        )
        html_body = _email_html_body(msg)
    finally:
        _restore_table("email_templates", snapshot)

    assert "海安律所|抖音 / 小红书" in html_body
    assert "<article>正文</article>" in html_body


def test_active_email_template_supports_report_body_alias(tmp_path):
    init_db()
    snapshot = _snapshot_table("email_templates")
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<article>报告正文别名</article>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")
    try:
        save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name}",
                "html_template": "<main>{law_firm_name}|{report_body}</main>",
                "is_active": True,
            }
        )
        msg = build_report_email(
            {"sender": "sender@example.com"},
            ["target@example.com"],
            "测试日报",
            {
                "summary": {"platforms": ["dy"]},
                "html_path": str(html_path),
                "excel_path": str(xlsx_path),
                "markdown_path": str(md_path),
            },
            {"law_firm_name": "海安律所"},
        )
        html_body = _email_html_body(msg)
    finally:
        _restore_table("email_templates", snapshot)

    assert "海安律所|<article>报告正文别名</article>" in html_body


def test_report_email_preview_reuses_active_email_template(tmp_path):
    init_db()
    snapshot = _snapshot_table("email_templates")
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<article>真实报告正文</article>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")
    try:
        save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name} {negative_count}",
                "html_template": "<main>{law_firm_name}|{negative_count}|{report_html}</main>",
                "is_active": True,
            }
        )
        preview = render_report_email_preview(
            {"law_firm_name": "海安律所"},
            {
                "summary": {"negative_count": 3, "platforms": ["dy"]},
                "html_path": str(html_path),
                "excel_path": str(xlsx_path),
                "markdown_path": str(md_path),
            },
            {"sender": "sender@example.com"},
        )
    finally:
        _restore_table("email_templates", snapshot)

    assert preview["subject"] == "日报 海安律所 3"
    assert "海安律所|3|<article>真实报告正文</article>" in preview["html"]


def test_job_bound_email_template_takes_precedence_for_email_and_preview(tmp_path):
    init_db()
    snapshot = _snapshot_table("email_templates")
    html_path = tmp_path / "report.html"
    xlsx_path = tmp_path / "report.xlsx"
    md_path = tmp_path / "report.md"
    html_path.write_text("<article>报告正文</article>", encoding="utf-8")
    xlsx_path.write_bytes(b"fake-xlsx")
    md_path.write_text("# 日报", encoding="utf-8")
    try:
        active = save_email_template(
            {
                "name": "默认邮件模板",
                "subject_template": "默认 {law_firm_name}",
                "html_template": "<main>默认模板|{law_firm_name}</main>",
                "is_active": True,
            }
        )
        bound = save_email_template(
            {
                "name": "海安任务模板",
                "subject_template": "绑定 {law_firm_name} {new_contents}",
                "html_template": "<main>绑定模板|{law_firm_name}|{new_contents}|{report_body}</main>",
                "is_active": False,
            }
        )
        job = {"law_firm_name": "海安律所", "email_template_id": bound["id"]}
        report = {
            "summary": {"new_contents": 5, "platforms": ["dy"]},
            "html_path": str(html_path),
            "excel_path": str(xlsx_path),
            "markdown_path": str(md_path),
        }

        preview = render_report_email_preview(job, report, {"sender": "sender@example.com"})
        msg = build_report_email(
            {"sender": "sender@example.com"},
            ["target@example.com"],
            preview["subject"],
            report,
            job,
        )
        html_body = _email_html_body(msg)

        assert active["is_active"] is True
        assert preview["subject"] == "绑定 海安律所 5"
        assert "绑定模板|海安律所|5|<article>报告正文</article>" in preview["html"]
        assert "绑定模板|海安律所|5|<article>报告正文</article>" in html_body
        assert "默认模板" not in html_body
    finally:
        _restore_table("email_templates", snapshot)


def test_email_template_preview_supports_report_body_alias():
    preview = asyncio.run(
        monitor_router.email_template_preview(
            {
                "subject_template": "日报 {law_firm_name}",
                "html_template": "<main>{law_firm_name}|{report_body}</main>",
                "law_firm_name": "海安律所",
            }
        )
    )["preview"]

    assert preview["subject"] == "日报 海安律所"
    assert "海安律所|" in preview["html"]
    assert "高风险线索" in preview["html"]


def test_report_email_preview_api_returns_actual_email_body():
    init_db()
    snapshots = {
        "email_templates": _snapshot_table("email_templates"),
        "monitor_jobs": _snapshot_monitor_jobs(),
    }
    _clear_monitor_jobs()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "keywords": ["海安律所避雷"],
            "exclude_words": [],
            "platforms": ["dy"],
            "recipients": ["target@example.com"],
            "enabled": False,
        }
    )
    run_id = create_run(job["id"])
    try:
        save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name} {new_contents}",
                "html_template": "<main>{law_firm_name}|{new_contents}|{report_html}</main>",
                "is_active": True,
            }
        )
        report = create_report(
            run_id,
            job,
            {"platforms": ["dy"], "failed_platforms": [], "new_contents": 2, "negative_count": 0, "high_count": 0},
        )

        result = asyncio.run(monitor_router.report_email_preview(int(report["id"])))["preview"]

        assert result["subject"] == "日报 海安律所 2"
        assert "海安律所|2|" in result["html"]
        assert "AI 结果仅用于舆情线索筛查" in result["html"]
    finally:
        _cleanup_test_records(job["id"], "")
        _restore_table("email_templates", snapshots["email_templates"])
        _restore_monitor_jobs(snapshots["monitor_jobs"])


def test_report_download_media_types_are_specific(tmp_path):
    assert (
        monitor_router._report_download_media_type("excel", tmp_path / "report.xlsx")
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert monitor_router._report_download_media_type("markdown", tmp_path / "report.md") == "text/markdown"
    assert monitor_router._report_download_media_type("html", tmp_path / "report.html") == "text/html"


def test_report_path_guard_rejects_files_outside_report_dir(tmp_path, monkeypatch):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    safe_path = reports_dir / "report.html"
    unsafe_path = tmp_path / "secret.txt"
    safe_path.write_text("ok", encoding="utf-8")
    unsafe_path.write_text("secret", encoding="utf-8")
    monkeypatch.setattr(monitor_router, "MONITOR_DATA_DIR", tmp_path)

    assert monitor_router._safe_report_path(str(safe_path)) == safe_path
    with pytest.raises(HTTPException) as exc:
        monitor_router._safe_report_path(str(unsafe_path))

    assert exc.value.status_code == 403


def test_sensitive_text_is_redacted():
    text = "Authorization: Bearer sk-secret123456789 api_key=abc123 password=hunter2 cookie=session=abc token=mytoken"
    proxy_text = "proxy=http://user:pass@127.0.0.1:8081"
    redacted = redact_sensitive(text)
    redacted_proxy = redact_sensitive(proxy_text)

    assert "sk-secret123456789" not in redacted
    assert "abc123" not in redacted
    assert "hunter2" not in redacted
    assert "session=abc" not in redacted
    assert "mytoken" not in redacted
    assert "user:pass" not in redacted_proxy
    assert "http://[REDACTED]@127.0.0.1:8081" in redacted_proxy
    assert "[REDACTED]" in redacted


def test_run_summary_and_log_api_redact_sensitive_values(tmp_path, monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "脱敏测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["脱敏测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    run_id = create_run(job["id"])
    secret_text = "api_key=abc123 password=hunter2 cookie=session=abc"
    finish_run(
        run_id,
        "failed",
        {"platform_results": {"dy": {"status": "failed", "error": secret_text}}},
        secret_text,
    )
    run_dir = tmp_path / "runs" / "job_1" / f"run_{run_id}_pytest" / "dy"
    run_dir.mkdir(parents=True)
    (run_dir / "crawler.log").write_text(secret_text, encoding="utf-8")
    monkeypatch.setattr(monitor_router, "MONITOR_DATA_DIR", tmp_path)

    with get_conn() as conn:
        row = conn.execute("SELECT summary, error_message FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    logs = asyncio.run(monitor_router.run_logs(run_id))["logs"]
    _cleanup_test_records(job["id"], "")

    assert "abc123" not in row["summary"]
    assert "hunter2" not in row["error_message"]
    assert logs
    assert "session=abc" not in logs[0]["content"]
    assert "[REDACTED]" in logs[0]["content"]


def test_ai_test_requires_contract_shaped_output():
    valid = _validate_ai_output(
        {
            "is_related": True,
            "is_negative": True,
            "risk_level": "high",
            "reason": "命中投诉",
            "evidence_quotes": ["退费争议"],
            "recommended_action": "人工复核",
        }
    )
    assert valid["risk_level"] == "high"
    tolerant = _validate_ai_output(
        {
            "result": {
                "is_related": "true",
                "is_negative": "false",
                "risk_level": "高风险",
                "reason": "命中投诉",
                "evidence_quotes": "退费争议",
                "recommended_action": "人工复核",
            }
        }
    )
    assert tolerant["is_related"] is True
    assert tolerant["is_negative"] is False
    assert tolerant["risk_level"] == "high"
    assert tolerant["evidence_quotes"] == ["退费争议"]
    with pytest.raises(ValueError, match="AI 输出缺少字段"):
        _validate_ai_output({"is_related": True})
    with pytest.raises(ValueError, match="risk_level"):
        _validate_ai_output(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "urgent",
                "reason": "命中投诉",
                "evidence_quotes": ["退费争议"],
                "recommended_action": "人工复核",
            }
        )


def test_ai_json_parser_accepts_fenced_json_with_prefix_text():
    parsed = _parse_json(
        """
        下面是判断结果：
        ```json
        {"is_related": true, "is_negative": false, "risk_level": "low", "reason": "普通内容", "evidence_quotes": [], "recommended_action": "无需处理"}
        ```
        """
    )

    assert parsed["is_related"] is True
    assert parsed["risk_level"] == "low"


def test_ai_evaluation_failure_redacts_provider_endpoint(monkeypatch):
    monkeypatch.delenv("MONITOR_SKIP_AI_API", raising=False)
    monkeypatch.setattr(ai_module, "get_active_ai_key_profile", lambda masked=False: None)
    monkeypatch.setattr(
        ai_module,
        "get_ai_config",
        lambda masked=False: {
            "provider": "openai",
            "base_url": "https://deedee.tech",
            "api_key": "sk-test",
            "model": "test-model",
            "temperature": 0,
            "prompt": DEFAULT_PROMPT,
        },
    )

    async def fake_call_openai(cfg, prompt, payload):
        request = httpx.Request("POST", "https://deedee.tech/v1/chat/completions")
        response = httpx.Response(502, request=request)
        raise httpx.HTTPStatusError(
            "Server error '502 Bad Gateway' for url 'https://deedee.tech/v1/chat/completions'",
            request=request,
            response=response,
        )

    monkeypatch.setattr(ai_module, "_call_openai", fake_call_openai)

    result = asyncio.run(
        ai_module.evaluate_content(
            {"law_firm_name": "海安律所", "aliases": [], "exclude_words": []},
            {
                "platform": "dy",
                "source_keyword": "海安律所避雷",
                "title": "海安律所退费投诉",
                "description": "退费迟迟没有处理",
            },
            [],
        )
    )

    assert result["status"] == "pending_review"
    assert "deedee.tech" not in result["reason"]
    assert "v1/chat/completions" not in result["reason"]
    assert "[AI_ENDPOINT_REDACTED]" in result["reason"]


def test_ai_test_uses_haian_sample_payload(monkeypatch):
    init_db()
    seen: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen.update(payload)
        return json.dumps(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "medium",
                "reason": "命中退费投诉",
                "evidence_quotes": ["退费拖了很久"],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

    result = asyncio.run(
        run_ai_config_test(
            {
                "provider": "openai",
                "base_url": "https://example.com",
                "api_key": "sk-test",
                "model": "test-model",
                "temperature": 0,
            }
        )
    )

    assert result["risk_level"] == "medium"
    assert seen["law_firm_name"] == "海安律所"
    assert seen["source_keyword"] == "海安律所避雷"
    assert "海安律所" in seen["title"]
    assert seen["content_url"].startswith("https://www.douyin.com/video/")
    assert seen["cover_url"]
    assert seen["comment_summary"]["sample_count"] == 2


def test_ai_test_accepts_editable_sample_context(monkeypatch):
    init_db()
    seen: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen.update(payload)
        return json.dumps(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "medium",
                "reason": "样例命中",
                "evidence_quotes": [payload["source_keyword"]],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

    result = asyncio.run(
        run_ai_config_test(
            {
                "provider": "openai",
                "base_url": "https://example.com",
                "api_key": "sk-test",
                "model": "test-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "sample_law_firm_name": "测试律所",
                "sample_platform": "xhs",
                "sample_source_keyword": "测试律所投诉",
                "sample_title": "测试律所投诉样例",
                "sample_text": "收费争议需要复核",
                "sample_comments": "自定义评论一\n自定义评论二",
            }
        )
    )

    assert result["risk_level"] == "medium"
    assert seen["law_firm_name"] == "测试律所"
    assert seen["platform"] == "小红书"
    assert seen["platform_code"] == "xhs"
    assert seen["source_keyword"] == "测试律所投诉"
    assert seen["title"] == "测试律所投诉样例"
    assert seen["description"] == "收费争议需要复核"
    assert seen["comments"] == ["自定义评论一", "自定义评论二"]


def test_ai_evaluation_payload_includes_content_and_comment_context():
    payload = build_evaluation_payload(
        {
            "law_firm_name": "海安律所",
            "aliases": ["海安律师事务所"],
            "exclude_words": ["招聘"],
        },
        {
            "platform": "xhs",
            "platform_label": "小红书",
            "source_keyword": "海安律所退费",
            "title": "海安律所退费沟通记录",
            "description": "咨询退费一直没有明确回复。",
            "author_name": "海安用户",
            "content_url": "https://www.xiaohongshu.com/explore/haian-note",
            "cover_url": "https://example.com/cover.jpg",
            "publish_time": 1781280000,
            "comment_count": 12,
        },
        [
            {"content": "我也想知道退费怎么处理", "author_name": "评论用户A", "create_time": 1781280100},
            {"content": "先保留合同和聊天记录", "author_name": "评论用户B", "create_time": 1781280200},
        ],
    )

    assert payload["law_firm_name"] == "海安律所"
    assert payload["platform"] == "小红书"
    assert payload["platform_code"] == "xhs"
    assert payload["content_url"].endswith("haian-note")
    assert payload["cover_url"].endswith("cover.jpg")
    assert payload["author_name"] == "海安用户"
    assert payload["comment_count"] == 12
    assert payload["comments"] == ["我也想知道退费怎么处理", "先保留合同和聊天记录"]
    assert payload["comment_samples"][0]["author_name"] == "评论用户A"
    assert payload["comment_summary"]["declared_count"] == 12
    assert payload["comment_summary"]["observed_count"] == 2
    assert "退费" in payload["comment_summary"]["sample_text"]


def test_ai_offline_check_does_not_call_provider_or_update_test_status(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    called = False

    async def fake_call_openai(cfg, prompt, payload):
        nonlocal called
        called = True
        raise RuntimeError("offline check must not call provider")

    try:
        save_ai_config(
            {
                "provider": "openai",
                "base_url": "https://saved.example.com",
                "api_key": "sk-saved",
                "model": "saved-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        before = get_ai_config()
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(
            monitor_router.ai_config_offline_check(
                {
                    "provider": "openai",
                    "base_url": "https://example.com",
                    "api_key": "sk-test",
                    "model": "test-model",
                    "temperature": 0,
                    "prompt": DEFAULT_PROMPT,
                }
            )
        )["result"]
        after = get_ai_config()

        assert called is False
        assert result["mode"] == "offline"
        assert result["endpoint"] == "https://example.com/v1/chat/completions"
        assert result["api_key_present"] is True
        assert result["sample_payload"]["law_firm_name"] == "海安律所"
        assert result["sample_payload"]["source_keyword"] == "海安律所避雷"
        assert after["base_url"] == before["base_url"]
        assert after["last_test_status"] == before["last_test_status"]
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ai_profiles_can_be_selected_and_used_for_evaluation(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    seen: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen.update(cfg)
        return json.dumps(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "high",
                "reason": "命中投诉",
                "evidence_quotes": ["投诉"],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    try:
        profile = save_ai_key_profile(
            {
                "name": "主力 OpenAI",
                "provider": "openai",
                "base_url": "https://ai.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": True,
            }
        )
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(
            ai_module.evaluate_content(
                {"law_firm_name": "海安律所"},
                {"platform": "dy", "title": "海安律所投诉", "description": "退费迟迟没有处理"},
                [],
            )
        )

        assert profile["is_active"] is True
        assert get_active_ai_key_profile()["id"] == profile["id"]
        assert seen["model"] == "profile-model"
        assert result["risk_level"] == "high"
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)


def test_ai_rule_test_uses_global_evaluation_prompt_with_active_profile(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    profile_snapshot = _snapshot_table("ai_key_profiles")
    email_snapshot = _snapshot_singleton_table("email_configs")
    seen: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen["prompt"] = prompt
        seen["model"] = cfg.get("model")
        return json.dumps(
            {
                "is_related": True,
                "is_negative": False,
                "risk_level": "low",
                "reason": "按当前规则判断",
                "evidence_quotes": [],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    try:
        save_ai_config(
            {
                "provider": "openai",
                "base_url": "",
                "api_key": "",
                "model": "",
                "temperature": 0,
                "prompt": "全局评估规则 Prompt",
            }
        )
        save_ai_key_profile(
            {
                "name": "默认 AI 接入",
                "provider": "openai",
                "base_url": "https://profile.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": "不应使用的接入 Prompt",
                "is_active": True,
            }
        )
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(run_ai_config_test({}))

        assert result["risk_level"] == "low"
        assert seen["model"] == "profile-model"
        assert seen["prompt"] == "全局评估规则 Prompt"
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_table("ai_key_profiles", profile_snapshot)


def test_job_bound_ai_profile_takes_precedence_over_active_profile(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    seen: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen.update(cfg)
        return json.dumps(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "medium",
                "reason": "命中退费投诉",
                "evidence_quotes": ["退费投诉"],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    try:
        active = save_ai_key_profile(
            {
                "name": "默认 AI 接入",
                "provider": "openai",
                "base_url": "https://active.example.com",
                "api_key": "sk-active",
                "model": "active-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": True,
            }
        )
        bound = save_ai_key_profile(
            {
                "name": "海安任务 AI 接入",
                "provider": "openai",
                "base_url": "https://bound.example.com",
                "api_key": "sk-bound",
                "model": "bound-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(
            ai_module.evaluate_content(
                {"law_firm_name": "海安律所", "ai_profile_id": bound["id"]},
                {"platform": "dy", "title": "海安律所退费", "description": "投诉退费迟迟没有处理"},
                [],
            )
        )

        assert active["is_active"] is True
        assert seen["model"] == "bound-model"
        assert seen["base_url"] == "https://bound.example.com"
        assert result["risk_level"] == "medium"
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)


def test_evaluate_content_sends_enriched_payload_to_provider(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    seen_payload: dict[str, Any] = {}

    async def fake_call_openai(cfg, prompt, payload):
        seen_payload.update(payload)
        return json.dumps(
            {
                "is_related": True,
                "is_negative": True,
                "risk_level": "medium",
                "reason": "评论和正文均提到退费投诉",
                "evidence_quotes": ["退费一直没有回复"],
                "recommended_action": "人工复核",
            },
            ensure_ascii=False,
        )

    try:
        save_ai_key_profile(
            {
                "name": "海安律所 OpenAI 接入",
                "provider": "openai",
                "base_url": "https://ai.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": True,
            }
        )
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(
            ai_module.evaluate_content(
                {"law_firm_name": "海安律所", "aliases": ["海安律师"], "exclude_words": []},
                {
                    "platform": "dy",
                    "platform_label": "抖音",
                    "source_keyword": "海安律所投诉",
                    "title": "海安律所投诉记录",
                    "description": "退费一直没有回复。",
                    "author_name": "海安用户",
                    "content_url": "https://www.douyin.com/video/haian-complaint",
                    "cover_url": "https://example.com/haian.jpg",
                    "publish_time": 1781280000,
                    "comment_count": 6,
                },
                [
                    {"content": "我也在等退费", "author_name": "评论用户A", "create_time": 1781280100},
                    {"content": "投诉后有人处理吗", "author_name": "评论用户B", "create_time": 1781280200},
                ],
            )
        )

        assert result["risk_level"] == "medium"
        assert seen_payload["law_firm_name"] == "海安律所"
        assert seen_payload["content_url"].endswith("haian-complaint")
        assert seen_payload["cover_url"].endswith("haian.jpg")
        assert seen_payload["author_name"] == "海安用户"
        assert seen_payload["publish_time"] == 1781280000
        assert seen_payload["comment_summary"]["declared_count"] == 6
        assert seen_payload["comment_summary"]["observed_count"] == 2
        assert seen_payload["comment_samples"][1]["author_name"] == "评论用户B"
        assert "投诉" in seen_payload["comments"][1]
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)


def test_ai_profile_offline_check_uses_profile_without_calling_provider(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    called = False

    async def fake_call_openai(cfg, prompt, payload):
        nonlocal called
        called = True
        raise RuntimeError("offline profile check must not call provider")

    try:
        profile = save_ai_key_profile(
            {
                "name": "海安律所 OpenAI 接入",
                "provider": "openai",
                "base_url": "https://profile.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": False,
            }
        )
        monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

        result = asyncio.run(monitor_router.ai_profile_offline_check(int(profile["id"])))["result"]

        assert called is False
        assert result["mode"] == "offline"
        assert result["endpoint"] == "https://profile.example.com/v1/chat/completions"
        assert result["model"] == "profile-model"
        assert result["api_key_present"] is True
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)


def test_ai_connection_test_returns_request_and_model_text(monkeypatch):
    monkeypatch.delenv("MONITOR_SKIP_AI_API", raising=False)

    async def fake_ping_openai(cfg):
        assert cfg["model"] == "deepseek-test"
        return {"choices": [{"message": {"content": "pong from model"}}]}

    monkeypatch.setattr(ai_module, "_ping_openai", fake_ping_openai)

    result = asyncio.run(
        ai_module.test_ai_connection(
            {
                "provider": "openai",
                "base_url": "https://api.example.com",
                "api_key": "sk-test",
                "model": "deepseek-test",
                "temperature": 0,
            }
        )
    )

    assert result["ok"] is True
    assert result["protocol"] == "openai"
    assert result["request_message"] == "hi"
    assert result["response_text"] == "pong from model"
    assert result["response_preview"] == "pong from model"
    assert "返回文本" in result["message"]


def test_ai_connection_test_reports_empty_response_shape(monkeypatch):
    monkeypatch.delenv("MONITOR_SKIP_AI_API", raising=False)

    async def fake_ping_openai(cfg):
        return {"id": "chatcmpl-empty", "choices": [{"message": {"content": ""}}]}

    monkeypatch.setattr(ai_module, "_ping_openai", fake_ping_openai)

    with pytest.raises(ValueError) as exc:
        asyncio.run(
            ai_module.test_ai_connection(
                {
                    "provider": "openai",
                    "base_url": "https://api.example.com",
                    "api_key": "sk-test",
                    "model": "deepseek-test",
                    "temperature": 0,
                }
            )
        )

    assert "没有返回文本" in str(exc.value)
    assert "chatcmpl-empty" in str(exc.value)


def test_anthropic_connection_test_uses_content_blocks_and_larger_token_budget(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"content": [{"type": "text", "text": "Hi"}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr(ai_module.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(
        ai_module.test_ai_connection(
            {
                "provider": "anthropic",
                "base_url": "https://api.example.com/anthropic",
                "api_key": "sk-test",
                "model": "compatible-model",
                "temperature": 0,
            }
        )
    )

    assert result["response_text"] == "Hi"
    assert result["protocol"] == "anthropic"
    assert captured["url"] == "https://api.example.com/anthropic/v1/messages"
    assert captured["json"]["max_tokens"] == ai_module.AI_CONNECTION_TEST_MAX_TOKENS
    assert captured["json"]["messages"] == [
        {"role": "user", "content": [{"type": "text", "text": "hi"}]}
    ]


def test_ai_model_text_extractor_supports_anthropic_and_compatible_shapes():
    assert ai_module._extract_model_text({"content": [{"text": "Hi there"}]}) == "Hi there"
    assert ai_module._extract_model_text({"content": "Hi from string"}) == "Hi from string"
    assert ai_module._extract_model_text({"choices": [{"message": {"content": [{"type": "text", "text": "Hi from array"}]}}]}) == "Hi from array"
    assert ai_module._extract_model_text({"choices": [{"text": "Hi from choice"}]}) == "Hi from choice"


def test_ai_model_list_fetches_openai_compatible_models(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"id": "deepseek-v4-flash"}, {"id": "deepseek-reasoner"}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers):
            captured["url"] = url
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(ai_module.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(
        ai_module.list_ai_models(
            {
                "provider": "openai",
                "base_url": "https://api.example.com",
                "api_key": "sk-test",
            }
        )
    )

    assert result["models"] == ["deepseek-v4-flash", "deepseek-reasoner"]
    assert result["endpoint"] == "https://api.example.com/v1/models"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"


def test_ai_model_list_fetches_anthropic_compatible_models(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"id": "claude-compatible"}, {"name": "custom-model"}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers):
            captured["url"] = url
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setattr(ai_module.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(
        ai_module.list_ai_models(
            {
                "provider": "anthropic",
                "base_url": "https://api.example.com/anthropic",
                "api_key": "sk-test",
            }
        )
    )

    assert result["models"] == ["claude-compatible", "custom-model"]
    assert result["endpoint"] == "https://api.example.com/anthropic/v1/models"
    assert captured["headers"]["x-api-key"] == "sk-test"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"


def test_ai_model_list_falls_back_from_adapter_path_to_parent_models(monkeypatch):
    attempts = []

    class FakeResponse:
        def __init__(self, url: str, ok: bool):
            self.url = url
            self.ok = ok

        def raise_for_status(self):
            if self.ok:
                return None
            request = httpx.Request("GET", self.url)
            response = httpx.Response(404, request=request)
            raise httpx.HTTPStatusError("not found", request=request, response=response)

        def json(self):
            return {"data": [{"id": "deepseek-v4-flash"}]}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def get(self, url, headers):
            attempts.append(url)
            return FakeResponse(url, ok=url == "https://api.example.com/models")

    monkeypatch.setattr(ai_module.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(
        ai_module.list_ai_models(
            {
                "provider": "anthropic",
                "base_url": "https://api.example.com/anthropic",
                "api_key": "sk-test",
            }
        )
    )

    assert result["models"] == ["deepseek-v4-flash"]
    assert result["endpoint"] == "https://api.example.com/models"
    assert attempts[:3] == [
        "https://api.example.com/anthropic/v1/models",
        "https://api.example.com/anthropic/models",
        "https://api.example.com/models",
    ]


def test_ai_model_list_requires_connection_fields(monkeypatch):
    with pytest.raises(ValueError) as exc:
        asyncio.run(ai_module.list_ai_models({"provider": "openai", "base_url": "", "api_key": ""}))

    assert "AI 接入未配置完整" in str(exc.value)


def test_ai_profile_real_test_respects_skip_env_and_records_result(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    try:
        profile = save_ai_key_profile(
            {
                "name": "海安律所 Anthropic Profile",
                "provider": "anthropic",
                "base_url": "https://anthropic.example.com",
                "api_key": "sk-ant",
                "model": "claude-test",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": False,
            }
        )
        monkeypatch.setenv("MONITOR_SKIP_AI_API", "true")

        with pytest.raises(HTTPException) as exc:
            asyncio.run(monitor_router.test_ai_profile(int(profile["id"])))

        assert exc.value.status_code == 400
        assert "未启用" in exc.value.detail
        tested = next(item for item in list_ai_key_profiles() if item["id"] == profile["id"])
        assert tested["last_test_status"] == "failed"
        assert "未启用" in tested["last_test_error"]
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)


def test_readiness_and_doctor_prefer_active_ai_profile(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    profile_snapshot = _snapshot_table("ai_key_profiles")
    try:
        save_ai_config(
            {
                "provider": "openai",
                "base_url": "",
                "api_key": "",
                "model": "",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        profile = save_ai_key_profile(
            {
                "name": "海安律所当前 AI 接入",
                "provider": "openai",
                "base_url": "https://profile.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": True,
            }
        )
        profile = monitor_router.mark_ai_key_profile_test_result(int(profile["id"]), True)
        assert profile["last_test_status"] == "success"

        readiness_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "ai_config")
        doctor_check = next(check for check in run_doctor()["checks"] if check["key"] == "ai_config")

        assert readiness_check["ok"] is True
        assert "profile-model" in readiness_check["message"]
        assert doctor_check["ok"] is True
        assert "profile-model" in doctor_check["message"]
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_table("ai_key_profiles", profile_snapshot)


def test_email_templates_preview_and_pool_configs_are_persisted():
    init_db()
    snapshots = {
        "email_templates": _snapshot_table("email_templates"),
        "social_accounts": _snapshot_table("social_accounts"),
        "proxy_profiles": _snapshot_table("proxy_profiles"),
    }
    try:
        preview = render_email_template_preview(
            {
                "subject_template": "日报 {law_firm_name} {date}",
                "html_template": "<h1>{law_firm_name}</h1><section>{report_html}</section>",
            }
        )
        template = save_email_template(
            {
                "name": "企业日报模板",
                "subject_template": "日报 {law_firm_name}",
                "html_template": "<main>{report_html}</main>",
                "is_active": True,
            }
        )
        proxy = save_proxy_profile(
            {
                "name": "华东代理池",
                "provider": "manual",
                "proxy_url": "http://user:pass@127.0.0.1:8081",
                "status": "active",
                "max_concurrency": 2,
            }
        )
        account = save_social_account(
            {
                "name": "抖音一号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "proxy_id": proxy["id"],
            }
        )
        summary = get_dashboard_summary()

        assert preview["subject"].startswith("日报 海安律所")
        assert "{report_html}" not in preview["html"]
        assert "海安律所退费投诉" in preview["html"]
        assert template["is_active"] is True
        assert list_email_templates()[0]["id"] == template["id"]
        assert list_proxy_profiles()[0]["proxy_url"].startswith("htt")
        assert account["platform"] == "dy"
        assert account["proxy_name"] == "华东代理池"
        assert account["proxy_status"] == "active"
        assert list_social_accounts()[0]["name"] == "抖音一号"
        assert list_social_accounts()[0]["proxy_name"] == "华东代理池"
        assert summary["social_accounts_total"] >= 1
        assert summary["proxy_profiles_total"] >= 1
        with pytest.raises(ValueError, match="proxy not found"):
            save_social_account(
                {
                    "name": "海安律所异常代理账号",
                    "platform": "dy",
                    "login_type": "qrcode",
                    "status": "standby",
                    "proxy_id": 99999999,
                }
            )
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_init_db_creates_default_email_template_when_empty():
    init_db()
    snapshot = _snapshot_table("email_templates")
    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM email_templates")
        init_db()
        templates = list_email_templates()

        assert len(templates) == 1
        assert templates[0]["name"] == "标准舆情日报模板"
        assert templates[0]["is_active"] is True
        assert "{report_html}" in templates[0]["html_template"]
    finally:
        _restore_table("email_templates", snapshot)


def test_login_sessions_are_persisted_for_server_side_login_flow():
    init_db()
    snapshot = _snapshot_table("login_sessions")
    try:
        session = create_login_session(
            {
                "platform": "dy",
                "account_id": None,
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
            }
        )
        listed = list_login_sessions()
        summary = get_dashboard_summary()

        assert session["status"] == "waiting_manual_browser"
        assert get_login_session(session["id"])["platform"] == "dy"
        assert listed[0]["id"] == session["id"]
        assert summary["login_sessions_total"] >= 1
        with pytest.raises(ValueError, match="unsupported platform"):
            create_login_session({"platform": "wb"})
    finally:
        _restore_table("login_sessions", snapshot)


def test_login_sessions_can_be_expired_for_same_account():
    init_db()
    snapshot = _snapshot_table("login_sessions")
    try:
        first = create_login_session(
            {
                "platform": "dy",
                "account_id": 10001,
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/account_10001",
            }
        )
        other = create_login_session(
            {
                "platform": "dy",
                "account_id": 10002,
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/account_10002",
            }
        )

        expired = expire_login_sessions_for_account(10001, "dy", "browser_data/account_10001")

        assert expired == [first["id"]]
        assert get_login_session(first["id"])["status"] == "expired"
        assert get_login_session(other["id"])["status"] == "waiting_manual_browser"
    finally:
        _restore_table("login_sessions", snapshot)


def test_login_session_routes_create_pollable_session(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("dy")
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "抖音",
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
                "debug_port": 9323,
                "browser_path": "chrome",
            },
        )
        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": True,
                "qr_image": "data:image/png;base64,abc",
                "message": "请扫码登录",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
            }

        async def fake_poll_qrcode_login_session(session_id):
            return {"active": True, "success": False, "message": "等待扫码确认。"}

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)
        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "dy",
                    "platform_label": "抖音",
                    "profile_path": "browser_data/cdp_dy_user_data_dir",
                    "login_ready": False,
                    "login_window_open": False,
                }
            ],
        )

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "dy", "account_id": account["id"]}))
        session_id = created["session"]["id"]
        polled = asyncio.run(monitor_router.login_session(session_id))

        assert created["capabilities"]["manual_browser_fallback"] is True
        assert created["capabilities"]["login_capability_source"] == "平台采集服务"
        assert created["capabilities"]["login_boundary"] == "复用平台采集服务登录能力"
        assert "验证码" in created["capabilities"]["captcha_policy"]
        assert created["capabilities"]["qr_image_supported"] is True
        assert created["session"]["status"] == "waiting_qrcode"
        assert created["session"]["qr_image"].startswith("data:image")
        assert polled["session"]["status"] == "waiting_qrcode"
        assert polled["platform_status"]["platform"] == "dy"
        assert polled["capabilities"]["login_capability_source"] == "平台采集服务"
        assert polled["capabilities"]["login_boundary"] == "复用平台采集服务登录能力"
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_session_route_falls_back_when_qrcode_unavailable(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("dy")
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "抖音",
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
                "debug_port": 9323,
                "browser_path": "chrome",
            },
        )

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": False,
                "message": "没有在页面中找到登录二维码，请使用网页登录窗口处理。当前页面：登录页",
                "diagnostic_image": "data:image/png;base64,diagnostic",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "dy", "account_id": account["id"]}))

        assert created["capabilities"]["manual_browser_fallback"] is True
        assert created["capabilities"]["qr_image_supported"] is False
        assert created["capabilities"]["diagnostic_image_supported"] is False
        assert created["capabilities"]["diagnostic_image"] == ""
        assert created["session"]["status"] == "waiting_manual_browser"
        assert "网页登录窗口处理" in created["session"]["message"]
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_account_login_session_does_not_inherit_default_platform_success(monkeypatch, tmp_path):
    init_db()
    snapshots = {
        "login_sessions": _snapshot_table("login_sessions"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    try:
        account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "standby",
                "profile_path": str(tmp_path / "account_profile"),
            }
        )
        session = create_login_session(
            {
                "platform": "dy",
                "account_id": account["id"],
                "login_url": "https://www.douyin.com",
                "profile_path": account["profile_path"],
                "message": "TargetClosedError: 浏览器会话被关闭或 Profile 正被占用，请稍后重试。",
            }
        )
        session = monitor_router.update_login_session_status(
            int(session["id"]),
            "waiting_manual_browser",
            "TargetClosedError: 浏览器会话被关闭或 Profile 正被占用，请稍后重试。",
        )

        async def fake_poll_qrcode_login_session(session_id):
            return {"active": False, "success": False, "message": "二维码浏览器会话不在运行，请重新生成二维码或打开登录窗口。"}

        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "dy",
                    "platform_label": "抖音",
                    "profile_path": str(tmp_path / "default_profile"),
                    "active_account_id": None,
                    "login_ready": True,
                    "login_window_open": False,
                }
            ],
        )

        polled = asyncio.run(monitor_router.login_session(int(session["id"])))
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)

    assert polled["session"]["status"] == "waiting_manual_browser"
    assert "TargetClosedError" in polled["session"]["message"]
    assert polled["platform_status"]["login_ready"] is True


def test_terminal_login_session_lookup_does_not_downgrade_checked_account(monkeypatch, tmp_path):
    init_db()
    snapshots = {
        "login_sessions": _snapshot_table("login_sessions"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    try:
        account = save_social_account(
            {
                "name": "海安律所小红书采集号",
                "platform": "xhs",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(tmp_path / "xhs_profile"),
            }
        )
        update_social_account_check_state(int(account["id"]), True, "登录态有效")
        session = create_login_session(
            {
                "platform": "xhs",
                "account_id": account["id"],
                "login_url": "https://www.xiaohongshu.com",
                "profile_path": account["profile_path"],
                "message": "二维码已过期，请重新生成。",
            }
        )
        monitor_router.update_login_session_status(int(session["id"]), "expired", "二维码已过期，请重新生成。")

        async def fake_poll_qrcode_login_session(session_id):
            return {"active": False, "success": False, "expired": True, "message": "二维码已过期，请重新生成。"}

        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(monitor_router, "list_platform_status", lambda: [])

        polled = asyncio.run(monitor_router.login_session(int(session["id"])))
        refreshed = get_social_account(int(account["id"]))
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)

    assert polled["session"]["status"] == "expired"
    assert refreshed["status"] == "active"
    assert refreshed["last_error"] == ""
    assert refreshed["last_checked_at"]


def test_default_login_session_does_not_turn_manual_failure_into_success(monkeypatch, tmp_path):
    init_db()
    snapshot = _snapshot_table("login_sessions")
    try:
        profile_path = str(tmp_path / "default_profile")
        session = create_login_session(
            {
                "platform": "dy",
                "login_url": "https://www.douyin.com",
                "profile_path": profile_path,
                "message": "TargetClosedError: 浏览器会话被关闭或 Profile 正被占用，请稍后重试。",
            }
        )
        monitor_router.update_login_session_status(
            int(session["id"]),
            "waiting_manual_browser",
            "TargetClosedError: 浏览器会话被关闭或 Profile 正被占用，请稍后重试。",
        )

        async def fake_poll_qrcode_login_session(session_id):
            return {"active": False, "success": False, "message": "二维码浏览器会话不在运行，请重新生成二维码或打开登录窗口。"}

        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "dy",
                    "platform_label": "抖音",
                    "profile_path": profile_path,
                    "active_account_id": None,
                    "login_ready": True,
                    "login_window_open": False,
                }
            ],
        )

        polled = asyncio.run(monitor_router.login_session(int(session["id"])))
    finally:
        _restore_table("login_sessions", snapshot)

    assert polled["session"]["status"] == "waiting_manual_browser"
    assert "TargetClosedError" in polled["session"]["message"]
    assert polled["platform_status"]["login_ready"] is True


def test_waiting_qrcode_session_does_not_inherit_platform_success(monkeypatch, tmp_path):
    init_db()
    snapshot = _snapshot_table("login_sessions")
    try:
        profile_path = str(tmp_path / "default_profile")
        session = create_login_session(
            {
                "platform": "xhs",
                "login_url": "https://www.xiaohongshu.com",
                "profile_path": profile_path,
                "qr_image": "data:image/png;base64,qr",
                "message": "请扫码登录",
            }
        )
        monitor_router.update_login_session_status(int(session["id"]), "waiting_qrcode", "二维码已生成，请扫码登录。", "data:image/png;base64,qr")

        async def fake_poll_qrcode_login_session(session_id):
            return {"active": True, "success": False, "qr_image": "data:image/png;base64,qr", "message": "二维码已生成，请扫码登录。"}

        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "xhs",
                    "platform_label": "小红书",
                    "profile_path": profile_path,
                    "active_account_id": None,
                    "login_ready": True,
                    "login_window_open": False,
                }
            ],
        )

        polled = asyncio.run(monitor_router.login_session(int(session["id"])))
    finally:
        _restore_table("login_sessions", snapshot)

    assert polled["session"]["status"] == "waiting_qrcode"
    assert polled["session"]["qr_image"].startswith("data:image")
    assert polled["platform_status"]["login_ready"] is True


def test_qrcode_lookup_falls_back_to_visible_page_candidate(monkeypatch):
    async def no_adapter_qrcode(login_adapter):
        return ""

    async def no_selector_qrcode(page, selector):
        return ""

    async def candidate_qrcode(page, platform):
        return "ZmFrZS1xcmNvZGU="

    monkeypatch.setattr(login_qrcode_module, "_find_qrcode_with_mediacrawler_adapter", no_adapter_qrcode)
    monkeypatch.setattr(login_qrcode_module, "_find_qrcode_with_mediacrawler_util", no_selector_qrcode)
    monkeypatch.setattr(login_qrcode_module, "_find_visible_qrcode_candidate_screenshot", candidate_qrcode)

    image = asyncio.run(login_qrcode_module._find_login_qrcode(object(), "xhs", 1000, object()))

    assert image == "ZmFrZS1xcmNvZGU="


def test_login_session_route_maps_manual_verification_then_qrcode(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("ks")
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "快手",
                "login_url": "https://www.kuaishou.com/?isHome=1",
                "profile_path": "browser_data/cdp_ks_user_data_dir",
                "debug_port": 9324,
                "browser_path": "chrome",
            },
        )

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": True,
                "needs_verification": True,
                "verification_type": "slider",
                "verification_label": "滑块验证",
                "verification_detail": "请拖动滑块完成拼图",
                "qr_image": "",
                "verification_image": "data:image/png;base64,ks-verification",
                "message": "平台要求先完成滑块验证，当前不会自动处理验证码。",
                "profile_path": command["profile_path"],
            }

        async def fake_poll_qrcode_login_session(session_id):
            return {
                "active": True,
                "success": False,
                "qr_image": "data:image/png;base64,ks-qr",
                "message": "二维码已生成，请扫码登录。",
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)
        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "ks",
                    "platform_label": "快手",
                    "profile_path": "browser_data/cdp_ks_user_data_dir",
                    "login_ready": False,
                    "login_window_open": False,
                }
            ],
        )

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "ks", "account_id": account["id"]}))
        polled = asyncio.run(monitor_router.login_session(int(created["session"]["id"])))

        assert created["session"]["status"] == "waiting_verification"
        assert created["capabilities"]["qr_image_supported"] is False
        assert created["capabilities"]["verification_image_supported"] is False
        assert created["capabilities"]["verification_image"] == ""
        assert created["capabilities"]["verification_type"] == "slider"
        assert created["capabilities"]["verification_label"] == "滑块验证"
        assert "拖动滑块" in created["capabilities"]["verification_detail"]
        assert "滑块" in created["session"]["message"]
        assert polled["session"]["status"] == "waiting_qrcode"
        assert polled["session"]["qr_image"].startswith("data:image")
        assert polled["capabilities"]["qr_image_supported"] is True
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_mediacrawler_login_capability_contract_is_explicit():
    expected_classes = {
        "dy": "media_platform.douyin.login.DouYinLogin",
        "ks": "media_platform.kuaishou.login.KuaishouLogin",
        "xhs": "media_platform.xhs.login.XiaoHongShuLogin",
    }
    for platform, class_path in expected_classes.items():
        capability = get_mediacrawler_login_capability(platform)

        assert capability["source"] == "MediaCrawler"
        assert capability["boundary"] == "media_crawler_only"
        assert capability["captcha_policy"] == "report_only"
        assert capability["login_engine"] == "MediaCrawler platform login class"
        assert capability["login_class"] == class_path
        assert capability["bridge_role"] == "capture_qrcode_and_forward_status_only"
        assert capability["qrcode_capture_method"] == "tools.utils.find_login_qrcode"
        assert capability["qrcode_prepare_method"].endswith(".prepare_qrcode_login")
        assert capability["qrcode_flow_steps"]
        assert "不实现独立平台登录爬虫" in capability["unsupported_behaviors"]


def test_login_session_response_exposes_mediacrawler_contract(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("xhs")
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "小红书",
                "login_url": "https://www.xiaohongshu.com",
                "profile_path": "browser_data/cdp_xhs_user_data_dir",
                "debug_port": 9325,
                "browser_path": "chrome",
            },
        )

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": True,
                "qr_image": "data:image/png;base64,xhs",
                "message": "请扫码登录",
                "profile_path": command["profile_path"],
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "xhs", "account_id": account["id"]}))
        caps = created["capabilities"]

        assert caps["login_capability_source"] == "平台采集服务"
        assert caps["login_boundary"] == "复用平台采集服务登录能力"
        assert "验证码" in caps["captcha_policy"]
        assert caps["login_class"] == ""
        assert caps["qrcode_capture_method"] == "页面二维码回传"
        assert caps["qrcode_prepare_method"] == "平台登录会话"
        assert caps["qrcode_flow_steps"]
        assert "不自动处理滑块、图形验证码或短信验证码" in caps["unsupported_behaviors"]
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_qrcode_bridge_uses_mediacrawler_login_adapter(monkeypatch):
    calls: list[str] = []

    class FakeLoginAdapter:
        def __init__(self, login_type, browser_context, context_page):
            calls.append(f"init:{login_type}")

        async def prepare_qrcode_login(self, timeout_ms=10000):
            calls.append(f"prepare:{timeout_ms}")

        async def capture_qrcode(self):
            calls.append("capture")
            return "data:image/png;base64,abc"

    class FakePage:
        async def wait_for_selector(self, *args, **kwargs):
            raise RuntimeError("selector unavailable")

    monkeypatch.setitem(login_qrcode_module.MEDIACRAWLER_LOGIN_CLASSES, "dy", FakeLoginAdapter)
    adapter = login_qrcode_module._build_mediacrawler_login_adapter("dy", object(), FakePage())

    asyncio.run(login_qrcode_module._prepare_login_page("dy", FakePage(), 1234, adapter))
    image = asyncio.run(login_qrcode_module._find_login_qrcode(FakePage(), "dy", 1234, adapter))

    assert image == "data:image/png;base64,abc"
    assert calls == ["init:qrcode", "prepare:1234", "capture"]


def test_login_session_route_keeps_manual_verification_status_when_window_is_open(monkeypatch):
    init_db()
    snapshot = _snapshot_table("login_sessions")
    try:
        session = create_login_session(
            {
                "platform": "ks",
                "login_url": "https://www.kuaishou.com/?isHome=1",
                "profile_path": "browser_data/cdp_ks_user_data_dir",
                "message": "等待完成人工验证",
            }
        )
        session = monitor_router.update_login_session_status(
            int(session["id"]),
            "waiting_verification",
            "等待完成人工验证",
        )

        async def fake_poll_qrcode_login_session(session_id):
            return {
                "active": True,
                "success": False,
                "needs_verification": True,
                "verification_type": "sms",
                "verification_label": "短信验证码",
                "verification_detail": "请输入验证码",
                "message": "平台要求先完成短信验证码，当前不会自动处理验证码。",
            }

        monkeypatch.setattr(monitor_router, "poll_qrcode_login_session", fake_poll_qrcode_login_session)
        monkeypatch.setattr(
            monitor_router,
            "list_platform_status",
            lambda: [
                {
                    "platform": "ks",
                    "platform_label": "快手",
                    "profile_path": session["profile_path"],
                    "login_ready": True,
                    "login_window_open": True,
                }
            ],
        )

        polled = asyncio.run(monitor_router.login_session(int(session["id"])))

        assert polled["session"]["status"] == "waiting_verification"
        assert "短信验证码" in polled["session"]["message"]
        assert polled["capabilities"]["verification_type"] == "sms"
        assert polled["capabilities"]["verification_label"] == "短信验证码"
    finally:
        _restore_table("login_sessions", snapshot)


def test_qrcode_data_url_is_preserved():
    raw = "data:image/png;base64,abc123"

    assert login_qrcode_module._as_data_url(raw) == raw


def test_mediacrawler_qrcode_util_fetches_remote_image_with_browser_request():
    class FakeResponse:
        ok = True
        headers = {"content-type": "image/jpeg"}

        async def body(self):
            return b"fake-image"

    class FakeRequest:
        async def get(self, url, headers=None):
            assert url == "https://example.com/qrcode.jpg"
            return FakeResponse()

    class FakeContext:
        request = FakeRequest()

    class FakeElement:
        async def get_attribute(self, attr):
            if attr == "src":
                return "https://example.com/qrcode.jpg"
            return ""

        async def evaluate(self, script):
            return "https://example.com/qrcode.jpg"

    class FakePage:
        context = FakeContext()

        async def wait_for_selector(self, selector):
            assert selector == "img.qrcode"
            return FakeElement()

    result = asyncio.run(login_qrcode_module.utils.find_login_qrcode(FakePage(), "img.qrcode"))

    assert result == "ZmFrZS1pbWFnZQ=="


def test_mediacrawler_qrcode_util_uses_element_screenshot_fallback():
    class FakeElement:
        async def get_attribute(self, attr):
            return ""

        async def evaluate(self, script):
            return ""

        async def screenshot(self):
            return b"png-bytes"

    class FakePage:
        async def wait_for_selector(self, selector):
            return FakeElement()

    result = asyncio.run(login_qrcode_module.utils.find_login_qrcode(FakePage(), "img.qrcode"))

    assert result == "cG5nLWJ5dGVz"


def test_qrcode_bridge_uses_mediacrawler_selectors():
    assert login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["ks"]["login_button_selector"] == "xpath=//p[text()='登录']"
    assert login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["ks"]["qrcode_selector"] == "xpath=//div[@class='qrcode-img']//img"
    assert login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["xhs"]["login_button_selector"] == "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button"
    assert "qrcode" in login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["xhs"]["qrcode_selector"]
    assert login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["ks"]["login_state"]["cookie_rules"] == {"passToken": None}
    assert login_qrcode_module.MEDIACRAWLER_LOGIN_FLOWS["xhs"]["login_state"]["session_cookie"] == "web_session"
    source = Path(login_qrcode_module.__file__).read_text(encoding="utf-8")
    assert "button:has-text('登录')" not in source
    assert "xpath=//li[contains(@class,'user-info-item')]" not in source
    assert "xpath=//div[contains(@class,'user')]" not in source
    assert "kwai-captcha" not in source
    assert "geetest" not in source
    assert "请按住滑块" not in source
    assert "验证码已发送" not in source
    assert "_image_from_selector" not in source
    assert "_fetch_image_data_url" not in source
    assert "AutomationControlled" not in source
    assert "navigator, 'webdriver'" not in source


def test_login_capabilities_are_sourced_from_mediacrawler():
    dy = get_mediacrawler_login_capability("dy")
    ks = get_mediacrawler_login_capability("ks")
    xhs = get_mediacrawler_login_capability("xhs")

    assert dy["source"] == "MediaCrawler"
    assert dy["boundary"] == "media_crawler_only"
    assert dy["captcha_policy"] == "report_only"
    assert dy["qrcode_selector"] == "xpath=//div[@id='animate_qrcode_container']//img"
    assert dy["login_state"]["cookie_rules"] == {"LOGIN_STATUS": "1"}
    assert dy["login_state"]["local_storage_rules"] == {"HasUserLogin": "1"}
    assert "phone" in dy["mediacrawler_supported_login_types"]
    assert "phone" not in dy["supported_login_types"]
    assert ks["login_button_selector"] == "xpath=//p[text()='登录']"
    assert ks["login_state"]["cookie_rules"] == {"passToken": None}
    assert "phone" not in ks["supported_login_types"]
    assert ks["manual_verification"]["labels"]["slider"] == "滑块验证"
    assert "请拖动滑块完成拼图" in ks["manual_verification"]["text_markers"]["slider"]
    assert "[class*='kwai-captcha']" in ks["manual_verification"]["selectors"]["slider"]
    assert xhs["login_button_selector"] == "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button"
    assert xhs["login_state"]["session_cookie"] == "web_session"
    assert ".geetest_panel" in xhs["manual_verification"]["selectors"]["slider"]


def test_qrcode_finder_prefers_mediacrawler_util(monkeypatch):
    seen: dict[str, str] = {}

    async def fake_find_login_qrcode(page, selector):
        seen["selector"] = selector
        return "data:image/png;base64,abc"

    monkeypatch.setattr(login_qrcode_module.utils, "find_login_qrcode", fake_find_login_qrcode)

    result = asyncio.run(login_qrcode_module._find_login_qrcode(object(), "xhs", 3000))

    assert "qrcode" in seen["selector"]
    assert result == "data:image/png;base64,abc"


def test_qrcode_start_prefers_qrcode_before_manual_verification(monkeypatch, tmp_path):
    events: list[str] = []

    class FakePage:
        def __init__(self):
            self.context = None

        def set_default_timeout(self, timeout):
            events.append("timeout")

        async def goto(self, *args, **kwargs):
            events.append("goto")

    class FakeContext:
        def __init__(self):
            self.pages = [FakePage()]
            self.pages[0].context = self

        async def new_page(self):
            page = FakePage()
            page.context = self
            self.pages.append(page)
            return page

        async def close(self):
            events.append("close")

        async def cookies(self):
            return []

    class FakeChromium:
        async def launch_persistent_context(self, **kwargs):
            return FakeContext()

    class FakePlaywright:
        chromium = FakeChromium()

        async def stop(self):
            events.append("stop")

    class FakePlaywrightFactory:
        async def start(self):
            return FakePlaywright()

    async def fake_prepare_login_page(platform, page, timeout, login_adapter=None):
        events.append("prepare")

    async def fake_detect_manual_verification(platform, page):
        events.append("verify")
        return {"needs_verification": True, "verification_type": "slider", "verification_label": "滑块验证", "verification_detail": "请拖动滑块"}

    async def fake_find_login_qrcode(page, platform, timeout, login_adapter=None):
        events.append("find_qr")
        return "data:image/png;base64,should-not-happen"

    monkeypatch.setattr(login_qrcode_module, "async_playwright", lambda: FakePlaywrightFactory())
    monkeypatch.setattr(login_qrcode_module, "_build_mediacrawler_login_adapter", lambda platform, context, page: object())
    monkeypatch.setattr(login_qrcode_module, "_prepare_login_page", fake_prepare_login_page)
    monkeypatch.setattr(login_qrcode_module, "_detect_manual_verification", fake_detect_manual_verification)
    monkeypatch.setattr(login_qrcode_module, "_find_login_qrcode", fake_find_login_qrcode)

    result = asyncio.run(
        login_qrcode_module.start_qrcode_login_session_with_profile(
            888001,
            "ks",
            {
                "profile_path": str(tmp_path / "ks_profile"),
                "browser_path": "chrome",
            },
        )
    )

    try:
        assert result["ok"] is True
        assert result["qr_image"] == "data:image/png;base64,should-not-happen"
        assert "needs_verification" not in result
        assert "verify" not in events
        assert "find_qr" in events
    finally:
        asyncio.run(login_qrcode_module.close_qrcode_login_session(888001))


def test_qrcode_login_defaults_to_server_headless_browser(monkeypatch):
    monkeypatch.delenv("MONITOR_LOGIN_QR_HEADLESS", raising=False)

    assert login_qrcode_module._login_qr_headless() is True


def test_qrcode_manual_verification_detects_slider_text_and_selector():
    class FakeLocator:
        def __init__(self, text: str = "", visible: bool = False):
            self.text = text
            self.visible = visible

        @property
        def first(self):
            return self

        async def inner_text(self, timeout=0):
            return self.text

        async def count(self):
            return 1 if self.visible else 0

        async def is_visible(self, timeout=0):
            return self.visible

    class TextPage:
        def locator(self, selector):
            return FakeLocator("请通过验证，向右拖动滑块", False)

    class SelectorPage:
        def locator(self, selector):
            if selector == "body":
                return FakeLocator("登录", False)
            return FakeLocator("", "captcha" in selector)

    assert asyncio.run(login_qrcode_module._needs_manual_verification("ks", TextPage())) is True
    assert asyncio.run(login_qrcode_module._needs_manual_verification("ks", SelectorPage())) is True


def test_qrcode_manual_verification_detects_challenge_url():
    class FakePage:
        url = "https://www.kuaishou.com/captcha/challenge"

    assert asyncio.run(login_qrcode_module._needs_manual_verification("ks", FakePage())) is True


def test_qrcode_manual_verification_detects_kuaishou_slider_copy():
    class FakeLocator:
        def __init__(self, text: str = ""):
            self.text = text

        @property
        def first(self):
            return self

        async def inner_text(self, timeout=0):
            return self.text

        async def count(self):
            return 0

        async def is_visible(self, timeout=0):
            return False

    class FakePage:
        url = "https://www.kuaishou.com/?isHome=1"

        def locator(self, selector):
            if selector == "body":
                return FakeLocator("请拖动滑块完成拼图")
            return FakeLocator("")

    assert asyncio.run(login_qrcode_module._needs_manual_verification("ks", FakePage())) is True


def test_qrcode_manual_verification_classifies_sms_code():
    class FakeLocator:
        def __init__(self, text: str = ""):
            self.text = text

        @property
        def first(self):
            return self

        async def inner_text(self, timeout=0):
            return self.text

        async def count(self):
            return 0

        async def is_visible(self, timeout=0):
            return False

    class FakePage:
        url = "https://www.douyin.com/"

        def locator(self, selector):
            if selector == "body":
                return FakeLocator("请输入验证码，验证码已发送")
            return FakeLocator("")

    result = asyncio.run(login_qrcode_module._detect_manual_verification("dy", FakePage()))

    assert result["needs_verification"] is True
    assert result["verification_type"] == "sms"
    assert result["verification_label"] == "短信验证码"


def test_xhs_login_state_requires_session_change_when_login_modal_visible():
    class FakeContext:
        async def cookies(self):
            return [{"name": "web_session", "value": "new-session"}]

    class FakePage:
        async def is_visible(self, selector, timeout=0):
            if selector == "div.login-container, .login-modal, img.qrcode-img":
                return True
            return False

    result = asyncio.run(login_qrcode_module._is_logged_in("xhs", FakeContext(), FakePage(), "old-session"))

    assert result is False


def test_xhs_login_state_succeeds_after_session_change():
    class FakeContext:
        async def cookies(self):
            return [{"name": "web_session", "value": "logged-session"}]

    result = asyncio.run(login_qrcode_module._is_logged_in("xhs", FakeContext(), object(), "guest-session"))

    assert result is True


def test_mediacrawler_login_state_check_uses_platform_method(monkeypatch):
    calls: list[str] = []

    class FakeLogin:
        def __init__(self, login_type, browser_context, context_page):
            calls.append(login_type)

        async def check_login_state(self):
            calls.append("check")
            return True

    monkeypatch.setitem(mediacrawler_login_module.MEDIACRAWLER_LOGIN_CLASSES, "dy", FakeLogin)

    result = asyncio.run(mediacrawler_login_module.call_mediacrawler_check_login_state("dy", object(), object()))

    assert result is True
    assert calls == ["qrcode", "check"]


def test_account_collectable_login_requires_mediacrawler_pong(monkeypatch):
    async def fake_login_state(platform, context, page, login_baseline=""):
        return True

    async def fake_pong(platform, context, page, timeout_ms):
        return {"ok": False, "message": "采集前验活未通过。"}

    monkeypatch.setattr(account_check_module, "call_mediacrawler_check_login_state", fake_login_state)
    monkeypatch.setattr(account_check_module, "_check_mediacrawler_client_pong", fake_pong)

    result = asyncio.run(account_check_module._verify_collectable_login("xhs", object(), object(), 1000, "guest-session"))

    assert result["ok"] is False
    assert result["status"] == "client_check_failed"
    assert "采集前验活" in result["message"]


def test_login_session_route_marks_existing_profile_success(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("dy")
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "抖音",
                "login_url": "https://www.douyin.com/",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
                "debug_port": 9323,
                "browser_path": "chrome",
            },
        )

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": True,
                "already_logged_in": True,
                "qr_image": "",
                "message": "当前 Profile 已经登录，不需要重新扫码。",
                "profile_path": "browser_data/cdp_dy_user_data_dir",
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)
        async def fake_check_social_account_login(account_id, timeout_ms=15000, allow_draft=False):
            return {
                "ok": True,
                "account": get_social_account(account_id),
            }

        monkeypatch.setattr(monitor_router, "check_social_account_login", fake_check_social_account_login)

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "dy", "account_id": account["id"]}))

        assert created["session"]["status"] == "success"
        assert created["capabilities"]["manual_browser_fallback"] is True
        assert created["capabilities"]["qr_image_supported"] is False
        assert "通过验活" in created["session"]["message"]
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_session_success_requires_account_check(monkeypatch):
    init_db()
    snapshots = {"login_sessions": _snapshot_table("login_sessions"), "social_accounts": _snapshot_table("social_accounts")}
    try:
        account = _login_test_account("xhs")

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            return {
                "ok": True,
                "already_logged_in": True,
                "qr_image": "",
                "message": "当前 Profile 已经登录，不需要重新扫码。",
                "profile_path": command["profile_path"],
            }

        async def fake_check_social_account_login(account_id, timeout_ms=15000, allow_draft=False):
            return {
                "ok": False,
                "message": "登录态无效或已失效，请重新扫码登录。",
                "account": update_social_account_check_state(account_id, False, "登录态无效或已失效，请重新扫码登录。"),
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)
        monkeypatch.setattr(monitor_router, "check_social_account_login", fake_check_social_account_login)

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "xhs", "account_id": account["id"]}))

        assert created["session"]["status"] == "failed"
        assert "重新扫码登录" in created["session"]["message"]
        assert created["account_status"]["status"] == "limited"
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_session_uses_social_account_profile(monkeypatch, tmp_path):
    init_db()
    snapshots = {
        "login_sessions": _snapshot_table("login_sessions"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    seen: dict[str, Any] = {}
    try:
        account_profile = tmp_path / "account_profile"
        account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "standby",
                "profile_path": str(account_profile),
            }
        )
        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "抖音",
                "login_url": "https://www.douyin.com/",
                "profile_path": str(tmp_path / "global_profile"),
                "debug_port": 9323,
                "browser_path": "chrome",
            },
        )

        async def fake_start_qrcode_login_session_with_profile(session_id, platform, command):
            seen["profile_path"] = command["profile_path"]
            return {
                "ok": True,
                "qr_image": "data:image/png;base64,abc",
                "message": "请扫码登录",
                "profile_path": command["profile_path"],
            }

        monkeypatch.setattr(monitor_router, "start_qrcode_login_session_with_profile", fake_start_qrcode_login_session_with_profile)

        created = asyncio.run(monitor_router.create_platform_login_session({"platform": "dy", "account_id": account["id"]}))

        assert seen["profile_path"] == str(account_profile)
        assert created["session"]["account_id"] == account["id"]
        assert created["session"]["profile_path"] == str(account_profile)
        assert created["session"]["qr_image"].startswith("data:image")
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_login_session_list_account_id_can_reopen_account_profile(monkeypatch, tmp_path):
    init_db()
    snapshots = {
        "login_sessions": _snapshot_table("login_sessions"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    seen: dict[str, Any] = {}
    try:
        account_profile = tmp_path / "haian_dy_account_profile"
        account = save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "standby",
                "profile_path": str(account_profile),
            }
        )
        session = create_login_session(
            {
                "platform": "dy",
                "account_id": account["id"],
                "login_url": "https://www.douyin.com/",
                "profile_path": str(account_profile),
                "message": "二维码生成失败，请使用登录窗口兜底",
            }
        )

        monkeypatch.setattr(
            monitor_router,
            "build_login_browser_command",
            lambda platform: {
                "platform": platform,
                "platform_label": "抖音",
                "login_url": "https://www.douyin.com/",
                "profile_path": str(tmp_path / "default_profile"),
                "debug_port": 9323,
                "browser_path": "chrome",
            },
        )

        def fake_open_login_browser_with_command(command):
            seen["profile_path"] = command["profile_path"]
            return {**command, "pid": 23456, "message": "ok"}

        monkeypatch.setattr(monitor_router, "open_login_browser_with_command", fake_open_login_browser_with_command)

        listed = list_login_sessions(limit=1)[0]
        result = asyncio.run(monitor_router.platform_login_browser(listed["platform"], {"account_id": listed["account_id"]}))

        assert listed["id"] == session["id"]
        assert listed["account_id"] == account["id"]
        assert result["pid"] == 23456
        assert seen["profile_path"] == str(account_profile)
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_social_account_profile_path_auto_generated_when_empty():
    init_db()
    snapshot = _snapshot_table("social_accounts")
    try:
        account = save_social_account(
            {
                "name": "海安律所小红书采集号",
                "platform": "xhs",
                "login_type": "qrcode",
                "status": "standby",
            }
        )
        assert "account_profiles" in account["profile_path"]
        assert "海安律所小红书采集号" in account["profile_path"]
        assert account["login_capability_source"] == "平台采集服务"
        assert account["login_boundary"] == "media_crawler_only"
        assert account["captcha_policy"] == "report_only"
        assert "qrcode" in account["supported_login_types"]

        updated = save_social_account({**account, "profile_path": ""}, int(account["id"]))

        assert updated["profile_path"]
        assert str(account["id"]) in updated["profile_path"]
    finally:
        _restore_table("social_accounts", snapshot)


def test_social_account_login_type_must_follow_mediacrawler_capability():
    init_db()
    snapshot = _snapshot_table("social_accounts")
    try:
        with pytest.raises(ValueError, match="暂未开放手机号登录"):
            save_social_account(
                {
                    "name": "海安律所快手采集号",
                    "platform": "ks",
                    "login_type": "phone",
                    "status": "standby",
                }
            )

        with pytest.raises(ValueError, match="暂未开放手机号登录"):
            save_social_account(
                {
                    "name": "海安律所抖音采集号",
                    "platform": "dy",
                    "login_type": "phone",
                    "status": "standby",
                }
            )

        account = save_social_account({"name": "海安律所抖音采集号", "platform": "dy", "login_type": "qrcode", "status": "standby"})
        assert account["login_capability_source"] == "平台采集服务"
        assert account["login_boundary"] == "media_crawler_only"
        assert account["supported_login_types"] == ["qrcode", "cookie"]
    finally:
        _restore_table("social_accounts", snapshot)


def test_qrcode_poll_success_closes_browser_session(monkeypatch):
    class DummyContext:
        closed = False

        async def close(self):
            self.closed = True

    class DummyPlaywright:
        stopped = False

        async def stop(self):
            self.stopped = True

    context = DummyContext()
    playwright = DummyPlaywright()
    handle = login_qrcode_module.LoginSessionHandle(
        platform="dy",
        playwright=playwright,
        context=context,
        page=object(),
        profile_path="browser_data/cdp_dy_user_data_dir",
        created_at=datetime.now(timezone.utc),
    )
    login_qrcode_module.ACTIVE_LOGIN_SESSIONS[99999] = handle

    async def fake_is_logged_in(platform, context, page, login_baseline=""):
        return True

    monkeypatch.setattr(login_qrcode_module, "_is_logged_in", fake_is_logged_in)

    result = asyncio.run(login_qrcode_module.poll_qrcode_login_session(99999))

    assert result["success"] is True
    assert 99999 not in login_qrcode_module.ACTIVE_LOGIN_SESSIONS
    assert context.closed is True
    assert playwright.stopped is True


def test_ai_skip_env_prevents_external_ai_calls(monkeypatch):
    init_db()
    called = False

    async def fake_call_openai(cfg, prompt, payload):
        nonlocal called
        called = True
        raise RuntimeError("AI provider should not be called")

    monkeypatch.setenv("MONITOR_SKIP_AI_API", "true")
    monkeypatch.setattr("api.monitoring.ai._call_openai", fake_call_openai)

    result = asyncio.run(
        ai_module.evaluate_content(
            {"law_firm_name": "海安律所"},
            {"platform": "dy", "title": "海安律所投诉", "description": "退费迟迟没有处理"},
            [],
        )
    )

    assert called is False
    assert result["status"] == "pending_review"
    assert "未启用" in result["reason"]
    with pytest.raises(ValueError, match="未启用"):
        asyncio.run(
            run_ai_config_test(
                {
                    "provider": "openai",
                    "base_url": "https://example.com",
                    "api_key": "sk-test",
                    "model": "test-model",
                    "temperature": 0,
                }
            )
        )


def test_ai_test_route_skip_env_does_not_save_payload(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    try:
        save_ai_config(
            {
                "provider": "openai",
                "base_url": "https://saved.example.com",
                "api_key": "sk-saved",
                "model": "saved-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        before = get_ai_config()
        monkeypatch.setenv("MONITOR_SKIP_AI_API", "true")

        with pytest.raises(HTTPException) as exc:
            asyncio.run(
                monitor_router.test_ai_config(
                    {
                        "provider": "openai",
                        "base_url": "https://changed.example.com",
                        "api_key": "sk-changed",
                        "model": "changed-model",
                        "temperature": 0,
                        "prompt": "changed",
                    }
                )
            )
        after = get_ai_config()

        assert exc.value.status_code == 400
        assert "未启用" in str(exc.value.detail)
        assert after["base_url"] == before["base_url"]
        assert after["model"] == before["model"]
        assert after["last_test_status"] == before["last_test_status"]
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ai_skip_env_warns_without_blocking_preflight(monkeypatch):
    monkeypatch.setenv("MONITOR_SKIP_AI_API", "true")
    cfg = {
        "provider": "openai",
        "base_url": "https://example.com",
        "api_key": "sk-********test",
        "model": "test-model",
        "last_test_status": "success",
        "last_test_at": "2026-06-12T00:00:00+00:00",
    }
    job = {
        "id": 1,
        "enabled": True,
        "law_firm_name": "海安律所",
        "keywords": ["海安律所避雷"],
        "platforms": ["dy"],
        "recipients": ["target@example.com"],
    }
    monkeypatch.setattr(
        "api.monitoring.preflight.list_platform_status",
        lambda: [
            {
                "platform": "dy",
                "platform_label": "抖音",
                "login_type": "qrcode",
                "profile_exists": True,
                "has_cookies": False,
                "needs_login": False,
                "login_ready": True,
                "login_window_open": False,
            }
        ],
    )
    monkeypatch.setattr("api.monitoring.preflight.get_ai_config", lambda masked=True: cfg)
    monkeypatch.setattr(
        "api.monitoring.preflight.get_email_config",
        lambda masked=True: {"smtp_host": "smtp.example.com", "sender": "sender@example.com", "last_test_status": "success"},
    )

    preflight = build_job_preflight(job, [])

    assert readiness_module._ai_ready(cfg) is False
    assert "未启用" in readiness_module._ai_message(cfg)
    actions = readiness_module._next_actions([{"key": "ai_config", "ok": False}], [], set(), set())
    assert any("未启用" in action for action in actions)
    assert preflight["can_run"] is True
    assert any("未启用" in item for item in preflight["warnings"])


def test_job_preflight_uses_active_ai_profile_before_legacy_config(monkeypatch):
    init_db()
    profile_snapshot = _snapshot_table("ai_key_profiles")
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    try:
        save_ai_config({"provider": "openai", "base_url": "", "api_key": "", "model": ""})
        profile = save_ai_key_profile(
            {
                "name": "海安律所当前 AI 接入",
                "provider": "openai",
                "base_url": "https://ai.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": True,
            }
        )
        with get_conn() as conn:
            conn.execute(
                "UPDATE ai_key_profiles SET last_test_status='success', last_test_at=?, last_test_error='' WHERE id=?",
                ("2026-06-12T00:00:00+00:00", profile["id"]),
            )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {
                    "platform": "dy",
                    "platform_label": "抖音",
                    "login_type": "qrcode",
                    "profile_exists": True,
                    "has_cookies": False,
                    "needs_login": False,
                    "login_ready": True,
                    "login_window_open": False,
                }
            ],
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.get_email_config",
            lambda masked=True: {"smtp_host": "smtp.example.com", "sender": "sender@example.com", "last_test_status": "success"},
        )
        job = {
            "id": 1,
            "enabled": True,
            "law_firm_name": "海安律所",
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": ["target@example.com"],
        }

        preflight = build_job_preflight(job, [])
        ai_check = next(item for item in preflight["checks"] if item["key"] == "ai_config")

        assert ai_check["ok"] is True
        assert "默认 AI 接入最近测试通过" in ai_check["message"]
        assert not any("AI" in warning for warning in preflight["warnings"])
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ai_email_test_results_are_persisted_for_readiness(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    profile_snapshot = _snapshot_table("ai_key_profiles")
    email_snapshot = _snapshot_singleton_table("email_configs")

    async def fake_ai_test(payload):
        return {
            "is_related": True,
            "is_negative": True,
            "risk_level": "medium",
            "reason": "测试通过",
            "evidence_quotes": ["测试"],
            "recommended_action": "继续",
        }

    def fake_send_test_email(payload):
        return None

    try:
        _restore_table("ai_key_profiles", [])
        monkeypatch.setattr(monitor_router.ai, "test_ai", fake_ai_test)
        result = asyncio.run(
            monitor_router.test_ai_config(
                {
                    "provider": "openai",
                    "base_url": "https://example.com",
                    "api_key": "sk-test",
                    "model": "test-model",
                    "temperature": 0,
                    "prompt": DEFAULT_PROMPT,
                }
            )
        )
        assert result["config"]["last_test_status"] == "success"
        ai_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "ai_config")
        assert ai_check["ok"] is True

        save_ai_config(
            {
                "provider": "openai",
                "base_url": "https://example.com",
                "api_key": "",
                "model": "test-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        assert get_ai_config()["last_test_status"] == "success"
        ai_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "ai_config")
        assert ai_check["ok"] is True

        save_ai_config({"provider": "openai", "base_url": "https://example.com", "api_key": "sk-test", "model": "changed"})
        assert get_ai_config()["last_test_status"] == "untested"
        ai_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "ai_config")
        assert ai_check["ok"] is False

        monkeypatch.setattr(monitor_router, "send_test_email", fake_send_test_email)
        result = asyncio.run(
            monitor_router.test_email(
                {
                    "smtp_host": "smtp.example.com",
                    "smtp_port": 465,
                    "encryption": "ssl",
                    "sender": "sender@example.com",
                    "username": "sender@example.com",
                    "password": "smtp-password",
                    "default_recipients": ["target@example.com"],
                }
            )
        )
        assert result["config"]["last_test_status"] == "success"
        email_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "email_config")
        assert email_check["ok"] is True

        save_email_config(
            {
                "smtp_host": "smtp.example.com",
                "smtp_port": 465,
                "encryption": "ssl",
                "sender": "sender@example.com",
                "username": "sender@example.com",
                "password": "",
                "default_recipients": ["target@example.com"],
            }
        )
        assert get_email_config()["last_test_status"] == "success"
        email_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "email_config")
        assert email_check["ok"] is True

        save_email_config({"smtp_host": "smtp.example.com", "sender": "changed@example.com", "default_recipients": ["target@example.com"]})
        assert get_email_config()["last_test_status"] == "untested"
        email_check = next(check for check in get_readiness_status()["checks"] if check["key"] == "email_config")
        assert email_check["ok"] is False
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)


def test_ai_test_can_reuse_saved_config_when_payload_is_empty(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")

    async def fake_ai_test(payload):
        assert payload == {}
        return {
            "is_related": True,
            "is_negative": True,
            "risk_level": "medium",
            "reason": "测试通过",
            "evidence_quotes": ["测试"],
            "recommended_action": "继续",
        }

    try:
        save_ai_config(
            {
                "provider": "openai",
                "base_url": "https://example.com",
                "api_key": "sk-test",
                "model": "test-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
            }
        )
        monkeypatch.setattr(monitor_router.ai, "test_ai", fake_ai_test)

        result = asyncio.run(monitor_router.test_ai_config({}))

        assert result["config"]["last_test_status"] == "success"
        assert result["config"]["base_url"] == "https://example.com"
        assert result["config"]["model"] == "test-model"
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ai_config_api_exposes_default_prompt():
    init_db()
    result = asyncio.run(monitor_router.ai_config())

    assert result["default_prompt"] == DEFAULT_PROMPT
    assert "负面" in result["default_prompt"]
    assert result["prompt_sections"]["role"]
    assert any(item["field"] == "risk_level" for item in result["output_schema"])
    assert any(item["field"] == "recommended_action" for item in result["output_schema"])


def test_ai_evaluation_config_test_preserves_editable_sample_context(monkeypatch):
    seen: dict[str, Any] = {}

    async def fake_ai_test(payload):
        seen.update(payload)
        return {
            "is_related": True,
            "is_negative": True,
            "risk_level": "high",
            "reason": payload["sample_law_firm_name"],
            "evidence_quotes": [payload["sample_title"]],
            "recommended_action": "人工复核",
        }

    monkeypatch.setattr(monitor_router.ai, "ai_api_disabled", lambda: False)
    monkeypatch.setattr(monitor_router.ai, "test_ai", fake_ai_test)

    result = asyncio.run(
        monitor_router.test_ai_evaluation_config(
            {
                "prompt": "只按当前样例判断",
                "sample_law_firm_name": "平安",
                "sample_platform": "dy",
                "sample_source_keyword": "平安律师避雷",
                "sample_title": "平安律师避雷：退费拖了很久",
                "sample_text": "我想曝光一下。",
                "sample_comments": "扫码后仍然没有确认\n评论区有人补充投诉",
            }
        )
    )

    assert result["result"]["reason"] == "平安"
    assert seen["sample_law_firm_name"] == "平安"
    assert seen["sample_title"] == "平安律师避雷：退费拖了很久"
    assert seen["sample_comments"] == "扫码后仍然没有确认\n评论区有人补充投诉"


def test_ai_rule_profiles_can_be_managed_and_selected():
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    rule_snapshot = _snapshot_table("ai_rule_profiles")

    try:
        rule_a = save_ai_rule_profile({"name": "海安默认规则", "prompt": "规则 A", "is_active": True})
        rule_b = save_ai_rule_profile({"name": "投诉高敏规则", "prompt": "规则 B"})

        listed = list_ai_rule_profiles()
        assert any(item["id"] == rule_a["id"] for item in listed)
        assert any(item["id"] == rule_b["id"] for item in listed)
        assert get_ai_config()["prompt"] == "规则 A"

        active = set_active_ai_rule_profile(rule_b["id"])

        assert active["is_active"] is True
        assert get_ai_config()["prompt"] == "规则 B"
        assert next(item for item in list_ai_rule_profiles() if item["id"] == rule_a["id"])["is_active"] is False
    finally:
        _restore_table("ai_rule_profiles", rule_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ai_rule_profile_routes_expose_profiles_and_test_status(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    rule_snapshot = _snapshot_table("ai_rule_profiles")

    async def fake_ai_test(payload):
        assert payload["prompt"] == "规则测试 Prompt"
        return {
            "is_related": True,
            "is_negative": True,
            "risk_level": "medium",
            "reason": "测试通过",
            "evidence_quotes": ["测试"],
            "recommended_action": "继续复核",
        }

    try:
        monkeypatch.setattr(monitor_router.ai, "test_ai", fake_ai_test)
        created = asyncio.run(
            monitor_router.create_ai_rule_profile(
                {"name": "规则测试", "prompt": "规则测试 Prompt", "is_active": True}
            )
        )["profile"]

        listed = asyncio.run(monitor_router.ai_rule_profiles())
        assert any(item["id"] == created["id"] for item in listed["profiles"])
        assert listed["output_schema"]

        tested = asyncio.run(monitor_router.test_ai_rule_profile(created["id"], {}))

        assert tested["result"]["risk_level"] == "medium"
        refreshed = next(item for item in list_ai_rule_profiles() if item["id"] == created["id"])
        assert refreshed["last_test_status"] == "success"
    finally:
        _restore_table("ai_rule_profiles", rule_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_failed_ai_test_is_recorded_after_saving_valid_config(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")

    async def failing_ai_test(payload):
        raise RuntimeError("provider rejected request")

    try:
        monkeypatch.setattr(monitor_router.ai, "test_ai", failing_ai_test)
        with pytest.raises(HTTPException):
            asyncio.run(
                monitor_router.test_ai_config(
                    {
                        "provider": "openai",
                        "base_url": "https://example.com",
                        "api_key": "sk-test",
                        "model": "test-model",
                        "temperature": 0,
                    }
                )
            )
        cfg = get_ai_config()
        assert cfg["last_test_status"] == "failed"
        assert "RuntimeError" in cfg["last_test_error"]
    finally:
        _restore_singleton_table("ai_configs", ai_snapshot)


def test_ingest_dedupes_and_report_keeps_pending_review(monkeypatch):
    asyncio.run(_dedupe_and_report_check(monkeypatch))


def test_dedupe_is_isolated_per_monitor_job():
    init_db()
    base = {
        "aliases": [],
        "exclude_words": [],
        "keywords": ["同ID测试律所避雷"],
        "platforms": ["dy"],
        "recipients": [],
        "enable_comments": False,
        "time_window_type": "recent_1d",
        "frequency": "daily",
        "email_time": "09:00",
        "enabled": True,
    }
    job_a = save_job({**base, "law_firm_name": "同ID测试律所A"})
    job_b = save_job({**base, "law_firm_name": "同ID测试律所B"})
    now_ts = int(datetime.now(timezone.utc).timestamp())
    item = {
        "aweme_id": "pytest_shared_content_001",
        "title": "同ID测试律所避雷",
        "desc": "服务争议",
        "create_time": now_ts,
    }

    run_a1 = create_run(job_a["id"])
    first_a = ingest_outputs(job_a, run_a1, "dy", [item], [])
    run_a2 = create_run(job_a["id"])
    second_a = ingest_outputs(job_a, run_a2, "dy", [item], [])
    run_b1 = create_run(job_b["id"])
    first_b = ingest_outputs(job_b, run_b1, "dy", [item], [])

    _cleanup_test_records(job_a["id"], "pytest_shared_content_001")
    _cleanup_test_records(job_b["id"], "pytest_shared_content_001")

    assert first_a["new_contents"] == 1
    assert second_a["new_contents"] == 0
    assert first_b["new_contents"] == 1


def test_exclude_words_filter_before_insert():
    init_db()
    job = save_job(
        {
            "law_firm_name": "排除测试律所",
            "aliases": [],
            "exclude_words": ["招聘"],
            "keywords": ["排除测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    now_ts = int(datetime.now(timezone.utc).timestamp())
    run_id = create_run(job["id"])
    result = ingest_outputs(
        job,
        run_id,
        "dy",
        [
            {
                "aweme_id": "pytest_exclude_keep_001",
                "title": "排除测试律所避雷",
                "desc": "服务争议",
                "create_time": now_ts,
            },
            {
                "aweme_id": "pytest_exclude_drop_001",
                "title": "排除测试律所招聘",
                "desc": "招聘信息",
                "create_time": now_ts,
            },
        ],
        [],
    )

    _cleanup_test_records(job["id"], "pytest_exclude_keep_001")
    _cleanup_test_records(job["id"], "pytest_exclude_drop_001")

    assert result["raw_contents"] == 2
    assert result["filtered_contents"] == 1
    assert result["excluded_contents"] == 1
    assert result["new_contents"] == 1


def test_unrelated_negative_is_not_reported_as_risk(monkeypatch):
    asyncio.run(_unrelated_negative_check(monkeypatch))


def test_report_includes_platform_status_and_failure_reason():
    init_db()
    job = save_job(
        {
            "law_firm_name": "报告失败测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["报告失败测试律所避雷"],
            "platforms": ["dy", "ks"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    run_id = create_run(job["id"])
    report = create_report(
        run_id,
        job,
        {
            "platforms": ["dy", "ks"],
            "failed_platforms": ["ks"],
            "platform_results": {
                "dy": {
                    "status": "success",
                    "raw_contents": 2,
                    "new_contents": 1,
                    "proxy": {"proxy_id": 8, "proxy_name": "华东采集代理", "provider": "manual"},
                },
                "ks": {"status": "failed", "error": "检测到登录态失效"},
            },
            "new_contents": 1,
            "negative_count": 0,
            "high_count": 0,
        },
    )
    html = Path(report["html_path"]).read_text(encoding="utf-8")
    markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")
    _cleanup_test_records(job["id"], "")

    assert "平台采集状态" in html
    assert "华东采集代理 / manual #8" in html
    assert "快手" in html
    assert "检测到登录态失效" in html
    assert "平台采集状态" in markdown
    assert "代理：华东采集代理 / manual #8" in markdown
    assert "快手：失败" in markdown


def test_leads_api_lists_pending_review_items():
    result = asyncio.run(create_sample_report())
    try:
        leads = list_leads(50)
        api_result = asyncio.run(monitor_router.leads(risk="pending"))["leads"]
        report_result = asyncio.run(monitor_router.reports(risk="pending"))["reports"]
        no_risk_reports = asyncio.run(monitor_router.reports(risk="none"))["reports"]
    finally:
        _cleanup_test_records(result["job"]["id"], f"selftest_negative_{result['run_id']}")
        _cleanup_test_records(result["job"]["id"], f"selftest_excluded_{result['run_id']}")

    assert any(item["content_id"] == f"selftest_negative_{result['run_id']}" for item in leads)
    assert any(item["content_id"] == f"system-check-{result['run_id']}" for item in api_result)
    assert all("selftest" not in item["content_id"] for item in api_result)
    assert all(item["eval_status"] == "pending_review" for item in api_result)
    assert any(item["id"] == result["report"]["id"] for item in report_result)
    assert next(item for item in report_result if item["id"] == result["report"]["id"])["summary"]["pending_review_count"] == 1
    assert all(item["id"] != result["report"]["id"] for item in no_risk_reports)


def test_selftest_report_generates_downloadable_artifacts():
    asyncio.run(_selftest_report_check())


def test_internal_selftest_jobs_are_hidden_from_operator_job_list():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
            "is_internal": True,
        }
    )
    visible_jobs = list_jobs()
    all_jobs = list_jobs(include_internal=True)
    _cleanup_test_records(job["id"], "")

    assert all(j["id"] != job["id"] for j in visible_jobs)
    assert any(j["id"] == job["id"] and j["is_internal"] for j in all_jobs)


def test_selftest_jobs_are_hidden_by_run_summary_marker():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    run_id = create_run(job["id"])
    try:
        finish_run(run_id, "selftest", {"selftest": True, "law_firm_name": "海安律所"})
        mark_selftest_jobs_internal()
        visible_jobs = list_jobs()
        all_jobs = list_jobs(include_internal=True)
    finally:
        _cleanup_test_records(job["id"], "")

    assert all(j["id"] != job["id"] for j in visible_jobs)
    assert any(j["id"] == job["id"] and j["is_internal"] for j in all_jobs)


def test_readiness_status_reports_checks():
    init_db()
    status = get_readiness_status()
    keys = {check["key"] for check in status["checks"]}

    assert {"platform_profiles", "ai_config", "email_config", "selftest_report", "real_report"} <= keys
    assert isinstance(status["ready"], bool)
    assert isinstance(status["next_actions"], list)
    assert len(status["platforms"]) == 3
    assert all("label" in check and "ok" in check and "message" in check for check in status["checks"])


def test_readiness_platform_profiles_only_require_douyin_but_preflight_checks_selected_platform(monkeypatch):
    init_db()
    job = {
        "id": 123,
        "enabled": True,
        "keywords": ["海安律所避雷"],
        "platforms": ["ks"],
        "recipients": ["target@example.com"],
    }
    monkeypatch.setattr(
        readiness_module,
        "list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": True},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False},
        ],
    )
    monkeypatch.setattr(
        "api.monitoring.preflight.list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": True},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False},
        ],
    )

    status = get_readiness_status()
    platform_check = next(check for check in status["checks"] if check["key"] == "platform_profiles")
    preflight = build_job_preflight(job, [])

    assert platform_check["ok"] is True
    assert "抖音登录配置可用" in platform_check["message"]
    assert "快手" in platform_check["message"]
    assert any("扩展平台资源" in action and "快手" in action for action in status["next_actions"])
    assert preflight["can_run"] is False
    assert any("重新登录" in blocker and "快手" in blocker for blocker in preflight["blockers"])


def test_readiness_and_preflight_warn_when_login_window_is_still_open(monkeypatch):
    init_db()
    job = {
        "id": 123,
        "enabled": True,
        "keywords": ["测试律所避雷"],
        "platforms": ["dy"],
        "recipients": ["target@example.com"],
    }
    statuses = [
        {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": True},
        {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
        {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
    ]
    monkeypatch.setattr(readiness_module, "list_platform_status", lambda: statuses)
    monkeypatch.setattr("api.monitoring.preflight.list_platform_status", lambda: statuses)

    readiness = get_readiness_status()
    preflight = build_job_preflight(job, [])

    platform_check = next(check for check in readiness["checks"] if check["key"] == "platform_profiles")
    assert platform_check["ok"] is False
    assert "登录窗口未关闭" in platform_check["message"]
    assert any("关闭" in action and "抖音" in action for action in readiness["next_actions"])
    assert preflight["can_run"] is False
    assert any("关闭登录窗口" in blocker for blocker in preflight["blockers"])


def test_readiness_and_preflight_block_missing_web_profile(monkeypatch):
    statuses = [
        {
            "platform": "dy",
            "platform_label": "抖音",
            "login_type": "qrcode",
            "profile_exists": True,
            "needs_login": False,
            "login_ready": True,
            "login_window_open": False,
        },
        {
            "platform": "ks",
            "platform_label": "快手",
            "login_type": "qrcode",
            "profile_exists": True,
            "needs_login": False,
            "login_ready": True,
            "login_window_open": False,
        },
        {
            "platform": "xhs",
            "platform_label": "小红书",
            "login_type": "qrcode",
            "profile_exists": False,
            "login_material_ready": False,
            "needs_login": True,
            "login_ready": False,
            "login_window_open": False,
        },
    ]
    monkeypatch.setattr(readiness_module, "list_platform_status", lambda: statuses)
    monkeypatch.setattr("api.monitoring.preflight.list_platform_status", lambda: statuses)

    readiness = get_readiness_status()
    preflight = build_job_preflight(
        {"id": 1009, "enabled": True, "keywords": ["海安律所投诉"], "platforms": ["xhs"], "recipients": ["target@example.com"]},
        [],
    )
    platform_check = next(check for check in readiness["checks"] if check["key"] == "platform_profiles")

    assert platform_check["ok"] is True
    assert "抖音登录配置可用" in platform_check["message"]
    assert "小红书网页登录态待准备" in platform_check["message"]
    assert any("扩展平台资源" in action and "小红书网页登录态待准备" in action for action in readiness["next_actions"])
    assert preflight["can_run"] is False
    assert any("请先重新登录小红书账号" in blocker for blocker in preflight["blockers"])


def test_job_preflight_blocks_active_account_with_disabled_proxy(monkeypatch):
    init_db()
    snapshots = {
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    statuses = [
        {"platform": "dy", "platform_label": "抖音", "login_type": "qrcode", "profile_exists": True, "needs_login": False, "login_window_open": False},
        {"platform": "ks", "platform_label": "快手", "login_type": "qrcode", "profile_exists": True, "needs_login": False, "login_window_open": False},
        {"platform": "xhs", "platform_label": "小红书", "login_type": "qrcode", "profile_exists": True, "needs_login": False, "login_window_open": False},
    ]
    monkeypatch.setattr("api.monitoring.preflight.list_platform_status", lambda: statuses)
    try:
        proxy = save_proxy_profile(
            {
                "name": "海安律所停用代理",
                "provider": "manual",
                "proxy_url": "http://user:pass@127.0.0.1:8081",
                "status": "disabled",
                "max_concurrency": 1,
            }
        )
        save_social_account(
            {
                "name": "海安律所抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "proxy_id": proxy["id"],
            }
        )

        preflight = build_job_preflight(
            {"id": 1010, "enabled": True, "keywords": ["海安律所避雷"], "platforms": ["dy"], "recipients": ["target@example.com"]},
            [],
        )

        assert preflight["can_run"] is False
        assert any("绑定代理已停用" in blocker and "抖音" in blocker for blocker in preflight["blockers"])
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_job_preflight_warns_active_account_with_limited_proxy_error(monkeypatch):
    init_db()
    snapshots = {
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    statuses = [
        {"platform": "xhs", "platform_label": "小红书", "login_type": "qrcode", "profile_exists": True, "needs_login": False, "login_window_open": False},
    ]
    monkeypatch.setattr("api.monitoring.preflight.list_platform_status", lambda: statuses)
    try:
        proxy = save_proxy_profile(
            {
                "name": "海安律所受限代理",
                "provider": "manual",
                "proxy_url": "http://user:pass@127.0.0.1:8081",
                "status": "limited",
                "max_concurrency": 1,
                "last_error": "timeout with password=hunter2",
            }
        )
        save_social_account(
            {
                "name": "海安律所小红书采集号",
                "platform": "xhs",
                "login_type": "qrcode",
                "status": "active",
                "proxy_id": proxy["id"],
            }
        )

        preflight = build_job_preflight(
            {"id": 1011, "enabled": True, "keywords": ["海安律所投诉"], "platforms": ["xhs"], "recipients": ["target@example.com"]},
            [],
        )

        assert preflight["can_run"] is True
        assert any("绑定代理状态为受限" in warning for warning in preflight["warnings"])
        assert any("最近有错误" in warning and "hunter2" not in warning for warning in preflight["warnings"])
    finally:
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)


def test_doctor_reports_deployment_diagnostics():
    init_db()
    status = run_doctor()
    keys = {check["key"] for check in status["checks"]}

    assert {"project_files", "uv", "data_dir", "database", "gitignore_runtime_data", "platform_login", "browser_profiles", "ai_config", "email_config", "reports"} <= keys
    assert "readiness" in status
    assert "paths" in status
    assert status["paths"]["monitor_data_dir"]
    assert isinstance(status["recommendations"], list)
    login_check = next(check for check in status["checks"] if check["key"] == "platform_login")
    assert login_check["ok"] is True
    assert "平台采集服务" in login_check["message"]
    capabilities = login_check["capabilities"]
    assert all(item["bridge_role"] == "capture_qrcode_and_forward_status_only" for item in capabilities)
    assert all(str(item["login_class"]).startswith("media_platform.") for item in capabilities)
    assert all(str(item["qrcode_prepare_method"]).endswith(".prepare_qrcode_login") for item in capabilities)
    assert all(item["qrcode_capture_method"] == "tools.utils.find_login_qrcode" for item in capabilities)


def test_doctor_checks_gitignore_runtime_data(monkeypatch, tmp_path):
    (tmp_path / ".gitignore").write_text("/browser_data/\n.env\n", encoding="utf-8")
    monkeypatch.setattr("api.monitoring.doctor.PROJECT_ROOT", tmp_path)

    status = run_doctor()
    check = next(item for item in status["checks"] if item["key"] == "gitignore_runtime_data")

    assert check["ok"] is False
    assert "/monitor_data/" in check["message"]
    assert "*.log" in check["message"]


def test_env_examples_cover_monitor_runtime_knobs():
    required = [
        "MONITOR_DATA_DIR",
        "MONITOR_BROWSER_DATA_DIR",
        "MONITOR_CRAWLER_HEADLESS",
        "MONITOR_CDP_CONNECT_EXISTING",
        "MONITOR_LOGIN_QR_HEADLESS",
        "MONITOR_LOGIN_QR_TIMEOUT_MS",
        "MONITOR_LOGIN_QR_TTL_SECONDS",
        "MONITOR_CDP_DEBUG_PORT_DY",
        "MONITOR_CDP_DEBUG_PORT_KS",
        "MONITOR_CDP_DEBUG_PORT_XHS",
        "MONITOR_CRAWLER_TIMEOUT_SECONDS",
        "MONITOR_CRAWLER_MAX_RETRIES",
        "MONITOR_CRAWLER_RETRY_DELAY_SECONDS",
        "MONITOR_JOB_LOCK_TTL_SECONDS",
        "MONITOR_SKIP_AI_API",
        "MONITOR_DISABLE_SCHEDULER",
    ]
    paths = [
        Path(".env.example"),
        Path("deploy/systemd/legal-sentiment-monitor.env.example"),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        missing = [name for name in required if name not in text]
        assert not missing, f"{path} missing {missing}"


def test_doctor_flags_non_mediacrawler_login_boundary(monkeypatch):
    def fake_capabilities():
        return [
            {
                "platform": "dy",
                "source": "Custom",
                "boundary": "custom",
                "bridge_role": "custom_login",
                "login_class": "custom.DouyinLogin",
                "qrcode_prepare_method": "custom.prepare",
                "qrcode_capture_method": "custom.capture",
                "qrcode_supported": True,
                "login_state": {"cookie_rules": {"LOGIN_STATUS": "1"}},
                "manual_verification": {"text_markers": {"captcha": ["验证"]}},
            },
            {
                "platform": "ks",
                "source": "MediaCrawler",
                "boundary": "media_crawler_only",
                "bridge_role": "capture_qrcode_and_forward_status_only",
                "login_class": "media_platform.kuaishou.login.KuaishouLogin",
                "qrcode_prepare_method": "KuaishouLogin.prepare_qrcode_login",
                "qrcode_capture_method": "tools.utils.find_login_qrcode",
                "qrcode_supported": True,
                "login_state": {"cookie_rules": {"passToken": None}},
                "manual_verification": {"text_markers": {"captcha": ["验证"]}},
            },
            {
                "platform": "xhs",
                "source": "MediaCrawler",
                "boundary": "media_crawler_only",
                "bridge_role": "capture_qrcode_and_forward_status_only",
                "login_class": "media_platform.xhs.login.XiaoHongShuLogin",
                "qrcode_prepare_method": "XiaoHongShuLogin.prepare_qrcode_login",
                "qrcode_capture_method": "tools.utils.find_login_qrcode",
                "qrcode_supported": True,
                "login_state": {"session_cookie": "web_session"},
                "manual_verification": {"text_markers": {"captcha": ["验证"]}},
            },
        ]

    monkeypatch.setattr("api.monitoring.doctor.list_mediacrawler_login_capabilities", fake_capabilities)

    status = run_doctor()
    login_check = next(check for check in status["checks"] if check["key"] == "platform_login")

    assert login_check["ok"] is False
    assert "抖音登录能力来源异常" in login_check["message"]
    assert "抖音边界不是 media_crawler_only" in login_check["message"]
    assert "抖音登录桥接角色不是只回传二维码和状态" in login_check["message"]
    assert "抖音缺少平台登录适配" in login_check["message"]
    assert "抖音缺少二维码准备能力" in login_check["message"]
    assert "抖音二维码获取能力异常" in login_check["message"]


def test_doctor_report_check_uses_full_report_history(monkeypatch):
    reports = [
        {
            "id": 30,
            "summary": {
                "platform_results": {
                    "dy": {"status": "success", "raw_contents": 1},
                    "ks": {"status": "success", "raw_contents": 1},
                    "xhs": {"status": "success", "raw_contents": 1},
                }
            },
        },
        {"id": 1, "summary": {"selftest": True}},
    ]
    monkeypatch.setattr("api.monitoring.doctor.list_reports", lambda limit=100: reports)

    status = run_doctor()
    report_check = next(check for check in status["checks"] if check["key"] == "reports")

    assert report_check["ok"] is True
    assert "系统自检报告和抖音采集报告" in report_check["message"]


def test_doctor_report_check_does_not_accept_partial_real_report(monkeypatch):
    reports = [
        {"id": 30, "summary": {"platform_results": {"dy": {"status": "success", "raw_contents": 1}}}},
        {"id": 1, "summary": {"selftest": True}},
    ]
    monkeypatch.setattr("api.monitoring.doctor.list_reports", lambda limit=100: reports)

    status = run_doctor()
    report_check = next(check for check in status["checks"] if check["key"] == "reports")

    assert report_check["ok"] is True
    assert "抖音采集报告" in report_check["message"]
    assert not any("selftest-report" in tip for tip in status["recommendations"])


def test_doctor_does_not_defer_job_recommendation_for_optional_platform_login(monkeypatch):
    monkeypatch.setattr(
        "api.monitoring.doctor.list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_ready": True},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": True, "login_ready": False},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_ready": True},
        ],
    )
    monkeypatch.setattr(
        readiness_module,
        "list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_ready": True},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": True, "login_ready": False},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_ready": True},
        ],
    )
    monkeypatch.setattr("api.monitoring.doctor.list_jobs", lambda: [{"id": 1007, "enabled": False}])

    status = run_doctor()

    browser_check = next(check for check in status["checks"] if check["key"] == "browser_profiles")
    assert browser_check["ok"] is True
    assert "扩展平台待维护" in browser_check["message"]
    assert any(tip == "在任务管理页创建并启用至少一个监控任务。" for tip in status["recommendations"])
    assert not any("登录态恢复后" in tip for tip in status["recommendations"])


def test_doctor_reports_ai_skip_mode(monkeypatch):
    init_db()
    monkeypatch.setenv("MONITOR_SKIP_AI_API", "true")

    status = run_doctor()
    ai_check = next(check for check in status["checks"] if check["key"] == "ai_config")

    assert ai_check["ok"] is False
    assert "未启用" in ai_check["message"]
    assert any("未启用" in tip for tip in status["recommendations"])


def test_doctor_lists_optional_login_window_as_maintenance(monkeypatch):
    init_db()
    statuses = [
        {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_ready": True, "login_window_open": False},
        {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_ready": False, "login_window_open": True},
        {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_ready": True, "login_window_open": False},
    ]
    monkeypatch.setattr("api.monitoring.doctor.list_platform_status", lambda: statuses)
    monkeypatch.setattr(readiness_module, "list_platform_status", lambda: statuses)

    status = run_doctor()
    browser_check = next(check for check in status["checks"] if check["key"] == "browser_profiles")

    assert browser_check["ok"] is True
    assert "扩展平台待维护" in browser_check["message"]
    assert "快手登录窗口待关闭" in browser_check["message"]
    assert not any("关闭" in tip and "快手" in tip for tip in status["recommendations"] if not tip.startswith("扩展平台资源"))


def test_doctor_blocks_when_required_login_window_is_still_open(monkeypatch):
    init_db()
    statuses = [
        {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_ready": False, "login_window_open": True},
        {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_ready": True, "login_window_open": False},
        {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_ready": True, "login_window_open": False},
    ]
    monkeypatch.setattr("api.monitoring.doctor.list_platform_status", lambda: statuses)
    monkeypatch.setattr(readiness_module, "list_platform_status", lambda: statuses)

    status = run_doctor()
    browser_check = next(check for check in status["checks"] if check["key"] == "browser_profiles")

    assert browser_check["ok"] is False
    assert "登录窗口未关闭" in browser_check["message"]
    assert "抖音" in browser_check["message"]
    assert any("关闭" in tip and "抖音" in tip for tip in status["recommendations"])


def test_doctor_api_exposes_deployment_diagnostics():
    init_db()
    status = asyncio.run(monitor_router.doctor())

    assert "checks" in status
    assert "readiness" in status
    assert "recommendations" in status
    assert "paths" in status
    visible = json.dumps(status, ensure_ascii=False)
    for forbidden in [
        "MediaCrawler",
        "media_platform.",
        "media_crawler_only",
        "tools.utils",
        "prepare_qrcode_login",
        "MONITOR_SKIP_AI_API",
        "selftest",
        "Profile",
        "离线模式",
        "离线自检",
        "uv 命令",
        "uv.EXE",
        "main.py",
        "docs/deployment_runbook.md",
    ]:
        assert forbidden not in visible


def test_readiness_dashboard_and_checklist_are_customer_safe():
    init_db()
    readiness = asyncio.run(monitor_router.readiness())
    dashboard = asyncio.run(monitor_router.dashboard())
    checklist = asyncio.run(monitor_router.system_checklist())

    assert "latest_system_check_report_id" in readiness
    assert "latest_selftest_report_id" not in readiness
    assert "latest_system_check_report_id" in dashboard["readiness"]
    assert "latest_system_check_report_id" in checklist
    visible = json.dumps({"readiness": readiness, "dashboard": dashboard, "checklist": checklist}, ensure_ascii=False)
    for forbidden in [
        "MediaCrawler",
        "MONITOR_SKIP_AI_API",
        "selftest",
        "Profile",
        "离线模式",
        "离线自检",
        "html_path",
        "markdown_path",
        "excel_path",
        "E:\\",
        "main.py",
        "debug_port",
    ]:
        assert forbidden not in visible


def test_smoke_check_generates_selftest_artifacts_and_summaries():
    result = asyncio.run(run_smoke_check())
    selftest = result["selftest"]
    artifacts = selftest["artifacts"]
    try:
        report = get_report(selftest["report_id"])
    finally:
        _cleanup_test_records(selftest["job_id"], f"selftest_negative_{selftest['run_id']}")
        _cleanup_test_records(selftest["job_id"], f"selftest_excluded_{selftest['run_id']}")

    assert result["ok"] is True
    assert report is not None
    assert artifacts["html"]["exists"] is True
    assert artifacts["excel"]["exists"] is True
    assert artifacts["markdown"]["exists"] is True
    assert artifacts["html"]["download_url"].endswith(f"/download?type=html")
    assert "failed_checks" in result["doctor"]
    assert "next_actions" in result["readiness"]
    assert "不调用真实平台" in result["note"]


def test_smoke_api_returns_local_smoke_result():
    result = asyncio.run(monitor_router.smoke())["result"]
    system_check = result["system_check"]
    try:
        report = get_report(system_check["report_id"])
    finally:
        _cleanup_test_records(report["job_id"], f"selftest_negative_{system_check['run_id']}")
        _cleanup_test_records(report["job_id"], f"selftest_excluded_{system_check['run_id']}")

    assert result["ok"] is True
    assert report is not None
    assert result["system_check"]["artifacts"]["markdown"]["download_url"].endswith("type=markdown")
    visible = json.dumps(result, ensure_ascii=False)
    for forbidden in ["MediaCrawler", "selftest", "本地自测", "smoke", "MONITOR_SKIP_AI_API"]:
        assert forbidden not in visible


def test_system_check_report_api_returns_operator_summary():
    result = asyncio.run(monitor_router.report_system_check())["result"]
    report = get_report(result["report_id"])
    try:
        assert result["ok"] is True
        assert result["artifacts"]["html"]["download_url"].endswith("type=html")
        assert result["artifacts"]["excel"]["exists"] is True
        assert result["artifacts"]["markdown"]["exists"] is True
        visible = json.dumps(result, ensure_ascii=False)
        for forbidden in ["MediaCrawler", "selftest", "本地自测", "html_path", "markdown_path", "excel_path"]:
            assert forbidden not in visible
    finally:
        _cleanup_test_records(report["job_id"], f"selftest_negative_{result['run_id']}")
        _cleanup_test_records(report["job_id"], f"selftest_excluded_{result['run_id']}")


def test_legacy_selftest_report_route_is_customer_safe():
    result = asyncio.run(monitor_router.report_selftest())["result"]
    report = get_report(result["report_id"])
    try:
        assert result["ok"] is True
        assert result["artifacts"]["html"]["download_url"].endswith("type=html")
        visible = json.dumps(result, ensure_ascii=False)
        for forbidden in ["MediaCrawler", "selftest", "本地自测", "html_path", "markdown_path", "excel_path", "E:\\"]:
            assert forbidden not in visible
    finally:
        _cleanup_test_records(report["job_id"], f"selftest_negative_{result['run_id']}")
        _cleanup_test_records(report["job_id"], f"selftest_excluded_{result['run_id']}")


def test_cli_smoke_command_runs_local_smoke(monkeypatch):
    result = asyncio.run(cli_module._run_command(cli_module.build_parser().parse_args(["smoke"])))
    selftest = result["selftest"]
    try:
        report = get_report(selftest["report_id"])
    finally:
        _cleanup_test_records(selftest["job_id"], f"selftest_negative_{selftest['run_id']}")
        _cleanup_test_records(selftest["job_id"], f"selftest_excluded_{selftest['run_id']}")

    assert result["ok"] is True
    assert report is not None
    assert result["selftest"]["artifacts"]["excel"]["exists"] is True


def test_scheduler_is_disabled_for_multi_worker_env(monkeypatch):
    monkeypatch.setenv("WEB_CONCURRENCY", "2")
    monkeypatch.setattr(scheduler_module, "_apscheduler", None)
    monkeypatch.setattr(scheduler_module, "_scheduler_task", None)

    assert "多 worker" in scheduler_disabled_reason()
    asyncio.run(scheduler_module.start_scheduler())
    status = run_doctor()
    scheduler_check = next(check for check in status["checks"] if check["key"] == "scheduler_mode")

    assert scheduler_module._apscheduler is None
    assert scheduler_module._scheduler_task is None
    assert scheduler_check["ok"] is False
    assert "多 worker" in scheduler_check["message"]


def test_scheduler_status_api_exposes_internal_mode(monkeypatch):
    monkeypatch.delenv("MONITOR_DISABLE_SCHEDULER", raising=False)
    monkeypatch.delenv("WEB_CONCURRENCY", raising=False)
    monkeypatch.delenv("UVICORN_WORKERS", raising=False)

    status = scheduler_status()
    api_status = asyncio.run(monitor_router.monitor_scheduler_status())

    assert status["enabled"] is True
    assert status["mode"] == "internal"
    assert "60 秒" in status["message"]
    assert api_status["enabled"] is True


def test_scheduler_tick_skips_template_jobs_and_continues(monkeypatch):
    calls: list[int] = []
    skipped: list[tuple[int, str]] = []
    schedule_updates: list[tuple[int, str | None]] = []
    jobs = [
        {
            "id": 1,
            "enabled": True,
            "law_firm_name": "请改成目标律所名称",
            "keywords": ["目标律所避雷"],
            "platforms": ["dy"],
            "frequency": "daily",
            "email_time": "00:00",
            "last_run_at": None,
        },
        {
            "id": 2,
            "enabled": True,
            "law_firm_name": "海安律所",
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "frequency": "daily",
            "email_time": "00:00",
            "last_run_at": None,
        },
    ]

    monkeypatch.setattr(scheduler_module, "list_jobs", lambda: jobs)
    monkeypatch.setattr(
        "api.monitoring.preflight.list_platform_status",
        lambda: [
            {
                "platform": "dy",
                "platform_label": "抖音",
                "login_type": "qrcode",
                "profile_exists": True,
                "needs_login": False,
                "login_ready": True,
                "login_window_open": False,
            }
        ],
    )
    monkeypatch.setattr(scheduler_module, "set_job_schedule_state", lambda job_id, value: schedule_updates.append((job_id, value)))
    monkeypatch.setattr(scheduler_module, "launch_job", lambda job_id, source="scheduler": calls.append(job_id))
    monkeypatch.setattr(scheduler_module, "record_skipped_run", lambda job_id, reason, summary=None: skipped.append((job_id, reason)))

    asyncio.run(scheduler_module.tick())

    assert calls == [2]
    assert skipped and skipped[0][0] == 1
    assert [job_id for job_id, _ in schedule_updates] == [1, 2]


def test_scheduler_tick_blocks_preflight_and_records_skipped_run(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    runs_snapshot = _snapshot_table("crawl_runs")
    try:
        _clear_monitor_jobs()
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "00:00",
                "enabled": True,
            }
        )
        calls: list[int] = []
        monkeypatch.setattr(scheduler_module, "launch_job", lambda job_id, source="scheduler": calls.append(job_id))
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": True},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        asyncio.run(scheduler_module.tick())
        runs = [run for run in list_runs(0) if run["job_id"] == job["id"]]

        assert calls == []
        assert runs
        assert runs[0]["status"] == "skipped"
        assert "运行前检查未通过" in (runs[0]["error_message"] or "")
        assert "关闭登录窗口" in (runs[0]["error_message"] or "")
        assert runs[0]["summary"]["skip_type"] == "preflight_blocked"
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_table("crawl_runs", runs_snapshot)


def test_record_skipped_run_deduplicates_recent_same_reason():
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    runs_snapshot = _snapshot_table("crawl_runs")
    try:
        _clear_monitor_jobs()
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所退费"],
                "platforms": ["dy"],
                "recipients": [],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": True,
            }
        )
        first = record_skipped_run(job["id"], "同一原因", {"law_firm_name": "海安律所"})
        second = record_skipped_run(job["id"], "同一原因", {"law_firm_name": "海安律所"})
        third = record_skipped_run(job["id"], "另一个原因", {"law_firm_name": "海安律所"})

        assert second == first
        assert third != first
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_table("crawl_runs", runs_snapshot)


def test_skipped_run_has_operator_display_fields():
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    runs_snapshot = _snapshot_table("crawl_runs")
    try:
        _clear_monitor_jobs()
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所投诉"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": True,
            }
        )
        reason = "运行前检查未通过：请先重新登录再运行采集：抖音"
        run_id = record_skipped_run(
            job["id"],
            reason,
            {
                "law_firm_name": "海安律所",
                "platforms": ["dy"],
                "keywords": ["海安律所投诉"],
                "skip_type": "preflight_blocked",
            },
        )
        run = get_run(run_id)
        dashboard = get_dashboard_summary()

        assert run["status"] == "skipped"
        assert run["display_status"] == "预检拦截"
        assert run["display_error"] == reason
        assert run["display_law_firm_name"] == "海安律所"
        assert dashboard["skipped_runs_recent"] >= 1
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_table("crawl_runs", runs_snapshot)


def test_job_preflight_warns_but_allows_missing_ai_email(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "预检测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["预检测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    profile_snapshot = _snapshot_table("ai_key_profiles")
    email_snapshot = _snapshot_singleton_table("email_configs")

    try:
        _restore_table("ai_key_profiles", [])
        save_ai_config({"provider": "openai", "base_url": "", "api_key": "", "model": ""})
        save_email_config({"smtp_host": "", "sender": "", "default_recipients": []})
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False},
            ],
        )

        preflight = build_job_preflight(job, [])
        api_result = asyncio.run(monitor_router.job_preflight(job["id"]))["preflight"]
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)
        _cleanup_test_records(job["id"], "")

    assert preflight["can_run"] is True
    assert preflight["ready"] is False
    assert any("AI" in item for item in preflight["warnings"])
    assert any("收件人" in item for item in preflight["warnings"])
    assert api_result["can_run"] is True


def test_job_preflight_blocks_missing_platform_search_terms_not_missing_ai_email(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    profile_snapshot = _snapshot_table("ai_key_profiles")
    email_snapshot = _snapshot_singleton_table("email_configs")
    job = {
        "id": 1008,
        "law_firm_name": "海安律所",
        "aliases": ["海安律师事务所"],
        "exclude_words": ["招聘"],
        "keywords": [],
        "platforms": ["dy"],
        "recipients": [],
        "enabled": True,
        "target_type": "search",
        "output_mode": "internal",
    }
    monkeypatch.setattr(
        "api.monitoring.preflight.list_platform_status",
        lambda: [{"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False}],
    )

    try:
        _restore_table("ai_key_profiles", [])
        save_ai_config({"provider": "openai", "base_url": "", "api_key": "", "model": ""})
        save_email_config({"smtp_host": "", "sender": "", "default_recipients": []})
        preflight = build_job_preflight(job, [])
    finally:
        _restore_table("ai_key_profiles", profile_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)

    assert preflight["can_run"] is False
    assert any("未配置平台搜索词" in blocker for blocker in preflight["blockers"])
    assert any("AI" in warning for warning in preflight["warnings"])
    assert any("收件人" in warning for warning in preflight["warnings"])


def test_job_preflight_uses_bound_ai_profile_and_email_template(monkeypatch):
    init_db()
    snapshots = {
        "monitor_jobs": _snapshot_monitor_jobs(),
        "ai_key_profiles": _snapshot_table("ai_key_profiles"),
        "email_templates": _snapshot_table("email_templates"),
        "email_configs": _snapshot_singleton_table("email_configs"),
    }
    try:
        _clear_monitor_jobs()
        save_email_config(
            {
                "smtp_host": "smtp.example.com",
                "smtp_port": 465,
                "sender": "sender@example.com",
                "default_recipients": [],
            }
        )
        profile = save_ai_key_profile(
            {
                "name": "海安任务 AI 接入",
                "provider": "openai",
                "base_url": "https://ai.example.com",
                "api_key": "sk-profile",
                "model": "profile-model",
                "temperature": 0,
                "prompt": DEFAULT_PROMPT,
                "is_active": False,
            }
        )
        template = save_email_template(
            {
                "name": "海安任务模板",
                "subject_template": "日报 {law_firm_name}",
                "html_template": "<main>{report_body}</main>",
                "is_active": False,
            }
        )
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
                "ai_profile_id": profile["id"],
                "email_template_id": template["id"],
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        preflight = build_job_preflight(job, [])
        ai_check = next(item for item in preflight["checks"] if item["key"] == "ai_config")
        email_check = next(item for item in preflight["checks"] if item["key"] == "email_config")
        template_check = next(item for item in preflight["checks"] if item["key"] == "email_template")

        assert ai_check["severity"] == "warning"
        assert "任务绑定 AI 接入" in ai_check["message"]
        assert "未测试通过" in ai_check["message"]
        assert "邮件配置未测试通过" in email_check["message"]
        assert template_check["severity"] == "ok"
        assert "任务绑定邮件模板可用" in template_check["message"]
    finally:
        _restore_monitor_jobs(snapshots["monitor_jobs"])
        _restore_table("ai_key_profiles", snapshots["ai_key_profiles"])
        _restore_table("email_templates", snapshots["email_templates"])
        _restore_singleton_table("email_configs", snapshots["email_configs"])


def test_job_preflight_warns_when_bound_profiles_are_missing(monkeypatch):
    init_db()
    snapshots = {
        "monitor_jobs": _snapshot_monitor_jobs(),
        "email_configs": _snapshot_singleton_table("email_configs"),
    }
    try:
        _clear_monitor_jobs()
        save_email_config(
            {
                "smtp_host": "smtp.example.com",
                "smtp_port": 465,
                "sender": "sender@example.com",
                "default_recipients": [],
                "last_test_status": "success",
            }
        )
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所退费"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
            }
        )
        job = {**job, "ai_profile_id": 99999901, "email_template_id": 99999902}
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        preflight = build_job_preflight(job, [])

        assert preflight["can_run"] is True
        assert any("任务绑定的 AI 接入已不存在" in item for item in preflight["warnings"])
        assert any("任务绑定的邮件模板已不存在" in item for item in preflight["warnings"])
        assert any(item["key"] == "email_template" and item["severity"] == "warning" for item in preflight["checks"])
    finally:
        _restore_monitor_jobs(snapshots["monitor_jobs"])
        _restore_singleton_table("email_configs", snapshots["email_configs"])


def test_job_preflight_blocks_already_running_job():
    job = {"id": 123, "enabled": True, "keywords": ["测试"], "platforms": ["dy"], "recipients": ["a@example.com"]}
    preflight = build_job_preflight(job, [123])

    assert preflight["can_run"] is False
    assert any("正在运行" in item for item in preflight["blockers"])


def test_manual_run_blocks_when_preflight_has_blockers(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    try:
        _clear_monitor_jobs()
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": True},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )
        called = False

        def fake_launch_job(job_id, source="manual"):
            nonlocal called
            called = True
            return {"started": True}

        monkeypatch.setattr(monitor_router, "launch_job", fake_launch_job)

        with pytest.raises(HTTPException) as exc:
            asyncio.run(monitor_router.run_job_now(job["id"]))

        assert exc.value.status_code == 400
        assert "运行前检查未通过" in str(exc.value.detail)
        assert called is False
    finally:
        _restore_monitor_jobs(jobs_snapshot)


def test_manual_run_allows_preflight_warnings_and_returns_preflight(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    email_snapshot = _snapshot_singleton_table("email_configs")
    try:
        _clear_monitor_jobs()
        save_ai_config({"provider": "openai", "base_url": "", "api_key": "", "model": ""})
        save_email_config({"smtp_host": "", "sender": "", "default_recipients": []})
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所退费"],
                "platforms": ["dy"],
                "recipients": [],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        monkeypatch.setattr(
            monitor_router,
            "launch_job",
            lambda job_id, source="manual": {"started": True, "status": "queued", "job_id": job_id, "source": source},
        )

        result = asyncio.run(monitor_router.run_job_now(job["id"]))

        assert result["started"] is True
        assert result["source"] == "manual"
        assert result["preflight"]["can_run"] is True
        assert result["preflight"]["warnings"]
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)


def test_resume_job_blocks_when_preflight_has_blockers(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    try:
        _clear_monitor_jobs()
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": True},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        with pytest.raises(HTTPException) as exc:
            asyncio.run(monitor_router.resume_job(job["id"]))

        assert exc.value.status_code == 400
        assert "启用前检查未通过" in str(exc.value.detail)
        assert get_job(job["id"])["enabled"] is False
    finally:
        _restore_monitor_jobs(jobs_snapshot)


def test_resume_job_allows_warnings_and_returns_preflight(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
    email_snapshot = _snapshot_singleton_table("email_configs")
    try:
        _clear_monitor_jobs()
        save_ai_config({"provider": "openai", "base_url": "", "api_key": "", "model": ""})
        save_email_config({"smtp_host": "", "sender": "", "default_recipients": []})
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所避雷"],
                "platforms": ["dy"],
                "recipients": [],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "09:00",
                "enabled": False,
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )

        result = asyncio.run(monitor_router.resume_job(job["id"]))

        assert result["ok"] is True
        assert result["job"]["enabled"] is True
        assert result["preflight"]["can_run"] is True
        assert result["preflight"]["warnings"]
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)


def test_job_preflight_and_launcher_block_template_placeholders(monkeypatch):
    job = {
        "id": 123,
        "enabled": True,
        "law_firm_name": "请改成目标律所名称",
        "keywords": ["目标律所避雷"],
        "platforms": ["dy"],
        "recipients": ["a@example.com"],
    }

    preflight = build_job_preflight(job, [])

    assert preflight["can_run"] is False
    assert any("测试数据模板" in item for item in preflight["blockers"])
    monkeypatch.setattr(scheduler_module, "get_job", lambda job_id: job)
    with pytest.raises(ValueError, match="测试数据模板"):
        scheduler_module.launch_job(123)


def test_scheduler_stop_job_requests_runner_stop(monkeypatch):
    scheduler_module._running_jobs.add(24680)
    scheduler_module._job_tasks.pop(24680, None)
    calls: list[int] = []

    def fake_request_stop_job(job_id):
        calls.append(job_id)
        return 2

    try:
        monkeypatch.setattr(scheduler_module, "request_stop_job", fake_request_stop_job)
        result = scheduler_module.stop_job(24680)
    finally:
        scheduler_module._running_jobs.discard(24680)
        scheduler_module._job_tasks.pop(24680, None)

    assert result["stopped"] is True
    assert result["terminated_processes"] == 2
    assert calls == [24680]


def test_refresh_jobs_schedule_api_recomputes_next_run_at():
    init_db()
    job = save_job(
        {
            "law_firm_name": "调度刷新测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["调度刷新测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "23:59",
            "enabled": True,
        }
    )
    try:
        result = asyncio.run(monitor_router.refresh_jobs_schedule())
        refreshed = next(item for item in result["jobs"] if item["id"] == job["id"])
    finally:
        _cleanup_test_records(job["id"], "")

    assert refreshed["next_run_at"]
    assert refreshed["next_run_at"].endswith("23:59:00")


def test_monitor_page_uses_tob_information_architecture_without_customer_facing_engine_traces():
    page = Path("api/monitor_web/index.html").read_text(encoding="utf-8")

    assert "总览" in page
    assert "舆情监控" in page
    assert "运行中心" in page
    assert "报告中心" in page
    assert "资源管理" in page
    assert "系统配置" in page
    assert "dashboard_metrics" in page
    assert "/dashboard" in page
    assert "企业级律所舆情监控" in page
    assert "系统运行状态" in page
    assert "调度器状态" in page
    assert "loadSchedulerStatus" in page
    assert "scheduler-status" in page
    assert "平台账号" in page
    assert "账号资源" in page
    assert "账号详情" in page
    assert "账号列表" in page
    assert "这里统一维护账号资源" in page
    assert "平台账号概览" not in page
    assert "账号资源台账" not in page
    assert "account_platform_overview" not in page
    assert ".account-console { display:grid; grid-template-columns:minmax(0,1fr);" in page
    assert ".account-list-panel" in page
    assert "account_modal" in page
    assert "drawer-backdrop" in page
    assert "openNewSocialAccountModal" in page
    assert "openSocialAccountModal" in page
    assert "closeSocialAccountModal" in page
    assert 'onclick="openNewSocialAccountModal()">新增账号' in page
    assert 'onclick="openNewSocialAccountModal()">添加账号' not in page
    assert "保存账号" in page
    assert "account_modal_actions" in page
    assert "account_save_button" in page
    assert "account_delete_button" in page
    assert "deleteCurrentSocialAccount" in page
    assert "account_login_prereq_hint" in page
    assert "updateAccountLoginPrerequisites" in page
    assert "请先填写账号名称。你可以先保存账号创建账号，再生成二维码登录。" in page
    assert "账号名称已填写，可以生成二维码；扫码后系统会自动确认登录结果。" in page
    assert "qrButton.disabled=!nameReady" in page
    assert "checkSocialAccountLogin" in page
    assert "检测登录态" in page
    assert "checkCurrentSocialAccountLogin" not in page
    assert "account_check_result" not in page
    assert "checkSelectedSocialAccountLogins" in page
    assert "/check-login" in page
    assert "updateAccountModalActions" in page
    assert "这是一个新账号。请先填写基础资料并保存账号，再按需完成扫码或 Cookie 登录。" in page
    assert "保存账号会更新账号资料；登录是否可用以登录维护和账号检测结果为准。" in page
    assert "account_login_type_filter" in page
    assert "selectedSocialAccountIds" in page
    assert "account_bulk_bar" in page
    assert "account_bulk_toolbar" in page
    assert "account_bulk_count" in page
    assert "account_bulk_check_btn" in page
    assert "未选择账号" in page
    assert "请先勾选账号" in page
    assert "updateAccountBulkToolbar" in page
    assert "toggleAllFilteredAccounts" in page
    assert "toggleAccountSelection" in page
    assert "批量操作只用于可用性维护" in page
    assert "批量停用" in page
    assert "批量启用" in page
    assert "toggleAccountActionMenu" in page
    assert "reloginSocialAccount" in page
    assert "setAccountPlatformLocked" in page
    assert "平台不可变更" in page
    assert "deleteSelectedSocialAccounts" in page
    assert "startLoginSessionFromSelected" not in page
    assert "openSelectedAccountLoginBrowser" not in page
    assert "accountLedgerTable" in page
    assert 'return `<div class="table-wrap"><table class="account-table">' in page
    assert '<th class="col-actions">操作</th>' in page
    assert "点击“详情”进入单个账号的登录、Cookie、代理和状态维护" in page
    assert "startLoginSessionForAccount" in page
    assert "openCurrentAccountLoginBrowser" in page
    assert "openLoginSessionBrowser" in page
    assert "session.account_id ? Number(session.account_id) : 'null'" in page
    assert "打开登录窗口" in page
    assert "打开登录窗口兜底" not in page
    assert "先按平台和状态定位账号资源" not in page
    assert "1. 基础资料" in page
    assert "2. 登录维护" in page
    assert "4. 完成账号设置" in page
    assert "高级设置" in page
    assert "登录态来源" in page
    assert "social_account_login_source" in page
    assert "social_account_error_summary" in page
    assert "updateAccountDerivedFields" in page
    assert "绑定代理" in page
    assert "不绑定代理" in page
    assert "renderProxySelectOptions" in page
    assert "accountProxyLabel" in page
    assert "plainAccountProxyLabel" in page
    assert "扫码登录" in page
    assert "生成登录二维码" in page
    assert "打开登录窗口" in page
    assert "Cookie 登录" in page
    assert "social_account_cookie_input" in page
    assert "saveCurrentPlatformCookieLogin" in page
    assert "手机号登录" not in page
    assert "social_account_phone" not in page
    assert "saveCurrentPlatformPhoneLogin" not in page
    assert "renderLoginModePanel" in page
    assert "handleSocialLoginTypeChange" in page
    assert "selectSocialLoginType" in page
    assert "supportedSocialLoginTypes" in page
    assert "social_login_method_options" in page
    assert "login-method-option" in page
    assert 'id="social_account_login_type" onchange="handleSocialLoginTypeChange()" style="display:none"' in page
    assert "platform-login-panel" in page
    assert "panel.style.display = active ? 'block' : 'none'" in page
    assert "login-card-grid" in page
    assert "登录状态与平台登录设置" not in page
    assert "运行线索" not in page
    assert "3. 登录记录" in page
    assert "这里只展示最近登录结果，登录和检测操作请在上方维护区或账号列表中完成" in page
    assert "查看状态" not in page
    assert "刷新记录" not in page
    assert "刷新当前账号" not in page
    assert "已生成登录态" in page
    assert "account_metrics" in page
    assert "renderAccountList" in page
    assert "social-accounts" in page
    assert "loadAccountsPool" in page
    assert "先生成二维码完成扫码登录；登录成功后，系统会把账号保存到账号池。" in page
    assert "二维码已生成，系统正在自动确认登录结果" in page
    assert "点击“生成二维码并登录”后，系统会自动确认扫码和登录结果。" in page
    assert "系统正在自动确认登录结果，每 3 秒刷新一次。" in page
    assert "登录成功，账号已保存" in page
    assert "生成二维码" in page
    assert "手机扫码确认" in page
    assert "保存登录态" in page
    assert "waiting_verification" in page
    assert "等待验证" in page
    assert "平台要求先完成验证，请按文字提示处理" in page
    assert "平台验证页面截图" not in page
    assert "verification_image" not in page
    assert "verification_label" in page
    assert "verification_detail" in page
    assert "diagnostic_image" not in page
    assert "登录页面诊断截图" not in page
    assert "我已处理，继续确认" in page
    assert "login-sessions" in page
    assert "pollLoginSession" in page
    assert "代理资源" in page
    assert "代理可绑定到账号或任务，采集时按绑定关系使用" in page
    assert "proxies" in page
    assert "loadProxyPool" in page
    assert "platformStatusTable" in page
    assert "platform_login_config_table" not in page
    assert "loadPlatformLoginConfigs" in page
    assert "platform-login-configs" in page
    assert "savePlatformLoginConfig" not in page
    assert "下一步处理" in page
    assert "尚未完成平台采集" in page
    assert "readiness_actions" in page
    assert "renderReadinessActions" in page
    assert "platformLoginActionNote" in page
    assert "action-card" in page
    assert "去账号池处理登录" in page
    assert "检查 AI 接入" in page
    assert "配置测试邮件" in page
    assert "运行抖音采集" in page
    assert "查看报告和线索" in page
    assert "switchTab" in page
    assert "已运行但未采到内容" in page
    assert "采集无结果" in page
    assert "系统诊断" in page
    assert "刷新调度时间" in page
    assert "refreshJobSchedule" in page
    assert "jobs/refresh-schedule" in page
    assert "toast('任务已保存'); resetJobForm(); closeJobDrawer(); await Promise.all([loadJobs(), loadDashboard(), loadDoctor()]);" in page
    assert "toast('调度时间已刷新'); await Promise.all([loadJobs(), loadSchedulerStatus(), loadDashboard()]);" in page
    assert "打开登录窗口" in page
    assert "用于默认登录态维护；账号资源请在账号详情里发起登录。" not in page
    assert "平台默认登录态" not in page
    assert "登录过程中如平台需要额外确认，请按页面提示完成后继续确认。" in page
    assert "如平台需要额外确认，系统会提示下一步操作。" in page
    assert "login-browser" in page
    assert "openPlatformLoginBrowser" in page
    assert "正在运行的任务 ID" in page
    assert "运行 ID" in page
    assert "任务 ID" in page
    assert "run_log_drawer" in page
    assert "copyCurrentRunLogs" in page
    assert "downloadCurrentRunLogs" in page
    assert "全部运行记录" in page
    assert "预检拦截" in page
    assert "skipped" in page
    assert "runStatusBadge" in page
    assert "runDisplayError" in page
    assert "登录态/配置阻断" in page
    assert "jobActions" in page
    assert "toggleJobActionMenu" in page
    assert "/jobs/'+id+'/stop" in page
    assert "/runs/'+id+'/stop" in page
    assert "await Promise.all([loadRuns(), loadSchedulerStatus(), loadDashboard()]);" in page
    assert "任务正在运行，请先停止后再删除" in page
    assert "startRunPolling" in page
    assert "api('/doctor')" in page
    assert "运行系统诊断" in page
    assert "runSmokeCheck" in page
    assert "smoke_result" in page
    assert "api('/smoke'" in page
    assert "renderSmokeResult" in page
    assert "正在运行系统诊断，请稍候。" in page
    assert "formatBytes" in page
    assert "preflight" in page
    assert "运行前提示" in page
    assert "填入海安律所样例" in page
    assert "基本信息" in page
    assert "采集设置" in page
    assert "过滤与去重" in page
    assert "平台搜索词（多行）" in page
    assert "律所名称和别名用于 AI 判断、报告标题和线索归属，不会自动追加为平台搜索词。" in page
    assert "排除词不参与平台搜索，只在内容采回后过滤标题、正文、作者和来源搜索词。" in page
    assert "未配置邮件也可以采集和生成报告，只是不发送邮件。" in page
    assert "这里的每一行才会用于平台搜索；律所别名不会自动参与搜索。" in page
    assert "监控对象" not in page
    assert "这里决定系统采什么内容" not in page
    assert "关键词栏" not in page
    assert "每 6 小时，起点" in page
    assert "每 12 小时，起点" in page
    assert "fill_sample_job_btn" in page
    assert "addEventListener('click', fillSampleJobTemplate)" in page
    assert "fillSampleJobTemplate" in page
    assert "hasJobTemplatePlaceholders" in page
    assert "请先把测试数据模板里的律所名称和平台搜索词改成真实内容" in page
    assert "恢复默认规则" in page
    assert "default_prompt" in page
    assert "resetAIPrompt" in page
    assert "维护可复用的舆情判断规则" in page
    assert "基础信息" in page
    assert "规则只影响模型如何判断和填写字段" in page
    assert "评估规则列表" in page
    assert "openNewAIRuleModal" in page
    assert "loadAIRuleProfiles" in page
    assert "ai-rule-profiles" in page
    assert "ai_rule_modal" in page
    assert "rule-modal-flow" in page
    assert "rule-modal-layout" not in page
    assert "rule-editor-stack" in page
    assert "rule-test-stack" in page
    assert "rule-side-stack" not in page
    assert "ai_rule_active_label" not in page
    assert "rule-accordion" in page
    assert "testAIRuleFromModal" in page
    assert "saveAIRuleFromModal" in page
    assert "activateAIRuleProfile" in page
    assert "deleteAIRuleProfile" in page
    assert "aiRuleActions" in page
    assert "toggleAIRuleActionMenu" in page
    assert "测试规则" in page
    assert "规则配置" in page
    assert "角色定位" in page
    assert "相关性判断" in page
    assert "疑似负面判断" in page
    assert "风险等级规则" in page
    assert "证据摘录规则" in page
    assert "处理建议规则" in page
    assert "生成后的 Prompt 预览" in page
    assert "composeAIPromptFromRules" in page
    assert "parsePromptSections" in page
    assert "applyPromptToRuleFields" in page
    assert "renderAIOutputSchema" in page
    assert "prompt_sections" in page
    assert "output_schema" in page
    ai_rule_modal = page[page.index('id="ai_rule_modal"') : page.index('id="email"')]
    assert ai_rule_modal.index("基础信息") < ai_rule_modal.index("规则配置") < ai_rule_modal.index("固定输出字段") < ai_rule_modal.index("测试样例") < ai_rule_modal.index("测试结果")
    assert "测试样例" in page
    assert "手动填写一条采集内容和评论样本，用来验证规则是否符合预期" in page
    assert "平台只作为样例上下文，不会触发采集或导入数据" in page
    assert "ai_sample_law_firm_name" in page
    assert "ai_sample_platform" in page
    assert "ai_sample_source_keyword" in page
    assert "ai_sample_title" in page
    assert "ai_sample_text" in page
    assert "ai_sample_comments" in page
    assert "海安律所避雷：退费拖了很久" in page
    assert "sample_law_firm_name:val('ai_sample_law_firm_name')" in page
    assert "sample_platform:val('ai_sample_platform')" in page
    assert "sample_source_keyword:val('ai_sample_source_keyword')" in page
    assert "sample_title:val('ai_sample_title')" in page
    assert "sample_text:val('ai_sample_text')" in page
    assert "sample_comments:val('ai_sample_comments')" in page
    assert "is_related(boolean), is_negative(boolean), risk_level(high|medium|low|irrelevant)" in page
    assert "规则只影响模型如何判断和填写字段" in page
    assert "字段由系统固定校验" in page
    assert "AI 接入资源" in page
    assert "接口协议" in page
    assert "OpenAI-compatible / Anthropic-compatible 协议的模型连接资源" in page
    assert "Provider" not in page
    assert "获取模型列表" in page
    assert "ai_profile_model_options" in page
    assert "toggleAIProfileModelOptions" in page
    assert "selectAIProfileModel" in page
    assert "loadAIProfileModels" in page
    assert "ai-profiles/models" in page
    assert "models" in page
    assert "ai-profiles" in page
    assert "loadAIProfiles" in page
    assert "activateAIProfile" in page
    assert "testAIProfile" in page
    assert "testAIProfile" in page
    assert "ai-profiles/'+id+'/connection-test" in page
    assert "ai-profiles/'+id+'/connection-test" in page
    assert "ai_connection_test_modal" in page
    assert "ai_result" not in page
    assert "openAIConnectionTestModal" in page
    assert "runAIConnectionTest" in page
    assert "closeAIConnectionTestModal" in page
    assert "测试 AI 接入" in page
    assert "开始测试" in page
    assert "测试消息" in page
    assert "模型返回" in page
    assert "模型已返回文本" in page
    assert "连接测试只验证 API 是否能返回文本，不使用舆情评估 Prompt。" in page
    assert "连接测试" in page
    assert "连接测试" in page
    assert "ai-evaluation-config/test" in page
    assert "testAI" in page
    assert "HTML 邮件模板" in page
    assert "email_template_summary" in page
    assert "email-templates/preview" in page
    assert "email_template_preview" in page
    assert "scheduleEmailPreview" in page
    assert "线索明细" in page
    reports_section = page[page.index('<section id="reports"') : page.index('<section id="doctor"')]
    assert reports_section.index("<h3>报告列表</h3>") < reports_section.index("<h3>线索明细</h3>") < reports_section.index("选择报告后查看正文")
    assert "report-workspace" not in page
    assert "reportActions" in page
    assert "renderReportsTable" in page
    assert "currentReports" in page
    assert "action-menu-host" in page
    assert "下载 Markdown" in page
    assert "api('/leads?" in page
    assert "待人工复核" in page
    assert "待复核" in page
    assert "运行系统诊断" in page
    assert "reports/system-check" in page
    assert "loadReports(), loadRuns(), loadReadiness(), loadDoctor(), loadDashboard()" in page
    assert "重发邮件" in page
    assert "系统自检报告已生成" not in page


def test_monitor_page_uses_consistent_buttons_tables_and_modal_actions():
    page = Path("api/monitor_web/index.html").read_text(encoding="utf-8")

    assert "white-space:nowrap" in page
    assert "word-break:keep-all" in page
    assert "min-height:36px" in page
    assert ".row > * { flex:0 1 auto; }" in page
    assert ".row > button, .row > a { flex:0 0 auto; }" in page
    assert ".wide-actions { display:inline-flex; gap:6px; align-items:center; flex-wrap:nowrap;" in page
    assert "td.col-actions, th.col-actions" in page
    assert "position:sticky; right:0" in page
    assert "th.col-actions { background:#f8fafc; z-index:4; }" in page
    assert "headers[i]==='操作'?'col-actions':''" in page
    assert "Math.max(920, (headers||[]).length * 112)" in page
    assert "class=\"form-actions\"" in page
    assert ".form-actions { position:sticky;" in page
    assert ".account-flow-actions { position:sticky;" in page
    assert ".ai-test-actions { position:sticky;" in page
    assert ".rule-modal-actions { position:sticky;" in page
    assert ".config-section .section-note, .config-section .field-hint { display:none; }" in page
    assert ".ui-icon svg" in page
    assert '<symbol id="icon-dashboard"' in page
    assert '<use href="#icon-monitor">' in page
    assert ".page-toolbar { display:flex;" in page
    assert "report-workspace" not in page
    assert ".schema-item { grid-template-columns:1fr; }" in page
    assert ".action-menu-host" in page
    assert ".action-menu.active" in page
    assert "openReportMenuId" in page
    assert "oldHtml = btn ? btn.innerHTML : ''" in page
    assert "btn.innerHTML = oldHtml" in page
    assert "<div class=\"wide-actions\"><button class=\"secondary\" onclick=\"switchTab('accounts')\">管理账号</button></div>" in page
    assert "jobActions(j, running)" in page
    assert "leadLinks(item)" in page
    assert "resendReportEmail" in page
    assert "resend-email" in page
    assert "邮件预览" in page
    assert "report_email_subject" in page
    assert "email-preview" in page
    assert "邮件标题：" in page
    assert "download?type=html" in page
    assert "download?type=excel" in page
    assert "download?type=markdown" in page
    assert "下一步处理" in page
    assert "next_actions" in page
    forbidden = [
        "MediaCrawler",
        "MONITOR_SKIP_AI_API",
        "selftest",
        "上线验收",
        "待验收",
        "项目进展",
        "MVP自测",
        "登录窗口测试律所",
        "first commit",
        "生成自测报告",
        "本地冒烟自检",
        "部署诊断",
        "运行三平台采集",
    ]
    assert not [word for word in forbidden if word in page]


def test_cli_run_due_runs_only_due_enabled_jobs(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    run_calls: list[int] = []
    _clear_monitor_jobs()

    due_job = save_job(
        {
            "law_firm_name": "CLI到期测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["CLI到期测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "08:00",
            "enabled": True,
        }
    )
    future_job = save_job(
        {
            "law_firm_name": "CLI未到期测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["CLI未到期测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "23:00",
            "enabled": True,
        }
    )
    disabled_job = save_job(
        {
            "law_firm_name": "CLI暂停测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["CLI暂停测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "08:00",
            "enabled": False,
        }
    )

    async def fake_run_job(job_id):
        run_calls.append(job_id)
        return {"run_id": 999, "status": "success", "summary": {}, "report": {}}

    try:
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )
        monkeypatch.setattr(cli_module, "run_job", fake_run_job)
        result = asyncio.run(run_due_jobs(datetime(2026, 6, 12, 9, 0, 0)))
    finally:
        _restore_monitor_jobs(jobs_snapshot)

    assert result["ran"] == 1
    assert result["ok"] is True
    assert run_calls == [due_job["id"]]
    assert future_job["id"] not in run_calls
    assert disabled_job["id"] not in run_calls


def test_cli_run_due_skips_legacy_template_placeholder_jobs(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    run_calls: list[int] = []
    _clear_monitor_jobs()

    try:
        with get_conn() as conn:
            now = "2026-06-12T00:00:00+00:00"
            cur = conn.execute(
                """
                INSERT INTO monitor_jobs (
                    law_firm_name, aliases, exclude_words, enable_comments, time_window_type,
                    frequency, email_time, enabled, is_internal, created_at, updated_at
                ) VALUES (?, '[]', '[]', 0, 'recent_1d', 'daily', '08:00', 1, 0, ?, ?)
                """,
                ("请改成目标律所名称", now, now),
            )
            job_id = int(cur.lastrowid)
            conn.execute("INSERT INTO job_keywords (job_id, keyword) VALUES (?, ?)", (job_id, "目标律所避雷"))
            conn.execute("INSERT INTO job_platforms (job_id, platform) VALUES (?, ?)", (job_id, "dy"))

        async def fake_run_job(job_id):
            run_calls.append(job_id)
            return {"run_id": 999, "status": "success", "summary": {}, "report": {}}

        monkeypatch.setattr(cli_module, "run_job", fake_run_job)
        result = asyncio.run(run_due_jobs(datetime(2026, 6, 12, 9, 0, 0)))
    finally:
        _restore_monitor_jobs(jobs_snapshot)

    assert result["ran"] == 0
    assert result["skipped"] == 1
    assert result["ok"] is True
    assert run_calls == []
    assert "测试数据模板" in result["results"][0]["reason"]
    assert "平台搜索词" in result["results"][0]["reason"]


def test_cli_run_due_blocks_preflight_and_records_skipped_run(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    runs_snapshot = _snapshot_table("crawl_runs")
    run_calls: list[int] = []
    _clear_monitor_jobs()

    try:
        job = save_job(
            {
                "law_firm_name": "海安律所",
                "aliases": [],
                "exclude_words": [],
                "keywords": ["海安律所投诉"],
                "platforms": ["xhs"],
                "recipients": ["target@example.com"],
                "enable_comments": False,
                "time_window_type": "recent_1d",
                "frequency": "daily",
                "email_time": "08:00",
                "enabled": True,
            }
        )
        monkeypatch.setattr(
            "api.monitoring.preflight.list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": True, "login_window_open": False},
            ],
        )

        async def fake_run_job(job_id):
            run_calls.append(job_id)
            return {"run_id": 999, "status": "success", "summary": {}, "report": {}}

        monkeypatch.setattr(cli_module, "run_job", fake_run_job)
        result = asyncio.run(run_due_jobs(datetime(2026, 6, 12, 9, 0, 0)))
        skipped = get_run(int(result["results"][0]["run_id"]))
    finally:
        _restore_monitor_jobs(jobs_snapshot)
        _restore_table("crawl_runs", runs_snapshot)

    assert result["ran"] == 0
    assert result["skipped"] == 1
    assert result["ok"] is True
    assert run_calls == []
    assert result["results"][0]["status"] == "skipped"
    assert "重新登录" in result["results"][0]["reason"]
    assert skipped and skipped["status"] == "skipped"
    assert skipped["summary"]["source"] == "cli"
    assert skipped["summary"]["skip_type"] == "preflight_blocked"


def test_report_resend_email_updates_status(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "重发测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["重发测试律所避雷"],
            "platforms": ["dy"],
            "recipients": ["ops@example.com"],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_id = create_run(job["id"])
    report = create_report(
        run_id,
        job,
        {"platforms": ["dy"], "failed_platforms": [], "new_contents": 0, "negative_count": 0, "high_count": 0},
    )

    def fake_send_report(job, report):
        return False, "SMTP 配置未完成"

    try:
        monkeypatch.setattr("api.monitoring.reporting.send_report", fake_send_report)
        ok, error, refreshed = resend_report_email(report["id"])
        stored = get_report(report["id"])
    finally:
        _cleanup_test_records(job["id"], "")

    assert ok is False
    assert error == "SMTP 配置未完成"
    assert refreshed["email_status"] == "failed"
    assert stored and stored["email_status"] == "failed"
    assert stored["email_error"] == "SMTP 配置未完成"


def test_run_job_skips_when_cross_process_lock_exists():
    init_db()
    job = save_job(
        {
            "law_firm_name": "锁测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["锁测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    lock_path = runner_module.LOCKS_DIR / f"job_{job['id']}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("locked", encoding="utf-8")
    with get_conn() as conn:
        before = conn.execute("SELECT COUNT(*) AS n FROM crawl_runs WHERE job_id=?", (job["id"],)).fetchone()["n"]
    try:
        result = asyncio.run(run_monitor_job(job["id"]))
        with get_conn() as conn:
            after = conn.execute("SELECT COUNT(*) AS n FROM crawl_runs WHERE job_id=?", (job["id"],)).fetchone()["n"]
    finally:
        lock_path.unlink(missing_ok=True)
        _cleanup_test_records(job["id"], "")

    assert result["status"] == "already_running"
    assert result["run_id"] is None
    assert after == before


def test_run_history_keeps_job_snapshot_after_job_deleted():
    init_db()
    job = save_job(
        {
            "law_firm_name": "运行快照测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["运行快照测试律所避雷"],
            "platforms": ["dy"],
            "recipients": ["ops@example.com"],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_id = create_run(job["id"])
    finish_run(
        run_id,
        "success",
        {
            "job_id": job["id"],
            "law_firm_name": job["law_firm_name"],
            "keywords": job["keywords"],
            "platforms": job["platforms"],
        },
    )

    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM monitor_jobs WHERE id=?", (job["id"],))
        run = get_run(run_id)
    finally:
        with get_conn() as conn:
            conn.execute("DELETE FROM reports WHERE run_id=?", (run_id,))
            conn.execute("DELETE FROM crawl_runs WHERE id=?", (run_id,))
        _cleanup_test_records(job["id"], "")

    assert run
    assert run["job_id"] == job["id"]
    assert run["law_firm_name"] == "运行快照测试律所"
    assert run["job_deleted"] is True


def test_report_history_keeps_law_firm_snapshot_after_job_deleted(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "报告快照测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["报告快照测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": False,
        }
    )
    run_id = create_run(job["id"])
    report = create_report(
        run_id,
        job,
        {
            "job_id": job["id"],
            "law_firm_name": job["law_firm_name"],
            "platforms": job["platforms"],
            "keywords": job["keywords"],
            "failed_platforms": [],
        },
    )

    try:
        with get_conn() as conn:
            conn.execute("DELETE FROM monitor_jobs WHERE id=?", (job["id"],))
        stored = get_report(report["id"])
        listed = next(item for item in list_reports(200) if item["id"] == report["id"])
    finally:
        with get_conn() as conn:
            conn.execute("DELETE FROM reports WHERE id=?", (report["id"],))
            conn.execute("DELETE FROM crawl_runs WHERE id=?", (run_id,))
        _cleanup_test_records(job["id"], "")

    assert stored and stored["law_firm_name"] == "报告快照测试律所"
    assert listed["law_firm_name"] == "报告快照测试律所"
    assert stored["job_deleted"] is True


def test_list_runs_limit_zero_returns_all_recent_rows():
    init_db()
    job = save_job(
        {
            "law_firm_name": "全部运行测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["全部运行测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_ids = [create_run(job["id"]) for _ in range(2)]
    try:
        assert len([r for r in list_runs(1) if r["id"] in run_ids]) == 1
        assert len([r for r in list_runs(0) if r["id"] in run_ids]) == 2
    finally:
        _cleanup_test_records(job["id"], "")


def test_running_run_keeps_job_snapshot_before_finish():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": ["海安律师事务所"],
            "exclude_words": [],
            "keywords": ["海安律所避雷", "海安律所退费", "海安律所投诉"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_id = create_run(
        job["id"],
        {
            "job_id": job["id"],
            "law_firm_name": job["law_firm_name"],
            "platforms": job["platforms"],
            "keywords": job["keywords"],
        },
    )
    try:
        run = get_run(run_id)
    finally:
        _cleanup_test_records(job["id"], "")

    assert run
    assert run["status"] == "running"
    assert run["display_law_firm_name"] == "海安律所"
    assert run["summary"]["keywords"] == ["海安律所避雷", "海安律所退费", "海安律所投诉"]
    assert run["summary"]["duration_seconds"] >= 0


def test_list_reports_limit_zero_returns_all_recent_rows():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_ids = [create_run(job["id"]) for _ in range(2)]
    reports = []
    try:
        for run_id in run_ids:
            reports.append(
                create_report(
                    run_id,
                    job,
                    {
                        "job_id": job["id"],
                        "law_firm_name": job["law_firm_name"],
                        "platforms": ["dy"],
                        "failed_platforms": [],
                    },
                )
            )
        report_ids = {report["id"] for report in reports}
        assert len([r for r in list_reports(1) if r["id"] in report_ids]) == 1
        assert len([r for r in list_reports(0) if r["id"] in report_ids]) == 2
    finally:
        _cleanup_test_records(job["id"], "")


def test_list_leads_limit_zero_returns_all_recent_rows():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_id = create_run(job["id"])
    content_ids = ["pytest_all_leads_001", "pytest_all_leads_002"]
    now_ts = int(datetime.now(timezone.utc).timestamp())
    items = [
        {"aweme_id": content_id, "title": f"海安律所避雷 {index}", "create_time": now_ts}
        for index, content_id in enumerate(content_ids, start=1)
    ]
    try:
        ingest_outputs(job, run_id, "dy", items, [])
        stored_ids = {item["content_id"] for item in list_leads(0) if item["content_id"] in content_ids}
        assert len([item for item in list_leads(1) if item["content_id"] in content_ids]) == 1
        assert stored_ids == set(content_ids)
    finally:
        for content_id in content_ids:
            _cleanup_test_records(job["id"], content_id)


def test_leads_api_can_scope_items_to_selected_report():
    init_db()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": ["海安律师事务所"],
            "exclude_words": [],
            "keywords": ["海安律所避雷", "海安律所退费", "海安律所投诉"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    now_ts = int(datetime.now(timezone.utc).timestamp())
    first_id = "pytest_report_scope_001"
    second_id = "pytest_report_scope_002"
    try:
        run1 = create_run(job["id"])
        ingest_outputs(job, run1, "dy", [{"aweme_id": first_id, "title": "海安律所避雷", "create_time": now_ts}], [])
        report1 = create_report(run1, job, {"job_id": job["id"], "law_firm_name": job["law_firm_name"], "platforms": ["dy"], "failed_platforms": []})
        run2 = create_run(job["id"])
        ingest_outputs(job, run2, "dy", [{"aweme_id": second_id, "title": "海安律所退费", "create_time": now_ts}], [])
        create_report(run2, job, {"job_id": job["id"], "law_firm_name": job["law_firm_name"], "platforms": ["dy"], "failed_platforms": []})

        scoped = asyncio.run(monitor_router.leads(report_id=report1["id"], limit=0))["leads"]
    finally:
        _cleanup_test_records(job["id"], first_id)
        _cleanup_test_records(job["id"], second_id)

    assert [item["content_id"] for item in scoped] == [first_id]


def test_delete_running_job_is_blocked_and_stop_job_marks_stale_run(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "停止删除测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["停止删除测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    run_id = create_run(job["id"])
    try:
        monkeypatch.setattr(monitor_router, "running_job_ids", lambda: [])
        with pytest.raises(HTTPException) as exc:
            asyncio.run(monitor_router.remove_job(job["id"]))
        assert exc.value.status_code == 409

        result = asyncio.run(monitor_router.stop_job_now(job["id"]))
        run = get_run(run_id)
    finally:
        _cleanup_test_records(job["id"], "")

    assert result["status"] == "cancelled_stale_run"
    assert run and run["status"] == "cancelled"


def test_run_job_blocks_platform_when_login_window_is_open(monkeypatch):
    init_db()
    jobs_snapshot = _snapshot_monitor_jobs()
    job = save_job(
        {
            "law_firm_name": "海安律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["海安律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("MediaCrawler subprocess should not start while login window is open")

    try:
        monkeypatch.setattr(
            runner_module,
            "list_platform_status",
            lambda: [
                {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False, "login_window_open": True},
                {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False, "login_window_open": False},
                {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False, "login_window_open": False},
            ],
        )
        monkeypatch.setattr(runner_module.subprocess, "run", fail_if_called)
        result = asyncio.run(run_monitor_job(job["id"]))
    finally:
        _restore_monitor_jobs(jobs_snapshot)

    assert result["status"] == "partial_failed"
    assert result["summary"]["failed_platforms"] == ["dy"]
    assert "登录窗口未关闭" in result["summary"]["platform_results"]["dy"]["error"]


def test_run_platform_retries_transient_crawler_failure(tmp_path, monkeypatch):
    init_db()
    job = {
        "id": 9991,
        "law_firm_name": "重试测试律所",
        "keywords": ["重试测试律所避雷"],
        "enable_comments": False,
        "time_window_type": "recent_1d",
    }
    calls: list[Path] = []

    def fake_run_attempt(job_arg, platform_arg, out_dir, proxy_binding=None):
        calls.append(out_dir)
        if len(calls) == 1:
            (out_dir / "crawler.log").write_text("temporary network error", encoding="utf-8")
            raise RuntimeError(f"MediaCrawler exited with 1; see {out_dir / 'crawler.log'}")
        json_dir = out_dir / "douyin" / "json"
        json_dir.mkdir(parents=True)
        (json_dir / "search_contents_retry.json").write_text(
            json.dumps(
                [
                    {
                        "aweme_id": "pytest_retry_success_001",
                        "title": "重试测试律所避雷",
                        "desc": "第二次成功",
                        "create_time": int(datetime.now(timezone.utc).timestamp()),
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    monkeypatch.setenv("MONITOR_CRAWLER_MAX_RETRIES", "1")
    monkeypatch.setenv("MONITOR_CRAWLER_RETRY_DELAY_SECONDS", "0")
    monkeypatch.setattr(runner_module, "list_platform_status", lambda: [{"platform": "dy", "login_window_open": False}])
    monkeypatch.setattr(runner_module, "_run_crawler_attempt", fake_run_attempt)

    result = asyncio.run(runner_module.run_platform(job, 10001, "dy", tmp_path))

    _cleanup_test_records(job["id"], "pytest_retry_success_001")

    assert len(calls) == 2
    assert calls[0].name == "attempt_1"
    assert calls[1].name == "attempt_2"
    assert result["attempts"] == 2
    assert result["max_retries"] == 1
    assert result["new_contents"] == 1


def test_run_platform_attaches_bound_proxy_summary(tmp_path, monkeypatch):
    init_db()
    snapshots = {
        "proxy_profiles": _snapshot_table("proxy_profiles"),
        "social_accounts": _snapshot_table("social_accounts"),
    }
    job = {
        "id": 9993,
        "law_firm_name": "代理测试律所",
        "keywords": ["代理测试律所避雷"],
        "enable_comments": False,
        "time_window_type": "recent_1d",
    }
    seen: dict[str, Any] = {}

    def fake_run_attempt(job_arg, platform_arg, out_dir, proxy_binding=None):
        seen["proxy_binding"] = proxy_binding
        json_dir = out_dir / "douyin" / "json"
        json_dir.mkdir(parents=True)
        (json_dir / "search_contents_proxy.json").write_text(
            json.dumps(
                [
                    {
                        "aweme_id": "pytest_proxy_success_001",
                        "title": "代理测试律所避雷",
                        "desc": "代理绑定测试",
                        "create_time": int(datetime.now(timezone.utc).timestamp()),
                    }
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    try:
        proxy = save_proxy_profile(
            {
                "name": "华东采集代理",
                "provider": "manual",
                "proxy_url": "http://user:pass@127.0.0.1:8081",
                "status": "active",
                "max_concurrency": 1,
            }
        )
        save_social_account(
            {
                "name": "抖音采集号",
                "platform": "dy",
                "login_type": "qrcode",
                "status": "active",
                "profile_path": str(tmp_path / "dy_account_profile"),
                "proxy_id": proxy["id"],
            }
        )
        monkeypatch.setenv("MONITOR_CRAWLER_MAX_RETRIES", "0")
        monkeypatch.setattr(runner_module, "list_platform_status", lambda: [{"platform": "dy", "login_window_open": False}])
        monkeypatch.setattr(runner_module, "_run_crawler_attempt", fake_run_attempt)

        result = asyncio.run(runner_module.run_platform(job, 10003, "dy", tmp_path))
    finally:
        _cleanup_test_records(job["id"], "pytest_proxy_success_001")
        for table, snapshot in snapshots.items():
            _restore_table(table, snapshot)

    assert seen["proxy_binding"]["proxy_url"] == "http://user:pass@127.0.0.1:8081"
    assert seen["proxy_binding"]["profile_path"] == str(tmp_path / "dy_account_profile")
    assert result["account"]["account_name"] == "抖音采集号"
    assert result["account"]["profile_path"] == str(tmp_path / "dy_account_profile")
    assert result["proxy"]["proxy_id"] == proxy["id"]
    assert "user:pass" not in result["proxy"]["proxy_url"]
    assert result["new_contents"] == 1


def test_run_platform_does_not_retry_login_required_error(tmp_path, monkeypatch):
    job = {
        "id": 9992,
        "law_firm_name": "登录失败测试律所",
        "keywords": ["登录失败测试律所避雷"],
        "enable_comments": False,
        "time_window_type": "recent_1d",
    }
    calls = 0

    def fake_run_attempt(job_arg, platform_arg, out_dir, proxy_binding=None):
        nonlocal calls
        calls += 1
        raise RuntimeError("MediaCrawler exited with 1；检测到登录态失效，请先重新登录该平台账号")

    monkeypatch.setenv("MONITOR_CRAWLER_MAX_RETRIES", "3")
    monkeypatch.setenv("MONITOR_CRAWLER_RETRY_DELAY_SECONDS", "0")
    monkeypatch.setattr(runner_module, "list_platform_status", lambda: [{"platform": "dy", "login_window_open": False}])
    monkeypatch.setattr(runner_module, "_run_crawler_attempt", fake_run_attempt)

    with pytest.raises(RuntimeError, match="failed after 1 attempt"):
        asyncio.run(runner_module.run_platform(job, 10002, "dy", tmp_path))

    assert calls == 1


def test_expired_cross_process_lock_is_replaced(tmp_path, monkeypatch):
    monkeypatch.setattr(runner_module, "LOCKS_DIR", tmp_path / "locks")
    monkeypatch.setattr(runner_module, "JOB_LOCK_TTL_SECONDS", 60)
    job_id = 98765
    lock_path = runner_module.LOCKS_DIR / f"job_{job_id}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    old_created_at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    lock_path.write_text(json.dumps({"job_id": job_id, "created_at": old_created_at}), encoding="utf-8")

    acquired = runner_module._acquire_job_lock(job_id)
    try:
        assert acquired == lock_path
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
        assert payload["job_id"] == job_id
        assert payload["created_at"] != old_created_at
    finally:
        if acquired:
            runner_module._release_job_lock(acquired)


def test_readiness_requires_successful_douyin_report_for_mvp(monkeypatch):
    monkeypatch.setattr(
        readiness_module,
        "list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False},
        ],
    )
    monkeypatch.setattr(
        readiness_module,
        "get_ai_config",
        lambda masked=True: {
            "provider": "openai",
            "base_url": "https://example.com",
            "api_key": "sk-********test",
            "model": "test-model",
            "last_test_status": "success",
            "last_test_at": "2026-06-11T00:00:00+00:00",
        },
    )
    monkeypatch.setattr(
        readiness_module,
        "get_email_config",
        lambda masked=True: {
            "smtp_host": "smtp.example.com",
            "sender": "sender@example.com",
            "default_recipients": ["target@example.com"],
            "last_test_status": "success",
            "last_test_at": "2026-06-11T00:00:00+00:00",
        },
    )

    partial_reports = [
        {
            "id": 1,
            "summary": {
                "platform_results": {
                    "dy": {"status": "success", "raw_contents": 2, "new_contents": 1},
                    "ks": {"status": "success", "raw_contents": 0, "new_contents": 0},
                }
            },
        },
        {"id": 2, "summary": {"selftest": True}},
    ]
    monkeypatch.setattr(readiness_module, "list_reports", lambda limit=200: partial_reports)
    partial = readiness_module.get_readiness_status()
    partial_real_check = next(check for check in partial["checks"] if check["key"] == "real_report")

    complete_reports = [
        {
            "id": 3,
            "summary": {
                "platform_results": {
                    "dy": {"status": "success", "raw_contents": 2, "new_contents": 1},
                    "ks": {"status": "success", "raw_contents": 3, "new_contents": 2},
                    "xhs": {"status": "success", "raw_contents": 1, "new_contents": 1},
                }
            },
        },
        {"id": 4, "summary": {"selftest": True}},
    ]
    monkeypatch.setattr(readiness_module, "list_reports", lambda limit=200: complete_reports)
    complete = readiness_module.get_readiness_status()
    complete_real_check = next(check for check in complete["checks"] if check["key"] == "real_report")

    assert partial_real_check["ok"] is True
    assert partial["real_platforms"] == ["dy"]
    assert partial["empty_real_platforms"] == []
    assert partial["missing_real_platforms"] == []
    assert "抖音采集闭环已完成" in partial_real_check["message"]
    assert complete_real_check["ok"] is True
    assert complete["missing_real_platforms"] == []
    assert complete["empty_real_platforms"] == []


def test_readiness_uses_all_reports_for_real_platform_audit(monkeypatch):
    seen: dict[str, int] = {}
    monkeypatch.setattr(
        readiness_module,
        "list_platform_status",
        lambda: [
            {"platform": "dy", "platform_label": "抖音", "profile_exists": True, "needs_login": False},
            {"platform": "ks", "platform_label": "快手", "profile_exists": True, "needs_login": False},
            {"platform": "xhs", "platform_label": "小红书", "profile_exists": True, "needs_login": False},
        ],
    )
    monkeypatch.setattr(
        readiness_module,
        "get_ai_config",
        lambda masked=True: {
            "base_url": "https://example.com",
            "api_key": "sk-********test",
            "model": "test-model",
            "last_test_status": "success",
        },
    )
    monkeypatch.setattr(
        readiness_module,
        "get_email_config",
        lambda masked=True: {
            "smtp_host": "smtp.example.com",
            "sender": "sender@example.com",
            "default_recipients": ["target@example.com"],
            "last_test_status": "success",
        },
    )

    def fake_list_reports(limit=100):
        seen["limit"] = limit
        return []

    monkeypatch.setattr(readiness_module, "list_reports", fake_list_reports)

    readiness_module.get_readiness_status()

    assert seen["limit"] == 0


async def _dedupe_and_report_check(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "监控测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["监控测试律所避雷"],
            "platforms": ["dy"],
            "recipients": ["test@example.com"],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    now_ts = int(datetime.now(timezone.utc).timestamp())
    item = {
        "aweme_id": "pytest_monitor_dy_001",
        "title": "监控测试律所避雷",
        "desc": "收费争议",
        "aweme_url": "https://example.com/video",
        "cover_url": "https://example.com/cover.jpg",
        "create_time": now_ts,
    }

    async def pending_review(job, content, comments):
        return {
            "status": "pending_review",
            "is_related": True,
            "is_negative": False,
            "risk_level": "low",
            "reason": "AI 未完成判断，请人工复核",
            "evidence_quotes": [content.get("title") or ""],
            "recommended_action": "人工复核",
            "raw_response": "",
        }

    monkeypatch.setattr(runner_module, "evaluate_content", pending_review)
    run1 = create_run(job["id"])
    first = ingest_outputs(job, run1, "dy", [item], [])
    await evaluate_new_contents(job, run1, first["content_db_ids"])
    report = create_report(
        run1,
        job,
        {"platforms": ["dy"], "failed_platforms": [], "new_contents": first["new_contents"], "negative_count": 0, "high_count": 0},
    )
    html = Path(report["html_path"]).read_text(encoding="utf-8")
    markdown = Path(report["markdown_path"]).read_text(encoding="utf-8")

    run2 = create_run(job["id"])
    second = ingest_outputs(job, run2, "dy", [item], [])
    with get_conn() as conn:
        run2_rows = conn.execute("SELECT COUNT(*) AS n FROM raw_contents WHERE run_id=?", (run2,)).fetchone()["n"]

    _cleanup_test_records(job["id"], "pytest_monitor_dy_001")

    assert first["new_contents"] == 1
    assert second["new_contents"] == 0
    assert run2_rows == 0
    assert "待人工复核" in html
    assert "- 待人工复核：1" in markdown
    assert "https://example.com/cover.jpg" in html


async def _unrelated_negative_check(monkeypatch):
    init_db()
    job = save_job(
        {
            "law_firm_name": "相关性测试律所",
            "aliases": [],
            "exclude_words": [],
            "keywords": ["相关性测试律所避雷"],
            "platforms": ["dy"],
            "recipients": [],
            "enable_comments": False,
            "time_window_type": "recent_1d",
            "frequency": "daily",
            "email_time": "09:00",
            "enabled": True,
        }
    )
    now_ts = int(datetime.now(timezone.utc).timestamp())
    item = {
        "aweme_id": "pytest_unrelated_negative_001",
        "title": "其他机构避雷",
        "desc": "投诉内容很负面，但和目标律所无关",
        "create_time": now_ts,
    }

    async def fake_evaluate_content(job, content, comments):
        return {
            "status": "ok",
            "is_related": False,
            "is_negative": True,
            "risk_level": "high",
            "reason": "内容负面但不相关",
            "evidence_quotes": ["其他机构避雷"],
            "recommended_action": "忽略",
            "raw_response": "{}",
        }

    monkeypatch.setattr(runner_module, "evaluate_content", fake_evaluate_content)
    run_id = create_run(job["id"])
    ingested = ingest_outputs(job, run_id, "dy", [item], [])
    eval_summary = await evaluate_new_contents(job, run_id, ingested["content_db_ids"])
    report = create_report(run_id, job, {"platforms": ["dy"], "failed_platforms": [], **ingested, **eval_summary})
    html = Path(report["html_path"]).read_text(encoding="utf-8")

    _cleanup_test_records(job["id"], "pytest_unrelated_negative_001")

    assert eval_summary["negative_count"] == 0
    assert eval_summary["high_count"] == 0
    assert "本次未发现新增疑似负面线索" in html
    assert "其他机构避雷" not in html


async def _selftest_report_check():
    result = await create_sample_report()
    report = result["report"]
    summary = result["summary"]
    html_path = Path(report["html_path"])
    markdown_path = Path(report["markdown_path"])
    excel_path = Path(report["excel_path"])
    html = html_path.read_text(encoding="utf-8")
    markdown = markdown_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        row = conn.execute("SELECT email_status, email_error FROM reports WHERE id=?", (report["id"],)).fetchone()
    _cleanup_test_records(result["job"]["id"], f"selftest_negative_{result['run_id']}")
    _cleanup_test_records(result["job"]["id"], f"selftest_excluded_{result['run_id']}")

    assert html_path.exists()
    assert markdown_path.exists()
    assert excel_path.exists()
    assert "海安律所" in html
    assert "待人工复核" in html
    assert "- 待人工复核：1" in markdown
    assert "AI 结果仅用于舆情线索筛查" in markdown
    assert summary["email_status"] == "skipped"
    assert row["email_status"] == "skipped"
    assert row["email_error"] == "本地自测不发送邮件"


def _cleanup_test_records(job_id: int, content_id: str) -> None:
    with get_conn() as conn:
        run_ids = [r["id"] for r in conn.execute("SELECT id FROM crawl_runs WHERE job_id=?", (job_id,)).fetchall()]
        raw_ids = [
            r["id"]
            for r in conn.execute(
                "SELECT id FROM raw_contents WHERE job_id=? AND content_id=?",
                (job_id, content_id),
            ).fetchall()
        ]
        if raw_ids:
            conn.execute("DELETE FROM ai_evaluations WHERE raw_content_id IN (%s)" % ",".join("?" for _ in raw_ids), raw_ids)
        conn.execute("DELETE FROM raw_comments WHERE content_id=?", (content_id,))
        conn.execute("DELETE FROM raw_contents WHERE job_id=? AND content_id=?", (job_id, content_id))
        if run_ids:
            conn.execute("DELETE FROM reports WHERE run_id IN (%s)" % ",".join("?" for _ in run_ids), run_ids)
            conn.execute("DELETE FROM crawl_runs WHERE id IN (%s)" % ",".join("?" for _ in run_ids), run_ids)
        conn.execute("DELETE FROM monitor_jobs WHERE id=?", (job_id,))


def _email_html_body(msg) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()
    raise AssertionError("email html body not found")


def _snapshot_singleton_table(table: str) -> dict:
    with get_conn() as conn:
        return dict(conn.execute(f"SELECT * FROM {table} WHERE id=1").fetchone())


def _restore_singleton_table(table: str, snapshot: dict) -> None:
    columns = [key for key in snapshot.keys() if key != "id"]
    assignments = ", ".join(f"{key}=?" for key in columns)
    values = [snapshot[key] for key in columns] + [snapshot["id"]]
    with get_conn() as conn:
        conn.execute(f"UPDATE {table} SET {assignments} WHERE id=?", values)


def _snapshot_table(table: str) -> list[dict]:
    with get_conn() as conn:
        return [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()]


def _restore_table(table: str, snapshot: list[dict]) -> None:
    with get_conn() as conn:
        conn.execute(f"DELETE FROM {table}")
        if not snapshot:
            return
        columns = list(snapshot[0].keys())
        placeholders = ",".join("?" for _ in columns)
        conn.executemany(
            f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
            [[row[col] for col in columns] for row in snapshot],
        )


def _cmd_value(cmd: list[str], flag: str) -> str | None:
    if flag not in cmd:
        return None
    index = cmd.index(flag)
    return cmd[index + 1] if index + 1 < len(cmd) else None


def _login_test_account(platform: str, tmp_path: Path | None = None) -> dict[str, object]:
    label = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}.get(platform, platform)
    profile_root = tmp_path or Path("monitor_data/test_profiles")
    profile_name = f"{platform}_login_profile_{uuid.uuid4().hex}"
    return save_social_account(
        {
            "name": f"海安律所{label}采集号",
            "platform": platform,
            "login_type": "qrcode",
            "status": "standby",
            "profile_path": str(profile_root / profile_name),
        }
    )


def _snapshot_monitor_jobs() -> dict[str, list[dict]]:
    tables = ["monitor_jobs", "job_keywords", "job_platforms", "job_recipients"]
    with get_conn() as conn:
        return {table: [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()] for table in tables}


def _restore_monitor_jobs(snapshot: dict[str, list[dict]]) -> None:
    tables = ["job_recipients", "job_platforms", "job_keywords", "monitor_jobs"]
    with get_conn() as conn:
        for table in tables:
            conn.execute(f"DELETE FROM {table}")
        for table in ["monitor_jobs", "job_keywords", "job_platforms", "job_recipients"]:
            rows = snapshot.get(table, [])
            if not rows:
                continue
            columns = list(rows[0].keys())
            placeholders = ",".join("?" for _ in columns)
            conn.executemany(
                f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                [[row[col] for col in columns] for row in rows],
            )


def _clear_monitor_jobs() -> None:
    with get_conn() as conn:
        for table in ["job_recipients", "job_platforms", "job_keywords", "monitor_jobs"]:
            conn.execute(f"DELETE FROM {table}")
