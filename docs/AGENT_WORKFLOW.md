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

Phase 1 user and permission implementation must start only after Phase 0.5
schema foundation work is complete.

Specialist document routing:

- UI/page work: `docs/UI_UX_GUIDELINES.md` and
  `docs/PRODUCT_REQUIREMENTS.md`
- user/permission work: `docs/ROLES_AND_PERMISSIONS.md` and
  `docs/PERMISSIONS_CONFIRMATION.md`
- API authentication/authorization work: `docs/API_AUTHENTICATION.md`
- account/login/profile/proxy work: `docs/ACCOUNT_ENVIRONMENT.md` and
  `docs/TEST_PLAN.md`
- server/deployment work: `docs/SERVER_DEPLOYMENT.md` and `docs/TEST_PLAN.md`
- runtime setting work: `docs/SYSTEM_SETTINGS.md`
- data-model work: `docs/DATA_MODEL.md` and `docs/SCHEMA_MIGRATION.md`
- documentation consistency tooling: `docs/DOCUMENTATION_CHECKS.md`

If documents conflict, follow this priority:

1. `docs/DECISIONS.md`
2. relevant specialist documents
3. `docs/CURRENT_STATE.md`
4. `docs/TASKS.md`
5. general product or workflow documents

## New Requirement Intake

When the user gives a new requirement:

1. Decide whether it is already covered by existing documents.
2. If it is new or changes scope, add an entry to `CHANGE_REQUESTS.md`.
3. If it is ambiguous, mark it as `Proposed` and ask the user to confirm.
4. If it changes product behavior, update `PRODUCT_REQUIREMENTS.md` only after
   the decision is clear, or mark the section as proposed.
5. If it changes UI rules, update `UI_UX_GUIDELINES.md` only after the decision
   is clear, or mark the section as proposed.
6. If it changes a product or technical decision, append to `DECISIONS.md`
   after user confirmation.
7. Add or update tasks in `TASKS.md`.
8. Add or update rows in `TRACEABILITY.md`.

Do not implement meaningful new scope only from chat memory.

## Confirmation Gate

Ask the user before accepting or implementing assumptions that affect:

- product scope;
- role permissions;
- server deployment;
- browser/profile/account behavior;
- proxy behavior;
- data model;
- security;
- billing or SaaS boundaries;
- customer-facing wording.

Allowed without confirmation:

- formatting fixes;
- typo fixes;
- adding clearly marked draft sections;
- documenting already-confirmed decisions;
- updating progress after completed work.

When confirmation is needed, use this flow:

1. record the item as `Proposed` in `CHANGE_REQUESTS.md`;
2. list assumptions clearly;
3. ask the user to confirm or correct;
4. after confirmation, change status to `Accepted`;
5. then implement or update stable product documents.

## During Implementation

- Before starting Phase 1-9 work, verify Phase 0.5 tasks are marked `[x]` in
  `TASKS.md`.
- Before implementing authentication, RBAC, workspace filtering, or runtime
  settings, verify the active schema creates `users`, `workspaces`,
  `user_sessions`, `system_settings`, and `audit_logs`.
- Do not implement authentication, RBAC, or workspace filtering on top of the
  pre-Phase-0.5 schema.
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

Cross-phase examples:

- `codex/schema-and-auth` for Phase 0.5 plus Phase 1 work;
- `codex/settings-and-ui` for Phase 2 plus related administrator UI work.

Rules:

- one worktree per feature area;
- avoid multiple agents editing the same large frontend file at the same time;
- merge one feature branch at a time;
- update documents in every branch;
- run relevant tests before merge.

### Document Update Protocol For Parallel Work

- Each branch or worktree may update shared documents, but the final merge must
  reconcile `TASKS.md`, `CURRENT_STATE.md`, `TRACEABILITY.md`, and
  `TEST_RESULTS.md`.
- Rebase on the latest main branch before merging a feature branch.
- `DECISIONS.md` is append-only; keep all confirmed decisions and resolve
  conflicts by preserving both dated entries when they are not contradictory.
- `TEST_RESULTS.md` is append-at-top; resolve conflicts by preserving all
  dated entries in reverse chronological order.
- If two branches change the same requirement or task status, the later merge
  must verify the actual code state before marking anything implemented.
- If document conflict resolution changes product meaning, add or update a
  change request before merging.
