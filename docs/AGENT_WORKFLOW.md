# Agent Workflow

This document defines how coding agents should use and update the project
documents.

## Start Of Work

Before implementation, read:

1. `AGENTS.md`
2. `docs/GOAL.md`
3. `docs/CURRENT_STATE.md`
4. `docs/TASKS.md`
5. `docs/DECISIONS.md`
6. Relevant specialist documents.

Specialist document routing:

- UI/page work: `docs/UI_UX_GUIDELINES.md` and
  `docs/PRODUCT_REQUIREMENTS.md`
- user/permission work: `docs/PRODUCT_REQUIREMENTS.md`
- account/login/profile/proxy work: `docs/GOAL.md`, `docs/TEST_PLAN.md`, and
  future account-environment docs
- server/deployment work: `docs/TEST_PLAN.md` and future deployment docs
- runtime setting work: `docs/PRODUCT_REQUIREMENTS.md`

## New Requirement Intake

When the user gives a new requirement:

1. Decide whether it is already covered by existing documents.
2. If it is new or changes scope, add an entry to `CHANGE_REQUESTS.md`.
3. If it changes product behavior, update `PRODUCT_REQUIREMENTS.md`.
4. If it changes UI rules, update `UI_UX_GUIDELINES.md`.
5. If it changes a product or technical decision, append to `DECISIONS.md`.
6. Add or update tasks in `TASKS.md`.
7. Add or update rows in `TRACEABILITY.md`.

Do not implement meaningful new scope only from chat memory.

## During Implementation

- Keep changes scoped to the related task.
- Do not expand V1 scope without a change request and decision.
- Do not expose secrets, raw server paths, local browser assumptions, or
  implementation-only wording in customer-facing UI.
- Prefer small, verifiable changes.
- If using parallel agents or worktrees, each agent should own a distinct module
  or file area.

## Completion Checklist

A change is complete only when:

- code is updated;
- relevant tests or checks are run;
- `TASKS.md` reflects task status;
- `CURRENT_STATE.md` reflects latest state;
- `TEST_RESULTS.md` records verification;
- `DECISIONS.md` records any new decision;
- `TRACEABILITY.md` links requirements to tasks and tests where applicable.

## Parallel Development

Parallel work is allowed only with clear boundaries.

Recommended branches/worktrees:

- `codex/auth-rbac`
- `codex/ui-ux`
- `codex/account-environment`
- `codex/runtime-settings`
- `codex/server-deployment`
- `codex/docs-governance`

Rules:

- one worktree per feature area;
- avoid multiple agents editing the same large frontend file at the same time;
- merge one feature branch at a time;
- update documents in every branch;
- run relevant tests before merge.

