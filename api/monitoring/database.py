from __future__ import annotations

import json
import sqlite3
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlite3 import IntegrityError
from typing import Any

from .account_environment import (
    ACCOUNT_PROFILE_ROOT,
    account_profile_environment,
    default_account_profile_key,
    resolve_account_profile_path,
)
from .account_identity import generate_account_identity, validate_account_identity
from .auth import generate_session_token, hash_password, hash_session_token, verify_password
from .mediacrawler_login import LOGIN_TYPE_LABELS, PLATFORM_LOGIN_TYPES, SUPPORTED_MONITOR_PLATFORMS, get_mediacrawler_login_capability
from .login_status import (
    LOGIN_STATE_NEEDS_VERIFICATION,
    LOGIN_STATE_PLATFORM_ERROR,
    LOGIN_STATE_PREPARING,
    LOGIN_STATE_QRCODE_FAILED,
    LOGIN_STATE_SUCCESS,
    LOGIN_STATE_TIMEOUT,
    LOGIN_STATE_WAITING_CONFIRM,
    LOGIN_STATE_WAITING_QRCODE,
    LOGIN_STATE_WAITING_SCAN,
    PENDING_LOGIN_STATES,
    STRUCTURED_LOGIN_STATES,
    normalize_login_state,
)
from .prompts import DEFAULT_PROMPT
from .security import MONITOR_DATA_DIR, customer_safe_text, customer_safe_url, decrypt_secret, encrypt_secret, mask_secret, redact_local_paths, redact_sensitive
from .settings import (
    DEFINITIONS_BY_KEY,
    effective_runtime_settings,
    setting_value_json,
    validate_runtime_setting,
)


DB_PATH = MONITOR_DATA_DIR / "monitor.sqlite"
DEFAULT_WORKSPACE_ID = 1
DEFAULT_WORKSPACE_NAME = "Default Workspace"
DEFAULT_EMAIL_SUBJECT_TEMPLATE = "【律所舆情日报】{law_firm_name} - {date}"
DEFAULT_EMAIL_TEMPLATE_NAME = "标准舆情日报模板"
REPORT_BODY_PLACEHOLDERS = ("{report_html}", "{report_body}")
JOB_TEMPLATE_PLACEHOLDERS = ("请改成", "目标律所", "律所简称", "律师事务所简称")
JOB_TARGET_TYPES = {"search", "detail", "creator"}
JOB_OUTPUT_MODES = {"internal", "json", "excel"}
JOB_BROWSER_MODES = {"server_qrcode", "profile", "local_window"}
USER_ROLES = {"administrator", "normal"}
USER_STATUSES = {"active", "disabled"}
EMAIL_DELIVERY_SEND_TYPES = {"auto", "manual_resend"}
EMAIL_DELIVERY_STATUSES = {"pending", "sending", "sent", "failed", "skipped"}
SESSION_TTL_SECONDS = 8 * 60 * 60
RUN_TERMINAL_STATUSES = {"success", "partial_failed", "failed", "timeout", "cancelled", "interrupted", "skipped", "selftest"}
AI_TRACE_PROMPT_LIMIT = 16 * 1024
AI_TRACE_REQUEST_LIMIT = 24 * 1024
AI_TRACE_RESPONSE_LIMIT = 24 * 1024
AI_TRACE_TOTAL_LIMIT = 64 * 1024
LEAD_STATUS_LABELS = {
    "unrelated": "不相关",
    "no_risk": "已评估无风险",
    "suspected_negative": "疑似负面",
    "high_risk": "高风险",
    "pending_review": "待人工复核",
    "unevaluated": "未评估",
    "limited_context": "上下文有限",
}


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


def lead_status_from_evaluation(
    *,
    eval_status: Any,
    is_related: Any,
    is_negative: Any,
    risk_level: Any,
    evaluation_missing: bool = False,
    run_status: Any = "",
) -> str:
    if evaluation_missing:
        return "limited_context" if str(run_status or "") in RUN_TERMINAL_STATUSES else "unevaluated"
    if str(eval_status or "") == "pending_review":
        return "pending_review"
    related = bool(is_related)
    negative = bool(is_negative)
    if related and negative and str(risk_level or "") == "high":
        return "high_risk"
    if related and negative:
        return "suspected_negative"
    if not related:
        return "unrelated"
    return "no_risk"


def apply_lead_status_fields(item: dict[str, Any]) -> dict[str, Any]:
    evaluation_missing = item.get("evaluation_id") in (None, "")
    run_status = str(item.get("run_status") or "")
    lead_status = lead_status_from_evaluation(
        eval_status=item.get("eval_status"),
        is_related=item.get("is_related"),
        is_negative=item.get("is_negative"),
        risk_level=item.get("risk_level"),
        evaluation_missing=evaluation_missing,
        run_status=run_status,
    )
    item["evaluation_missing"] = bool(evaluation_missing)
    item["limited_context"] = lead_status == "limited_context"
    item["lead_status"] = lead_status
    item["lead_status_label"] = LEAD_STATUS_LABELS.get(lead_status, lead_status)
    if evaluation_missing:
        item["eval_status"] = lead_status
        item["risk_level"] = "unevaluated"
        item["is_related"] = False
        item["is_negative"] = False
        item["reason"] = "AI 评估记录缺失；该内容未被判定为无风险。"
        item["recommended_action"] = "请人工复核或在安全流程中补建待复核记录。"
    return item


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                email TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL DEFAULT '',
                password_hash TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'normal',
                status TEXT NOT NULL DEFAULT 'active',
                last_login_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_active_at TEXT,
                user_agent TEXT NOT NULL DEFAULT '',
                ip_address TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                key TEXT NOT NULL,
                value_json TEXT NOT NULL DEFAULT 'null',
                value_type TEXT NOT NULL DEFAULT 'json',
                is_locked INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'database',
                updated_by INTEGER,
                updated_at TEXT NOT NULL,
                UNIQUE(workspace_id, key)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                user_id INTEGER,
                action_type TEXT NOT NULL,
                resource_type TEXT NOT NULL DEFAULT '',
                resource_id TEXT NOT NULL DEFAULT '',
                details_json TEXT NOT NULL DEFAULT '{}',
                ip_address TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS monitor_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
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
                created_by INTEGER,
                updated_by INTEGER,
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
                workspace_id INTEGER NOT NULL DEFAULT 1,
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
                created_by INTEGER,
                updated_by INTEGER,
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
                workspace_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                subject_template TEXT NOT NULL DEFAULT '【律所舆情日报】{law_firm_name} - {date}',
                html_template TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 0,
                created_by INTEGER,
                updated_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                login_type TEXT NOT NULL DEFAULT 'qrcode',
                cookies_encrypted TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'standby',
                profile_key TEXT NOT NULL DEFAULT '',
                profile_path TEXT NOT NULL DEFAULT '',
                proxy_id INTEGER,
                environment_region TEXT NOT NULL DEFAULT '',
                browser_platform TEXT NOT NULL DEFAULT '',
                identity_template TEXT NOT NULL DEFAULT '',
                fingerprint_seed TEXT NOT NULL DEFAULT '',
                user_agent TEXT NOT NULL DEFAULT '',
                timezone TEXT NOT NULL DEFAULT '',
                locale TEXT NOT NULL DEFAULT '',
                accept_language TEXT NOT NULL DEFAULT '',
                screen_width INTEGER,
                screen_height INTEGER,
                viewport_width INTEGER,
                viewport_height INTEGER,
                device_scale_factor REAL,
                is_mobile INTEGER NOT NULL DEFAULT 0,
                has_touch INTEGER NOT NULL DEFAULT 0,
                identity_generator_name TEXT NOT NULL DEFAULT '',
                identity_generator_version TEXT NOT NULL DEFAULT '',
                identity_environment_version TEXT NOT NULL DEFAULT '',
                proxy_region_snapshot TEXT NOT NULL DEFAULT '',
                browser_environment_locked_at TEXT,
                browser_environment_lock_reason TEXT NOT NULL DEFAULT '',
                requires_relogin INTEGER NOT NULL DEFAULT 0,
                identity_state TEXT NOT NULL DEFAULT 'draft',
                identity_runtime_snapshot_json TEXT NOT NULL DEFAULT '',
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
                locked_by_run_id INTEGER,
                locked_at TEXT,
                lock_expires_at TEXT,
                created_by INTEGER,
                updated_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS proxy_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT 'manual',
                proxy_url_encrypted TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'standby',
                max_concurrency INTEGER NOT NULL DEFAULT 1,
                notes TEXT NOT NULL DEFAULT '',
                last_checked_at TEXT,
                last_error TEXT NOT NULL DEFAULT '',
                created_by INTEGER,
                updated_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                platform TEXT NOT NULL,
                account_id INTEGER,
                status TEXT NOT NULL DEFAULT 'preparing',
                login_url TEXT NOT NULL DEFAULT '',
                qr_image TEXT NOT NULL DEFAULT '',
                profile_key TEXT NOT NULL DEFAULT '',
                profile_path TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL DEFAULT '',
                created_by INTEGER,
                updated_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT
            );

            CREATE TABLE IF NOT EXISTS crawl_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                job_id INTEGER REFERENCES monitor_jobs(id) ON DELETE SET NULL,
                account_id INTEGER,
                proxy_id INTEGER,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                summary TEXT NOT NULL DEFAULT '{}',
                error_message TEXT,
                timeout_seconds INTEGER,
                deadline_at TEXT,
                timeout_reason TEXT,
                visibility TEXT NOT NULL DEFAULT 'visible',
                run_type TEXT NOT NULL DEFAULT 'scheduled',
                archived_at TEXT,
                archived_by INTEGER,
                created_by INTEGER,
                updated_by INTEGER
            );

            CREATE TABLE IF NOT EXISTS raw_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
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
                created_by INTEGER,
                updated_by INTEGER,
                UNIQUE(job_id, platform, content_id)
            );

            CREATE TABLE IF NOT EXISTS raw_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                platform TEXT NOT NULL,
                comment_id TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content TEXT,
                author_name TEXT,
                create_time INTEGER,
                raw_json TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                created_by INTEGER,
                updated_by INTEGER,
                UNIQUE(platform, comment_id)
            );

            CREATE TABLE IF NOT EXISTS ai_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
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
                created_by INTEGER,
                updated_by INTEGER,
                UNIQUE(raw_content_id)
            );

            CREATE TABLE IF NOT EXISTS ai_evaluation_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL,
                run_id INTEGER NOT NULL,
                raw_content_id INTEGER NOT NULL,
                ai_evaluation_id INTEGER,
                attempt_index INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                prompt_snapshot TEXT NOT NULL DEFAULT '',
                input_payload_json TEXT NOT NULL DEFAULT '{}',
                request_snapshot_json TEXT NOT NULL DEFAULT '{}',
                response_snapshot TEXT NOT NULL DEFAULT '',
                parsed_result_json TEXT NOT NULL DEFAULT '{}',
                error_message TEXT NOT NULL DEFAULT '',
                duration_ms INTEGER,
                started_at TEXT,
                finished_at TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                run_id INTEGER NOT NULL REFERENCES crawl_runs(id) ON DELETE CASCADE,
                job_id INTEGER,
                job_snapshot_json TEXT,
                html_path TEXT NOT NULL,
                markdown_path TEXT NOT NULL,
                excel_path TEXT NOT NULL,
                email_status TEXT NOT NULL DEFAULT 'pending',
                email_error TEXT,
                summary TEXT NOT NULL DEFAULT '{}',
                created_by INTEGER,
                updated_by INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS email_delivery_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                job_id INTEGER NOT NULL,
                report_id INTEGER,
                send_window_key TEXT NOT NULL,
                send_type TEXT NOT NULL CHECK(send_type IN ('auto', 'manual_resend')),
                sent_by INTEGER,
                sent_at TEXT,
                status TEXT NOT NULL CHECK(status IN ('pending', 'sending', 'sent', 'failed', 'skipped')),
                error_message TEXT,
                recipients_json TEXT,
                trigger_source TEXT NOT NULL DEFAULT '',
                effective_recipients_json TEXT NOT NULL DEFAULT '[]',
                effective_recipient_source TEXT NOT NULL DEFAULT '',
                email_template_id INTEGER,
                email_template_name TEXT NOT NULL DEFAULT '',
                email_template_source TEXT NOT NULL DEFAULT '',
                email_subject_template TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resource_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                resource_type TEXT NOT NULL,
                resource_id INTEGER NOT NULL,
                run_id INTEGER NOT NULL,
                locked_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                UNIQUE(resource_type, resource_id, run_id)
            );
            """
        )
        now = utc_now()
        conn.execute(
            """
            INSERT OR IGNORE INTO workspaces (id, name, status, created_at, updated_at)
            VALUES (?, ?, 'active', ?, ?)
            """,
            (DEFAULT_WORKSPACE_ID, DEFAULT_WORKSPACE_NAME, now, now),
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
        _ensure_phase_05_schema(conn)
        _ensure_phase_51_account_identity_schema(conn)
        mark_selftest_jobs_internal(conn)
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


def report_job_snapshot(job: dict[str, Any] | None) -> dict[str, Any] | None:
    if not job:
        return None
    job_id = _safe_int(job.get("id") or job.get("job_id"))
    if not job_id:
        return None
    platforms = [customer_safe_text(str(item)) for item in (job.get("platforms") or []) if str(item).strip()]
    keywords = [customer_safe_text(str(item)) for item in (job.get("keywords") or []) if str(item).strip()]
    return {
        "job_id": job_id,
        "law_firm_name": customer_safe_text(job.get("law_firm_name")),
        "platforms": platforms,
        "keywords": keywords,
        "frequency": customer_safe_text(job.get("frequency") or ""),
        "email_template": effective_email_template_provenance(job),
        "deleted_at": job.get("deleted_at") or None,
    }


def report_job_snapshot_json(job: dict[str, Any] | None) -> str | None:
    snapshot = report_job_snapshot(job)
    if not snapshot:
        return None
    return json.dumps(snapshot, ensure_ascii=False)


def _actor_scope_clause(
    actor: dict[str, Any] | None,
    table_alias: str = "",
    owner_column: str = "created_by",
    workspace_column: str = "workspace_id",
) -> tuple[str, list[Any]]:
    if not actor:
        return "", []
    prefix = f"{table_alias}." if table_alias else ""
    workspace_id = _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID
    clauses = [f"{prefix}{workspace_column}=?"]
    params: list[Any] = [workspace_id]
    if actor.get("role") != "administrator":
        clauses.append(f"{prefix}{owner_column}=?")
        params.append(_safe_int(actor.get("id")) or 0)
    return " AND ".join(clauses), params


def user_can_access_job(job: dict[str, Any] | None, actor: dict[str, Any] | None) -> bool:
    if not job or not actor:
        return False
    if (_safe_int(job.get("workspace_id")) or DEFAULT_WORKSPACE_ID) != (_safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID):
        return False
    if actor.get("role") == "administrator":
        return True
    return _safe_int(job.get("created_by")) == (_safe_int(actor.get("id")) or 0)


def list_jobs(include_internal: bool = False, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with get_conn() as conn:
        clauses = []
        params: list[Any] = []
        if not include_internal:
            clauses.append("is_internal=0")
        actor_clause, actor_params = _actor_scope_clause(actor)
        if actor_clause:
            clauses.append(actor_clause)
            params.extend(actor_params)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = conn.execute(f"SELECT * FROM monitor_jobs{where} ORDER BY id DESC", params).fetchall()
        return [row_to_job(conn, row) for row in rows]


def get_job(job_id: int, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_conn() as conn:
        actor_clause, actor_params = _actor_scope_clause(actor)
        where = "id=?"
        params: list[Any] = [job_id]
        if actor_clause:
            where += f" AND {actor_clause}"
            params.extend(actor_params)
        row = conn.execute(f"SELECT * FROM monitor_jobs WHERE {where}", params).fetchone()
        return row_to_job(conn, row) if row else None


def save_job(payload: dict[str, Any], job_id: int | None = None, actor: dict[str, Any] | None = None) -> dict[str, Any]:
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
    workspace_id = (_safe_int((actor or {}).get("workspace_id")) or DEFAULT_WORKSPACE_ID) if actor else DEFAULT_WORKSPACE_ID
    actor_id = _safe_int((actor or {}).get("id")) if actor else None
    with get_conn() as conn:
        if job_id:
            actor_clause, actor_params = _actor_scope_clause(actor)
            exists_sql = "SELECT * FROM monitor_jobs WHERE id=?"
            exists_params: list[Any] = [job_id]
            if actor_clause:
                exists_sql += f" AND {actor_clause}"
                exists_params.extend(actor_params)
            exists = conn.execute(exists_sql, exists_params).fetchone()
            if not exists:
                raise ValueError("job not found")
            conn.execute(
                """
                UPDATE monitor_jobs SET law_firm_name=?, aliases=?, exclude_words=?,
                    enable_comments=?, enable_sub_comments=?, time_window_type=?, custom_start=?, custom_end=?,
                    frequency=?, cron_expr=?, email_time=?, target_type=?, max_pages=?, max_items=?,
                    start_page=?, output_mode=?, browser_mode=?, ai_profile_id=?, email_template_id=?,
                    account_id=?, proxy_id=?, enabled=?, is_internal=?, updated_by=?, updated_at=?
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
                    actor_id,
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
                    workspace_id, law_firm_name, aliases, exclude_words, enable_comments, enable_sub_comments, time_window_type,
                    custom_start, custom_end, frequency, cron_expr, email_time, target_type, max_pages, max_items,
                    start_page, output_mode, browser_mode, ai_profile_id, email_template_id, account_id, proxy_id,
                    enabled, is_internal, created_by, updated_by,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    workspace_id,
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
                    actor_id,
                    actor_id,
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


def _ensure_phase_05_schema(conn: sqlite3.Connection) -> None:
    ownership_tables = [
        "monitor_jobs",
        "social_accounts",
        "proxy_profiles",
        "login_sessions",
        "crawl_runs",
        "raw_contents",
        "raw_comments",
        "ai_evaluations",
        "reports",
        "email_templates",
        "ai_key_profiles",
    ]
    for table in ownership_tables:
        _ensure_column(conn, table, "workspace_id", f"INTEGER NOT NULL DEFAULT {DEFAULT_WORKSPACE_ID}")
        _ensure_column(conn, table, "created_by", "INTEGER")
        _ensure_column(conn, table, "updated_by", "INTEGER")

    _ensure_column(conn, "social_accounts", "profile_key", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "social_accounts", "locked_by_run_id", "INTEGER")
    _ensure_column(conn, "social_accounts", "locked_at", "TEXT")
    _ensure_column(conn, "social_accounts", "lock_expires_at", "TEXT")
    _ensure_column(conn, "login_sessions", "profile_key", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "crawl_runs", "account_id", "INTEGER")
    _ensure_column(conn, "crawl_runs", "proxy_id", "INTEGER")
    _ensure_column(conn, "crawl_runs", "timeout_seconds", "INTEGER")
    _ensure_column(conn, "crawl_runs", "deadline_at", "TEXT")
    _ensure_column(conn, "crawl_runs", "timeout_reason", "TEXT")
    _ensure_phase_14_run_center_schema(conn)
    _ensure_phase_16_email_delivery_schema(conn)
    _ensure_phase_18_report_snapshot_schema(conn)
    _ensure_phase_20_ai_trace_schema(conn)
    _backfill_social_account_profile_keys(conn)
    _backfill_login_session_profile_keys(conn)

    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_users_workspace_role_status
            ON users(workspace_id, role, status);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_token_status
            ON user_sessions(session_token_hash, status);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_user_status
            ON user_sessions(user_id, status);
        CREATE INDEX IF NOT EXISTS idx_system_settings_workspace_key
            ON system_settings(workspace_id, key);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace_created
            ON audit_logs(workspace_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_account_lock_status
            ON social_accounts(locked_by_run_id, lock_expires_at);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_resource_locks_unique
            ON resource_locks(resource_type, resource_id, run_id);
        CREATE INDEX IF NOT EXISTS idx_resource_lock_lookup
            ON resource_locks(resource_type, resource_id, expires_at);
        CREATE INDEX IF NOT EXISTS idx_resource_lock_cleanup
            ON resource_locks(expires_at);
        """
    )


def _ensure_phase_51_account_identity_schema(conn: sqlite3.Connection) -> None:
    columns = (
        ("environment_region", "TEXT NOT NULL DEFAULT ''"),
        ("browser_platform", "TEXT NOT NULL DEFAULT ''"),
        ("identity_template", "TEXT NOT NULL DEFAULT ''"),
        ("fingerprint_seed", "TEXT NOT NULL DEFAULT ''"),
        ("user_agent", "TEXT NOT NULL DEFAULT ''"),
        ("timezone", "TEXT NOT NULL DEFAULT ''"),
        ("locale", "TEXT NOT NULL DEFAULT ''"),
        ("accept_language", "TEXT NOT NULL DEFAULT ''"),
        ("screen_width", "INTEGER"),
        ("screen_height", "INTEGER"),
        ("viewport_width", "INTEGER"),
        ("viewport_height", "INTEGER"),
        ("device_scale_factor", "REAL"),
        ("is_mobile", "INTEGER NOT NULL DEFAULT 0"),
        ("has_touch", "INTEGER NOT NULL DEFAULT 0"),
        ("identity_generator_name", "TEXT NOT NULL DEFAULT ''"),
        ("identity_generator_version", "TEXT NOT NULL DEFAULT ''"),
        ("identity_environment_version", "TEXT NOT NULL DEFAULT ''"),
        ("proxy_region_snapshot", "TEXT NOT NULL DEFAULT ''"),
        ("browser_environment_locked_at", "TEXT"),
        ("browser_environment_lock_reason", "TEXT NOT NULL DEFAULT ''"),
        ("requires_relogin", "INTEGER NOT NULL DEFAULT 0"),
        ("identity_state", "TEXT NOT NULL DEFAULT 'draft'"),
        ("identity_runtime_snapshot_json", "TEXT NOT NULL DEFAULT ''"),
    )
    for column, definition in columns:
        _ensure_column(conn, "social_accounts", column, definition)
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_social_accounts_identity_state
            ON social_accounts(workspace_id, identity_state);
        CREATE INDEX IF NOT EXISTS idx_social_accounts_requires_relogin
            ON social_accounts(workspace_id, requires_relogin);
        CREATE INDEX IF NOT EXISTS idx_social_accounts_identity_template
            ON social_accounts(workspace_id, identity_template);
        """
    )


def _ensure_phase_14_run_center_schema(conn: sqlite3.Connection) -> None:
    _ensure_column(conn, "crawl_runs", "visibility", "TEXT NOT NULL DEFAULT 'visible'")
    _ensure_column(conn, "crawl_runs", "run_type", "TEXT NOT NULL DEFAULT 'scheduled'")
    _ensure_column(conn, "crawl_runs", "archived_at", "TEXT")
    _ensure_column(conn, "crawl_runs", "archived_by", "INTEGER")
    conn.execute("UPDATE crawl_runs SET visibility='visible' WHERE COALESCE(visibility, '') = ''")
    conn.execute("UPDATE crawl_runs SET run_type='scheduled' WHERE COALESCE(run_type, '') = ''")
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_crawl_runs_visibility
            ON crawl_runs(workspace_id, visibility, started_at);
        CREATE INDEX IF NOT EXISTS idx_crawl_runs_type_status
            ON crawl_runs(workspace_id, run_type, status);
        """
    )


def _ensure_phase_16_email_delivery_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS email_delivery_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER NOT NULL DEFAULT 1,
            job_id INTEGER NOT NULL,
            report_id INTEGER,
            send_window_key TEXT NOT NULL,
            send_type TEXT NOT NULL DEFAULT 'auto',
            sent_by INTEGER,
            sent_at TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            error_message TEXT,
            recipients_json TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    _ensure_column(conn, "email_delivery_logs", "workspace_id", f"INTEGER NOT NULL DEFAULT {DEFAULT_WORKSPACE_ID}")
    _ensure_column(conn, "email_delivery_logs", "job_id", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(conn, "email_delivery_logs", "report_id", "INTEGER")
    _ensure_column(conn, "email_delivery_logs", "send_window_key", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "send_type", "TEXT NOT NULL DEFAULT 'auto'")
    _ensure_column(conn, "email_delivery_logs", "sent_by", "INTEGER")
    _ensure_column(conn, "email_delivery_logs", "sent_at", "TEXT")
    _ensure_column(conn, "email_delivery_logs", "status", "TEXT NOT NULL DEFAULT 'pending'")
    _ensure_column(conn, "email_delivery_logs", "error_message", "TEXT")
    _ensure_column(conn, "email_delivery_logs", "recipients_json", "TEXT")
    _ensure_column(conn, "email_delivery_logs", "trigger_source", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "effective_recipients_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "email_delivery_logs", "effective_recipient_source", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "email_template_id", "INTEGER")
    _ensure_column(conn, "email_delivery_logs", "email_template_name", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "email_template_source", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "email_subject_template", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "email_delivery_logs", "created_at", "TEXT NOT NULL DEFAULT ''")
    now = utc_now()
    conn.execute(
        "UPDATE email_delivery_logs SET workspace_id=? WHERE COALESCE(workspace_id, 0) = 0",
        (DEFAULT_WORKSPACE_ID,),
    )
    conn.execute("UPDATE email_delivery_logs SET send_type='auto' WHERE send_type NOT IN ('auto', 'manual_resend')")
    conn.execute(
        "UPDATE email_delivery_logs SET status='pending' WHERE status NOT IN ('pending', 'sending', 'sent', 'failed', 'skipped')"
    )
    conn.execute("UPDATE email_delivery_logs SET recipients_json='[]' WHERE recipients_json IS NULL")
    conn.execute("UPDATE email_delivery_logs SET trigger_source=CASE send_type WHEN 'manual_resend' THEN 'manual_resend' ELSE 'scheduler_auto' END WHERE COALESCE(trigger_source, '') = ''")
    conn.execute("UPDATE email_delivery_logs SET effective_recipients_json='[]' WHERE COALESCE(effective_recipients_json, '') = ''")
    conn.execute("UPDATE email_delivery_logs SET effective_recipient_source='limited_context' WHERE COALESCE(effective_recipient_source, '') = ''")
    conn.execute("UPDATE email_delivery_logs SET email_template_name='' WHERE email_template_name IS NULL")
    conn.execute("UPDATE email_delivery_logs SET email_template_source='' WHERE email_template_source IS NULL")
    conn.execute("UPDATE email_delivery_logs SET email_subject_template='' WHERE email_subject_template IS NULL")
    conn.execute("UPDATE email_delivery_logs SET created_at=? WHERE COALESCE(created_at, '') = ''", (now,))
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_email_delivery_job_window
            ON email_delivery_logs(workspace_id, job_id, send_window_key);
        CREATE INDEX IF NOT EXISTS idx_email_delivery_report
            ON email_delivery_logs(workspace_id, report_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_email_delivery_status
            ON email_delivery_logs(workspace_id, status, created_at);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_email_delivery_auto_window_unique
            ON email_delivery_logs(workspace_id, job_id, send_window_key, send_type)
            WHERE send_type='auto' AND status IN ('pending', 'sending', 'sent');
        """
    )


def _ensure_phase_18_report_snapshot_schema(conn: sqlite3.Connection) -> None:
    _ensure_column(conn, "reports", "job_snapshot_json", "TEXT")
    rows = conn.execute(
        """
        SELECT reports.id AS report_id, monitor_jobs.*
        FROM reports
        JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
        WHERE COALESCE(reports.job_snapshot_json, '') = ''
        """
    ).fetchall()
    for row in rows:
        job = row_to_job(conn, row)
        conn.execute(
            "UPDATE reports SET job_snapshot_json=? WHERE id=?",
            (report_job_snapshot_json(job), row["report_id"]),
        )


def _ensure_phase_20_ai_trace_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_evaluation_traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id INTEGER NOT NULL,
            run_id INTEGER NOT NULL,
            raw_content_id INTEGER NOT NULL,
            ai_evaluation_id INTEGER,
            attempt_index INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL,
            provider TEXT NOT NULL DEFAULT '',
            model TEXT NOT NULL DEFAULT '',
            prompt_snapshot TEXT NOT NULL DEFAULT '',
            input_payload_json TEXT NOT NULL DEFAULT '{}',
            request_snapshot_json TEXT NOT NULL DEFAULT '{}',
            response_snapshot TEXT NOT NULL DEFAULT '',
            parsed_result_json TEXT NOT NULL DEFAULT '{}',
            error_message TEXT NOT NULL DEFAULT '',
            duration_ms INTEGER,
            started_at TEXT,
            finished_at TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_ai_traces_run_content
            ON ai_evaluation_traces(workspace_id, run_id, raw_content_id);
        CREATE INDEX IF NOT EXISTS idx_ai_traces_evaluation
            ON ai_evaluation_traces(workspace_id, ai_evaluation_id);
        CREATE INDEX IF NOT EXISTS idx_ai_traces_status_created
            ON ai_evaluation_traces(workspace_id, status, created_at);
        """
    )


def _backfill_social_account_profile_keys(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT id, workspace_id, platform FROM social_accounts
        WHERE COALESCE(profile_key, '') = ''
        """
    ).fetchall()
    for row in rows:
        conn.execute(
            "UPDATE social_accounts SET profile_key=? WHERE id=?",
            (
                _default_account_profile_key(
                    _safe_int(row["workspace_id"]) or DEFAULT_WORKSPACE_ID,
                    str(row["platform"] or ""),
                    int(row["id"]),
                ),
                row["id"],
            ),
        )


def _backfill_login_session_profile_keys(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT s.id AS session_id, a.profile_key AS account_profile_key
        FROM login_sessions s
        JOIN social_accounts a ON a.id = s.account_id
        WHERE COALESCE(s.profile_key, '') = ''
          AND COALESCE(a.profile_key, '') <> ''
        """
    ).fetchall()
    for row in rows:
        conn.execute(
            "UPDATE login_sessions SET profile_key=? WHERE id=?",
            (row["account_profile_key"], row["session_id"]),
        )


def bootstrap_admin_from_env(email: str | None, password: str | None, display_name: str | None = None) -> dict[str, Any] | None:
    normalized_email = _normalize_email(email)
    if not normalized_email or not password:
        return None
    now = utc_now()
    with get_conn() as conn:
        existing_admin = conn.execute(
            "SELECT * FROM users WHERE role='administrator' AND status='active' ORDER BY id LIMIT 1"
        ).fetchone()
        if existing_admin:
            return _row_to_user(dict(existing_admin))
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (normalized_email,)).fetchone()
        if row:
            conn.execute(
                """
                UPDATE users SET password_hash=?, role='administrator', status='active',
                    display_name=COALESCE(NULLIF(?, ''), display_name), updated_at=?
                WHERE id=?
                """,
                (hash_password(password), display_name or "", now, row["id"]),
            )
            target_id = int(row["id"])
        else:
            cur = conn.execute(
                """
                INSERT INTO users (workspace_id, email, display_name, password_hash, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'administrator', 'active', ?, ?)
                """,
                (DEFAULT_WORKSPACE_ID, normalized_email, display_name or normalized_email, hash_password(password), now, now),
            )
            target_id = int(cur.lastrowid)
        _record_audit_log(conn, DEFAULT_WORKSPACE_ID, target_id, "bootstrap_admin", "user", str(target_id), {})
    return get_user(target_id)


def has_active_administrator() -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE role='administrator' AND status='active' LIMIT 1").fetchone()
    return bool(row)


def list_users() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY role, id").fetchall()
    return [_row_to_user(dict(row)) for row in rows]


def get_user(user_id: int | None) -> dict[str, Any] | None:
    if not user_id:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return _row_to_user(dict(row)) if row else None


def get_user_by_email(email: str | None) -> dict[str, Any] | None:
    normalized = _normalize_email(email)
    if not normalized:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (normalized,)).fetchone()
    return _row_to_user(dict(row)) if row else None


def save_user(payload: dict[str, Any], user_id: int | None = None, actor_id: int | None = None) -> dict[str, Any]:
    password = str(payload.get("password") or "")
    now = utc_now()
    with get_conn() as conn:
        if user_id:
            current = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not current:
                raise ValueError("user not found")
            email = _normalize_email(payload.get("email") or current["email"])
            role = _validate_user_role(payload.get("role") or current["role"])
            status = _validate_user_status(payload.get("status") or current["status"])
            display_name = str(payload.get("display_name") or current["display_name"] or email).strip()
            duplicate = conn.execute("SELECT id FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
            if duplicate and int(duplicate["id"]) != int(user_id):
                raise ValueError("email already exists")
            assignments = [
                "email=?",
                "display_name=?",
                "role=?",
                "status=?",
                "updated_at=?",
            ]
            values: list[Any] = [email, display_name, role, status, now]
            if password:
                assignments.append("password_hash=?")
                values.append(hash_password(password))
            values.append(user_id)
            conn.execute(f"UPDATE users SET {', '.join(assignments)} WHERE id=?", values)
            target_id = int(user_id)
            action = "update_user"
        else:
            email = _normalize_email(payload.get("email"))
            if not email:
                raise ValueError("email is required")
            role = _validate_user_role(payload.get("role") or "normal")
            status = _validate_user_status(payload.get("status") or "active")
            display_name = str(payload.get("display_name") or email).strip()
            duplicate = conn.execute("SELECT id FROM users WHERE lower(email)=lower(?)", (email,)).fetchone()
            if duplicate:
                raise ValueError("email already exists")
            if not password:
                raise ValueError("password is required")
            cur = conn.execute(
                """
                INSERT INTO users (workspace_id, email, display_name, password_hash, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (DEFAULT_WORKSPACE_ID, email, display_name, hash_password(password), role, status, now, now),
            )
            target_id = int(cur.lastrowid)
            action = "create_user"
        _record_audit_log(conn, DEFAULT_WORKSPACE_ID, actor_id, action, "user", str(target_id), {"role": role, "status": status})
    return get_user(target_id) or {}


def authenticate_user(email: str | None, password: str | None) -> dict[str, Any] | None:
    normalized = _normalize_email(email)
    if not normalized or not password:
        return None
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email)=lower(?)", (normalized,)).fetchone()
        if not row or row["status"] != "active":
            return None
        if not verify_password(str(password), str(row["password_hash"] or "")):
            return None
        now = utc_now()
        conn.execute("UPDATE users SET last_login_at=?, updated_at=? WHERE id=?", (now, now, row["id"]))
        refreshed = conn.execute("SELECT * FROM users WHERE id=?", (row["id"],)).fetchone()
    return _row_to_user(dict(refreshed)) if refreshed else None


def create_user_session(
    user_id: int,
    user_agent: str = "",
    ip_address: str = "",
    ttl_seconds: int = SESSION_TTL_SECONDS,
) -> tuple[str, dict[str, Any]]:
    token = generate_session_token()
    now_dt = datetime.now(timezone.utc)
    now = now_dt.isoformat()
    expires_at = (now_dt + timedelta(seconds=ttl_seconds)).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO user_sessions (
                user_id, session_token_hash, status, created_at, expires_at,
                last_active_at, user_agent, ip_address
            ) VALUES (?, ?, 'active', ?, ?, ?, ?, ?)
            """,
            (user_id, hash_session_token(token), now, expires_at, now, user_agent[:500], ip_address[:120]),
        )
        session_id = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM user_sessions WHERE id=?", (session_id,)).fetchone()
    return token, dict(row)


def get_user_for_session_token(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    token_hash = hash_session_token(token)
    now_dt = datetime.now(timezone.utc)
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT s.id AS session_id, s.expires_at, s.status AS session_status, u.*
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_token_hash=?
            """,
            (token_hash,),
        ).fetchone()
        if not row:
            return None
        expires_at = _parse_iso_datetime(row["expires_at"])
        if row["session_status"] != "active" or not expires_at or expires_at <= now_dt:
            conn.execute("UPDATE user_sessions SET status='expired' WHERE id=?", (row["session_id"],))
            return None
        if row["status"] != "active":
            return None
        now = now_dt.isoformat()
        conn.execute("UPDATE user_sessions SET last_active_at=? WHERE id=?", (now, row["session_id"]))
        result = _row_to_user(dict(row))
        result["session_id"] = int(row["session_id"])
    return result


def invalidate_user_session(token: str | None) -> None:
    if not token:
        return
    with get_conn() as conn:
        conn.execute("UPDATE user_sessions SET status='expired' WHERE session_token_hash=?", (hash_session_token(token),))


def record_audit_log(
    action_type: str,
    resource_type: str,
    resource_id: str | int,
    details: dict[str, Any] | None = None,
    user_id: int | None = None,
    workspace_id: int = DEFAULT_WORKSPACE_ID,
    ip_address: str = "",
) -> None:
    with get_conn() as conn:
        _record_audit_log(
            conn,
            workspace_id,
            user_id,
            action_type,
            resource_type,
            str(resource_id),
            details or {},
            ip_address=ip_address,
        )


def list_audit_logs(limit: int = 100) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit, 100)
    sql = "SELECT * FROM audit_logs ORDER BY id DESC"
    params: list[Any] = []
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def list_runtime_settings() -> dict[str, dict[str, Any]]:
    db_values: dict[str, Any] = {}
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT key, value_json FROM system_settings WHERE workspace_id=?",
            (DEFAULT_WORKSPACE_ID,),
        ).fetchall()
    for row in rows:
        key = str(row["key"] or "")
        if key not in DEFINITIONS_BY_KEY:
            continue
        db_values[key] = _json_loads(row["value_json"], DEFINITIONS_BY_KEY[key].default)
    return effective_runtime_settings(db_values=db_values)


def get_runtime_setting_value(key: str) -> Any:
    settings = list_runtime_settings()
    if key not in settings:
        raise ValueError(f"unknown runtime setting: {key}")
    return settings[key]["value"]


def save_ai_evaluation_trace(trace: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(trace, dict):
        trace = {}
    prepared = _prepare_ai_trace_for_storage(trace)
    now = utc_now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO ai_evaluation_traces (
                workspace_id, run_id, raw_content_id, ai_evaluation_id,
                attempt_index, status, provider, model, prompt_snapshot,
                input_payload_json, request_snapshot_json, response_snapshot,
                parsed_result_json, error_message, duration_ms, started_at,
                finished_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prepared["workspace_id"],
                prepared["run_id"],
                prepared["raw_content_id"],
                prepared.get("ai_evaluation_id"),
                prepared["attempt_index"],
                prepared["status"],
                prepared["provider"],
                prepared["model"],
                prepared["prompt_snapshot"],
                prepared["input_payload_json"],
                prepared["request_snapshot_json"],
                prepared["response_snapshot"],
                prepared["parsed_result_json"],
                prepared["error_message"],
                prepared.get("duration_ms"),
                prepared.get("started_at") or None,
                prepared.get("finished_at") or None,
                now,
            ),
        )
        trace_id = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM ai_evaluation_traces WHERE id=?", (trace_id,)).fetchone()
    return _hydrate_ai_trace_row(row)


def get_ai_evaluation_trace(ai_evaluation_id: int | None = None, raw_content_id: int | None = None, run_id: int | None = None) -> dict[str, Any] | None:
    clauses: list[str] = []
    params: list[Any] = []
    if ai_evaluation_id:
        clauses.append("ai_evaluation_id=?")
        params.append(int(ai_evaluation_id))
    if raw_content_id:
        clauses.append("raw_content_id=?")
        params.append(int(raw_content_id))
    if run_id:
        clauses.append("run_id=?")
        params.append(int(run_id))
    if not clauses:
        return None
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM ai_evaluation_traces WHERE {' AND '.join(clauses)} ORDER BY id DESC LIMIT 1",
            params,
        ).fetchone()
    return _hydrate_ai_trace_row(row) if row else None


def ai_evaluation_trace_state(ai_evaluation_id: int | None = None, raw_content_id: int | None = None, run_id: int | None = None) -> dict[str, Any]:
    trace = get_ai_evaluation_trace(ai_evaluation_id=ai_evaluation_id, raw_content_id=raw_content_id, run_id=run_id)
    if trace:
        return {"status": "available", "limited_context": False, "trace_id": trace["id"], "message": ""}
    return {
        "status": "limited_context",
        "limited_context": True,
        "trace_id": None,
        "message": "历史记录未保存完整入参/出参。",
    }


def role_safe_ai_trace_view(trace: dict[str, Any] | None, *, admin: bool = False) -> dict[str, Any]:
    if not trace:
        return {
            "status": "limited_context",
            "limited_context": True,
            "message": "历史记录未保存完整入参/出参。",
        }
    business_input = _business_safe_ai_input(trace.get("input_payload"))
    structured_output = _business_safe_ai_output(trace.get("parsed_result"))
    result = {
        "status": "available",
        "limited_context": False,
        "trace_id": trace.get("id"),
        "business_input": business_input,
        "structured_output": structured_output,
        "provider": customer_safe_text(trace.get("provider")),
        "model": customer_safe_text(trace.get("model")),
        "duration_ms": trace.get("duration_ms"),
        "started_at": customer_safe_text(trace.get("started_at")),
        "finished_at": customer_safe_text(trace.get("finished_at")),
        "created_at": customer_safe_text(trace.get("created_at")),
        "error_message": customer_safe_text(trace.get("error_message")),
    }
    if admin:
        result["debug"] = {
            "prompt_snapshot": customer_safe_text(trace.get("prompt_snapshot")),
            "request_snapshot": _trace_safe_api_payload(trace.get("request_snapshot") or {}),
            "response_snapshot": customer_safe_text(trace.get("response_snapshot")),
            "parsed_result": _trace_safe_api_payload(trace.get("parsed_result") or {}),
        }
    return result


def cleanup_ai_evaluation_traces(retention_days: int | None = None, now: datetime | None = None) -> dict[str, Any]:
    try:
        days = int(retention_days if retention_days is not None else get_runtime_setting_value("ai_trace_retention_days"))
    except Exception:
        days = 30
    days = max(1, min(days, 3650))
    now_dt = now.astimezone(timezone.utc) if now and now.tzinfo else (now.replace(tzinfo=timezone.utc) if now else datetime.now(timezone.utc))
    cutoff = (now_dt - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM ai_evaluation_traces WHERE created_at < ?", (cutoff,))
        deleted = int(cur.rowcount or 0)
    return {"deleted": deleted, "retention_days": days, "cutoff": cutoff}


def _prepare_ai_trace_for_storage(trace: dict[str, Any]) -> dict[str, Any]:
    parsed_result = trace.get("parsed_result")
    if parsed_result is None and trace.get("structured_output") is not None:
        parsed_result = trace.get("structured_output")
    input_json, input_truncated = _trace_json_text(trace.get("input_payload") or trace.get("input_payload_json") or {}, AI_TRACE_REQUEST_LIMIT)
    request_json, request_truncated = _trace_json_text(trace.get("request_snapshot") or trace.get("request_snapshot_json") or {}, AI_TRACE_REQUEST_LIMIT)
    parsed_json, parsed_truncated = _trace_json_text(parsed_result or {}, AI_TRACE_REQUEST_LIMIT)
    prompt, prompt_truncated = _trace_text(trace.get("prompt_snapshot") or trace.get("prompt") or "", AI_TRACE_PROMPT_LIMIT)
    response, response_truncated = _trace_text(trace.get("response_snapshot") or trace.get("raw_response") or "", AI_TRACE_RESPONSE_LIMIT)
    error_message, error_truncated = _trace_text(trace.get("error_message") or trace.get("fallback_reason") or "", 4096)
    truncated_fields = {
        key
        for key, truncated in {
            "input_payload_json": input_truncated,
            "request_snapshot_json": request_truncated,
            "parsed_result_json": parsed_truncated,
            "prompt_snapshot": prompt_truncated,
            "response_snapshot": response_truncated,
            "error_message": error_truncated,
        }.items()
        if truncated
    }
    prepared = {
        "workspace_id": _safe_int(trace.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
        "run_id": _safe_int(trace.get("run_id")) or 0,
        "raw_content_id": _safe_int(trace.get("raw_content_id")) or 0,
        "ai_evaluation_id": _safe_int(trace.get("ai_evaluation_id")) or None,
        "attempt_index": max(1, _safe_int(trace.get("attempt_index")) or 1),
        "status": customer_safe_text(str(trace.get("status") or "pending_review"))[:80],
        "provider": customer_safe_text(str(trace.get("provider") or ""))[:80],
        "model": customer_safe_text(str(trace.get("model") or ""))[:160],
        "prompt_snapshot": prompt,
        "input_payload_json": input_json,
        "request_snapshot_json": request_json,
        "response_snapshot": response,
        "parsed_result_json": _merge_trace_meta(parsed_json, truncated_fields),
        "error_message": error_message,
        "duration_ms": _safe_int(trace.get("duration_ms")) if trace.get("duration_ms") not in (None, "") else None,
        "started_at": customer_safe_text(trace.get("started_at")),
        "finished_at": customer_safe_text(trace.get("finished_at")),
    }
    _enforce_trace_total_limit(prepared)
    return prepared


def _trace_json_text(value: Any, limit: int) -> tuple[str, bool]:
    cleaned = _redact_ai_trace_payload(value)
    text = json.dumps(cleaned, ensure_ascii=False)
    if len(text.encode("utf-8")) <= limit:
        return text, bool(isinstance(cleaned, dict) and cleaned.get("truncated"))
    preview, _ = _truncate_utf8(text, max(256, limit - 256), marker="")
    compact = {"truncated": True, "preview": preview}
    text = json.dumps(compact, ensure_ascii=False)
    if len(text.encode("utf-8")) > limit:
        preview, _ = _truncate_utf8(preview, max(32, limit - 128), marker="")
        text = json.dumps({"truncated": True, "preview": preview}, ensure_ascii=False)
    return text, True


def _trace_text(value: Any, limit: int) -> tuple[str, bool]:
    text = _redact_trace_text(str(value or ""))
    return _truncate_utf8(text, limit, marker="\n[truncated=true]")


def _truncate_utf8(text: str, limit: int, *, marker: str) -> tuple[str, bool]:
    raw = str(text or "")
    encoded = raw.encode("utf-8")
    if len(encoded) <= limit:
        return raw, False
    marker_bytes = marker.encode("utf-8")
    allowed = max(0, limit - len(marker_bytes))
    return encoded[:allowed].decode("utf-8", errors="ignore") + marker, True


def _redact_ai_trace_payload(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        truncated = bool(value.get("truncated"))
        for key, item in value.items():
            lower_key = str(key).lower()
            if _is_sensitive_trace_key(lower_key):
                result[key] = "[REDACTED]"
            elif lower_key in {"comments", "comment_samples"} and isinstance(item, list):
                result[key], field_truncated = _redact_trace_comments(item)
                truncated = truncated or field_truncated
            else:
                result[key] = _redact_ai_trace_payload(item)
        if truncated:
            result["truncated"] = True
        return result
    if isinstance(value, list):
        return [_redact_ai_trace_payload(item) for item in value]
    if isinstance(value, str):
        return _redact_trace_text(value)
    return value


def _redact_trace_comments(items: list[Any]) -> tuple[list[Any], bool]:
    result = []
    truncated = len(items) > 20
    for item in items[:20]:
        if isinstance(item, dict):
            cleaned = dict(_redact_ai_trace_payload(item))
            content = str(cleaned.get("content") or cleaned.get("text") or "")
            if content:
                cleaned["content"], was_truncated = _truncate_utf8(content, 500, marker="[truncated=true]")
                truncated = truncated or was_truncated
            result.append(cleaned)
        else:
            text, was_truncated = _truncate_utf8(_redact_trace_text(str(item or "")), 500, marker="[truncated=true]")
            truncated = truncated or was_truncated
            result.append(text)
    return result, truncated


def _is_sensitive_trace_key(key: str) -> bool:
    sensitive_fragments = (
        "authorization",
        "x-api-key",
        "api_key",
        "apikey",
        "cookie",
        "password",
        "smtp_password",
        "token",
        "secret",
        "proxy_url",
        "proxy_password",
        "cookies_encrypted",
        "api_key_encrypted",
        "password_encrypted",
        "profile_path",
        "profile_dir",
        "server_path",
        "local_path",
    )
    if key == "path" or key.endswith("_path"):
        return True
    return any(fragment in key for fragment in sensitive_fragments)


def _redact_trace_text(value: str) -> str:
    text = redact_sensitive(value)
    text = re.sub(
        r"(?i)([\"']?(?:authorization|x-api-key|api[_-]?key|cookie|password|smtp[_-]?password|token|secret|proxy[_-]?url)[\"']?\s*:\s*)[\"'][^\"']*[\"']",
        r"\1\"[REDACTED]\"",
        text,
    )
    text = redact_local_paths(text)
    text = re.sub(r"(?<!:)//+", "/", text)
    return text


def _merge_trace_meta(parsed_json: str, truncated_fields: set[str]) -> str:
    if not truncated_fields:
        return parsed_json
    parsed = _json_loads(parsed_json, {})
    if not isinstance(parsed, dict):
        parsed = {"value": parsed}
    parsed["_trace_meta"] = {
        "truncated": True,
        "truncated_fields": sorted(truncated_fields),
    }
    return json.dumps(_redact_ai_trace_payload(parsed), ensure_ascii=False)


def _enforce_trace_total_limit(prepared: dict[str, Any]) -> None:
    keys = (
        "prompt_snapshot",
        "input_payload_json",
        "request_snapshot_json",
        "response_snapshot",
        "parsed_result_json",
        "error_message",
    )
    total = sum(len(str(prepared.get(key) or "").encode("utf-8")) for key in keys)
    if total <= AI_TRACE_TOTAL_LIMIT:
        return
    overflow = total - AI_TRACE_TOTAL_LIMIT
    response = str(prepared.get("response_snapshot") or "")
    response_bytes = len(response.encode("utf-8"))
    if response_bytes > 1024:
        next_limit = max(1024, response_bytes - overflow - 64)
        prepared["response_snapshot"], _ = _truncate_utf8(response, next_limit, marker="\n[truncated=true]")
    total = sum(len(str(prepared.get(key) or "").encode("utf-8")) for key in keys)
    if total > AI_TRACE_TOTAL_LIMIT:
        parsed_meta = _json_loads(prepared.get("parsed_result_json"), {})
        if not isinstance(parsed_meta, dict):
            parsed_meta = {"value": parsed_meta}
        parsed_meta["_trace_meta"] = {
            **(parsed_meta.get("_trace_meta") if isinstance(parsed_meta.get("_trace_meta"), dict) else {}),
            "truncated": True,
            "total_limit_applied": True,
        }
        prepared["parsed_result_json"] = json.dumps(parsed_meta, ensure_ascii=False)


def _hydrate_ai_trace_row(row: sqlite3.Row | None) -> dict[str, Any]:
    if row is None:
        return {}
    item = dict(row)
    item["input_payload"] = _json_loads(item.get("input_payload_json"), {})
    item["request_snapshot"] = _json_loads(item.get("request_snapshot_json"), {})
    item["parsed_result"] = _json_loads(item.get("parsed_result_json"), {})
    item["prompt_snapshot"] = customer_safe_text(item.get("prompt_snapshot"))
    item["response_snapshot"] = customer_safe_text(item.get("response_snapshot"))
    item["error_message"] = customer_safe_text(item.get("error_message"))
    item["limited_context"] = False
    return item


def _business_safe_ai_input(payload: Any) -> dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    allowed = (
        "law_firm_name",
        "aliases",
        "exclude_words",
        "platform",
        "platform_code",
        "source_keyword",
        "title",
        "description",
        "author_name",
        "content_url",
        "cover_url",
        "publish_time",
        "comment_count",
        "comment_summary",
        "comments",
        "comment_samples",
    )
    result = {key: _trace_safe_api_payload(payload.get(key)) for key in allowed if key in payload}
    if "comment_samples" in result and isinstance(result["comment_samples"], list):
        result["comment_samples"] = result["comment_samples"][:20]
    if "comments" in result and isinstance(result["comments"], list):
        result["comments"] = [_trace_safe_text(item)[:500] for item in result["comments"][:20]]
    return result


def _business_safe_ai_output(payload: Any) -> dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    allowed = (
        "status",
        "is_related",
        "is_negative",
        "risk_level",
        "reason",
        "evidence_quotes",
        "recommended_action",
        "_trace_meta",
    )
    result = {key: _trace_safe_api_payload(payload.get(key)) for key in allowed if key in payload}
    if "evidence_quotes" in result and isinstance(result["evidence_quotes"], list):
        result["evidence_quotes"] = [_trace_safe_text(item) for item in result["evidence_quotes"][:20]]
    return result


EMAIL_VALIDATION_WINDOW_KEY = "__email_validation_window__"
EMAIL_VALIDATION_MAX_TTL_SECONDS = 15 * 60


def get_email_validation_window_state() -> dict[str, Any]:
    payload: dict[str, Any] = {}
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value_json FROM system_settings WHERE workspace_id=? AND key=?",
            (DEFAULT_WORKSPACE_ID, EMAIL_VALIDATION_WINDOW_KEY),
        ).fetchone()
        if row:
            payload = _json_loads(row["value_json"], {})
            if not isinstance(payload, dict):
                payload = {}
    return _email_validation_window_state_from_payload(payload)


def open_email_validation_window(
    *,
    actor_id: int,
    ttl_seconds: int = 300,
    single_use: bool = True,
    reason: str = "",
) -> dict[str, Any]:
    ttl = max(60, min(int(ttl_seconds or 300), EMAIL_VALIDATION_MAX_TTL_SECONDS))
    now_dt = datetime.now(timezone.utc)
    payload = {
        "opened": True,
        "opened_by": int(actor_id),
        "opened_at": now_dt.isoformat(),
        "expires_at": (now_dt + timedelta(seconds=ttl)).isoformat(),
        "ttl_seconds": ttl,
        "single_use": bool(single_use),
        "used": False,
        "last_delivery_log_id": None,
        "disable_reason": "",
        "reason": customer_safe_text(reason),
    }
    with get_conn() as conn:
        _upsert_email_validation_window(conn, payload, actor_id)
        _record_audit_log(
            conn,
            DEFAULT_WORKSPACE_ID,
            actor_id,
            "open_email_validation_window",
            "email_validation_window",
            "current",
            {
                "status": "open",
                "ttl_seconds": ttl,
                "single_use": bool(single_use),
                "reason": reason,
            },
        )
    return _email_validation_window_state_from_payload(payload)


def close_email_validation_window(*, actor_id: int | None = None, reason: str = "manual_close") -> dict[str, Any]:
    state = get_email_validation_window_state()
    payload = dict(state.get("raw") or {})
    if not payload:
        payload = {
            "opened": False,
            "opened_by": actor_id,
            "opened_at": "",
            "expires_at": "",
            "ttl_seconds": 0,
            "single_use": True,
            "used": False,
            "last_delivery_log_id": None,
        }
    payload["opened"] = False
    payload["disable_reason"] = customer_safe_text(reason)
    payload["disabled_at"] = utc_now()
    if actor_id is not None:
        payload["disabled_by"] = int(actor_id)
    with get_conn() as conn:
        _upsert_email_validation_window(conn, payload, actor_id)
        _record_audit_log(
            conn,
            DEFAULT_WORKSPACE_ID,
            actor_id,
            "close_email_validation_window",
            "email_validation_window",
            "current",
            {"status": "closed", "disable_reason": reason},
        )
    return _email_validation_window_state_from_payload(payload)


def mark_email_validation_window_used(*, delivery_log_id: int | None = None, actor_id: int | None = None) -> dict[str, Any]:
    state = get_email_validation_window_state()
    payload = dict(state.get("raw") or {})
    if not payload:
        return state
    payload["used"] = True
    payload["used_at"] = utc_now()
    if delivery_log_id is not None:
        payload["last_delivery_log_id"] = int(delivery_log_id)
    if payload.get("single_use", True):
        payload["opened"] = False
        payload["disable_reason"] = "used_single_delivery"
        payload["disabled_at"] = utc_now()
    with get_conn() as conn:
        _upsert_email_validation_window(conn, payload, actor_id)
        _record_audit_log(
            conn,
            DEFAULT_WORKSPACE_ID,
            actor_id,
            "use_email_validation_window",
            "email_validation_window",
            "current",
            {
                "status": "used",
                "delivery_log_id": delivery_log_id,
                "disable_reason": payload.get("disable_reason") or "",
            },
        )
    return _email_validation_window_state_from_payload(payload)


def _upsert_email_validation_window(conn: sqlite3.Connection, payload: dict[str, Any], actor_id: int | None) -> None:
    conn.execute(
        """
        INSERT INTO system_settings (
            workspace_id, key, value_json, value_type, is_locked, source,
            updated_by, updated_at
        ) VALUES (?, ?, ?, 'json', 0, 'database', ?, ?)
        ON CONFLICT(workspace_id, key) DO UPDATE SET
            value_json=excluded.value_json,
            value_type='json',
            is_locked=0,
            source='database',
            updated_by=excluded.updated_by,
            updated_at=excluded.updated_at
        """,
        (
            DEFAULT_WORKSPACE_ID,
            EMAIL_VALIDATION_WINDOW_KEY,
            json.dumps(_redact_json(payload), ensure_ascii=False),
            actor_id,
            utc_now(),
        ),
    )


def _email_validation_window_state_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload or {})
    now_dt = datetime.now(timezone.utc)
    expires_at = _parse_iso_datetime(payload.get("expires_at"))
    opened = bool(payload.get("opened"))
    expired = bool(opened and expires_at and expires_at <= now_dt)
    used = bool(payload.get("used"))
    if opened and expired:
        payload["opened"] = False
        payload["disable_reason"] = payload.get("disable_reason") or "expired"
    open_now = bool(payload.get("opened")) and not expired and not used
    remaining_seconds = 0
    if open_now and expires_at:
        remaining_seconds = max(0, int((expires_at - now_dt).total_seconds()))
    disable_reason = customer_safe_text(payload.get("disable_reason") or ("expired" if expired else ""))
    return {
        "is_open": open_now,
        "opened_by": _safe_int(payload.get("opened_by")),
        "opened_at": customer_safe_text(payload.get("opened_at")),
        "expires_at": customer_safe_text(payload.get("expires_at")),
        "ttl_seconds": _safe_int(payload.get("ttl_seconds")) or 0,
        "remaining_seconds": remaining_seconds,
        "single_use": bool(payload.get("single_use", True)),
        "used": used,
        "last_delivery_log_id": _safe_int(payload.get("last_delivery_log_id")),
        "disable_reason": disable_reason,
        "reason": customer_safe_text(payload.get("reason")),
        "raw": payload,
    }


def save_runtime_settings(payload: dict[str, Any], actor_id: int | None = None) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError("settings payload must be an object")
    current = list_runtime_settings()
    now = utc_now()
    changed: dict[str, Any] = {}
    with get_conn() as conn:
        for key, raw_value in payload.items():
            if key not in DEFINITIONS_BY_KEY:
                raise ValueError(f"unknown runtime setting: {key}")
            if current[key]["is_locked"]:
                raise ValueError(f"{key} is locked by deployment configuration")
            value = validate_runtime_setting(key, raw_value)
            changed[key] = value
            conn.execute(
                """
                INSERT INTO system_settings (
                    workspace_id, key, value_json, value_type, is_locked, source,
                    updated_by, updated_at
                ) VALUES (?, ?, ?, ?, 0, 'database', ?, ?)
                ON CONFLICT(workspace_id, key) DO UPDATE SET
                    value_json=excluded.value_json,
                    value_type=excluded.value_type,
                    is_locked=0,
                    source='database',
                    updated_by=excluded.updated_by,
                    updated_at=excluded.updated_at
                """,
                (
                    DEFAULT_WORKSPACE_ID,
                    key,
                    setting_value_json(value),
                    DEFINITIONS_BY_KEY[key].value_type,
                    actor_id,
                    now,
                ),
            )
        if changed:
            _record_audit_log(conn, DEFAULT_WORKSPACE_ID, actor_id, "update_runtime_settings", "system_settings", "runtime", changed)
    return list_runtime_settings()


def _row_to_user(row: dict[str, Any]) -> dict[str, Any]:
    row.pop("password_hash", None)
    return row


def _normalize_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _validate_user_role(role: str) -> str:
    if role not in USER_ROLES:
        raise ValueError("invalid user role")
    return role


def _validate_user_status(status: str) -> str:
    if status not in USER_STATUSES:
        raise ValueError("invalid user status")
    return status


def _record_audit_log(
    conn: sqlite3.Connection,
    workspace_id: int,
    user_id: int | None,
    action_type: str,
    resource_type: str,
    resource_id: str,
    details: dict[str, Any] | None = None,
    ip_address: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO audit_logs (
            workspace_id, user_id, action_type, resource_type, resource_id,
            details_json, ip_address, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            user_id,
            action_type,
            resource_type,
            resource_id,
            json.dumps(_redact_json(details or {}), ensure_ascii=False),
            ip_address,
            utc_now(),
        ),
    )


def _parse_iso_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
        _mark_report_snapshots_job_deleted(conn, job_id)
        conn.execute("DELETE FROM monitor_jobs WHERE id=?", (job_id,))


def _mark_report_snapshots_job_deleted(conn: sqlite3.Connection, job_id: int) -> None:
    row = conn.execute("SELECT * FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        return
    snapshot = report_job_snapshot(row_to_job(conn, row))
    if not snapshot:
        return
    snapshot["deleted_at"] = utc_now()
    conn.execute(
        "UPDATE reports SET job_snapshot_json=? WHERE job_id=?",
        (json.dumps(snapshot, ensure_ascii=False), job_id),
    )


def _summary_job_id_expr(alias: str = "summary") -> str:
    return f"CASE WHEN json_valid({alias}) THEN CAST(json_extract({alias}, '$.job_id') AS INTEGER) ELSE NULL END"


def has_running_run_for_job(job_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT 1
            FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id={_summary_job_id_expr('r.summary')}
            WHERE r.status='running'
              AND (
                r.job_id=?
                OR (r.job_id IS NULL AND j.id=?)
              )
            LIMIT 1
            """,
            (job_id, job_id),
        ).fetchone()
    return bool(row)


def cancel_running_runs_for_job(job_id: int, message: str) -> int:
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT r.id, r.summary
            FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id={_summary_job_id_expr('r.summary')}
            WHERE r.status='running'
              AND (
                r.job_id=?
                OR (r.job_id IS NULL AND j.id=?)
              )
            """,
            (job_id, job_id),
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


def create_run(job_id: int, summary: dict[str, Any] | None = None, timeout_seconds: int | None = None) -> int:
    with get_conn() as conn:
        job = conn.execute("SELECT workspace_id, created_by FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
        workspace_id = _safe_int(job["workspace_id"]) if job else DEFAULT_WORKSPACE_ID
        created_by = _safe_int(job["created_by"]) if job else None
        started_at = datetime.now(timezone.utc)
        deadline_at = (started_at + timedelta(seconds=int(timeout_seconds))).isoformat() if timeout_seconds else None
        cur = conn.execute(
            """
            INSERT INTO crawl_runs (
                workspace_id, job_id, status, started_at, summary,
                timeout_seconds, deadline_at, created_by, updated_by
            )
            VALUES (?, ?, 'running', ?, ?, ?, ?, ?, ?)
            """,
            (
                workspace_id or DEFAULT_WORKSPACE_ID,
                job_id,
                started_at.isoformat(),
                json.dumps(_redact_json(summary or {}), ensure_ascii=False),
                timeout_seconds,
                deadline_at,
                created_by,
                created_by,
            ),
        )
        return int(cur.lastrowid)


def set_run_resource_bindings(run_id: int, account_id: int | None = None, proxy_id: int | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE crawl_runs
            SET account_id=COALESCE(?, account_id),
                proxy_id=COALESCE(?, proxy_id),
                updated_by=updated_by
            WHERE id=?
            """,
            (account_id, proxy_id, run_id),
        )


def update_run_summary(run_id: int, summary: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE crawl_runs SET summary=? WHERE id=? AND status='running'",
            (json.dumps(_redact_json(summary), ensure_ascii=False), run_id),
        )


def finish_run(run_id: int, status: str, summary: dict[str, Any], error: str | None = None, timeout_reason: str | None = None) -> None:
    if status not in RUN_TERMINAL_STATUSES:
        raise ValueError(f"invalid terminal run status: {status}")
    payload = dict(summary or {})
    payload.setdefault("terminal_status", status)
    payload.setdefault("finalized_at", utc_now())
    payload["phase"] = payload.get("phase") or f"terminal:{status}"
    payload["progress_updated_at"] = utc_now()
    summary_json = json.dumps(_redact_json(payload), ensure_ascii=False)
    trimmed_error = _trim_error(error)
    trimmed_timeout = _trim_error(timeout_reason)
    with get_conn() as conn:
        current = conn.execute("SELECT status FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
        if not current:
            return
        if str(current["status"] or "") in RUN_TERMINAL_STATUSES:
            payload["terminal_status"] = str(current["status"] or "")
            payload["phase"] = payload.get("phase") or f"terminal:{current['status']}"
            summary_json = json.dumps(_redact_json(payload), ensure_ascii=False)
            conn.execute(
                """
                UPDATE crawl_runs
                SET summary=?,
                    error_message=COALESCE(NULLIF(error_message, ''), ?),
                    timeout_reason=COALESCE(timeout_reason, ?)
                WHERE id=?
                """,
                (summary_json, trimmed_error, trimmed_timeout, run_id),
            )
            return
        conn.execute(
            """
            UPDATE crawl_runs
            SET status=?, finished_at=?, summary=?, error_message=?, timeout_reason=COALESCE(?, timeout_reason)
            WHERE id=? AND status NOT IN (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                status,
                utc_now(),
                summary_json,
                trimmed_error,
                trimmed_timeout,
                run_id,
                *sorted(RUN_TERMINAL_STATUSES),
            ),
        )


def record_skipped_run(job_id: int, reason: str, summary: dict[str, Any] | None = None, cooldown_seconds: int = 300) -> int:
    payload = dict(summary or {})
    payload.setdefault("job_id", job_id)
    payload.setdefault("skipped", True)
    payload.setdefault("skip_reason", reason)
    now = utc_now()
    with get_conn() as conn:
        job = conn.execute("SELECT workspace_id, created_by FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
        workspace_id = _safe_int(job["workspace_id"]) if job else DEFAULT_WORKSPACE_ID
        created_by = _safe_int(job["created_by"]) if job else None
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
            INSERT INTO crawl_runs (workspace_id, job_id, status, started_at, finished_at, summary, error_message, created_by, updated_by)
            VALUES (?, ?, 'skipped', ?, ?, ?, ?, ?, ?)
            """,
            (
                workspace_id or DEFAULT_WORKSPACE_ID,
                job_id,
                now,
                now,
                json.dumps(_redact_json(payload), ensure_ascii=False),
                _trim_error(reason),
                created_by,
                created_by,
            ),
        )
        return int(cur.lastrowid)


def acquire_account_lock(account_id: int | None, run_id: int, lock_expires_at: str | None = None) -> bool:
    if not account_id:
        return True
    now = utc_now()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT locked_by_run_id FROM social_accounts WHERE id=?",
            (account_id,),
        ).fetchone()
        if not row:
            return False
        if row["locked_by_run_id"] and int(row["locked_by_run_id"]) != int(run_id):
            return False
        cur = conn.execute(
            """
            UPDATE social_accounts
            SET locked_by_run_id=?, locked_at=?, lock_expires_at=?, updated_at=?
            WHERE id=? AND (
                locked_by_run_id IS NULL
                OR locked_by_run_id=?
            )
            """,
            (run_id, now, lock_expires_at or "", now, account_id, run_id),
        )
        return cur.rowcount == 1


def release_account_lock(account_id: int | None, run_id: int | None = None) -> None:
    if not account_id:
        return
    with get_conn() as conn:
        if run_id:
            conn.execute(
                """
                UPDATE social_accounts
                SET locked_by_run_id=NULL, locked_at=NULL, lock_expires_at=NULL, updated_at=?
                WHERE id=? AND locked_by_run_id=?
                """,
                (utc_now(), account_id, run_id),
            )
        else:
            conn.execute(
                """
                UPDATE social_accounts
                SET locked_by_run_id=NULL, locked_at=NULL, lock_expires_at=NULL, updated_at=?
                WHERE id=?
                """,
                (utc_now(), account_id),
            )


def acquire_proxy_lock(proxy_id: int | None, run_id: int, expires_at: str | None = None, workspace_id: int | None = None) -> bool:
    if not proxy_id:
        return True
    now = utc_now()
    with get_conn() as conn:
        proxy = conn.execute(
            "SELECT workspace_id, max_concurrency, status FROM proxy_profiles WHERE id=?",
            (proxy_id,),
        ).fetchone()
        if not proxy or proxy["status"] != "active":
            return False
        limit = max(1, _safe_int(proxy["max_concurrency"]) or 1)
        existing = conn.execute(
            """
            SELECT id FROM resource_locks
            WHERE resource_type='proxy' AND resource_id=? AND run_id=?
            """,
            (proxy_id, run_id),
        ).fetchone()
        if existing:
            return True
        active_count = conn.execute(
            """
            SELECT COUNT(*) AS n
            FROM resource_locks l
            JOIN crawl_runs r ON r.id = l.run_id
            WHERE l.resource_type='proxy'
              AND l.resource_id=?
              AND r.status='running'
            """,
            (proxy_id,),
        ).fetchone()["n"]
        if int(active_count or 0) >= limit:
            return False
        try:
            conn.execute(
                """
                INSERT INTO resource_locks (workspace_id, resource_type, resource_id, run_id, locked_at, expires_at)
                VALUES (?, 'proxy', ?, ?, ?, ?)
                """,
                (_safe_int(workspace_id) or _safe_int(proxy["workspace_id"]) or DEFAULT_WORKSPACE_ID, proxy_id, run_id, now, expires_at or ""),
            )
        except sqlite3.IntegrityError:
            return True
        return True


def release_proxy_locks(run_id: int, proxy_id: int | None = None) -> None:
    with get_conn() as conn:
        if proxy_id:
            conn.execute(
                "DELETE FROM resource_locks WHERE resource_type='proxy' AND resource_id=? AND run_id=?",
                (proxy_id, run_id),
            )
        else:
            conn.execute("DELETE FROM resource_locks WHERE run_id=?", (run_id,))


def release_run_resource_locks(run_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE social_accounts
            SET locked_by_run_id=NULL, locked_at=NULL, lock_expires_at=NULL, updated_at=?
            WHERE locked_by_run_id=?
            """,
            (utc_now(), run_id),
        )
        conn.execute("DELETE FROM resource_locks WHERE run_id=?", (run_id,))


def preview_crawl_run_job_id_backfill(apply: bool = False) -> dict[str, Any]:
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT r.id, {_summary_job_id_expr('r.summary')} AS summary_job_id, j.id AS resolved_job_id
            FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id={_summary_job_id_expr('r.summary')}
            WHERE r.job_id IS NULL
              AND {_summary_job_id_expr('r.summary')} IS NOT NULL
            ORDER BY r.id
            """
        ).fetchall()
        resolvable = [
            {"run_id": int(row["id"]), "job_id": int(row["resolved_job_id"])}
            for row in rows
            if row["resolved_job_id"] is not None
        ]
        unresolved = [
            {"run_id": int(row["id"]), "summary_job_id": int(row["summary_job_id"])}
            for row in rows
            if row["resolved_job_id"] is None and row["summary_job_id"] is not None
        ]
        applied = 0
        if apply:
            for item in resolvable:
                cur = conn.execute(
                    "UPDATE crawl_runs SET job_id=? WHERE id=? AND job_id IS NULL",
                    (item["job_id"], item["run_id"]),
                )
                applied += cur.rowcount
    return {"resolvable": resolvable, "unresolved": unresolved, "applied": applied, "dry_run": not apply}


def recover_stale_runs_and_locks(reason: str = "scheduler_recovery") -> dict[str, int]:
    now_dt = datetime.now(timezone.utc)
    now = now_dt.isoformat()
    recovered_runs = 0
    interrupted_runs = 0
    released_account_locks = 0
    released_proxy_locks = 0
    try:
        heartbeat_grace_seconds = int(get_runtime_setting_value("stale_run_heartbeat_grace_seconds"))
    except Exception:
        heartbeat_grace_seconds = 600
    with get_conn() as conn:
        running_rows = conn.execute(
            """
            SELECT
                r.id,
                r.summary,
                r.deadline_at,
                r.account_id,
                r.proxy_id,
                EXISTS(SELECT 1 FROM social_accounts a WHERE a.locked_by_run_id=r.id) AS has_account_lock,
                EXISTS(SELECT 1 FROM resource_locks l WHERE l.run_id=r.id) AS has_proxy_lock
            FROM crawl_runs r
            WHERE r.status='running'
            """
        ).fetchall()
        for row in running_rows:
            deadline = _parse_iso_datetime(row["deadline_at"])
            summary = _json_loads(row["summary"], {})
            if not isinstance(summary, dict):
                summary = {}
            if deadline and deadline <= now_dt:
                summary["timeout"] = True
                summary["timeout_reason"] = "任务达到系统运行时间上限，恢复流程已释放资源锁"
                summary["recovered_by"] = reason
                summary["phase"] = "terminal:timeout"
                summary["progress_updated_at"] = now
                cur = conn.execute(
                    """
                    UPDATE crawl_runs
                    SET status='timeout', finished_at=?, summary=?, error_message=?, timeout_reason=COALESCE(timeout_reason, ?)
                    WHERE id=? AND status='running'
                    """,
                    (
                        now,
                        json.dumps(_redact_json(summary), ensure_ascii=False),
                        _trim_error(summary["timeout_reason"]),
                        _trim_error(reason),
                        row["id"],
                    ),
                )
                if cur.rowcount:
                    recovered_runs += 1
                continue
            if _should_interrupt_stale_run(row, summary, now_dt, heartbeat_grace_seconds):
                summary["interrupted"] = True
                summary["interruption_reason"] = "运行进程已无活跃证据，恢复流程已标记为中断"
                summary["recovered_by"] = reason
                summary["phase"] = "terminal:interrupted"
                summary["progress_updated_at"] = now
                summary.setdefault("unresolved_ai_count", 0)
                cur = conn.execute(
                    """
                    UPDATE crawl_runs
                    SET status='interrupted', finished_at=?, summary=?, error_message=?
                    WHERE id=? AND status='running'
                    """,
                    (
                        now,
                        json.dumps(_redact_json(summary), ensure_ascii=False),
                        _trim_error(summary["interruption_reason"]),
                        row["id"],
                    ),
                )
                if cur.rowcount:
                    interrupted_runs += 1
        terminal_statuses = ("success", "partial_failed", "failed", "timeout", "cancelled", "interrupted", "skipped")
        placeholders = ",".join("?" for _ in terminal_statuses)
        rows = conn.execute(
            f"""
            SELECT a.id
            FROM social_accounts a
            LEFT JOIN crawl_runs r ON r.id = a.locked_by_run_id
            WHERE a.locked_by_run_id IS NOT NULL
              AND (
                r.id IS NULL
                OR r.status IN ({placeholders})
              )
            """,
            terminal_statuses,
        ).fetchall()
        account_ids = [int(row["id"]) for row in rows]
        if account_ids:
            conn.execute(
                f"""
                UPDATE social_accounts
                SET locked_by_run_id=NULL, locked_at=NULL, lock_expires_at=NULL, updated_at=?
                WHERE id IN ({",".join("?" for _ in account_ids)})
                """,
                [now, *account_ids],
            )
            released_account_locks = len(account_ids)
        proxy_rows = conn.execute(
            f"""
            SELECT l.id
            FROM resource_locks l
            LEFT JOIN crawl_runs r ON r.id = l.run_id
            WHERE r.id IS NULL
               OR r.status IN ({placeholders})
            """,
            terminal_statuses,
        ).fetchall()
        proxy_lock_ids = [int(row["id"]) for row in proxy_rows]
        if proxy_lock_ids:
            conn.execute(
                f"DELETE FROM resource_locks WHERE id IN ({','.join('?' for _ in proxy_lock_ids)})",
                proxy_lock_ids,
            )
            released_proxy_locks = len(proxy_lock_ids)
    return {
        "recovered_runs": recovered_runs,
        "interrupted_runs": interrupted_runs,
        "released_account_locks": released_account_locks,
        "released_proxy_locks": released_proxy_locks,
    }


def _should_interrupt_stale_run(row: sqlite3.Row, summary: dict[str, Any], now_dt: datetime, heartbeat_grace_seconds: int) -> bool:
    if not summary.get("phase_7_1_lifecycle"):
        return False
    if row["has_account_lock"] or row["has_proxy_lock"]:
        return False
    if summary.get("retry_state") in {"running", "waiting"}:
        return False
    progress_raw = summary.get("progress_updated_at") or summary.get("phase_started_at")
    progress_at = _parse_iso_datetime(progress_raw)
    if not progress_at:
        return False
    return (now_dt - progress_at).total_seconds() >= max(60, int(heartbeat_grace_seconds or 600))


def get_run(run_id: int, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_conn() as conn:
        actor_clause = ""
        actor_params: list[Any] = []
        if actor:
            actor_clause = "r.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, r.created_by)=?)"
            actor_params = [
                _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
                actor.get("role"),
                _safe_int(actor.get("id")) or 0,
            ]
        where = "r.id=?"
        params: list[Any] = [run_id]
        if actor_clause:
            where += f" AND {actor_clause}"
            params.extend(actor_params)
        row = conn.execute(
            f"""
            SELECT r.*, j.law_firm_name FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {where}
            """,
            params,
        ).fetchone()
    if not row:
        return None
    item = _hydrate_run_row(row)
    _attach_run_lead_counts([item])
    return item


def get_run_detail_bundle(
    run_id: int,
    *,
    actor: dict[str, Any] | None = None,
    ai_filters: dict[str, Any] | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any] | None:
    run = get_run(run_id, actor=actor)
    if not run:
        return None
    collection_logs = list_run_collection_logs(run_id)
    contents = list_run_collected_contents(run_id, actor=actor)
    ai_result = list_run_ai_evaluations(run_id, actor=actor, filters=ai_filters or {}, page=page, per_page=per_page)
    reports = list_run_reports(run_id, actor=actor)
    report_ids = [int(report["id"]) for report in reports if report.get("id")]
    delivery_logs = list_run_email_delivery_logs(run_id, report_ids=report_ids, actor=actor)
    return {
        "run": run,
        "overview": {
            "run_id": run.get("id"),
            "job_id": run.get("job_id"),
            "status": run.get("status"),
            "display_status": run.get("display_status"),
            "law_firm_name": run.get("display_law_firm_name") or run.get("law_firm_name"),
            "summary": run.get("summary") or {},
        },
        "collection_logs": collection_logs,
        "collected_contents": contents,
        "ai_evaluations": ai_result["items"],
        "ai_pagination": ai_result["pagination"],
        "ai_filters": ai_result["filters"],
        "reports": reports,
        "email_delivery_logs": delivery_logs,
    }


def list_run_collected_contents(run_id: int, actor: dict[str, Any] | None = None, limit: int = 500) -> list[dict[str, Any]]:
    limit = min(5000, _coerce_limit(limit, 500))
    clauses = ["c.run_id=?"]
    params: list[Any] = [run_id]
    if actor:
        clauses.append("c.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by)=?)")
        params.extend([
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ])
    sql = f"""
        SELECT
            c.id, c.platform, c.content_id, c.job_id, c.run_id,
            COALESCE(c.law_firm_name, j.law_firm_name) AS law_firm_name,
            c.source_keyword, c.title, c.description, c.author_name,
            c.content_url, c.cover_url, c.publish_time, c.comment_count,
            c.first_seen_at, c.last_seen_at
        FROM raw_contents c
        LEFT JOIN monitor_jobs j ON j.id = c.job_id
        WHERE {' AND '.join(clauses)}
        ORDER BY c.id DESC
    """
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_hydrate_run_content_row(dict(row)) for row in rows]


def list_run_collection_logs(run_id: int, limit_chars: int = 20000) -> list[dict[str, Any]]:
    run_root = MONITOR_DATA_DIR / "runs"
    logs = []
    for path in run_root.glob(f"**/run_{int(run_id)}_*/**/crawler.log"):
        content = customer_safe_text(path.read_text(encoding="utf-8", errors="ignore"))[-limit_chars:]
        logs.append({"path": "运行日志", "content": content})
    return logs


def _hydrate_run_content_row(item: dict[str, Any]) -> dict[str, Any]:
    for key in ("law_firm_name", "source_keyword", "title", "description", "author_name"):
        item[key] = customer_safe_text(item.get(key))
    item["content_url"] = customer_safe_url(item.get("content_url"))
    item["cover_url"] = customer_safe_url(item.get("cover_url"))
    return item


def list_run_ai_evaluations(
    run_id: int,
    *,
    actor: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    filters = dict(filters or {})
    page = max(1, _safe_int(page) or 1)
    per_page = min(200, _coerce_limit(per_page, 50))
    clauses = ["c.run_id=?"]
    params: list[Any] = [run_id]
    applied: dict[str, Any] = {}
    report_id = _safe_int(filters.get("report_id"))
    if report_id:
        applied["report_id"] = report_id
    if actor:
        clauses.append("c.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by)=?)")
        params.extend([
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ])
    status = str(filters.get("status") or "").strip()
    if status:
        if status in {"unevaluated", "limited_context"}:
            clauses.append("e.id IS NULL")
        else:
            clauses.append("e.status=?")
            params.append(status)
        applied["status"] = status
    risk = str(filters.get("risk") or "").strip()
    if risk:
        if risk == "high":
            clauses.append("e.status!='pending_review' AND e.is_related=1 AND e.is_negative=1 AND e.risk_level='high'")
        elif risk in {"negative", "suspected_negative"}:
            clauses.append("e.status!='pending_review' AND e.is_related=1 AND e.is_negative=1 AND COALESCE(e.risk_level, '')!='high'")
        elif risk == "pending":
            clauses.append("e.status='pending_review'")
        elif risk == "unrelated":
            clauses.append("e.id IS NOT NULL AND e.status!='pending_review' AND e.is_related=0")
        elif risk in {"none", "no_risk"}:
            clauses.append("e.id IS NOT NULL AND e.status!='pending_review' AND e.is_related=1 AND e.is_negative=0")
        elif risk in {"unevaluated", "limited_context"}:
            clauses.append("e.id IS NULL")
        applied["risk"] = risk
    platform = str(filters.get("platform") or "").strip()
    if platform:
        clauses.append("c.platform=?")
        params.append(platform)
        applied["platform"] = platform
    keyword = str(filters.get("keyword") or "").strip()
    if keyword:
        clauses.append("COALESCE(c.source_keyword, '') LIKE ?")
        params.append(f"%{keyword}%")
        applied["keyword"] = keyword
    title = str(filters.get("title") or "").strip()
    if title:
        clauses.append("COALESCE(c.title, '') LIKE ?")
        params.append(f"%{title}%")
        applied["title"] = title
    where = " AND ".join(clauses)
    base_sql = f"""
        FROM raw_contents c
        LEFT JOIN monitor_jobs j ON j.id = c.job_id
        LEFT JOIN crawl_runs r ON r.id = c.run_id
        LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
        LEFT JOIN ai_evaluation_traces t ON t.ai_evaluation_id = e.id
        WHERE {where}
    """
    with get_conn() as conn:
        total = int(conn.execute(f"SELECT COUNT(*) AS n {base_sql}", params).fetchone()["n"] or 0)
        sql = f"""
            SELECT
                c.id, c.platform, c.content_id, c.job_id, c.run_id,
                COALESCE(c.law_firm_name, j.law_firm_name) AS law_firm_name,
                c.source_keyword, c.title, c.description, c.author_name,
                c.content_url, c.cover_url, c.publish_time, c.comment_count,
                c.first_seen_at, c.last_seen_at,
                r.status AS run_status,
                e.id AS evaluation_id,
                e.status AS eval_status, e.is_related, e.is_negative, e.risk_level,
                e.reason, e.evidence_quotes, e.recommended_action, e.created_at AS evaluated_at,
                t.id AS trace_id
            {base_sql}
            ORDER BY c.id DESC
        """
        query_params = list(params)
        if per_page > 0:
            sql += " LIMIT ? OFFSET ?"
            query_params.extend([per_page, (page - 1) * per_page])
        rows = conn.execute(sql, query_params).fetchall()
    items = [_hydrate_run_ai_evaluation_row(dict(row)) for row in rows]
    total_pages = 1 if per_page <= 0 else max(1, (total + per_page - 1) // per_page)
    return {
        "items": items,
        "pagination": {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages},
        "filters": applied,
    }


def _hydrate_run_ai_evaluation_row(item: dict[str, Any]) -> dict[str, Any]:
    item["is_related"] = bool(item.get("is_related"))
    item["is_negative"] = bool(item.get("is_negative"))
    item["evidence_quotes"] = [customer_safe_text(str(q)) for q in _json_loads(item.get("evidence_quotes"))]
    for key in ("law_firm_name", "source_keyword", "title", "description", "author_name", "reason", "recommended_action"):
        item[key] = customer_safe_text(item.get(key))
    item["content_url"] = customer_safe_url(item.get("content_url"))
    item["cover_url"] = customer_safe_url(item.get("cover_url"))
    apply_lead_status_fields(item)
    item["trace_state"] = {
        "status": "available" if item.get("trace_id") else "limited_context",
        "limited_context": not bool(item.get("trace_id")),
        "trace_id": item.get("trace_id"),
        "message": "" if item.get("trace_id") else "历史记录未保存完整入参/出参。",
    }
    return item


def get_ai_evaluation_detail(
    evaluation_id: int,
    *,
    run_id: int | None = None,
    actor: dict[str, Any] | None = None,
    admin_debug: bool = False,
) -> dict[str, Any] | None:
    clauses = ["e.id=?"]
    params: list[Any] = [evaluation_id]
    if run_id is not None:
        clauses.append("c.run_id=?")
        params.append(run_id)
    if actor:
        clauses.append("c.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by, e.created_by)=?)")
        params.extend([
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ])
    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT
                c.id, c.platform, c.content_id, c.job_id, c.run_id,
                COALESCE(c.law_firm_name, j.law_firm_name) AS law_firm_name,
                c.source_keyword, c.title, c.description, c.author_name,
                c.content_url, c.cover_url, c.publish_time, c.comment_count,
                c.first_seen_at, c.last_seen_at,
                r.status AS run_status,
                e.id AS evaluation_id,
                e.status AS eval_status, e.is_related, e.is_negative, e.risk_level,
                e.reason, e.evidence_quotes, e.recommended_action, e.created_at AS evaluated_at,
                t.id AS trace_id
            FROM ai_evaluations e
            JOIN raw_contents c ON c.id = e.raw_content_id
            LEFT JOIN monitor_jobs j ON j.id = c.job_id
            LEFT JOIN crawl_runs r ON r.id = c.run_id
            LEFT JOIN ai_evaluation_traces t ON t.ai_evaluation_id = e.id
            WHERE {' AND '.join(clauses)}
            ORDER BY t.id DESC
            LIMIT 1
            """,
            params,
        ).fetchone()
    if not row:
        return None
    item = _hydrate_run_ai_evaluation_row(dict(row))
    trace = get_ai_evaluation_trace(ai_evaluation_id=evaluation_id, raw_content_id=item.get("id"), run_id=item.get("run_id"))
    item["trace"] = role_safe_ai_trace_view(trace, admin=admin_debug)
    return item


def list_run_reports(run_id: int, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    clauses = ["reports.run_id=?"]
    params: list[Any] = [run_id]
    if actor:
        clauses.append("reports.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)")
        params.extend([
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ])
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT reports.*, monitor_jobs.id AS current_job_id, monitor_jobs.law_firm_name
            FROM reports
            LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
            WHERE {' AND '.join(clauses)}
            ORDER BY reports.id DESC
            """,
            params,
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["summary"] = _json_loads(item.get("summary"), {})
        _hydrate_report_item(item)
        result.append(item)
    _attach_report_lead_counts(result)
    return result


def list_run_email_delivery_logs(run_id: int, report_ids: list[int] | None = None, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    report_ids = [int(item) for item in (report_ids or []) if _safe_int(item)]
    clauses = ["(reports.run_id=?"]
    params: list[Any] = [run_id]
    if report_ids:
        clauses[0] += f" OR email_delivery_logs.report_id IN ({','.join('?' for _ in report_ids)})"
        params.extend(report_ids)
    clauses[0] += ")"
    if actor:
        clauses.append("email_delivery_logs.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)")
        params.extend([
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ])
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT email_delivery_logs.*
            FROM email_delivery_logs
            LEFT JOIN reports ON reports.id = email_delivery_logs.report_id
            LEFT JOIN monitor_jobs ON monitor_jobs.id = email_delivery_logs.job_id
            WHERE {' AND '.join(clauses)}
            ORDER BY email_delivery_logs.id DESC
            """,
            params,
        ).fetchall()
    return [_hydrate_email_delivery_log(dict(row)) for row in rows]


def _run_actor_scope_clause(actor: dict[str, Any] | None) -> tuple[str, list[Any]]:
    if not actor:
        return "", []
    return (
        "r.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, r.created_by)=?)",
        [
            _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
            actor.get("role"),
            _safe_int(actor.get("id")) or 0,
        ],
    )


def _run_filter_clause(filters: dict[str, Any] | None, *, include_archived_default: bool = False) -> tuple[str, list[Any], dict[str, Any]]:
    filters = dict(filters or {})
    clauses: list[str] = []
    params: list[Any] = []
    applied: dict[str, Any] = {}

    visibility = str(filters.get("visibility") or ("all" if include_archived_default else "visible")).strip()
    if visibility not in {"visible", "archived", "all"}:
        visibility = "visible"
    if visibility != "all":
        clauses.append("r.visibility=?")
        params.append(visibility)
    applied["visibility"] = visibility

    run_type = str(filters.get("run_type") or "").strip()
    if run_type == "operational":
        clauses.append("COALESCE(r.run_type, 'scheduled') IN ('scheduled', 'manual')")
        applied["run_type"] = run_type
    elif run_type in {"scheduled", "manual", "test"}:
        clauses.append("r.run_type=?")
        params.append(run_type)
        applied["run_type"] = run_type

    status = str(filters.get("status") or "").strip()
    if status:
        clauses.append("r.status=?")
        params.append(status)
        applied["status"] = status

    job_id = _safe_int(filters.get("job_id") or filters.get("task_id"))
    if job_id is not None:
        clauses.append("r.job_id=?")
        params.append(job_id)
        applied["job_id"] = job_id

    law_firm = str(filters.get("law_firm") or filters.get("task") or "").strip()
    if law_firm:
        clauses.append("(j.law_firm_name LIKE ? OR r.summary LIKE ?)")
        like = f"%{law_firm}%"
        params.extend([like, like])
        applied["law_firm"] = law_firm

    platform = str(filters.get("platform") or "").strip()
    if platform:
        clauses.append("r.summary LIKE ?")
        params.append(f"%\"{platform}\"%")
        applied["platform"] = platform

    date_from = str(filters.get("date_from") or "").strip()
    if date_from:
        clauses.append("substr(r.started_at, 1, 10) >= ?")
        params.append(date_from[:10])
        applied["date_from"] = date_from[:10]

    date_to = str(filters.get("date_to") or "").strip()
    if date_to:
        clauses.append("substr(r.started_at, 1, 10) <= ?")
        params.append(date_to[:10])
        applied["date_to"] = date_to[:10]

    return " AND ".join(clauses), params, applied


def list_runs(limit: int = 100, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    page = list_runs_page(page=1, per_page=limit, actor=actor, include_archived_default=True)
    return page["items"]


def list_runs_page(
    page: int = 1,
    per_page: int = 100,
    actor: dict[str, Any] | None = None,
    filters: dict[str, Any] | None = None,
    include_archived_default: bool = False,
) -> dict[str, Any]:
    page = max(1, _safe_int(page) or 1)
    per_page = _coerce_limit(per_page, default=100)
    filter_clause, filter_params, applied_filters = _run_filter_clause(
        filters,
        include_archived_default=include_archived_default,
    )
    scope_clause, scope_params = _run_actor_scope_clause(actor)
    clauses = [clause for clause in (scope_clause, filter_clause) if clause]
    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    params = [*scope_params, *filter_params]
    base_sql = """
        FROM crawl_runs r
        LEFT JOIN monitor_jobs j ON j.id = r.job_id
    """
    with get_conn() as conn:
        total = int(
            conn.execute(
                f"SELECT COUNT(*) AS n {base_sql}{where_sql}",
                params,
            ).fetchone()["n"]
            or 0
        )
        sql = f"""
            SELECT r.*, j.law_firm_name {base_sql}{where_sql}
            ORDER BY r.id DESC
        """
        query_params = list(params)
        if per_page > 0:
            sql += " LIMIT ? OFFSET ?"
            query_params.extend([per_page, (page - 1) * per_page])
        rows = conn.execute(sql, query_params).fetchall()
    items = [_hydrate_run_row(row) for row in rows]
    _attach_run_lead_counts(items)
    total_pages = 1 if per_page <= 0 else max(1, (total + per_page - 1) // per_page)
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "filters": applied_filters,
    }


def set_run_visibility(run_id: int, visibility: str, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if visibility not in {"visible", "archived"}:
        raise ValueError("invalid run visibility")
    actor_scope, actor_params = _run_actor_scope_clause(actor)
    where = "r.id=?"
    params: list[Any] = [run_id]
    if actor_scope:
        where += f" AND {actor_scope}"
        params.extend(actor_params)
    with get_conn() as conn:
        row = conn.execute(
            f"""
            SELECT r.id FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {where}
            """,
            params,
        ).fetchone()
        if not row:
            return None
        if visibility == "archived":
            archived_at = utc_now()
            archived_by = _safe_int((actor or {}).get("id"))
        else:
            archived_at = None
            archived_by = None
        conn.execute(
            """
            UPDATE crawl_runs
            SET visibility=?, archived_at=?, archived_by=?
            WHERE id=?
            """,
            (visibility, archived_at, archived_by, run_id),
        )
    return get_run(run_id, actor=actor)


def archive_run(run_id: int, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return set_run_visibility(run_id, "archived", actor=actor)


def restore_run(run_id: int, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    return set_run_visibility(run_id, "visible", actor=actor)


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
    _hydrate_run_progress_fields(item, summary)
    return item


def _hydrate_run_progress_fields(item: dict[str, Any], summary: dict[str, Any]) -> None:
    collection_progress = summary.get("collection_progress")
    if isinstance(collection_progress, dict):
        item["collection_progress"] = _customer_safe_payload(collection_progress)
    ai_progress = summary.get("ai_progress")
    if isinstance(ai_progress, dict):
        item["ai_progress"] = _customer_safe_payload(ai_progress)
    progress_message = str(summary.get("progress_message") or "").strip()
    if progress_message:
        item["progress_message"] = customer_safe_text(progress_message)
    item["progress_updated_at"] = customer_safe_text(summary.get("progress_updated_at") or item.get("finished_at") or item.get("started_at") or "")


def _attach_run_lead_counts(runs: list[dict[str, Any]]) -> None:
    run_ids = [int(run["id"]) for run in runs if run.get("id")]
    if not run_ids:
        return
    counts = _lead_counts_by_run(run_ids)
    for run in runs:
        summary = run.get("summary") if isinstance(run.get("summary"), dict) else {}
        row = counts.get(int(run.get("id") or 0))
        if row:
            summary.update(_lead_count_summary(row))
        else:
            _setdefault_lead_count_summary(summary)
        run["summary"] = summary


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
        "success": "已完成",
        "partial_failed": "部分失败",
        "failed": "失败",
        "cancelled": "已取消",
        "timeout": "运行超时",
        "interrupted": "执行中断",
    }
    return labels.get(status, status or "")


def _run_display_error(item: dict[str, Any], summary: dict[str, Any]) -> str:
    status = str(item.get("status") or "")
    if status == "skipped":
        return str(summary.get("skip_reason") or item.get("error_message") or "")
    if status == "timeout":
        return str(summary.get("timeout_reason") or item.get("timeout_reason") or item.get("error_message") or "")
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


def list_reports(limit: int = 100, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit)
    sql = """
        SELECT reports.*, monitor_jobs.id AS current_job_id, monitor_jobs.law_firm_name FROM reports
        LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
    """
    params: list[Any] = []
    if actor:
        sql += " WHERE reports.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)"
        params.extend(
            [
                _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
                actor.get("role"),
                _safe_int(actor.get("id")) or 0,
            ]
        )
    sql += " ORDER BY reports.id DESC"
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


def get_report(report_id: int, actor: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_conn() as conn:
        where = "reports.id=?"
        params: list[Any] = [report_id]
        if actor:
            where += " AND reports.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)"
            params.extend(
                [
                    _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
                    actor.get("role"),
                    _safe_int(actor.get("id")) or 0,
                ]
            )
        row = conn.execute(
            f"""
            SELECT reports.*, monitor_jobs.id AS current_job_id, monitor_jobs.law_firm_name FROM reports
            LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
            WHERE {where}
            """,
            params,
        ).fetchone()
    if not row:
        return None
    report = dict(row)
    report["summary"] = _json_loads(report.get("summary"), {})
    _hydrate_report_item(report)
    _attach_report_lead_counts([report])
    return report


def email_send_window_key(job_id: int, frequency: str, when: datetime | str | None = None) -> str:
    target_id = _safe_int(job_id)
    if not target_id:
        raise ValueError("job_id is required")
    if isinstance(when, datetime):
        send_at = when
    elif when:
        send_at = _parse_iso_datetime(when)
        if send_at is None:
            raise ValueError("invalid send time")
    else:
        send_at = datetime.now(timezone.utc)
    if send_at.tzinfo is None:
        send_at = send_at.replace(tzinfo=timezone.utc)
    send_at = send_at.astimezone(timezone.utc)
    normalized_frequency = str(frequency or "daily").strip().lower()
    if normalized_frequency == "daily":
        return f"{target_id}_{send_at.date().isoformat()}"
    if normalized_frequency in {"6h", "12h", "cron"}:
        return f"{target_id}_{send_at.date().isoformat()}_{send_at.strftime('%H')}"
    raise ValueError("invalid email send frequency")


def record_email_delivery_log(payload: dict[str, Any]) -> dict[str, Any]:
    send_type = str(payload.get("send_type") or "").strip()
    if send_type not in EMAIL_DELIVERY_SEND_TYPES:
        raise ValueError("invalid email delivery send_type")
    status = str(payload.get("status") or "").strip()
    if status not in EMAIL_DELIVERY_STATUSES:
        raise ValueError("invalid email delivery status")
    job_id = _safe_int(payload.get("job_id"))
    if not job_id:
        raise ValueError("job_id is required")
    report_id = _safe_int(payload.get("report_id"))
    sent_by = _safe_int(payload.get("sent_by"))
    workspace_id = _safe_int(payload.get("workspace_id"))
    send_window_key = str(payload.get("send_window_key") or "").strip()
    if not send_window_key:
        frequency = str(payload.get("frequency") or "daily")
        send_window_key = email_send_window_key(job_id, frequency, payload.get("sent_at") or payload.get("created_at"))
    recipients_json = _email_recipients_json(payload.get("recipients_json", payload.get("recipients")))
    effective_recipients_json = _email_recipients_json(payload.get("effective_recipients_json", payload.get("effective_recipients")))
    trigger_source = customer_safe_text(str(payload.get("trigger_source") or _default_email_trigger_source(send_type)).strip())
    effective_recipient_source = customer_safe_text(str(payload.get("effective_recipient_source") or "limited_context").strip())
    email_template_id = _safe_int(payload.get("email_template_id"))
    email_template_name = customer_safe_text(payload.get("email_template_name"))
    email_template_source = customer_safe_text(payload.get("email_template_source"))
    email_subject_template = customer_safe_text(payload.get("email_subject_template"))
    sent_at = str(payload.get("sent_at") or "").strip() or None
    created_at = str(payload.get("created_at") or "").strip() or utc_now()
    with get_conn() as conn:
        if not workspace_id:
            row = conn.execute("SELECT workspace_id FROM monitor_jobs WHERE id=?", (job_id,)).fetchone()
            workspace_id = _safe_int(row["workspace_id"]) if row else DEFAULT_WORKSPACE_ID
        cur = conn.execute(
            """
            INSERT INTO email_delivery_logs (
                workspace_id, job_id, report_id, send_window_key, send_type,
                sent_by, sent_at, status, error_message, recipients_json,
                trigger_source, effective_recipients_json, effective_recipient_source,
                email_template_id, email_template_name, email_template_source,
                email_subject_template, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workspace_id or DEFAULT_WORKSPACE_ID,
                job_id,
                report_id,
                send_window_key,
                send_type,
                sent_by,
                sent_at,
                status,
                customer_safe_text(payload.get("error_message")),
                recipients_json,
                trigger_source,
                effective_recipients_json,
                effective_recipient_source,
                email_template_id,
                email_template_name,
                email_template_source,
                email_subject_template,
                created_at,
            ),
        )
        row = conn.execute("SELECT * FROM email_delivery_logs WHERE id=?", (int(cur.lastrowid),)).fetchone()
    return _hydrate_email_delivery_log(dict(row))


def try_record_email_delivery_log(payload: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return record_email_delivery_log(payload)
    except IntegrityError:
        return None


def update_email_delivery_log_status(
    log_id: int,
    status: str,
    error_message: str | None = None,
    sent_at: str | None = None,
) -> dict[str, Any] | None:
    if status not in EMAIL_DELIVERY_STATUSES:
        raise ValueError("invalid email delivery status")
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE email_delivery_logs
            SET status=?, error_message=?, sent_at=COALESCE(?, sent_at)
            WHERE id=?
            """,
            (status, customer_safe_text(error_message), sent_at, log_id),
        )
        row = conn.execute("SELECT * FROM email_delivery_logs WHERE id=?", (log_id,)).fetchone()
    return _hydrate_email_delivery_log(dict(row)) if row else None


def list_email_delivery_logs(
    job_id: int | None = None,
    report_id: int | None = None,
    limit: int = 100,
    actor: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit)
    clauses: list[str] = []
    params: list[Any] = []
    if job_id is not None:
        clauses.append("email_delivery_logs.job_id=?")
        params.append(job_id)
    if report_id is not None:
        clauses.append("email_delivery_logs.report_id=?")
        params.append(report_id)
    if actor:
        clauses.append(
            "email_delivery_logs.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)"
        )
        params.extend(
            [
                _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
                actor.get("role"),
                _safe_int(actor.get("id")) or 0,
            ]
        )
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"""
        SELECT email_delivery_logs.*
        FROM email_delivery_logs
        LEFT JOIN monitor_jobs ON monitor_jobs.id = email_delivery_logs.job_id
        LEFT JOIN reports ON reports.id = email_delivery_logs.report_id
        {where}
        ORDER BY email_delivery_logs.id DESC
    """
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_hydrate_email_delivery_log(dict(row)) for row in rows]


def _email_recipients_json(value: Any) -> str:
    if isinstance(value, str):
        loaded = _json_loads(value, [])
        if loaded != [] or value.strip() in {"[]", ""}:
            value = loaded
        else:
            value = [value]
    if not isinstance(value, list):
        value = []
    return json.dumps([customer_safe_text(str(item)) for item in value if str(item).strip()], ensure_ascii=False)


def _hydrate_email_delivery_log(item: dict[str, Any]) -> dict[str, Any]:
    item["error_message"] = customer_safe_text(item.get("error_message"))
    item["recipients"] = _json_loads(item.get("recipients_json"), [])
    item["recipients"] = [customer_safe_text(str(value)) for value in item["recipients"]]
    item["recipients_json"] = json.dumps(item["recipients"], ensure_ascii=False)
    item["trigger_source"] = customer_safe_text(item.get("trigger_source"))
    item["effective_recipients"] = _json_loads(item.get("effective_recipients_json"), [])
    item["effective_recipients"] = [customer_safe_text(str(value)) for value in item["effective_recipients"]]
    item["effective_recipients_json"] = json.dumps(item["effective_recipients"], ensure_ascii=False)
    item["effective_recipient_source"] = customer_safe_text(item.get("effective_recipient_source"))
    item["email_template_name"] = customer_safe_text(item.get("email_template_name"))
    item["email_template_source"] = customer_safe_text(item.get("email_template_source"))
    item["email_subject_template"] = customer_safe_text(item.get("email_subject_template"))
    return item


def _default_email_trigger_source(send_type: str) -> str:
    return "manual_resend" if send_type == "manual_resend" else "scheduler_auto"


def effective_email_template_provenance(job: dict[str, Any] | None) -> dict[str, Any]:
    job = job or {}
    template = None
    source = "default_renderer"
    template_id = _safe_int(job.get("email_template_id"))
    if template_id:
        template = get_email_template(template_id)
        if template:
            source = "task_bound"
    if not template:
        template = get_active_email_template()
        if template:
            source = "active_global_fallback"
    return {
        "id": _safe_int((template or {}).get("id")),
        "name": customer_safe_text((template or {}).get("name")),
        "source": source,
        "subject_template": customer_safe_text((template or {}).get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE),
    }


def _hydrate_report_item(item: dict[str, Any]) -> None:
    summary = item.get("summary") or {}
    if not isinstance(summary, dict):
        summary = {}
    snapshot = _json_loads(item.get("job_snapshot_json"), {})
    if not isinstance(snapshot, dict):
        snapshot = {}
    snapshot = _customer_safe_payload(snapshot)
    snapshot_job_id = _safe_int(summary.get("job_id"))
    report_snapshot_job_id = _safe_int(snapshot.get("job_id"))
    report_job_id = _safe_int(item.get("job_id"))
    current_job_id = _safe_int(item.get("current_job_id"))
    item["summary"] = _customer_safe_payload(summary)
    item["job_snapshot"] = snapshot
    if not item.get("law_firm_name"):
        item["law_firm_name"] = snapshot.get("law_firm_name") or summary.get("law_firm_name") or ""
    item["law_firm_name"] = customer_safe_text(item.get("law_firm_name"))
    item["display_law_firm_name"] = customer_safe_text(
        item.get("law_firm_name")
        or snapshot.get("law_firm_name")
        or summary.get("law_firm_name")
        or "历史报告"
    )
    item["email_error"] = customer_safe_text(item.get("email_error"))
    item["job_deleted"] = bool((report_snapshot_job_id or snapshot_job_id or report_job_id) and not current_job_id)
    has_recoverable_context = bool(
        report_snapshot_job_id
        or snapshot_job_id
        or snapshot.get("law_firm_name")
        or snapshot.get("platforms")
        or snapshot.get("keywords")
        or summary.get("law_firm_name")
        or summary.get("platforms")
        or summary.get("keywords")
    )
    item["legacy_without_job_snapshot"] = bool(not current_job_id and not has_recoverable_context)
    item["limited_context"] = bool(item["legacy_without_job_snapshot"])


def _attach_report_lead_counts(reports: list[dict[str, Any]]) -> None:
    run_ids = [int(report["run_id"]) for report in reports if report.get("run_id")]
    if not run_ids:
        return
    counts = _lead_counts_by_run(run_ids)
    for report in reports:
        summary = report.get("summary") or {}
        row = counts.get(int(report.get("run_id") or 0))
        if row:
            summary.update(_lead_count_summary(row))
        else:
            _setdefault_lead_count_summary(summary)
        report["summary"] = summary


def _lead_counts_by_run(run_ids: list[int]) -> dict[int, dict[str, int]]:
    if not run_ids:
        return {}
    placeholders = ",".join("?" for _ in run_ids)
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT
                c.run_id,
                COUNT(*) AS total_count,
                SUM(CASE WHEN e.status='pending_review' THEN 1 ELSE 0 END) AS pending_review_count,
                SUM(CASE WHEN e.status!='pending_review' AND e.is_related=1 AND e.is_negative=1 THEN 1 ELSE 0 END) AS negative_count,
                SUM(CASE WHEN e.status!='pending_review' AND e.is_related=1 AND e.is_negative=1 AND COALESCE(e.risk_level, '')!='high' THEN 1 ELSE 0 END) AS suspected_negative_count,
                SUM(CASE WHEN e.status!='pending_review' AND e.is_related=1 AND e.is_negative=1 AND e.risk_level='high' THEN 1 ELSE 0 END) AS high_count,
                SUM(CASE WHEN e.id IS NOT NULL AND e.status!='pending_review' AND e.is_related=0 THEN 1 ELSE 0 END) AS unrelated_count,
                SUM(CASE WHEN e.id IS NOT NULL AND e.status!='pending_review' AND e.is_related=1 AND e.is_negative=0 THEN 1 ELSE 0 END) AS no_risk_count,
                SUM(CASE WHEN e.id IS NULL THEN 1 ELSE 0 END) AS unevaluated_count
            FROM raw_contents c
            LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
            WHERE c.run_id IN ({placeholders})
            GROUP BY c.run_id
            """,
            run_ids,
        ).fetchall()
    return {int(row["run_id"]): {key: int(row[key] or 0) for key in row.keys()} for row in rows}


def _lead_count_summary(row: dict[str, int]) -> dict[str, int]:
    return {
        "lead_total_count": int(row.get("total_count") or 0),
        "pending_review_count": int(row.get("pending_review_count") or 0),
        "negative_count": int(row.get("negative_count") or 0),
        "suspected_negative_count": int(row.get("suspected_negative_count") or 0),
        "high_count": int(row.get("high_count") or 0),
        "unrelated_count": int(row.get("unrelated_count") or 0),
        "no_risk_count": int(row.get("no_risk_count") or 0),
        "unevaluated_count": int(row.get("unevaluated_count") or 0),
        "limited_context_count": int(row.get("unevaluated_count") or 0),
    }


def _setdefault_lead_count_summary(summary: dict[str, Any]) -> None:
    for key in (
        "lead_total_count",
        "pending_review_count",
        "negative_count",
        "suspected_negative_count",
        "high_count",
        "unrelated_count",
        "no_risk_count",
        "unevaluated_count",
        "limited_context_count",
    ):
        summary.setdefault(key, 0)


def list_leads(limit: int = 100, actor: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    limit = _coerce_limit(limit)
    sql = """
        SELECT
            c.id, c.platform, c.content_id, c.job_id, c.run_id,
            COALESCE(c.law_firm_name, j.law_firm_name) AS law_firm_name,
            c.source_keyword, c.title, c.description, c.author_name,
            c.content_url, c.cover_url, c.publish_time, c.comment_count,
            c.first_seen_at, c.last_seen_at,
            r.status AS run_status,
            e.id AS evaluation_id,
            e.status AS eval_status, e.is_related, e.is_negative, e.risk_level,
            e.reason, e.evidence_quotes, e.recommended_action, e.created_at AS evaluated_at
        FROM raw_contents c
        LEFT JOIN monitor_jobs j ON j.id = c.job_id
        LEFT JOIN crawl_runs r ON r.id = c.run_id
        LEFT JOIN ai_evaluations e ON e.raw_content_id = c.id
    """
    params: list[Any] = []
    if actor:
        sql += " WHERE c.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by)=?)"
        params.extend(
            [
                _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID,
                actor.get("role"),
                _safe_int(actor.get("id")) or 0,
            ]
        )
    sql += " ORDER BY c.id DESC"
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
        apply_lead_status_fields(item)
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


def _trace_safe_api_payload(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            lower_key = str(key).lower()
            if _is_sensitive_trace_key(lower_key):
                continue
            result[key] = _trace_safe_api_payload(item)
        return result
    if isinstance(value, list):
        return [_trace_safe_api_payload(item) for item in value]
    if isinstance(value, str):
        text = _trace_safe_text(value)
        if text.lstrip().startswith("{") or text.lstrip().startswith("["):
            parsed = _json_loads(text, None)
            if parsed is not None:
                return _trace_safe_api_payload(parsed)
        return text
    return value


def _trace_safe_text(value: Any) -> str:
    text = customer_safe_text(str(value or ""))
    patterns = (
        r"(?i)\b(?:authorization|x-api-key|api[_-]?key|api key|cookie|cookies?[_-]?encrypted|password|smtp[_-]?password|token|secret|proxy[_-]?url|proxy[_-]?password|profile_path|profile_dir|server_path|local_path)\b\s*(?:[:=]\s*(?:bearer\s+)?)?[^\s,;，；\"'<>]+",
        r"(?i)['\"](?:authorization|x-api-key|api[_-]?key|api key|cookie|cookies?[_-]?encrypted|password|smtp[_-]?password|token|secret|proxy[_-]?url|proxy[_-]?password|profile_path|profile_dir|server_path|local_path)['\"]\s*:\s*['\"][^'\"]*['\"]",
    )
    for pattern in patterns:
        text = re.sub(pattern, "[REDACTED]", text)
    text = re.sub(r"(?i)\bauthorization\b\s*:\s*bearer\s+\[REDACTED\]", "[REDACTED]", text)
    text = re.sub(r"(?i)\bprofile_path\b", "[REDACTED]", text)
    text = re.sub(r"(?i)\bprofile_dir\b", "[REDACTED]", text)
    text = re.sub(r"(?i)\bserver_path\b", "[REDACTED]", text)
    text = re.sub(r"(?i)\blocal_path\b", "[REDACTED]", text)
    return text


def get_dashboard_summary(actor: dict[str, Any] | None = None) -> dict[str, Any]:
    actor_params: list[Any] = []
    job_scope = "is_internal=0"
    run_scope = "1=1"
    report_scope = "1=1"
    content_scope = "1=1"
    eval_scope = "1=1"
    latest_run_scope = "1=1"
    if actor:
        workspace_id = _safe_int(actor.get("workspace_id")) or DEFAULT_WORKSPACE_ID
        actor_id = _safe_int(actor.get("id")) or 0
        role = str(actor.get("role") or "")
        job_scope += " AND workspace_id=?"
        actor_params.append(workspace_id)
        if role != "administrator":
            job_scope += " AND created_by=?"
            actor_params.append(actor_id)
        run_scope = "r.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, r.created_by)=?)"
        report_scope = "reports.workspace_id=? AND (?='administrator' OR COALESCE(monitor_jobs.created_by, reports.created_by)=?)"
        content_scope = "c.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by)=?)"
        eval_scope = "e.workspace_id=? AND (?='administrator' OR COALESCE(j.created_by, c.created_by, e.created_by)=?)"
        latest_run_scope = run_scope
        scoped_params = [workspace_id, role, actor_id]
    else:
        scoped_params = []
    with get_conn() as conn:
        jobs_total = conn.execute(f"SELECT COUNT(*) AS n FROM monitor_jobs WHERE {job_scope}", actor_params).fetchone()["n"]
        jobs_enabled = conn.execute(f"SELECT COUNT(*) AS n FROM monitor_jobs WHERE {job_scope} AND enabled=1", actor_params).fetchone()["n"]
        runs_total = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {run_scope}
            """,
            scoped_params,
        ).fetchone()["n"]
        contents_total = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM raw_contents c
            LEFT JOIN monitor_jobs j ON j.id = c.job_id
            WHERE {content_scope}
            """,
            scoped_params,
        ).fetchone()["n"]
        reports_total = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM reports
            LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
            WHERE {report_scope}
            """,
            scoped_params,
        ).fetchone()["n"]
        pending_review = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM ai_evaluations e
            LEFT JOIN raw_contents c ON c.id = e.raw_content_id
            LEFT JOIN monitor_jobs j ON j.id = c.job_id
            WHERE {eval_scope} AND e.status='pending_review'
            """,
            scoped_params,
        ).fetchone()["n"]
        negative_total = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM ai_evaluations e
            LEFT JOIN raw_contents c ON c.id = e.raw_content_id
            LEFT JOIN monitor_jobs j ON j.id = c.job_id
            WHERE {eval_scope} AND e.is_related=1 AND e.is_negative=1
            """,
            scoped_params,
        ).fetchone()["n"]
        high_total = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM ai_evaluations e
            LEFT JOIN raw_contents c ON c.id = e.raw_content_id
            LEFT JOIN monitor_jobs j ON j.id = c.job_id
            WHERE {eval_scope} AND e.is_related=1 AND e.is_negative=1 AND e.risk_level='high'
            """,
            scoped_params,
        ).fetchone()["n"]
        if actor and actor.get("role") != "administrator":
            social_total = proxy_total = ai_profiles_total = login_sessions_total = 0
        else:
            social_total = conn.execute("SELECT COUNT(*) AS n FROM social_accounts WHERE COALESCE(is_draft, 0)=0").fetchone()["n"]
            proxy_total = conn.execute("SELECT COUNT(*) AS n FROM proxy_profiles").fetchone()["n"]
            ai_profiles_total = conn.execute("SELECT COUNT(*) AS n FROM ai_key_profiles").fetchone()["n"]
            login_sessions_total = conn.execute("SELECT COUNT(*) AS n FROM login_sessions").fetchone()["n"]
        running_runs = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {run_scope} AND r.status='running'
            """,
            scoped_params,
        ).fetchone()["n"]
        today_prefix = datetime.now(timezone.utc).date().isoformat()
        runs_today = conn.execute(
            f"""
            SELECT COUNT(*) AS n FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {run_scope} AND substr(COALESCE(r.started_at, ''), 1, 10)=?
            """,
            [*scoped_params, today_prefix],
        ).fetchone()["n"]
        email_rows = conn.execute(
            f"""
            SELECT reports.email_status, COUNT(*) AS n FROM reports
            LEFT JOIN monitor_jobs ON monitor_jobs.id = reports.job_id
            WHERE {report_scope}
            GROUP BY reports.email_status
            """,
            scoped_params,
        ).fetchall()
        latest_runs = conn.execute(
            f"""
            SELECT r.status, r.summary, r.started_at, r.finished_at FROM crawl_runs r
            LEFT JOIN monitor_jobs j ON j.id = r.job_id
            WHERE {latest_run_scope}
            ORDER BY r.id DESC LIMIT 20
            """,
            scoped_params,
        ).fetchall()
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
    email_status_counts = {str(row["email_status"] or "pending"): int(row["n"] or 0) for row in email_rows}
    sent_statuses = {"sent", "success", "delivered"}
    failed_statuses = {"failed", "error"}
    email_sent = sum(count for status, count in email_status_counts.items() if status in sent_statuses)
    email_failed = sum(count for status, count in email_status_counts.items() if status in failed_statuses)
    email_unsent = max(0, int(reports_total or 0) - email_sent - email_failed)
    jobs_total_int = int(jobs_total or 0)
    jobs_enabled_int = int(jobs_enabled or 0)
    runs_total_int = int(runs_total or 0)
    reports_total_int = int(reports_total or 0)
    contents_total_int = int(contents_total or 0)
    pending_review_int = int(pending_review or 0)
    negative_total_int = int(negative_total or 0)
    high_total_int = int(high_total or 0)
    social_total_int = int(social_total or 0)
    proxy_total_int = int(proxy_total or 0)
    ai_profiles_total_int = int(ai_profiles_total or 0)
    login_sessions_total_int = int(login_sessions_total or 0)
    is_admin_view = not actor or actor.get("role") == "administrator"
    if is_admin_view:
        resource_health = {
            "scope": "workspace",
            "status": "ready" if social_total_int and proxy_total_int and ai_profiles_total_int else "needs_attention",
            "social_accounts_total": social_total_int,
            "proxy_profiles_total": proxy_total_int,
            "ai_profiles_total": ai_profiles_total_int,
            "login_sessions_total": login_sessions_total_int,
            "signals": [
                {
                    "key": "account_pool",
                    "label": "平台账号",
                    "status": "ready" if social_total_int else "empty",
                    "count": social_total_int,
                },
                {
                    "key": "proxy_pool",
                    "label": "代理资源",
                    "status": "ready" if proxy_total_int else "empty",
                    "count": proxy_total_int,
                },
                {
                    "key": "ai_access",
                    "label": "AI 接入",
                    "status": "ready" if ai_profiles_total_int else "empty",
                    "count": ai_profiles_total_int,
                },
                {
                    "key": "login_sessions",
                    "label": "登录会话",
                    "status": "ready" if login_sessions_total_int else "empty",
                    "count": login_sessions_total_int,
                },
            ],
        }
    else:
        resource_health = {
            "scope": "business_safe",
            "status": "available",
            "signals": [
                {
                    "key": "resource_supply",
                    "label": "采集资源",
                    "status": "available",
                    "note": "资源由管理员维护",
                }
            ],
        }
    operations_home = {
        "last_updated_at": utc_now(),
        "scope": "workspace" if is_admin_view else "own",
        "task_health": {
            "total": jobs_total_int,
            "active": jobs_enabled_int,
            "paused": max(0, jobs_total_int - jobs_enabled_int),
            "needs_attention": int(failed_runs + skipped_runs + email_failed + pending_review_int),
        },
        "run_activity": {
            "total": runs_total_int,
            "today": int(runs_today or 0),
            "running": int(running_runs or 0),
            "failed_recent": failed_runs,
            "skipped_recent": skipped_runs,
            "platform_counts_recent": platform_counts,
        },
        "report_activity": {
            "total": reports_total_int,
            "generated": reports_total_int,
            "manual_review": pending_review_int,
            "email_failed": email_failed,
            "email_unsent": email_unsent,
        },
        "email_delivery": {
            "source": "reports.email_status",
            "total": reports_total_int,
            "sent": email_sent,
            "failed": email_failed,
            "unsent": email_unsent,
            "history_available": False,
            "history_note": "邮件交付历史将在报告中心交付历史阶段展示",
            "status_counts": email_status_counts,
        },
        "lead_metrics": {
            "contents_total": contents_total_int,
            "suspected_negative": negative_total_int,
            "high_risk": high_total_int,
            "pending_review": pending_review_int,
            "trend_available": False,
        },
        "resource_health": resource_health,
    }
    return {
        "jobs_total": jobs_total_int,
        "jobs_enabled": jobs_enabled_int,
        "runs_total": runs_total_int,
        "reports_total": reports_total_int,
        "contents_total": contents_total_int,
        "pending_review": pending_review_int,
        "negative_total": negative_total_int,
        "high_total": high_total_int,
        "failed_runs_recent": failed_runs,
        "skipped_runs_recent": skipped_runs,
        "platform_counts_recent": platform_counts,
        "social_accounts_total": social_total_int,
        "proxy_profiles_total": proxy_total_int,
        "ai_profiles_total": ai_profiles_total_int,
        "login_sessions_total": login_sessions_total_int,
        "operations_home": operations_home,
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
    validate_email_template_report_body(html_template)
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


def render_email_template_preview(payload: dict[str, Any]) -> dict[str, Any]:
    subject = payload.get("subject_template") or DEFAULT_EMAIL_SUBJECT_TEMPLATE
    html_template = payload.get("html_template") or ""
    has_body_placeholder = email_template_has_report_body_placeholder(html_template)
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
    preview_template = html_template or _default_email_preview_html()
    if html_template.strip() and not has_body_placeholder:
        preview_template = html_template + "\n{report_html}"
    return {
        "subject": _safe_format(subject, sample),
        "html": _safe_format(preview_template, sample),
        "sample_data_note": "预览使用样例数据；真实发送会使用对应运行生成的报告 HTML。",
        "body_guardrail": (
            "正文占位符已存在，真实发送会插入系统生成的报告正文。"
            if has_body_placeholder or not html_template.strip()
            else "HTML 模板缺少 {report_html} 或 {report_body}，保存会被阻止；预览已临时追加样例报告正文。"
        ),
        "has_report_body_placeholder": has_body_placeholder or not html_template.strip(),
    }


def _row_to_email_template(row: dict[str, Any]) -> dict[str, Any]:
    row["is_active"] = bool(row.get("is_active"))
    row["has_report_body_placeholder"] = email_template_has_report_body_placeholder(row.get("html_template"))
    return row


def email_template_has_report_body_placeholder(html_template: Any) -> bool:
    value = str(html_template or "")
    return any(placeholder in value for placeholder in REPORT_BODY_PLACEHOLDERS)


def validate_email_template_report_body(html_template: Any) -> None:
    value = str(html_template or "")
    if value.strip() and not email_template_has_report_body_placeholder(value):
        raise ValueError("HTML 模板必须包含 {report_html} 或 {report_body}，否则真实邮件会缺少报告正文")


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
    profile_key = (payload.get("profile_key") or "").strip()
    if account_id and not profile_key:
        with get_conn() as conn:
            row = conn.execute("SELECT workspace_id, profile_key FROM social_accounts WHERE id=?", (account_id,)).fetchone()
        if row and row["profile_key"]:
            profile_key = str(row["profile_key"])
        else:
            profile_key = _default_account_profile_key(_safe_int(row["workspace_id"]) if row else DEFAULT_WORKSPACE_ID, platform, account_id)
    profile_path = ""
    if profile_key:
        profile_path = str(resolve_account_profile_path(profile_key))
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
        profile_key,
        profile_path,
        proxy_id,
        is_draft,
        payload.get("notes") or "",
        payload.get("last_error") or "",
        now,
    )
    with get_conn() as conn:
        _ensure_unique_account_profile(conn, profile_key, account_id)
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
                    profile_key=?, profile_path=?, proxy_id=?, is_draft=?, notes=?, last_error=?, updated_at=? WHERE id=?
                """,
                (*values, account_id),
            )
            target_id = account_id
        else:
            cur = conn.execute(
                """
                INSERT INTO social_accounts (
                    name, platform, login_type, cookies_encrypted, status, profile_key, profile_path, proxy_id, is_draft, notes,
                    last_error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*values[:-1], now, now),
            )
            target_id = int(cur.lastrowid)
            if not profile_key:
                profile_key = _default_account_profile_key(DEFAULT_WORKSPACE_ID, platform, target_id)
                profile_path = str(resolve_account_profile_path(profile_key))
                conn.execute(
                    "UPDATE social_accounts SET profile_key=?, profile_path=?, updated_at=? WHERE id=?",
                    (profile_key, profile_path, now, target_id),
                )
            _generate_new_social_account_identity(
                conn,
                account_id=target_id,
                workspace_id=DEFAULT_WORKSPACE_ID,
                platform=platform,
                proxy_id=proxy_id,
                proxy_region_snapshot=str(payload.get("proxy_region_snapshot") or "CN_MAINLAND"),
                template_family=str(payload.get("identity_template_family") or "auto"),
                updated_at=now,
            )
    return get_social_account(target_id) or {}


def _generate_new_social_account_identity(
    conn: sqlite3.Connection,
    *,
    account_id: int,
    workspace_id: int,
    platform: str,
    proxy_id: int | None,
    proxy_region_snapshot: str,
    template_family: str,
    updated_at: str,
) -> None:
    generated = generate_account_identity(
        workspace_id=workspace_id,
        platform=platform,
        account_id=account_id,
        proxy_region_snapshot=proxy_region_snapshot,
        template_family=template_family,
    )
    bound_proxy_exists = proxy_id is None or conn.execute(
        "SELECT 1 FROM proxy_profiles WHERE id=?",
        (proxy_id,),
    ).fetchone() is not None
    validate_account_identity(
        {
            **generated,
            "id": account_id,
            "workspace_id": workspace_id,
            "platform": platform,
            "proxy_id": proxy_id,
            "identity_state": "generated",
            "requires_relogin": False,
        },
        bound_proxy_exists=bound_proxy_exists,
    )
    conn.execute(
        """
        UPDATE social_accounts SET
            environment_region=?, browser_platform=?, identity_template=?, fingerprint_seed=?,
            user_agent=?, timezone=?, locale=?, accept_language=?, screen_width=?, screen_height=?,
            viewport_width=?, viewport_height=?, device_scale_factor=?, is_mobile=?, has_touch=?,
            identity_generator_name=?, identity_generator_version=?, identity_environment_version=?,
            proxy_region_snapshot=?, identity_state='generated', updated_at=?
        WHERE id=?
        """,
        (
            generated["environment_region"],
            generated["browser_platform"],
            generated["identity_template"],
            generated["fingerprint_seed"],
            generated["user_agent"],
            generated["timezone"],
            generated["locale"],
            generated["accept_language"],
            generated["screen_width"],
            generated["screen_height"],
            generated["viewport_width"],
            generated["viewport_height"],
            generated["device_scale_factor"],
            1 if generated["is_mobile"] else 0,
            1 if generated["has_touch"] else 0,
            generated["identity_generator_name"],
            generated["identity_generator_version"],
            generated["identity_environment_version"],
            generated["proxy_region_snapshot"],
            updated_at,
            account_id,
        ),
    )


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
        "profile_key": account.get("profile_key") or "",
        "profile_path": account.get("profile_path") or "",
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


def _ensure_unique_account_profile(conn: sqlite3.Connection, profile_key: str, account_id: int | None = None) -> None:
    profile_key = str(profile_key or "").strip()
    if not profile_key:
        return
    params: list[Any] = [profile_key]
    sql = "SELECT id FROM social_accounts WHERE lower(profile_key)=lower(?)"
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


def _default_account_profile_key(workspace_id: int | None, platform: str, account_id: int | None) -> str:
    return default_account_profile_key(workspace_id or DEFAULT_WORKSPACE_ID, platform, account_id)


def delete_social_account(account_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM social_accounts WHERE id=?", (account_id,))


def update_social_account_login_state(account_id: int | None, status: str, message: str = "") -> dict[str, Any] | None:
    if not account_id:
        return None
    now = utc_now()
    status = normalize_login_state(status)
    if status == LOGIN_STATE_SUCCESS:
        account_status = "active"
        last_error = ""
        last_used_at = now
    elif status in {LOGIN_STATE_NEEDS_VERIFICATION, LOGIN_STATE_QRCODE_FAILED, LOGIN_STATE_TIMEOUT, LOGIN_STATE_PLATFORM_ERROR}:
        account_status = "limited" if status == LOGIN_STATE_NEEDS_VERIFICATION else "standby"
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
    profile_key = (payload.get("profile_key") or "").strip()
    account = None
    if account_id and not profile_key:
        account = get_social_account(account_id, masked=False)
        profile_key = str((account or {}).get("profile_key") or "")
    profile_path = ""
    if profile_key:
        profile_path = str(resolve_account_profile_path(profile_key))
    message = payload.get("message") or (
        "正在创建平台登录会话；如二维码或验证状态无法回传，可使用网页登录窗口人工处理。"
    )
    now = utc_now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO login_sessions (
                platform, account_id, status, login_url, qr_image, profile_key, profile_path,
                message, created_at, updated_at, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                account_id,
                normalize_login_state(payload.get("status") or LOGIN_STATE_PREPARING),
                login_url,
                payload.get("qr_image") or "",
                profile_key,
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


def expire_login_sessions_for_account(account_id: int | None, platform: str, profile_path: str = "", profile_key: str = "") -> list[int]:
    _validate_platform(platform)
    pending_statuses = tuple(PENDING_LOGIN_STATES | {"waiting_qrcode", "waiting_verification", "waiting_manual_browser", "scanned"})
    clauses = [f"platform=?", f"status IN ({','.join('?' for _ in pending_statuses)})"]
    params: list[Any] = [platform]
    params.extend(pending_statuses)
    if account_id:
        clauses.append("account_id=?")
        params.append(account_id)
    elif profile_key:
        clauses.append("profile_key=?")
        params.append(profile_key)
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
                f"UPDATE login_sessions SET status=?, message=?, updated_at=? WHERE id IN ({placeholders})",
                [LOGIN_STATE_TIMEOUT, "已被新的登录会话替换", now, *ids],
            )
    return ids


def update_login_session_status(session_id: int, status: str, message: str = "", qr_image: str = "") -> dict[str, Any]:
    status = normalize_login_state(status)
    allowed = STRUCTURED_LOGIN_STATES | {
        LOGIN_STATE_WAITING_QRCODE,
        LOGIN_STATE_WAITING_SCAN,
        LOGIN_STATE_WAITING_CONFIRM,
    }
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
    row["requires_relogin"] = bool(row.get("requires_relogin"))
    row["is_mobile"] = bool(row.get("is_mobile"))
    row["has_touch"] = bool(row.get("has_touch"))
    try:
        profile_env = account_profile_environment(row)
    except ValueError:
        profile_env = {"profile_key": row.get("profile_key") or "", "runtime_path": "", "profile_path": "", "profile_configured": False}
    row["profile_key"] = profile_env.get("profile_key") or row.get("profile_key") or ""
    row["profile_configured"] = bool(profile_env.get("profile_configured"))
    row["profile_runtime_path"] = "" if masked else str(profile_env.get("runtime_path") or "")
    row["profile_path"] = "" if masked else str(profile_env.get("profile_path") or "")
    if masked:
        row["platform_avatar_url"] = customer_safe_url(row.get("platform_avatar_url"))
        row["platform_home_url"] = customer_safe_url(row.get("platform_home_url"))
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
