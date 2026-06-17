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
- CR-029: Login Session Success Reconciliation
- CR-030: Row Action Menu Clipping Regression Fix
- CR-031: Run Center Realtime Progress Visibility
- CR-032: Requirement Classification And Optimization Documentation Rules
- CR-033: Formal Console Full-Coverage Positive UI Optimization
- CR-034: Run Detail And AI Evaluation Traceability
- CR-035: Run Lifecycle Finalization And AI Stuck Recovery Regression Fix
- CR-036: Test And Local Email Delivery Safety Regression Fix
- CR-037: Role-Based Email Delivery Governance And Quotas
- CR-038: Sticky Close Controls For Scrollable Drawers
- CR-039: Governed Report Email Template Presets And Template Provenance
- CR-040: Formal Console Page-Level UI/UX Refinement
- CR-041: Minimum Usable Pilot Acceptance Gate
- CR-042: Frontend-Controlled Real Email Validation Window
- CR-043: Administrator Frontend Real Email Send Toggle
- CR-044: Mail Test Recipient Coverage And SMTP Acceptance Clarity
- CR-045: AI Evaluation Accuracy And Unevaluated Lead Status Clarity
- CR-046: Platform Account Avatar Safe Cache Display Regression Fix
- CR-047: Account Browser Environment Consistency
- CR-048: Report Center Lead Detail Information Architecture
- CR-049: Mail Configuration And Delivery History Action Hierarchy
- CR-050: Report Center Lead Status Filter Precision Regression Fix

## Entry Classification Rule

For CR-031 and later, every meaningful change request should state its
classification before implementation:

- `New Capability`: adds a new user-visible capability, data surface, API,
  integration, role behavior, or deployment behavior.
- `Existing Feature Optimization`: improves an existing feature without
  changing the product boundary. It must name the current feature, the observed
  limitation, the behavior that must be preserved, and the regression tests
  needed to keep the old workflow safe.
- `Regression Fix`: restores intended behavior after a verified breakage. It
  must describe the broken surface, expected baseline, and the minimal
  acceptance check that prevents recurrence.
- `Documentation Governance`: changes how requirements, tasks, decisions, or
  tests are recorded.

Each new CR should include background, purpose, scope boundary, non-goals when
useful, related tasks, and acceptance criteria. If classification, scope,
permission, security, deployment, account/profile, data-model, or customer
wording impact is unclear, keep the CR as `Proposed` or `Needs Confirmation`
until the user confirms it.

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

## CR-029 - Login Session Success Reconciliation

Date: 2026-06-16

Source: user report during platform account login validation

Module: server login flow and platform account UI

Requirement:

When a server-side QR login session reports QR failure, timeout, platform
error, or a disappeared browser session, the system must reconcile the result
against the same account/Profile using MediaCrawler login-state validation. If
the account/Profile is collectable, the login session and modal must show
login success instead of QR failure.

Reason:

During mobile QR login, the platform account can be genuinely logged in and
usable while the monitor-side QR polling session is closed or lost. The UI
currently trusts the QR session status first, so it can show failure even
though account detection later verifies a valid login state.

Status: Verified

Related tasks:

- Phase 6 in `TASKS.md`

Acceptance:

- QR-session failure does not override a successful same-account
  MediaCrawler account/Profile check;
- Douyin, Xiaohongshu, and Kuaishou use the same reconciliation behavior;
- verification/captcha/SMS states are not bypassed;
- frontend login modal displays success when the same account is already
  collectable;
- tests cover success reconciliation and non-success fallback behavior.

## CR-030 - Row Action Menu Clipping Regression Fix

Date: 2026-06-16

Source: user screenshot feedback in the monitor console

Module: frontend row action menus

Requirement:

The row "more" action menus in Platform Accounts, Monitoring Tasks, and AI
Evaluation Rules must render as page-level fixed floating menus. They must not
be clipped, hidden, or visually covered by table scroll containers, sticky
columns, or card boundaries.

Reason:

The screenshots showed the "more" menu content being visually obstructed on
multiple pages. These menus are repeated operational controls, so clipping
creates an unreliable path for account maintenance, task maintenance, and AI
rule maintenance.

Status: Verified

Related tasks:

- Phase 11C in `TASKS.md`

Acceptance:

- account, monitoring-task, and AI-rule "more" menus are rendered through
  page-level floating containers;
- table rows keep only the trigger buttons, not the popup menu content;
- menus remain positioned inside the viewport and close on outside click,
  escape, page change, or successful action;
- tests protect against reintroducing inline row menu containers.

## CR-031 - Run Center Realtime Progress Visibility

Date: 2026-06-16

Source: user report during live run diagnosis

Module: run center, crawler execution progress, AI evaluation progress

Type: Existing Feature Optimization

Background:

The Run Center already has columns for collected count, new count, suspected
negative count, high-risk count, and manual-review count. During long
MediaCrawler runs, however, the table reads `crawl_runs.summary` and the
summary is initialized to zero until the platform subprocess exits, output
files are collected, and ingestion finishes. The frontend also stops its active
run polling after a short fixed window. Operators can therefore see crawler
logs and output files growing while the Run Center still appears to have no
collected results.

Purpose:

Make active runs visibly progress in the Run Center without misrepresenting
provisional crawler output as final ingested results. Operators should be able
to tell whether a run is collecting, ingesting, evaluating with AI, waiting on
report/email work, timed out with partial results, or complete.

Requirement:

- While a platform crawler subprocess is still running, the monitor should
  periodically read safe MediaCrawler output files or equivalent progress
  signals and update the running run summary with provisional collection
  progress.
- Provisional collection progress must be clearly distinguishable from final
  ingested counts. In-flight, partially written, missing, or malformed output
  files must not crash the run or produce a false final count.
- Final collected, filtered, excluded, and new counts remain governed by the
  existing collect-and-ingest step after the platform attempt exits, unless a
  later data-model decision explicitly introduces safe partial ingestion.
- During AI evaluation, the monitor should update progress in batches or time
  intervals so suspected negative, high-risk, manual-review, and evaluated
  counts no longer remain stale until the entire evaluation loop finishes.
- The frontend Run Center should keep polling while visible runs remain active,
  not only for a short fixed number of rounds, and should render active
  progress states without clipping or responsive layout regressions.
- Owner/workspace scope, run logs, stop action, archive/restore behavior,
  timeout behavior, and customer-safe error wording must be preserved.

Non-goals:

- Do not modify MediaCrawler platform implementations unless a later task
  proves an output/progress contract is missing.
- Do not introduce high-concurrency worker orchestration, complex account
  rotation, captcha/SMS bypass, or streaming web sockets for V1 unless
  separately approved.
- Do not expose raw output paths, crawler commands, cookies, profile paths, or
  platform secrets in customer-facing UI.

Status: Accepted

Related tasks:

- Phase 19 in `TASKS.md`

Acceptance:

- A simulated long platform crawl with growing output files updates Run Center
  provisional collection progress before the subprocess exits.
- Malformed or partially written output files are ignored or retried safely and
  do not mark final counts.
- After platform completion and ingestion, final collected/new counts match the
  existing ingest semantics and do not duplicate content.
- AI evaluation progress updates incrementally and final negative, high-risk,
  and manual-review counts remain accurate.
- Frontend polling continues while runs are active and stops after active runs
  finish.
- Desktop, tablet, and mobile Run Center layouts show active progress without
  overlapping controls or hidden actions.

## CR-032 - Requirement Classification And Optimization Documentation Rules

Date: 2026-06-16

Source: user request for future requirement-documentation planning

Module: project governance and agent workflow

Type: Documentation Governance

Background:

The project now receives both new product capabilities and refinements to
existing features. Treating both as generic "new requirements" makes it harder
to see whether a request expands product scope or optimizes an existing
workflow that must preserve previous behavior.

Purpose:

Standardize future requirement documentation so agents first classify a request
as a new capability, existing feature optimization, regression fix, or
documentation-governance change, then record background, purpose, scope
boundary, non-goals, related tasks, and acceptance criteria before coding.

Requirement:

- Future CR entries should include a `Type` field.
- Existing feature optimizations must name the existing feature, current
  limitation, preserved behavior, and regression-test boundary.
- New capabilities must identify added product/API/data/UI/deployment surface,
  confirmation needs, and non-goals.
- Regression fixes must identify the broken behavior, expected baseline, and
  recurrence-prevention test.
- Documentation-governance changes must update the relevant workflow or check
  documents and remain backward-compatible with historical CR entries.

Status: Verified

Related tasks:

- Phase 19A in `TASKS.md`

Acceptance:

- `CHANGE_REQUESTS.md` documents the classification rule for CR-031 and later.
- `AGENT_WORKFLOW.md` tells agents how to classify and bound new requirements
  and optimization requests.
- `TRACEABILITY.md` links this governance requirement to a documentation check
  path.

## CR-034 - Run Detail And AI Evaluation Traceability

Date: 2026-06-16

Source: user request after run-center and report-center workflow review

Module: run center, AI evaluation, lead detail, report center navigation

Type: Existing Feature Optimization

Background:

The Run Center currently shows run rows, counts, failure reasons, and crawler
logs. AI evaluation records are saved in `ai_evaluations`, and `/leads` can be
filtered by `run_id` or `report_id`, but the Run Center has no entry for
per-item AI evaluation details. The Report Center shows final reports and line
details, yet those line details are tied to report preview behavior and are not
obvious to discover. During a running task, AI evaluations can already exist
before a report is generated, so forcing operators to switch to the Report
Center creates a split process: collection and crawler logs in one page,
evaluation evidence and leads in another.

Current feasibility finding:

- The AI input business payload is constructed at evaluation time by
  `build_evaluation_payload(job, content, comments)`.
- OpenAI-compatible and Anthropic-compatible calls build request messages from
  the prompt plus that payload.
- `ai_evaluations` stores final structured fields and a redacted
  `raw_response`, but it does not persist the exact prompt snapshot, request
  message snapshot, input payload snapshot, provider/model metadata, duration,
  or per-attempt error detail.
- Therefore historical exact input/output traceability is not fully possible
  for old evaluations; new evaluations need a trace snapshot model.

Purpose:

Give operators a unified per-run detail view where they can inspect the full
run lifecycle and drill into every AI evaluation record, including business
input, prompt/request snapshot, structured output, raw/redacted model response,
and failure/fallback details where permitted.

Requirement:

- Add a Run Center "Run Detail" entry for each run. The detail surface should
  be grouped by `run_id` and show collection, ingestion, AI evaluation, report
  generation, and email delivery as one lifecycle.
- Add an AI Evaluation tab or section inside the run detail surface. It should
  list every evaluated or evaluation-pending content item for that run, with
  platform, source keyword, title, evaluation status, related/negative flags,
  risk level, reason, evidence quotes, recommended action, and evaluated time.
- Each AI evaluation row should have a detail view showing:
  - business input: target law firm, aliases, exclude words, platform,
    keyword, title, description, author, URL, publish time, comment counts, and
    sampled comments;
  - prompt/request snapshot: prompt or prompt version, provider/model, and the
    redacted request payload/messages used for the model call;
  - output snapshot: structured result, raw/redacted model response, parsing
    or validation error, fallback reason, duration, and timestamps.
- For old evaluations without trace snapshots, show an explicit
  "历史记录未保存完整入参/出参" state instead of reconstructing uncertain input
  as exact truth.
- Report Center should remain the final report and email-delivery surface, but
  report rows should expose an explicit "view leads" path. It should link back
  to the originating run detail when available.
- Preserve owner/workspace scope. Normal users may inspect their own run's
  business-safe evaluation results, while administrator-only debug fields
  require a clear permission boundary.
- Redact or omit API keys, authorization headers, cookies, proxy credentials,
  profile paths, real server paths, and raw account/session data from all
  customer-facing responses and stored trace views.

Confirmed decisions so far:

- AI evaluation trace retention must be an administrator-configurable runtime
  setting, not a hard-coded value. The default should be 30 days.
- Normal users should not see raw model responses. They should see only
  structured business results and business-safe summaries.
- Normal users should not see full prompt snapshots, request payload snapshots,
  or administrator debug metadata. They should see only business-safe
  input/output summaries for their own runs.
- Administrators may see redacted raw model responses for diagnosis. Unredacted
  raw model responses must not be exposed to any role.
- Trace snapshot size limits are storage and API guardrails, not business
  rules. The accepted default guardrails are: each trace is about 64KB, prompt
  snapshot up to 16KB, request snapshot up to 24KB, response snapshot up to
  24KB, and sampled comments up to 20 comments with each comment truncated to a
  safe per-comment length. Oversized snapshots should be truncated, marked with
  `truncated=true`, and must not block AI evaluation, report generation, or run
  finalization.
- Trace snapshots should be stored in a new `ai_evaluation_traces` table with
  redacted/capped JSON fields, linked to `run_id`, `raw_content_id`, and
  `ai_evaluations.id`.

Non-goals:

- Do not expose AI API keys, endpoint credentials, cookies, profile paths, or
  proxy secrets.
- Do not make Report Center the primary place to observe running AI evaluation
  progress.
- Do not claim old evaluations have exact input snapshots when they were not
  persisted.
- Do not introduce a new frontend framework or build pipeline.

Status: Accepted

Related tasks:

- Phase 20 in `TASKS.md`

Acceptance:

- Run Center exposes a per-run detail surface grouped by run record.
- The AI Evaluation tab lists all evaluation candidates/results for the run,
  including records before a report exists.
- New AI evaluations persist redacted trace snapshots sufficient to inspect
  input, prompt/request, structured output, raw/redacted response, and failure
  details.
- Old evaluations without trace snapshots show an explicit limited-context
  state.
- Normal-user and administrator views respect the confirmed permission
  boundary.
- Report Center has a clear "view leads" path and can link back to run detail
  when a report has `run_id`.

## CR-035 - Run Lifecycle Finalization And AI Stuck Recovery Regression Fix

Date: 2026-06-16

Source: live task/run diagnosis and follow-up review of
`docs/RUN_AI_STUCK_BUG_TODO.md`

Module: run lifecycle, AI evaluation fallback, stale-run recovery, report
generation, run center status safety

Type: Regression Fix

Background:

Live task `9297` and run `8317` showed that platform collection had completed
and AI evaluation had processed 250 of 271 collected contents, but
`crawl_runs.status` remained `running`, `finished_at` stayed null, no report
was generated, no resource locks remained, and `crawl_runs.job_id` was null
while `summary.job_id` still pointed to `9297`.

This exposes a gap in the completed Phase 7 run/report/AI behavior: AI failure
or interruption should degrade to manual review and should not block report
generation or leave a run indefinitely running. It also exposes missing
coverage around job identity persistence, background-task finalization,
stale-run recovery before deadline, and partial AI report generation.

Completed phase handling:

Phase 7 remains a historical verification snapshot. This CR does not rewrite
Phase 7 as incomplete. It creates a follow-up regression-fix phase under the
same responsibility area so the newly observed production-like failure can be
fixed and tested without mixing it into the Phase 19 progress-visibility
enhancement.

Purpose:

Restore the V1 guarantee that collection and reports survive AI failure. Runs
must finalize into a terminal or clearly interrupted state, partial collected
results must remain visible, and no disappeared background task should wait for
a multi-hour timeout before the UI stops showing ordinary `running`.

Requirement:

- New runs must persist `crawl_runs.job_id`; preventing future `job_id` gaps is
  the primary fix. Legacy reads must tolerate rows where only `summary.job_id`
  is available, and historical backfill is only a dry-run-first compatibility
  fallback.
- Run finalization must be centralized, idempotent, and concurrency-safe across
  success, failure, timeout, cancellation, interruption, and partial AI/report
  paths.
- Run lifecycle progress must capture step-level state and safe step return
  values/errors so the frontend can explain whether the task is collecting,
  ingesting, evaluating with AI, generating a report, sending email, retrying,
  interrupted, timed out, or failed.
- Interruption diagnosis must not rely only on a fixed elapsed-time rule. The
  monitor should first inspect live task evidence, resource locks, last
  progress heartbeat, last step, retry state, and redacted last error before it
  marks a run interrupted.
- Retry policy must be explicit before timeout/fallback behavior: retryable
  platform/browser/network/AI failures should be retried within the run
  deadline, while non-retryable failures or deadline exhaustion should finalize
  into a customer-safe terminal state.
- Per-item AI invalid JSON, timeout, or unexpected exception must save
  `pending_review` and continue when the run deadline allows.
- Active finalization may create `pending_review` fallback rows for known
  not-yet-evaluated candidates before report generation.
- Active finalization applies to runs handled by the fixed runtime path after
  deployment. Historical stuck/interrupted runs, including run `8317`, must not
  be auto-repaired by startup or scheduler recovery. They require a separate
  dry-run repair workflow, explicit operator approval, database backup, and
  rollback notes before AI rows, reports, or terminal status are changed.
- Running and final summaries must include AI evaluation progress counts, such
  as total candidates, successful evaluations, failed/fallback evaluations,
  pending-review count, and unresolved count where available.
- Stale `running` runs with no live task/lock/recent-progress evidence must be
  recovered before the original wall-clock deadline.
- Partial AI/manual-review state must still produce a report when collected
  content exists.
- Background exceptions, progress messages, finalization errors, and recovery
  messages must be redacted before storage or display.
- Historical run `8317` must not be modified without explicit operator
  confirmation, backup, and rollback plan.

Open confirmation items:

- Confirmed: `interrupted` is a first-class terminal `crawl_runs.status`.
- Confirmed: active finalization may auto-create `pending_review` rows for
  unresolved AI candidates; historical interrupted runs must not rewrite AI
  rows without explicit operator approval.
- Confirmed: run summaries should include AI evaluation success/failure and
  unresolved counts.
- Confirmed: future `job_id` gaps must be prevented first; historical backfill
  is fallback-only.
- Confirmed: stale recovery uses lifecycle evidence before elapsed time:
  live task evidence, resource locks, last heartbeat, last completed step, and
  redacted last error.
- Confirmed: default stale-heartbeat grace period is 10 minutes.
- Confirmed: retry policy reuses existing crawler retry controls for
  platform/browser/network failures and applies a separate AI item retry budget
  within the run deadline.
- Confirmed: `ai_item_timeout_seconds` defaults to 120 seconds and is capped by
  the remaining run deadline.

Non-goals:

- Do not implement CR-034/Phase 20 raw AI prompt/request/response traceability.
- Do not change MediaCrawler platform implementations unless no safe external
  progress or finalization signal exists.
- Do not introduce high-concurrency worker orchestration.
- Do not bypass captcha, slider, SMS, or platform verification.
- Do not expose API keys, cookies, profile paths, proxy credentials, provider
  endpoints, local paths, crawler commands, or raw runtime data.

Status: Accepted

Related tasks:

- Phase 7.1 in `TASKS.md`
- Phase 19B-19D only for the separate progress-visibility enhancement

Acceptance:

- New runs persist `crawl_runs.job_id`; legacy rows with `summary.job_id` remain
  readable, stoppable, and safely backfillable when resolvable.
- A simulated run with 271 collected contents and AI interruption at item 251
  does not remain `running`.
- AI item failure, timeout, or invalid JSON creates `pending_review` and allows
  the loop/report to continue when safe.
- Repeated or concurrent finalization calls produce one terminal state and do
  not re-open or corrupt a run.
- Stale `running` rows before deadline recover as the confirmed terminal or
  interrupted state without releasing unsafe secrets.
- Partial AI/manual-review state can generate a report and preserve owner and
  workspace scope.
- Historical run repair requires explicit operator approval, database backup,
  and rollback notes.

## CR-036 - Test And Local Email Delivery Safety Regression Fix

Date: 2026-06-16

Source: user report after receiving two unexpected `日报 海安律所` emails while
no operator-visible task was running

Module: report email delivery, automated tests, local diagnostics, operations
safety

Type: Regression Fix

Background:

The user received two real emails with subject `日报 海安律所` after the console
appeared to have no active task. Read-only inspection found that the emails
were distinct messages, not duplicate mailbox downloads:

- `C:/Users/Administrator/Desktop/日报 海安律所.eml` was sent at
  `2026-06-16T07:27:11Z` with attachments
  job_9686_run_8380_20260616_152702.xlsx and
  job_9686_run_8380_20260616_152702.md;
- `C:/Users/Administrator/Desktop/日报 海安律所.2eml.eml` was sent at
  `2026-06-16T08:55:33Z` with attachments
  job_9759_run_8447_20260616_165528.xlsx and
  job_9759_run_8447_20260616_165528.md;
- `email_delivery_logs` contains sent automatic rows for `job_id=9686` /
  `report_id=3959` and `job_id=9759` / `report_id=3998`;
- the corresponding report artifact files still exist under
  `monitor_data/reports/`;
- current `monitor_jobs`, `crawl_runs`, and `reports` rows for those
  job/run/report IDs no longer exist, which explains why the operator could not
  see a matching active task in the console.

The strongest local trigger evidence is
`tests/test_monitoring_mvp.py::test_run_job_blocks_platform_when_login_window_is_open`.
That test creates a temporary `海安律所` Douyin job with empty task recipients,
simulates `login_window_open=True`, blocks the MediaCrawler subprocess, and
calls `run_monitor_job(job["id"])`. It does not mock the report email delivery
path. `run_monitor_job` can still create a failed-platform report and call
`send_report_with_delivery_log(..., send_type="auto")`.

Root cause:

The completed Phase 17 email delivery governance correctly added delivery logs
and automatic-send idempotency for normal scheduler windows, but it did not add
a cross-cutting test/local safety boundary for real SMTP side effects. Three
gaps combined:

- tests that invoke `run_monitor_job` can reach the real mailer unless each
  test manually monkeypatches the delivery path;
- task recipients can be empty while `send_report` falls back to global
  `email_configs.default_recipients`, so a temporary test job can still send to
  real configured recipients;
- the UI labels do not make the precedence obvious: SMTP `sender` is the
  from-address, task recipients are task-specific delivery targets, and global
  default recipients are only the fallback when a task has no recipients;
- `email_delivery_logs.recipients_json` currently records only explicit
  `job.recipients`, not the final effective recipients after default-recipient
  fallback, so the log can show `[]` even when a real email was delivered to
  global defaults.

Completed phase handling:

Phase 17 remains a historical verification snapshot for automatic-send
idempotency and delivery-history behavior. This CR creates a Phase 17.1
follow-up regression fix under the same email-delivery responsibility area.
It does not rewrite Phase 17 as incomplete and does not belong to Phase 19 run
progress or Phase 20 AI traceability.

Purpose:

Prevent automated tests, local diagnostics, and accidental local execution from
sending real external report emails silently. At the same time, preserve
explicit real-email validation, production report email delivery, manual
resend, delivery history, and the V1 guarantee that email failure does not
block report generation.

Requirement:

- Add a single email-delivery safety gate used by automatic report sends,
  manual resend, and test-mail paths where appropriate. Routine automated tests
  and local diagnostics must not create hidden real SMTP side effects.
- Keep an explicit real-email validation path for production and pilot
  confidence. A real send is acceptable only when the operator intentionally
  starts a real-mail validation or the deployment is configured for real
  production/pilot sending.
- The sender, trigger source, task/report/run context, effective recipients,
  and delivery result must be visible enough that an operator can understand
  why an email was sent even after the task/run record is no longer active.
- Clarify recipient precedence in the product surface: task recipients override
  global default recipients; global default recipients are a fallback only; the
  SMTP sender is separate from all recipient fields.
- Ensure the automated test suite cannot call `smtplib.SMTP`,
  `smtplib.SMTP_SSL`, or `EmailMessage.send_message` through an unmocked path.
  Tests that exercise report generation should use fake delivery outcomes.
- Update `test_run_job_blocks_platform_when_login_window_is_open` and any other
  `run_monitor_job` tests so they assert no real mailer call occurs unless the
  test is explicitly about email delivery.
- Record the final effective recipients in delivery logs, including recipients
  derived from default-recipient fallback. If delivery is skipped by the safety
  gate, record a customer-safe skipped status and reason without SMTP secrets.
- Define recipient metadata explicitly: `recipients_json` is the task/request
  recipient snapshot, `effective_recipients_json` is the final resolved
  delivery target, `effective_recipient_source` identifies where that target
  list came from, and `trigger_source` identifies why the send path ran.
- Keep the existing duplicate automatic-send idempotency behavior for
  scheduler windows.
- Keep manual resend available in production/pilot mode, but ensure local/test
  manual resend cannot silently send real mail unless the final confirmed
  safety policy allows that explicit validation path.
- Add a read-only remediation note for historical orphan email logs and report
  artifacts. Do not delete or mutate historical files/logs without explicit
  operator approval.

Confirmed decisions:

- Confirmed: real email delivery remains available only as intentional
  production/pilot delivery or an explicit validation action; routine automated
  tests and local diagnostics must not send hidden real mail.
- Confirmed: the delivery safety gate is environment-controlled and surfaced as
  a deployment-locked read-only runtime setting.
- Confirmed: local manual resend may only send real mail when the explicit
  real-mail validation policy allows it; otherwise it records a non-sending
  validation/skipped outcome.
- Confirmed: historical orphan delivery logs `60` and `81`, the two `.eml`
  files, and related report artifacts are preserved as evidence by default and
  must not be mutated without backup and explicit operator approval.

Non-goals:

- Do not remove production automatic report delivery.
- Do not remove global default recipients; they remain valid production
  configuration, but their use must be visible in effective-recipient logs.
- Do not change report generation, report wording, scheduler frequency, or
  MediaCrawler platform behavior.
- Do not implement the deferred CR-037 normal-user quota or role-governance
  layer as part of this safety fix.
- Do not send any new real email while implementing or testing this fix unless
  explicitly approved by the operator.
- Do not delete the two existing `.eml` files, report artifacts, database rows,
  or delivery logs without explicit operator approval.

Status: Verified

Related tasks:

- Phase 17.1 in `TASKS.md`

Acceptance:

- Running the full automated test suite with a real SMTP configuration present
  cannot send external email unless the explicit real-email opt-in is enabled.
- The `login_window_open` regression test completes without invoking the real
  SMTP client and still verifies the failed-platform report behavior.
- Automatic report delivery records the final effective recipients, including
  default-recipient fallback, in `email_delivery_logs`.
- When the safety gate blocks delivery, reports still generate and delivery
  logs show `skipped` or a confirmed equivalent state with a customer-safe
  reason.
- Production/pilot mode with explicit opt-in still allows automatic delivery,
  manual resend, and test mail.
- Delivery logs distinguish original task/request recipients from final
  effective recipients and the effective-recipient source.
- Documentation and tests clearly distinguish production real SMTP validation
  from local automated tests and diagnostics.

Verification:

- Verified on 2026-06-18 through Phase 17.1A-D implementation and tests.
  Automated/local/report-delivery paths are non-sending by default, the SMTP
  tripwire protects the test suite, delivery logs persist effective recipients
  and trigger source, preflight and UI copy explain recipient precedence, and
  historical orphan evidence review is dry-run only with `mutations_attempted=0`
  plus backup/approval/rollback gates.

## CR-037 - Role-Based Email Delivery Governance And Quotas

Date: 2026-06-16

Source: user decision discussion during CR-036 confirmation

Module: users and permissions, email delivery, report center, runtime strategy

Type: New Capability

Background:

CR-036 focuses on preventing hidden real-email side effects from tests, local
diagnostics, and accidental execution. During confirmation, the user clarified
a broader product direction: email sending should eventually be governed by
role and administrator policy. Administrators should keep the highest authority
to configure and use mail delivery, while normal users may be limited by
administrator-defined rules such as whether they can send or resend reports and
how many sends are allowed per day.

Purpose:

Add a future permission and quota layer for report email delivery without
overloading the immediate CR-036 safety fix. This should make email sending
auditable, role-aware, and controllable by administrators while keeping the V1
task/report loop simple.

Requirement:

- Administrators should be able to configure whether normal users may send or
  resend report emails.
- Administrators may need per-user, per-day, or per-task send quotas for normal
  users.
- Manual resend should respect the user's role and the administrator policy.
- Automatic report delivery should remain governed by task schedule and system
  email configuration, with clear ownership and audit records.
- The UI location is not confirmed. Candidate surfaces include a future Users
  And Permissions page, Runtime Strategy, or a dedicated Email Governance
  section.

Non-goals:

- Do not implement this in CR-036/Phase 17.1.
- Do not block the immediate hidden-email safety fix on quota design.
- Do not add a heavy multi-tenant permission model unless a later confirmed CR
  expands the product boundary.

Status: Deferred

Related tasks:

- Future phase to be created after user confirms the scope and UI location.

Acceptance:

- Administrator can define normal-user email send/resend policy.
- Normal-user manual resend follows the configured policy and returns clear
  messages when blocked.
- Send attempts are counted and auditable without exposing SMTP secrets.
- Existing administrator report delivery and manual resend remain available
  according to confirmed administrator permissions.

## CR-033 - Formal Console Full-Coverage Positive UI Optimization

Date: 2026-06-16

Source: user request to implement the full-coverage frontend positive
optimization baseline on the latest `main` formal console.

Module: formal monitor frontend

Type: Existing Feature Optimization

Background:

The earlier static prototype improved visual direction but did not preserve
every formal-console page, button, floating menu, drawer, and business
interaction. The accepted implementation baseline requires applying only
positive UI/UX improvements to the latest formal frontend while preserving the
existing task, run, report, email, and administrator-governance workflows.

Purpose:

Improve the formal console's visual freshness, commercial polish, loading
feedback, dashboard information priority, floating-menu reliability, and
responsive behavior without deleting or weakening existing functions.

Preserved behavior:

- Login, operations home, monitoring tasks, platform accounts, proxies, AI
  access, AI evaluation rules, mail configuration, mail templates, runtime
  strategy, run center, report center, and system diagnostics remain separate
  formal pages.
- Platform-account QR login, browser login, Cookie login, login history,
  account details, filters, batch actions, and row more menu remain available.
- Task drawer fields, run log drawer, report preview drawer, delivery history,
  download links, resend confirmation, resource forms, AI test modal, mail test
  modal, and email-template iframe preview remain available.
- Administrator-only resource/system pages remain hidden from normal users by
  the existing permission logic.

Scope boundary:

- Frontend-only changes in `api/monitor_web/index.html`.
- No backend API, database schema, permission model, crawler, AI provider,
  SMTP, or production data changes.
- No new framework or build step.

Non-goals:

- Do not merge Resource Management or System Configuration pages.
- Do not replace existing floating menus with side business drawers.
- Do not simplify platform-account login into a generic configuration dialog.
- Do not introduce dashboard metrics that require new backend fields.

Status: Verified

Related tasks:

- Formal Console Full-Coverage Positive UI Optimization in `TASKS.md`

Acceptance:

- Dashboard data appears before the 01-05 shortcut flow, and mobile dashboard
  density is reduced.
- Loading states use page-shaped skeletons or local loading notes.
- Secondary drawers and modals keep their original controls while showing
  button-level loading feedback for account login, resource saves, tests, and
  template preview actions.
- Account, task, AI rule, and report row menus render as unclipped floating
  menus.
- All formal pages are reachable on desktop and tablet/mobile navigation.
- Core drawers/modals open and close through visible close, Escape, and
  backdrop where supported by the existing modal contract.
- Browser checks cover desktop 1440px, tablet 1024px, and mobile 390px without
  horizontal page overflow.

## CR-038 - Sticky Close Controls For Scrollable Drawers

Date: 2026-06-16

Source: user report that long scrollable task drawers move the top-right close
button out of view, forcing the operator to scroll back to the top or click the
backdrop.

Module: formal monitor frontend drawers and modals

Type: Existing Feature Optimization

Background:

Long configuration drawers, such as task editing, can scroll inside the modal
body. The footer actions already remain reachable near the bottom, but the
drawer header and top-right close button scroll away with the content. Backdrop
click-to-close is useful and should stay available, but it should not be the
only convenient close path after the operator scrolls down.

Purpose:

Keep dismiss controls reachable throughout long drawer workflows while
preserving the existing drawer layout, backdrop-close behavior, and bottom
action bars.

Requirement:

- Make drawer/modal close controls remain visible while long drawer content is
  scrolled.
- Preserve backdrop click-to-close where it already exists.
- Preserve bottom action bars and existing save/close buttons.
- Apply the behavior consistently to long formal-console drawers including task
  edit, account, proxy, AI profile, mail config, mail template, run log, and
  report preview surfaces where applicable.
- Ensure sticky headers have a solid background, border/shadow separation, and
  z-index high enough to avoid being covered by form content.
- Verify desktop, tablet, and mobile viewports so the sticky close control does
  not overlap content, scrollbars, or bottom action bars.

Non-goals:

- Do not redesign drawer information architecture.
- Do not remove backdrop close.
- Do not change backend APIs, permissions, data model, crawler behavior, AI
  behavior, or SMTP behavior.

Status: Verified

Related tasks:

- Formal Console Drawer Close Accessibility Follow-up in `TASKS.md`

Verification:

- Implemented in `api/webui/monitor/monitor.css` with shared sticky
  drawer/modal headers, solid background, border/shadow separation, fixed close
  button sizing, and adjusted in-drawer sticky action-bar boundaries.
- Covered by `tests/test_monitoring_mvp.py` through CR-038 frontend hook checks
  for the required drawers, close handlers, backdrop handlers, sticky header
  CSS, floating-menu layering, sticky footer hooks, and Escape close support.
- Browser checked at desktop, tablet, and mobile sizes for task edit, account,
  proxy, AI profile, mail config, mail template, run log, and report preview
  drawers, including close-button reachability after scrolling, footer
  reachability, backdrop close, Escape close, and no horizontal page overflow.

Acceptance:

- In a long task drawer, scrolling down keeps the top-right close button visible
  and clickable.
- The same pattern works for other long drawers/modals that use the shared
  drawer structure.
- Clicking the backdrop still closes drawers where that behavior already
  existed.
- Browser checks at desktop/tablet/mobile sizes show no severe overlap or
  clipped close controls.

## CR-039 - Governed Report Email Template Presets And Template Provenance

Date: 2026-06-16

Source: user review of mail template behavior after comparing template preview,
active template state, and a received real report email.

Module: report email templates, report snapshots, email delivery logs

Type: Existing Feature Optimization

Background:

Current mail delivery resolves templates by task-bound template first and falls
back to the currently active global template. Formal sending then injects the
generated report HTML into the resolved template. The mail-template editor
preview uses sample data, so it may not match a historical real send if the
operator is looking at a different template or a later active-template state.

Free-form HTML editing also makes it possible to omit required report fields
such as `{report_html}` or `{report_body}`. In that case the email can be sent
successfully but miss the actual generated report body. Report snapshots and
delivery logs do not currently record the effective template id, template name,
or whether the template came from a task binding or global active-template
fallback, so historical diagnosis is difficult after templates change.

Purpose:

Make report emails predictable, traceable, and harder to misconfigure by
recording the exact template used for each send and moving future template
management toward controlled preset styles that always include the generated
report body.

Requirement:

- Record the effective email template id, template name, subject template, and
  template source for each report/email send, distinguishing task-bound template
  from global active-template fallback.
- When implemented in the same batch as CR-036, land this provenance metadata
  with the Phase 17.1C delivery metadata migration to avoid repeated
  `email_delivery_logs` schema churn. The preset-style product work may remain
  in Phase 17.2.
- Include template provenance in report snapshots and email delivery logs so an
  operator can later explain why a received email differed from a currently
  previewed template.
- Make preview semantics explicit: template editor preview uses sample data,
  while report sends use the generated report HTML for that run.
- Add validation or guarded rendering so report emails cannot silently omit the
  generated report body. At minimum, warn or block when a custom template has no
  `{report_html}` or `{report_body}` placeholder before free-form editing is
  removed.
- Move the product direction away from arbitrary free-form HTML editing and
  toward a small set of administrator-selectable preset styles. Preset styles
  should control the visual wrapper, while the report body comes from the
  system-generated report output.
- Preserve subject template flexibility if it remains useful, but make required
  body fields system-controlled.

Non-goals:

- Do not redesign the report generation algorithm in this follow-up.
- Do not remove historical templates or rewrite old email bodies.
- Do not expose SMTP secrets, API keys, local paths, cookies, proxy credentials,
  or raw platform credentials in template provenance.
- Do not make normal users edit template HTML.

Status: Verified

Related tasks:

- Phase 17.2 Report Email Template Governance in `TASKS.md`

Acceptance:

- A delivered email record shows which template was used and whether it was
  task-bound or inherited from the active global template.
- Report snapshots include enough template metadata to diagnose historical
  sends after templates are edited later.
- A template that would omit the generated report body is blocked or clearly
  warned before use.
- The mail-template UI direction is preset-style selection with
  system-controlled report body insertion, not unrestricted HTML editing as the
  long-term product model.

Verification:

- Verified on 2026-06-18 through Phase 17.2A-C implementation and tests. Report
  snapshots and delivery logs record effective template provenance; delivery
  history shows send-time template/source; custom templates without
  `{report_html}` or `{report_body}` are blocked on save; legacy templates
  remain readable and append the generated report body during preview/send; and
  the template drawer offers governed preset wrappers that preserve the
  system-generated report body.

## CR-040 - Formal Console Page-Level UI/UX Refinement

Date: 2026-06-16

Source: user request after comparing the static prototype with the latest
formal `main` console and asking for a complete, executable documentation plan
before any code changes.

Module: formal monitor frontend

Type: Existing Feature Optimization

Background:

CR-033 completed a verified frontend-only positive optimization pass and
preserved the formal `/monitor` console's pages, buttons, drawers, floating
menus, loading states, and responsive foundations. A later review compared the
static prototype at `design-prototypes/console-review/` with the latest formal
frontend and found that the prototype has useful visual ideas but cannot be
used as a functional baseline because it omits or simplifies many formal
business workflows.

The latest formal frontend is functionally stronger than the prototype, but it
still has design debt: the Operations Home can still feel like onboarding
because of the `01-05` shortcut block, navigation hierarchy can be clearer,
many pages use similar white-card surfaces, status labels are not yet a fully
unified business language, and dense administrator workflows can be made more
commercial, readable, and efficient without removing functionality.

Purpose:

Create a fine-grained, page-level UI/UX refinement roadmap for the formal
console so later implementation can improve visual quality, commercial polish,
information hierarchy, interaction efficiency, responsive behavior, and state
feedback while preserving every existing business workflow.

Requirement:

- Use `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` as the execution planning
  reference for this CR.
- Treat the formal `/monitor` frontend as the only implementation baseline.
- Treat the static prototype as visual reference only, not as a functional
  baseline.
- Preserve all formal pages, buttons, filters, batch actions, row actions,
  floating menus, drawers, modals, loading feedback, confirmation flows, role
  visibility rules, and task/run/report/email/account workflows.
- Split implementation into small workstreams:
  global shell/design tokens, navigation hierarchy, Operations Home,
  Monitoring/Task Drawer, Platform Accounts, Proxies, AI Access, AI Rules,
  Mail Configuration, Mail Templates, Runtime Strategy, Run Center, Report
  Center, System Diagnostics, Login, and cross-viewport verification.
- For each page, define what must be preserved, what may be visually refined,
  what must not be changed, how it should be tested, and what acceptance means.
- Prevent the prototype-observed layout failure from entering production: no
  dashboard card, closed-loop track, dense status card, or operational summary
  may squeeze Chinese text into one-character vertical columns, overlap
  neighboring content, or hide required actions at the accepted desktop,
  tablet, or mobile viewports.
- Keep the work frontend-only unless a later accepted CR explicitly changes
  backend/API/data-model scope.

Preserved behavior:

- Login, Operations Home, Monitoring Tasks, Platform Accounts, Proxies, AI
  Access, AI Evaluation Rules, Mail Configuration, Mail Templates, Runtime
  Strategy, Run Center, Report Center, and System Diagnostics remain separate
  formal pages.
- Platform-account QR login, local-window fallback where allowed, Cookie login,
  login records, account identity/details, filters, batch actions, and row more
  menu remain available.
- Task drawer fields, administrator advanced task settings, sample-fill, clear,
  save, and close remain available.
- Run Center filters, pagination, log drawer, stop, archive, and restore remain
  available.
- Report Center grouping, preview, lead detail, delivery history, resend, and
  HTML/Excel/Markdown downloads remain available.
- AI connection test, AI rule test, mail test, mail-template iframe preview,
  runtime strategy grouped tables, and system diagnosis actions remain
  available.
- Administrator-only pages remain hidden from normal users by existing
  permission logic.

Scope boundary:

- Planning document and later frontend-only changes in:
  `api/monitor_web/index.html`, `api/webui/monitor/monitor.css`, and
  `api/webui/monitor/monitor.js`.
- No backend API, database schema, permission model, crawler behavior,
  AI-provider behavior, SMTP behavior, scheduler behavior, or deployment
  behavior changes.
- No new frontend framework, build step, or required external UI library.

Non-goals:

- Do not reopen or mark CR-033 incomplete.
- Do not replace the formal frontend with the static prototype.
- Do not merge Resource Management or System Configuration pages.
- Do not simplify Platform Accounts into a generic configuration modal.
- Do not delete QR login, Cookie login, login history, external account
  identity details, filters, batch management, floating menus, report
  downloads, or runtime grouped tables.
- Do not add new metrics, charts, or progress fields that require new backend
  data.
- Do not implement the currently unrendered `Users And Permissions` page in
  this CR; if the user wants that missing page implemented later, record it as
  a separate new-capability CR.

Status: Accepted

Related tasks:

- Phase 21 in `TASKS.md`

Acceptance:

- The execution plan identifies the implementation files, preserved behaviors,
  allowed refinements, forbidden changes, test method, and acceptance standard
  for every existing formal console page and major secondary surface.
- The plan explicitly states that the static prototype is visual reference
  only and cannot be used to remove formal-console functions.
- The plan includes desktop `1440x900`, tablet `1024x768`, and mobile
  `390x844` verification requirements.
- Phase 21 verification treats one-character vertical text wrapping, content
  overlap, hidden primary actions, and horizontal overflow as hard failures for
  dashboard, run/report, resource, and secondary overlay layouts.
- `TASKS.md`, `TEST_PLAN.md`, and `TRACEABILITY.md` link this CR to the
  planning document and future verification areas.
- No production frontend code is changed as part of this planning-only update.

## CR-041 - Minimum Usable Pilot Acceptance Gate

Date: 2026-06-16

Source: user request to tighten acceptance around the standard "the system can
be used first" before continuing broader optimization work.

Module: pilot readiness, test safety, run lifecycle, deployment acceptance

Type: Documentation Governance

Background:

After CR-035, CR-036, CR-039, CR-040, and the Phase 19/21 roadmap were
documented, the user clarified that near-term priority should be judged by
whether the system can safely enter a small usable pilot, not by whether every
console optimization, realtime progress enhancement, or AI traceability feature
is finished.

The previous documents already listed the correct tasks, but the acceptance
boundary for "usable first" needed to be tighter and more explicit. In
particular, the gate must prevent accidental real email, prevent stuck runs
from hiding usable results, and prove one minimal server-like real workflow,
while keeping non-essential enhancements out of the pilot blocker set.

Purpose:

Define the minimum hard acceptance gate before declaring the system ready for a
small internal/customer pilot. The gate narrows the implementation focus to the
few safety and lifecycle guarantees needed to operate the system first.

Requirement:

- The system must not be considered minimally usable while tests, diagnostics,
  or ordinary local runs can accidentally send real SMTP email.
- The system must not be considered minimally usable while a normal run can
  remain indefinitely `running` after the background task disappears or AI
  evaluation partially stops.
- The minimum pilot gate must require a server-like validation path that does
  not depend on the operator's local Chrome.
- The minimum pilot gate must require at least one real platform login/crawl
  path, AI failure fallback or unavailable-AI fallback, and explicit-opt-in
  SMTP delivery validation before pilot handoff.
- The gate must preserve evidence and avoid historical mutation by default;
  historical run or orphan-email remediation remains dry-run, backup,
  rollback, and explicit-operator-approval gated.
- Phase 21 UI refinement, CR-038 drawer accessibility, Phase 19 realtime
  progress display, Phase 20 AI traceability, and CR-037 role/quota governance
  must not block the first usable pilot unless they expose a new accepted P0
  safety, security, or core-flow regression.

Scope boundary:

- This CR tightens acceptance and implementation priority; it does not replace
  CR-036, CR-035, CR-039, CR-040, or CR-031.
- It does not add a new business capability, backend API, database schema, UI
  page, crawler feature, AI-provider feature, or SMTP feature by itself.
- It uses existing Phase 17.1A-B, Phase 7.1A-C, and deployment validation as
  the hard pilot readiness path.

Non-goals:

- Do not require Phase 21 visual refinement for the first usable pilot.
- Do not require Phase 19 realtime progress display if the run lifecycle is
  safe and logs/refresh provide enough operational visibility for the pilot.
- Do not require Phase 20 AI prompt/request/response traceability before the
  first pilot.
- Do not implement CR-037 role-based email quotas as part of the minimum pilot
  gate.
- Do not mark historical run `8317` or orphan delivery evidence repaired
  without the existing explicit remediation gate.

Status: Verified

Related tasks:

- Minimum Usable Pilot Acceptance Gate in `TASKS.md`
- CR-036/Phase 17.1A-B in `TASKS.md`
- CR-035/Phase 7.1A-C in `TASKS.md`
- Server-like and pilot validation in `TEST_PLAN.md`

Acceptance:

- CR-036/Phase 17.1A-B is implemented and verified: automated tests, local
  diagnostics, and ordinary local report-delivery paths cannot reach real SMTP
  without explicit opt-in, even when real SMTP configuration and default
  recipients exist.
- A test-level SMTP tripwire fails the automated suite if `smtplib.SMTP` or
  `smtplib.SMTP_SSL` is reached without explicit opt-in.
- Automatic report delivery, manual resend, and mail-test paths use the same
  real-email safety gate; blocked delivery still lets report generation
  complete and records a customer-safe skipped state or confirmed equivalent.
- CR-035/Phase 7.1A-C is implemented and verified: new runs persist
  `crawl_runs.job_id`; all success, failure, timeout, cancellation,
  interruption, and partial-result paths finalize idempotently; AI item
  timeout, exception, or invalid JSON falls back to `pending_review`; collected
  partial results can produce a report when safe.
- The regression scenario "271 collected contents, AI interruption after item
  250/251" cannot leave the run indefinitely `running`.
- A minimum server-like pilot validation proves web-UI login through
  server-side browser/profile, one real platform crawl, AI unavailable/failure
  fallback, explicit-opt-in SMTP submission, recipient-side receipt
  confirmation, and sensitive-value redaction. SMTP `sent` records prove server
  acceptance only; they do not prove recipient inbox delivery by themselves.
- Phase 21, CR-038, Phase 19B-D, Phase 20, and CR-037 remain outside the first
  usable pilot blocker set unless a new accepted P0 regression changes the
  boundary.

Verification:

- Verified on 2026-06-17 with the CR-041 Pilot Gate C evidence chain:
  CR-036/Phase 17.1A-B safety gate and SMTP tripwire, CR-036/Phase
  17.1C/CR-039 Phase 17.2A delivery metadata, CR-035/Phase 7.1A-C lifecycle
  and AI fallback safeguards, automated server-like validation, real Douyin
  server-side crawl/report evidence for `run_id=3` / `report_id=3`, controlled
  frontend-enabled real SMTP submission recorded as `delivery_log_id=6`, operator
  confirmation that both approved recipients received the report email, and a
  passing redacted `pilot_gate_c_v2` evidence JSON check.

## CR-042 - Frontend-Controlled Real Email Validation Window

Date: 2026-06-17

Source: user asked whether the real-email switch should be operable from the
frontend after a manual resend showed frontend success while the recipient did
not actually receive the email.

Module: email delivery safety, runtime settings, administrator operations

Type: Existing Feature Optimization

Background:

CR-036 intentionally made real SMTP delivery a deployment-controlled safety
gate so tests, diagnostics, and ordinary local runs cannot accidentally send
external email. During Pilot Gate C validation, the operator needs a practical
way to temporarily enable real SMTP delivery from the console. The current
environment-only switch is safe but operationally awkward, while a simple
always-editable frontend boolean would reintroduce accidental real-email risk.

Purpose:

Allow administrator-controlled real-email validation from the frontend without
weakening the hidden-real-email safety guarantees that CR-036 added.

Requirement:

- Provide an administrator-only frontend action for a temporary real-email
  validation window, not a permanent ordinary settings toggle.
- Keep a deployment-level allow switch as the first gate. Recommended shape:
  frontend validation windows can only be opened when deployment configuration
  explicitly allows frontend-controlled real-email validation.
- Require strong confirmation text before enabling the window, including the
  effective recipients, trigger scope, and warning that SMTP acceptance does
  not prove recipient inbox delivery.
- Limit the validation window by time and/or single-use delivery count, and
  auto-disable it after expiry or after the approved validation send.
- Require automatic scheduler delivery to remain disabled or otherwise
  explicitly excluded while the validation window is open.
- Record audit logs with actor, trigger source, enabled time, expiry, effective
  recipients summary, delivery-log IDs, and disable reason.
- Show runtime state clearly in the frontend: default non-sending, validation
  window open, expired, disabled after validation, or deployment gate closed.
- Preserve the existing test tripwire and default non-sending behavior for
  automated tests, local diagnostics, and ordinary report delivery.
- Pilot Gate C must remain incomplete until both SMTP submission and
  recipient-side receipt confirmation are recorded in redacted evidence. This
  was satisfied for CR-041 on 2026-06-17 with `delivery_log_id=6` and a
  passing redacted evidence check.

Scope boundary:

- This CR may add frontend controls, API endpoints, runtime settings, audit
  records, and tests for temporary validation-window behavior after the user
  confirms the design.
- It must not expose SMTP passwords, API keys, raw recipients beyond
  customer-safe summaries, cookies, proxy credentials, profile paths, local
  paths, or raw command lines.

Non-goals:

- Do not create a permanent always-on frontend real-email toggle.
- Do not allow normal users to enable real SMTP delivery.
- Do not allow scheduler-driven bulk email to run merely because a manual
  validation window is opened.
- Do not treat SMTP `sent` as proof of recipient inbox delivery.

Status: Rejected

Superseded by:

- CR-043 - Administrator Frontend Real Email Send Toggle

Supersession note:

On 2026-06-17, after using the validation-window flow, the user explicitly
rejected the multi-layer design as too complex and confirmed that the product
should use one administrator-controlled frontend switch only. Future
implementation must not reintroduce deployment gates, scheduler-exclusion
gates, expiry windows, or single-use validation-window behavior for daily
operation.

Historical recommended option:

Implement a deployment-gated, administrator-only, time-limited validation
window with audit logging and automatic disable after validation.

Historical confirmation:

On 2026-06-17 the user initially confirmed that the real-email switch should
be operable from the frontend. A validation window was implemented, then later
rejected by the user as too complex and superseded by CR-043.

Alternative:

Keep real email fully environment-only and operate it through service restart
runbooks. This is safer but harder to use during repeated pilot validation.

Related tasks:

- Frontend-Controlled Real Email Validation Window in `TASKS.md`
- Pilot Gate C in `TASKS.md`
- CR-036/Phase 17.1A-B in `TASKS.md`

Acceptance:

- The frontend cannot enable real email unless the deployment-level frontend
  validation gate is already allowed.
- A validation window requires administrator confirmation and shows effective
  recipient source/count before any real external send can happen.
- The window auto-disables after expiry or approved validation send, and the
  frontend shows the final disabled state.
- Automatic scheduled delivery cannot silently send during the validation
  window unless explicitly confirmed by a later accepted requirement.
- Audit and delivery logs show actor, trigger source, environment/gate state,
  effective recipient summary, result, and disable reason without secrets.
- Automated tests prove default paths remain non-sending and the SMTP tripwire
  still blocks accidental real SMTP.

Historical implementation:

- Added deployment-locked runtime visibility for
  `frontend_real_email_validation` /
  `MONITOR_ALLOW_FRONTEND_REAL_EMAIL_VALIDATION`.
- Added administrator-only API endpoints to read, open, and close a
  time-limited single-use real-email validation window.
- Opening the window requires both real-email deployment gates and scheduler
  exclusion (`scheduler_disabled=true`) so automatic scheduled delivery cannot
  silently send during the manual validation window.
- Mail-test and administrator manual-resend API paths require the validation
  window before real SMTP is allowed. Normal-user resend remains non-sending
  through the default safety gate.
- Successful validation use marks the window used and closes it automatically.
  Audit logs record open, use, close, gate state, recipient source/count, and
  delivery-log reference without secrets.

## CR-043 - Administrator Frontend Real Email Send Toggle

Date: 2026-06-17

Source: user explicitly said "一个开关即可" and rejected the multi-layer
real-email validation-window UI as too complex.

Module: email delivery safety, mail configuration frontend, runtime settings

Type: Existing Feature Optimization

Background:

CR-036 fixed hidden real-email side effects after unexpected report emails were
observed. CR-042 then tried to keep real SMTP validation safe through a
deployment-gated, scheduler-excluded, single-use validation window. The user
found this too hard to operate. The product need is simpler: an administrator
should be able to decide in the frontend whether the system is allowed to send
real report emails.

Purpose:

Replace the validation-window workflow with one persisted administrator switch
on the Mail Configuration page.

Requirement:

- Show exactly one user-facing control for real email delivery: an
  administrator-only "real email send" switch on Mail Configuration.
- Persist the switch as the `real_email_delivery` runtime setting, with default
  `false`.
- When the switch is off, mail test, manual resend, and automatic report
  delivery must not submit real SMTP; report generation must still continue and
  blocked delivery should be recorded with customer-safe wording.
- When the switch is on and SMTP configuration is complete, mail test,
  administrator/manual resend, and automatic report delivery may submit real
  SMTP.
- Normal users must not be able to edit the switch.
- The UI may show a confirmation before turning the switch on, effective
  recipient source/count, and the warning that SMTP acceptance is not recipient
  inbox proof.
- Do not require a deployment-level frontend gate, scheduler exclusion,
  expiry, or single-use validation window for daily operation.
- Automated tests must still be protected from accidental real SMTP by the
  test-level tripwire and mocked SMTP paths.
- Do not commit SMTP passwords, real recipients, local databases, browser
  profiles, cookies, or runtime-only configuration.

Scope boundary:

- In scope: mail configuration frontend, runtime setting persistence, mailer
  gate, API response compatibility, tests, and documentation.
- Compatibility endpoints may remain for older frontend/API callers if they
  simply map to the same `real_email_delivery` switch.
- Out of scope: role/quota governance for normal-user sending, scheduler bulk
  policy redesign, additional provider-specific SMTP troubleshooting, and
  historical evidence mutation.

Non-goals:

- Do not add a second real-email setting in Runtime Strategy.
- Do not expose SMTP secrets or raw recipient lists beyond customer-safe
  summaries.
- Do not treat SMTP `sent` as proof of recipient inbox delivery.

Status: Verified

Related tasks:

- Administrator Frontend Real Email Send Toggle in `TASKS.md`
- CR-036/Phase 17.1A-B in `TASKS.md`
- Phase 17 email delivery governance in `TASKS.md`

Acceptance:

- Mail Configuration shows one real-email send switch and no open/close
  validation-window buttons.
- `real_email_delivery` is admin-editable, persisted, default-off, and not
  environment-locked in normal product operation.
- Runtime Strategy does not expose a second Email settings group for the same
  switch.
- Mail test and manual resend are blocked while the switch is off and can use
  mocked SMTP while the switch is on in tests.
- The administrator API can update the switch; normal users cannot.
- Scheduler exclusion, deployment frontend gate, expiry, and single-use
  behavior are not required for the switch to work.
- Tests and docs confirm that no real external email is sent during automated
  verification.

## CR-044 - Mail Test Recipient Coverage And SMTP Acceptance Clarity

Date: 2026-06-17

Source: user reported that the Mail Configuration test mail showed
"submitted to SMTP and recorded as passed" but no recipient-side message was
found.

Module: mail configuration, SMTP validation, administrator operations

Type: Regression Fix

Background:

The administrator Mail Configuration page can contain multiple global default
recipients, and report delivery uses the full effective recipient list. The
test-mail path, however, only selected the first default recipient when no
explicit test target was supplied. The frontend also displayed a generic
success message that did not show how many recipients were submitted. This made
operator validation confusing when the configured default recipient list had
more than one address.

Purpose:

Make the Mail Configuration test action match administrator expectations:
when no explicit target is supplied, submit the test message to all configured
default recipients and show the submitted recipient count while still stating
that SMTP acceptance is not inbox proof.

Requirement:

- The test-mail path must continue to require the administrator
  `real_email_delivery` switch before submitting real SMTP.
- With no explicit test target, test mail must submit one message addressed to
  all configured global default recipients.
- With an explicit test target, test mail may still use only the explicit
  target or targets.
- The API response must include the test recipient count and source without
  exposing raw SMTP passwords.
- The frontend success message must show how many test recipients were
  submitted and must keep the warning that SMTP acceptance does not prove
  recipient inbox delivery.
- Automated tests must mock SMTP and continue to protect against accidental
  real external mail.

Scope boundary:

- In scope: test-mail recipient resolution, API response metadata, frontend
  success text, tests, and documentation.
- Out of scope: provider-specific QQ Mail deliverability diagnosis, bounce
  mailbox monitoring, recipient-side read receipts, normal-user quotas, and
  changing report-delivery recipient precedence.

Non-goals:

- Do not treat SMTP `sent` or test-mail success as recipient inbox proof.
- Do not expose raw recipient lists in public/customer-safe surfaces beyond
  existing administrator configuration views.
- Do not send real SMTP during automated verification.

Status: Verified

Related tasks:

- CR-044 Mail Test Recipient Coverage And SMTP Acceptance Clarity in
  `TASKS.md`
- CR-043 Administrator Frontend Real Email Send Toggle in `TASKS.md`
- CR-036/Phase 17.1A-B in `TASKS.md`

Acceptance:

- A configured two-recipient default list results in a test email addressed to
  both recipients when the administrator switch is on.
- The test-mail API returns `test_result.recipient_count` and
  `test_result.recipient_source`.
- The Mail Configuration test console reports the submitted recipient count
  and warns that SMTP acceptance still requires manual inbox/spam confirmation.
- When the administrator switch is off, test mail remains blocked and no SMTP
  client is instantiated.
- Targeted mocked-SMTP tests cover the multi-recipient path without sending
  external email.

Verification:

- Verified on 2026-06-17 with targeted mocked-SMTP tests for blocked-off
  behavior, mocked real-email send behavior, SMTP refused-recipient handling,
  and the CR-044 two-default-recipient test-mail path. No real external SMTP
  was used during automated verification.

## CR-045 - AI Evaluation Accuracy And Unevaluated Lead Status Clarity

Date: 2026-06-17

Source: user observed in the Report Center that some rows had empty AI
reason/evidence and that the current AI evaluation felt inaccurate during a
real Douyin pilot run.

Module: AI evaluation, run finalization, report leads, Run Center, Report
Center

Type: Regression Fix

Background:

During live pilot inspection, run `4` had 102 newly ingested contents. The
system had AI evaluation rows for 91 contents and no AI evaluation rows for 11
remaining contents after the run reached the 900-second wall-clock timeout.
The current lead-status rendering could treat rows with no evaluation record as
"no risk", and broad search terms such as "北京海安律所退费" recalled many
unrelated platform posts about education refunds, medical refunds, clothing
refund fraud, generic lawyer refund advice, and other law firms.

This exposed two related defects in the completed Phase 7 responsibility area:
unevaluated content can be confused with no-risk content, and the AI relevance
rules allow `source_keyword` to influence relatedness too strongly even when
the actual title, description, author, and comments do not identify the target
law firm or aliases.

Purpose:

Make AI evaluation results safer to operate in a pilot: unreviewed content must
not be presented as safe, target-law-firm relevance must be stricter, and
operators must be able to distinguish unrelated content, evaluated no-risk
content, pending-review fallback, and truly unevaluated content.

Requirement:

- Do not display missing AI evaluation records as "no risk". Missing,
  interrupted, or timeout-leftover evaluations must be surfaced as
  "unevaluated" or converted to `pending_review` during safe finalization.
- Ensure timeout and partial-failure finalization attempts to create
  `pending_review` fallback rows for known unresolved AI candidates before
  report generation when the candidate IDs are known and mutation is safe.
- Keep `source_keyword` as recall provenance only. It may explain why the item
  was collected, but it must not by itself prove that the content is related to
  the target law firm.
- Add or enforce a target-evidence gate: title, description, author, or sampled
  comments should contain the target law firm name, accepted aliases, or a
  clearly equivalent reference before AI can mark the item as related or
  negative. Homonyms and geography such as "海安" as a place name must not be
  treated as the target law firm by default.
- Use comments as evaluation evidence only when comments were actually
  collected and passed into the evaluation payload.
- Preserve the existing guarantee that AI provider failures do not block
  collection, report generation, or email delivery.
- Distinguish at least these lead states in API/frontend behavior: unrelated,
  evaluated no-risk, suspected negative, high-risk, pending manual review, and
  unevaluated/limited-context history.
- If new structured AI output fields such as target-match level, negative
  signal level, confidence, or review reason are added, document the schema and
  role-safe display boundary before implementation.
- Add a small real-sample calibration set from pilot data or fixtures so broad
  refund/legal keywords and target-law-firm mentions can be regression-tested.

Scope boundary:

- In scope: AI prompt/rule hardening, deterministic pre-AI relevance gating if
  needed, timeout/failure fallback finalization for unresolved candidates,
  lead-status API/frontend wording, report counts, and regression tests.
- In scope: linking this work to Phase 20 traceability where detailed per-item
  input/output viewing is needed for diagnosis.
- Out of scope: changing crawler platform implementations, bypassing platform
  anti-abuse checks, adding high-concurrency AI workers, storing unredacted raw
  AI responses, or completing all Phase 20 trace snapshot/debug surfaces.

Non-goals:

- Do not claim AI output is a factual determination.
- Do not rely on `source_keyword` alone as legal or reputational evidence.
- Do not expose API keys, raw provider headers, cookies, profile paths, local
  paths, proxy credentials, or unredacted model responses while improving
  evaluation transparency.
- Do not rewrite historical completed Phase 7 or Phase 7.1 status; record this
  as a follow-up fix.

Status: Verified

Related tasks:

- Phase 7.2 - AI Evaluation Accuracy And Lead Status Clarity Follow-up in
  `TASKS.md`
- Phase 20 - Run Detail And AI Evaluation Traceability in `TASKS.md`
- PR-RUNREPORT-001 in `TRACEABILITY.md`

Acceptance:

- A content row with no AI evaluation record is never shown as "no risk" in
  Report Center or Run Detail; it is shown as unevaluated/limited-context or
  becomes `pending_review` through safe finalization.
- A timeout run with known candidate IDs creates pending-review fallback rows
  for unresolved candidates before report generation, or records an explicit
  limited-context state if safe mutation is not possible.
- Reports and lead filters count `pending_review`, unrelated, and no-risk
  rows separately.
- AI prompt/rule behavior states that `source_keyword` is recall provenance,
  not relatedness proof.
- Fixture coverage proves generic refund/legal posts without target-law-firm
  evidence are not marked as target-related negative leads even if they were
  collected by a broad target-bearing search keyword.
- Fixture coverage proves title/description/comment evidence that clearly
  names the target law firm or alias can still be marked related and negative
  when the negative signal is present.
- Normal-user output remains business-safe; administrator-only debug detail
  remains governed by Phase 20.

## CR-046 - Platform Account Avatar Safe Cache Display Regression Fix

Date: 2026-06-17

Source: user observed that the Platform Accounts page no longer showed the
recognized account avatar after the Douyin account identity had been detected.

Module: Platform Accounts, account identity display, customer-safe URL
redaction

Type: Regression Fix

Background:

The account identity check can capture `platform_account_name` and
`platform_avatar_url`. The customer-facing account-list API redacts URL query
parameters before sending URLs to the frontend so signed platform URLs and
tracking-like parameters are not exposed. Douyin avatar images can depend on
those signed query parameters, so the sanitized external avatar URL can fail to
load even though the account identity and raw avatar URL are present in the
server-side database.

Purpose:

Restore platform-account avatar display without exposing signed platform image
URLs, cookies, profile paths, proxy credentials, or other runtime data to the
frontend.

Requirement:

- Do not expose the original signed platform avatar URL to the frontend.
- The social-account list API should return a same-origin avatar URL when an
  account has a platform avatar source, not the external platform URL.
- The same-origin avatar endpoint must be administrator-only, must reject path
  traversal, and must serve only cached account-avatar files.
- The server may lazily fetch and cache the remote platform avatar when the
  administrator opens the same-origin avatar URL.
- If the remote avatar cannot be fetched or validated as an image, the frontend
  should fall back to the existing placeholder avatar.
- Avatar cache files are runtime data and must stay out of Git.

Scope boundary:

- In scope: platform-account identity API output, safe avatar cache helper,
  administrator-only avatar read endpoint, and regression tests.
- Out of scope: changing login-state detection semantics, crawler behavior,
  normal-user access to platform accounts, exposing raw signed URLs, or adding
  long-term media-retention management.

Non-goals:

- Do not proxy arbitrary user-provided URLs beyond stored account-avatar
  sources.
- Do not make account avatars available to normal users.
- Do not treat missing avatars as account-login failure.

Status: Verified

Related tasks:

- CR-046 Platform Account Avatar Safe Cache Display Regression Fix in
  `TASKS.md`
- PR-RESOURCE-001 in `TRACEABILITY.md`

Acceptance:

- A stored signed Douyin avatar source results in a same-origin
  `/api/monitor/social-accounts/{account_id}/avatar` URL in the administrator
  account-list response.
- The account-list response does not include the external platform avatar host
  or signed query parameters.
- The avatar endpoint fetches and caches the remote image server-side, returns
  image bytes for administrators, rejects normal users, and rejects traversal
  paths.
- If avatar fetching fails, the frontend keeps the placeholder and the account
  row remains usable.

Verification:

- Verified on 2026-06-17 with targeted avatar-cache tests covering signed URL
  redaction, same-origin avatar URL output, administrator-only avatar serving,
  path traversal rejection, and profile/cookie path hiding.

## CR-047 - Account Browser Environment Consistency

Date: 2026-06-17

Source: user request after reviewing CloakHQ/CloakBrowser-Manager as a
reference for stable browser-profile environments. This requirement was
initially drafted locally as CR-042, but CR-042 is already the historical
rejected real-email validation-window design, so this accepted requirement is
recorded as CR-047.

Module: account environment, platform account login, server-side browser
runtime

Type: Existing Feature Optimization

Background:

Phase 5 and Phase 6 already established the core account-environment model:
one platform account maps to one `profile_key`, the server persists account
profiles, login and crawling use server-side browser sessions, and
account/profile/proxy locks prevent concurrent reuse. The remaining
consistency gap is that `profile_key` identifies the persisted profile
directory, but it does not explicitly persist the browser identity inputs that
make a login environment stable.

CloakBrowser-Manager is useful as a technical reference because it treats
browser profile properties such as platform, fingerprint seed, user agent,
timezone, locale, screen size, proxy, CDP access, and noVNC viewing as
profile-level settings. The project should learn from that profile-environment
model, but should not copy CloakBrowser-Manager's standalone account center,
database, authentication model, frontend, or deployment shape into this
system.

Purpose:

Make the account environment rule explicit and enforceable:

```text
one platform account = one profile_key = one fixed browser environment
```

For the same platform account, server-side QR login, login-state checks, and
later crawling should all use the same persisted profile, same user agent, same
browser platform fingerprint family, same timezone/locale, same screen size,
and same proxy policy.

Requirement:

- Add a persisted account browser-environment configuration on top of the
  current `profile_key` model. The minimum fields are:
  `browser_platform`, `fingerprint_seed`, `user_agent`, `timezone`, `locale`,
  `screen_width`, `screen_height`, lock status/timestamp/reason, and the
  account-bound `proxy_id` policy.
- Generate or assign the account browser environment before the first
  server-side QR login attempt or accepted Cookie login validation, and lock it
  after successful login validation.
- Login, login-state checks, and crawling must read the same persisted account
  browser environment instead of deriving browser identity from changing
  process defaults.
- Existing Platform Accounts UI should show a customer-safe summary such as
  browser platform, timezone/locale, screen size, and proxy binding state, but
  must not expose raw profile paths, cookies, proxy credentials, local command
  lines, CDP endpoints, noVNC sessions, or fingerprint-debug output.
- Administrator changes to a locked browser environment require an explicit
  reset/re-login flow with audit logging. Silent edits after successful login
  are not allowed.
- Reconcile the existing proxy-priority rule with account-environment
  consistency before code implementation. The preferred direction is that an
  account-bound proxy is the stable default for that account; any task-level
  proxy override must be treated as an explicit, visible exception or blocked
  for fixed-environment accounts according to the final accepted design.
- Introduce an internal browser-environment provider boundary so the existing
  Playwright/CDP path can consume the persisted settings first. CloakBrowser or
  CloakBrowser-Manager-style CDP/noVNC management may be evaluated later as an
  optional provider, not as a required dependency.
- If an optional CloakBrowser-based provider is evaluated, review deployment
  fit, license boundaries, authentication exposure, noVNC access control,
  persistent storage, server resource use, and whether observable browser
  signals match the stored account environment.

Preserved behavior:

- Keep `profile_key = {workspace_id}/{platform}/acc_{account_id}` as the
  account profile identity.
- Keep one profile per platform account and one account/profile concurrency
  lock.
- Keep server-side QR/status login as the production path.
- Keep Cookie login as a supported account login type.
- Keep verification/captcha/SMS states returned to the UI rather than bypassed.
- Keep normal users away from account/profile/proxy/browser implementation
  details.

Scope boundary:

- This CR optimizes the existing account-environment feature. It does not
  create a separate browser-account product or replace the current account
  center.
- Planned implementation areas are `social_accounts` data model/migration,
  account environment helpers, login QR/session launch options, crawler/CDP
  runtime binding, Platform Accounts UI summaries, audit logs, and tests.
- CloakBrowser-Manager may be used as a reference design for stable profile
  settings, CDP, and noVNC, but its standalone manager service should not be
  adopted wholesale without a separate provider evaluation and decision.

Non-goals:

- Do not promise that every platform login HTTP request is byte-for-byte
  identical. Dynamic tokens, timestamps, cookies, platform challenges, and
  network behavior can still change.
- Do not bypass captcha, slider, SMS, or manual platform verification.
- Do not add complex account rotation, dynamic proxy scheduling, or
  high-concurrency browser orchestration.
- Do not expose raw profile paths, cookies, proxy credentials, fingerprint
  internals, CDP endpoints, or noVNC sessions to normal users.
- Do not make CloakBrowser or CloakBrowser-Manager a hard dependency for the
  first implementation batch.

Status: Accepted

Related tasks:

- Phase 5.1 Account Browser Environment Consistency in `TASKS.md`
- CR-047 Account Browser Environment Consistency in `TRACEABILITY.md`

Acceptance:

- New platform accounts receive a deterministic `profile_key` and a persisted
  browser-environment configuration before first QR login or Cookie
  validation.
- Successful QR login or accepted Cookie validation locks the
  browser-environment configuration.
- Repeated login-state checks and crawl runs for the same account use the same
  stored `profile_key`, `browser_platform`, `fingerprint_seed`, `user_agent`,
  `timezone`, `locale`, `screen_width`, `screen_height`, and effective proxy
  policy.
- Same-platform accounts have separate profile keys and separate browser
  environment values unless an administrator explicitly clones a safe template
  before first login.
- Attempts to edit a locked browser environment are blocked unless the operator
  uses an explicit reset/re-login path that records an audit log.
- Tests verify that service restart or process default changes do not change
  the observable account browser environment for subsequent login/crawl
  sessions.
- If an optional CloakBrowser-style provider is enabled, CDP/noVNC access is
  administrator-scoped, authenticated, and does not bypass the existing
  account/profile/proxy locks or sensitive-data redaction rules.

## CR-048 - Report Center Lead Detail Information Architecture

Date: 2026-06-17

Source: user observation during Report Center review: the lead detail area is
flattened directly on the page, and it is unclear whether it shows all leads,
leads under current filters, or leads for a selected report. The user also
questioned whether Report Center is carrying both report aggregation and lead
aggregation responsibilities.

Module: Report Center, report leads, Run Detail navigation, UI information
architecture

Type: Existing Feature Optimization

Background:

Phase 18B grouped Report Center history by monitoring task while preserving
preview, lead detail switching, downloads, delivery history, and row actions.
CR-034 / Phase 20 already accepted that Report Center should expose an
explicit "view leads" path and link report leads back to Run Detail where
possible.

The remaining product ambiguity is the default lead-detail presentation. A
flat lead detail area inside Report Center can look like a global lead list or
lead workbench even when the intended relationship is "leads for the selected
report" or "leads under the current report filters." This makes operators ask
whether they are seeing every accessible lead, a filtered aggregate, or one
report's leads.

Purpose:

Clarify Report Center as a report-first surface. Lead detail may exist there,
but it must be an explicit, scoped secondary view tied to a selected report,
selected report group, or visibly labeled filter state. The full per-run and
per-AI-evaluation inspection surface remains Phase 20 Run Detail.

Placement rule:

- Run Center / Run Detail is the primary operational home for run-generated
  leads and AI evaluation inspection because leads are produced by a specific
  crawl/evaluation run and can exist before a report is generated.
- Report Center provides report-scoped "view leads" shortcuts after report
  generation. These shortcuts answer "what leads are included in this report,"
  not "what happened during the whole run."
- A standalone top-level Lead Center or global lead workbench is out of scope
  for CR-048 and requires a separate confirmed capability CR if needed later.

Requirements:

- Report Center lead details must always show their scope: selected report,
  selected report group, originating run, or current report filters.
- The page must not silently display all accessible leads, or all filtered
  leads, as an unlabeled flat "line detail" table.
- Add an explicit "view leads" action for report rows or report groups,
  separate from report preview. Preview may still update lead context, but it
  must not be the only discoverable path.
- Lead detail scope should include a count and applied filter summary such as
  drawer-local lead status, platform, date range, law firm, report ID, group,
  or run ID when available.
- Empty states must distinguish "no report selected," "this selected report
  has no leads," and "current filters have no matching leads."
- If a current-filter aggregate lead list is kept, it must be visually and
  textually labeled as a filtered aggregate, not as selected-report detail.
- Report Center remains responsible for final reports, report-scoped leads,
  previews, downloads, resend actions, and email delivery history.
- Run Center should expose or preserve a run-detail entry for run-scoped leads
  and AI evaluation records, including items that exist before report
  generation or after partial/failed runs.
- Run lifecycle, collection logs, every AI evaluation record, trace snapshots,
  and debug fields belong to CR-034 / Phase 20 Run Detail, not to the Report
  Center lead table.

Preserved behavior:

- Preserve report grouping by monitoring task and deleted-task snapshots.
- Preserve report filters, report preview, HTML/Excel/Markdown downloads,
  delivery history, resend, and customer-safe report wording.
- Preserve owner/workspace scope for report and lead reads.
- Preserve the existing no-build frontend architecture.

Scope boundary:

- This CR optimizes the existing Report Center information architecture. It
  does not create a standalone global lead workbench.
- A future global lead workbench would require a separate confirmed capability
  CR with its own filters, ownership rules, actions, and tests.
- This CR does not implement AI trace persistence, raw prompt/request/response
  views, or per-evaluation debug detail; those remain Phase 20 work.

Non-goals:

- Do not remove report preview, downloads, delivery history, or resend.
- Do not make Report Center the primary place for observing running AI
  evaluation progress.
- Do not change AI relatedness or risk-classification semantics.
- Do not expose administrator-only AI debug fields or raw model responses in
  Report Center.

Status: Verified

Related tasks:

- Phase 20E Report Center Lead Detail Clarity in `TASKS.md`
- Phase 21M Report Center in `TASKS.md`
- CR-048 Report Center Lead Detail Information Architecture in
  `TRACEABILITY.md`

Acceptance:

- Operators can tell whether the visible lead list belongs to a selected
  report, selected report group, originating run, or current filters.
- Opening "view leads" on a report or group visibly changes the lead-detail
  scope and count.
- Report preview is not the only way to inspect report leads.
- The default Report Center page no longer looks like an unlabeled global lead
  workbench.
- Run Center remains the primary entry for run-scoped lead/evaluation
  inspection, while Report Center exposes report-scoped shortcuts.
- Empty states explain whether no report is selected, the selected report has
  no leads, or the current filters have no matches.
- Report Center keeps a report-first hierarchy while Phase 20 Run Detail
  remains the place for per-run lifecycle and per-AI-evaluation evidence.

Verification:

- Verified on 2026-06-17 in the focused CR-048/CR-049 frontend batch. Report
  Center no longer renders a first-level `leads_table`, no longer shows the
  process-draft preview hint, and exposes report row "查看线索" as a scoped
  drawer with scope label, count, and selected-report filter summary.
- Run Center rows expose a "查看线索" entry that opens the same drawer with a
  run-scoped title, count, and "not a global lead workbench" hint.
- Follow-up acceptance tuning moved `线索状态` out of the first-level Report
  Center toolbar and into the lead drawer. The first-level Report Center toolbar
  now stays on report dimensions (`律所`, `平台`, date range, `报告范围`), while
  drawer-local `线索状态` filters only the selected report or selected run lead
  scope.

## CR-049 - Mail Configuration And Delivery History Action Hierarchy

Date: 2026-06-17

Source: user review of the Mail Configuration page and Report Center delivery
history. The Mail Configuration page already has top-level "edit mail
configuration" and "send test mail" actions, but the "SMTP and sending
defaults" block repeats "edit configuration" and "test mail." The real email
send switch is visually heavy and takes a full row even though it is a compact
safety state/action. The user also raised the same hierarchy concern for
Report Center email delivery history.

Module: Mail Configuration, Report Center email delivery history, formal
console UI action hierarchy

Type: Existing Feature Optimization

Background:

CR-043 intentionally introduced one administrator-controlled real-email send
switch on Mail Configuration, backed by the default-off `real_email_delivery`
runtime setting. CR-044 clarified test-mail recipient coverage and SMTP
acceptance wording. Phase 17B added Report Center delivery history and manual
resend visibility. These safety and audit functions are correct, but the
current page hierarchy can make the mail configuration surface feel heavier
than needed and can duplicate the same actions in multiple places.

Purpose:

Keep mail and delivery controls operationally clear without letting secondary
safety/status panels dominate the page. Primary mail actions should live in the
page-level action bar; content sections should show status, configuration
summaries, and lightweight explanations instead of repeating the same controls.

Requirements:

- Mail Configuration should have one primary action group in the page header:
  edit configuration, send test mail, refresh/read status, view delivery
  status, and a compact real-email send state/action where permitted.
- The "SMTP and sending defaults" section should not repeat "edit
  configuration" or "test mail" if those actions already exist in the page
  header. It should focus on sender, recipient source/count, title/template
  summary, latest test state, and safe status text.
- The real-email send control remains the single CR-043 administrator switch,
  but its visual treatment should be compact: a labeled toolbar toggle/button
  plus concise state text or tooltip. It should not occupy a large full-width
  card unless the state is exceptional and needs attention.
- Turning real email on still requires explicit confirmation and must preserve
  the warning that SMTP acceptance is not inbox proof.
- When real email is off, the UI should still make the state visible, but as a
  compact safe default rather than a dominant warning block.
- Report Center delivery history should be reachable from a report row/status
  action and displayed as scoped secondary detail. It should not visually
  compete with the grouped report list, report preview, or report-scoped lead
  detail by default.
- Delivery history scope should show the selected report and latest delivery
  status, then reveal detailed attempts on demand.

Preserved behavior:

- Preserve CR-043 one-switch real-email safety behavior and default-off state.
- Preserve CR-044 test-mail recipient count/source and SMTP acceptance
  warning.
- Preserve report generation when email fails or real SMTP is disabled.
- Preserve delivery history, manual resend, automatic/manual send type,
  recipient summaries, and customer-safe delivery errors.
- Preserve administrator-only real-email control and role-safe visibility.

Scope boundary:

- This CR changes frontend information architecture and action placement. It
  should not change SMTP delivery logic, delivery-log schema, recipient
  precedence, permission rules, or real-email safety semantics.
- This CR does not add role quotas, normal-user resend policy, or new mail
  provider troubleshooting.

Non-goals:

- Do not remove the real-email safety switch.
- Do not hide safety status or SMTP acceptance warnings entirely.
- Do not create a second real-email send toggle.
- Do not treat SMTP `sent` as proof of recipient inbox delivery.
- Do not send real SMTP during automated verification.

Status: Verified

Related tasks:

- Phase 21I Mail Configuration in `TASKS.md`
- Phase 21M Report Center in `TASKS.md`
- CR-049 Mail Configuration And Delivery History Action Hierarchy in
  `TRACEABILITY.md`

Acceptance:

- Mail Configuration has one page-level primary action bar for edit, test,
  refresh/status, delivery-status navigation, and compact real-email state.
- The SMTP/defaults section no longer repeats primary edit/test actions and
  reads as status/configuration summary.
- The real-email send state is visible but compact when off, and still uses an
  explicit confirmation before turning on.
- Report Center delivery history is opened from a scoped report action/status
  and does not dominate the initial report page layout.
- Existing CR-043/CR-044 safety behavior and wording remain intact.

Verification:

- Verified on 2026-06-17 in the focused CR-048/CR-049 frontend batch. Mail
  Configuration keeps edit, test, refresh/status, delivery-status navigation,
  and the single real-email switch in the page-level action bar.
- The old first-level "SMTP 与发送默认值" and full-width real-email status
  panels were removed; the page now shows only compact summary metrics plus
  the modal edit/test flows.
- Report Center no longer renders `email_delivery_history` as a first-level
  panel. Clicking a report email status or "更多 > 查看交付历史" opens a scoped
  delivery-history drawer with selected-report scope, count, refresh action,
  latest status, and SMTP-acceptance wording.
## CR-050 - Report Center Lead Status Filter Precision Regression Fix

Date: 2026-06-17

Source: user manual acceptance found that after filtering Report Center lead
details by `高风险`, switching to `疑似负面` still showed both `疑似负面` and
`高风险` rows.

Module: Report Center, leads API, report risk filters

Type: Regression Fix

Background:

CR-045/Phase 7.2A-B split lead states into unrelated, evaluated no-risk,
suspected negative, high-risk, pending manual review, and
unevaluated/limited-context. The Report Center filter implementation still
treated `risk=negative` as a broad "all negative" bucket for lead details,
including both `high_risk` and `suspected_negative` rows. Report-list filtering
also used `negative_count`, which is a total negative summary count and can
include high-risk rows.

Purpose:

Make Report Center status filters match their labels. `高风险` must mean exact
high-risk rows, while `疑似负面` must mean exact suspected-negative rows.

Requirement:

- `/api/monitor/leads?risk=high` must return only `lead_status=high_risk`.
- `/api/monitor/leads?risk=negative` must return only
  `lead_status=suspected_negative`.
- Report-list `risk=negative` filtering must use an exact suspected-negative
  count, not the total negative count that includes high-risk rows.
- Existing total negative report summary and report template placeholders may
  remain compatible, but they must not drive exact status filtering.
- Pending review, unrelated, evaluated no-risk, and unevaluated/limited-context
  filters must remain separate.

Scope boundary:

- In scope: Report Center risk filter semantics, leads API filter semantics,
  derived report lead-count summary fields, targeted regression tests, and
  documentation.
- Out of scope: Phase 7.2C-D relevance hardening, AI calibration fixtures,
  Phase 19 realtime progress, Phase 20 AI traceability, report visual redesign,
  or historical data repair.

Non-goals:

- Do not change crawler behavior, AI provider behavior, SMTP delivery, role
  scope, or production/runtime data.
- Do not rewrite historical report artifacts just to backfill display-only
  summary fields.

Status: Verified

Related tasks:

- CR-050 Report Center Lead Status Filter Precision Regression Fix in
  `TASKS.md`
- CR-045/Phase 7.2A-B in `TASKS.md`
- PR-RUNREPORT-001 in `TRACEABILITY.md`

Acceptance:

- A high-risk-only report or lead is not returned by the `疑似负面` filter.
- A suspected-negative-only report or lead is not returned by the `高风险`
  filter.
- A mixed report can still appear when filtering by suspected negative, but its
  lead details show only suspected-negative rows under that filter.
- No-risk, unrelated, pending-review, and unevaluated filters remain unchanged.

Verification:

- Verified on 2026-06-17 with targeted regression coverage proving
  high-risk and suspected-negative report/lead filters do not include each
  other.
