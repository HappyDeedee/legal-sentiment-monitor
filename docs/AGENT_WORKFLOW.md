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

- frontend architecture or console-wide UI redesign:
  `docs/FRONTEND_ARCHITECTURE.md`
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
- goal execution, atomic task split, and acceptance gates:
  `docs/GOAL_EXECUTION_GUIDELINES.md`

If documents conflict, follow this priority:

1. `docs/DECISIONS.md`
2. relevant specialist documents
3. `docs/CURRENT_STATE.md`
4. `docs/TASKS.md`
5. general product or workflow documents

If a later decision supersedes an earlier decision, keep both entries in
`DECISIONS.md` and add a short `Superseded by` note to the older decision when
safe to do so without rewriting its meaning.

## Global Roadmap Review

When the user asks for a plan review, roadmap audit, execution-readiness
review, or goal-command review for a multi-phase roadmap, start with the whole
roadmap rather than the next implementation batch.

The review must answer:

- whether the roadmap is executable enough to reach the final product goal;
- whether the phase order and dependencies are coherent;
- whether each phase is small enough for a safe goal, with a clear file/data
  boundary, rollback path, and verification standard;
- whether changes in one phase create migration, UI, API, permission, data,
  or test risks for later phases;
- whether cross-cutting concerns such as role scope, responsive behavior,
  report history, email idempotency, data migration, and no-build deployment
  are preserved across the whole roadmap.

Only after the global review is complete should the agent generate or approve a
phase-specific execution goal such as a Phase 11A goal. A phase-specific goal
is an execution gate, not a substitute for the global roadmap review.

## Todo Baseline Review Gate

Before starting a new execution lane, approving a non-trivial goal packet, or
resolving sequencing ambiguity, perform a read-only todo baseline review. Read
the open items in `TASKS.md`, `CHANGE_REQUESTS.md`, `CURRENT_STATE.md`,
`TRACEABILITY.md`, `TEST_PLAN.md`, and accepted decisions, then compare them
against current `main`, local worktree state, and relevant code, schema, UI,
runtime, or documented evidence.

Classify each active or next item as current, already completed, stale old
baseline, duplicate or overlapping, future-only, deferred, `Needs
Confirmation`, operator-gated, or historical/archive-only. Treat stale or
misaligned tasks as documentation issues first: rewrite, defer, mark
completed, merge duplicates, operator-gate, archive, or create a follow-up CR.
Do not reopen completed historical phases through old unchecked boxes.

## Goal Readiness Gate

Before starting or approving a non-trivial implementation or documentation
governance goal, read `docs/GOAL_EXECUTION_GUIDELINES.md` and confirm the goal
packet is complete.

The packet must state:

- owner CR or phase;
- current baseline;
- in scope and out of scope;
- hard boundaries and must-not-change behavior;
- dependencies and start gate;
- expected file, module, data, or document touch surface;
- execution steps;
- test iteration loop;
- acceptance criteria;
- rollback or recovery path;
- documentation updates;
- stop conditions.

Do not start a goal if it mixes separate lanes such as a follow-up against the
closed Phase 21 visual baseline, Phase 5.1P read-only preflight, Phase 5.1
implementation, CR-070 export/import, CR-092 `/monitor-next`, CR-093 public
exposure, or CR-094 provider architecture without a later accepted decision
that deliberately merges those boundaries.

Current goal rhythm:

1. Phase 21 is merged and closed on `main`.
2. Phase 5.1P documentation/read-only compatibility preflight is the next
   active lane.
3. Phase 5.1A-D implementation in order.
4. Phase 5.1 acceptance gate.
5. CR-070 / Phase 5.2A-E only after CR-047 provider/effective snapshot
   verification.
6. CR-092, CR-093, and CR-094 remain future independent backlog lanes.

Use the iteration rule from `docs/GOAL_EXECUTION_GUIDELINES.md`:
pre-check, implement only the packet, run targeted checks, fix and rerun, run
broader checks proportional to blast radius, update documents, run docs
consistency, and use read-only cross-review for roadmap, acceptance, provider,
deployment, permission, account, or external-side-effect goals.

If the next item is unclear, a `Needs Confirmation` item is being treated as
ready, or the tests cannot prove a required negative guarantee, stop and record
the blocker instead of widening the goal.

## New Requirement Intake

When the user gives a new requirement:

1. Decide whether it is already covered by existing documents.
2. Classify it before implementation:
   - `New Capability` for a new user-visible capability, API, data surface,
     integration, role behavior, or deployment behavior;
   - `Existing Feature Optimization` for improving an existing workflow while
     preserving its current product boundary and old working behavior;
   - `Regression Fix` for restoring intended behavior after a verified
     breakage;
   - `Documentation Governance` for changing requirement, task, decision, or
     verification-document rules.
3. If it is new, changes scope, or materially optimizes an existing feature,
   add an entry to `CHANGE_REQUESTS.md`.
4. Update the `CHANGE_REQUESTS.md` Quick Index when adding a new CR.
5. Each CR should include background, purpose, requirement type, scope
   boundary, non-goals when useful, related tasks, and acceptance criteria.
6. For `Existing Feature Optimization`, name the current feature, observed
   limitation, behavior that must be preserved, rollback boundary, and
   regression tests.
7. For `New Capability`, name the added product/API/data/UI/deployment surface,
   dependencies, confirmation needs, and explicit non-goals.
8. For `Regression Fix`, name the broken surface, expected baseline behavior,
   minimal fix boundary, and recurrence-prevention test.
9. If it is ambiguous, mark it as `Proposed` and ask the user to confirm.
10. If it changes product behavior, update `PRODUCT_REQUIREMENTS.md` only after
   the decision is clear, or mark the section as proposed.
11. If it changes UI rules, update `UI_UX_GUIDELINES.md` only after the decision
   is clear, or mark the section as proposed.
12. If it changes a product or technical decision, append to `DECISIONS.md`
   after user confirmation.
13. Add or update tasks in `TASKS.md`.
14. Add or update rows in `TRACEABILITY.md`.

Do not implement meaningful new scope only from chat memory.

## Completed Phase Follow-up

When a new defect is found in a phase that is already marked complete:

1. Do not rewrite the historical phase as incomplete or delete older
   verification notes.
2. Classify the new work as a `Regression Fix`.
3. Add a new CR in `CHANGE_REQUESTS.md`.
4. Add a follow-up task block under the original responsibility area, for
   example `Phase 7.1` for a Phase 7 run/report/AI defect.
5. Link the follow-up CR back to the original requirement in
   `TRACEABILITY.md`.
6. Add tests that would have caught the defect.
7. Update `CURRENT_STATE.md` to explain that the old phase remains a historical
   verification snapshot and the new work is a follow-up fix.

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
- If the next implementation phase is ambiguous or blocked, stop and report the
  issue instead of selecting a later phase opportunistically.
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
- `CHANGE_REQUESTS.md` lifecycle status matches the actual proof level:
  `Accepted` before implementation, `Implemented` after code completion, and
  `Verified` only after the recorded acceptance checks pass;
- `TASKS.md` reflects task status;
- completed planning checklists are not left unchecked beside duplicate
  completed implementation checklists;
- `CURRENT_STATE.md` reflects latest state;
- `TEST_RESULTS.md` records verification;
- `DECISIONS.md` records any new decision;
- `TRACEABILITY.md` links requirements to tasks and tests where applicable.

The final semantic lifecycle comparison is a manual current-baseline review
unless `scripts/check_docs.py` explicitly implements the same check. A passing
documentation script must not be used to justify stale `Accepted`, `In
Progress`, or unchecked-task labels that conflict with current code and
recorded verification.

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
