from __future__ import annotations

import json
import sqlite3
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .mediacrawler_login import LOGIN_TYPE_LABELS, PLATFORM_LOGIN_TYPES, SUPPORTED_MONITOR_PLATFORMS, get_mediacrawler_login_capability
from .prompts import DEFAULT_PROMPT
from .security import MONITOR_DATA_DIR, customer_safe_text, decrypt_secret, encrypt_secret, mask_secret, redact_sensitive


DB_PATH = MONITOR_DATA_DIR / "monitor.sqlite"
DEFAULT_EMAIL_SUBJECT_TEMPLATE = "【律所舆情日报】{law_firm_name} - {date}"
DEFAULT_EMAIL_TEMPLATE_NAME = "标准舆情日报模板"
JOB_TEMPLATE_PLACEHOLDERS = ("请改成", "目标律所", "律所简称", "律师事务所简称")
JOB_TARGET_TYPES = {"search", "detail", "creator"}
JOB_OUTPUT_MODES = {"internal", "json", "excel"}
JOB_BROWSER_MODES = {"server_qrcode", "profile", "local_window"}

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
                enable_sub_comments INTEGER NOT NULL DEFAULT 0,
                time_window_type TEXT NOT NULL DEFAULT 'recent_1d',
                custom_start TEXT,
                custom_end TEXT,
                frequency TEXT NOT NULL DEFAULT 'daily',
                cron_expr TEXT,
                email_time TEXT NOT NULL DEFAULT '09:00',
                target_type TEXT NOT NULL DEFAULT 'search',
                max_pages INTEGER NOT NULL DEFAULT 1,
                max_items INTEGER NOT NULL DEFAULT 50,
                start_page INTEGER NOT NULL DEFAULT 1,
                output_mode TEXT NOT NULL DEFAULT 'internal',
                browser_mode TEXT NOT NULL DEFAULT 'server_qrcode',
                ai_profile_id INTEGER,
                email_template_id INTEGER,
                account_id INTEGER,
                proxy_id INTEGER,
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
                login_phone_encrypted TEXT NOT NULL DEFAULT '',
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

            CREATE TABLE IF NOT EXISTS ai_rule_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
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
                cookies_encrypted TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'standby',
                profile_path TEXT NOT NULL DEFAULT '',
                proxy_id INTEGER,
                is_draft INTEGER NOT NULL DEFAULT 0,
                platform_account_id TEXT NOT NULL DEFAULT '',
                platform_account_name TEXT NOT NULL DEFAULT '',
                platform_avatar_url TEXT NOT NULL DEFAULT '',
                platform_home_url TEXT NOT NULL DEFAULT '',
                platform_identity_checked_at TEXT,
                notes TEXT NOT NULL DEFAULT '',
                last_used_at TEXT,
                last_checked_at TEXT,
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
        _ensure_column(conn, "monitor_jobs", "enable_sub_comments", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "monitor_jobs", "target_type", "TEXT NOT NULL DEFAULT 'search'")
        _ensure_column(conn, "monitor_jobs", "max_pages", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "monitor_jobs", "max_items", "INTEGER NOT NULL DEFAULT 50")
        _ensure_column(conn, "monitor_jobs", "start_page", "INTEGER NOT NULL DEFAULT 1")
        _ensure_column(conn, "monitor_jobs", "output_mode", "TEXT NOT NULL DEFAULT 'internal'")
        _ensure_column(conn, "monitor_jobs", "browser_mode", "TEXT NOT NULL DEFAULT 'server_qrcode'")
        _ensure_column(conn, "monitor_jobs", "ai_profile_id", "INTEGER")
        _ensure_column(conn, "monitor_jobs", "email_template_id", "INTEGER")
        _ensure_column(conn, "monitor_jobs", "account_id", "INTEGER")
        _ensure_column(conn, "monitor_jobs", "proxy_id", "INTEGER")
        _ensure_column(conn, "ai_configs", "last_test_status", "TEXT NOT NULL DEFAULT 'untested'")
        _ensure_column(conn, "ai_configs", "last_test_at", "TEXT")
        _ensure_column(conn, "ai_configs", "last_test_error", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "email_configs", "last_test_status", "TEXT NOT NULL DEFAULT 'untested'")
        _ensure_column(conn, "email_configs", "last_test_at", "TEXT")
        _ensure_column(conn, "email_configs", "last_test_error", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "platform_login_configs", "login_phone_encrypted", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "cookies_encrypted", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "is_draft", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "social_accounts", "last_checked_at", "TEXT")
        _ensure_column(conn, "social_accounts", "platform_account_id", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "platform_account_name", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "platform_avatar_url", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "platform_home_url", "TEXT NOT NULL DEFAULT ''")
        _ensure_column(conn, "social_accounts", "platform_identity_checked_at", "TEXT")
        _migrate_raw_contents_unique_by_job(conn)
        mark_selftest_jobs_internal(conn)
        now = utc_now()
        conn.execute(
            "INSERT OR IGNORE INTO ai_configs (id, updated_at) VALUES (1, ?)",
            (now,),
        )
        _ensure_default_ai_rule_profile(conn)
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
        conn.execute("UPDATE platform_login_configs SET login_type='qrcode', updated_at=? WHERE login_type NOT IN ('qrcode', 'cookie')", (now,))
        conn.execute("UPDATE social_accounts SET login_type='qrcode', updated_at=? WHERE login_type NOT IN ('qrcode', 'cookie')", (now,))
        if not conn.execute("SELECT 1 FROM email_templates LIMIT 1").fetchone():
            conn.execute(
                """
                INSERT INTO email_templates (name, subject_template, html_template, is_active, created_at, updated_at)
                VALUES (?, ?, ?, 1, ?, ?)
                """,
                (
                    DEFAULT_EMAIL_TEMPLATE_NAME,
                    DEFAULT_EMAIL_SUBJECT_TEMPLATE,
                    _default_email_preview_html(),
                    now,
                    now,
                ),
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
    result["enable_sub_comments"] = bool(result.get("enable_sub_comments", 0))
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
        raise ValueError("律所名称不能为空")
    keywords = [str(k).strip() for k in payload.get("keywords", []) if str(k).strip()]
    if not keywords:
        raise ValueError("平台搜索词不能为空")
    if has_job_template_placeholders({"law_firm_name": law_firm_name, "keywords": keywords}):
        raise ValueError("请先把测试数据模板里的律所名称和平台搜索词改成真实内容")
    platforms = [p for p in payload.get("platforms", []) if p in {"dy", "ks", "xhs"}]
    if not platforms:
        raise ValueError("请至少选择一个采集平台")
    recipients = [str(e).strip() for e in payload.get("recipients", []) if str(e).strip()]
    validate_recipients(recipients)
    aliases = [str(v).strip() for v in payload.get("aliases", []) if str(v).strip()]
    exclude_words = [str(v).strip() for v in payload.get("exclude_words", []) if str(v).strip()]
    time_window_type = _validate_time_window(payload)
    frequency = _validate_frequency(payload)
    email_time = _validate_email_time(payload.get("email_time") or "09:00")
    target_type = _validate_choice(_payload_value(payload, "target_type", "job_target_type", default="search"), JOB_TARGET_TYPES, "target_type")
    max_pages = _validate_positive_int(_payload_value(payload, "max_pages", "job_max_pages", default=1), "max_pages", minimum=1, maximum=100)
    max_items = _validate_positive_int(_payload_value(payload, "max_items", "job_max_items", default=50), "max_items", minimum=1, maximum=5000)
    start_page = _validate_positive_int(_payload_value(payload, "start_page", "job_start_page", default=1), "start_page", minimum=1, maximum=100)
    output_mode = _validate_choice(_payload_value(payload, "output_mode", "job_output_mode", default="internal"), JOB_OUTPUT_MODES, "output_mode")
    browser_mode = _validate_choice(_payload_value(payload, "browser_mode", "job_browser_mode", default="server_qrcode"), JOB_BROWSER_MODES, "browser_mode")
    ai_profile_id = _optional_existing_id(payload.get("ai_profile_id") or payload.get("job_ai_profile_id"), "ai_key_profiles", "AI Profile")
    email_template_id = _optional_existing_id(payload.get("email_template_id") or payload.get("job_email_template_id"), "email_templates", "email template")
    account_id = _optional_existing_id(payload.get("account_id") or payload.get("job_account_id"), "social_accounts", "social account")
    proxy_id = _optional_existing_id(payload.get("proxy_id") or payload.get("job_proxy_id"), "proxy_profiles", "proxy profile")
    enable_sub_comments = bool(payload.get("enable_sub_comments", False))
    with get_conn() as conn:
        if job_id:
            exists = conn.execute("SELECT id FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
            if not exists:
                raise ValueError("job not found")
            conn.execute(
                """
                UPDATE monitor_jobs SET law_firm_name=?, aliases=?, exclude_words=?,
                    enable_comments=?, enable_sub_comments=?, time_window_type=?, custom_start=?, custom_end=?,
                    frequency=?, cron_expr=?, email_time=?, target_type=?, max_pages=?, max_items=?,
                    start_page=?, output_mode=?, browser_mode=?, ai_profile_id=?, email_template_id=?,
                    account_id=?, proxy_id=?, enabled=?, is_internal=?, updated_at=?
                WHERE id=?
                """,
                (
                    law_firm_name,
                    _json_dumps(aliases),
                    _json_dumps(exclude_words),
                    1 if payload.get("enable_comments", True) else 0,
                    1 if enable_sub_comments else 0,
                    time_window_type,
                    payload.get("custom_start") or None,
                    payload.get("custom_end") or None,
                    frequency,
                    payload.get("cron_expr") or None,
                    email_time,
                    target_type,
                    max_pages,
                    max_items,
                    start_page,
                    output_mode,
                    browser_mode,
                    ai_profile_id,
                    email_template_id,
                    account_id,
                    proxy_id,
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
                    law_firm_name, aliases, exclude_words, enable_comments, enable_sub_comments, time_window_type,
                    custom_start, custom_end, frequency, cron_expr, email_time, target_type, max_pages, max_items,
                    start_page, output_mode, browser_mode, ai_profile_id, email_template_id, account_id, proxy_id,
                    enabled, is_internal,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    law_firm_name,
                    _json_dumps(aliases),
                    _json_dumps(exclude_words),
                    1 if payload.get("enable_comments", True) else 0,
                    1 if enable_sub_comments else 0,
                    time_window_type,
                    payload.get("custom_start") or None,
                    payload.get("custom_end") or None,
                    frequency,
                    payload.get("cron_expr") or None,
                    email_time,
                    target_type,
                    max_pages,
                    max_items,
                    start_page,
                    output_mode,
                    browser_mode,
                    ai_profile_id,
                    email_template_id,
                    account_id,
                    proxy_id,
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


def _validate_choice(value: Any, allowed: set[str], field: str) -> str:
    normalized = str(value or "").strip()
    if normalized not in allowed:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(allowed))}")
    return normalized


def _payload_value(payload: dict[str, Any], key: str, legacy_key: str, default: Any) -> Any:
    for candidate in (key, legacy_key):
        if candidate in payload and payload.get(candidate) not in (None, ""):
            return payload.get(candidate)
    return default


def _validate_positive_int(value: Any, field: str, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    if number < minimum or number > maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return number


def _optional_existing_id(value: Any, table: str, label: str) -> int | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        target_id = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {label} id") from exc
    with get_conn() as conn:
        row = conn.execute(f"SELECT id FROM {table} WHERE id=?", (target_id,)).fetchone()
    if not row:
        raise ValueError(f"{label} not found")
    return target_id


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
        active_rule = conn.execute("SELECT id, name, prompt FROM ai_rule_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
        if active_rule:
            data["prompt"] = active_rule["prompt"] or data.get("prompt") or ""
            data["ai_rule_profile_id"] = active_rule["id"]
            data["ai_rule_profile_name"] = active_rule["name"]
    data["api_key"] = mask_secret(data.pop("api_key_encrypted")) if masked else decrypt_secret(data.pop("api_key_encrypted"))
    return data


def _ensure_default_ai_rule_profile(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT id FROM ai_rule_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
    if row:
        return
    legacy = conn.execute("SELECT prompt FROM ai_configs WHERE id=1").fetchone()
    prompt = (legacy["prompt"] if legacy else "") or DEFAULT_PROMPT
    now = utc_now()
    conn.execute(
        """
        INSERT INTO ai_rule_profiles (
            name, prompt, is_active, last_test_status, last_test_at, last_test_error, created_at, updated_at
        ) VALUES (?, ?, 1, 'untested', NULL, '', ?, ?)
        """,
        ("默认评估规则", prompt, now, now),
    )


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
    provider = payload.get("provider") or current.get("provider") or "openai"
    if provider not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    temperature = validate_temperature(payload.get("temperature", current.get("temperature", 0)) or 0)
    next_config = {
        "provider": provider,
        "base_url": (payload.get("base_url") if payload.get("base_url") is not None else current.get("base_url") or "").strip(),
        "api_key": next_api_key or "",
        "model": (payload.get("model") if payload.get("model") is not None else current.get("model") or "").strip(),
        "temperature": temperature,
        "prompt": payload.get("prompt") if payload.get("prompt") is not None else current.get("prompt") or "",
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
        if payload.get("prompt") is not None:
            _ensure_default_ai_rule_profile(conn)
            conn.execute(
                """
                UPDATE ai_rule_profiles SET prompt=?, last_test_status=?, last_test_at=?,
                    last_test_error=?, updated_at=? WHERE id=(
                        SELECT id FROM ai_rule_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1
                    )
                """,
                (
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
        row = conn.execute("SELECT id FROM ai_rule_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            conn.execute(
                """
                UPDATE ai_rule_profiles SET last_test_status=?, last_test_at=?, last_test_error=?, updated_at=?
                WHERE id=?
                """,
                ("success" if success else "failed", utc_now(), "" if success else _trim_error(error), utc_now(), row["id"]),
            )
    return get_ai_config(masked=True)


def list_ai_rule_profiles() -> list[dict[str, Any]]:
    with get_conn() as conn:
        _ensure_default_ai_rule_profile(conn)
        rows = conn.execute("SELECT * FROM ai_rule_profiles ORDER BY is_active DESC, id DESC").fetchall()
    return [_row_to_ai_rule_profile(dict(row)) for row in rows]


def get_ai_rule_profile(rule_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM ai_rule_profiles WHERE id=?", (rule_id,)).fetchone()
    return _row_to_ai_rule_profile(dict(row)) if row else None


def get_active_ai_rule_profile() -> dict[str, Any] | None:
    with get_conn() as conn:
        _ensure_default_ai_rule_profile(conn)
        row = conn.execute("SELECT * FROM ai_rule_profiles WHERE is_active=1 ORDER BY id DESC LIMIT 1").fetchone()
    return _row_to_ai_rule_profile(dict(row)) if row else None


def save_ai_rule_profile(payload: dict[str, Any], rule_id: int | None = None) -> dict[str, Any]:
    current = get_ai_rule_profile(rule_id) if rule_id else {}
    name = (payload.get("name") or (current or {}).get("name") or "").strip()
    if not name:
        raise ValueError("rule name is required")
    prompt = (payload.get("prompt") if payload.get("prompt") is not None else (current or {}).get("prompt") or "").strip()
    if not prompt:
        prompt = DEFAULT_PROMPT
    is_active = bool(payload.get("is_active", (current or {}).get("is_active", False)))
    changed = not current or (current.get("prompt") or "") != prompt or (current.get("name") or "") != name
    test_state = _next_test_state(current or {}, changed)
    now = utc_now()
    with get_conn() as conn:
        if is_active:
            conn.execute("UPDATE ai_rule_profiles SET is_active=0")
        if rule_id:
            exists = conn.execute("SELECT id FROM ai_rule_profiles WHERE id=?", (rule_id,)).fetchone()
            if not exists:
                raise ValueError("AI rule profile not found")
            conn.execute(
                """
                UPDATE ai_rule_profiles SET name=?, prompt=?, is_active=?, last_test_status=?,
                    last_test_at=?, last_test_error=?, updated_at=? WHERE id=?
                """,
                (
                    name,
                    prompt,
                    1 if is_active else 0,
                    test_state["last_test_status"],
                    test_state["last_test_at"],
                    test_state["last_test_error"],
                    now,
                    rule_id,
                ),
            )
            target_id = rule_id
        else:
            cur = conn.execute(
                """
                INSERT INTO ai_rule_profiles (
                    name, prompt, is_active, last_test_status, last_test_at, last_test_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    prompt,
                    1 if is_active else 0,
                    test_state["last_test_status"],
                    test_state["last_test_at"],
                    test_state["last_test_error"],
                    now,
                    now,
                ),
            )
            target_id = int(cur.lastrowid)
        if is_active:
            conn.execute("UPDATE ai_configs SET prompt=?, updated_at=? WHERE id=1", (prompt, now))
    return get_ai_rule_profile(target_id) or {}


def delete_ai_rule_profile(rule_id: int) -> None:
    with get_conn() as conn:
        active_count = conn.execute("SELECT COUNT(*) AS n FROM ai_rule_profiles").fetchone()["n"]
        if int(active_count or 0) <= 1:
            raise ValueError("至少保留一套评估规则")
        row = conn.execute("SELECT is_active FROM ai_rule_profiles WHERE id=?", (rule_id,)).fetchone()
        if not row:
            raise ValueError("AI rule profile not found")
        conn.execute("DELETE FROM ai_rule_profiles WHERE id=?", (rule_id,))
        if row["is_active"]:
            fallback = conn.execute("SELECT id, prompt FROM ai_rule_profiles ORDER BY id DESC LIMIT 1").fetchone()
            if fallback:
                conn.execute("UPDATE ai_rule_profiles SET is_active=1, updated_at=? WHERE id=?", (utc_now(), fallback["id"]))
                conn.execute("UPDATE ai_configs SET prompt=?, updated_at=? WHERE id=1", (fallback["prompt"], utc_now()))


def set_active_ai_rule_profile(rule_id: int) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT id, prompt FROM ai_rule_profiles WHERE id=?", (rule_id,)).fetchone()
        if not row:
            raise ValueError("AI rule profile not found")
        now = utc_now()
        conn.execute("UPDATE ai_rule_profiles SET is_active=0")
        conn.execute("UPDATE ai_rule_profiles SET is_active=1, updated_at=? WHERE id=?", (now, rule_id))
        conn.execute("UPDATE ai_configs SET prompt=?, updated_at=? WHERE id=1", (row["prompt"], now))
    return get_ai_rule_profile(rule_id) or {}


def mark_ai_rule_profile_test_result(rule_id: int, success: bool, error: str | None = None) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM ai_rule_profiles WHERE id=?", (rule_id,)).fetchone()
        if not row:
            raise ValueError("AI rule profile not found")
        conn.execute(
            """
            UPDATE ai_rule_profiles SET last_test_status=?, last_test_at=?, last_test_error=?, updated_at=?
            WHERE id=?
            """,
            ("success" if success else "failed", utc_now(), "" if success else _trim_error(error), utc_now(), rule_id),
        )
    return get_ai_rule_profile(rule_id) or {}


def _row_to_ai_rule_profile(row: dict[str, Any]) -> dict[str, Any]:
    row["is_active"] = bool(row.get("is_active"))
    row["last_test_error"] = customer_safe_text(row.get("last_test_error"))
    return row


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
    if login_type == "phone":
        raise ValueError("当前版本暂未开放手机号登录，请使用扫码或 Cookie 登录")
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
            INSERT INTO platform_login_configs (platform, login_type, cookies_encrypted, login_phone_encrypted, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(platform) DO UPDATE SET
                login_type=excluded.login_type,
                cookies_encrypted=excluded.cookies_encrypted,
                login_phone_encrypted=excluded.login_phone_encrypted,
                updated_at=excluded.updated_at
            """,
            (platform, login_type, encrypt_secret(cookies), "", utc_now()),
        )
    return get_platform_login_config(platform, masked=True)


def _row_to_platform_login_config(row: dict[str, Any], masked: bool) -> dict[str, Any]:
    platform = row.get("platform") or ""
    capability = get_mediacrawler_login_capability(platform)
    supported_types = tuple(capability.get("supported_login_types") or PLATFORM_LOGIN_TYPES.get(platform, ("qrcode", "cookie")))
    encrypted = row.get("cookies_encrypted") or ""
    cookies = mask_secret(encrypted) if masked else decrypt_secret(encrypted)
    raw_cookies = decrypt_secret(encrypted)
    login_type = row.get("login_type") or "qrcode"
    if login_type not in {"qrcode", "cookie"}:
        login_type = "qrcode"
    return {
        "platform": platform,
        "login_type": login_type,
        "login_type_label": LOGIN_TYPE_LABELS.get(login_type, login_type),
        "supported_login_types": list(supported_types),
        "supported_login_type_labels": capability.get("supported_login_type_labels")
        or {item: LOGIN_TYPE_LABELS.get(item, item) for item in supported_types},
        "login_capability_source": "平台采集服务",
        "login_url": capability.get("login_url") or "",
        "login_engine": "平台采集服务登录模块",
        "login_class": "",
        "bridge_role": capability.get("bridge_role") or "",
        "qrcode_capture_method": "页面二维码回传",
        "qrcode_prepare_method": "平台登录会话",
        "qrcode_flow_steps": [
            "打开平台登录页",
            "等待二维码或平台验证提示",
            "前端展示二维码、截图或验证状态",
            "运营扫码或按页面提示处理后，系统保存登录状态",
        ],
        "integration_note": "后台只包装平台采集服务已有登录方式；验证码、滑块、短信只回传状态，不自动绕过。",
        "qrcode_supported": bool(capability.get("qrcode_supported")),
        "phone_supported": False,
        "unsupported_reason": _unsupported_login_reason(platform),
        "cookies": cookies,
        "has_cookies": bool(raw_cookies),
        "updated_at": row.get("updated_at"),
    }


def _default_platform_login_config(platform: str, masked: bool = True) -> dict[str, Any]:
    return _row_to_platform_login_config(
        {"platform": platform, "login_type": "qrcode", "cookies_encrypted": "", "login_phone_encrypted": "", "updated_at": None},
        masked,
    )


def _validate_platform(platform: str) -> None:
    if platform not in SUPPORTED_MONITOR_PLATFORMS:
        raise ValueError("unsupported platform")


def _validate_platform_login_type(platform: str, login_type: str) -> None:
    supported = tuple(get_mediacrawler_login_capability(platform).get("supported_login_types") or PLATFORM_LOGIN_TYPES.get(platform, ()))
    if login_type not in supported:
        labels = " / ".join(LOGIN_TYPE_LABELS.get(item, item) for item in supported)
        extra = _unsupported_login_reason(platform)
        suffix = f"；{extra}" if extra else ""
        raise ValueError(f"{platform} does not support login_type={login_type}; supported: {labels}{suffix}")


def _unsupported_login_reason(platform: str) -> str:
    return "当前版本暂未开放手机号登录，请使用扫码或 Cookie 登录。"


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


def record_skipped_run(job_id: int, reason: str, summary: dict[str, Any] | None = None, cooldown_seconds: int = 300) -> int:
    payload = dict(summary or {})
    payload.setdefault("job_id", job_id)
    payload.setdefault("skipped", True)
    payload.setdefault("skip_reason", reason)
    now = utc_now()
    with get_conn() as conn:
        if cooldown_seconds > 0:
            cutoff = (datetime.now(timezone.utc) - timedelta(seconds=cooldown_seconds)).isoformat()
            existing = conn.execute(
                """
                SELECT id FROM crawl_runs
                WHERE job_id=? AND status='skipped' AND error_message=? AND started_at>=?
                ORDER BY id DESC LIMIT 1
                """,
                (job_id, _trim_error(reason), cutoff),
            ).fetchone()
            if existing:
                return int(existing["id"])
        cur = conn.execute(
            """
            INSERT INTO crawl_runs (job_id, status, started_at, finished_at, summary, error_message)
            VALUES (?, 'skipped', ?, ?, ?, ?)
            """,
            (job_id, now, now, json.dumps(_redact_json(payload), ensure_ascii=False), _trim_error(reason)),
        )
        return int(cur.lastrowid)


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
    if not item.get("law_firm_name"):
        item["law_firm_name"] = summary.get("law_firm_name") or ""
    item["law_firm_name"] = customer_safe_text(item.get("law_firm_name"))
    if item.get("status") == "running":
        summary["duration_seconds"] = summary.get("duration_seconds") or _elapsed_seconds(item.get("started_at"))
    item["summary"] = _customer_safe_payload(summary)
    is_legacy_without_snapshot = current_job_id is None and snapshot_job_id is None and not summary.get("selftest")
    item["display_law_firm_name"] = customer_safe_text(item.get("law_firm_name") or summary.get("law_firm_name") or (
        "旧记录无任务快照" if is_legacy_without_snapshot else ""
    ))
    item["job_deleted"] = bool(snapshot_job_id and not current_job_id)
    item["legacy_without_job_snapshot"] = bool(is_legacy_without_snapshot)
    item["display_status"] = _run_display_status(str(item.get("status") or ""), summary)
    item["display_error"] = customer_safe_text(_run_display_error(item, summary))
    item["error_message"] = customer_safe_text(item.get("error_message"))
    return item


def _run_display_status(status: str, summary: dict[str, Any]) -> str:
    if status == "skipped":
        skip_type = summary.get("skip_type")
        if skip_type == "preflight_blocked":
            return "预检拦截"
        if skip_type == "template_placeholders":
            return "模板未填写"
        return "已跳过"
    labels = {
        "running": "运行中",
        "success": "成功",
        "partial_failed": "部分失败",
        "failed": "失败",
        "cancelled": "已停止",
    }
    return labels.get(status, status or "")


def _run_display_error(item: dict[str, Any], summary: dict[str, Any]) -> str:
    status = str(item.get("status") or "")
    if status == "skipped":
        return str(summary.get("skip_reason") or item.get("error_message") or "")
    if item.get("error_message"):
        return str(item.get("error_message") or "")
    if summary.get("cancel_reason"):
        return str(summary.get("cancel_reason") or "")
    return ""


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
    item["summary"] = _customer_safe_payload(summary)
    if not item.get("law_firm_name"):
        item["law_firm_name"] = summary.get("law_firm_name") or ""
    item["law_firm_name"] = customer_safe_text(item.get("law_firm_name"))
    item["display_law_firm_name"] = customer_safe_text(item.get("law_firm_name") or summary.get("law_firm_name") or "")
    item["email_error"] = customer_safe_text(item.get("email_error"))
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
        item["evidence_quotes"] = [customer_safe_text(str(q)) for q in _json_loads(item.get("evidence_quotes"))]
        for key in ("law_firm_name", "source_keyword", "title", "description", "author_name", "reason", "recommended_action"):
            item[key] = customer_safe_text(item.get(key))
        result.append(item)
    return result


def _customer_safe_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _customer_safe_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_customer_safe_payload(item) for item in value]
    if isinstance(value, str):
        return customer_safe_text(value)
    return value


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
        social_total = conn.execute("SELECT COUNT(*) AS n FROM social_accounts WHERE COALESCE(is_draft, 0)=0").fetchone()["n"]
        proxy_total = conn.execute("SELECT COUNT(*) AS n FROM proxy_profiles").fetchone()["n"]
        ai_profiles_total = conn.execute("SELECT COUNT(*) AS n FROM ai_key_profiles").fetchone()["n"]
        login_sessions_total = conn.execute("SELECT COUNT(*) AS n FROM login_sessions").fetchone()["n"]
        latest_runs = conn.execute("SELECT status, summary, started_at, finished_at FROM crawl_runs ORDER BY id DESC LIMIT 20").fetchall()
    failed_runs = 0
    skipped_runs = 0
    platform_counts: dict[str, int] = {}
    for row in latest_runs:
        if row["status"] in {"failed", "partial_failed", "cancelled"}:
            failed_runs += 1
        if row["status"] == "skipped":
            skipped_runs += 1
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
        "skipped_runs_recent": skipped_runs,
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


def mark_ai_key_profile_test_result(profile_id: int, success: bool, error: str | None = None) -> dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM ai_key_profiles WHERE id=?", (profile_id,)).fetchone()
        if not row:
            raise ValueError("AI profile not found")
        conn.execute(
            """
            UPDATE ai_key_profiles SET last_test_status=?, last_test_at=?, last_test_error=?, updated_at=?
            WHERE id=?
            """,
            ("success" if success else "failed", utc_now(), "" if success else _trim_error(error), utc_now(), profile_id),
        )
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
        "report_body": _sample_report_html(),
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


def list_social_accounts(masked: bool = True, include_drafts: bool = False) -> list[dict[str, Any]]:
    where = "" if include_drafts else "WHERE COALESCE(a.is_draft, 0)=0"
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT
                a.*,
                p.name AS proxy_name,
                p.provider AS proxy_provider,
                p.status AS proxy_status,
                p.max_concurrency AS proxy_max_concurrency,
                p.last_error AS proxy_last_error
            FROM social_accounts a
            LEFT JOIN proxy_profiles p ON p.id = a.proxy_id
            {where}
            ORDER BY a.platform, a.id DESC
            """
        ).fetchall()
    return [_row_to_pool_item(dict(row), masked=masked) for row in rows]


def save_social_account(payload: dict[str, Any], account_id: int | None = None) -> dict[str, Any]:
    name = (payload.get("name") or "").strip()
    platform = (payload.get("platform") or "").strip()
    if not name:
        raise ValueError("account name is required")
    _validate_platform(platform)
    login_type = payload.get("login_type") or "qrcode"
    _validate_platform_login_type(platform, login_type)
    status = _validate_pool_status(payload.get("status") or "standby")
    is_draft = 1 if payload.get("is_draft") else 0
    now = utc_now()
    profile_path = (payload.get("profile_path") or "").strip()
    if account_id and not profile_path:
        profile_path = _default_account_profile_path(platform, name, account_id)
    proxy_id = _safe_int(payload.get("proxy_id")) or None
    if proxy_id and not get_proxy_profile(proxy_id, masked=True):
        raise ValueError("proxy not found")
    current_cookies = ""
    if account_id:
        with get_conn() as conn:
            row = conn.execute("SELECT cookies_encrypted FROM social_accounts WHERE id=?", (account_id,)).fetchone()
        if row:
            current_cookies = decrypt_secret(row["cookies_encrypted"] or "")
    if payload.get("clear_cookies"):
        cookies = ""
    elif "cookies" in payload and str(payload.get("cookies") or "").strip():
        cookies = str(payload.get("cookies") or "").strip()
    else:
        cookies = current_cookies
    if login_type == "cookie" and not cookies:
        raise ValueError("Cookie 登录需要先填写 Cookie")
    values = (
        name,
        platform,
        login_type,
        encrypt_secret(cookies),
        status,
        profile_path,
        proxy_id,
        is_draft,
        payload.get("notes") or "",
        payload.get("last_error") or "",
        now,
    )
    with get_conn() as conn:
        _ensure_unique_account_profile(conn, profile_path, account_id)
        if account_id:
            exists = conn.execute("SELECT id FROM social_accounts WHERE id=?", (account_id,)).fetchone()
            if not exists:
                raise ValueError("account not found")
            current_platform = conn.execute("SELECT platform FROM social_accounts WHERE id=?", (account_id,)).fetchone()
            if current_platform and current_platform["platform"] != platform:
                raise ValueError("账号平台保存后不可变更，请为新平台新增账号")
            conn.execute(
                """
                UPDATE social_accounts SET name=?, platform=?, login_type=?, cookies_encrypted=?, status=?,
                    profile_path=?, proxy_id=?, is_draft=?, notes=?, last_error=?, updated_at=? WHERE id=?
                """,
                (*values, account_id),
            )
            target_id = account_id
        else:
            cur = conn.execute(
                """
                INSERT INTO social_accounts (
                    name, platform, login_type, cookies_encrypted, status, profile_path, proxy_id, is_draft, notes,
                    last_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*values[:-1], now, now),
            )
            target_id = int(cur.lastrowid)
            if not profile_path:
                profile_path = _default_account_profile_path(platform, name, target_id)
                _ensure_unique_account_profile(conn, profile_path, target_id)
                conn.execute(
                    "UPDATE social_accounts SET profile_path=?, updated_at=? WHERE id=?",
                    (profile_path, now, target_id),
                )
    return get_social_account(target_id) or {}


def create_draft_social_account(payload: dict[str, Any]) -> dict[str, Any]:
    platform = (payload.get("platform") or "").strip()
    _validate_platform(platform)
    name = (payload.get("name") or "").strip() or f"{LOGIN_TYPE_LABELS.get('qrcode', '扫码登录')}临时账号"
    return save_social_account(
        {
            **payload,
            "name": name,
            "platform": platform,
            "login_type": "qrcode",
            "status": "standby",
            "is_draft": True,
        }
    )


def confirm_social_account(account_id: int, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    account = get_social_account(account_id, masked=False)
    if not account:
        raise ValueError("account not found")
    payload = payload or {}
    merged = {
        **account,
        "name": (payload.get("name") or account.get("name") or "").strip(),
        "platform": account.get("platform"),
        "login_type": payload.get("login_type") or account.get("login_type") or "qrcode",
        "status": payload.get("status") or ("active" if account.get("status") == "active" else account.get("status") or "standby"),
        "proxy_id": payload.get("proxy_id") if "proxy_id" in payload else account.get("proxy_id"),
        "profile_path": payload.get("profile_path") or account.get("profile_path") or "",
        "notes": payload.get("notes") if "notes" in payload else account.get("notes") or "",
        "last_error": payload.get("last_error") if "last_error" in payload else account.get("last_error") or "",
        "is_draft": False,
    }
    if not merged["name"]:
        raise ValueError("account name is required")
    return save_social_account(merged, account_id)


def get_social_account(account_id: int, masked: bool = True) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT
                a.*,
                p.name AS proxy_name,
                p.provider AS proxy_provider,
                p.status AS proxy_status,
                p.max_concurrency AS proxy_max_concurrency,
                p.last_error AS proxy_last_error
            FROM social_accounts a
            LEFT JOIN proxy_profiles p ON p.id = a.proxy_id
            WHERE a.id=?
            """,
            (account_id,),
        ).fetchone()
    return _row_to_pool_item(dict(row), masked=masked) if row else None


def _ensure_unique_account_profile(conn: sqlite3.Connection, profile_path: str, account_id: int | None = None) -> None:
    profile_path = str(profile_path or "").strip()
    if not profile_path:
        return
    params: list[Any] = [profile_path]
    sql = "SELECT id FROM social_accounts WHERE lower(profile_path)=lower(?)"
    if account_id:
        sql += " AND id<>?"
        params.append(account_id)
    row = conn.execute(sql, params).fetchone()
    if row:
        raise ValueError("该登录态已被其他账号使用，请为每个账号使用独立登录态")


def _default_account_profile_path(platform: str, account_name: str, account_id: int | None = None) -> str:
    slug_source = f"{platform}_{account_id or ''}_{account_name}"
    slug = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]+", "_", slug_source).strip("_") or platform
    slug = slug[:80]
    return str((ACCOUNT_PROFILE_ROOT / platform / slug).resolve())


def delete_social_account(account_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM social_accounts WHERE id=?", (account_id,))


def update_social_account_login_state(account_id: int | None, status: str, message: str = "") -> dict[str, Any] | None:
    if not account_id:
        return None
    now = utc_now()
    if status == "success":
        account_status = "active"
        last_error = ""
        last_used_at = now
    elif status in {"waiting_verification", "waiting_manual_browser", "failed", "expired"}:
        account_status = "limited" if status == "waiting_verification" else "standby"
        last_error = customer_safe_text(message)
        last_used_at = None
    else:
        return get_social_account(account_id)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE social_accounts
            SET status=?, last_error=?, last_used_at=COALESCE(?, last_used_at), updated_at=?
            WHERE id=?
            """,
            (account_status, last_error, last_used_at, now, account_id),
        )
    return get_social_account(account_id)


def update_social_account_check_state(
    account_id: int,
    ok: bool,
    message: str = "",
    status: str | None = None,
    identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = utc_now()
    account_status = status or ("active" if ok else "limited")
    account_status = _validate_pool_status(account_status)
    last_error = "" if ok else customer_safe_text(message)
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE social_accounts
            SET status=?, last_error=?, last_checked_at=?, updated_at=?
            WHERE id=?
            """,
            (account_status, last_error, now, now, account_id),
        )
        if ok and identity:
            conn.execute(
                """
                UPDATE social_accounts
                SET platform_account_id=?, platform_account_name=?, platform_avatar_url=?,
                    platform_home_url=?, platform_identity_checked_at=?, updated_at=?
                WHERE id=?
                """,
                (
                    str(identity.get("platform_account_id") or "")[:240],
                    str(identity.get("platform_account_name") or "")[:240],
                    str(identity.get("platform_avatar_url") or "")[:1000],
                    str(identity.get("platform_home_url") or "")[:1000],
                    now,
                    now,
                    account_id,
                ),
            )
    return get_social_account(account_id) or {}


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
        "正在创建平台登录会话；如二维码或验证状态无法回传，可使用网页登录窗口人工处理。"
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


def list_login_sessions(limit: int = 20, account_id: int | None = None) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit, 20)
    sql = "SELECT * FROM login_sessions ORDER BY id DESC"
    params: list[Any] = []
    if account_id:
        sql = "SELECT * FROM login_sessions WHERE account_id=? ORDER BY id DESC"
        params.append(account_id)
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def latest_successful_login_session_at(platform: str) -> str:
    _validate_platform(platform)
    try:
        with get_conn() as conn:
            row = conn.execute(
                """
                SELECT updated_at FROM login_sessions
                WHERE platform=? AND status='success'
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (platform,),
            ).fetchone()
    except sqlite3.OperationalError:
        return ""
    return str(row["updated_at"] or "") if row else ""


def expire_login_sessions_for_account(account_id: int | None, platform: str, profile_path: str = "") -> list[int]:
    _validate_platform(platform)
    clauses = ["platform=?", "status IN ('waiting_qrcode', 'waiting_verification', 'waiting_manual_browser', 'scanned')"]
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
    allowed = {"waiting_qrcode", "waiting_verification", "waiting_manual_browser", "scanned", "success", "expired", "failed"}
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
    return row


def _row_to_pool_item(row: dict[str, Any], masked: bool = True) -> dict[str, Any]:
    encrypted = row.pop("cookies_encrypted", "")
    raw_cookies = decrypt_secret(encrypted)
    row["cookies"] = mask_secret(encrypted) if masked else raw_cookies
    row["has_cookies"] = bool(raw_cookies)
    row["is_draft"] = bool(row.get("is_draft"))
    platform = row.get("platform")
    if platform in SUPPORTED_MONITOR_PLATFORMS:
        capability = get_mediacrawler_login_capability(str(platform))
        row["login_capability_source"] = "平台采集服务"
        row["login_boundary"] = capability.get("boundary") or "media_crawler_only"
        row["captcha_policy"] = capability.get("captcha_policy") or "report_only"
        row["login_engine"] = "平台采集服务登录模块"
        row["login_class"] = ""
        row["bridge_role"] = capability.get("bridge_role") or ""
        row["qrcode_capture_method"] = "页面二维码回传"
        row["qrcode_prepare_method"] = "平台登录会话"
        row["qrcode_flow_steps"] = [
            "打开平台登录页",
            "等待二维码或平台验证提示",
            "前端展示二维码、截图或验证状态",
            "运营扫码或按页面提示处理后，系统保存登录状态",
        ]
        row["integration_note"] = "后台只包装平台采集服务已有登录方式；验证码、滑块、短信只回传状态，不自动绕过。"
        row["supported_login_types"] = list(capability.get("supported_login_types") or [])
        row["supported_login_type_labels"] = capability.get("supported_login_type_labels") or {}
        row["unsupported_reason"] = _unsupported_login_reason(str(platform))
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
