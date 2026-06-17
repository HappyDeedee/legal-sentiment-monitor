from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "pilot_gate_c_v3"

REQUIRED_TRUE_FIELDS = [
    ("server_like_environment", "service_started"),
    ("server_like_environment", "web_ui_admin_login"),
    ("server_like_environment", "server_side_browser_used"),
    ("server_like_environment", "local_chrome_not_required"),
    ("server_like_environment", "profile_root_persistent"),
    ("real_platform_workflow", "web_qr_status_login_completed"),
    ("real_platform_workflow", "server_side_profile_persisted"),
    ("real_platform_workflow", "crawl_completed_with_server_profile"),
    ("real_platform_workflow", "report_generated"),
    ("ai_fallback", "ai_unavailable_or_failure_exercised"),
    ("ai_fallback", "pending_review_or_manual_review_recorded"),
    ("ai_fallback", "report_generated"),
    ("smtp_validation", "admin_toggle_enabled_for_validation"),
    ("smtp_validation", "real_smtp_send_succeeded"),
    ("smtp_validation", "delivery_recorded"),
    ("smtp_validation", "recipient_receipt_confirmed"),
    ("smtp_validation", "admin_toggle_disabled_after_validation"),
    ("smtp_validation", "default_paths_non_sending_confirmed"),
    ("redaction", "no_sensitive_values_found"),
    ("non_blocker_boundary", "non_blockers_confirmed"),
    ("non_blocker_boundary", "historical_mutation_not_performed"),
]

REQUIRED_TEXT_FIELDS = [
    ("real_email_toggle", "operator"),
    ("real_email_toggle", "started_at"),
    ("real_email_toggle", "ended_at"),
    ("server_like_environment", "environment_reference"),
    ("real_platform_workflow", "platform"),
    ("real_platform_workflow", "account_reference"),
    ("real_platform_workflow", "run_reference"),
    ("real_platform_workflow", "report_reference"),
    ("ai_fallback", "scenario"),
    ("ai_fallback", "evidence_reference"),
    ("smtp_validation", "recipient_reference"),
    ("smtp_validation", "delivery_log_reference"),
    ("smtp_validation", "recipient_receipt_reference"),
    ("redaction", "evidence_reference"),
]

REQUIRED_REDACTION_SURFACES = {"logs", "reports", "delivery_records", "ui_or_api"}

PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "replace",
    "replace_me",
    "pending",
    "not_yet_validated",
}

SENSITIVE_VALUE_PATTERNS = [
    ("api_key", re.compile(r"\b(?:sk|sk-proj|sk-ant|rk)-[A-Za-z0-9_-]{12,}\b")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{10,}", re.IGNORECASE)),
    ("cloud_access_key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github_token", re.compile(r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{12,}\b")),
    ("proxy_credentials", re.compile(r"\bhttps?://[^/\s:@]+:[^/\s:@]+@[^/\s]+", re.IGNORECASE)),
    ("windows_local_path", re.compile(r"\b[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\?)+")),
    ("linux_local_path", re.compile(r"(?<!https:)\b/(?:app|data|home|opt|root|tmp|var)(?:/[A-Za-z0-9_.@ -]+)+")),
    ("env_or_deployment_file", re.compile(r"(?i)(?:^|[\\/\s])(?:\.env|monitor\.yaml)(?:$|[\\/\s])")),
    ("cookie_header", re.compile(r"(?i)\bcookie\s*[:=]\s*[^<\s][^\r\n]{6,}")),
    ("password_assignment", re.compile(r"(?i)\b(?:smtp[_-]?password|password|passwd|api[_-]?key|secret|token)\s*[:=]\s*[^<\s][^\s,;]{3,}")),
    ("provider_endpoint", re.compile(r"(?i)https?://(?:api\.openai\.com|dashscope\.aliyuncs\.com|api\.anthropic\.com|generativelanguage\.googleapis\.com)[^\s]*")),
]

SENSITIVE_KEY_PARTS = {
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "cookie",
    "local_path",
    "password",
    "profile_path",
    "proxy_url",
    "secret",
    "smtp_password",
    "token",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def build_template() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "incomplete",
        "real_email_toggle": {
            "operator": "",
            "started_at": "",
            "ended_at": "",
            "notes": "Fill this file only with redacted references after the real Pilot Gate C run.",
        },
        "server_like_environment": {
            "environment_reference": "",
            "service_started": False,
            "web_ui_admin_login": False,
            "server_side_browser_used": False,
            "local_chrome_not_required": False,
            "profile_root_persistent": False,
        },
        "real_platform_workflow": {
            "platform": "",
            "account_reference": "",
            "web_qr_status_login_completed": False,
            "server_side_profile_persisted": False,
            "crawl_completed_with_server_profile": False,
            "run_reference": "",
            "report_reference": "",
            "report_generated": False,
        },
        "ai_fallback": {
            "scenario": "",
            "ai_unavailable_or_failure_exercised": False,
            "pending_review_or_manual_review_recorded": False,
            "report_generated": False,
            "evidence_reference": "",
        },
        "smtp_validation": {
            "recipient_reference": "",
            "delivery_log_reference": "",
            "recipient_receipt_reference": "",
            "admin_toggle_enabled_for_validation": False,
            "real_smtp_send_succeeded": False,
            "delivery_recorded": False,
            "recipient_receipt_confirmed": False,
            "admin_toggle_disabled_after_validation": False,
            "default_paths_non_sending_confirmed": False,
        },
        "redaction": {
            "checked_surfaces": [],
            "no_sensitive_values_found": False,
            "evidence_reference": "",
            "notes": "",
        },
        "non_blocker_boundary": {
            "non_blockers_confirmed": False,
            "historical_mutation_not_performed": False,
            "notes": "Phase 21, CR-038, Phase 19B-D, Phase 20, CR-037, run 8317 repair, and orphan evidence cleanup are outside the first-pilot blocker set unless a new accepted P0 regression changes that boundary.",
        },
    }


def validate_evidence(payload: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if payload.get("schema_version") != SCHEMA_VERSION:
        issues.append(ValidationIssue("schema_version", "schema_version", f"must be {SCHEMA_VERSION}"))
    if payload.get("status") != "passed":
        issues.append(ValidationIssue("status", "status", "must be passed before CR-041 Pilot Gate C can close"))

    for path in REQUIRED_TRUE_FIELDS:
        value = _get_path(payload, path)
        if value is not True:
            issues.append(ValidationIssue("required_true", ".".join(path), "must be true"))

    for path in REQUIRED_TEXT_FIELDS:
        value = _get_path(payload, path)
        if not isinstance(value, str) or _is_placeholder(value):
            issues.append(ValidationIssue("required_text", ".".join(path), "must contain a non-placeholder redacted reference"))

    surfaces = _get_path(payload, ("redaction", "checked_surfaces"))
    if not isinstance(surfaces, list):
        issues.append(ValidationIssue("redaction_surfaces", "redaction.checked_surfaces", "must be a list"))
    else:
        normalized = {str(item).strip().lower() for item in surfaces}
        missing = sorted(REQUIRED_REDACTION_SURFACES - normalized)
        if missing:
            issues.append(
                ValidationIssue(
                    "redaction_surfaces",
                    "redaction.checked_surfaces",
                    f"missing required surfaces: {', '.join(missing)}",
                )
            )

    for path, value in _iter_string_values(payload):
        lowered_path = path.lower()
        for key_part in SENSITIVE_KEY_PARTS:
            if key_part in lowered_path:
                issues.append(ValidationIssue("sensitive_key", path, f"forbidden sensitive evidence key: {key_part}"))
                break
        for name, pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                issues.append(ValidationIssue("sensitive_value", path, f"looks like {name}; store only redacted references"))
                break

    return _dedupe_issues(issues)


def _get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _is_placeholder(value: str) -> bool:
    stripped = value.strip()
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    return stripped.startswith("<") and stripped.endswith(">")


def _iter_string_values(value: Any, prefix: str = "$") -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}"
            items.extend(_iter_string_values(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_iter_string_values(child, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        items.append((prefix, value))
    return items


def _dedupe_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[ValidationIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return unique


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("evidence file must contain a JSON object")
    return payload


def write_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_template(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate redacted CR-041 Pilot Gate C operator evidence.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-template", metavar="PATH", help="Write a redacted evidence template JSON file.")
    group.add_argument("--check", metavar="PATH", help="Validate an operator-filled evidence JSON file.")
    args = parser.parse_args(argv)

    if args.write_template:
        write_template(Path(args.write_template))
        print(json.dumps({"ok": True, "template": args.write_template}, ensure_ascii=False))
        return 0

    payload = load_json(Path(args.check))
    issues = validate_evidence(payload)
    result = {"ok": not issues, "issues": [issue.as_dict() for issue in issues]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
