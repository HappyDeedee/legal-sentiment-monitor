from scripts import check_docs


def test_needs_confirmation_detection_stays_within_each_cr_section(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "CHANGE_REQUESTS.md").write_text(
        """# Change Requests

## CR-095 - Verified Governance

Status: Verified

This CR explains how Needs Confirmation items are handled.

## CR-106B - Pending Dashboard Change

Status: Needs Confirmation
""",
        encoding="utf-8",
    )
    (docs / "TRACEABILITY.md").write_text(
        """| Requirement | Module | Task Area | Code Area | Test Area | Status |
| --- | --- | --- | --- | --- | --- |
| CR-095 | Governance | Tasks | Docs | Review | Verified |
| CR-106B | Dashboard | Pending | Docs | Planned | Needs Confirmation |
""",
        encoding="utf-8",
    )
    (docs / "CURRENT_STATE.md").write_text(
        "CR-095 is unblocked for documentation work.\n"
        "CR-106B is unblocked for implementation.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(check_docs, "DOCS", docs)

    issues: list[str] = []
    check_docs.check_change_requests(issues)

    assert issues == [
        "[P0] CR-106B needs confirmation but CURRENT_STATE describes it as ready"
    ]
