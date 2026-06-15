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
- CR-018: Crawl Range Capability Boundaries
- CR-019: Frontend Navigation And Page Entry Redesign
- CR-020: Frontend Design System
- CR-021: Overview Operations Home Redesign
- CR-022: Run Center Governance
- CR-023: Report Center Task Grouping
- CR-024: Email Delivery Governance
- CR-025: Email Delivery Tracking Data Model
- CR-026: Run Visibility And Noise Filtering Data Model
- CR-027: Frontend Technology Stack Decision
- CR-028: Global Phase 10-18 Plan Review Gate

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

Status: Verified

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

Status: Verified

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

Status: Verified

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user has confirmed legacy profile migration can be direct-new-profile rather
  than compatibility-preserving;
- new account environments use `profile_key`;
- customer-facing UI and API should stop accepting arbitrary profile paths;
- Phase 6 and Phase 8 still need full server-login and server-like acceptance
  validation, but the Phase 5 account environment runtime is verified.

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

Status: Verified

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

Status: Verified

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirmed final format:
  `{workspace_id}/{platform}/acc_{account_id}`;
- examples are updated in `ACCOUNT_ENVIRONMENT.md`;
- path resolver tests use the confirmed format;
- Phase 5 resolver and runtime binding tests verify the confirmed format.

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

Status: Verified

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- administrator timeout is a run-level wall-clock deadline for newly started
  runs;
- V1 does not auto-compute timeout from crawl range;
- lock expiry follows the run deadline plus `lock_cleanup_buffer_seconds`;
- stale lock cleanup verifies the owning run state before releasing locks;
- timeout setting source is documented in `SYSTEM_SETTINGS.md`;
- Phase 5 recovery tests verify timed-out running runs are recovered before
  account/profile/proxy locks are released.

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

Status: Verified

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirmed storage strategy:
  inline fields for single account/profile locks and `resource_locks` table for
  proxy concurrency;
- schema migration plan is updated with the confirmed fields/tables;
- lock tests cover account, profile, and proxy concurrency;
- Phase 5 runtime tests verify inline account/profile locking and proxy
  `resource_locks` concurrency control.

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
- `scripts/server_like_validation.py` verifies the automated server-like HTTP
  service path, production login flags, profile restart persistence, runtime
  locks, and no-local-Chrome validation boundary.

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

Status: Accepted

Related tasks:

- Phase 2 in `TASKS.md`

Acceptance:

- user confirmed Runtime Strategy is administrator-only and uses grouped table
  sections;
- `PRODUCT_REQUIREMENTS.md` and `UI_UX_GUIDELINES.md` are updated with the
  confirmed layout;
- Phase 2 UI implementation follows the confirmed layout.

## CR-018 - Crawl Range Capability Boundaries

Date: 2026-06-14

Source: user conversation and code/document review

Module: monitoring task creation

Requirement:

Document the actual V1 meaning of normal-user crawl range fields and prevent
future agents from describing them as exact cross-platform guarantees.

Reason:

MediaCrawler platform support is not uniform. `max_items`, `start_page`,
`max_pages`, and time windows may be implemented by platform-native options,
monitoring-layer filtering, approximate conversion, or a combination of these.
Product copy, tests, and implementation plans must avoid overpromising exact
page or time-window behavior.

Status: Accepted

Related tasks:

- Phase 4 in `TASKS.md`
- Phase 7 in `TASKS.md`

Acceptance:

- `PRODUCT_REQUIREMENTS.md` distinguishes content-count cap, start-page support,
  approximate page count, and hybrid time-window filtering;
- normal-user UI copy should explain that some platforms may return fewer or
  approximate results within the selected range;
- tests cover range validation and timeout behavior without assuming exact
  platform-native page/time filtering on every platform.

## CR-019 - Frontend Navigation And Page Entry Redesign

Date: 2026-06-15

Source: user console review

Module: frontend navigation and user flow

Requirement:

Redesign the console page entries and navigation around the monitoring task
loop: operations home, monitoring tasks, run center, report center, email
delivery, and administrator resource support. Resource Management and System
Configuration must stop relying on detached popover navigation and should be
usable on desktop, tablet, and mobile.

Reason:

The current navigation hierarchy is hard to understand, Resource Management and
System Configuration use popover menus that are difficult on mobile, and the
user identity/logout area has weak visual grouping.

Status: Accepted

Related tasks:

- Phase 12 in `TASKS.md`

Acceptance:

- login routes to an operations home;
- administrator and normal-user page entries follow the task loop;
- user identity and logout are grouped at the top right;
- Resource Management and System Configuration are expandable navigation
  groups, not hover-only popovers;
- mobile navigation works without hover.

## CR-020 - Frontend Design System

Date: 2026-06-15

Source: user console review and external plan audit

Module: frontend design system

Requirement:

Create a unified frontend design system covering visual language, interaction
patterns, and responsive layout. The design direction should be Apple-style:
clean, high-end, low-noise, enterprise-ready, and still dense enough for
repeated operational work.

Reason:

The current console feels plain and uneven. Visual hierarchy, button levels,
table density, empty states, loading states, floating menus, and responsive
behavior need to be governed as one system instead of being patched page by
page.

Status: Accepted

Related tasks:

- Phase 11 in `TASKS.md`

Acceptance:

- `UI_UX_GUIDELINES.md` defines visual, interaction, and responsive rules;
- `FRONTEND_ARCHITECTURE.md` defines breakpoints and implementation strategy;
- desktop, tablet, and mobile layouts have explicit behavior;
- row "more" menus are not clipped by scroll containers;
- pages use consistent spacing, status tags, toolbars, modals, and action
  hierarchy.

## CR-021 - Overview Operations Home Redesign

Date: 2026-06-15

Source: user console review

Module: overview and operations home

Requirement:

Replace the text-heavy overview with an operations home focused on task health,
run activity, report generation, email delivery, suspected negative lead trends,
and drilldown entry points. Long system-running and platform-status blocks
should be removed from the default home view or reduced to concise
administrator health summaries.

Reason:

The current overview is stretched by system status content, feels mostly
textual, and does not give operators a clear visual understanding of monitoring
activity or next actions.

Status: Accepted

Related tasks:

- Phase 13 in `TASKS.md`

Acceptance:

- operations home has visual metrics and drilldowns;
- system diagnostics are not the dominant first-screen content;
- account/platform availability appears as a concise business signal;
- normal users see their own task/report health, not administrator resource
  internals.

## CR-022 - Run Center Governance

Date: 2026-06-15

Source: user console review

Module: run center

Requirement:

Redesign the run center with pagination, filtering, visible/noise separation,
archive and restore operations, clearer run grouping, and reduced duplicate or
diagnostic noise in the default list.

Reason:

The current run center has no pagination, limited filtering, no practical
delete/hide behavior, and presents repeated or skipped records in a way that
feels noisy.

Status: Accepted

Related tasks:

- Phase 15 in `TASKS.md`

Acceptance:

- run list has pagination and useful filters;
- default list shows visible operational records first;
- archive hides a run without physically deleting it;
- administrators can view archived records;
- test runs can be hidden by default when noise filtering is enabled;
- logs remain refreshable, copyable, and downloadable.

## CR-023 - Report Center Task Grouping

Date: 2026-06-15

Source: user console review and confirmed user decision

Module: report center

Requirement:

Group reports by monitoring task by default, with a stable snapshot for reports
whose original task has been deleted or is otherwise unavailable. Use
`reports.job_snapshot_json` for report history context instead of relying only
on a nullable `job_id`.

Reason:

The current report center behaves like one flat list, which makes it difficult
to connect reports back to a law-firm monitoring task. Existing `reports.job_id`
can be nullable, so historical reports need independent task context.

Status: Accepted

Related tasks:

- Phase 18 in `TASKS.md`

Acceptance:

- report center groups by active task when `job_id` resolves;
- report center groups orphan reports using `job_snapshot_json`;
- deleted-task reports show business context such as law firm, platforms,
  keywords, and frequency;
- report preview and lead details still switch by selected report.

## CR-024 - Email Delivery Governance

Date: 2026-06-15

Source: user console review

Module: report email delivery

Requirement:

Prevent duplicate automatic emails for the same task and schedule window while
allowing explicit manual resend with audit-friendly delivery history.

Reason:

The user reported receiving multiple emails even though only one monitoring
task was configured. Current email sending is state-light and does not record
delivery attempts in a way that supports idempotency or operator review.

Status: Accepted

Related tasks:

- Phase 17 in `TASKS.md`

Acceptance:

- automatic delivery is idempotent by task and schedule window;
- manual resend is allowed but recorded separately;
- report center shows delivery history and latest status;
- email failure does not block report generation.

## CR-025 - Email Delivery Tracking Data Model

Date: 2026-06-15

Source: user confirmation after external plan audit

Module: data model and email delivery

Requirement:

Add an `email_delivery_logs` table to record automatic and manual report email
attempts. Use `send_window_key` for automatic-send idempotency.

Confirmed rules:

- `daily`: `{job_id}_{YYYY-MM-DD}`;
- `6h`, `12h`, and `cron`: `{job_id}_{YYYY-MM-DD}_{HH}`;
- automatic send: one successful or in-flight auto delivery per
  `job_id + send_window_key`;
- manual resend: use `send_type = manual_resend`, allow repeat attempts, and
  record the triggering user when available.

Reason:

The `reports` table only stores latest email status/error and cannot represent
multiple attempts, manual resend, or idempotent automatic delivery history.

Status: Accepted

Related tasks:

- Phase 16 in `TASKS.md`
- Phase 17 in `TASKS.md`

Acceptance:

- `DATA_MODEL.md` defines `email_delivery_logs`;
- `SCHEMA_MIGRATION.md` defines compatible migration steps;
- send-window generation matches the currently supported frequencies:
  `daily`, `6h`, `12h`, and `cron`;
- tests cover repeated scheduler triggers and manual resend.

## CR-026 - Run Visibility And Noise Filtering Data Model

Date: 2026-06-15

Source: user confirmation after external plan audit

Module: data model and run center

Requirement:

Add run visibility and run type fields to support archive, restore, and noise
filtering without physically deleting run records.

Confirmed fields:

- `crawl_runs.visibility TEXT DEFAULT 'visible'`, with values `visible` and
  `archived`;
- `crawl_runs.run_type TEXT DEFAULT 'scheduled'`, with values `scheduled`,
  `manual`, and `test`;
- `crawl_runs.archived_at TEXT NULL`;
- `crawl_runs.archived_by INTEGER NULL`.

Reason:

The run center needs to hide duplicate or low-value operational noise while
preserving execution history for administrators and audits.

Status: Accepted

Related tasks:

- Phase 14 in `TASKS.md`
- Phase 15 in `TASKS.md`

Acceptance:

- default run list shows `visibility = visible`;
- archive changes visibility but does not delete records;
- administrators can view archived records;
- test runs can be filtered separately from scheduled/manual runs;
- old run records are backfilled with `visible` and `scheduled` defaults.

## CR-027 - Frontend Technology Stack Decision

Date: 2026-06-15

Source: user confirmation after external plan audit

Module: frontend architecture

Requirement:

Use Vanilla JavaScript plus CSS custom properties for the console redesign.
Keep optional lightweight dependencies limited to focused charting or floating
menu placement needs. Do not migrate this round to Tailwind, Alpine.js,
Petite-Vue, React, Vue, or another major frontend stack.

Reason:

The existing console is vanilla JavaScript and no-build. A full framework
migration would add risk before the product flow, visual system, responsive
rules, run governance, report grouping, and email delivery behavior are
stabilized.

Status: Accepted

Related tasks:

- Phase 10 in `TASKS.md`

Acceptance:

- `FRONTEND_ARCHITECTURE.md` records the accepted stack;
- no new framework/build pipeline is required by Phase 10-18 plans;
- any optional lightweight library must be justified and recorded before code
  implementation.

## CR-028 - Global Phase 10-18 Plan Review Gate

Date: 2026-06-15

Source: user correction during plan-review workflow

Module: project governance and roadmap planning

Requirement:

Before generating a phase-specific execution goal for Phase 11-18, agents must
review the full Phase 10-18 roadmap as one connected plan. The review must
evaluate global executability, implementation granularity, cross-phase
dependencies, cross-phase impact risks, rollback boundaries, verification
coverage, and whether the roadmap can achieve the final console goal.

Reason:

A single-phase readiness review can incorrectly conclude that one small batch
is safe while missing whether the full roadmap is coherent, sufficiently
landable, and aligned with the monitoring task-loop product goal.

Status: Accepted

Related tasks:

- Phase 10.5 in `TASKS.md`

Acceptance:

- `AGENT_WORKFLOW.md` requires global roadmap review before phase-specific
  execution goals;
- `TASKS.md` includes a Phase 10.5 global review gate before Phase 11;
- `FRONTEND_ARCHITECTURE.md` documents cross-phase impact review points;
- `TEST_PLAN.md` includes a Phase 10.5 global plan review checklist;
- no Phase 11A-only goal is generated until the global Phase 10-18 review has
  no P0/P1 blockers.
