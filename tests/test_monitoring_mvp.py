from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import HTTPException

from api.monitoring.ai import _build_endpoint, _parse_json, _validate_ai_output, test_ai as run_ai_config_test
from api.monitoring.ai import DEFAULT_PROMPT
from api.monitoring.database import create_run, finish_run, get_ai_config, get_conn, get_email_config, get_platform_login_config, get_report, get_run, init_db, list_jobs, list_leads, list_platform_login_configs, list_reports, list_runs, save_ai_config, save_email_config, save_job, save_platform_login_config
from api.monitoring.login_browser import build_login_browser_command, open_login_browser
from api.monitoring.login_state import login_window_status, record_login_window
from api.monitoring.mailer import build_report_email, send_test_email
from api.monitoring.normalizer import collect_platform_outputs, in_time_window, normalize_content, parse_jsonl_file, resolve_window
from api.monitoring.platform_status import list_platform_status
from api.monitoring.preflight import build_job_preflight
from api.monitoring.readiness import get_readiness_status
from api.monitoring.reporting import create_report, resend_report_email
from api.monitoring.security import redact_sensitive
from api.monitoring.selftest import create_sample_report
from api.monitoring.cli import run_due_jobs
from api.monitoring.doctor import run_doctor
from api.routers import monitor as monitor_router
import api.monitoring.cli as cli_module
import api.monitoring.readiness as readiness_module
import api.monitoring.runner as runner_module
import api.monitoring.scheduler as scheduler_module
from api.monitoring.runner import evaluate_new_contents, ingest_outputs
from api.monitoring.runner import run_job as run_monitor_job
from api.monitoring.scheduler import _is_due, next_run_at, scheduler_disabled_reason, scheduler_status
from tools.cdp_browser import resolve_cdp_user_data_dir


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


def test_platform_status_ignores_login_error_older_than_profile_update(tmp_path):
    profile = tmp_path / "browser_data" / "cdp_dy_user_data_dir"
    profile.mkdir(parents=True)
    state = profile / "state"
    state.write_text("ok", encoding="utf-8")
    error_time = datetime(2026, 6, 12, 9, 0, tzinfo=timezone.utc)
    updated_time = error_time + timedelta(minutes=10)
    os.utime(state, (updated_time.timestamp(), updated_time.timestamp()))

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
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["profile_exists"] is True
    assert dy["needs_login"] is False
    assert dy["last_error"] == ""


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
    assert not (tmp_path / "login_windows" / "dy.json").exists()


def test_platform_status_supports_custom_browser_data_dir(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    (browser_data / "cdp_dy_user_data_dir").mkdir(parents=True)
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))

    statuses = list_platform_status(tmp_path, [])
    dy = next(item for item in statuses if item["platform"] == "dy")

    assert dy["profile_path"] == str((browser_data / "cdp_dy_user_data_dir").resolve())
    assert dy["profile_exists"] is True


def test_cdp_browser_uses_same_custom_profile_root_as_status(tmp_path, monkeypatch):
    browser_data = tmp_path / "profiles"
    monkeypatch.setenv("MONITOR_BROWSER_DATA_DIR", str(browser_data))

    expected = browser_data / "cdp_dy_user_data_dir"

    assert Path(resolve_cdp_user_data_dir("dy")) == expected
    dy_status = next(item for item in list_platform_status(tmp_path, []) if item["platform"] == "dy")
    assert dy_status["profile_path"] == str(expected.resolve())


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
    with pytest.raises(ValueError, match="验收模板"):
        save_job({**base, "law_firm_name": "请改成目标律所名称", "recipients": []})
    with pytest.raises(ValueError, match="验收模板"):
        save_job({**base, "keywords": ["目标律所避雷"], "recipients": []})


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
        assert "phone" in dy["supported_login_types"]
        assert "phone" not in ks["supported_login_types"]

        saved = save_platform_login_config("dy", {"login_type": "cookie", "cookies": "sessionid=secret-cookie"})
        raw = get_platform_login_config("dy", masked=False)

        assert saved["login_type"] == "cookie"
        assert saved["has_cookies"] is True
        assert "secret-cookie" not in saved["cookies"]
        assert raw["cookies"] == "sessionid=secret-cookie"

        with pytest.raises(ValueError, match="does not support"):
            save_platform_login_config("ks", {"login_type": "phone"})
        with pytest.raises(ValueError, match="Cookie 登录需要先填写 Cookie"):
            save_platform_login_config("xhs", {"login_type": "cookie"})
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
    redacted = redact_sensitive(text)

    assert "sk-secret123456789" not in redacted
    assert "abc123" not in redacted
    assert "hunter2" not in redacted
    assert "session=abc" not in redacted
    assert "mytoken" not in redacted
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


def test_ai_email_test_results_are_persisted_for_readiness(monkeypatch):
    init_db()
    ai_snapshot = _snapshot_singleton_table("ai_configs")
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
        monkeypatch.setattr(monitor_router.ai, "test_ai", fake_ai_test)
        result = asyncio.run(
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
                "dy": {"status": "success", "raw_contents": 2, "new_contents": 1},
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
    assert "快手" in html
    assert "检测到登录态失效" in html
    assert "平台采集状态" in markdown
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
    assert any(item["content_id"] == f"selftest_negative_{result['run_id']}" for item in api_result)
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


def test_readiness_status_reports_checks():
    init_db()
    status = get_readiness_status()
    keys = {check["key"] for check in status["checks"]}

    assert {"platform_profiles", "ai_config", "email_config", "selftest_report", "real_report"} <= keys
    assert isinstance(status["ready"], bool)
    assert isinstance(status["next_actions"], list)
    assert len(status["platforms"]) == 3
    assert all("label" in check and "ok" in check and "message" in check for check in status["checks"])


def test_readiness_platform_profiles_require_valid_login_state(monkeypatch):
    init_db()
    job = {
        "id": 123,
        "enabled": True,
        "keywords": ["测试律所避雷"],
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

    assert platform_check["ok"] is False
    assert "重新登录" in platform_check["message"]
    assert any("账号登录" in action and "快手" in action for action in status["next_actions"])
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


def test_doctor_reports_deployment_diagnostics():
    init_db()
    status = run_doctor()
    keys = {check["key"] for check in status["checks"]}

    assert {"project_files", "uv", "data_dir", "database", "browser_profiles", "ai_config", "email_config", "reports"} <= keys
    assert "readiness" in status
    assert "paths" in status
    assert status["paths"]["monitor_data_dir"]
    assert isinstance(status["recommendations"], list)


def test_doctor_api_exposes_deployment_diagnostics():
    init_db()
    status = asyncio.run(monitor_router.doctor())

    assert "checks" in status
    assert "readiness" in status
    assert "recommendations" in status
    assert "paths" in status


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
    email_snapshot = _snapshot_singleton_table("email_configs")

    try:
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
        _restore_singleton_table("ai_configs", ai_snapshot)
        _restore_singleton_table("email_configs", email_snapshot)
        _cleanup_test_records(job["id"], "")

    assert preflight["can_run"] is True
    assert preflight["ready"] is False
    assert any("AI" in item for item in preflight["warnings"])
    assert any("收件人" in item for item in preflight["warnings"])
    assert api_result["can_run"] is True


def test_job_preflight_blocks_already_running_job():
    job = {"id": 123, "enabled": True, "keywords": ["测试"], "platforms": ["dy"], "recipients": ["a@example.com"]}
    preflight = build_job_preflight(job, [123])

    assert preflight["can_run"] is False
    assert any("正在运行" in item for item in preflight["blockers"])


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
    assert any("验收模板" in item for item in preflight["blockers"])
    monkeypatch.setattr(scheduler_module, "get_job", lambda job_id: job)
    with pytest.raises(ValueError, match="验收模板"):
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


def test_monitor_page_exposes_acceptance_checklist():
    page = Path("api/monitor_web/index.html").read_text(encoding="utf-8")

    assert "上线验收状态" in page
    assert "调度器状态" in page
    assert "loadSchedulerStatus" in page
    assert "scheduler-status" in page
    assert "账号登录" in page
    assert "登录方式按平台统一配置" in page
    assert "平台登录方式配置" in page
    assert "Cookie 会加密保存" in page
    assert "account_status_table" in page
    assert "platformStatusTable" in page
    assert "platform_login_config_table" in page
    assert "loadPlatformLoginConfigs" in page
    assert "platform-login-configs" in page
    assert "savePlatformLoginConfig" in page
    assert "login_type_" in page
    assert "cookies_" in page
    assert "下一步处理" in page
    assert "尚未完成真实采集" in page
    assert "已运行但未采到内容" in page
    assert "真实采集空结果" in page
    assert "部署诊断" in page
    assert "刷新调度时间" in page
    assert "refreshJobSchedule" in page
    assert "jobs/refresh-schedule" in page
    assert "打开登录窗口" in page
    assert "用于 Profile 登录或人工刷新登录态。" in page
    assert "login-browser" in page
    assert "openPlatformLoginBrowser" in page
    assert "正在运行的任务 ID" in page
    assert "运行ID" in page
    assert "任务ID" in page
    assert "全部运行记录" in page
    assert "/jobs/'+id+'/stop" in page
    assert "/runs/'+id+'/stop" in page
    assert "任务正在运行，请先停止后再删除" in page
    assert "startRunPolling" in page
    assert "api('/doctor')" in page
    assert "preflight" in page
    assert "运行前提示" in page
    assert "填入三平台验收模板" in page
    assert "fill_acceptance_template_btn" in page
    assert "addEventListener('click', fillAcceptanceJobTemplate)" in page
    assert "fillAcceptanceJobTemplate" in page
    assert "hasJobTemplatePlaceholders" in page
    assert "请先把验收模板里的律所名称和关键词改成真实内容" in page
    assert "恢复默认 Prompt" in page
    assert "default_prompt" in page
    assert "resetAIPrompt" in page
    assert "线索明细" in page
    assert "api('/leads?" in page
    assert "待人工复核" in page
    assert "待复核" in page
    assert "生成自测报告" in page
    assert "重发邮件" in page
    assert "resendReportEmail" in page
    assert "resend-email" in page
    assert "download?type=html" in page
    assert "download?type=excel" in page
    assert "download?type=markdown" in page
    assert "下一步处理" in page
    assert "next_actions" in page


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
    assert "验收模板" in result["results"][0]["reason"]


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

    def fake_run_attempt(job_arg, platform_arg, out_dir):
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


def test_run_platform_does_not_retry_login_required_error(tmp_path, monkeypatch):
    job = {
        "id": 9992,
        "law_firm_name": "登录失败测试律所",
        "keywords": ["登录失败测试律所避雷"],
        "enable_comments": False,
        "time_window_type": "recent_1d",
    }
    calls = 0

    def fake_run_attempt(job_arg, platform_arg, out_dir):
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


def test_readiness_requires_successful_real_reports_for_all_three_platforms(monkeypatch):
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

    assert partial_real_check["ok"] is False
    assert partial["real_platforms"] == ["dy"]
    assert partial["empty_real_platforms"] == ["ks"]
    assert partial["missing_real_platforms"] == ["ks", "xhs"]
    assert "未采到内容" in partial_real_check["message"]
    assert any("换真实可搜索关键词" in action and "快手" in action for action in partial["next_actions"])
    assert any("真实采集" in action and "小红书" in action for action in partial["next_actions"])
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

    run2 = create_run(job["id"])
    second = ingest_outputs(job, run2, "dy", [item], [])
    with get_conn() as conn:
        run2_rows = conn.execute("SELECT COUNT(*) AS n FROM raw_contents WHERE run_id=?", (run2,)).fetchone()["n"]

    _cleanup_test_records(job["id"], "pytest_monitor_dy_001")

    assert first["new_contents"] == 1
    assert second["new_contents"] == 0
    assert run2_rows == 0
    assert "待人工复核" in html
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
