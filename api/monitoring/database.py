from __future__ import annotations

import json
import sqlite3
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .prompts import DEFAULT_PROMPT
from .security import MONITOR_DATA_DIR, decrypt_secret, encrypt_secret, mask_secret, redact_sensitive


DB_PATH = MONITOR_DATA_DIR / "monitor.sqlite"
DEFAULT_EMAIL_SUBJECT_TEMPLATE = "【律所舆情日报】{law_firm_name} - {date}"
JOB_TEMPLATE_PLACEHOLDERS = ("请改成", "目标律所", "律所简称", "律师事务所简称")
SUPPORTED_MONITOR_PLATFORMS = ("dy", "ks", "xhs")
PLATFORM_LOGIN_TYPES = {
    "dy": ("qrcode", "phone", "cookie"),
    "ks": ("qrcode", "cookie"),
    "xhs": ("qrcode", "phone", "cookie"),
}
LOGIN_TYPE_LABELS = {
    "qrcode": "浏览器 Profile / 扫码",
    "phone": "手机号",
    "cookie": "Cookie",
}

ACCOUNT_PROFILE_ROOT = MONITOR_DATA_DIR / "account_profiles"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_conn() -> sqlite3.Connection:
    MONITOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _json_dumps(value: Any) -> str:
    return json.dumps(value or [], ensure_ascii=False)


def _json_loads(value: str | None, default: Any = None) -> Any:
    if value in (None, ""):
        return [] if default is None else default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return [] if default is None else default


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS monitor_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                law_firm_name TEXT NOT NULL,
                aliases TEXT NOT NULL DEFAULT '[]',
                exclude_words TEXT NOT NULL DEFAULT '[]',
                enable_comments INTEGER NOT NULL DEFAULT 1,
                time_window_type TEXT NOT NULL DEFAULT 'recent_1d',
                custom_start TEXT,
                custom_end TEXT,
                frequency TEXT NOT NULL DEFAULT 'daily',
                cron_expr TEXT,
                email_time TEXT NOT NULL DEFAULT '09:00',
                enabled INTEGER NOT NULL DEFAULT 1,
                is_internal INTEGER NOT NULL DEFAULT 0,
                next_run_at TEXT,
                last_run_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS job_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL REFERENCES monitor_jobs(id) ON DELETE CASCADE,
                keyword TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS job_platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL REFERENCES monitor_jobs(id) ON DELETE CASCADE,
                platform TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS job_recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL REFERENCES monitor_jobs(id) ON DELETE CASCADE,
                email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ai_configs (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                provider TEXT NOT NULL DEFAULT 'openai',
                base_url TEXT NOT NULL DEFAULT '',
                api_key_encrypted TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                temperature REAL NOT NULL DEFAULT 0,
                prompt TEXT NOT NULL DEFAULT '',
                last_test_status TEXT NOT NULL DEFAULT 'untested',
                last_test_at TEXT,
                last_test_error TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS email_configs (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                smtp_host TEXT NOT NULL DEFAULT '',
                smtp_port INTEGER NOT NULL DEFAULT 465,
                encryption TEXT NOT NULL DEFAULT 'ssl',
                sender TEXT NOT NULL DEFAULT '',
                username TEXT NOT NULL DEFAULT '',
                password_encrypted TEXT NOT NULL DEFAULT '',
                subject_template TEXT NOT NULL DEFAULT '【律所舆情日报】{law_firm_name} - {date}',
                default_recipients TEXT NOT NULL DEFAULT '[]',
                last_test_status TEXT NOT NULL DEFAULT 'untested',
                last_test_at TEXT,
                last_test_error TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS platform_login_configs (
                platform TEXT PRIMARY KEY,
                login_type TEXT NOT NULL DEFAULT 'qrcode',
                cookies_encrypted TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ai_key_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'openai',
                base_url TEXT NOT NULL DEFAULT '',
                api_key_encrypted TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                temperature REAL NOT NULL DEFAULT 0,
                prompt TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 0,
                last_test_status TEXT NOT NULL DEFAULT 'untested',
                last_test_at TEXT,
                last_test_error TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject_template TEXT NOT NULL DEFAULT '【律所舆情日报】{law_firm_name} - {date}',
                html_template TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                login_type TEXT NOT NULL DEFAULT 'qrcode',
                status TEXT NOT NULL DEFAULT 'standby',
                profile_path TEXT NOT NULL DEFAULT '',
                proxy_id INTEGER,
                notes TEXT NOT NULL DEFAULT '',
                last_used_at TEXT,
                last_error TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS proxy_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'manual',
                proxy_url_encrypted TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'standby',
                max_concurrency INTEGER NOT NULL DEFAULT 1,
                notes TEXT NOT NULL DEFAULT '',
                last_checked_at TEXT,
                last_error TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                account_id INTEGER,
                status TEXT NOT NULL DEFAULT 'waiting_manual_browser',
                login_url TEXT NOT NULL DEFAULT '',
                qr_image TEXT NOT NULL DEFAULT '',
                profile_path TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT
            );

            CREATE TABLE IF NOT EXISTS crawl_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER REFERENCES monitor_jobs(id) ON DELETE SET NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                summary TEXT NOT NULL DEFAULT '{}',
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS raw_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_id TEXT NOT NULL,
                job_id INTEGER,
                run_id INTEGER,
                law_firm_name TEXT,
                source_keyword TEXT,
                title TEXT,
                description TEXT,
                author_name TEXT,
                content_url TEXT,
                cover_url TEXT,
                publish_time INTEGER,
                comment_count INTEGER,
                raw_json TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                UNIQUE(job_id, platform, content_id)
            );

            CREATE TABLE IF NOT EXISTS raw_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                comment_id TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content TEXT,
                author_name TEXT,
                create_time INTEGER,
                raw_json TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                UNIQUE(platform, comment_id)
            );

            CREATE TABLE IF NOT EXISTS ai_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_content_id INTEGER NOT NULL REFERENCES raw_contents(id) ON DELETE CASCADE,
                run_id INTEGER,
                status TEXT NOT NULL,
                is_related INTEGER NOT NULL DEFAULT 0,
                is_negative INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'irrelevant',
                reason TEXT NOT NULL DEFAULT '',
                evidence_quotes TEXT NOT NULL DEFAULT '[]',
                recommended_action TEXT NOT NULL DEFAULT '',
                raw_response TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                UNIQUE(raw_content_id)
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL REFERENCES crawl_runs(id) ON DELETE CASCADE,
                job_id INTEGER,
                html_path TEXT NOT NULL,
                markdown_path TEXT NOT NULL,
                excel_path TEXT NOT NULL,
                email_status TEXT NOT NULL DEFAULT 'pending',
                email_error TEXT,
                summary TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            """
        )
        _ensure_column(conn, "monitor_jobs", "is_internal", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "ai_configs", "last_test_status", "TEXT NOT NULL DEFAULT 'untested'")
        _ensure_column(conn, "ai_configs", "last_test_at", "TEXT")
        _ensure_column(conn, "ai_configs", "last_test_error", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "email_configs", "last_test_status", "TEXT NOT NULL DEFAULT 'untested'")
        _ensure_column(conn, "email_configs", "last_test_at", "TEXT")
        _ensure_column(conn, "email_configs", "last_test_error", "TEXT NOT NULL DEFAULT ''")
        _migrate_raw_contents_unique_by_job(conn)
        mark_selftest_jobs_internal(conn)
        now = utc_now()
        conn.execute(
            "INSERT OR IGNORE INTO ai_configs (id, updated_at) VALUES (1, ?)",
            (now,),
        )
        conn.execute(
            "INSERT OR IGNORE INTO email_configs (id, updated_at) VALUES (1, ?)",
            (now,),
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO platform_login_configs (platform, login_type, updated_at)
            VALUES (?, 'qrcode', ?)
            """,
            [(platform, now) for platform in SUPPORTED_MONITOR_PLATFORMS],
        )


def row_to_job(conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    job_id = row["id"]
    keywords = [
        r["keyword"]
        for r in conn.execute("SELECT keyword FROM job_keywords WHERE job_id=? ORDER BY id", (job_id,))
    ]
    platforms = [
        r["platform"]
        for r in conn.execute("SELECT platform FROM job_platforms WHERE job_id=? ORDER BY id", (job_id,))
    ]
    recipients = [
        r["email"]
        for r in conn.execute("SELECT email FROM job_recipients WHERE job_id=? ORDER BY id", (job_id,))
    ]
    result = dict(row)
    result["aliases"] = _json_loads(result.get("aliases"))
    result["exclude_words"] = _json_loads(result.get("exclude_words"))
    result["keywords"] = keywords
    result["platforms"] = platforms
    result["recipients"] = recipients
    result["enabled"] = bool(result["enabled"])
    result["enable_comments"] = bool(result["enable_comments"])
    result["is_internal"] = bool(result.get("is_internal", 0))
    return result


def list_jobs(include_internal: bool = False) -> list[dict[str, Any]]:
    with get_conn() as conn:
        if include_internal:
            rows = conn.execute("SELECT * FROM monitor_jobs ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM monitor_jobs WHERE is_internal=0 ORDER BY id DESC").fetchall()
        return [row_to_job(conn, row) for row in rows]


def get_job(job_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
        return row_to_job(conn, row) if row else None


def save_job(payload: dict[str, Any], job_id: int | None = None) -> dict[str, Any]:
    now = utc_now()
    law_firm_name = (payload.get("law_firm_name") or "").strip()
    if not law_firm_name:
        raise ValueError("law_firm_name is required")
    keywords = [str(k).strip() for k in payload.get("keywords", []) if str(k).strip()]
    if not keywords:
        raise ValueError("keywords is required")
    if has_job_template_placeholders({"law_firm_name": law_firm_name, "keywords": keywords}):
        raise ValueError("请先把验收模板里的律所名称和关键词改成真实内容")
    platforms = [p for p in payload.get("platforms", []) if p in {"dy", "ks", "xhs"}]
    if not platforms:
        raise ValueError("at least one platform is required")
    recipients = [str(e).strip() for e in payload.get("recipients", []) if str(e).strip()]
    validate_recipients(recipients)
    aliases = [str(v).strip() for v in payload.get("aliases", []) if str(v).strip()]
    exclude_words = [str(v).strip() for v in payload.get("exclude_words", []) if str(v).strip()]
    time_window_type = _validate_time_window(payload)
    frequency = _validate_frequency(payload)
    email_time = _validate_email_time(payload.get("email_time") or "09:00")
    with get_conn() as conn:
        if job_id:
            exists = conn.execute("SELECT id FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
            if not exists:
                raise ValueError("job not found")
            conn.execute(
                """
                UPDATE monitor_jobs SET law_firm_name=?, aliases=?, exclude_words=?,
                    enable_comments=?, time_window_type=?, custom_start=?, custom_end=?,
                    frequency=?, cron_expr=?, email_time=?, enabled=?, is_internal=?, updated_at=?
                WHERE id=?
                """,
                (
                    law_firm_name,
                    _json_dumps(aliases),
                    _json_dumps(exclude_words),
                    1 if payload.get("enable_comments", True) else 0,
                    time_window_type,
                    payload.get("custom_start") or None,
                    payload.get("custom_end") or None,
                    frequency,
                    payload.get("cron_expr") or None,
                    email_time,
                    1 if payload.get("enabled", True) else 0,
                    1 if payload.get("is_internal", False) else 0,
                    now,
                    job_id,
                ),
            )
            target_id = job_id
            conn.execute("DELETE FROM job_keywords WHERE job_id=?", (target_id,))
            conn.execute("DELETE FROM job_platforms WHERE job_id=?", (target_id,))
            conn.execute("DELETE FROM job_recipients WHERE job_id=?", (target_id,))
        else:
            cur = conn.execute(
                """
                INSERT INTO monitor_jobs (
                    law_firm_name, aliases, exclude_words, enable_comments, time_window_type,
                    custom_start, custom_end, frequency, cron_expr, email_time, enabled, is_internal,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    law_firm_name,
                    _json_dumps(aliases),
                    _json_dumps(exclude_words),
                    1 if payload.get("enable_comments", True) else 0,
                    time_window_type,
                    payload.get("custom_start") or None,
                    payload.get("custom_end") or None,
                    frequency,
                    payload.get("cron_expr") or None,
                    email_time,
                    1 if payload.get("enabled", True) else 0,
                    1 if payload.get("is_internal", False) else 0,
                    now,
                    now,
                ),
            )
            target_id = int(cur.lastrowid)
        conn.executemany(
            "INSERT INTO job_keywords (job_id, keyword) VALUES (?, ?)",
            [(target_id, k) for k in keywords],
        )
        conn.executemany(
            "INSERT INTO job_platforms (job_id, platform) VALUES (?, ?)",
            [(target_id, p) for p in platforms],
        )
        conn.executemany(
            "INSERT INTO job_recipients (job_id, email) VALUES (?, ?)",
            [(target_id, e) for e in recipients],
        )
    return get_job(target_id) or {}


def has_job_template_placeholders(job: dict[str, Any]) -> bool:
    values = [str(job.get("law_firm_name") or ""), *(str(item) for item in job.get("keywords", []))]
    joined = "\n".join(values)
    if any(placeholder in joined for placeholder in JOB_TEMPLATE_PLACEHOLDERS):
        return True
    return False


def mark_selftest_jobs_internal(conn: sqlite3.Connection | None = None) -> None:
    """Hide jobs created only to verify report generation."""
    sql = """
        UPDATE monitor_jobs
        SET is_internal=1
        WHERE id IN (
            SELECT DISTINCT job_id FROM crawl_runs
            WHERE job_id IS NOT NULL
              AND (summary LIKE '%"selftest": true%' OR summary LIKE '%"selftest":true%')
        )
    """
    if conn is not None:
        conn.execute(sql)
        return
    with get_conn() as managed_conn:
        managed_conn.execute(sql)


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def _migrate_raw_contents_unique_by_job(conn: sqlite3.Connection) -> None:
    if _has_unique_index(conn, "raw_contents", ["job_id", "platform", "content_id"]):
        return

    conn.commit()
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute("BEGIN")
        conn.execute("DROP TABLE IF EXISTS ai_evaluations_backup")
        conn.execute("CREATE TABLE ai_evaluations_backup AS SELECT * FROM ai_evaluations")
        conn.execute("DROP TABLE ai_evaluations")
        conn.execute("ALTER TABLE raw_contents RENAME TO raw_contents_old")
        conn.execute(
            """
            CREATE TABLE raw_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_id TEXT NOT NULL,
                job_id INTEGER,
                run_id INTEGER,
                law_firm_name TEXT,
                source_keyword TEXT,
                title TEXT,
                description TEXT,
                author_name TEXT,
                content_url TEXT,
                cover_url TEXT,
                publish_time INTEGER,
                comment_count INTEGER,
                raw_json TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                UNIQUE(job_id, platform, content_id)
            )
            """
        )
        columns = [
            "id",
            "platform",
            "content_id",
            "job_id",
            "run_id",
            "law_firm_name",
            "source_keyword",
            "title",
            "description",
            "author_name",
            "content_url",
            "cover_url",
            "publish_time",
            "comment_count",
            "raw_json",
            "first_seen_at",
            "last_seen_at",
        ]
        column_list = ", ".join(columns)
        conn.execute(
            f"INSERT OR IGNORE INTO raw_contents ({column_list}) SELECT {column_list} FROM raw_contents_old"
        )
        conn.execute("DROP TABLE raw_contents_old")
        conn.execute(
            """
            CREATE TABLE ai_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_content_id INTEGER NOT NULL REFERENCES raw_contents(id) ON DELETE CASCADE,
                run_id INTEGER,
                status TEXT NOT NULL,
                is_related INTEGER NOT NULL DEFAULT 0,
                is_negative INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'irrelevant',
                reason TEXT NOT NULL DEFAULT '',
                evidence_quotes TEXT NOT NULL DEFAULT '[]',
                recommended_action TEXT NOT NULL DEFAULT '',
                raw_response TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                UNIQUE(raw_content_id)
            )
            """
        )
        eval_columns = [row["name"] for row in conn.execute("PRAGMA table_info(ai_evaluations_backup)").fetchall()]
        if eval_columns:
            eval_column_list = ", ".join(eval_columns)
            conn.execute(
                f"INSERT OR IGNORE INTO ai_evaluations ({eval_column_list}) SELECT {eval_column_list} FROM ai_evaluations_backup"
            )
        conn.execute("DROP TABLE ai_evaluations_backup")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def _has_unique_index(conn: sqlite3.Connection, table: str, columns: list[str]) -> bool:
    for index in conn.execute(f"PRAGMA index_list({table})").fetchall():
        if not index["unique"]:
            continue
        index_columns = [
            row["name"]
            for row in conn.execute(f"PRAGMA index_info({index['name']})").fetchall()
        ]
        if index_columns == columns:
            return True
    return False


def validate_recipients(recipients: list[str]) -> None:
    invalid = [email for email in recipients if "@" not in email or email.startswith("@") or email.endswith("@")]
    if invalid:
        raise ValueError("invalid recipient email: " + ", ".join(invalid))


def _validate_time_window(payload: dict[str, Any]) -> str:
    window = payload.get("time_window_type") or "recent_1d"
    if window not in {"recent_1d", "recent_7d", "recent_30d", "custom"}:
        raise ValueError("invalid time_window_type")
    if window == "custom":
        start = _parse_date(payload.get("custom_start"))
        end = _parse_date(payload.get("custom_end"))
        if not start or not end:
            raise ValueError("custom_start and custom_end are required")
        if start > end:
            raise ValueError("custom_start must be before custom_end")
    return window


def _validate_frequency(payload: dict[str, Any]) -> str:
    frequency = payload.get("frequency") or "daily"
    if frequency not in {"daily", "12h", "6h", "cron"}:
        raise ValueError("invalid frequency")
    if frequency == "cron":
        cron_expr = (payload.get("cron_expr") or "").strip()
        if not cron_expr:
            raise ValueError("cron_expr is required")
        try:
            from apscheduler.triggers.cron import CronTrigger

            CronTrigger.from_crontab(cron_expr)
        except Exception as exc:
            raise ValueError(f"invalid cron_expr: {exc}") from exc
    return frequency


def _validate_email_time(value: str) -> str:
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValueError("email_time must be HH:MM") from exc
    return value


def _parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def delete_job(job_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM monitor_jobs WHERE id=?", (job_id,))


def has_running_run_for_job(job_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM crawl_runs WHERE job_id=? AND status='running' LIMIT 1",
            (job_id,),
        ).fetchone()
    return bool(row)


def cancel_running_runs_for_job(job_id: int, message: str) -> int:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, summary FROM crawl_runs WHERE job_id=? AND status='running'",
            (job_id,),
        ).fetchall()
    count = 0
    for row in rows:
        summary = _json_loads(row["summary"], {})
        if not isinstance(summary, dict):
            summary = {}
        summary["cancelled"] = True
        summary["cancel_reason"] = message
        finish_run(int(row["id"]), "cancelled", summary, message)
        count += 1
    return count


def cancel_run(run_id: int, message: str) -> bool:
    run = get_run(run_id)
    if not run or run.get("status") != "running":
        return False
    summary = run.get("summary") or {}
    if not isinstance(summary, dict):
        summary = {}
    summary["cancelled"] = True
    summary["cancel_reason"] = message
    finish_run(run_id, "cancelled", summary, message)
    return True


def set_job_enabled(job_id: int, enabled: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE monitor_jobs SET enabled=?, updated_at=? WHERE id=?",
            (1 if enabled else 0, utc_now(), job_id),
        )


def set_job_schedule_state(job_id: int, next_run_at: str | None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE monitor_jobs SET next_run_at=?, updated_at=? WHERE id=?",
            (next_run_at, utc_now(), job_id),
        )


def get_ai_config(masked: bool = True) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM ai_configs WHERE id=1").fetchone()
        data = dict(row)
    data["api_key"] = mask_secret(data.pop("api_key_encrypted")) if masked else decrypt_secret(data.pop("api_key_encrypted"))
    return data


def _effective_ai_prompt(value: str | None) -> str:
    return value or DEFAULT_PROMPT


def _ai_config_changed(current: dict[str, Any], next_config: dict[str, Any]) -> bool:
    return (
        (current.get("provider") or "openai") != next_config["provider"]
        or (current.get("base_url") or "") != next_config["base_url"]
        or (current.get("api_key") or "") != next_config["api_key"]
        or (current.get("model") or "") != next_config["model"]
        or float(current.get("temperature") or 0) != float(next_config["temperature"])
        or _effective_ai_prompt(current.get("prompt")) != _effective_ai_prompt(next_config["prompt"])
    )


def _email_config_changed(current: dict[str, Any], next_config: dict[str, Any]) -> bool:
    return (
        (current.get("smtp_host") or "") != next_config["smtp_host"]
        or int(current.get("smtp_port") or 465) != int(next_config["smtp_port"])
        or (current.get("encryption") or "ssl") != next_config["encryption"]
        or (current.get("sender") or "") != next_config["sender"]
        or (current.get("username") or "") != next_config["username"]
        or (current.get("password") or "") != next_config["password"]
        or (current.get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE) != next_config["subject_template"]
        or (current.get("default_recipients") or []) != (next_config["default_recipients"] or [])
    )


def _next_test_state(current: dict[str, Any], changed: bool) -> dict[str, str | None]:
    if changed:
        return {
            "last_test_status": "untested",
            "last_test_at": None,
            "last_test_error": "配置已更新，需重新测试",
        }
    return {
        "last_test_status": current.get("last_test_status") or "untested",
        "last_test_at": current.get("last_test_at"),
        "last_test_error": current.get("last_test_error") or "",
    }


def save_ai_config(payload: dict[str, Any]) -> dict[str, Any]:
    current = get_ai_config(masked=False)
    api_key = payload.get("api_key")
    next_api_key = str(api_key) if api_key else current.get("api_key")
    encrypted = encrypt_secret(next_api_key)
    provider = payload.get("provider") or "openai"
    if provider not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    temperature = validate_temperature(payload.get("temperature", 0) or 0)
    next_config = {
        "provider": provider,
        "base_url": (payload.get("base_url") or "").strip(),
        "api_key": next_api_key or "",
        "model": (payload.get("model") or "").strip(),
        "temperature": temperature,
        "prompt": payload.get("prompt") or "",
    }
    changed = _ai_config_changed(current, next_config)
    test_state = _next_test_state(current, changed)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE ai_configs SET provider=?, base_url=?, api_key_encrypted=?, model=?,
                temperature=?, prompt=?, last_test_status=?, last_test_at=?,
                last_test_error=?, updated_at=? WHERE id=1
            """,
            (
                next_config["provider"],
                next_config["base_url"],
                encrypted,
                next_config["model"],
                next_config["temperature"],
                next_config["prompt"],
                test_state["last_test_status"],
                test_state["last_test_at"],
                test_state["last_test_error"],
                utc_now(),
            ),
        )
    return get_ai_config(masked=True)


def mark_ai_test_result(success: bool, error: str | None = None) -> dict[str, Any]:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE ai_configs SET last_test_status=?, last_test_at=?, last_test_error=?
            WHERE id=1
            """,
            ("success" if success else "failed", utc_now(), "" if success else _trim_error(error)),
        )
    return get_ai_config(masked=True)


def get_email_config(masked: bool = True) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM email_configs WHERE id=1").fetchone()
        data = dict(row)
    data["default_recipients"] = _json_loads(data.get("default_recipients"))
    data["password"] = mask_secret(data.pop("password_encrypted")) if masked else decrypt_secret(data.pop("password_encrypted"))
    return data


def save_email_config(payload: dict[str, Any]) -> dict[str, Any]:
    current = get_email_config(masked=False)
    password = payload.get("password")
    next_password = str(password) if password else current.get("password")
    encrypted = encrypt_secret(next_password)
    recipients = [str(e).strip() for e in payload.get("default_recipients", []) if str(e).strip()]
    validate_recipients(recipients)
    smtp_port = validate_port(payload.get("smtp_port") or 465)
    encryption_mode = payload.get("encryption") or "ssl"
    if encryption_mode not in {"ssl", "starttls", "none"}:
        raise ValueError("invalid email encryption")
    next_config = {
        "smtp_host": (payload.get("smtp_host") or "").strip(),
        "smtp_port": smtp_port,
        "encryption": encryption_mode,
        "sender": (payload.get("sender") or "").strip(),
        "username": (payload.get("username") or "").strip(),
        "password": next_password or "",
        "subject_template": payload.get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE,
        "default_recipients": recipients,
    }
    changed = _email_config_changed(current, next_config)
    test_state = _next_test_state(current, changed)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE email_configs SET smtp_host=?, smtp_port=?, encryption=?, sender=?,
                username=?, password_encrypted=?, subject_template=?, default_recipients=?,
                last_test_status=?, last_test_at=?,
                last_test_error=?, updated_at=? WHERE id=1
            """,
            (
                next_config["smtp_host"],
                next_config["smtp_port"],
                next_config["encryption"],
                next_config["sender"],
                next_config["username"],
                encrypted,
                next_config["subject_template"],
                _json_dumps(next_config["default_recipients"]),
                test_state["last_test_status"],
                test_state["last_test_at"],
                test_state["last_test_error"],
                utc_now(),
            ),
        )
    return get_email_config(masked=True)


def mark_email_test_result(success: bool, error: str | None = None) -> dict[str, Any]:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE email_configs SET last_test_status=?, last_test_at=?, last_test_error=?
            WHERE id=1
            """,
            ("success" if success else "failed", utc_now(), "" if success else _trim_error(error)),
        )
    return get_email_config(masked=True)


def list_platform_login_configs(masked: bool = True) -> list[dict[str, Any]]:
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM platform_login_configs ORDER BY CASE platform WHEN 'dy' THEN 1 WHEN 'ks' THEN 2 WHEN 'xhs' THEN 3 ELSE 99 END"
            ).fetchall()
    except sqlite3.OperationalError:
        return [_default_platform_login_config(platform, masked) for platform in SUPPORTED_MONITOR_PLATFORMS]
    configs = [_row_to_platform_login_config(dict(row), masked) for row in rows]
    existing = {item["platform"] for item in configs}
    for platform in SUPPORTED_MONITOR_PLATFORMS:
        if platform not in existing:
            configs.append(_default_platform_login_config(platform, masked))
    return sorted(configs, key=lambda item: SUPPORTED_MONITOR_PLATFORMS.index(item["platform"]))


def get_platform_login_config(platform: str, masked: bool = True) -> dict[str, Any]:
    _validate_platform(platform)
    try:
        with get_conn() as conn:
            row = conn.execute("SELECT * FROM platform_login_configs WHERE platform=?", (platform,)).fetchone()
    except sqlite3.OperationalError:
        return _default_platform_login_config(platform, masked)
    if not row:
        return _default_platform_login_config(platform, masked)
    return _row_to_platform_login_config(dict(row), masked)


def save_platform_login_config(platform: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_platform(platform)
    current = get_platform_login_config(platform, masked=False)
    login_type = (payload.get("login_type") or current.get("login_type") or "qrcode").strip()
    _validate_platform_login_type(platform, login_type)
    if payload.get("clear_cookies"):
        cookies = ""
    elif payload.get("cookies"):
        cookies = str(payload.get("cookies") or "").strip()
    else:
        cookies = current.get("cookies") or ""
    if login_type == "cookie" and not cookies:
        raise ValueError("Cookie 登录需要先填写 Cookie")
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO platform_login_configs (platform, login_type, cookies_encrypted, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(platform) DO UPDATE SET
                login_type=excluded.login_type,
                cookies_encrypted=excluded.cookies_encrypted,
                updated_at=excluded.updated_at
            """,
            (platform, login_type, encrypt_secret(cookies), utc_now()),
        )
    return get_platform_login_config(platform, masked=True)


def _row_to_platform_login_config(row: dict[str, Any], masked: bool) -> dict[str, Any]:
    platform = row.get("platform") or ""
    encrypted = row.get("cookies_encrypted") or ""
    cookies = mask_secret(encrypted) if masked else decrypt_secret(encrypted)
    raw_cookies = decrypt_secret(encrypted)
    login_type = row.get("login_type") or "qrcode"
    return {
        "platform": platform,
        "login_type": login_type,
        "login_type_label": LOGIN_TYPE_LABELS.get(login_type, login_type),
        "supported_login_types": list(PLATFORM_LOGIN_TYPES.get(platform, ("qrcode", "cookie"))),
        "supported_login_type_labels": {
            item: LOGIN_TYPE_LABELS.get(item, item) for item in PLATFORM_LOGIN_TYPES.get(platform, ("qrcode", "cookie"))
        },
        "cookies": cookies,
        "has_cookies": bool(raw_cookies),
        "updated_at": row.get("updated_at"),
    }


def _default_platform_login_config(platform: str, masked: bool = True) -> dict[str, Any]:
    return _row_to_platform_login_config(
        {"platform": platform, "login_type": "qrcode", "cookies_encrypted": "", "updated_at": None},
        masked,
    )


def _validate_platform(platform: str) -> None:
    if platform not in SUPPORTED_MONITOR_PLATFORMS:
        raise ValueError("unsupported platform")


def _validate_platform_login_type(platform: str, login_type: str) -> None:
    supported = PLATFORM_LOGIN_TYPES.get(platform, ())
    if login_type not in supported:
        labels = " / ".join(LOGIN_TYPE_LABELS.get(item, item) for item in supported)
        raise ValueError(f"{platform} does not support login_type={login_type}; supported: {labels}")


def validate_temperature(value: Any) -> float:
    try:
        temperature = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("temperature must be a number") from exc
    if temperature < 0 or temperature > 2:
        raise ValueError("temperature must be between 0 and 2")
    return temperature


def validate_port(value: Any) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("smtp_port must be a number") from exc
    if port <= 0 or port > 65535:
        raise ValueError("smtp_port must be between 1 and 65535")
    return port


def _trim_error(error: str | None) -> str:
    return redact_sensitive(str(error or ""))[:1000]


def create_run(job_id: int, summary: dict[str, Any] | None = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO crawl_runs (job_id, status, started_at, summary) VALUES (?, 'running', ?, ?)",
            (job_id, utc_now(), json.dumps(_redact_json(summary or {}), ensure_ascii=False)),
        )
        return int(cur.lastrowid)


def update_run_summary(run_id: int, summary: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_json(summary), ensure_ascii=False), run_id),
        )


def finish_run(run_id: int, status: str, summary: dict[str, Any], error: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE crawl_runs SET status=?, finished_at=?, summary=?, error_message=? WHERE id=?",
            (status, utc_now(), json.dumps(_redact_json(summary), ensure_ascii=False), _trim_error(error), run_id),
        )


def get_run(run_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT r.*, j.law_firm_name FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE r.id=?
            """,
            (run_id,),
        ).fetchone()
    return _hydrate_run_row(row) if row else None


def list_runs(limit: int = 100) -> list[dict[str, Any]]:
    sql = """
        SELECT r.*, j.law_firm_name FROM crawl_runs r
        LEFT JOIN monitor_jobs j ON j.id = r.job_id
        ORDER BY r.id DESC
    """
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_hydrate_run_row(row) for row in rows]


def _hydrate_run_row(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    summary = _json_loads(item.get("summary"), {})
    if not isinstance(summary, dict):
        summary = {}
    snapshot_job_id = _safe_int(summary.get("job_id"))
    current_job_id = _safe_int(item.get("job_id"))
    if current_job_id is None and snapshot_job_id is not None:
        item["job_id"] = snapshot_job_id
    item["summary"] = summary
    if not item.get("law_firm_name"):
        item["law_firm_name"] = summary.get("law_firm_name") or ""
    if item.get("status") == "running":
        summary["duration_seconds"] = summary.get("duration_seconds") or _elapsed_seconds(item.get("started_at"))
    is_legacy_without_snapshot = current_job_id is None and snapshot_job_id is None and not summary.get("selftest")
    item["display_law_firm_name"] = item.get("law_firm_name") or summary.get("law_firm_name") or (
        "旧记录无任务快照" if is_legacy_without_snapshot else ""
    )
    item["job_deleted"] = bool(snapshot_job_id and not current_job_id)
    item["legacy_without_job_snapshot"] = bool(is_legacy_without_snapshot)
    return item


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _elapsed_seconds(started_at: Any) -> int:
    try:
        started = datetime.fromisoformat(str(started_at or "").replace("Z", "+00:00"))
        now = datetime.fromisoformat(utc_now())
        return max(0, int((now - started).total_seconds()))
    except ValueError:
        return 0


def list_reports(limit: int = 100) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit)
    sql = """
        SELECT reports.*, monitor_jobs.id AS current_job_id, monitor_jobs.law_firm_name FROM reports
        LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
        ORDER BY reports.id DESC
    """
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["summary"] = _json_loads(item.get("summary"), {})
        _hydrate_report_item(item)
        result.append(item)
    _attach_report_lead_counts(result)
    return result


def get_report(report_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT reports.*, monitor_jobs.id AS current_job_id, monitor_jobs.law_firm_name FROM reports
            LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
            WHERE reports.id=?
            """,
            (report_id,),
        ).fetchone()
    if not row:
        return None
    report = dict(row)
    report["summary"] = _json_loads(report.get("summary"), {})
    _hydrate_report_item(report)
    _attach_report_lead_counts([report])
    return report


def _hydrate_report_item(item: dict[str, Any]) -> None:
    summary = item.get("summary") or {}
    if not isinstance(summary, dict):
        summary = {}
    snapshot_job_id = _safe_int(summary.get("job_id"))
    report_job_id = _safe_int(item.get("job_id"))
    current_job_id = _safe_int(item.get("current_job_id"))
    if not item.get("law_firm_name"):
        item["law_firm_name"] = summary.get("law_firm_name") or ""
    item["display_law_firm_name"] = item.get("law_firm_name") or summary.get("law_firm_name") or ""
    item["job_deleted"] = bool((snapshot_job_id or report_job_id) and not current_job_id)


def _attach_report_lead_counts(reports: list[dict[str, Any]]) -> None:
    run_ids = [int(report["run_id"]) for report in reports if report.get("run_id")]
    if not run_ids:
        return
    placeholders = ",".join("?" for _ in run_ids)
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT
                c.run_id,
                SUM(CASE WHEN e.status='pending_review' THEN 1 ELSE 0 END) AS pending_review_count,
                SUM(CASE WHEN e.is_related=1 AND e.is_negative=1 THEN 1 ELSE 0 END) AS negative_count,
                SUM(CASE WHEN e.is_related=1 AND e.is_negative=1 AND e.risk_level='high' THEN 1 ELSE 0 END) AS high_count
            FROM raw_contents c
            LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
            WHERE c.run_id IN ({placeholders})
            GROUP BY c.run_id
            """,
            run_ids,
        ).fetchall()
    counts = {int(row["run_id"]): dict(row) for row in rows}
    for report in reports:
        summary = report.get("summary") or {}
        row = counts.get(int(report.get("run_id") or 0), {})
        if row:
            summary["pending_review_count"] = int(row.get("pending_review_count") or 0)
            summary["negative_count"] = int(row.get("negative_count") or summary.get("negative_count") or 0)
            summary["high_count"] = int(row.get("high_count") or summary.get("high_count") or 0)
        else:
            summary.setdefault("pending_review_count", 0)
        report["summary"] = summary


def list_leads(limit: int = 100) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit)
    sql = """
        SELECT
            c.id, c.platform, c.content_id, c.job_id, c.run_id,
            COALESCE(c.law_firm_name, j.law_firm_name) AS law_firm_name,
            c.source_keyword, c.title, c.description, c.author_name,
            c.content_url, c.cover_url, c.publish_time, c.comment_count,
            c.first_seen_at, c.last_seen_at,
            e.status AS eval_status, e.is_related, e.is_negative, e.risk_level,
            e.reason, e.evidence_quotes, e.recommended_action, e.created_at AS evaluated_at
        FROM raw_contents c
        LEFT JOIN monitor_jobs j ON j.id = c.job_id
        LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
        ORDER BY c.id DESC
    """
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["is_related"] = bool(item.get("is_related"))
        item["is_negative"] = bool(item.get("is_negative"))
        item["evidence_quotes"] = _json_loads(item.get("evidence_quotes"))
        result.append(item)
    return result


def get_dashboard_summary() -> dict[str, Any]:
    with get_conn() as conn:
        jobs_total = conn.execute("SELECT COUNT(*) AS n FROM monitor_jobs WHERE is_internal=0").fetchone()["n"]
        jobs_enabled = conn.execute("SELECT COUNT(*) AS n FROM monitor_jobs WHERE is_internal=0 AND enabled=1").fetchone()["n"]
        runs_total = conn.execute("SELECT COUNT(*) AS n FROM crawl_runs").fetchone()["n"]
        contents_total = conn.execute("SELECT COUNT(*) AS n FROM raw_contents").fetchone()["n"]
        reports_total = conn.execute("SELECT COUNT(*) AS n FROM reports").fetchone()["n"]
        pending_review = conn.execute("SELECT COUNT(*) AS n FROM ai_evaluations WHERE status='pending_review'").fetchone()["n"]
        negative_total = conn.execute("SELECT COUNT(*) AS n FROM ai_evaluations WHERE is_related=1 AND is_negative=1").fetchone()["n"]
        high_total = conn.execute("SELECT COUNT(*) AS n FROM ai_evaluations WHERE is_related=1 AND is_negative=1 AND risk_level='high'").fetchone()["n"]
        social_total = conn.execute("SELECT COUNT(*) AS n FROM social_accounts").fetchone()["n"]
        proxy_total = conn.execute("SELECT COUNT(*) AS n FROM proxy_profiles").fetchone()["n"]
        ai_profiles_total = conn.execute("SELECT COUNT(*) AS n FROM ai_key_profiles").fetchone()["n"]
        login_sessions_total = conn.execute("SELECT COUNT(*) AS n FROM login_sessions").fetchone()["n"]
        latest_runs = conn.execute("SELECT status, summary, started_at, finished_at FROM crawl_runs ORDER BY id DESC LIMIT 20").fetchall()
    failed_runs = 0
    platform_counts: dict[str, int] = {}
    for row in latest_runs:
        if row["status"] in {"failed", "partial_failed", "cancelled"}:
            failed_runs += 1
        summary = _json_loads(row["summary"], {})
        for platform in summary.get("platforms") or []:
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
    return {
        "jobs_total": int(jobs_total or 0),
        "jobs_enabled": int(jobs_enabled or 0),
        "runs_total": int(runs_total or 0),
        "reports_total": int(reports_total or 0),
        "contents_total": int(contents_total or 0),
        "pending_review": int(pending_review or 0),
        "negative_total": int(negative_total or 0),
        "high_total": int(high_total or 0),
        "failed_runs_recent": failed_runs,
        "platform_counts_recent": platform_counts,
        "social_accounts_total": int(social_total or 0),
        "proxy_profiles_total": int(proxy_total or 0),
        "ai_profiles_total": int(ai_profiles_total or 0),
        "login_sessions_total": int(login_sessions_total or 0),
    }


def list_ai_key_profiles(masked: bool = True) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM ai_key_profiles ORDER BY is_active DESC, id DESC").fetchall()
    return [_row_to_ai_profile(dict(row), masked) for row in rows]


def get_ai_key_profile(profile_id: int, masked: bool = True) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM ai_key_profiles WHERE id=?", (profile_id,)).fetchone()
    return _row_to_ai_profile(dict(row), masked) if row else None


def get_active_ai_key_profile(masked: bool = True) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM ai_key_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
    return _row_to_ai_profile(dict(row), masked) if row else None


def save_ai_key_profile(payload: dict[str, Any], profile_id: int | None = None) -> dict[str, Any]:
    current = get_ai_key_profile(profile_id, masked=False) if profile_id else {}
    name = (payload.get("name") or (current or {}).get("name") or "").strip()
    if not name:
        raise ValueError("profile name is required")
    provider = payload.get("provider") or (current or {}).get("provider") or "openai"
    if provider not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    api_key = str(payload.get("api_key") or "") or (current or {}).get("api_key") or ""
    temperature = validate_temperature(payload.get("temperature", (current or {}).get("temperature", 0)) or 0)
    next_config = {
        "name": name,
        "provider": provider,
        "base_url": (payload.get("base_url") or (current or {}).get("base_url") or "").strip(),
        "api_key": api_key,
        "model": (payload.get("model") or (current or {}).get("model") or "").strip(),
        "temperature": temperature,
        "prompt": payload.get("prompt") if payload.get("prompt") is not None else (current or {}).get("prompt", ""),
        "is_active": bool(payload.get("is_active", (current or {}).get("is_active", False))),
    }
    changed = not current or _ai_config_changed(current, next_config)
    test_state = _next_test_state(current or {}, changed)
    now = utc_now()
    with get_conn() as conn:
        if next_config["is_active"]:
            conn.execute("UPDATE ai_key_profiles SET is_active=0")
        if profile_id:
            exists = conn.execute("SELECT id FROM ai_key_profiles WHERE id=?", (profile_id,)).fetchone()
            if not exists:
                raise ValueError("AI profile not found")
            conn.execute(
                """
                UPDATE ai_key_profiles SET name=?, provider=?, base_url=?, api_key_encrypted=?,
                    model=?, temperature=?, prompt=?, is_active=?, last_test_status=?,
                    last_test_at=?, last_test_error=?, updated_at=? WHERE id=?
                """,
                (
                    next_config["name"],
                    next_config["provider"],
                    next_config["base_url"],
                    encrypt_secret(next_config["api_key"]),
                    next_config["model"],
                    next_config["temperature"],
                    next_config["prompt"],
                    1 if next_config["is_active"] else 0,
                    test_state["last_test_status"],
                    test_state["last_test_at"],
                    test_state["last_test_error"],
                    now,
                    profile_id,
                ),
            )
            target_id = profile_id
        else:
            cur = conn.execute(
                """
                INSERT INTO ai_key_profiles (
                    name, provider, base_url, api_key_encrypted, model, temperature, prompt,
                    is_active, last_test_status, last_test_at, last_test_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    next_config["name"],
                    next_config["provider"],
                    next_config["base_url"],
                    encrypt_secret(next_config["api_key"]),
                    next_config["model"],
                    next_config["temperature"],
                    next_config["prompt"],
                    1 if next_config["is_active"] else 0,
                    test_state["last_test_status"],
                    test_state["last_test_at"],
                    test_state["last_test_error"],
                    now,
                    now,
                ),
            )
            target_id = int(cur.lastrowid)
    return get_ai_key_profile(target_id, masked=True) or {}


def delete_ai_key_profile(profile_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM ai_key_profiles WHERE id=?", (profile_id,))


def set_active_ai_key_profile(profile_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM ai_key_profiles WHERE id=?", (profile_id,)).fetchone()
        if not row:
            raise ValueError("AI profile not found")
        conn.execute("UPDATE ai_key_profiles SET is_active=0")
        conn.execute("UPDATE ai_key_profiles SET is_active=1, updated_at=? WHERE id=?", (utc_now(), profile_id))
    return get_ai_key_profile(profile_id, masked=True) or {}


def _row_to_ai_profile(row: dict[str, Any], masked: bool) -> dict[str, Any]:
    encrypted = row.pop("api_key_encrypted", "")
    row["api_key"] = mask_secret(encrypted) if masked else decrypt_secret(encrypted)
    row["is_active"] = bool(row.get("is_active"))
    return row


def list_email_templates() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM email_templates ORDER BY is_active DESC, id DESC").fetchall()
    return [_row_to_email_template(dict(row)) for row in rows]


def get_active_email_template() -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM email_templates WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
    return _row_to_email_template(dict(row)) if row else None


def save_email_template(payload: dict[str, Any], template_id: int | None = None) -> dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("template name is required")
    subject_template = payload.get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE
    html_template = payload.get("html_template") or ""
    is_active = bool(payload.get("is_active"))
    now = utc_now()
    with get_conn() as conn:
        if is_active:
            conn.execute("UPDATE email_templates SET is_active=0")
        if template_id:
            exists = conn.execute("SELECT id FROM email_templates WHERE id=?", (template_id,)).fetchone()
            if not exists:
                raise ValueError("email template not found")
            conn.execute(
                "UPDATE email_templates SET name=?, subject_template=?, html_template=?, is_active=?, updated_at=? WHERE id=?",
                (name, subject_template, html_template, 1 if is_active else 0, now, template_id),
            )
            target_id = template_id
        else:
            cur = conn.execute(
                """
                INSERT INTO email_templates (name, subject_template, html_template, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, subject_template, html_template, 1 if is_active else 0, now, now),
            )
            target_id = int(cur.lastrowid)
    return get_email_template(target_id) or {}


def get_email_template(template_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM email_templates WHERE id=?", (template_id,)).fetchone()
    return _row_to_email_template(dict(row)) if row else None


def delete_email_template(template_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM email_templates WHERE id=?", (template_id,))


def render_email_template_preview(payload: dict[str, Any]) -> dict[str, str]:
    subject = payload.get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE
    html_template = payload.get("html_template") or ""
    sample = {
        "law_firm_name": payload.get("law_firm_name") or "海安律所",
        "date": datetime.now().date().isoformat(),
        "new_contents": "12",
        "negative_count": "3",
        "high_count": "1",
        "pending_review_count": "4",
        "platforms": "抖音 / 快手 / 小红书",
        "report_html": _sample_report_html(),
        "report_url": "https://example.com/report-preview",
    }
    return {
        "subject": _safe_format(subject, sample),
        "html": _safe_format(html_template or _default_email_preview_html(), sample),
    }


def _row_to_email_template(row: dict[str, Any]) -> dict[str, Any]:
    row["is_active"] = bool(row.get("is_active"))
    return row


def _safe_format(template: str, values: dict[str, Any]) -> str:
    try:
        return template.format_map(_FormatDict(values))
    except Exception:
        return template


class _FormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _default_email_preview_html() -> str:
    return (
        "<div style='font-family:Arial,Microsoft YaHei,sans-serif;color:#1f2937'>"
        "<h2>【律所舆情日报】{law_firm_name} - {date}</h2>"
        "<p>新增 {new_contents} 条，疑似负面 {negative_count} 条，高风险 {high_count} 条，待复核 {pending_review_count} 条。</p>"
        "<p>覆盖平台：{platforms}</p>"
        "{report_html}"
        "<p style='color:#64748b;font-size:12px'>AI 仅作线索筛查，不代表事实认定。</p>"
        "</div>"
    )


def _sample_report_html() -> str:
    return (
        "<section style='border-top:1px solid #e5e7eb;padding-top:14px'>"
        "<h2 style='font-size:16px;margin:0 0 10px'>高风险线索</h2>"
        "<table style='width:100%;border-collapse:collapse;font-size:13px'>"
        "<tr>"
        "<th style='text-align:left;border-bottom:1px solid #e5e7eb;padding:8px'>平台</th>"
        "<th style='text-align:left;border-bottom:1px solid #e5e7eb;padding:8px'>标题</th>"
        "<th style='text-align:left;border-bottom:1px solid #e5e7eb;padding:8px'>AI 理由</th>"
        "</tr>"
        "<tr>"
        "<td style='border-bottom:1px solid #e5e7eb;padding:8px'>抖音</td>"
        "<td style='border-bottom:1px solid #e5e7eb;padding:8px'>海安律所退费投诉</td>"
        "<td style='border-bottom:1px solid #e5e7eb;padding:8px'>包含退费、投诉等风险表达，建议人工复核。</td>"
        "</tr>"
        "</table>"
        "</section>"
    )


def list_social_accounts() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM social_accounts ORDER BY platform, id DESC").fetchall()
    return [_row_to_pool_item(dict(row)) for row in rows]


def save_social_account(payload: dict[str, Any], account_id: int | None = None) -> dict[str, Any]:
    name = (payload.get("name") or "").strip()
    platform = (payload.get("platform") or "").strip()
    if not name:
        raise ValueError("account name is required")
    _validate_platform(platform)
    login_type = payload.get("login_type") or "qrcode"
    _validate_platform_login_type(platform, login_type)
    status = _validate_pool_status(payload.get("status") or "standby")
    now = utc_now()
    profile_path = (payload.get("profile_path") or "").strip()
    if account_id and not profile_path:
        profile_path = _default_account_profile_path(platform, name, account_id)
    values = (
        name,
        platform,
        login_type,
        status,
        profile_path,
        _safe_int(payload.get("proxy_id")) or None,
        payload.get("notes") or "",
        payload.get("last_error") or "",
        now,
    )
    with get_conn() as conn:
        if account_id:
            exists = conn.execute("SELECT id FROM social_accounts WHERE id=?", (account_id,)).fetchone()
            if not exists:
                raise ValueError("account not found")
            conn.execute(
                """
                UPDATE social_accounts SET name=?, platform=?, login_type=?, status=?,
                    profile_path=?, proxy_id=?, notes=?, last_error=?, updated_at=? WHERE id=?
                """,
                (*values, account_id),
            )
            target_id = account_id
        else:
            cur = conn.execute(
                """
                INSERT INTO social_accounts (
                    name, platform, login_type, status, profile_path, proxy_id, notes,
                    last_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*values[:-1], now, now),
            )
            target_id = int(cur.lastrowid)
            if not profile_path:
                profile_path = _default_account_profile_path(platform, name, target_id)
                conn.execute(
                    "UPDATE social_accounts SET profile_path=?, updated_at=? WHERE id=?",
                    (profile_path, now, target_id),
                )
    return get_social_account(target_id) or {}


def get_social_account(account_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM social_accounts WHERE id=?", (account_id,)).fetchone()
    return _row_to_pool_item(dict(row)) if row else None


def _default_account_profile_path(platform: str, account_name: str, account_id: int | None = None) -> str:
    slug_source = f"{platform}_{account_id or ''}_{account_name}"
    slug = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]+", "_", slug_source).strip("_") or platform
    slug = slug[:80]
    return str((ACCOUNT_PROFILE_ROOT / platform / slug).resolve())


def delete_social_account(account_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM social_accounts WHERE id=?", (account_id,))


def list_proxy_profiles(masked: bool = True) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM proxy_profiles ORDER BY id DESC").fetchall()
    return [_row_to_proxy_profile(dict(row), masked) for row in rows]


def save_proxy_profile(payload: dict[str, Any], proxy_id: int | None = None) -> dict[str, Any]:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("proxy name is required")
    status = _validate_pool_status(payload.get("status") or "standby")
    max_concurrency = max(1, int(payload.get("max_concurrency") or 1))
    current = get_proxy_profile(proxy_id, masked=False) if proxy_id else {}
    proxy_url = str(payload.get("proxy_url") or "") or (current or {}).get("proxy_url") or ""
    now = utc_now()
    with get_conn() as conn:
        if proxy_id:
            exists = conn.execute("SELECT id FROM proxy_profiles WHERE id=?", (proxy_id,)).fetchone()
            if not exists:
                raise ValueError("proxy not found")
            conn.execute(
                """
                UPDATE proxy_profiles SET name=?, provider=?, proxy_url_encrypted=?, status=?,
                    max_concurrency=?, notes=?, last_error=?, updated_at=? WHERE id=?
                """,
                (
                    name,
                    (payload.get("provider") or "manual").strip(),
                    encrypt_secret(proxy_url),
                    status,
                    max_concurrency,
                    payload.get("notes") or "",
                    payload.get("last_error") or "",
                    now,
                    proxy_id,
                ),
            )
            target_id = proxy_id
        else:
            cur = conn.execute(
                """
                INSERT INTO proxy_profiles (
                    name, provider, proxy_url_encrypted, status, max_concurrency,
                    notes, last_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    (payload.get("provider") or "manual").strip(),
                    encrypt_secret(proxy_url),
                    status,
                    max_concurrency,
                    payload.get("notes") or "",
                    payload.get("last_error") or "",
                    now,
                    now,
                ),
            )
            target_id = int(cur.lastrowid)
    return get_proxy_profile(target_id, masked=True) or {}


def get_proxy_profile(proxy_id: int | None, masked: bool = True) -> dict[str, Any] | None:
    if not proxy_id:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM proxy_profiles WHERE id=?", (proxy_id,)).fetchone()
    return _row_to_proxy_profile(dict(row), masked) if row else None


def delete_proxy_profile(proxy_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM proxy_profiles WHERE id=?", (proxy_id,))


def create_login_session(payload: dict[str, Any]) -> dict[str, Any]:
    platform = (payload.get("platform") or "").strip()
    _validate_platform(platform)
    account_id = _safe_int(payload.get("account_id")) or None
    login_url = (payload.get("login_url") or "").strip()
    profile_path = (payload.get("profile_path") or "").strip()
    message = payload.get("message") or (
        "当前 MediaCrawler 版本暂未稳定回传网页登录二维码；请先使用本地/远程浏览器窗口完成扫码，后续会升级为页面二维码登录。"
    )
    now = utc_now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO login_sessions (
                platform, account_id, status, login_url, qr_image, profile_path,
                message, created_at, updated_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                account_id,
                "waiting_manual_browser",
                login_url,
                payload.get("qr_image") or "",
                profile_path,
                message,
                now,
                now,
                payload.get("expires_at") or "",
            ),
        )
        target_id = int(cur.lastrowid)
    return get_login_session(target_id) or {}


def get_login_session(session_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM login_sessions WHERE id=?", (session_id,)).fetchone()
    return dict(row) if row else None


def list_login_sessions(limit: int = 20) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit, 20)
    sql = "SELECT * FROM login_sessions ORDER BY id DESC"
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def expire_login_sessions_for_account(account_id: int | None, platform: str, profile_path: str = "") -> list[int]:
    _validate_platform(platform)
    clauses = ["platform=?", "status IN ('waiting_qrcode', 'waiting_manual_browser', 'scanned')"]
    params: list[Any] = [platform]
    if account_id:
        clauses.append("account_id=?")
        params.append(account_id)
    elif profile_path:
        clauses.append("profile_path=?")
        params.append(profile_path)
    else:
        return []
    where = " AND ".join(clauses)
    now = utc_now()
    with get_conn() as conn:
        rows = conn.execute(f"SELECT id FROM login_sessions WHERE {where}", params).fetchall()
        ids = [int(row["id"]) for row in rows]
        if ids:
            placeholders = ",".join("?" for _ in ids)
            conn.execute(
                f"UPDATE login_sessions SET status='expired', message=?, updated_at=? WHERE id IN ({placeholders})",
                ["已被新的登录会话替换", now, *ids],
            )
    return ids


def update_login_session_status(session_id: int, status: str, message: str = "", qr_image: str = "") -> dict[str, Any]:
    allowed = {"waiting_qrcode", "waiting_manual_browser", "scanned", "success", "expired", "failed"}
    if status not in allowed:
        raise ValueError("invalid login session status")
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM login_sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            raise ValueError("login session not found")
        conn.execute(
            """
            UPDATE login_sessions SET status=?, message=?, qr_image=COALESCE(NULLIF(?, ''), qr_image), updated_at=?
            WHERE id=?
            """,
            (status, message, qr_image, utc_now(), session_id),
        )
    return get_login_session(session_id) or {}


def delete_login_session(session_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM login_sessions WHERE id=?", (session_id,))


def _row_to_proxy_profile(row: dict[str, Any], masked: bool) -> dict[str, Any]:
    encrypted = row.pop("proxy_url_encrypted", "")
    row["proxy_url"] = mask_secret(encrypted) if masked else decrypt_secret(encrypted)
    return _row_to_pool_item(row)


def _row_to_pool_item(row: dict[str, Any]) -> dict[str, Any]:
    return row


def _validate_pool_status(status: str) -> str:
    if status not in {"standby", "active", "limited", "disabled"}:
        raise ValueError("invalid pool status")
    return status


def _coerce_limit(value: Any, default: int = 100) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def _redact_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _redact_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_json(item) for item in value]
    if isinstance(value, str):
        return redact_sensitive(value)
    return value
