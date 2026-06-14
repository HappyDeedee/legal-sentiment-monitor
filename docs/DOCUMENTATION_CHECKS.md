# Documentation Checks

This document defines the intended documentation consistency check for coding
agents. The script is not implemented yet; this file is the specification for
the future `scripts/check_docs.py` task.

## Purpose

Before and after each implementation phase, verify that project documents stay
consistent with each other and that no accepted requirement exists only in chat
history.

## Intended Command

```text
python scripts/check_docs.py
```

The command should be safe to run locally and in CI. It should not modify files.

## Required Checks

1. Every `CR-xxx` entry in `CHANGE_REQUESTS.md` appears in `TRACEABILITY.md`.
2. Every `Needs Confirmation` CR is not described as ready for implementation
   in `CURRENT_STATE.md`.
3. Every implemented or accepted CR maps to at least one task area and one test
   area.
4. Every Phase in `TASKS.md` has matching coverage in `TEST_PLAN.md` or a
   documented reason why it does not.
5. Every specialist document is referenced by `AGENTS.md` or
   `AGENT_WORKFLOW.md`.
6. `DECISIONS.md` contains accepted high-impact decisions before stable product
   documents depend on them.
7. `monitor.example.yaml` keys align with `SYSTEM_SETTINGS.md`.
8. No customer-facing UI rules allow raw profile paths, local paths, command
   lines, cookies, API keys, SMTP passwords, or proxy credentials.
9. Internal markdown links and referenced document filenames exist.
10. Tables marked as implemented or required for the active phase exist in
    `api/monitoring/database.py` or are clearly marked as not yet implemented.
11. Fields marked as Phase 0.5 required in `SCHEMA_MIGRATION.md` exist in the
    corresponding schema creation or migration code after Phase 0.5 is marked
    complete.
12. Editable runtime settings in `SYSTEM_SETTINGS.md` have matching config keys
    in `monitor.example.yaml` or a documented reason why they are database-only.
13. `CURRENT_STATE.md` implementation claims match actual code evidence for
    schema, auth, settings, profile, and deployment work.

## Suggested Output

```text
PASS docs consistency
```

or:

```text
FAIL docs consistency
- [P0] CR-012B is Needs Confirmation but CURRENT_STATE says Phase 5 can start.
- [P1] A specialist document is not referenced by AGENTS.md.
```

## Severity

- P0: can mislead a coding agent into implementing the wrong product or schema.
- P1: reduces development reliability or testability.
- P2: readability, navigation, or maintainability issue.

## When To Run

- before starting a new phase;
- after adding or accepting a change request;
- before merging a feature branch or worktree;
- before asking another agent to audit the project documents.

## Status

Specification exists. Script implementation is still pending in `TASKS.md`.
