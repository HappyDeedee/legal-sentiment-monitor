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
- user/permission work: `docs/ROLES_AND_PERMISSIONS.md`
- account/login/profile/proxy work: `docs/ACCOUNT_ENVIRONMENT.md` and
  `docs/TEST_PLAN.md`
- server/deployment work: `docs/TEST_PLAN.md` and future deployment docs
- runtime setting work: `docs/SYSTEM_SETTINGS.md`
- data-model work: `docs/DATA_MODEL.md`

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
