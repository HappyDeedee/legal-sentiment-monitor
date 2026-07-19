from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "phase_5_1_acceptance_v1"

ENVIRONMENT_TYPES = {"docker", "systemd"}
PLATFORMS = {"dy", "ks", "xhs"}
BROWSER_SOURCES = {"explicit", "playwright_bundled"}
CRAWL_TRIGGER_SOURCES = {"manual", "scheduler", "cli_manual"}
REDACTION_SURFACES = {
    "safe_runtime_results",
    "account_api",
    "run_summaries",
    "logs",
    "evidence_file",
}

PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "replace",
    "replace_me",
    "pending",
    "not_yet_validated",
    "account-x",
    "run-y",
}

REQUIRED_TRUE_FIELDS = [
    ("environment", "service_started"),
    ("environment", "web_admin_login"),
    ("environment", "server_browser_owned"),
    ("environment", "persistent_data_root"),
    ("environment", "persistent_profile_root"),
    ("environment", "local_window_disabled"),
    ("environment", "connect_existing_disabled"),
    ("environment", "restart_completed"),
    ("accounts", "qr", "acceptance_labeled"),
    ("accounts", "cookie", "acceptance_labeled"),
    ("restart", "profile_login_survived"),
    ("proxy", "account_bound"),
    ("proxy", "browser_region_proof_passed"),
    ("proxy", "no_task_or_default_override"),
    ("runtime_authority", "safe_results_collected"),
    ("runtime_authority", "browser_source_managed"),
    ("runtime_authority", "profile_reference_matched"),
    ("runtime_authority", "proxy_policy_account_bound"),
    ("runtime_authority", "provider_mode_launch_owned"),
    ("runtime_authority", "mismatch_evidence_empty"),
    ("runtime_authority", "fallback_used_false"),
    ("runtime_authority", "child_result_matched_before_ingest"),
    ("bounds", "serial_execution"),
    ("bounds", "all_terminal"),
    ("redaction", "no_sensitive_values_found"),
    ("redaction", "filled_evidence_outside_git"),
    ("attestations", "operator_observed"),
    ("attestations", "reviewer_cross_checked"),
]

REQUIRED_TEXT_FIELDS = [
    ("baseline", "commit"),
    ("baseline", "environment_type"),
    ("baseline", "environment_reference"),
    ("baseline", "operator_reference"),
    ("baseline", "reviewer_reference"),
    ("baseline", "template_created_at"),
    ("baseline", "run_window_started_at"),
    ("baseline", "run_window_ended_at"),
    ("baseline", "checked_at"),
    ("environment", "browser_source"),
    ("environment", "browser_family"),
    ("environment", "browser_version"),
    ("accounts", "qr", "platform"),
    ("accounts", "qr", "account_reference"),
    ("accounts", "cookie", "platform"),
    ("accounts", "cookie", "account_reference"),
    ("restart", "restarted_at"),
    ("restart", "lock_timestamp_before"),
    ("restart", "lock_timestamp_after"),
    ("restart", "environment_digest_before"),
    ("restart", "environment_digest_after"),
    ("proxy", "region_reference"),
    ("redaction", "evidence_reference"),
    ("attestations", "notes"),
]

SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "browser_executable_path",
    "browser_process_argv",
    "command",
    "command_line",
    "cookie",
    "cookie_header",
    "cookie_value",
    "cookies",
    "environment_dump",
    "internal_plan",
    "password",
    "profile_path",
    "proxy_password",
    "proxy_url",
    "proxy_username",
    "raw_snapshot",
    "secret",
    "token",
}

SENSITIVE_VALUE_PATTERNS = [
    ("api_key", re.compile(r"\b(?:sk|sk-proj|sk-ant|rk)-[A-Za-z0-9_-]{12,}\b")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{10,}", re.IGNORECASE)),
    ("proxy_credentials", re.compile(r"\bhttps?://[^/\s:@]+:[^/\s:@]+@[^/\s]+", re.IGNORECASE)),
    ("network_url", re.compile(r"(?:https?|socks5?|wss?|file)://[^\s<>\"']+", re.IGNORECASE)),
    ("windows_local_path", re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/](?:[^\\/\r\n]+[\\/])*[^\\/\r\n]+")),
    ("windows_unc_path", re.compile(r"\\\\[^\\/\s]+[\\/](?:[^\\/\r\n]+[\\/])*[^\\/\r\n]+")),
    ("windows_unc_forward_path", re.compile(r"//[^/\s]+/(?:[^/\s]+/)*[^/\s]+")),
    ("linux_local_path", re.compile(r"(?<![\w/])/(?!/)(?:[^/\s]+/)*[^/\s]+")),
    ("cookie_header", re.compile(r"(?i)\bcookie\s*[:=]\s*[^<\s][^\r\n]{6,}")),
    ("password_assignment", re.compile(r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*[^<\s][^\s,;]{3,}")),
    ("internal_plan", re.compile(r"MONITOR_BROWSER_ENVIRONMENT_(?:PLAN|RESULT_PATH)", re.IGNORECASE)),
    ("browser_command", re.compile(r"--(?:user-data-dir|proxy-server|remote-debugging-port)(?:=|\s)", re.IGNORECASE)),
]

_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
_VERSION_RE = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def build_template(now: datetime | None = None) -> dict[str, Any]:
    created_at = _as_utc(now or datetime.now(timezone.utc)).isoformat()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "incomplete",
        "baseline": {
            "commit": "",
            "environment_type": "",
            "environment_reference": "",
            "operator_reference": "",
            "reviewer_reference": "",
            "template_created_at": created_at,
            "run_window_started_at": "",
            "run_window_ended_at": "",
            "checked_at": "",
        },
        "environment": {
            "service_started": False,
            "web_admin_login": False,
            "server_browser_owned": False,
            "browser_source": "",
            "browser_family": "",
            "browser_version": "",
            "persistent_data_root": False,
            "persistent_profile_root": False,
            "local_window_disabled": False,
            "connect_existing_disabled": False,
            "restart_completed": False,
        },
        "accounts": {
            "qr": {"platform": "", "account_reference": "", "acceptance_labeled": False},
            "cookie": {"platform": "", "account_reference": "", "acceptance_labeled": False},
        },
        "login_actions": [
            _action_template("qr_login", "qrcode_login", "persistent_launch"),
            _action_template(
                "cookie_validation",
                "cookie_validation",
                "ephemeral_cookie_validation",
            ),
            _action_template("login_check", "profile_validation", "persistent_launch"),
            _action_template("login_check", "profile_validation", "persistent_launch"),
        ],
        "restart": {
            "restarted_at": "",
            "lock_timestamp_before": "",
            "lock_timestamp_after": "",
            "environment_digest_before": "",
            "environment_digest_after": "",
            "profile_login_survived": False,
        },
        "proxy": {
            "account_bound": False,
            "region_reference": "",
            "browser_region_proof_passed": False,
            "no_task_or_default_override": False,
        },
        "crawl_actions": [
            _crawl_action_template("manual"),
            _crawl_action_template("scheduler"),
            _crawl_action_template("cli_manual"),
        ],
        "runtime_authority": {
            "safe_results_collected": False,
            "browser_source_managed": False,
            "profile_reference_matched": False,
            "proxy_policy_account_bound": False,
            "provider_mode_launch_owned": False,
            "mismatch_evidence_empty": False,
            "fallback_used_false": False,
            "child_result_matched_before_ingest": False,
        },
        "bounds": {
            "serial_execution": False,
            "all_terminal": False,
            "max_pages": 1,
            "max_accepted_items": 10,
            "timeout_seconds": 300,
        },
        "redaction": {
            "checked_surfaces": [],
            "no_sensitive_values_found": False,
            "filled_evidence_outside_git": False,
            "evidence_reference": "",
        },
        "attestations": {
            "operator_observed": False,
            "reviewer_cross_checked": False,
            "notes": "",
        },
    }


def _action_template(action: str, trigger_source: str, provider_mode: str) -> dict[str, Any]:
    return {
        "action": action,
        "trigger_source": trigger_source,
        "account_reference": "",
        "runtime_reference": "",
        "resolution_reference": "",
        "attempt_reference": "",
        "environment_digest": "",
        "observed_at": "",
        "provider_mode": provider_mode,
        "browser_source": "",
        "proxy_effect": "",
        "fallback_used": True,
        "mismatch_count": -1,
    }


def _crawl_action_template(trigger_source: str) -> dict[str, Any]:
    item = _action_template("crawl", trigger_source, "cdp_launch")
    item.update(
        {
            "run_reference": "",
            "terminal_status": "",
            "pages": 0,
            "accepted_items": 0,
            "duration_seconds": 0,
        }
    )
    return item


def validate_evidence(
    payload: dict[str, Any],
    *,
    expected_commit: str | None = None,
    now: datetime | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(payload, dict):
        return [ValidationIssue("shape", "$", "evidence must be a JSON object")]
    if payload.get("schema_version") != SCHEMA_VERSION:
        issues.append(ValidationIssue("schema_version", "schema_version", f"must be {SCHEMA_VERSION}"))
    if payload.get("status") != "passed":
        issues.append(ValidationIssue("status", "status", "must be passed before Phase 5.1 can close"))

    for path in REQUIRED_TRUE_FIELDS:
        if _get_path(payload, path) is not True:
            issues.append(ValidationIssue("required_true", ".".join(path), "must be true"))
    for path in REQUIRED_TEXT_FIELDS:
        value = _get_path(payload, path)
        if not isinstance(value, str) or _is_placeholder(value):
            issues.append(ValidationIssue("required_text", ".".join(path), "must contain a non-placeholder redacted value"))

    _validate_enums(payload, issues, expected_commit=expected_commit)
    login_actions = _validate_actions(payload.get("login_actions"), "login_actions", issues, crawl=False)
    crawl_actions = _validate_actions(payload.get("crawl_actions"), "crawl_actions", issues, crawl=True)
    _validate_action_matrix(payload, login_actions, crawl_actions, issues)
    _validate_uniqueness(login_actions + crawl_actions, issues)
    _validate_chronology(payload, login_actions, crawl_actions, issues, now=now)
    _validate_restart_and_digest(payload, login_actions, crawl_actions, issues)
    _validate_bounds(payload, crawl_actions, issues)
    _validate_redaction_surfaces(payload, issues)
    _validate_sensitive_content(payload, issues)
    return _dedupe_issues(issues)


def _validate_enums(
    payload: dict[str, Any],
    issues: list[ValidationIssue],
    *,
    expected_commit: str | None,
) -> None:
    commit = _get_path(payload, ("baseline", "commit"))
    if not isinstance(commit, str) or not _COMMIT_RE.fullmatch(commit):
        issues.append(ValidationIssue("baseline", "baseline.commit", "must be a full lowercase 40-character Git commit"))
    if expected_commit is not None and commit != expected_commit:
        issues.append(ValidationIssue("baseline", "baseline.commit", "must equal the expected deployed commit"))
    if _get_path(payload, ("baseline", "environment_type")) not in ENVIRONMENT_TYPES:
        issues.append(ValidationIssue("enum", "baseline.environment_type", "must be docker or systemd"))
    if _get_path(payload, ("environment", "browser_source")) not in BROWSER_SOURCES:
        issues.append(ValidationIssue("enum", "environment.browser_source", "must be a managed server browser source"))
    if _get_path(payload, ("environment", "browser_family")) != "chromium":
        issues.append(ValidationIssue("enum", "environment.browser_family", "must be chromium"))
    browser_version = _get_path(payload, ("environment", "browser_version"))
    if not isinstance(browser_version, str) or not _VERSION_RE.fullmatch(browser_version):
        issues.append(ValidationIssue("version", "environment.browser_version", "must be a concrete browser version"))
    for kind in ("qr", "cookie"):
        if _get_path(payload, ("accounts", kind, "platform")) not in PLATFORMS:
            issues.append(ValidationIssue("enum", f"accounts.{kind}.platform", "must be dy, ks, or xhs"))


def _validate_actions(
    value: Any,
    path: str,
    issues: list[ValidationIssue],
    *,
    crawl: bool,
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        issues.append(ValidationIssue("shape", path, "must be a list"))
        return []
    expected_count = 3 if crawl else 4
    if len(value) != expected_count:
        issues.append(ValidationIssue("action_count", path, f"must contain exactly {expected_count} actions"))
    result: list[dict[str, Any]] = []
    common_text = {
        "action",
        "trigger_source",
        "account_reference",
        "runtime_reference",
        "resolution_reference",
        "attempt_reference",
        "environment_digest",
        "observed_at",
        "provider_mode",
        "browser_source",
        "proxy_effect",
    }
    for index, item in enumerate(value):
        item_path = f"{path}.{index}"
        if not isinstance(item, dict):
            issues.append(ValidationIssue("shape", item_path, "must be an object"))
            continue
        result.append(item)
        for field_name in common_text:
            field_value = item.get(field_name)
            if not isinstance(field_value, str) or _is_placeholder(field_value):
                issues.append(ValidationIssue("required_text", f"{item_path}.{field_name}", "must contain a non-placeholder redacted value"))
        if not isinstance(item.get("environment_digest"), str) or not _DIGEST_RE.fullmatch(item.get("environment_digest", "")):
            issues.append(ValidationIssue("digest", f"{item_path}.environment_digest", "must be sha256 followed by 64 lowercase hex characters"))
        if item.get("browser_source") not in BROWSER_SOURCES:
            issues.append(ValidationIssue("enum", f"{item_path}.browser_source", "must be a managed browser source"))
        if item.get("proxy_effect") != "passed":
            issues.append(ValidationIssue("proxy_effect", f"{item_path}.proxy_effect", "must be passed"))
        if item.get("fallback_used") is not False:
            issues.append(ValidationIssue("fallback", f"{item_path}.fallback_used", "must be false"))
        if type(item.get("mismatch_count")) is not int or item.get("mismatch_count") != 0:
            issues.append(ValidationIssue("mismatch", f"{item_path}.mismatch_count", "must be integer zero"))
        if crawl:
            for field_name in ("run_reference", "terminal_status"):
                field_value = item.get(field_name)
                if not isinstance(field_value, str) or _is_placeholder(field_value):
                    issues.append(ValidationIssue("required_text", f"{item_path}.{field_name}", "must contain a non-placeholder redacted value"))
            if item.get("action") != "crawl":
                issues.append(ValidationIssue("action", f"{item_path}.action", "must be crawl"))
            if item.get("provider_mode") != "cdp_launch":
                issues.append(ValidationIssue("provider_mode", f"{item_path}.provider_mode", "must be cdp_launch"))
            if item.get("terminal_status") != "completed":
                issues.append(ValidationIssue("terminal_status", f"{item_path}.terminal_status", "must be completed"))
    return result


def _validate_action_matrix(
    payload: dict[str, Any],
    login_actions: list[dict[str, Any]],
    crawl_actions: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    expected_login = [
        ("qr_login", "qrcode_login", "persistent_launch"),
        ("cookie_validation", "cookie_validation", "ephemeral_cookie_validation"),
        ("login_check", "profile_validation", "persistent_launch"),
        ("login_check", "profile_validation", "persistent_launch"),
    ]
    actual_login = sorted(
        (str(item.get("action")), str(item.get("trigger_source")), str(item.get("provider_mode")))
        for item in login_actions
    )
    if actual_login != sorted(expected_login):
        issues.append(ValidationIssue("login_actions", "login_actions", "must contain QR, Cookie, and two Profile checks with exact modes"))
    trigger_sources = {item.get("trigger_source") for item in crawl_actions}
    if trigger_sources != CRAWL_TRIGGER_SOURCES:
        issues.append(ValidationIssue("trigger_sources", "crawl_actions", "must contain manual, scheduler, and cli_manual"))
    qr_reference = _get_path(payload, ("accounts", "qr", "account_reference"))
    cookie_reference = _get_path(payload, ("accounts", "cookie", "account_reference"))
    normalized_references: dict[str, Any] = {"qr": qr_reference, "cookie": cookie_reference}
    for kind, reference in normalized_references.items():
        if isinstance(reference, str):
            normalized_references[kind] = reference.strip()
            if reference != reference.strip():
                issues.append(
                    ValidationIssue(
                        "account_reference",
                        f"accounts.{kind}.account_reference",
                        "must not contain leading or trailing whitespace",
                    )
                )
    normalized_qr = normalized_references["qr"]
    normalized_cookie = normalized_references["cookie"]
    if normalized_qr == normalized_cookie and isinstance(normalized_qr, str) and not _is_placeholder(normalized_qr):
        issues.append(
            ValidationIssue(
                "account_reference",
                "accounts.cookie.account_reference",
                "Cookie validation must use a separate account fixture",
            )
        )
    for index, item in enumerate(login_actions):
        expected_reference = cookie_reference if item.get("action") == "cookie_validation" else qr_reference
        if item.get("account_reference") != expected_reference:
            issues.append(ValidationIssue("account_reference", f"login_actions.{index}.account_reference", "does not match the owning account"))
    for index, item in enumerate(crawl_actions):
        if item.get("account_reference") != qr_reference:
            issues.append(ValidationIssue("account_reference", f"crawl_actions.{index}.account_reference", "real crawls must use the QR/Profile account"))
    expected_browser_source = _get_path(payload, ("environment", "browser_source"))
    for collection_name, actions in (("login_actions", login_actions), ("crawl_actions", crawl_actions)):
        for index, item in enumerate(actions):
            if item.get("browser_source") != expected_browser_source:
                issues.append(
                    ValidationIssue(
                        "browser_source",
                        f"{collection_name}.{index}.browser_source",
                        "must match the acceptance environment browser source",
                    )
                )


def _validate_uniqueness(actions: list[dict[str, Any]], issues: list[ValidationIssue]) -> None:
    for field_name in ("runtime_reference", "resolution_reference", "attempt_reference"):
        seen: set[str] = set()
        for index, item in enumerate(actions):
            value = item.get(field_name)
            if not isinstance(value, str):
                continue
            if value in seen:
                issues.append(ValidationIssue("duplicate_reference", f"actions.{index}.{field_name}", f"duplicate {field_name}"))
            seen.add(value)


def _validate_chronology(
    payload: dict[str, Any],
    login_actions: list[dict[str, Any]],
    crawl_actions: list[dict[str, Any]],
    issues: list[ValidationIssue],
    *,
    now: datetime | None,
) -> None:
    timestamps: dict[str, datetime] = {}
    for path in (
        ("baseline", "template_created_at"),
        ("baseline", "run_window_started_at"),
        ("baseline", "run_window_ended_at"),
        ("baseline", "checked_at"),
        ("restart", "restarted_at"),
        ("restart", "lock_timestamp_before"),
        ("restart", "lock_timestamp_after"),
    ):
        parsed = _parse_datetime(_get_path(payload, path))
        if parsed is None:
            issues.append(ValidationIssue("timestamp", ".".join(path), "must be an ISO-8601 timestamp with timezone"))
        else:
            timestamps[".".join(path)] = parsed
    required = (
        "baseline.template_created_at",
        "baseline.run_window_started_at",
        "baseline.run_window_ended_at",
        "baseline.checked_at",
        "restart.restarted_at",
    )
    if all(name in timestamps for name in required):
        template_at, started_at, ended_at, checked_at, restarted_at = (timestamps[name] for name in required)
        if not template_at <= started_at <= restarted_at <= ended_at <= checked_at:
            issues.append(ValidationIssue("chronology", "restart.restarted_at", "template, run window, restart, and check timestamps are out of order"))
        for field_name in ("restart.lock_timestamp_before", "restart.lock_timestamp_after"):
            lock_at = timestamps.get(field_name)
            if lock_at is not None and not started_at <= lock_at < restarted_at:
                issues.append(
                    ValidationIssue(
                        "chronology",
                        field_name,
                        "environment lock timestamp must fall inside the run window before restart",
                    )
                )
        current = _as_utc(now or datetime.now(timezone.utc))
        if checked_at > current:
            issues.append(ValidationIssue("chronology", "baseline.checked_at", "cannot be in the future"))
        profile_checks: list[datetime] = []
        observed_actions: dict[str, list[tuple[int, dict[str, Any], datetime]]] = {
            "login_actions": [],
            "crawl_actions": [],
        }
        for collection_name, actions in (("login_actions", login_actions), ("crawl_actions", crawl_actions)):
            for index, item in enumerate(actions):
                observed = _parse_datetime(item.get("observed_at"))
                if observed is None:
                    issues.append(ValidationIssue("timestamp", f"{collection_name}.{index}.observed_at", "must be an ISO-8601 timestamp with timezone"))
                    continue
                if not started_at <= observed <= ended_at:
                    issues.append(ValidationIssue("chronology", f"{collection_name}.{index}.observed_at", "must fall inside the run window"))
                observed_actions[collection_name].append((index, item, observed))
                if collection_name == "login_actions" and item.get("action") == "login_check":
                    profile_checks.append(observed)
        if len(profile_checks) == 2 and not min(profile_checks) < restarted_at < max(profile_checks):
            issues.append(ValidationIssue("chronology", "restart.restarted_at", "restart must be between the two Profile checks"))
        for index, item, observed in observed_actions["login_actions"]:
            if item.get("action") in {"qr_login", "cookie_validation"} and observed >= restarted_at:
                issues.append(
                    ValidationIssue(
                        "chronology",
                        f"login_actions.{index}.observed_at",
                        "QR login and Cookie validation must complete before restart",
                    )
                )
        post_restart_checks = [observed for observed in profile_checks if observed > restarted_at]
        if len(post_restart_checks) == 1:
            post_restart_check = post_restart_checks[0]
            for index, _item, observed in observed_actions["crawl_actions"]:
                if observed <= post_restart_check:
                    issues.append(
                        ValidationIssue(
                            "chronology",
                            f"crawl_actions.{index}.observed_at",
                            "crawl actions must run after the post-restart Profile check",
                        )
                    )


def _validate_restart_and_digest(
    payload: dict[str, Any],
    login_actions: list[dict[str, Any]],
    crawl_actions: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    lock_before = _get_path(payload, ("restart", "lock_timestamp_before"))
    lock_after = _get_path(payload, ("restart", "lock_timestamp_after"))
    if lock_before != lock_after:
        issues.append(ValidationIssue("restart_lock", "restart.lock_timestamp_after", "must equal lock_timestamp_before"))
    digest_before = _get_path(payload, ("restart", "environment_digest_before"))
    digest_after = _get_path(payload, ("restart", "environment_digest_after"))
    for field_name, value in (("before", digest_before), ("after", digest_after)):
        if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
            issues.append(ValidationIssue("digest", f"restart.environment_digest_{field_name}", "must be a safe SHA-256 digest"))
    if digest_before != digest_after:
        issues.append(ValidationIssue("stable_digest", "restart.environment_digest_after", "must equal the pre-restart digest"))
    qr_reference = _get_path(payload, ("accounts", "qr", "account_reference"))
    qr_digests = {
        item.get("environment_digest")
        for item in login_actions + crawl_actions
        if item.get("account_reference") == qr_reference
    }
    if qr_digests != {digest_before}:
        issues.append(ValidationIssue("stable_digest", "crawl_actions", "QR/Profile actions must share the restart digest"))


def _validate_bounds(
    payload: dict[str, Any],
    crawl_actions: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    expected = {"max_pages": 1, "max_accepted_items": 10, "timeout_seconds": 300}
    for field_name, expected_value in expected.items():
        if _get_path(payload, ("bounds", field_name)) != expected_value:
            issues.append(ValidationIssue("bounds", f"bounds.{field_name}", f"must equal {expected_value}"))
    for index, item in enumerate(crawl_actions):
        values = {
            "pages": (item.get("pages"), 1, 1),
            "accepted_items": (item.get("accepted_items"), 1, 10),
            "duration_seconds": (item.get("duration_seconds"), 1, 300),
        }
        for field_name, (value, minimum, maximum) in values.items():
            if type(value) is not int or not minimum <= value <= maximum:
                issues.append(
                    ValidationIssue(
                        "bounds",
                        f"crawl_actions.{index}.{field_name}",
                        f"must be an integer between {minimum} and {maximum}",
                    )
                )


def _validate_redaction_surfaces(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    surfaces = _get_path(payload, ("redaction", "checked_surfaces"))
    if not isinstance(surfaces, list):
        issues.append(ValidationIssue("redaction_surfaces", "redaction.checked_surfaces", "must be a list"))
        return
    normalized = {str(item).strip().lower() for item in surfaces}
    missing = sorted(REDACTION_SURFACES - normalized)
    if missing:
        issues.append(ValidationIssue("redaction_surfaces", "redaction.checked_surfaces", f"missing required surfaces: {', '.join(missing)}"))


def _validate_sensitive_content(payload: dict[str, Any], issues: list[ValidationIssue]) -> None:
    for path, key in _iter_keys(payload):
        lowered = key.lower()
        if path == "$.accounts.cookie":
            continue
        if lowered in SENSITIVE_KEYS or lowered.endswith("_argv") or lowered.endswith("_path"):
            issues.append(ValidationIssue("sensitive_key", path, f"forbidden sensitive evidence key: {key}"))
    for path, value in _iter_strings(payload):
        for name, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                issues.append(ValidationIssue("sensitive_value", path, f"looks like {name}; store only redacted references"))
                break


def _get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _is_placeholder(value: str) -> bool:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered in PLACEHOLDER_VALUES:
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    return bool(re.fullmatch(r"(?i)(?:account|run|result|resolution|attempt)[-_ ]?[xy0]", stripped))


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return _as_utc(parsed)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _iter_keys(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            items.append((path, str(key)))
            items.extend(_iter_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_iter_keys(child, f"{prefix}[{index}]"))
    return items


def _iter_strings(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_iter_strings(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_iter_strings(child, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        items.append((prefix, value))
    return items


def _dedupe_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    seen: set[tuple[str, str, str]] = set()
    result: list[ValidationIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key in seen:
            continue
        seen.add(key)
        result.append(issue)
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("evidence file must contain a JSON object")
    return payload


def write_template(path: Path, now: datetime | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_template(now=now), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate redacted Phase 5.1 server-like acceptance evidence.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-template", metavar="PATH", help="Write an incomplete redacted evidence template.")
    group.add_argument("--check", metavar="PATH", help="Validate an operator-filled evidence file.")
    parser.add_argument(
        "--expected-commit",
        default="",
        help="Exact 40-character Git commit deployed for the acceptance run (required with --check).",
    )
    args = parser.parse_args(argv)

    if args.write_template:
        write_template(Path(args.write_template))
        print(json.dumps({"ok": True, "template": args.write_template}, ensure_ascii=False))
        return 0

    if not _COMMIT_RE.fullmatch(args.expected_commit):
        parser.error("--expected-commit must be the exact lowercase 40-character deployed Git commit")
    try:
        payload = load_json(Path(args.check))
    except OSError:
        issues = [ValidationIssue("input", "evidence_file", "evidence file could not be read")]
    except (json.JSONDecodeError, UnicodeError):
        issues = [ValidationIssue("invalid_json", "evidence_file", "evidence file must contain valid JSON")]
    except ValueError:
        issues = [ValidationIssue("shape", "evidence_file", "evidence file must contain a JSON object")]
    else:
        issues = validate_evidence(
            payload,
            expected_commit=args.expected_commit,
        )
    result = {
        "ok": not issues,
        "issues": [issue.as_dict() for issue in issues],
        "proof_boundary": "schema, chronology, consistency, and redaction only; external actions require operator and reviewer attestation",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
