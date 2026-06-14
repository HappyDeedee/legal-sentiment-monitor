# Change Requests

Record every meaningful new requirement here before implementation.

Status values:

- Proposed
- Needs Confirmation
- Accepted
- In Progress
- Implemented
- Verified
- Deferred
- Rejected

## Quick Index

- CR-001: Documentation Governance Bootstrap
- CR-002: Full Menu Product Coverage
- CR-003: Requirement Intake And Documentation Loop
- CR-004: Confirmation Gate For Ambiguous Requirements
- CR-005: P0 Implementation Specification Documents
- CR-006: User And Workspace Permission Design
- CR-007: Account Environment And Profile Migration Direction
- CR-008: Runtime Settings Specification
- CR-009: Permission Confirmation Pack
- CR-010: Compatible Schema Migration Plan
- CR-011: Runtime Config Example
- CR-012A: Account Environment Profile Key Format
- CR-012B: Account And Profile Lock Timeout
- CR-012C: Account/Profile/Proxy Lock Storage
- CR-013: API Authentication Implementation Guide
- CR-014: Server Deployment Guide
- CR-015: Documentation Consistency Check Specification
- CR-016: Phase 0.5 And Code-State Documentation Hardening
- CR-017: Runtime Strategy Page Layout Detail

## CR-001 - Documentation Governance Bootstrap

Date: 2026-06-14

Source: user conversation

Module: project governance

Requirement:

Create a Git-tracked documentation system that lets coding agents understand
project goals, update progress, record decisions, and validate changes without
relying on chat history.

Reason:

The project scope is expanding from a crawler wrapper into a server-deployed
ToB monitoring system. Development needs persistent project context.

Status: Verified

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `AGENTS.md` exists;
- goal, tasks, current state, decisions, UI/UX, and test documents exist;
- documents are committed to Git.

## CR-002 - Full Menu Product Coverage

Date: 2026-06-14

Source: user conversation

Module: product requirements

Requirement:

Document every active menu item and page, not only the features discussed in
chat.

Reason:

Future coding agents need complete page-level logic and acceptance criteria.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `PRODUCT_REQUIREMENTS.md` covers overview, monitoring, run center, report
  center, resource management, and system configuration.

## CR-003 - Requirement Intake And Documentation Loop

Date: 2026-06-14

Source: user conversation

Module: agent workflow

Requirement:

When the user raises a new requirement, agents must record it in project
documents, connect it to tasks and tests, and update progress after
implementation.

Reason:

Requirements should not exist only in chat. The project needs a closed-loop
documentation mechanism.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `CHANGE_REQUESTS.md` exists;
- `TRACEABILITY.md` exists;
- `AGENT_WORKFLOW.md` defines when to update documents;
- `AGENTS.md` references the workflow.

## CR-004 - Confirmation Gate For Ambiguous Requirements

Date: 2026-06-14

Source: user conversation

Module: agent workflow

Requirement:

Agents must confirm with the user before turning ambiguous assumptions into
accepted product, permission, deployment, account-environment, security, or
data-model requirements.

Reason:

The project is now governed by documents. Incorrect assumptions in documents can
mislead future coding agents and create product or architecture drift.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `AGENT_WORKFLOW.md` contains a confirmation gate;
- `AGENTS.md` tells agents to ask before accepting ambiguous high-impact
  requirements;
- assumptions can be drafted only when marked as proposed or needing
  confirmation.

## CR-005 - P0 Implementation Specification Documents

Date: 2026-06-14

Source: external documentation review

Module: project governance

Requirement:

Create P0 specialist documents for roles and permissions, account environment,
system settings, and data model so coding agents do not need to guess critical
implementation details.

Reason:

The review found that the project governance loop exists, but implementation
specifications for Phase 1, Phase 2, and Phase 5 were missing or too high-level.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 1 in `TASKS.md`
- Phase 2 in `TASKS.md`
- Phase 5 in `TASKS.md`

Acceptance:

- `ROLES_AND_PERMISSIONS.md` exists;
- `ACCOUNT_ENVIRONMENT.md` exists;
- `SYSTEM_SETTINGS.md` exists;
- `DATA_MODEL.md` exists;
- open assumptions are marked as needing user confirmation.

## CR-006 - User And Workspace Permission Design

Date: 2026-06-14

Source: external documentation review

Module: users and permissions

Requirement:

Define role permissions, workspace data scope, menu visibility, API access
policy, and user lifecycle before implementing Phase 1.

Reason:

Without this, Phase 1 requires guessing user, role, and workspace behavior.

Status: Accepted

Related tasks:

- Phase 1 in `TASKS.md`

Acceptance:

- V1 uses one default workspace;
- initial administrator is created through environment bootstrap;
- normal users can delete own non-running tasks;
- normal users can resend own reports;
- disabled users cannot log in but existing tasks continue under workspace
  ownership;
- MVP includes minimal audit log.

## CR-007 - Account Environment And Profile Migration Direction

Date: 2026-06-14

Source: external documentation review

Module: account environment

Requirement:

Define platform account, profile, proxy, browser session, login session, and
profile migration behavior before implementing Phase 5 and Phase 6.

Reason:

The current code still has legacy `profile_path` concepts, while product
decisions require stable `profile_key` and hidden real paths.

Status: Accepted

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user has confirmed legacy profile migration can be direct-new-profile rather
  than compatibility-preserving;
- new account environments use `profile_key`;
- customer-facing UI and API should stop accepting arbitrary profile paths.

## CR-008 - Runtime Settings Specification

Date: 2026-06-14

Source: external documentation review

Module: system settings

Requirement:

Define runtime settings, configuration precedence, editable fields, locked
fields, validation ranges, and config-file shape before implementing Phase 2.

Reason:

Runtime settings are currently spread across code defaults and environment
variables.

Status: Accepted

Related tasks:

- Phase 2 in `TASKS.md`

Acceptance:

- user confirms flexible key-value settings table;
- MVP audit log direction is confirmed for security-sensitive administrator
  actions.

## CR-009 - Permission Confirmation Pack

Date: 2026-06-14

Source: external documentation review

Module: users and permissions

Requirement:

Gather Phase 1 blocking permission, workspace, initial administrator, auth, and
disabled-user behavior questions into a single confirmation document with
recommended and alternative options.

Reason:

Phase 1 cannot start safely until high-impact permission decisions are
confirmed.

Status: Implemented

Related tasks:

- Phase 1 in `TASKS.md`

Acceptance:

- `PERMISSIONS_CONFIRMATION.md` exists;
- every blocking item has a recommended option and alternative;
- accepted V1 decisions are recorded after user confirmation.

## CR-010 - Compatible Schema Migration Plan

Date: 2026-06-14

Source: external documentation review

Module: data model

Requirement:

Create a compatible schema migration plan before user, workspace, profile_key,
system settings, and lock fields are implemented.

Reason:

The target data model is ahead of the current schema. A migration plan is needed
to avoid breaking existing monitoring data and account profiles.

Status: Implemented

Related tasks:

- Phase 1 in `TASKS.md`
- Phase 5 in `TASKS.md`

Acceptance:

- `SCHEMA_MIGRATION.md` exists;
- migration steps add fields before removing legacy fields;
- direct-new-profile migration direction is documented for low-volume existing
  accounts.

## CR-011 - Runtime Config Example

Date: 2026-06-14

Source: external documentation review

Module: system settings

Requirement:

Add a committed `monitor.example.yaml` that documents the intended runtime
configuration shape without real secrets.

Reason:

Phase 2 needs a concrete configuration example and deployment operators need a
safe starting point.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 2 in `TASKS.md`

Acceptance:

- `monitor.example.yaml` exists;
- the file contains runtime, platform, login, scheduler, and retention examples;
- deployment-only values remain environment-variable based.

## CR-012A - Account Environment Profile Key Format

Date: 2026-06-14

Source: external documentation review

Module: account environment

Requirement:

Confirm the final `profile_key` format before implementing the account profile
resolver.

Reason:

The product direction is accepted, but the exact key format affects filesystem
layout, database values, diagnostics, and migration scripts.

Status: Needs Confirmation

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirms final format, with current recommendation:
  `{workspace_id}/{platform}/acc_{account_id}`;
- examples are updated in `ACCOUNT_ENVIRONMENT.md`;
- path resolver tests use the confirmed format.

## CR-012B - Account And Profile Lock Timeout

Date: 2026-06-14

Source: external documentation review

Module: account environment

Requirement:

Confirm lock timeout behavior before implementing account/profile lock
acquisition and stale-lock recovery.

Reason:

Lock timeout affects failed-run recovery and whether a stuck browser session can
block future scheduled runs.

Status: Needs Confirmation

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirms timeout strategy, with current recommendation:
  task timeout plus cleanup buffer;
- stale lock cleanup behavior is documented;
- timeout setting source is documented in `SYSTEM_SETTINGS.md` if configurable.

## CR-012C - Account/Profile/Proxy Lock Storage

Date: 2026-06-14

Source: external documentation review

Module: account environment

Requirement:

Confirm lock storage before implementing account, profile, and proxy
concurrency controls.

Reason:

Inline lock fields and a dedicated lock table have different migration,
querying, and proxy concurrency tradeoffs.

Status: Needs Confirmation

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirms storage strategy, with current recommendation:
  inline fields for single account/profile locks and `resource_locks` table for
  proxy concurrency;
- schema migration plan is updated with the confirmed fields/tables;
- lock tests cover account, profile, and proxy concurrency.

## CR-013 - API Authentication Implementation Guide

Date: 2026-06-14

Source: external documentation review

Module: users and permissions

Requirement:

Create an implementation guide for V1 session-based authentication, API
authorization, workspace/user data scope, bootstrap administrator creation, and
audit behavior.

Reason:

`ROLES_AND_PERMISSIONS.md` defines permissions, but coding agents also need a
concrete API/auth contract to avoid inconsistent FastAPI implementations.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 1 in `TASKS.md`

Acceptance:

- `API_AUTHENTICATION.md` exists;
- it documents session storage, cookie behavior, API endpoints,
  authorization dependencies, data-scope rules, errors, audit, and
  implementation order.

## CR-014 - Server Deployment Guide

Date: 2026-06-14

Source: external documentation review

Module: server deployment

Requirement:

Create a server deployment and server-like validation guide covering
container/systemd deployment, persistent profile storage, environment
variables, browser requirements, backup, reverse proxy, and acceptance checks.

Reason:

The product must be deployed on a server and validated through the web UI, not
through the operator's local browser.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 8 in `TASKS.md`

Acceptance:

- `SERVER_DEPLOYMENT.md` exists;
- it documents server-like acceptance requirements and persistent data;
- `AGENTS.md` and `AGENT_WORKFLOW.md` route deployment work to the document.

## CR-015 - Documentation Consistency Check Specification

Date: 2026-06-14

Source: external documentation review

Module: project governance

Requirement:

Define the future documentation check script before implementation, including
what it should validate and how it should report inconsistencies.

Reason:

The task list required a documentation check script, but no specification
existed for coding agents to implement it consistently.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `DOCUMENTATION_CHECKS.md` exists;
- it defines required checks, severity levels, output format, and run timing;
- the script implementation remains explicitly pending in `TASKS.md`.

## CR-016 - Phase 0.5 And Code-State Documentation Hardening

Date: 2026-06-14

Source: external documentation review

Module: project governance

Requirement:

Make the documentation more explicit that Phase 0.5 is not implemented yet and
is a blocking prerequisite before Phase 1-9 implementation work.

Reason:

The documents described the target architecture, but coding agents could still
misread planning completion as code implementation completion.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 0.5 in `TASKS.md`

Acceptance:

- `CURRENT_STATE.md` states that Phase 0.5 is not implemented yet;
- `TASKS.md` marks Phase 0.5 as a blocking prerequisite;
- `TEST_PLAN.md` includes Phase 0.5 migration regression checks;
- `DATA_MODEL.md` states that target tables and fields are not assumed to
  exist before Phase 0.5;
- `AGENT_WORKFLOW.md` prevents Phase 1-9 work from skipping Phase 0.5.

## CR-017 - Runtime Strategy Page Layout Detail

Date: 2026-06-14

Source: external documentation review

Module: UI/UX

Requirement:

Confirm the detailed layout pattern for the administrator Runtime Strategy
page.

Reason:

The settings fields and categories are documented, but the exact UI pattern
for grouping, apply-scope display, and locked-setting display should be clear
before implementation.

Status: Needs Confirmation

Related tasks:

- Phase 2 in `TASKS.md`

Acceptance:

- user confirms whether Runtime Strategy uses a dense table, grouped form
  sections, or another layout;
- `PRODUCT_REQUIREMENTS.md` and `UI_UX_GUIDELINES.md` are updated with the
  confirmed layout;
- Phase 2 UI implementation follows the confirmed layout.
