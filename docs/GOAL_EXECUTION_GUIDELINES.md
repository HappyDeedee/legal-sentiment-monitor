# Goal Execution Guidelines

This document defines how open todos become executable goals after CR-095. It
does not add product scope, reopen completed phases, or replace
`CURRENT_STATE.md` as the source for the next allowed implementation order.

## Purpose

Every future implementation or documentation-governance goal must be small
enough to finish, test, review, and document without guessing boundaries. A
goal is ready only when it has one owner, one primary risk area, clear start
and stop gates, and tests that prove both intended behavior and forbidden
side effects.

## Goal Packet Template

Before starting a non-trivial goal, write or confirm a compact packet with:

- Goal name and owner CR or phase.
- Current baseline from source documents and, when relevant, current code.
- In scope.
- Out of scope.
- Hard boundaries and must-not-change behavior.
- Start gate and dependencies.
- Expected file, module, data, or document touch surface.
- Execution steps.
- Test iteration loop.
- Acceptance criteria.
- Rollback or recovery path.
- Documentation updates.
- Stop conditions.

If any required field cannot be answered from the current documents, stop and
record the ambiguity instead of starting a later or broader task.

## Atomicity Rules

- One goal owns one boundary and one primary risk area.
- A planning or preflight goal must not include implementation changes.
- A UI visual goal must not change backend APIs, schema, permissions, runtime
  behavior, crawler behavior, scheduler behavior, account identity, or
  deployment behavior unless a separate accepted CR says so.
- A backend, schema, or provider goal must not use visual cleanup as a reason
  to change Task Center, Run Detail, drawer, modal, select/date, scroll, close,
  route, or permission behavior.
- A `Needs Confirmation` CR can receive read-only analysis or planning, but it
  cannot become implementation-ready until the required decision is accepted.
- A completed historical phase stays historical. New defects or structural
  issues become follow-up CRs or explicitly named follow-up phases.
- External side effects such as real email, real crawling, real platform login,
  real proxy use, profile export/import, file deletion, or production route
  exposure require explicit gates and tests or tripwires.

## Todo Baseline Review

Before approving or starting an active or next goal, compare the open todo and
CR entries against current `main`, local worktree state, accepted decisions,
traceability, test plan, and relevant code/schema/UI/runtime evidence. Classify
items as current, already completed, stale, duplicate, future-only, deferred,
`Needs Confirmation`, operator-gated, or historical/archive-only. Resolve stale
or duplicate documentation before treating the item as implementation-ready.

## Current Execution Lanes

Use this serial rhythm unless `CURRENT_STATE.md` is updated by a later accepted
decision:

1. Phase 21 is merged and closed on `main`. The current `/monitor` frontend
   baseline is Task Center / Run Detail with the verified drawer, modal,
   enhanced select/date, close, scroll, refresh, and routing logic preserved.
   Further UI work requires a separate accepted CR.
2. Keep the verified Phase 5.1P read-only result in
   `docs/phase-5.1p-browser-entrypoint-map.md` as the compatibility boundary
   for QR login, Cookie validation, login-state checks, manual and scheduler
   runs, runner behavior, and MediaCrawler CDP launch/reconnect.
3. Phase 5.1A additive account identity data model is implemented and
   independently verified.
4. Keep completed Phase 5.1B-D and their follow-up regressions closed as
   verified history.
5. Close the separate CR-047 Linux/server-like acceptance only after its gate
   proves requested/effective
   runtime snapshots, provider metadata, proxy effect proof or fail-closed
   behavior, manual/scheduler reuse, MediaCrawler CDP binding, and
   container/server-like validation.
6. Execute accepted CR-112 Packet B, C, and D serially. Packet B begins only
   after its validated plan documents are committed atomically; local CR-112
   proof does not close the CR-047 server-like gate.
7. Start CR-070 / Phase 5.2 only after CR-112 Packet D is verified. Execute Phase 5.2A-E in
   order: package contract/security, export flow, import flow,
   post-import/recovery, then test safety and verification.
8. Keep CR-092, CR-093, and CR-094 as future independent backlog lanes. They do
   not block Phase 21, Phase 5.1P, Phase 5.1, or CR-070, and they cannot be
   treated as hidden prerequisites without a later accepted decision.
9. Keep CR-037, Users And Permissions page work, and Phase 7.1D historical
    remediation as separate deferred or operator-gated items.

## Test Iteration Loop

Each implementation goal uses this loop:

1. Pre-check: read the required source documents and confirm the first
   unblocked item.
2. Implement only the goal packet.
3. Run targeted checks for the changed area.
4. Fix failures and rerun the targeted checks until clean.
5. Run broader checks proportional to the blast radius.
6. Update `TASKS.md`, `CURRENT_STATE.md`, `TEST_RESULTS.md`, and
   `TRACEABILITY.md` when requirements, tasks, or tests changed.
7. Run documentation consistency checks.
8. For roadmap, acceptance, provider, deployment, permission, account, or
   external-side-effect goals, run a read-only cross-review before calling the
   goal ready.

Do not advance to the next goal while any targeted check, required broader
check, documentation check, acceptance gate, or blocking review finding is
still open.

## Acceptance Standards

A documentation-only governance goal is complete only when:

- the owning CR, task block, current-state note, test-plan entry, traceability
  row, and test-result entry agree;
- `uv run python scripts/check_docs.py` passes;
- `git diff --check` passes or reports only known Windows line-ending warnings;
- a final MECE and boundary review finds no blocking issue.

A code or UI implementation goal is complete only when:

- code, tests, and documents agree;
- the accepted behavior is verified through targeted tests;
- broader regression checks match the blast radius;
- customer-facing surfaces avoid secrets, raw paths, debug wording, and
  implementation-only language;
- `docs/TEST_RESULTS.md` records what was proved and what was not proved.

A future goal that changes the closed Phase 21 baseline must include browser
verification for administrator and normal-user paths at `1440x900`,
`1024x768`, and `390x844`, and must fail on one-character vertical text,
overlap, hidden primary actions, broken drawer/modal/menu behavior, or
horizontal page overflow.

Phase 5.1 and CR-070 goals must use container/server-like validation as the
acceptance baseline. Local Chrome, local-window login, CDP connect-existing,
process defaults, and default-network fallback are development diagnostics
only unless a later accepted decision changes that rule.

## Stop Conditions

Stop the current goal and record the blocker when:

- the next allowed item is unclear;
- two open goals would edit the same critical files or product surface without
  coordination;
- a `Needs Confirmation` item is being treated as implementation-ready;
- a required provider, route, permission, proxy, deployment, or data-model
  decision is missing;
- tests cannot prove a required negative guarantee or forbidden side effect;
- implementation would touch code, UI, schema, runtime data, account profiles,
  cookies, proxies, crawler behavior, deployment configuration, or production
  state outside the accepted boundary.
