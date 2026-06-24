from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_issue(issues: list[str], severity: str, message: str) -> None:
    issues.append(f"[{severity}] {message}")


def check_change_requests(issues: list[str]) -> None:
    change_requests = read(DOCS / "CHANGE_REQUESTS.md")
    traceability = read(DOCS / "TRACEABILITY.md")
    current_state = read(DOCS / "CURRENT_STATE.md")
    cr_headings = re.findall(r"^## (CR-\d+[A-Z]?)\b", change_requests, re.MULTILINE)
    duplicated_headings = sorted({cr_id for cr_id in cr_headings if cr_headings.count(cr_id) > 1})
    for cr_id in duplicated_headings:
        add_issue(issues, "P0", f"{cr_id} is reused by multiple CHANGE_REQUESTS.md headings")

    trace_rows = re.findall(r"^\| (CR-\d+[A-Z]?) \|", traceability, re.MULTILINE)
    duplicated_trace_rows = sorted({cr_id for cr_id in trace_rows if trace_rows.count(cr_id) > 1})
    for cr_id in duplicated_trace_rows:
        add_issue(issues, "P0", f"{cr_id} is reused by multiple TRACEABILITY.md rows")

    cr_ids = sorted(set(cr_headings))
    trace_ids = set(re.findall(r"\bCR-\d+[A-Z]?\b", traceability))
    for cr_id in cr_ids:
        if cr_id not in trace_ids:
            add_issue(issues, "P0", f"{cr_id} is missing from TRACEABILITY.md")

    needs_confirmation = re.findall(
        r"^## (CR-\d+[A-Z]?)\b[\s\S]*?^Status: Needs Confirmation\b",
        change_requests,
        re.MULTILINE,
    )
    for cr_id in needs_confirmation:
        if re.search(rf"{re.escape(cr_id)}[\s\S]{{0,200}}(can begin|ready to start|unblocked)", current_state, re.IGNORECASE):
            add_issue(issues, "P0", f"{cr_id} needs confirmation but CURRENT_STATE describes it as ready")

    rows = [
        line
        for line in traceability.splitlines()
        if line.startswith("| CR-") and "| --- " not in line
    ]
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) < 6:
            add_issue(issues, "P1", f"Malformed traceability row: {row}")
            continue
        requirement, _module, task_area, _code_area, test_area, status = cells[:6]
        if any(word in status for word in ("Accepted", "Implemented", "Verified")):
            if not task_area or task_area == "-":
                add_issue(issues, "P1", f"{requirement} has no task area")
            if not test_area or test_area == "-":
                add_issue(issues, "P1", f"{requirement} has no test area")


def check_phase_test_coverage(issues: list[str]) -> None:
    tasks = read(DOCS / "TASKS.md")
    test_plan = read(DOCS / "TEST_PLAN.md")
    phases = re.findall(r"^## (Phase [\d.]+|Phase \d+) - ([^\n]+)", tasks, re.MULTILINE)
    for phase, title in phases:
        normalized = title.lower()
        if phase == "Phase 0":
            if "documentation review" not in test_plan.lower():
                add_issue(issues, "P2", "Phase 0 lacks documentation review coverage in TEST_PLAN.md")
            continue
        key_terms = [part for part in re.split(r"\W+", normalized) if len(part) > 3]
        if not any(term in test_plan.lower() for term in key_terms):
            add_issue(issues, "P1", f"{phase} - {title} has no obvious TEST_PLAN.md coverage")


def check_specialist_references(issues: list[str]) -> None:
    agents = read(ROOT / "AGENTS.md")
    workflow = read(DOCS / "AGENT_WORKFLOW.md")
    references = agents + "\n" + workflow
    if "Todo Baseline Review Rule" not in agents:
        add_issue(issues, "P1", "AGENTS.md is missing the Todo Baseline Review Rule")
    if "Todo Baseline Review Gate" not in workflow:
        add_issue(issues, "P1", "AGENT_WORKFLOW.md is missing the Todo Baseline Review Gate")
    specialist_docs = [
        "FRONTEND_ARCHITECTURE.md",
        "UI_UX_GUIDELINES.md",
        "PRODUCT_REQUIREMENTS.md",
        "ROLES_AND_PERMISSIONS.md",
        "API_AUTHENTICATION.md",
        "PERMISSIONS_CONFIRMATION.md",
        "ACCOUNT_ENVIRONMENT.md",
        "DATA_MODEL.md",
        "SCHEMA_MIGRATION.md",
        "SERVER_DEPLOYMENT.md",
        "SYSTEM_SETTINGS.md",
        "DOCUMENTATION_CHECKS.md",
        "AGENT_WORKFLOW.md",
    ]
    for filename in specialist_docs:
        if filename not in references and filename != "AGENT_WORKFLOW.md":
            add_issue(issues, "P1", f"{filename} is not referenced by AGENTS.md or AGENT_WORKFLOW.md")


def check_markdown_references(issues: list[str]) -> None:
    markdown_files = [ROOT / "AGENTS.md", *DOCS.glob("*.md")]
    for path in markdown_files:
        text = read(path)
        for filename in re.findall(r"`([^`]+\.md)`", text):
            target = (path.parent / filename).resolve()
            if not target.exists():
                target = (ROOT / filename).resolve()
            if not target.exists():
                add_issue(issues, "P1", f"{rel(path)} references missing markdown file {filename}")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)", text):
            if link.startswith(("http://", "https://")):
                continue
            target = (path.parent / link).resolve()
            if not target.exists():
                add_issue(issues, "P1", f"{rel(path)} links to missing markdown file {link}")


def check_schema_evidence(issues: list[str]) -> None:
    tasks = read(DOCS / "TASKS.md")
    db_code = read(ROOT / "api" / "monitoring" / "database.py")
    if "Phase 0.5 - Schema Foundation" not in tasks:
        return
    required_tables = ["workspaces", "users", "user_sessions", "system_settings", "audit_logs", "resource_locks"]
    for table in required_tables:
        if f"CREATE TABLE IF NOT EXISTS {table}" not in db_code:
            add_issue(issues, "P0", f"Phase 0.5 required table {table} is missing from database.py")
    required_fields = ["workspace_id", "created_by", "updated_by", "profile_key", "timeout_seconds", "deadline_at", "timeout_reason"]
    for field in required_fields:
        if field not in db_code:
            add_issue(issues, "P0", f"Phase 0.5 required field {field} is missing from database.py")


def check_monitor_yaml_gitignore(issues: list[str]) -> None:
    gitignore = read(ROOT / ".gitignore") if (ROOT / ".gitignore").exists() else ""
    if "monitor.yaml" not in gitignore:
        add_issue(issues, "P0", "monitor.yaml is not ignored by .gitignore")
    if not (ROOT / "monitor.example.yaml").exists():
        add_issue(issues, "P0", "monitor.example.yaml is missing")


def main() -> int:
    issues: list[str] = []
    for required in [
        ROOT / "AGENTS.md",
        DOCS / "CHANGE_REQUESTS.md",
        DOCS / "TRACEABILITY.md",
        DOCS / "CURRENT_STATE.md",
        DOCS / "TASKS.md",
        DOCS / "TEST_PLAN.md",
        DOCS / "DOCUMENTATION_CHECKS.md",
    ]:
        if not required.exists():
            add_issue(issues, "P0", f"missing required file {rel(required)}")
    if issues:
        print("FAIL docs consistency")
        for issue in issues:
            print(f"- {issue}")
        return 1

    check_change_requests(issues)
    check_phase_test_coverage(issues)
    check_specialist_references(issues)
    check_markdown_references(issues)
    check_schema_evidence(issues)
    check_monitor_yaml_gitignore(issues)

    if issues:
        print("FAIL docs consistency")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("PASS docs consistency")
    return 0


if __name__ == "__main__":
    sys.exit(main())
