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
- CR-047: Account Identity Fidelity
- CR-048: Report Center Lead Detail Information Architecture
- CR-049: Mail Configuration And Delivery History Action Hierarchy
- CR-050: Report Center Lead Status Filter Precision Regression Fix
- CR-051: Task Center And Report Grouping Consolidation
- CR-052: Task Center Row Action Deduplication
- CR-053: Task Center Field Priority And Global Select Alignment
- CR-054: Task Center Status Badge Compactness Regression Fix
- CR-055: Task Center Status Column Visual Refinement
- CR-056: Filter Dropdown Alignment Regression Fix
- CR-057: Task Center Group Summary Metric Chips
- CR-058: Filter Date Picker Alignment Regression Fix
- CR-059: Filter Date Picker Edge Anchoring Regression Fix
- CR-060: Filter Date Picker Compact Center Alignment Regression Fix
- CR-061: Filter Date Picker Trigger-Width Anchoring Regression Fix
- CR-062: Filter Date Picker Grid Compression Regression Fix
- CR-063: Filter Date Picker Readable Anchored Popover Regression Fix
- CR-064: Filter Date Picker Trigger-Attached Edge Shrink Regression Fix
- CR-065: Filter Date Picker Center-Anchored Visual Alignment Regression Fix
- CR-066: Filter Date Picker Trigger-Attached Dropdown Alignment Regression Fix
- CR-067: Filter Date Picker Trigger-Width Visual Attachment Regression Fix
- CR-068: Filter Date Picker Local Attached Menu Regression Fix
- CR-069: Run Detail AI Evaluation Lead Entry Consolidation
- CR-070: Account Environment Export And Import Package
- CR-071: Drawer And Modal Select Dropdown Consistency
- CR-072: Task Edit Custom Date Picker Consistency
- CR-073: Scrollable Drawer Corner Radius Regression Fix
- CR-074: Console Refresh Action Deduplication And Icon Loading
- CR-091: Open Todo MECE Rebaseline And Phase 5.1 Preflight Gate
- CR-092: Frontend Stack Migration Evaluation And Monitor Next Plan
- CR-093: MediaCrawler Internalization And Public Exposure Boundary
- CR-094: Crawler Engine Provider Architecture
- CR-095: Atomic Goal Execution Governance And Readiness Gate
- CR-097: Operations Home Visual Density Reduction
- CR-098: Operations Home Data-First Visual Refit
- CR-099: Operations Home Legend-First Visual Clarity
- CR-100: Operations Home Dense Visual Composition
- CR-101: Operations Home Flow Chart Layer Separation
- CR-102: Operations Home Flow Chart Node Simplification
- CR-103: Operations Home Flow Chart Semantic Trend Rebuild
- CR-104: Operations Home Data Cockpit Moderate Rebuild
- CR-105: Operations Home ECharts Dashboard Rebaseline
- CR-106A: Operations Home Data-Aware Signal Refinement
- CR-106B: Email Delivery Log Dashboard Aggregation
- CR-107: Windows One-Click Local Startup Launcher And Browser URL Separation
- CR-108: Local/Server Login Initialization And Verification Flow Hardening
- CR-109: Monitoring Task Collection Rule Explanation Removal
- CR-110: QR Login SMS Verification Manual Submission Regression Fix
- CR-111: Current-Main Documentation State Synchronization
- CR-112: Local Browser Auto-Sync Cookie Acquisition
- CR-113: QR Draft Account Identity Choice Forwarding
- CR-114: Browser Runtime Binding Object Identity Collision Regression Fix
- CR-096: AI Evaluation Postprocessing Scope Reduction
- CR-075: Responsive Navigation Interaction Consistency
- CR-076: Mobile Header Layout Resilience Regression Fix
- CR-077: Mobile Header Final Cascade Resilience Regression Fix
- CR-078: Mobile And Tablet Navigation Layout Resilience Regression Fix
- CR-079: Mobile Header Compact Rail Regression Fix
- CR-080: Tablet Side Rail Horizontal Scrollbar Cleanup
- CR-081: Scrollable Drawer Fixed Footer Boundary Regression Fix
- CR-082: Drawer Scrollbar Header Footer Boundary Recheck
- CR-083: AI Access Model Helper Copy Removal Regression Fix
- CR-084: Tablet Side Rail Narrow-Width Collapse Regression Fix
- CR-085: Narrow Tablet Inline Cascade Side Rail Regression Fix
- CR-086: Explanatory Helper Copy Tooltip Consolidation
- CR-087: Explanatory Helper Tooltip Removal
- CR-088: AI Rule Modal Residual Helper Text Removal
- CR-089: Mail Template Row Helper Text And Update-Time Compactness
- CR-090: AI Rule List And Modal Field Width Compactness

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

Status: Verified

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

## CR-107 - Windows One-Click Local Startup Launcher And Browser URL Separation

Date: 2026-06-24

Source: user request for a Windows one-click startup scheme

Module: deployment/startup ergonomics

Type: Existing Feature Optimization

Status: Verified

Background:

The repository already has separate startup entry points for the WebUI
service and for opening the browser. The current experience still requires
operators to connect the bind host, port, and browser URL manually, which can
lead to mistakes if the service binds on `0.0.0.0` but the browser should open
`127.0.0.1` locally or an explicit remote URL.

Purpose:

Provide one Windows-friendly entry point that starts the service, waits for it
to become healthy, and opens the correct browser URL without conflating the
service bind host with the browser destination.

Requirements:

- Add a Windows one-click launcher that starts `/monitor` with one command.
- Keep the service bind host and browser open URL separate.
- Default the browser open URL to the local machine URL when no explicit
  override is provided.
- Allow an explicit browser URL override for remote access or proxy-based
  access.
- Preserve the existing service-only startup entry points.

Scope boundary:

- Deployment/startup ergonomics only.
- No backend API, database, permission, crawler, AI, SMTP, scheduler, or
  browser UI changes.
- No Windows service installer, auto-update, or dependency bootstrap.

Non-goals:

- Do not change the `/monitor` page behavior.
- Do not introduce a new build pipeline or runtime framework.
- Do not auto-detect or rewrite remote network topology beyond the explicit
  browser URL override.

Related tasks:

- Windows one-click startup task in `TASKS.md`
- Windows one-click launcher checks in `TEST_PLAN.md`
- Startup instructions in `README.md` and `SERVER_DEPLOYMENT.md`

Acceptance:

- A single Windows launcher script starts the service and opens the browser.
- The launcher defaults to a local browser URL while the service may bind to
  `0.0.0.0`.
- An explicit browser URL override is honored without changing the bind host.
- Existing service-only startup commands still work.

## CR-108 - Local/Server Login Initialization And Verification Flow Hardening

Date: 2026-06-26

Source: user reports from a newly cloned Windows computer and follow-up review
of the older server-login/SMS/Docker worktree at
`C:\Users\Administrator\.codex\worktrees\1d0a\MediaCrawler`.

Module: deployment startup, platform-account login sessions, server-side QR
login, local Windows first-run login initialization, Docker/server packaging.

Type: Existing Feature Optimization and Regression Fix

Status: Verified

Background:

CR-107 made the Windows launcher start `/monitor` and open the browser with a
separate bind-host/browser-URL model. A newly cloned Windows machine can still
fail the first real platform login because the account profile is machine-local
and must be initialized on that machine or server. The same investigation also
showed that opening a local login window and then starting a QR session can make
both flows compete for the same account profile, leading to unclear QR failure
messages such as a closed browser session or an occupied Profile.

The older worktree contains useful but stale server-side evidence: Docker
packaging, Tencent server QR/SMS verification UI work, and a Douyin
second-verify exact `验证` submit fix. That worktree used its own CR-107 and
CR-108 numbering, which conflicts with the current mainline where CR-107 is the
Windows one-click launcher. Those older entries are historical evidence and
implementation source material only; they must be remapped into this current
CR-108 instead of copied with their old numbering.

A local one-click verification run also showed a QR initialization hang:
`POST /api/monitor/login-sessions` could remain blocked inside the
server-side Playwright/platform preparation path, leaving the database session
in `preparing`. A later poll could then report that the QR browser session was
not running before the original initialization attempt had reached a QR handle.
CR-108 must bound that startup path, clean up half-initialized browser state,
and keep fresh `preparing` sessions pending until the QR startup timeout window
has actually elapsed.

A follow-up local scan test showed a second hang after the QR image was already
visible: authenticated polling of `/api/monitor/login-sessions/{id}` could
block while checking MediaCrawler login state or re-reading the QR image. CR-108
must also bound each polling step so a slow platform page cannot stop the UI
from continuing to show a pending confirmation state.

A later regression check found that the scan-time polling hardening was too
aggressive around login-state confirmation: the polling route wrapped
`_is_logged_in()` with the same short timeout that `_is_logged_in()` uses for
the MediaCrawler login-state method itself. If the MediaCrawler check timed out
right when the platform had already written login cookies/session state, the
outer timeout could cancel the fallback cookie/session checks and leave the UI
waiting instead of advancing to success. CR-108 must keep the MediaCrawler
method bounded without cancelling the same-account cookie/session fallback.

Purpose:

Make first-run platform login reliable and understandable in both supported
modes:

- server/container mode uses the server-side QR/status flow and disables local
  login windows;
- Windows local mode can use a service-owned visible browser window as an
  explicit development/operator fallback when the platform requires captcha,
  SMS, slider, or device verification;
- QR login and manual login windows must not silently compete for the same
  `profile_key` or runtime profile path.

Scope Boundary:

- Documentation must land first and pass consistency checks before code changes.
- Docker/server packaging may be selectively migrated from the older worktree.
- Login-session changes are limited to profile contention, customer-safe state
  messages, verification-state clarity, and first-run guidance.
- Existing dashboard, Task Center, Run Detail, routing, permissions, reports,
  crawler business logic, AI, and email behavior must stay unchanged.
- New work must preserve the existing `profile_key` account model and must not
  expose raw `profile_path`, cookies, QR payloads, verification codes, local
  commands, proxy credentials, or browser profile directories.

Non-goals:

- Do not bypass captcha, slider, SMS, phone confirmation, or platform risk
  checks.
- Do not automate SMS receiving.
- Do not add new backend platform fields or migrate to another frontend stack.
- Do not directly merge the old server-login worktree.
- Do not treat Docker configuration parsing as proof that every Windows host's
  Docker Desktop or WSL engine is healthy.

Required merge policy:

- Use the current mainline CR numbering; old worktree CR-107/CR-108 content is
  folded into current CR-108 as historical evidence or implementation source.
- Copying old documentation verbatim is forbidden when it would introduce
  conflicting CR numbers or claim unverified current-main status.
- `TEST_RESULTS.md` must distinguish current-main verification, old-worktree
  evidence, Tencent server evidence, and items that are not revalidated.

Related tasks:

- CR-108 documentation-first task group in `TASKS.md`.
- CR-108 login/Docker tests in `TEST_PLAN.md`.
- CR-108 traceability row in `TRACEABILITY.md`.

Acceptance:

- CR-108 documentation gate passes before non-document code changes.
- Docker packaging is migrated only as a selective, tested package with clear
  host-health limitations.
- QR sessions and local login windows are mutually exclusive for the same
  account profile and show customer-safe conflict messages.
- QR session startup is bounded by the configured timeout, cleans up partial
  Playwright/browser state on timeout, and does not let polling prematurely
  convert a fresh initializing session into `qrcode_failed`.
- QR session polling is also bounded per step after scan, so login-state checks,
  QR rediscovery, and manual-verification detection cannot block the UI polling
  loop indefinitely.
- Local Windows first-run login has a clear path for manual platform
  verification and follow-up account check.
- Server/container mode keeps local-window login disabled and uses server-side
  QR/status flow.
- If Douyin SMS/diagnostic improvements are migrated, the exact second-verify
  `验证` action is preferred without clicking send/resend controls.
- Required automated checks and documented manual acceptance pass or are
  explicitly recorded as not revalidated.

## CR-109 - Monitoring Task Collection Rule Explanation Removal

Date: 2026-06-26

Source: user screenshot and request to remove the "采集规则说明" block from the
Monitoring / 舆情监控 task page.

Module: Monitoring task page frontend.

Type: Existing Feature Optimization

Status: Verified

Scope:

- Remove the standalone "采集规则说明" disclosure block below the monitoring
  task table.
- Remove CSS that only styled that deleted task-page disclosure block.
- Preserve task creation/editing, filters, task table, drawer workflow,
  platform accounts, crawler behavior, login, reports, AI, email, permissions,
  and backend API contracts.

Acceptance:

- The Monitoring / 舆情监控 page no longer renders "采集规则说明".
- Static frontend regression coverage fails if the text returns to the
  monitoring task section.
- JavaScript syntax, documentation checks, and whitespace checks pass.

## CR-110 - QR Login SMS Verification Manual Submission Regression Fix

Date: 2026-06-26

Source: user report that Douyin showed SMS/captcha verification but the current
version did not have the older worktree's send/input/submit verification-code
flow.

Module: platform-account login sessions, server-side QR login, account login
modal frontend.

Type: Regression Fix

Status: Verified

Background:

CR-108 deliberately did not migrate the older worktree SMS submit route because
current main did not yet expose the required SMS submission API and UI. The
latest manual Douyin QR test showed that this missing piece is now a real
operator blocker: the UI can show `needs_verification` and tell the operator
to handle verification, but it only offers "我已处理，继续确认" or the local
login-window fallback. In server-like QR mode, the operator also needs a
bounded manual path to request a platform SMS code, type the code they receive,
and submit it into the server-side browser session.

Purpose:

Restore the manual SMS verification loop for server-side QR login without
adding SMS receiving automation or bypass behavior.

Scope Boundary:

- Add backend login-session endpoints for requesting and submitting a manually
  received SMS verification code.
- Add frontend controls for send, input, inline validation, submit, and
  continue-confirm when `verification_type` is `sms`.
- Prefer the Douyin `#uc-second-verify` exact visible `验证` control when
  submitting the code so send/resend controls are not clicked as submit.
- Preserve existing QR, local-login-window fallback, account check, profile
  locking, task execution, reports, AI, email, permissions, and crawler
  business logic.

Non-goals:

- Do not receive, read, intercept, or automate SMS.
- Do not bypass captcha, slider, phone confirmation, device verification, or
  platform risk checks.
- Do not migrate the older worktree's larger technical diagnostics UI.
- Do not expose verification codes, cookies, profile paths, QR payloads, local
  commands, or proxy credentials in customer-facing UI.

Related tasks:

- CR-110 task block in `TASKS.md`.
- CR-110 tests in `TEST_PLAN.md`.
- CR-110 traceability row in `TRACEABILITY.md`.

Acceptance:

- When a login session reports SMS verification, the account login modal shows
  a compact send/input/submit/continue-confirm panel.
- The input preserves the typed code while the UI is re-rendered.
- Backend routes can request SMS send and submit the code to the active
  server-side browser session.
- Douyin second-verify submission prefers the exact visible `验证` control and
  does not click send/resend controls as submit.
- Automated tests cover route behavior, server-page submission, send-code
  clicks, frontend rendering, inline validation, and login regression scope.

## CR-111 - Current-Main Documentation State Synchronization

Date: 2026-07-12

Source: user request to synchronize all project governance documents against
the code and verification evidence currently merged on `main`.

Module: documentation governance, current state, task lifecycle, validation,
and traceability.

Type: Documentation Governance and Regression Fix

Status: Verified

Background:

The current code baseline is `main` at `abb4d66`. The product implementation,
tests, and traceability records show that several CRs are verified, while some
older lifecycle labels still say `Accepted`, `In Progress`, or `Implemented`.
`TASKS.md` also keeps five unchecked CR-107 planning items beside a completed
implementation checklist, `CURRENT_STATE.md` still contains pre-merge wording
for Phase 21 and CR-107 through CR-110, CR-052 lacks a traceability row, and
CR-066 lacks a `Status` field. The existing automated documentation check
passes because it validates structure and references, not every semantic
lifecycle comparison.

Purpose:

Make the human-readable governance documents describe the actual current-main
baseline without reopening completed work, promoting future or gated work, or
changing product behavior.

Current Baseline:

- Baseline source: clean `main` at `abb4d66`, matching the current local
  `origin/main` tracking reference.
- Baseline evidence read: current Git/worktree state, all open `TASKS.md`
  checkboxes, CR statuses, traceability rows, current-state text, test plans,
  test results, recent commit contents, relevant implementation symbols, and
  targeted/full validation commands.
- Existing behavior to preserve: Phase 21 remains closed; CR-107 through
  CR-110 remain current-main history; Phase 5.1P remains the first unblocked
  lane; Phase 5.1A-D and Phase 5.2 remain dependency-gated; `Needs
  Confirmation`, deferred, operator-gated, and historical items remain
  non-executable.
- Out of scope: product code, UI behavior, schema, runtime data, account
  profiles, cookies, local databases, deployment secrets, and old-worktree
  mutation or merge.
- Old-baseline conflict rule: current `main` plus verified current documents
  win over stale planning labels, unmerged worktree content, old screenshots,
  or chat history.

Scope Boundary:

- Synchronize CR lifecycle labels only where current code, completed tasks,
  traceability, and recorded verification provide sufficient evidence.
- Mark the duplicate unchecked CR-107 planning checklist complete while
  preserving its verified implementation checklist.
- Repair current-state wording and keep the next allowed lane explicit.
- Add missing CR-052 traceability and CR-066 status metadata.
- Fix the documentation check's `Needs Confirmation` parser so a later CR's
  status cannot be attributed to an earlier CR section.
- Record semantic status-review guidance without claiming it is already an
  automated `scripts/check_docs.py` check.
- Append validation evidence for this documentation-only synchronization.

Non-goals:

- Do not implement Phase 5.1, Phase 5.2, CR-092, CR-093, CR-094, CR-106B, or
  any operator-gated historical repair.
- Do not treat Docker Compose configuration validation as proof that this host
  can run Linux containers or that production deployment is accepted.
- Do not treat unit/static tests as new real-platform, SMTP, AI-provider, or
  production-pilot evidence.
- Do not merge, reset, clean, or delete the old server-login worktree.

Related tasks:

- CR-111 task block in `TASKS.md`.
- CR-111 semantic alignment checks in `TEST_PLAN.md`.
- CR-111 row in `TRACEABILITY.md`.
- CR-111 evidence entry in `TEST_RESULTS.md` after verification.

Acceptance:

- Lifecycle labels, task completion, current-state wording, and traceability
  no longer contradict verified current-main evidence.
- Remaining unchecked tasks are only current, dependency-blocked,
  future-only, `Needs Confirmation`, or operator-gated work.
- Phase 5.1P remains the first unblocked lane and no future/gated item is
  promoted to implementation-ready.
- `GOAL.md`, `DECISIONS.md`, specialist product documents, README, and
  deployment documents remain unchanged when their existing statements match
  current code and proof boundaries.
- Documentation consistency, machine-readable dry-run validation, relevant
  tests, Docker Compose configuration, and whitespace checks pass.
- A focused regression test proves `Needs Confirmation` detection does not
  cross CR section boundaries.

## CR-112 - Local Browser Auto-Sync Cookie Acquisition

Date: 2026-07-19

Source: user request to improve local account login by automatically acquiring
and validating Cookie material from a project-managed browser, followed by a
Claude Code cross-validation request and formal project-document synchronization.

Module: platform account login, browser environment, Cookie acquisition,
multi-account binding, local deployment, and login UI.

Type: New Capability

Status: Needs Confirmation

Interpretation: except for the explicitly labeled 2026-07-19 confirmed
login-material sub-decision, all CR-112 schema, runtime, connector, extension,
protocol, migration, and acceptance wording below is proposed future contract,
not current implementation or verification evidence.

Background:

The current product supports server-side QR login, a local visible-browser
fallback, and manually pasted Cookie login. The local visible-browser fallback
still requires the operator to return to the monitor and complete follow-up
steps, while manual Cookie login requires external copying and pasting. A
CookieBridge reference implementation demonstrates browser-extension Cookie
observation, but the evaluated source uses an unauthenticated `client_id`, can
select an arbitrary available client, hardcodes `ws://localhost:8274/ws`, keeps
connection/cache state in memory, requires Python 3.12 for its reference
server, and is licensed for non-commercial learning use.

Purpose:

Plan an optional local-desktop workflow in which the monitor opens a dedicated
application-managed Chrome or Edge Profile, the user completes normal platform
login in that browser, a project-owned compatible extension synchronizes the
exact account's Cookie material to a loopback connector, and the monitor
validates and encrypts the Cookie without manual copy/paste. Preserve the
server-first QR production boundary and the advanced manual Cookie path.

Proposed Product Boundary:

- Keep the backend login types `qrcode` and `cookie`; represent automatic and
  manual Cookie acquisition with `cookie_source=bridge|manual` rather than a
  third login type.
- Keep QR login as the default user-facing method. Show local browser auto-sync
  only when the feature is enabled and healthy. Keep manual Cookie entry in a
  collapsed advanced section and do not automatically promote it after a
  Bridge failure.
- Use an application-managed persistent Profile derived from `profile_key`.
  Do not depend on the user's default Chrome Profile, a Google account, manual
  Chrome Profile creation, extension-store installation, or developer-tools
  Cookie copying.
- Resolve a valid explicit `MONITOR_BROWSER_EXECUTABLE` first, then Chrome,
  Edge, and supported Chromium. Chrome remains preferred when Chrome and Edge
  both exist.
- Limit V1 auto-sync to a same-host Windows local-desktop topology. The
  project-owned connector is proposed as a feature-gated WebSocket module in
  the existing Python 3.11 FastAPI service and accepts extension connections
  only through loopback.
- Because the monitor service may listen on `0.0.0.0`, enforce locality from
  the server-side socket peer rather than only from the extension URL. Accept
  only a parseable loopback peer (`127.0.0.1` or `::1`), ignore
  `X-Forwarded-For`/`Forwarded` for this authorization decision, require the
  exact stable `chrome-extension://<extension-id>` Origin, and reject invalid
  peer or Origin before WebSocket acceptance.
- When the feature is disabled, do not mount the connector route. A normal HTTP
  probe receives 404; the pinned Starlette/Uvicorn baseline rejects an
  unmatched WebSocket upgrade with 403 before acceptance, and Packet B fixes
  the packaged-runtime expectation. When enabled, reverse proxies must deny
  and must not forward `/api/monitor/cookie-bridge/`; LAN-address access,
  spoofed forwarding headers, missing/wrong Origin, and reverse-proxy access
  must fail before connector protocol state.
- Current status-code evidence is FastAPI `0.110.2` and Uvicorn `0.29.0` exact
  pins plus Starlette `0.37.2` in `uv.lock`. Dependency changes may update the
  asserted status only after re-audit; route absence and zero protocol state do
  not change.
- Keep production/server acceptance on the current server-started QR browser
  and server-persisted Profile. Local Chrome/Edge success is not production
  acceptance. Remote/cross-host Bridge and headless Bridge support remain
  outside V1 unless a later accepted decision and test result add them.

Confirmed Identity And Login-Material Contract (2026-07-19):

- `social_account` plus `profile_key` remains account identity authority.
  QR login and accepted Cookie login both converge on the application-managed
  persistent Profile resolved from that `profile_key`. The Profile is the
  normal browser session and crawl environment for both modes.
- A Bridge- or manually supplied Cookie is bootstrap, refresh, recovery, and
  migration material. Inject it into an account-bound persistent Profile,
  validate the exact platform identity in that same Profile, and activate the
  result only after validation. Retain the verified Cookie through the
  encrypted account store; connector cache is temporary acquisition state.
- For an existing active account, keep one fixed active path derived from
  `profile_key` and use the durable, same-volume candidate/rollback promotion
  journal defined in `ACCOUNT_ENVIRONMENT.md`. Failed validation, swap,
  active-path recheck, or database commit preserves both the previous active
  Profile and previous verified encrypted Cookie, or blocks the account as
  `recovery_required` without guessing.
- Initialize the candidate fresh from the locked Phase 5.1 provider inputs;
  never clone or mutate the active Profile or its extension credential storage
  before `swapping`. Remove one-time Bridge material and perform the active-path
  recheck without Bridge/session-extension launch arguments.
- The target managed-account crawl path launches from the prepared persistent
  Profile and does not pass raw Cookie material in child-process arguments.
  Process inspection must prove raw Cookie is absent from child argv before
  Packet C is accepted.

Proposed Pairing And Security Contract:

- Reuse the existing draft-account flow so every new browser-sync session has a
  persisted account id and assigned `profile_key` before browser launch.
- Pair one login session to one extension `client_id` with a cryptographically
  random single-use token, short expiry, atomic consume, stable extension
  origin, Profile-scoped reconnect credential, credential rotation/revocation,
  and exact request/response ids.
- Derive the stable extension ID/Origin from packaged manifest-key material and
  prove it across Chrome, Edge, ephemeral copies, and clean installations. The
  extension requests only exact supported-platform/loopback permissions and
  excludes `<all_urls>` and unrelated hosts.
- Never select the first, newest, or only connected client implicitly. Empty,
  stale, late, replayed, wrong-origin, wrong-Profile, or wrong-platform claims
  fail closed and do not replace the previous verified Cookie.
- Store raw Cookies only through the existing encrypted account mechanism.
  Store only pairing/credential hashes server-side and redact Cookie, token,
  credential, raw Profile path, proxy secret, and extension internals from UI,
  logs, diagnostics, tests, and documentation evidence.
- Treat the temporary third-party CookieBridge source as evaluation evidence
  only. Product delivery requires written permission for the intended use or a
  project-owned compatible implementation; the proposed default is a
  project-owned implementation without copying restricted source.
- Classify current `runner.py --cookies` behavior as a pre-existing secret
  exposure risk because decrypted Cookie material can appear in OS process
  arguments and diagnostics. The accepted CR-112 target removes raw Cookie
  from child argv by preparing and validating the persistent Profile before
  crawler launch. Packet C must assign the migration owner, compatibility
  boundary, rollback, and tests before changing the current runner contract.
- Keep Bridge Cookie payloads structured and versioned so domain/path/security
  attributes and duplicate-name scopes survive transport. Advanced manual
  strings are canonicalized into the shared internal record model; unrelated
  domains, malformed scope, unsupported required attributes, and unbounded
  payloads fail closed.
- Deliver Packet C as C.1 shared Cookie-to-Profile promotion/recovery, C.2
  feature-gated Bridge acquisition, and C.3 internal profile-only runner
  migration. The Bridge flag controls only C.2. After C.3 acceptance, rollback
  preserves C.1/C.3 and never restores raw Cookie argv.
- C.2 uses `pending|active|revoked` binding lifecycle. Bridge commit activates
  the exact candidate and revokes the predecessor; manual-Cookie commit creates
  no candidate binding and revokes the predecessor; rollback revokes the
  candidate and preserves the predecessor.
- C.1 writes each rename checkpoint only after the rename succeeds. The
  account/Cookie/binding plus journal-commit database transaction decides old
  versus new authority; an operation marker and the exact directory-shape table
  resolve the one-rename checkpoint gap. Startup/periodic/pre-refresh cleanup
  keeps rollback artifact count at one.
- Keep customer-visible login types `qrcode|cookie`. The internal profile-only
  child path replaces managed `login_type=cookie` execution in CR-112 V1,
  performs a second login-state check, and fails `requires_relogin` before
  QR/Cookie/phone login code, generic Profile fallback, or default network can
  run. Existing QR/Profile execution remains regression-protected and is not
  silently reclassified.
- The C.3 parent keeps `--lt cookie`, adds hidden
  `--monitor_profile_only true`, passes the exact provider/account/promotion
  environment, clears/rejects Cookie material, and maps only child exit code 42
  to `requires_relogin`. C.3 is activated after a paused migration leaves no
  runnable version-0 Cookie account; version 0 is then rejected before spawn.
- `MONITOR_COOKIE_BRIDGE_ENABLED` is owned only by C.2 route/UI/readiness/
  extension/pairing code. C.1 manual validation/promotion/recovery and C.3
  command/child/platform guards remain independent when the flag is false.

Dependencies And Sequencing:

- Phase 5.1P is verified as a read-only preflight; its provider map remains the
  CR-047 implementation boundary.
- Phase 5.1A-C are implemented and independently verified. Phase 5.1D and the Phase 5.1
  acceptance gate remain owned by CR-047 and must complete before any CR-112
  product implementation.
- CR-070 / Phase 5.2 retains its currently accepted position after CR-047.
  CR-112 does not preempt or silently reorder CR-070 while this CR is `Needs
  Confirmation`; a later accepted sequencing decision must place the CR-112
  compatibility spike and implementation packets.
- CR-112 Packet B is a disposable compatibility/pairing/protocol spike only.
  It also fixes Cookie Protocol V1 fields and limits. Packet C contains serial
  C.1-C.3 local implementation. Packet D contains clean-computer and deployment
  acceptance. Each packet keeps its own start, exit, rollback, and stop gates.

Non-goals:

- No captcha, slider, device, or SMS bypass.
- No SMS receiving automation.
- No complex account rotation or dynamic proxy scheduling.
- No use of personal/default browser Profiles.
- No remote Bridge, cross-host Cookie transport, or local-browser-as-server
  production acceptance.
- No Firefox, Safari, or unverified Chromium-fork support.
- No third-party restricted-source bundling.
- No product-wide Python 3.12 upgrade or second connector service lifecycle.
- No implicit acceptance of raw Cookie exposure through subprocess arguments.
  Current `runner.py --cookies` remains baseline evidence until Packet C, but
  the accepted target requires persistent Profile preparation and no raw
  Cookie in managed crawler child argv.
- No Task Center, Run Detail, report, email, AI, role, or crawler-provider
  architecture changes.

Required Confirmations:

- Confirmed 2026-07-19: QR and Cookie login converge on the same account-bound
  persistent Profile; encrypted Cookie is bootstrap/refresh/recovery/migration
  material, and the target crawl path contains no raw Cookie in child argv.
- Confirm the same-host Windows local-desktop scope for V1 auto-sync.
- Confirm the project-owned extension and in-process Python 3.11 connector
  direction, subject to Packet B compatibility proof.
- Confirm CR-112 sequencing relative to the already accepted CR-070 / Phase 5.2
  lane after CR-047 acceptance.

Related Plans:

- `docs/superpowers/plans/2026-07-18-cross-computer-cookiebridge-login.md`
- `docs/superpowers/plans/2026-07-19-phase-5.1p-browser-provider-preflight.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-pairing-compatibility-spike.md`
- `docs/superpowers/plans/2026-07-19-local-browser-auto-sync-login.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-deployment-acceptance.md`

Related Governance:

- CR-112 task block in `TASKS.md`.
- CR-112 proposed boundaries in `ACCOUNT_ENVIRONMENT.md` and
  `SERVER_DEPLOYMENT.md`.
- CR-112 planned tests in `TEST_PLAN.md`.
- CR-112 proposed schema in `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`.
- CR-112 row in `TRACEABILITY.md`.
- CR-112 planning synchronization evidence in `TEST_RESULTS.md`.

Acceptance For This Documentation Stage:

- CR-112 remains `Needs Confirmation` and is not described as
  implementation-ready.
- Phase 5.1P and Phase 5.1A-C are recorded as verified, Phase 5.1D follows
  Phase 5.1C integration, and CR-047 and CR-070 ownership and sequencing are
  preserved.
- The five reviewed plan artifacts are linked from formal governance docs and
  distinguish roadmap readiness from future execution gates.
- All five plan artifacts and their CR-112 formal references in
  `CHANGE_REQUESTS.md`, `TASKS.md`, `CURRENT_STATE.md`, `TRACEABILITY.md`,
  `TEST_PLAN.md`, `TEST_RESULTS.md`, `ACCOUNT_ENVIRONMENT.md`, and
  `SERVER_DEPLOYMENT.md`, plus the CR-112 sections in `DATA_MODEL.md` and
  `SCHEMA_MIGRATION.md`, must be staged and committed atomically. A partial
  commit is not a valid CR-112 documentation delivery.
- Account, security, local/server, distribution, runtime, testing, proof, and
  rollback boundaries agree across all affected documents.
- The confirmed persistent-Profile authority decision is recorded in
  `DECISIONS.md`; CR-112 remains `Needs Confirmation` only for its other open
  product and sequencing decisions.
- Documentation consistency, whitespace validation, and focused independent
  read-only review pass.

Implementation Acceptance If Later Confirmed:

- Standard tests prove pairing, replay rejection, exact account routing,
  concurrent account isolation, timeout/cancellation/browser-close cleanup,
  restart/reconnect, prior-Cookie preservation, and no real external effects.
- Promotion tests kill/restart at every journal checkpoint and prove fixed-path
  restore/commit, bounded cleanup, disk/open-handle failures, no ambiguous
  dual-active Profile, and no database/Profile disagreement.
- Runtime tests prove missing/expired Profile returns `requires_relogin` before
  crawl and cannot enter QR, Cookie, phone, generic Profile, or default-network
  fallback.
- Cutover tests prove hidden profile-only CLI/provider-env wiring, default and
  explicit Cookie clearing, exit-code-42 mapping, zero runnable version-0
  accounts at activation, and version-0 pre-spawn rejection.
- Feature-off tests prove C.2 is removed while C.1 advanced manual Cookie and
  C.3 profile-only execution remain usable and raw argv stays retired.
- Opt-in Chrome and Edge tests prove extension Service Worker load, authenticated
  registration, exact client pairing, structured Cookie attribute fidelity,
  fixed protocol limits, stable manifest-key-derived ID/Origin, least-privilege
  permissions, and one synthetic Cookie roundtrip/Profile restart. Removing the
  session extension/config copy must leave the Profile crawler-usable without
  reconnect or a missing-path dependency.
- Security tests prove non-loopback socket peers, spoofed forwarding headers,
  missing/wrong extension Origins, and reverse-proxy forwarding fail before
  connector protocol state; feature-disabled startup leaves the route
  unmounted, returns HTTP 404, and rejects unmatched WebSocket upgrade with the
  packaged-runtime pre-accept status (403 on the pinned baseline).
- Process inspection proves the managed-account crawler child argv contains no
  raw Cookie after the persistent-Profile transition.
- A clean Windows installation requires no manual extension/Profile setup or
  extra connector/Python runtime placement.
- A local pilot verifies exact-account login, encrypted Cookie persistence,
  persistent Profile reuse after restart, and no sensitive evidence exposure.
- Existing server QR login, advanced manual Cookie login, account checks,
  scheduler/manual runs, and crawler behavior show no regression.

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

Status: Implemented

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

Status: Verified

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

Superseded current-rule detail:

- CR-096 keeps CR-045's lead-state safety, fallback, and prompt guidance, but
  supersedes the application-layer target-evidence gate as current behavior.
  Target evidence is now a prompt/model judgment constraint, not a hardcoded
  post-provider semantic override.

## CR-096 - AI Evaluation Postprocessing Scope Reduction

Date: 2026-06-21

Source: user review of a real clue where valid AI high-risk output was later
rewritten to unrelated by application postprocessing.

Module: AI evaluation postprocessing, trace safety, Phase 7.2 follow-up

Type: Regression Fix

Status: Verified

Background:

A collected clue with title text identifying "北京海安律师事务所" and negative
"被骗" allegations could be returned by the model as related, negative, and
high risk. The application-level target-evidence gate then compared only
hardcoded target terms such as "北京海安律所" and erased the model judgment to
`irrelevant`. The same hardcoded gate can also hide genuine risk when the
content uses reasonable law-firm name variants that the target/alias list did
not enumerate.

Purpose:

Narrow AI evaluation postprocessing from a second semantic judge to format and
storage-safety validation only. If the model returns a structurally valid
result, keep `is_related`, `is_negative`, `risk_level`, `reason`,
`evidence_quotes`, and `recommended_action` as the model output. Invalid or
malformed model output still falls back to `pending_review`.

Requirements:

- Remove application-layer semantic rewriting from AI evaluation
  postprocessing.
- Do not use hardcoded target-name, alias, `source_keyword`, or evidence quote
  matching to change a valid AI output to `irrelevant`.
- Keep JSON parsing, required-field checks, boolean coercion, `risk_level`
  enum validation, and `evidence_quotes` type normalization.
- Keep malformed JSON, missing fields, invalid risk levels, provider errors,
  and timeouts on the existing `pending_review` fallback path.
- Keep trace/log storage safety: API key, Authorization, Cookie, token,
  secret, password, SMTP password, proxy URL/credentials, profile path, local
  path, and server path redaction.
- Keep prompt/request/response/comment snapshot size caps and explicit
  truncation metadata.
- Keep prompt guidance that `source_keyword` is recall provenance only and
  should not by itself prove target-law-firm relatedness.

Scope boundary:

- In scope: `api/monitoring/ai.py` postprocessing behavior, focused regression
  tests, and documentation alignment for CR-045/Phase 7.2 current behavior.
- Out of scope: changing the core AI prompt, adding law-firm equivalent-term
  generation, adding suspicious-point annotations, adding a new manual-review
  state machine, changing frontend copy, or rewriting historical saved
  `irrelevant` evaluations.

Non-goals:

- Do not claim model output is a legal or factual conclusion.
- Do not remove trace redaction, trace truncation, or format validation.
- Do not auto-reprocess old rows that were already persisted as `irrelevant`.

Related tasks:

- CR-096 AI Evaluation Postprocessing Scope Reduction in `TASKS.md`
- CR-096 row in `TRACEABILITY.md`
- Phase 7.2 AI Evaluation Accuracy And Lead Status Tests in `TEST_PLAN.md`

Acceptance:

- A valid model result remains unchanged even when the only application-visible
  hardcoded target/alias evidence would previously have failed.
- `law_firm_name=北京海安律所`, `aliases=[]`, a title containing
  "北京海安律师事务所骗了", and a valid model high-risk result persist as high
  risk.
- Existing malformed-output tests still save `pending_review`.
- Phase 20B trace redaction and truncation tests still pass.
- Documentation states that CR-045's target-evidence gate is historical and
  superseded by CR-096 for current postprocessing behavior.

Verification:

- Verified on 2026-06-21 with targeted AI evaluation tests and docs
  consistency. Valid model output is preserved, malformed output still falls
  back to `pending_review`, and trace redaction/truncation coverage remains
  passing.

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

## CR-047 - Account Identity Fidelity

Date: 2026-06-17

Source: user request after reviewing CloakHQ/CloakBrowser-Manager as a
reference for stable browser-profile environments, followed by account
identity lifecycle discussion. This requirement was initially drafted locally
as CR-042, but CR-042 is already the historical rejected real-email
validation-window design, so this accepted requirement is recorded as CR-047.

Module: account environment, platform account login, server-side browser
runtime

Type: Existing Feature Optimization

Background:

Phase 5 and Phase 6 already established the core account-environment model:
one platform account maps to one `profile_key`, the server persists account
profiles, login and crawling use server-side browser sessions, and
account/profile/proxy locks prevent concurrent reuse. The remaining fidelity
gap is that `profile_key` identifies the persisted profile directory and
therefore preserves browser traces such as cookies, local storage, IndexedDB,
cache, history, preferences, service workers, and session state, but the
database does not yet explicitly persist the browser identity inputs that make
the account's login and crawl environment stable and self-consistent.

CloakBrowser-Manager is useful as a technical reference because it treats
browser profile properties such as platform, fingerprint seed, user agent,
timezone, locale, screen size, proxy, CDP access, and noVNC viewing as
profile-level settings. The project should learn from that profile-environment
model, but should not copy CloakBrowser-Manager's standalone account center,
database, authentication model, frontend, or deployment shape into this
system.

Purpose:

Make account identity fidelity explicit and enforceable:

```text
one platform account = one profile_key = one stable account identity
```

For the same platform account, server-side QR login, accepted Cookie
validation, login-state checks, and later crawling should all use the same
persisted profile traces, browser environment, proxy region/policy, runtime
binding, lock state, and audit trail. This is an account identity lifecycle
management requirement: profile traces plus browser environment plus proxy
region plus run binding plus lock/audit consistency.

Requirement:

- Add a persisted account identity configuration on top of the current
  `profile_key` model. The profile folder stores browser traces; the database
  stores the launch/environment rules and lock/audit state used to recreate the
  same identity.
- Persist at least these environment fields: `environment_region`,
  `browser_platform`, `identity_template`, `fingerprint_seed`, `user_agent`,
  `timezone`, `locale`, `accept_language`, `screen_width`, `screen_height`,
  `viewport_width`, `viewport_height`, `device_scale_factor`, `is_mobile`,
  `has_touch`, `identity_generator_name`, `identity_generator_version`,
  `identity_environment_version`, lock status/timestamp/reason,
  `requires_relogin`, account-bound `proxy_id`, and a customer-safe
  `proxy_region_snapshot`.
- Generate or assign the account browser environment before the first
  server-side QR login attempt or accepted Cookie login validation, and lock it
  after successful login validation.
- Introduce an Account Identity Generator that is stable, differentiated,
  self-consistent, and explainable. Given the same workspace, platform,
  account, proxy/region policy, automatic template selection or
  administrator-selected template family, and seed salt, it must produce the
  same identity. Different accounts should normally receive different
  fingerprints unless an administrator explicitly assigns a safe template
  family before first login.
- Template selection defaults to the system. Normal users cannot choose
  templates or browser-environment fields. Ordinary administrator account
  creation does not require template choice; an advanced pre-login path may
  choose only a template family, not individual UA, viewport, screen,
  timezone, locale, accept-language, or device flags.
- Introduce an Account Identity Validator that rejects inconsistent or
  incomplete identity data before login/crawl launch. It must catch mismatches
  such as proxy region versus timezone/locale, desktop UA with mobile touch
  flags, mobile UA with desktop screen assumptions, missing locked fields, and
  hidden process-default fallback.
- For China mainland proxies, the default generated region should be
  self-consistent: `environment_region = CN_MAINLAND`, `timezone =
  Asia/Shanghai`, `locale = zh-CN`, and `accept_language =
  zh-CN,zh;q=0.9`. The system should avoid overfitting province-level browser
  details and instead keep proxy region/ISP, device template, and browser
  environment coherent.
- Login, login-state checks, and crawling must read the same persisted account
  identity instead of deriving user agent, locale, timezone, viewport, proxy,
  or fingerprint inputs from changing process defaults.
- Existing Platform Accounts UI should show a customer-safe summary such as
  browser platform, timezone/locale, screen size, and proxy binding state, but
  must not expose raw profile paths, cookies, proxy credentials, local command
  lines, CDP endpoints, noVNC sessions, or fingerprint-debug output.
- Administrator changes to a locked browser environment require an explicit
  reset/re-login flow with audit logging. Silent edits after successful login
  are not allowed.
- Reconcile the existing proxy-priority rule with account-environment
  consistency before code implementation. Confirmed design: after CR-047 locks
  an account identity, the account-bound proxy is the stable default for that
  account, and task-level proxy overrides are blocked for locked account
  environments. Changing the proxy requires explicit reset/re-login.
- Introduce an internal browser-environment provider boundary so the existing
  Playwright/CDP path can consume the persisted settings first. V1 does not
  introduce CloakBrowser. CloakBrowser or CloakBrowser-Manager-style CDP/noVNC
  management may be evaluated later as an optional provider, not as a required
  dependency.
- Treat Canvas, WebGL, font inventory, `navigator.plugins`, extension state,
  and long browsing history as future/provider-dependent scope. They are not
  simple static launch options; they depend on provider behavior, browser
  build, OS/fonts, graphics stack, installed extensions, profile history, and
  runtime JavaScript probes. V1 must not claim these are fully managed unless a
  dedicated provider and effective-value validation are added.
- Use the implementation specifications in `ACCOUNT_ENVIRONMENT.md` as the
  source of truth for deterministic identity generation, template expansion,
  fail-closed validation, provider mapping, lifecycle state, runtime snapshots,
  audit events, and test safety tripwires.
- Persist `identity_state` and a customer-safe
  `identity_runtime_snapshot_json` so requested/effective browser identity
  values, provider metadata, unsupported fields, and no-fallback evidence can
  be audited without exposing cookies, proxy credentials, raw paths, CDP
  endpoints, or noVNC tokens.
- Tests and local diagnostics must not touch real profile roots, cookies,
  proxy credentials, or platform login sessions unless the explicit
  test-allow environment flags documented in `ACCOUNT_ENVIRONMENT.md` are set.
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
- V1 high-fidelity boundary: Playwright/CDP is the provider path. Canvas,
  WebGL, fonts, plugins, extensions, and long browsing history are recorded as
  future/provider-dependent, not as V1 acceptance commitments.
- Future high-fidelity browser-persona work should be estimated separately:
  about 1-2 days for provider/license/deployment review, 3-5 days for a local
  one-platform prototype, 1-2 weeks for optional provider integration with
  locks/redaction/runtime snapshots, and 3-6+ weeks for a production-grade
  browser-pool/profile-history capability.

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
- Do not promise complete Canvas, WebGL, font, plugin, extension, or long-term
  browsing-history management in V1.

Status: Accepted

Phase 5.1P preflight result (2026-07-19):

- Verified `docs/phase-5.1p-browser-entrypoint-map.md` as the read-only map of
  current login, validation, run, child-process, CDP, and fallback paths.
- Confirmed one immutable BrowserEnvironmentProvider plan/result contract can
  cover the formal monitor paths with caller-specific adapters.
- Phase 5.1A additive schema/read-compatibility is implemented and
  independently verified.

Phase 5.1B implementation result (2026-07-19):

- Implemented the exact six-template generator catalog, documented
  HMAC-SHA256 selection/fingerprint derivation, and fixed deployment-key domain
  separation.
- New account INSERTs generate and validate identity in one SQLite transaction;
  existing UPDATEs do not backfill or regenerate identity.
- Implemented fail-closed missing/contradiction/proxy/relogin checks, safe
  administrator pre-login region/template-family controls, API redaction, and
  blocked-by-default pytest Playwright entrypoints.
- Focused Phase 5.1B tests pass (`9 passed`) and the full monitor regression
  passes (`361 passed`).

Phase 5.1C implementation result (2026-07-19):

- Implemented SQLite-authoritative identity prepare/completion,
  lock/activation, failure recovery, safe configuration, non-destructive
  reset, and allowlisted audit behavior across QR, visible-browser, Cookie,
  Profile, verification-code, administrator-check, cancellation, and draft
  confirmation paths.
- Added the administrator safe environment summary and explicit locked
  change/reset/re-login flow; CR-113 fixes QR draft safe-choice forwarding.
- Focused Phase 5.1C/CR-113 tests pass (`17 passed`) and the full monitor
  regression passes (`378 passed`). Python compile, documentation gates,
  browser checks, and independent Claude Code full-diff review pass. Phase 5.1D
  and final server-like acceptance remain serially gated.

Related tasks:

- Phase 5.1 Account Identity Fidelity in `TASKS.md`
- CR-047 Account Identity Fidelity in `TRACEABILITY.md`

Acceptance:

- New platform accounts receive a deterministic `profile_key` and a persisted
  account identity configuration before first QR login or Cookie validation.
- Successful QR login or accepted Cookie validation locks the
  account identity configuration.
- Repeated login-state checks and crawl runs for the same account use the same
  stored `profile_key`, `browser_platform`, `fingerprint_seed`, `user_agent`,
  `timezone`, `locale`, `accept_language`, screen/viewport/device fields, and
  effective proxy policy.
- Same-platform accounts have separate profile keys and separate browser
  environment values unless an administrator explicitly chooses a safe template
  family before first login.
- Account Identity Generator output is stable for the same seed/input and
  self-consistent with the proxy region. Validator checks fail closed when
  identity fields are missing or contradictory.
- Automatic template selection is deterministic, traceable to the template
  catalog and generator version, and not dependent on runtime randomness or
  process defaults.
- Normal users cannot choose identity templates, and administrators cannot
  edit individual identity fields directly.
- The deterministic generation algorithm, provider contract, lifecycle state
  machine, fail-closed rules, and runtime snapshot shape are documented before
  implementation, and tests cover exact template expansion plus requested
  versus effective values.
- Attempts to edit a locked browser environment are blocked unless the operator
  uses an explicit reset/re-login path that records an audit log.
- Task-level proxy overrides are rejected for locked account environments. To
  use another proxy, an administrator must reset the account identity and
  re-login under the new proxy policy.
- Existing logged-in accounts are not silently backfilled with guessed identity
  values. They stay readable and should be re-logged in under the CR-047
  identity rules when the feature is implemented.
- Tests verify that service restart or process default changes do not change
  the observable account browser environment for subsequent login/crawl
  sessions.
- Tests prove local/automated runs cannot touch real account profiles,
  cookies, proxy credentials, or platform login sessions without explicit
  opt-in environment flags.
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
- Superseded in the current Task Center surface by CR-051/CR-052 follow-ups:
  the report-list row status/more-menu entry is no longer exposed, and the same
  delivery-history, resend, and download capabilities are reached through Run
  Detail.
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

## CR-051 - Task Center And Report Grouping Consolidation

Date: 2026-06-18

Source: user conversation

Module: formal console information architecture

Type: Existing Feature Optimization

Status: Verified

Background:

The console already has run detail, report grouping, and delivery-history
surfaces. The current split between Run Center and Report Center makes the
same operational story feel duplicated: one page shows execution records while
another shows grouped report artifacts. The user wants a single main task
center that makes the monitoring task-to-public-opinion relationship obvious
at a glance.

Purpose:

Consolidate the two top-level execution/report surfaces into one task-scoped
center. The user should be able to see, for each monitoring task, which
reports and public-opinion results belong to it without navigating through a
separate Report Center first.

Requirements:

- Rename the primary run/report entry to `任务中心` in the console navigation.
- Reuse the existing report grouping logic inside that center so task groups
  and their report rows are visible together.
- Remove the separate top-level Report Center entry and section from the main
  navigation.
- The first-level task-center list should not copy every old run-record
  column. It should prioritize monitoring-task identity and result summary:
  law firm/task, platforms, keyword summary, latest status or report state,
  latest run time where available, collected/new counts, suspected negative,
  high risk, manual review, unevaluated, and a run-detail drilldown.
- Operational run fields such as run ID, task ID, run type, visibility,
  duration, and full failure reason remain available in the `运行记录` subview
  and Run Detail.
- Keep Run Detail as the deep drilldown for lifecycle, logs, AI evaluation, and
  per-run report/email inspection.
- Keep report preview, run detail, report-scoped lead inspection, and delivery
  history reachable from the task-scoped surface.
- Preserve CR-048 / CR-049 scoped detail behavior; only the center-level IA
  changes.

Scope boundary:

- This CR changes frontend information architecture and entry placement only.
- It does not change backend APIs, data model, permissions, AI behavior, crawl
  behavior, SMTP behavior, or report generation semantics.

Non-goals:

- Do not introduce a new task database model.
- Do not reopen CR-048/CR-049 scoped drawer behavior.
- Do not add a second report workspace.

Related tasks:

- Phase 21L Run Center in `TASKS.md`
- Phase 21M Report Center in `TASKS.md`

Acceptance:

- The main navigation exposes a single task-centric entry instead of separate
  Run Center and Report Center entries.
- Grouped task/report rows are visible inside that entry and clearly show which
  reports belong to which monitoring task.
- Run Detail remains accessible as the deep drilldown for execution and AI
  detail.
- Report-scoped preview and delivery history remain reachable from the
  task-scoped surface.
- Existing CR-048 / CR-049 scoped drawer behavior remains intact.

Verification:

- Verified on 2026-06-18 with a frontend-only consolidation of the formal
  console: the navigation exposes `任务中心`, the separate `reports` section
  and `report_center` menu key are removed, legacy `reports` shortcut calls are
  normalized into the task-group view, report grouping renders inside
  `task_group_view`, and `run_records_view` preserves the old run-record table
  for operational troubleshooting.
- Targeted regression coverage
  `test_cr051_task_center_consolidates_report_grouping_without_separate_report_center`
  asserts the single-entry task center, grouped report surface, run-record
  subview, legacy route normalization, and first-level field split.

## CR-052 - Task Center Row Action Deduplication

Date: 2026-06-18

Source: user conversation

Module: formal console task center information architecture

Type: Existing Feature Optimization

Status: Verified

Background:

After CR-051 merged Run Center and Report Center into Task Center, some row
actions duplicated capabilities already available inside Run Detail. In the
run-record subview, `查看日志` opened the same run logs that are available in
Run Detail's `采集日志` section. In the task-group report rows, `预览` opened
the same report preview available from Run Detail's `报告` section.

Purpose:

Keep Task Center's first-level rows clean and make Run Detail the primary
drilldown for logs, reports, AI evaluation, and delivery evidence.

Requirements:

- Remove the run-record row-level `查看日志` button.
- Keep the same log content reachable from Run Detail's `采集日志` section.
- Preserve log copy and download actions from the Run Detail log section.
- Remove the task-group report row-level `预览` button.
- Keep report preview reachable from Run Detail's `报告` section.
- Keep task-group report rows focused on `运行详情` and `更多`; `更多` retains
  report-scoped lead inspection, delivery history, resend, and downloads.

Scope boundary:

- This is a frontend information-architecture cleanup only.
- It does not change run-log APIs, report preview APIs, report artifacts,
  permissions, crawler behavior, AI behavior, SMTP behavior, or data model.

Non-goals:

- Do not remove the standalone log drawer implementation if older paths still
  reference it.
- Do not remove report preview capability.
- Do not change CR-048 / CR-049 scoped lead and delivery-history behavior.

Related tasks:

- CR-052 Task Center Row Action Deduplication in `TASKS.md`
- CR-051 Task Center And Report Grouping Consolidation in `TASKS.md`
- Phase 20D Run Detail Frontend in `TASKS.md`

Acceptance:

- Run-record rows no longer show a first-level `查看日志` button.
- Run Detail still shows `采集日志` and can copy/download the current run logs.
- Task-group report rows no longer show a first-level `预览` button.
- Run Detail's `报告` section still exposes report preview.
- `运行详情`, `查看线索`, delivery history, resend, downloads, stop, archive,
  and restore remain available in their intended scopes.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage proving
  the row-level duplicate actions are removed while Run Detail retains log
  copy/download and report preview.

## CR-053 - Task Center Field Priority And Global Select Alignment

Date: 2026-06-18

Source: user conversation and in-app browser review

Module: formal console task center table density and global filters

Type: Existing Feature Optimization

Status: Verified

Background:

After CR-051 and CR-052, Task Center became the single operational entry, but
the run table still read too much like the old dense Run Center. The status
cell could contain long progress copy such as completed ingestion detail, key
run identifiers were not the first visible fields, the filter toolbar had two
refresh entry points, and native select dropdowns could appear visually
misaligned because the main content container clipped overflow.

Purpose:

Make Task Center easier to scan before opening Run Detail: operators should
first identify the monitoring task and concrete run, then read a compact
status and the most important business counts. Filters and dropdowns should
feel stable across all console pages.

Requirements:

- In flat mode, put `任务 ID` and `运行 ID` at the beginning of Task Center
  run tables, followed by compact `状态`.
- In grouped mode, keep `任务 ID` in the group header and hide the duplicated
  task ID column inside the group; group rows begin with `运行 ID` followed by
  compact `状态`.
- Keep status cells short. Terminal success rows should show `已完成` without
  appending long ingestion detail; active rows may show only short progress
  such as `AI 3/10` or `采集中 20（临时）`.
- Render the status cell as a compact badge, not as a full-width bar.
- Keep full lifecycle, progress, logs, report, AI evaluation, and delivery
  detail in Run Detail instead of expanding the first-level status cell.
- In grouped mode, continue using the same run-row mapping and field
  semantics, while keeping task ID, platform, keyword, and task name context in
  the group header to reduce duplicated width.
- Keep only one Task Center refresh entry at page level; the filter toolbar
  should keep `筛选` and `清空`.
- Prioritize the filter toolbar around task/law firm, status, platform, date
  range, and then secondary run type, visibility, and page size.
- Fix select/dropdown visual alignment globally by ensuring the main content
  container does not clip vertical overflow.

Scope boundary:

- This CR is frontend-only. It does not change backend APIs, permissions,
  data model, crawler behavior, AI behavior, SMTP behavior, report artifacts,
  or run/report semantics.

Non-goals:

- Do not reintroduce a separate Report Center.
- Do not add a new grouping model.
- Do not remove Run Detail fields or report/email/AI trace capabilities.

Related tasks:

- CR-053 Task Center Field Priority And Global Select Alignment in `TASKS.md`
- CR-051 Task Center And Report Grouping Consolidation in `TASKS.md`
- CR-052 Task Center Row Action Deduplication in `TASKS.md`

Acceptance:

- Flat Task Center rows begin with `任务 ID`, `运行 ID`, and compact `状态`;
  grouped rows hide duplicated `任务 ID` and begin with `运行 ID`, then `状态`.
- Completed rows do not show long progress detail inside the status cell.
- Status badges wrap to their own text width and do not stretch across the
  status column.
- Run Detail remains the place for full progress, logs, reports, AI
  evaluation, and delivery detail.
- Task Center has only one refresh button at page level.
- Native select dropdowns are not clipped or shifted by the main content
  container.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage and syntax
  checks proving the reordered headers, compact status logic, single refresh
  entry, and global content overflow fix.

## CR-054 - Task Center Status Badge Compactness Regression Fix

Date: 2026-06-18

Source: user in-app browser review of Task Center status cells

Module: formal console Task Center run table

Type: Regression Fix

Status: Verified

Background:

After CR-053, the Task Center table was intended to show compact status
badges, but a completed row could still display a long backend
`display_status` string such as completed ingestion detail inside the status
badge. This made the first visible column look like a long progress bar and
pushed important identifiers and run parameters out of view.

Purpose:

Restore the CR-053 compact-status contract: the first-level Task Center table
must show a short, scannable lifecycle label, while full progress and
ingestion detail stays in Run Detail.

Requirements:

- Task Center status badges must use normalized short lifecycle labels such as
  `已完成`, `运行中`, `部分失败`, `运行超时`, `已取消`, and `执行中断`.
- A long backend `display_status` or progress message must not be rendered as
  the status badge label.
- Completed rows must not show ingestion completion text in the status badge.
- The badge must stay text-sized and must not stretch across the status cell.
- Active rows may still show one short progress cue under the badge.

Scope boundary:

- This is a frontend-only regression fix linked to CR-053.
- It does not change backend APIs, run lifecycle semantics, database fields,
  AI behavior, report generation, email delivery, permissions, or Run Detail
  content.

Non-goals:

- Do not redesign Task Center again.
- Do not reintroduce duplicate row actions.
- Do not remove Run Detail progress, logs, AI evaluation, report, or email
  delivery information.

Related tasks:

- CR-054 Task Center Status Badge Compactness Regression Fix in `TASKS.md`
- CR-053 Task Center Field Priority And Global Select Alignment in `TASKS.md`

Acceptance:

- A completed row with a long `display_status` still renders the first-level
  status badge as `已完成`.
- First-level Task Center status badges use a compact text-sized style.
- Short active progress remains available below the status badge when a run is
  active.
- Existing field order, grouping, single refresh, and Run Detail entry remain
  unchanged.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, docs check, and browser inspection of the local `/monitor` page.

## CR-113 - QR Draft Account Identity Choice Forwarding

Date: 2026-07-19

Source: Phase 5.1C route audit of the existing new-account QR login flow.

Module: platform account draft creation, QR login, and account identity input
forwarding.

Type: Regression Fix

Status: Verified

Background:

The account form already submitted the administrator's safe
`proxy_region_snapshot` and `identity_template_family` choices to
`POST /login-sessions`. The route created the draft account with only name,
platform, proxy ID, and notes, so the two accepted identity choices were lost
and Phase 5.1B generated the CN/automatic default instead.

Requirements:

- Forward the existing `proxy_region_snapshot` and
  `identity_template_family` request values into
  `create_draft_social_account()` before QR login preparation.
- Keep generated fields such as user agent, timezone, locale, viewport,
  device flags, and fingerprint seed owned by the Account Identity Generator.
- Do not change existing-account QR payloads, login types, Profile ownership,
  proxy credentials, or normal-user permissions.
- Add a route regression test that captures the draft payload and proves the
  two safe values are forwarded while an attempted generated field is not.

Acceptance:

- A new-account QR login uses the same safe region/template-family choices
  shown in the account form.
- Unknown or generated identity fields are not forwarded to draft creation.
- Phase 5.1B remains historically verified; this follow-up does not reopen or
  rewrite that phase.

Verification:

- The focused CR-113/Phase 5.1C selection and full monitoring suite pass in
  the isolated Phase 5.1C worktree. Python compile, documentation gates,
  browser checks, and the independent Claude Code full-diff review also pass.

## CR-114 - Browser Runtime Binding Object Identity Collision Regression Fix

Date: 2026-07-19

Source: clean-worktree baseline verification after Phase 5.1D PR #5 merged.

Module: browser environment runtime binding and CDP page preparation

Type: Regression Fix

Status: Verified

Background:

Phase 5.1D stored BrowserContext plans, runtime proof state, and prepared Page
markers in process-global collections keyed only by Python `id(...)`. Python
may reuse an integer ID after an old object is released. A new Context could
therefore read another Context's plan, or a new CDP Page could be mistaken for
an already prepared Page and skip the required pre-navigation identity
commands. A fresh-worktree full-suite run exposed this as one intermittent
`Emulation.setUserAgentOverride` fail-closed test failure.

Requirements:

- Bind the immutable plan and mutable proof state to the exact BrowserContext
  object rather than a process-global numeric ID.
- Bind CDP preparation to the exact Page plus the current resolution and
  attempt, so a reused object ID or a rebound Page cannot skip preparation.
- Fail closed with the existing provider error family if a provider object
  cannot retain the binding.
- Preserve the exact CDP command order, requested/effective proof, safe result
  handling, and managed no-fallback behavior from Phase 5.1D.
- Add a deterministic regression that simulates repeated numeric object IDs
  and proves both Contexts use their own plans and both Pages are prepared.

Scope boundary:

- This follow-up changes only in-process BrowserContext/Page binding and its
  regression coverage. It does not change schema, API, UI, account identity
  fields, Profile/Cookie/proxy data, login types, deployment settings, or the
  CR-112/CR-070 boundaries.
- Phase 5.1D remains merged history. CR-114 owns this newly discovered defect
  and must merge before the separate Phase 5.1 server-like acceptance run.

Acceptance:

- The deterministic repeated-ID regression fails on the merged Phase 5.1D
  implementation and passes after the object-scoped binding change.
- Focused Phase 5.1B-D and full monitoring regressions pass serially.
- Python compile, documentation checks, independent read-only review, PR
  integration, and post-merge verification pass before server-like acceptance
  starts.

Verification:

- RED reproduced deterministically with one failing repeated-ID regression.
- The regression plus adjacent CDP preparation/failure checks pass (`7
  passed`), the focused Phase 5.1B-D selection passes (`132 passed`), and the
  full monitoring suite passes (`485 passed`). Python compile, documentation
  consistency/regression, and independent Claude Code full-diff review pass
  with no blocking or material finding. PR integration and post-merge
  re-verification initially remained open.
- PR #6 merged the fix as `main@27389a8`. Post-merge full monitoring tests
  pass (`485 passed`), focused Phase 5.1B-D tests pass (`132 passed`), and
  compile/documentation gates pass. CR-114 is closed; the separate Phase 5.1
  server-like acceptance packet is now the next unit.

## CR-056 - Filter Dropdown Alignment Regression Fix

Date: 2026-06-18

Source: user in-app browser review at 1440x900.

Module: formal console global filter dropdowns

Type: Regression Fix

Status: Verified

Background:

CR-053 reduced the original native select clipping issue by changing the main
content overflow rule, but at `1440x900` the browser still showed visual
misalignment for filter dropdowns. The reliable fix is to keep the existing
filter values and page logic, while replacing only the visual dropdown surface
inside `.page-filter-region` with a controlled in-page floating menu that is
positioned from the button itself.

Purpose:

Keep filter controls aligned across console pages at `1440x900`, `1024x768`,
and `390x844` without disturbing form selects used for edit drawers or other
non-filter configuration surfaces.

Requirements:

- Enhance only selects inside `.page-filter-region`.
- Keep the original `<select>` elements and `change` behavior so existing page
  filtering code continues to work.
- Render the visible filter control as a button plus fixed-position floating
  menu that is not clipped by table, drawer, or scroll-container layout.
- Keep the dropdown positioned from the clicked control and close it on outside
  click, Escape, resize, scroll, or menu selection.
- Do not touch ordinary configuration selects outside filter regions.

Scope boundary:

- Frontend-only regression fix linked to CR-053.
- No backend API, data model, run lifecycle, AI trace, report, or email logic
  changes.

Non-goals:

- Do not redesign Task Center again.
- Do not convert all form selects into custom menus.
- Do not alter the meaning of any filter values.

Related tasks:

- CR-056 Filter Dropdown Alignment Regression Fix in `TASKS.md`
- CR-053 Task Center Field Priority And Global Select Alignment in `TASKS.md`

Acceptance:

- Filter dropdowns in Task Center and other page filter toolbars stay aligned
  with their trigger control at `1440x900`.
- Filter selection still updates the underlying page logic.
- Non-filter form selects continue to use their existing native behavior.
- No new clipping or misalignment appears in the browser validation sweep.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, docs check, and browser inspection at `1440x900`.

## CR-057 - Task Center Group Summary Metric Chips

Date: 2026-06-18

Source: user in-app browser review of the Task Center grouped-run summary.

Module: formal console Task Center grouped run cards

Type: Existing Feature Optimization

Status: Verified

Background:

After Task Center consolidation, grouped mode correctly aggregates runs under a
monitoring task, but the group header summary rendered as one long sentence such
as `2 条运行 / 采集 ...`. At desktop width this made the top of each group feel
like unstructured copy rather than a scannable task summary.

Purpose:

Make the grouped Task Center header easier to scan while preserving the same
counts, grouping key, row table, Run Detail entry, filters, and role behavior.

Requirements:

- Keep the group header focused on monitoring-task identity: task/law firm,
  task badge, and task ID.
- Replace the long run-summary sentence with compact metric chips for run
  count, collected count, new count, suspected negative, high risk, manual
  review, and unevaluated.
- Use restrained risk emphasis for non-zero suspected negative, high-risk,
  manual-review, and unevaluated values.
- Keep limited-context, deleted-task, and historical-context explanations as a
  short note only when needed.
- Do not convert the group header into large nested cards or add duplicate row
  actions.

Scope boundary:

- Frontend-only information-density refinement linked to CR-051 through CR-056.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not reintroduce a separate Report Center.
- Do not change grouping semantics or table field order.
- Do not hide counts or move operational evidence out of Run Detail.

Related tasks:

- CR-057 Task Center Group Summary Metric Chips in `TASKS.md`
- CR-051 Task Center And Report Grouping Consolidation in `TASKS.md`

Acceptance:

- Grouped Task Center headers no longer show the aggregate counts as one long
  slash-separated sentence.
- The same aggregate values are visible as compact labeled chips.
- Limited-context or deleted-task context remains visible without dominating the
  header.
- Browser review at `1440x900` shows the grouped header is more scannable and
  does not collide with the table or filter dropdowns.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, docs check, and browser inspection at `1398x874` effective content
  viewport for the local `/monitor` page. Grouped Task Center headers render
  the aggregate values as compact metric chips and keep the grouped table,
  filters, single `详情` action, and Run Detail entry intact.

## CR-058 - Filter Date Picker Alignment Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-056 replaced filter-region selects with fixed-position in-page menus, but
Task Center date range filters still used native `<input type="date">`
pickers. Browser review at the same desktop viewport showed the date picker
could still appear visually offset, leaving one remaining filter-control
alignment regression.

Purpose:

Apply the same controlled floating-menu behavior to page-level filter date
inputs without changing the stored date value or existing filter behavior.

Requirements:

- Enhance only `.page-filter-region input[type="date"]` controls.
- Keep the original date input in place so existing `val(...)`, inline
  `onchange`, and filter logic still read the same value.
- Render the visible date picker as a button plus fixed-position in-page date
  menu appended to the document body.
- Selecting or clearing a date updates the original input value and dispatches
  the same `change` event used by existing filters.
- Programmatic reset paths such as `clearRunFilters()` synchronize the visible
  date button text.
- When the date menu is wider than its trigger control, center the menu on the
  trigger by default and clamp inward only enough to keep it inside the
  viewport.
- Ordinary form or configuration date inputs remain native unless a later
  accepted requirement changes them.

Scope boundary:

- Frontend-only regression fix linked to CR-056.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not replace all date inputs in edit/configuration forms.
- Do not change date filter semantics or add a new date-range model.
- Do not redesign the Task Center table or grouping.

Related tasks:

- CR-058 Filter Date Picker Alignment Regression Fix in `TASKS.md`
- CR-056 Filter Dropdown Alignment Regression Fix in `TASKS.md`

Acceptance:

- Task Center date filter menus stay aligned with their trigger control at the
  desktop browser viewport used during review.
- Task Center date filter menus remain visually anchored to the trigger when
  the menu is wider than the input/button.
- Selecting a date updates the underlying date input and existing filter logic.
- Clearing a date resets both the underlying input and visible date label.
- Non-filter date inputs remain native.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, docs check, and browser coordinate inspection of the local `/monitor`
  Task Center date filter. At `1398x874` effective content viewport, the date
  menu used `position: fixed`, opened with a 4px top gap, stayed within the
  viewport, and date select/clear synchronized the original input and visible
  label.
- Follow-up verification on 2026-06-18 covered both `开始日期` and `结束日期`
  triggers: when the 280px menu is wider than the 173px trigger, the menu
  centers on the trigger by default; near the right viewport edge it clamps
  inward just enough to stay visible.

## CR-059 - Filter Date Picker Edge Anchoring Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-058.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-058 replaced page-level filter date inputs with a fixed-position in-page
menu and then centered the wider date menu on the clicked trigger. Browser
review still found the date dropdown could visually read as offset when the
menu was wider than the date button, especially around the Task Center
start/end date controls at the desktop review viewport.

Purpose:

Keep date filter menus visually attached to the control the user clicked by
using trigger-edge anchoring, while preserving the original hidden date input,
value, change event, selection, clearing, and viewport safety behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Use fixed positioning and append the menu outside table and page scroll
  containers.
- When space allows, align the date menu's left edge with the clicked trigger's
  left edge.
- Near the right viewport edge, align the menu's right edge with the clicked
  trigger's right edge if that prevents overflow.
- Clamp only as a final safety fallback when neither trigger edge can fit
  cleanly inside the viewport.
- Preserve date selection, clear/reset synchronization, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not redesign Task Center filters.
- Do not add a new date-range component or external dependency.
- Do not replace non-filter date inputs.

Related tasks:

- CR-059 Filter Date Picker Edge Anchoring Regression Fix in `TASKS.md`
- CR-058 Filter Date Picker Alignment Regression Fix in `TASKS.md`

Acceptance:

- `开始日期` opens with the menu left edge aligned to the trigger left edge
  when space allows.
- `结束日期` near the right side opens with the menu right edge aligned to the
  trigger right edge when needed to avoid overflow.
- Both menus remain inside the viewport and keep the small top gap below the
  trigger unless they must open upward.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, docs check, and browser coordinate inspection of the local `/monitor`
  Task Center date filters at the desktop review viewport.
- `开始日期` opened with the menu left edge aligned to the trigger left edge
  within about `0.36px`.
- `结束日期` opened with the menu right edge aligned to the trigger right edge
  within about `0.42px`.
- Both menus stayed inside the viewport with about a `4px` top gap, and date
  select/clear synchronized the original input and visible label.

## CR-060 - Filter Date Picker Compact Center Alignment Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-059.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-059 proved that the date menu could be mathematically edge-aligned to the
clicked trigger, but browser review still found the menu visually misaligned.
The reason was that the date menu kept a 280px minimum width while the date
filter button was about 173px wide; edge anchoring made the calendar extend far
to one side and still look detached from the control.

Purpose:

Make page-level date filter menus feel visually attached to their trigger by
using a compact calendar width and trigger-center alignment, while preserving
the original hidden date input, value, change event, selection, clearing, and
viewport safety behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Keep fixed positioning and append the menu outside table and page scroll
  containers.
- Use a compact calendar width close to the date trigger instead of forcing a
  large 280px minimum when the trigger is narrow.
- Align the date menu center line to the clicked trigger center line when
  space allows.
- Clamp only as a final safety fallback to keep the menu inside the viewport.
- Preserve date selection, clear/reset synchronization, original `change`
  events, and ordinary form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 and CR-059.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not redesign Task Center filters.
- Do not add a new date-range component or external dependency.
- Do not replace non-filter date inputs.

Related tasks:

- CR-060 Filter Date Picker Compact Center Alignment Regression Fix in
  `TASKS.md`
- CR-059 Filter Date Picker Edge Anchoring Regression Fix in `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` open with the menu center aligned to the trigger
  center within browser sub-pixel tolerance at the desktop review viewport.
- The date menu is compact enough that it does not visibly drift far beyond the
  date trigger on either side.
- Both menus remain inside the viewport and keep the small top gap below the
  trigger unless they must open upward.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, docs check, and browser coordinate inspection of the local `/monitor`
  Task Center date filters at the desktop review viewport.
- `开始日期` opened with the menu center aligned to the trigger center within
  about `0.13px`; the menu width was about `232px` instead of `280px`.
- `结束日期` opened with the menu center aligned to the trigger center within
  about `0.10px`; the menu stayed inside the viewport.
- Both menus kept about a `4px` top gap and preserved the original date input
  behavior.

## CR-061 - Filter Date Picker Trigger-Width Anchoring Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-060.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-060 proved that the date menu could be centered to the trigger within
sub-pixel tolerance, but browser review still found the picker visually
misaligned. The remaining issue was visual rather than mathematical: even a
compact centered menu was still wider than the date trigger, so it extended on
both sides and looked detached from the filter box.

Purpose:

Make page-level date filter menus behave like ordinary dropdowns by matching
the visible date trigger width and aligning the menu left edge to the trigger
left edge, while preserving the original hidden date input, value, change
event, selection, clearing, and viewport safety behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Keep fixed positioning and append the menu outside table and page scroll
  containers.
- Use the clicked trigger's visual width for the date menu when viewport space
  allows, with only a small minimum fallback for extremely narrow controls.
- Align the date menu left edge to the clicked trigger left edge so the menu
  reads as attached to the filter box.
- Compact the calendar internals enough that the month grid remains readable
  inside the trigger-width menu.
- Clamp only as a final safety fallback to keep the menu inside the viewport.
- Preserve date selection, clear/reset synchronization, original `change`
  events, and ordinary form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-060.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not redesign Task Center filters.
- Do not add a new date-range component or external dependency.
- Do not replace non-filter date inputs.

Related tasks:

- CR-061 Filter Date Picker Trigger-Width Anchoring Regression Fix in
  `TASKS.md`
- CR-060 Filter Date Picker Compact Center Alignment Regression Fix in
  `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` open with the menu width matching the trigger width
  within browser sub-pixel tolerance at the desktop review viewport.
- The menu left and right edges align to the trigger edges within browser
  sub-pixel tolerance when viewport clamping is not needed.
- Both menus remain inside the viewport and keep the small top gap below the
  trigger unless they must open upward.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, and browser coordinate inspection of the local `/monitor` Task Center
  date filters at the desktop review viewport.
- `开始日期` opened with the menu width matching the trigger within about
  `0.03px`; left and right edges aligned within about `0.40px`.
- `结束日期` opened with the menu width matching the trigger within about
  `0.03px`; left and right edges aligned within about `0.43px`.
- Both menus stayed inside the viewport, kept about a `4px` top gap, and
  preserved the original date input behavior.

## CR-062 - Filter Date Picker Grid Compression Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-061.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-061 made the date picker menu width match the trigger and fixed the outer
alignment, but browser review found the calendar could still look wrong because
the internal date cells inherited browser button padding and auto minimum
width. At narrow trigger-width menus, the last date columns could be visually
compressed or clipped even when the menu shell itself was aligned.

Purpose:

Keep the trigger-width anchored date picker while making the seven-column
calendar grid readable and non-clipped.

Requirements:

- Keep CR-061's trigger-width menu and left-edge anchoring behavior.
- Reset date-cell minimum width and padding so seven day columns share the
  available grid width instead of overflowing their cells.
- Keep weekdays, day cells, selected-day state, today state, quick actions, date
  selection, clearing, and original date input `change` semantics unchanged.
- Ordinary form/configuration date inputs remain native.

Scope boundary:

- Frontend-only CSS regression fix linked to CR-061.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, or system-setting changes.

Non-goals:

- Do not redesign Task Center filters.
- Do not widen the date menu into a detached calendar surface.
- Do not replace non-filter date inputs.

Related tasks:

- CR-062 Filter Date Picker Grid Compression Regression Fix in `TASKS.md`
- CR-061 Filter Date Picker Trigger-Width Anchoring Regression Fix in
  `TASKS.md`

Acceptance:

- Task Center date filter menus still align to the clicked trigger's left edge
  and match the trigger width within browser sub-pixel tolerance.
- Weekday and day grids show all seven columns without clipped day numbers at
  the desktop review viewport.
- Date cells do not horizontally overflow their grid cells.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with targeted frontend regression tests and browser
  inspection of the local `/monitor` Task Center date filters.
- `结束日期` opened with menu width matching the trigger within about `0.03px`,
  left/right edge deltas within about `0.43px`, no overflowing date cells, and
  all seven day columns visible.

## CR-063 - Filter Date Picker Readable Anchored Popover Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-062.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-061 and CR-062 made the date picker shell align to the trigger and prevented
day-cell overflow, but browser review still found the date dropdown visually
wrong. The remaining issue was UX-level readability: forcing a seven-column
calendar into the narrow trigger width made the menu feel cramped and could
still read as visually offset even when coordinates were correct.

Purpose:

Keep the date menu visibly attached to the clicked filter while giving the
calendar enough width to read like a normal date picker.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Use a readable compact calendar width instead of forcing narrow desktop
  date triggers to be the menu width.
- Use a top anchor marker aligned to the clicked trigger center so the menu
  still reads as attached to the trigger.
- When the menu would overflow the viewport, align the right edge to the
  trigger right edge or clamp within the viewport.
- Preserve the original hidden date input, value, `change` event, date
  selection, clearing, reset synchronization, weekday/day grid, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-062.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not replace non-filter date inputs.
- Do not add a new external date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.

Related tasks:

- CR-063 Filter Date Picker Readable Anchored Popover Regression Fix in
  `TASKS.md`
- CR-062 Filter Date Picker Grid Compression Regression Fix in `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` open as readable calendar menus rather than cramped
  trigger-width calendars.
- The menu remains visually anchored to the clicked date filter through the
  top anchor marker and edge/viewport positioning.
- The menu stays within the viewport at desktop, tablet, and mobile widths.
- Weekday/day grids show all seven columns without clipped day numbers.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, inline script parse check, docs check, and browser inspection of the
  local `/monitor` Task Center date filters.
- At the desktop review viewport, `开始日期` opened at about `236px` wide with
  its left edge aligned to the trigger and no overflowing day cells; `结束日期`
  opened at about `236px` wide with its right edge aligned to the trigger and
  no overflowing day cells.
- Tablet `1024x768` and mobile `390x844` viewport checks kept the menu inside
  the viewport, with zero overflowing date cells and no page horizontal
  overflow.

## CR-064 - Filter Date Picker Trigger-Attached Edge Shrink Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-063.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-063 made the date menu readable and anchored, but browser review still found
the right-side `结束日期` dropdown visually offset. The root cause was that the
fixed-position menu used the content/visual viewport for edge safety, so the
right-side date control was treated as too close to the scrollbar. The menu
then right-aligned to the trigger, which stayed in bounds but made the calendar
look detached from the clicked field.

Purpose:

Keep readable page-filter date menus visually attached to the clicked date
filter even near the right edge. When the menu is only slightly wider than the
remaining space, reduce its width within a readable lower bound and keep its
left edge attached to the trigger before falling back to right alignment.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Prefer aligning the menu left edge to the clicked trigger's left edge.
- Use the visual viewport width for fixed-position edge checks.
- Near the right edge, slightly shrink the readable menu when doing so keeps
  the menu attached and all seven date columns readable.
- Use right-edge alignment or viewport clamping only when the attached width
  would become too narrow.
- Preserve the top anchor marker, original hidden date input, value,
  `change` event, date selection, clearing, reset synchronization, weekday/day
  grid, and ordinary form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-063.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not add a new date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.
- Do not replace non-filter date inputs.

Related tasks:

- CR-064 Filter Date Picker Trigger-Attached Edge Shrink Regression Fix in
  `TASKS.md`
- CR-063 Filter Date Picker Readable Anchored Popover Regression Fix in
  `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` menus read as attached to their own clicked field at
  desktop, tablet, and mobile widths.
- Right-side date menus may shrink within the readable lower bound instead of
  drifting left through premature right alignment.
- The menu stays inside the visual viewport with no horizontal page overflow.
- Weekday/day grids show all seven columns without clipped day numbers.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with syntax checks, targeted frontend regression
  tests, inline script parse check, docs check, and browser coordinate
  inspection of the local `/monitor` Task Center date filters.
- Desktop effective viewport `1383x874`: `开始日期` left edge aligned to the
  trigger within about `0.4px`; `结束日期` left edge aligned within about
  `0.4px` after shrinking to about `221px`; both menus had zero overflowing
  date cells and no visual-viewport overflow.
- Tablet effective viewport `980x746`: `结束日期` left edge aligned within
  about `0.4px` after shrinking to about `198px`, with zero overflowing date
  cells and no visual-viewport overflow.
- Mobile effective viewport `364x819`: both date menus used the mobile trigger
  width, stayed attached to the field, and had zero overflowing date cells.

## CR-065 - Filter Date Picker Center-Anchored Visual Alignment Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-064.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-064 kept the right-side date menu inside the visual viewport and attached
its left edge to the `结束日期` trigger, but browser review at `1440x900` still
found the dropdown visually offset because the readable calendar remained wider
than the trigger and extended noticeably to the right.

Purpose:

Make page-level date filter menus read as naturally attached to their clicked
field by aligning the menu's visual center to the trigger center, while keeping
the readable compact calendar, top anchor marker, viewport safety, and existing
date-filter behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Use the visual viewport width for fixed-position date-menu edge checks.
- Use a compact readable calendar width, but position it from the clicked
  trigger center rather than from the trigger left or right edge.
- Clamp inward only when center alignment would overflow the visual viewport.
- Keep the top anchor marker aligned to the clicked trigger center after any
  viewport clamp.
- Preserve the original hidden date input, value, `change` event, date
  selection, clearing, reset synchronization, weekday/day grid, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-064.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not add a new date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.
- Do not replace non-filter date inputs.

Related tasks:

- CR-065 Filter Date Picker Center-Anchored Visual Alignment Regression Fix in
  `TASKS.md`
- CR-064 Filter Date Picker Trigger-Attached Edge Shrink Regression Fix in
  `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` menus align their center line to the clicked trigger
  center when the menu can fit inside the visual viewport.
- Near the viewport edge, the menu clamps inward without losing the visible top
  anchor marker connection to the clicked trigger.
- The menu stays inside the visual viewport with no horizontal page overflow.
- Weekday/day grids show all seven columns without clipped day numbers.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, inline script parse check, docs check, and browser coordinate
  inspection of the local `/monitor` Task Center date filters.
- Desktop effective viewport `1383x874`: `结束日期` opened at about `236px`
  wide, center-aligned to the trigger within about `0.1px`, stayed inside the
  visual viewport, and had zero overflowing date cells.

## CR-066 - Filter Date Picker Trigger-Attached Dropdown Alignment Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-065.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-065 made the date menu mathematically centered on the clicked field, but
browser review at `1440x900` still read the wider calendar as visually
detached from the filter input because the left edge no longer felt anchored to
the trigger.

Purpose:

Make page-level date filter menus read like a normal attached dropdown by
anchoring the visible menu to the clicked field's left edge when room allows,
while still keeping the readable compact calendar, top anchor marker, viewport
safety, and existing date-filter behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Use the visual viewport width for fixed-position date-menu edge checks.
- Use a compact readable calendar width, but position the menu from the clicked
  trigger's left edge when the viewport can accommodate it.
- If the menu would overflow the visual viewport on the right, shrink the
  width first before falling back to clamping.
- Keep the top anchor marker aligned to the clicked trigger center after any
  width adjustment or viewport clamp.
- Preserve the original hidden date input, value, `change` event, date
  selection, clearing, reset synchronization, weekday/day grid, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-065.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not add a new date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.
- Do not replace non-filter date inputs.

Related tasks:

- CR-066 Filter Date Picker Trigger-Attached Dropdown Alignment Regression Fix
  in `TASKS.md`
- CR-065 Filter Date Picker Center-Anchored Visual Alignment Regression Fix in
  `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` menus align their left edge to the clicked trigger
  when the viewport can accommodate the readable width.
- Near the viewport edge, the menu shrinks within a readable lower bound before
  clamping inward.
- The menu stays inside the visual viewport with no horizontal page overflow.
- Weekday/day grids show all seven columns without clipped day numbers.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, inline script parse check, docs check, and browser coordinate
  inspection of the local `/monitor` Task Center date filters.
- Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus opened
  at about `236px` wide and aligned their left edge to the clicked trigger
  within about `0.4px`, while staying inside the visual viewport with zero
  overflowing date cells.

## CR-067 - Filter Date Picker Trigger-Width Visual Attachment Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-066.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-066 attached the date menu's left edge to the clicked trigger, but browser
review at the desktop review viewport still found the right-side `结束日期`
dropdown visually offset. The remaining issue was that the menu could still be
noticeably wider than the date trigger, so even correct left-edge alignment
looked like a detached calendar block.

Purpose:

Make page-level date filter menus read as ordinary attached dropdowns by
matching the clicked trigger width whenever that width is usable, while keeping
the fixed-position portal menu, trigger-center anchor marker, viewport safety,
and existing date-filter behavior.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Use the visual viewport width for fixed-position date-menu edge checks.
- Match the visible date menu width to the clicked trigger width whenever the
  trigger is wide enough for the seven-column grid.
- Use a small minimum readable width only for unusually narrow trigger fields.
- Clamp or shrink only when the attached menu would overflow the visual
  viewport.
- Keep the top anchor marker aligned to the clicked trigger center after any
  width adjustment or viewport clamp.
- Preserve the original hidden date input, value, `change` event, date
  selection, clearing, reset synchronization, weekday/day grid, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-066.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not add a new date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.
- Do not replace non-filter date inputs.

Related tasks:

- CR-067 Filter Date Picker Trigger-Width Visual Attachment Regression Fix in
  `TASKS.md`
- CR-066 Filter Date Picker Trigger-Attached Dropdown Alignment Regression Fix
  in `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` menus match the clicked trigger width within browser
  sub-pixel tolerance when the trigger is wide enough.
- The menu left edge aligns to the clicked trigger left edge within browser
  sub-pixel tolerance.
- The top anchor marker remains tied to the clicked trigger center.
- The menu stays inside the visual viewport with no horizontal page overflow.
- Weekday/day grids show all seven columns without clipped day numbers.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, inline script parse check, docs check, and browser coordinate
  inspection of the local `/monitor` Task Center date filters.
- Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus matched
  the trigger width within about `0.04px`, aligned left edges within about
  `0.4px`, kept the top anchor marker aligned to the trigger center within
  about `0.12px`, stayed inside the visual viewport, and had zero overflowing
  date cells.

## CR-068 - Filter Date Picker Local Attached Menu Regression Fix

Date: 2026-06-18

Source: user in-app browser review of the Task Center date filter picker after
CR-067.

Module: formal console global filter date controls

Type: Regression Fix

Status: Verified

Background:

CR-067 made the date menu mathematically match the clicked trigger width and
left edge, but browser review at `1440x900` still found the date dropdown
visually offset. The remaining weakness was that the date menu still used a
document-body fixed-position portal and viewport math, so the control could be
coordinate-correct while still reading as detached from the field.

Purpose:

Make page-level date filter menus behave like ordinary attached dropdowns by
mounting the active date menu inside the clicked date control wrapper and
positioning it from that wrapper rather than from page-level viewport
coordinates.

Requirements:

- Keep the CR-058 custom date menu scoped only to `.page-filter-region
  input[type="date"]`.
- Move the active date menu into the clicked `.filter-date-enhanced` wrapper
  before positioning.
- Use wrapper-local absolute positioning with `left: 0` and `top: calc(100% +
  4px)` so the menu opens directly under the clicked field.
- Keep the visible menu width equal to the clicked trigger width.
- Keep the top anchor marker centered within the attached menu.
- Preserve the original hidden date input, value, `change` event, date
  selection, clearing, reset synchronization, weekday/day grid, and ordinary
  form/configuration date input behavior.

Scope boundary:

- Frontend-only regression fix linked to CR-058 through CR-067.
- No backend API, database, run lifecycle, AI trace, report, email, permission,
  scheduler, deployment, or system-setting changes.

Non-goals:

- Do not add a new date-picker dependency.
- Do not redesign the Task Center filter toolbar or field set.
- Do not replace non-filter date inputs.

Related tasks:

- CR-068 Filter Date Picker Local Attached Menu Regression Fix in `TASKS.md`
- CR-067 Filter Date Picker Trigger-Width Visual Attachment Regression Fix in
  `TASKS.md`

Acceptance:

- `开始日期` and `结束日期` menus are children of their clicked
  `.filter-date-enhanced` wrapper while open.
- The menu uses wrapper-local `position: absolute`, `left: 0`, and
  `top: calc(100% + 4px)` rather than document-body fixed-position viewport
  coordinates.
- The menu left edge aligns to the clicked field and the visible gap below the
  field is stable at the desktop review viewport.
- The menu width matches the clicked trigger width within browser sub-pixel
  tolerance.
- Selecting and clearing dates still update the underlying original input and
  existing filter behavior.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, inline script parse check, docs check, and browser coordinate
  inspection of the local `/monitor` Task Center date filters.
- Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus were
  mounted inside their clicked date wrappers, used `position: absolute`, had
  left-edge delta `0px`, top gap about `4px`, and width delta about `0.03px`.

## CR-069 - Run Detail AI Evaluation Lead Entry Consolidation

Date: 2026-06-18

Source: user in-app browser acceptance of Task Center / Run Detail.

Module: Task Center, Run Detail, report leads, AI evaluation traceability

Type: Existing Feature Optimization

Status: Verified

Background:

After CR-051 consolidated Run Center and Report Center into Task Center, Run
Detail became the main lifecycle surface with `AI 评估`, `报告`, and
`邮件交付` sections. Manual acceptance found that the report `查看线索` drawer
and the Run Detail `AI 评估` list carried very similar content, creating a
duplicated drilldown path.

Purpose:

Make Run Detail's `AI 评估` section the single primary lead/evaluation detail
surface. Report lead inspection becomes a filtered AI-evaluation view rather
than a second table or drawer.

Requirements:

- Add a report-scope filter to the Run Detail AI evaluation list.
- Keep existing AI evaluation filters for status, risk, platform, keyword, and
  title.
- From a report row, `查看线索` should switch to Run Detail's `AI 评估` tab and
  apply the selected report filter instead of opening a separate lead drawer.
- Remove the standalone report-lead drawer/table from the current UI surface.
- Keep report preview, downloads, delivery history, and resend actions inside
  Run Detail's `报告` and `邮件交付` areas.
- Preserve normal-user owner scope, administrator redacted debug scope,
  limited-context old evaluations, and sensitive-field redaction.

Scope boundary:

- Frontend information architecture plus the minimal Run Detail API
  `report_id` filter needed for the unified AI Evaluation view.
- No data-model, report-generation, AI-classification, trace-retention, email,
  crawler, scheduler, deployment, or permission-model change.

Non-goals:

- Do not introduce a standalone global lead workbench.
- Do not recreate the old top-level Report Center.
- Do not rewrite CR-048/CR-051 historical verification.
- Do not repair or backfill old report/evaluation data.

Related tasks:

- CR-069 Run Detail AI Evaluation Lead Entry Consolidation in `TASKS.md`
- CR-034 Run Detail And AI Evaluation Traceability in `TRACEABILITY.md`
- CR-051 Task Center And Report Grouping Consolidation in `TRACEABILITY.md`

Acceptance:

- Run Detail `AI 评估` shows the current run's AI candidates by default.
- Report `查看线索` opens the same AI Evaluation tab with `report_id` filter
  applied and a visible report scope.
- AI Evaluation filters support report, status, risk, platform, keyword, and
  title.
- The report filter is rendered as a selectable `报告范围` control only when the
  selected run has multiple reports; runs with zero or one report show a
  read-only scope note instead.
- The current UI no longer renders the duplicate report-lead drawer/table.
- Existing report preview, downloads, delivery history, resend, AI trace
  detail, limited-context rows, and role-safe redaction remain available.

Verification:

- Verified on 2026-06-18 with targeted Phase 20 / CR-048 / CR-051 regression
  coverage, the full `tests/test_monitoring_mvp.py` suite, syntax checks,
  inline monitor script parse, docs consistency, and administrator browser
  inspection of local `/monitor`.
- Browser inspection confirmed Run Detail `AI 评估` uses the same enhanced
  page-filter dropdown treatment as first-level Task Center filters, and a run
  with no generated report shows `报告范围` as a read-only scope note rather than
  a dropdown.

## CR-071 - Drawer And Modal Select Dropdown Consistency

Date: 2026-06-19

Source: user in-app browser review of dropdown consistency inside secondary
drawers and modals.

Module: formal console secondary drawers/modals, select dropdown interaction

Type: Existing Feature Optimization

Status: Verified

Background:

CR-056 introduced the enhanced `.page-filter-region select` dropdown mechanism
for page-level filter bars after native browser dropdowns appeared misaligned
inside the console shell. Later browser review found that several secondary
drawers and modals still used native select dropdowns, so the same console
could show two visibly different dropdown interaction patterns.

Purpose:

Reuse the existing Task Center filter dropdown mechanism for accepted
drawer/modal select fields without introducing a second custom select
component or changing the underlying form values, change events, save behavior,
permissions, or data model.

Requirements:

- In the following secondary surfaces, select fields should opt into the
  existing `.page-filter-region select` enhancement and render through
  `.filter-select-enhanced`, `.filter-select-button`,
  `.filter-select-menu`, and `.filter-select-option.is-selected`:
  - Monitoring task edit drawer;
  - Platform account detail drawer;
  - Proxy edit drawer;
  - AI Access edit drawer;
  - AI Evaluation Rule edit modal;
  - Mail Configuration edit drawer;
  - Mail Template edit drawer.
- The AI Access `模型名称` combobox must keep its existing free-text/model-list
  interaction and must not be converted to the filter dropdown mechanism.
- Task edit drawer custom date inputs must remain ordinary form date inputs;
  CR-068's enhanced date menu remains limited to intentionally marked
  `.page-filter-region` date inputs.
- Dynamic option refreshes for account, proxy, AI profile, and email template
  selects must keep the visible enhanced button label synchronized with the
  underlying select value and disabled state.
- Drawer/modal opt-in regions should not inherit the heavy page-filter panel
  background or border; only the select dropdown interaction should be shared.

Scope boundary:

- Frontend-only interaction consistency for the listed secondary surfaces.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, account environment, report, or trace behavior changes.

Non-goals:

- Do not introduce a new select component.
- Do not enhance every form/configuration select globally.
- Do not change AI Access model-name search/list behavior.
- Do not change date-picker behavior beyond preserving the existing CR-068
  boundaries.

Related tasks:

- CR-071 Drawer And Modal Select Dropdown Consistency in `TASKS.md`
- CR-056 Filter Dropdown Alignment Regression Fix in `TRACEABILITY.md`
- CR-068 Filter Date Picker Local Attached Menu Regression Fix in
  `TRACEABILITY.md`

Acceptance:

- The listed drawer/modal selects render with the same enhanced dropdown
  classes and menu behavior as Task Center filters.
- The original select values and `change` semantics remain intact.
- Dynamic option refreshes update the visible enhanced button labels.
- AI Access `模型名称` remains the existing combobox and is not enhanced.
- Task edit custom date inputs remain native form date inputs.
- Existing Task Center, Run Detail AI Evaluation, and CR-056/CR-068 dropdown
  behavior remains unchanged.

Verification:

- Verified on 2026-06-19 with targeted frontend static regression tests,
  syntax checks, inline monitor script parse, docs consistency check, and
  local browser inspection of representative drawer/modal selects.

## CR-072 - Task Edit Custom Date Picker Consistency

Date: 2026-06-19

Source: user in-app browser review of Monitoring -> More -> Edit Task custom
date controls.

Module: Monitoring task edit drawer, custom crawl date controls

Type: Existing Feature Optimization

Status: Verified

Background:

CR-071 intentionally kept task edit custom start/end date fields native while
only unifying drawer/modal select controls. The user later clarified that, for
the Monitoring task edit drawer, `自定义开始日期` and `自定义结束日期` should use
the same local attached calendar interaction as Task Center's page-level
`开始日期 / 结束日期` date filters.

Purpose:

Make the two task edit custom date fields visually and behaviorally consistent
with the existing `.page-filter-region input[type="date"]` enhancement while
preserving the underlying task form date values, save payload, and change
semantics.

Requirements:

- In the Monitoring task edit drawer, `custom_start` and `custom_end` must opt
  into the existing date enhancement and render through
  `.filter-date-enhanced`, `.filter-select-button.filter-date-button`, and
  `.filter-date-menu`.
- The visible trigger should match the Task Center date-filter select-style
  button.
- Clicking the trigger should open the calendar menu directly under that
  button, mounted inside the clicked wrapper rather than using the browser
  native date picker.
- The menu must include month title, previous/next month controls, weekday row,
  date grid, `今天`, and `清空`.
- The menu width must match the trigger and stay locally attached without
  drifting or floating away.
- The original hidden date input must keep the stored value and dispatch the
  same `change` behavior when a date is selected or cleared.

Scope boundary:

- Frontend-only interaction consistency for the Monitoring task edit drawer's
  two custom crawl date fields.
- This is a focused exception to CR-071's original native-date boundary.
- No backend API, database schema, task-save payload, scheduler, crawler, AI,
  report, email, permission, deployment, or system-setting change.

Non-goals:

- Do not convert every ordinary edit/configuration date field globally.
- Do not add a new date-picker dependency.
- Do not change Task Center, Run Detail AI Evaluation, or CR-068 date filter
  behavior beyond reusing the existing mechanism.

Related tasks:

- CR-072 Task Edit Custom Date Picker Consistency in `TASKS.md`
- CR-068 Filter Date Picker Local Attached Menu Regression Fix in
  `TRACEABILITY.md`
- CR-071 Drawer And Modal Select Dropdown Consistency in `TRACEABILITY.md`

Acceptance:

- `custom_start` and `custom_end` sit inside an explicit
  `.page-filter-region.modal-filter-region` opt-in scope.
- Both fields are enhanced into `.filter-date-enhanced` wrappers with
  `.filter-select-button.filter-date-button` triggers.
- Opening either date control shows the existing `.filter-date-menu` locally
  attached below the clicked trigger, with one selected-day state when a value
  exists.
- Selecting `今天`, selecting a date, or clearing updates the original input
  value and dispatches the existing `change` event.
- AI Access `模型名称`, drawer/modal selects, and unrelated form fields keep
  their current behavior.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, syntax
  checks, inline monitor script parse, docs consistency check, and local
  browser inspection of task edit custom date controls.

## CR-073 - Scrollable Drawer Corner Radius Regression Fix

Date: 2026-06-19

Source: user in-app browser review of scrollable secondary drawers/modals.

Module: formal console secondary drawers/modals, scrollable drawer chrome

Type: Regression Fix

Status: Verified

Background:

After the shared sticky drawer header and drawer/modal select/date consistency
work, browser review found that secondary drawers with vertical scrollbars can
visually lose the top-right radius because the scrollbar track paints into the
rounded corner. Moving the close button inward would preserve reachability but
would make the drawer chrome feel off-center and is not accepted.

Purpose:

Preserve the shared drawer/modal top-right rounded corner when content is
scrollable, while keeping the close button in the top-right header position and
without changing drawer information architecture or business behavior.

Requirements:

- Scrollable drawers/modals must keep a rounded top-right corner even when a
  vertical scrollbar is present.
- The outer drawer shell must not be the vertical scroll container; content
  after `.drawer-head` / `.modal-head` should scroll inside a shared
  `.drawer-scroll-body` so the scrollbar starts below the header area.
- The close button must remain in the top-right header position and stay
  reachable while content scrolls.
- The fix should apply through shared drawer/modal chrome styles so task edit,
  run detail, account detail, AI rule, mail configuration, mail template, run
  log, report preview, and delivery-history surfaces stay consistent.
- The fix must preserve CR-038 sticky close behavior and CR-071/CR-072
  drawer/modal dropdown/date interactions.

Scope boundary:

- Frontend-only visual regression fix for existing secondary drawers/modals.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, report, or trace behavior changes.

Non-goals:

- Do not redesign drawer layout or move the close button away from the
  top-right header position.
- Do not introduce a new drawer component, framework, or dependency.
- Do not change Task Center, Run Detail, report, email, AI trace, or
  permission semantics.

Related tasks:

- CR-073 Scrollable Drawer Corner Radius Regression Fix in `TASKS.md`
- CR-038 Sticky Close Controls For Scrollable Drawers in `TRACEABILITY.md`
- CR-071 Drawer And Modal Select Dropdown Consistency in `TRACEABILITY.md`
- CR-072 Task Edit Custom Date Picker Consistency in `TRACEABILITY.md`

Acceptance:

- A scrollable shared drawer keeps the top-right rounded corner visually intact
  with the scrollbar visible.
- The scrollbar track/thumb must not start at the drawer's absolute top edge;
  it should belong to `.drawer-scroll-body` below the header so it reads like a
  content scrollbar, not a full-height outer-frame scrollbar.
- The close button remains at the top-right and is not moved toward the center.
- Sticky header, close handlers, backdrop/Escape closing, enhanced select
  menus, and task edit custom date menus keep their accepted behavior.
- Static regression coverage verifies the shared inner-scroll structure,
  scrollbar/radius styling, and representative drawer surfaces.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, syntax
  checks, inline monitor script parse, docs consistency check, and local
  browser inspection of a long Monitoring task drawer.

## CR-074 - Console Refresh Action Deduplication And Icon Loading

Date: 2026-06-19

Source: user in-app browser review of duplicate refresh buttons across console
pages.

Module: formal console page headers, Task Center, resource pages, secondary
refresh actions

Type: Existing Feature Optimization

Status: Verified

Background:

After Task Center consolidation and the recent drawer/filter refinements, many
formal console pages showed both the shared top-bar refresh control and a
page-local refresh button such as refresh home, refresh accounts, refresh
proxies, refresh AI access, refresh templates, refresh runtime strategy, or
refresh Task Center. These controls mostly reloaded the same current page data,
creating visual noise and making the page header feel like it had two equal
refresh actions.

Purpose:

Make refresh behavior easier to scan by keeping one page-level current-page
refresh control and rendering refresh affordances as a refresh icon with a
loading spin state instead of visible Chinese button text.

Requirements:

- The top bar must provide the single page-level refresh entry for the active
  first-level page.
- Page-local refresh buttons that only duplicate the current page load should
  be removed from Overview, Platform Accounts, Proxy Resources, AI Access, AI
  Evaluation Rules, Mail Configuration, Mail Templates, Runtime Strategy, and
  Task Center.
- Page filter toolbars must not repeat another generic refresh button when the
  top-bar current-page refresh already reloads that same list.
- Refresh controls must render as icon-only SVG buttons without visible
  Chinese refresh labels.
- While a refresh is running, the refresh icon must show a loading/spinning
  state and the clicked button must be disabled until the associated refresh
  work finishes.
- Semantically different scoped actions may remain, but must use the same
  icon-only refresh treatment when they are refresh actions:
  schedule-time recomputation, delivery-history refresh, email-template
  preview refresh, run-log refresh, and run-detail refresh.
- The Monitoring page's schedule-time recomputation remains because it calls
  a mutation endpoint and is not the same as reloading the Monitoring list.
- System Diagnostics `重新诊断` and `运行系统诊断` remain diagnostic actions
  rather than generic page refresh duplicates.

Scope boundary:

- Frontend-only information-density and interaction-feedback optimization.
- No backend API, database schema, permission, crawler, scheduler, AI provider,
  SMTP, report, run lifecycle, or deployment behavior changes.

Non-goals:

- Do not remove scoped refresh actions that operate on a drawer, log,
  preview, delivery history, or run detail.
- Do not rename or redesign non-refresh diagnostic actions.
- Do not introduce a new icon library, frontend framework, or build step.

Related tasks:

- CR-074 Console Refresh Action Deduplication And Icon Loading in `TASKS.md`
- CR-053 Task Center Field Priority And Global Select Alignment in
  `TRACEABILITY.md`
- CR-073 Scrollable Drawer Corner Radius Regression Fix in `TRACEABILITY.md`

Acceptance:

- The visible first-level console has one page-level current-page refresh icon
  in the top bar.
- Redundant page-header and filter-toolbar refresh buttons for the same page
  are absent.
- The refresh icon spins while the refresh promise is pending and restores when
  the work completes.
- Icon-only refresh buttons keep accessible labels/tooltips for current page
  refresh and scoped refresh actions.
- Task Center grouping, filters, Run Detail, report preview, log refresh,
  delivery-history refresh, template preview, and diagnostics remain reachable.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, inline
  monitor script parse, docs consistency check, and local browser inspection.
  Browser verification confirmed the current-page refresh is icon-only, no
  visible button text starts with `刷新`, six scoped refresh icon buttons remain
  where they refresh different local scopes, and the top-bar refresh button
  enters disabled/loading state before restoring.

## CR-075 - Responsive Navigation Interaction Consistency

Date: 2026-06-19

Source: user in-app browser review of the top-left `打开导航` button appearing
at a `1169px`-wide viewport.

Module: formal console navigation shell, responsive breakpoints, Phase 21B

Type: Existing Feature Optimization

Status: Verified

Background:

After the focused Phase 21 navigation visual pass, the console still used the
mobile drawer trigger for every viewport below `1280px`. Browser review found
that a `1169px` viewport showed the top-left `打开导航` button even though the
viewport is wide enough for the same sidebar interaction model used elsewhere.
This made navigation feel like two different systems rather than one coherent
responsive shell.

Purpose:

Unify navigation behavior across accepted breakpoints so desktop uses the full
sidebar, tablet/narrow desktop uses the same sidebar as a persistent icon rail,
and only true mobile uses the top-left drawer trigger.

Requirements:

- Desktop `>= 1280px` keeps the expanded sidebar and bottom collapse control.
- Tablet / narrow desktop `768px - 1279px` must keep a persistent side rail,
  default it to the collapsed icon state, and hide the top-left `打开导航`
  trigger and mobile backdrop.
- Mobile `< 768px` keeps the existing touch-safe top-left navigation trigger,
  backdrop, Escape close, and page-selection close behavior.
- Resize and initial-load behavior must synchronize to the active breakpoint:
  close mobile navigation at `>= 768px`, collapse the sidebar by default for
  `768px - 1279px`, and disable sidebar collapse below `768px`.
- Collapsed side-rail hover, active, and tooltip behavior must remain aligned
  with the Phase 21 neutral hover and teal selected-state tokens.

Scope boundary:

- Frontend-only responsive navigation optimization.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date, drawer,
  modal, row menu, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not restore separate top-level Run Center / Report Center.
- Do not add a standalone `reports` top-level page.
- Do not change the Task Center grouping model, `运行记录`, Run Detail tabs,
  overlay close behavior, `.drawer-scroll-body`, enhanced dropdown logic, or
  date-picker value/change semantics.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-040 Formal Console Page-Level UI/UX Refinement in `TRACEABILITY.md`
- Phase 11D Responsive Layout And Mobile Navigation in `TEST_PLAN.md`

Acceptance:

- At `1440x900`, the full sidebar remains visible and can collapse to icons.
- At `1024x768` and similar `1169px`-wide viewports, the top-left `打开导航`
  trigger is absent, the side rail remains visible as icons, and the bottom
  expand/collapse control remains usable.
- At `390x844`, the top-left navigation trigger remains visible and opens the
  mobile drawer; backdrop, Escape, and page-selection close behavior remain.
- Administrator and normal-user menu visibility remains role-safe.
- The single top-level `任务中心`, default task/report grouping, `运行记录`, Run
  Detail six sections, CR-071/CR-072 controls, CR-073 drawer scroll ownership,
  and CR-074 top-bar refresh remain unchanged.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and browser
  verification at desktop, tablet/narrow desktop, and mobile widths.
- Browser verification confirmed `1440x900` keeps the full sidebar without the
  mobile trigger, `1169px`/`1024x768` use the collapsed icon side rail without
  the top-left `打开导航` trigger, and `390x844` keeps a horizontal two-row
  mobile header plus working navigation drawer open/backdrop-close behavior.

## CR-076 - Mobile Header Layout Resilience Regression Fix

Date: 2026-06-19

Source: user in-app browser screenshot showing the mobile `/monitor` header
title squeezed into one-character vertical wrapping.

Module: formal console mobile header, responsive shell, Phase 21B

Type: Regression Fix

Status: Verified

Background:

After CR-075 unified the responsive navigation breakpoints, browser review on a
mobile-width viewport still found a layout state where the top header could
compress the product title into a narrow vertical column. The visible cause was
that the mobile header still let the navigation trigger, title, status chips,
refresh icon, and account control compete for the same first-screen width.

Purpose:

Make the mobile header resilient under the accepted `<768px` drawer-navigation
model so the title remains readable and the status/refresh/account controls do
not squeeze it.

Requirements:

- Mobile `<768px` keeps the top-left navigation trigger and the same drawer
  open, backdrop close, Escape close, and page-selection close behavior.
- The mobile header title must occupy its own full-width row instead of
  sharing the row with status chips, refresh, or account controls.
- Status chips must occupy their own mobile header row and must not force the
  title into one-character wrapping.
- The top-bar refresh icon and compact account control remain visible and
  reachable on mobile.
- Generic mobile `.row` wrapping rules must not stretch the account area or
  status area in a way that breaks the header grid.

Scope boundary:

- Frontend-only regression fix for responsive layout.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date, drawer,
  modal, row menu, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not remove the mobile navigation trigger.
- Do not change mobile drawer close behavior or `.drawer-scroll-body`.
- Do not change Task Center grouping, `运行记录`, Run Detail tabs, enhanced
  dropdown/date logic, or top-bar refresh semantics.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-075 Responsive Navigation Interaction Consistency in `CHANGE_REQUESTS.md`
- Phase 12 Navigation And Page Entry Tests in `TEST_PLAN.md`

Acceptance:

- At `390x844`, `舆情监控运营后台` remains horizontal and readable.
- The mobile header lays out as navigation plus refresh/account controls,
  then title, then status chips.
- No horizontal page overflow is introduced.
- The mobile drawer still opens and closes through the accepted CR-075 paths.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, and local HTTP resource checks.
  Browser attachment was retried during the same pass; if the in-app browser
  session is unavailable, the CSS/test regression remains the authoritative
  automated gate and manual browser refresh should confirm the same layout.

## CR-077 - Mobile Header Final Cascade Resilience Regression Fix

Date: 2026-06-19

Source: user in-app browser screenshot showing the mobile `/monitor` header
still collapsing into vertical one-character title text after the first
CR-076 pass.

Module: formal console mobile header, inline/CSS cascade, Phase 21B

Type: Regression Fix

Status: Verified

Background:

CR-076 added the correct mobile header grid in `monitor.css`, but the formal
page still has multiple inline `<style>` blocks that load after the static CSS.
Browser review found that under the live page cascade, a later mobile inline
rule could still override or weaken the intended final header layout and let
the product title collapse vertically.

Purpose:

Make the accepted CR-076 mobile header rule resilient in the final loaded page
cascade so the browser's computed layout, not only the static CSS file, keeps
navigation, title, status, refresh, and account controls in their expected
mobile grid areas.

Requirements:

- Keep the mobile `<768px` drawer-navigation model from CR-075.
- Keep the CR-076 mobile header layout as the final cascade rule: top row
  navigation / refresh / account, second row title, third row status.
- Ensure the formal page's inline style blocks cannot stretch `.header-actions`
  back into a full-width flex row that squeezes the title.
- Ensure static regression tests inspect all inline `<style>` blocks, not only
  the first one, because the formal page intentionally has more than one style
  block.
- Preserve tablet/narrow desktop icon rail behavior and desktop
  full/collapsible sidebar behavior.

Scope boundary:

- Frontend-only responsive regression fix.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date, drawer,
  modal, row menu, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not remove the mobile navigation trigger.
- Do not change mobile drawer close behavior or `.drawer-scroll-body`.
- Do not change Task Center grouping, `运行记录`, Run Detail tabs, enhanced
  dropdown/date logic, or top-bar refresh semantics.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-076 Mobile Header Layout Resilience Regression Fix in
  `CHANGE_REQUESTS.md`
- Phase 12 Navigation And Page Entry Tests in `TEST_PLAN.md`

Acceptance:

- At mobile width, `舆情监控运营后台` remains horizontal and readable in the
  browser's computed layout.
- Mobile `#top_status` and `.account-area` occupy their intended grid areas.
- Page content, including representative resource pages, has no right-side
  horizontal overflow.
- Mobile drawer open/backdrop/page-selection close behavior remains unchanged.
- Tablet/narrow desktop still hides the top-left mobile trigger and uses the
  persistent icon rail.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and in-app
  browser checks at mobile, tablet, and desktop widths.

## CR-078 - Mobile And Tablet Navigation Layout Resilience Regression Fix

Date: 2026-06-19

Source: user in-app browser screenshot showing the mobile `/monitor` layout
with vertically squeezed header title text and user review of the tablet
collapsed side rail behavior.

Module: formal console responsive shell, mobile resource pages, tablet icon
side rail, Phase 21B

Type: Regression Fix

Status: Verified

Background:

After the CR-075 through CR-077 responsive navigation fixes, browser review
still found mobile states where the loaded page could look like a desktop/tablet
layout at a phone width or could risk squeezing the header title into a narrow
vertical column. A separate tablet check also found a previous risk that the
last collapsed navigation item could enter the bottom collapse button hit area.

Purpose:

Harden the already accepted responsive shell so the same navigation model works
across desktop, tablet, and mobile: desktop keeps a full/collapsible sidebar,
tablet keeps a persistent icon rail, and phone widths keep the drawer trigger
without the title or resource pages becoming visually broken.

Requirements:

- At mobile `<768px`, the header must keep navigation, refresh, account, title,
  and status in the accepted grid rows in the final loaded cascade.
- The product title must remain horizontal and use `keep-all`/nowrap treatment
  instead of one-character vertical wrapping.
- A closed mobile drawer must stay off-canvas and must not reserve visible page
  width.
- Representative resource pages, including `代理资源`, must keep their page
  header, metric cards, filter toolbar, and table container inside the viewport;
  tables may scroll only inside `.table-wrap`.
- At tablet/narrow desktop `768px - 1279px`, the collapsed side rail must keep
  the navigation list in its own scrollable grid row so the final item does not
  overlap the bottom collapse button.

Scope boundary:

- Frontend-only responsive regression fix.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date, drawer,
  modal, row menu, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not remove the mobile navigation trigger.
- Do not change mobile drawer close behavior, backdrop, Escape handling, or
  `.drawer-scroll-body`.
- Do not change Task Center grouping, `运行记录`, Run Detail tabs, enhanced
  dropdown/date logic, top-bar refresh semantics, or role-based menu visibility.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-075 Responsive Navigation Interaction Consistency in `CHANGE_REQUESTS.md`
- CR-076 / CR-077 mobile header resilience fixes in `CHANGE_REQUESTS.md`
- Phase 21 Browser And Responsive Tests in `TEST_PLAN.md`

Acceptance:

- At a real mobile breakpoint (`innerWidth` around `390px`), `舆情监控运营后台`
  remains horizontal and readable.
- Mobile `代理资源` opens through the existing drawer navigation and closes the
  drawer after selection; page width and document scroll width remain equal.
- The closed mobile drawer remains off-canvas with the trigger still visible.
- At `1024x768`, the top-left mobile trigger is hidden, the icon side rail is
  visible, and clicking `系统诊断` activates the System Diagnostics page rather
  than the bottom collapse button.
- At `1440x900`, the full sidebar and user-controlled collapse behavior remain.
- Browser console errors remain absent for the checked `/monitor` interactions.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and in-app browser
  checks at effective mobile, tablet, and desktop breakpoints.
- Browser measurements confirmed mobile `innerWidth≈379`, `matchMobile=true`,
  title `writing-mode: horizontal-tb`, document/client widths equal on
  `代理资源`, tablet `系统诊断` center hit-tested to the navigation button, and
  the desktop collapse button still toggled `sidebar-collapsed`.

## CR-079 - Mobile Header Compact Rail Regression Fix

Date: 2026-06-19

Source: user in-app browser screenshot showing that a phone viewport could
still render the `/monitor` header title as a narrow one-character vertical
column on a resource page after CR-078.

Module: formal console mobile header, responsive shell, Phase 21B

Type: Regression Fix

Status: Verified

Background:

CR-078 strengthened the mobile header and resource-page containment, but a
later browser review still found a phone-width state where the visible header
could look squeezed: the navigation trigger retained the visible `导航` label
and the first mobile grid row could reserve width for controls before the title
had a stable readable column.

Purpose:

Make the mobile header resilient by treating the mobile navigation trigger as a
compact icon control, keeping the product title in the first-row main column,
and moving status chips to their own wrapping row. This preserves the same
mobile drawer model while preventing header controls from squeezing the title
into one-character wrapping.

Requirements:

- At mobile `<768px`, the top row uses compact columns for navigation, refresh,
  and account controls, with the product title in the remaining main column.
- The mobile navigation trigger keeps its accessible name but hides the visible
  `导航` text so it occupies a stable icon-button width.
- The product title remains horizontal with `keep-all`/nowrap treatment and a
  stable nonzero main-column width.
- Status chips remain below the first row and may wrap instead of clipping or
  compressing the title.
- Representative resource pages, including `代理资源`, keep document width equal
  to viewport width and show no one-character Chinese text columns.

Scope boundary:

- Frontend-only responsive regression fix.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date, drawer,
  modal, row menu, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not remove the mobile navigation trigger or its drawer behavior.
- Do not change backdrop, Escape, page-selection close behavior, or
  `.drawer-scroll-body`.
- Do not change Task Center grouping, `运行记录`, Run Detail tabs, enhanced
  dropdown/date logic, top-bar refresh semantics, or role-based menu
  visibility.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-075 through CR-078 responsive navigation fixes in `CHANGE_REQUESTS.md`
- Phase 12 Navigation And Page Entry Tests in `TEST_PLAN.md`
- Phase 21 Browser And Responsive Tests in `TEST_PLAN.md`

Acceptance:

- At a real mobile breakpoint (`innerWidth` around `390px`), the header grid is
  `nav title refresh account` followed by a full-width status row.
- The mobile navigation button is a 40px icon button while retaining the
  existing accessible open-navigation control.
- `舆情监控运营后台` remains horizontal and readable on mobile.
- Mobile `代理资源` has no document-level horizontal overflow and no detected
  one-character Chinese text columns.
- Mobile drawer open, page selection, and close behavior remain unchanged.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and in-app
  browser checks at mobile, tablet, and desktop widths.
  Browser measurements confirmed mobile `innerWidth≈379`, header grid
  `nav title refresh account` plus a full-width status row, hidden visible
  `导航` label with a 40px trigger, horizontal title text, no document-level
  overflow on `代理资源`, and no detected narrow Chinese text columns.

## CR-080 - Tablet Side Rail Horizontal Scrollbar Cleanup

Date: 2026-06-19

Source: user in-app browser review of the highlighted bottom horizontal
scrollbar in the collapsed side rail at a `1169px`-wide `/monitor` viewport.
The user clarified that the issue was the navigation bar's bottom scrollbar,
not the sidebar collapse button.

Module: formal console tablet/narrow-desktop side rail, Phase 21B

Type: Existing Feature Optimization

Status: Verified

Background:

CR-075 through CR-079 established one responsive navigation model: desktop
keeps a full/collapsible sidebar, tablet/narrow desktop uses a persistent
collapsed icon rail, and true mobile uses the drawer trigger. After that model
was verified, browser review found a horizontal scrollbar at the bottom of the
tablet/narrow-desktop side rail. The scrollbar was visual noise caused by
horizontal overflow in the icon navigation rail, not a business control.

Purpose:

Remove the tablet/narrow-desktop side rail's bottom horizontal scrollbar while
preserving the existing sidebar collapse button, desktop user-controlled
collapse, and true-mobile drawer navigation. The tablet/narrow-desktop rail
should read as a clean icon navigation surface without a horizontal scroll
track at the bottom.

Requirements:

- At `768px - 1279px`, keep the persistent collapsed icon rail and prevent
  horizontal overflow from exposing a bottom scrollbar.
- Keep the side-rail navigation itself scrollable so all permitted entries,
  including the final `系统诊断` entry for administrators, remain reachable.
- Keep the existing sidebar collapse button and its expand/collapse behavior.
- At desktop `>=1280px`, keep the expanded/collapsible sidebar behavior.
- At mobile `<768px`, keep the existing drawer trigger, backdrop, Escape, and
  page-selection close behavior.
- Do not change menu visibility, page routing, Task Center, Run Detail,
  enhanced select/date behavior, `.drawer-scroll-body`, owner scope, report
  scope, or top-bar refresh behavior.

Scope boundary:

- Frontend-only responsive navigation visual/interaction cleanup.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, drawer, modal, enhanced
  select/date, owner-scope, or report-scope behavior changes.

Non-goals:

- Do not remove the sidebar collapse control.
- Do not hide permitted navigation entries or rely on a horizontal scrollbar.
- Do not add a new mobile or tablet navigation mechanism.
- Do not change the accepted top-level `任务中心` information architecture or
  Run Detail tab structure.

Related tasks:

- Phase 21B Navigation Hierarchy in `TASKS.md`
- CR-075 through CR-079 responsive navigation fixes in `CHANGE_REQUESTS.md`
- Phase 12 Navigation And Page Entry Tests in `TEST_PLAN.md`
- Phase 21 Browser And Responsive Tests in `TEST_PLAN.md`

Acceptance:

- At a tablet/narrow-desktop breakpoint such as the observed `innerWidth≈1169`,
  the side rail exposes no bottom horizontal scrollbar.
- The side rail still displays the collapse button and permitted icon
  navigation entries; the final administrator entry remains clickable.
- There is no document-level horizontal overflow.
- Desktop `>=1280px` still exposes and operates the collapse button.
- Mobile `<768px` still uses the drawer trigger and close behavior.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and in-app
  browser inspection of the observed tablet/narrow-desktop width.

## CR-081 - Scrollable Drawer Fixed Footer Boundary Regression Fix

Date: 2026-06-19

Source: user in-app browser review showing scrollable drawers/modals whose
scrollbar visually continued through the fixed top header or bottom action bar.

Module: formal console secondary drawers/modals, `.drawer-scroll-body`, fixed
drawer footer chrome

Type: Regression Fix

Status: Verified

Background:

CR-073 moved drawer content scrolling into `.drawer-scroll-body` so the outer
drawer shell kept its rounded chrome. During the Phase 21G AI Access visual pass,
browser review found that action bars such as Mail Configuration, AI Access,
proxy edit, and account edit could still sit inside the scrolling content area.
That made the scrollbar read as if it extended through the bottom fixed action
bar instead of stopping between the header and footer.

Purpose:

Keep every scrollable drawer/modal visually divided into three stable regions:
the top header, the middle `.drawer-scroll-body`, and the bottom action footer.
Only the middle content region should own the scrollbar.

Requirements:

- Shared drawer normalization must keep `.drawer-scroll-body` as the only
  content scroll owner.
- Existing footer action groups (`.form-actions`, `.resource-modal-actions`,
  `.account-flow-actions`, `.ai-test-actions`, and `.rule-modal-actions`) must be
  lifted out of `.drawer-scroll-body` and attached as direct drawer children with
  shared `.drawer-fixed-footer` chrome.
- The visible scrollbar must begin below the header and end above the footer.
- Preserve all existing save, close, clear, delete, test, preview, and refresh
  actions; do not remove or rename footer buttons.
- Preserve close buttons, backdrop click, Escape handling, enhanced drawer/modal
  selects, task edit date picker behavior, Run Detail tabs, Task Center, owner
  scope, report scope, and top-bar refresh semantics.

Scope boundary:

- Frontend-only visual/structural regression fix for existing drawer chrome.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, report, or trace behavior changes.

Non-goals:

- Do not redesign drawer workflows or move actions to new pages.
- Do not change `.drawer-scroll-body` into a different scroll owner.
- Do not change modal/backdrop/Escape/page-switch close contracts.

Related tasks:

- CR-081 Scrollable Drawer Fixed Footer Boundary Regression Fix in `TASKS.md`
- CR-073 Scrollable Drawer Corner Radius Regression Fix in `TRACEABILITY.md`
- Phase 21G AI Access in `TASKS.md`

Acceptance:

- Long drawers and modals show the scrollbar only in the middle content region,
  between the fixed header and fixed footer.
- Browser checks at desktop, tablet, and phone widths verify the direct drawer
  structure: fixed header, `.drawer-scroll-body`, and fixed footer have zero
  visual gaps, and the scroll body does not contain footer action buttons.
- Bottom action bars remain visible, aligned, and usable without becoming part
  of the scrolling content.
- AI Access edit drawer, AI connection test modal, Mail Configuration modal,
  proxy drawer, account drawer, and task drawer preserve their existing buttons
  and close behavior.
- Targeted static tests cover footer extraction, fixed footer CSS, and the
  absence of the old in-scroll sticky-footer boundary.

Verification:

- Verified on 2026-06-19 with targeted frontend regression coverage, static JS
  check, inline monitor script parse, docs consistency check, and in-app
  browser checks at desktop, tablet, and phone widths. CR-082 adds a focused
  follow-up recheck for the visible scrollbar track boundary.

## CR-082 - Drawer Scrollbar Header Footer Boundary Recheck

Date: 2026-06-19

Source: user in-app browser review clarifying that every scrollable overlay's
visible scrollbar must stay between the fixed top header and fixed bottom
action bar.

Module: formal console secondary drawers/modals, `.drawer-scroll-body`, fixed
drawer chrome

Type: Regression Fix

Status: Verified

Background:

CR-081 moved footer action groups out of `.drawer-scroll-body` so bottom
actions no longer scrolled with the form content. A follow-up browser review
clarified the stricter visual acceptance rule: in any scrollable drawer or
modal, the visible scrollbar track itself must not run through either the fixed
header region or the fixed footer region.

Purpose:

Recheck and lock the overlay geometry so the header, middle scroll body, and
footer are three direct regions. The scrollbar belongs only to the middle
`.drawer-scroll-body` region, with zero visual gaps between header/body/footer
and no footer actions inside the scroll body.

Requirements:

- All drawer/modal open paths must call shared drawer normalization before
  activation so late-rendered or previously normalized drawers are rechecked.
- `.drawer-scroll-body` remains the only content scroll owner and is marked
  with `data-scroll-owner="drawer-content"` for verification.
- Drawers with direct fixed footers carry `has-fixed-footer`.
- The outer `.drawer` keeps `overflow: hidden` and rounded chrome, while the
  middle `.drawer-scroll-body` keeps vertical scrolling.
- The visible scrollbar must start at the bottom edge of the header and end at
  the top edge of the fixed footer.
- Preserve close buttons, backdrop/Escape close behavior, page-switch close
  behavior, bottom footer actions, enhanced select/date behavior, Run Detail
  tabs, Task Center, owner scope, report scope, and top-bar refresh semantics.

Scope boundary:

- Frontend-only regression recheck for existing overlay chrome.
- No backend API, database schema, permission, crawler, AI provider, SMTP,
  scheduler, deployment, Task Center, Run Detail, enhanced select/date,
  owner-scope, or report-scope behavior changes.

Non-goals:

- Do not change `.drawer-scroll-body` to a different scroll owner.
- Do not move close buttons or footer actions to new workflow categories.
- Do not change backdrop, Escape, or page-switch close contracts.
- Do not redesign Run Detail tabs or secondary drawer/modal categories.

Related tasks:

- CR-082 Drawer Scrollbar Header Footer Boundary Recheck in `TASKS.md`
- CR-081 Scrollable Drawer Fixed Footer Boundary Regression Fix in `TASKS.md`
- CR-073 Scrollable Drawer Corner Radius Regression Fix in `TRACEABILITY.md`

Acceptance:

- Representative scrollable overlays at desktop and mobile widths have direct
  header, `.drawer-scroll-body`, and optional `.drawer-fixed-footer` regions.
- Header-to-body and body-to-footer measured gaps are `0`.
- Footer action buttons are not descendants of `.drawer-scroll-body`.
- The document has no horizontal overflow while overlays are open.
- Required buttons such as save, cancel, sample fill, clear, close, refresh
  preview, and test remain visible and usable.

Verification:

- Verified on 2026-06-19 with `node --check
  api/webui/monitor/monitor.js`, inline monitor script parse,
  `python -m py_compile tests/test_monitoring_mvp.py`, targeted pytest for
  CR-073/CR-081/CR-082/CR-038, and in-app browser geometry checks.

## CR-083 - AI Access Model Helper Copy Removal Regression Fix

Date: 2026-06-19

Source: user in-app browser review of the AI Access drawer.

Module: formal console AI Access drawer, model combobox copy

Type: Regression Fix

Status: Verified

Background:

The AI Access drawer previously showed a persistent helper sentence under the
model-name field: `部分服务不提供模型列表；获取失败时仍可手动填写模型名称。`
The sentence was technically correct, but it occupied a full line in the drawer
and made the model section feel heavier than necessary. The user asked to remove
that sentence and keep the model-name input and `获取模型列表` action only.

Purpose:

Reduce visual noise in the AI Access drawer by removing the static helper copy
that was stretching the model section, while preserving the combobox, fetch
button, loading feedback, manual typing, and existing connection-test flow.

Requirements:

- remove the persistent helper sentence below the AI model combobox;
- keep the model-name input, `获取模型列表` button, and selection list;
- keep manual typing available when model-list fetch is unavailable or fails;
- preserve the drawer layout, fixed footer, close behavior, and connection test
  workflow;
- keep the model-list fetch button and model selection logic intact.

Scope boundary:

- Frontend-only copy/layout regression fix for the AI Access drawer.
- No backend API, authentication, permission, crawler, AI provider, SMTP,
  scheduler, deployment, or drawer-category changes.

Non-goals:

- Do not remove model-list fetch capability.
- Do not remove manual model-name entry.
- Do not change AI Access modal/drawer structure or button order.

Related tasks:

- CR-083 AI Access Model Helper Copy Removal Regression Fix in `TASKS.md`
- Phase 21G AI Access in `TASKS.md`
- CR-081 / CR-082 overlay boundary work in `TASKS.md`

Acceptance:

- the AI Access drawer no longer renders the static helper sentence under the
  model combobox;
- the `获取模型列表` button and manual entry remain usable;
- the drawer keeps its current layout at desktop, tablet, and phone widths;
- no console errors or horizontal overflow are introduced;
- the removal does not change the model combobox behavior or connection test
  workflow.

Verification:

- Verified on 2026-06-20 with the targeted AI Access regression test, static
  syntax checks, inline monitor script parse, docs consistency check, and
  in-app browser checks at `1440x900`, `1024x768`, and `390x844`.
- The opened AI Access drawer no longer renders the static helper sentence,
  while the model-name input, `获取模型列表` button, manual-entry placeholder,
  clear/save/close controls, fixed footer, `.drawer-scroll-body`, and
  connection-test workflow remain intact.

## CR-084 - Tablet Side Rail Narrow-Width Collapse Regression Fix

Date: 2026-06-20

Source: user in-app browser review of the tablet/narrow-desktop side rail at
`1024x768`.

Module: formal console navigation shell, tablet/narrow-desktop collapsed icon
rail

Type: Regression Fix

Status: Verified

Background:

The tablet/narrow-desktop navigation shell already switched to the collapsed
icon rail at `768px - 1279px`, but browser review at `1024x768` showed the
rail still reading too wide in the final cascade. The body state was already
`sidebar-collapsed`, so the regression was not the state toggle itself; the
collapsed rail needed an explicit final width contract so it rendered as a true
narrow icon rail instead of a wide fixed sidebar.

Purpose:

Restore the intended compact tablet rail width while preserving the existing
collapse button, vertically scrollable navigation, and mobile drawer behavior.

Requirements:

- ensure the `sidebar-collapsed` tablet rail contracts the shell sidebar to
  the narrow icon-rail width in the final cascade;
- preserve the collapse button, tooltip labels, and vertically scrollable
  navigation rail;
- keep true mobile drawer behavior, backdrop/Escape close, and page selection
  close unchanged;
- do not touch Task Center, Run Detail, or navigation hierarchy structure.

Scope boundary:

- Frontend-only regression fix for the tablet/narrow-desktop navigation shell.
- No backend API, permission, crawler, AI provider, SMTP, scheduler,
  deployment, or Task Center / Run Detail IA changes.

Non-goals:

- Do not remove the collapse button.
- Do not change mobile navigation into a different workflow.
- Do not alter sidebar grouping, active-state behavior, or page routes.

Related tasks:

- CR-084 Tablet Side Rail Narrow-Width Collapse Regression Fix in `TASKS.md`
- CR-075 Responsive Navigation Interaction Consistency in `TASKS.md`
- CR-080 Tablet Side Rail Horizontal Scrollbar Cleanup in `TASKS.md`

Acceptance:

- `1024x768` shows the collapsed icon rail at the intended narrow width when
  `sidebar-collapsed` is active;
- the collapse button remains visible and usable;
- administrator navigation entries remain reachable;
- the rail does not introduce a bottom horizontal scrollbar;
- mobile `<768px` continues to use the drawer trigger and close behavior.

Verification:

- Verified on 2026-06-20 with targeted navigation tests, docs consistency
  check, CSS cascade inspection, and in-app browser checks at `1440x900`,
  `1024x768`, and `390x844`.

## CR-085 - Narrow Tablet Inline Cascade Side Rail Regression Fix

Date: 2026-06-20

Source: user in-app browser review of `/monitor#jobs` at an in-app panel width
around `809px`.

Module: formal console navigation shell, final inline CSS cascade,
tablet/narrow-desktop collapsed icon rail

Type: Regression Fix

Status: Verified

Background:

After CR-084, browser review of a narrower in-app panel still showed a state
where the console could look like a phone-width content column pinned to the
left with empty space to the right. Runtime inspection showed the page was in
`sidebar-collapsed` state and the sidebar itself could contract to `68px`, but
the formal page's later inline `@media (max-width:1279px)` rules did not carry
the same `768px - 1279px` side-rail contract. That left the final cascade
dependent on load order and could temporarily or visually reserve the wrong
grid track.

Purpose:

Lock the final inline cascade to the accepted responsive-navigation model:
tablet/narrow desktop uses the persistent `68px` icon side rail, while true
mobile remains the only breakpoint that shows the hamburger drawer trigger.

Requirements:

- add a final inline `768px - 1279px` media rule that keeps
  `body.sidebar-collapsed .shell` on `68px minmax(0, 1fr)`;
- keep `#primary_sidebar` and `.shell > aside` capped at `68px` in that
  breakpoint;
- hide the mobile navigation trigger and backdrop at `768px - 1279px`;
- keep the sidebar collapse button visible at `768px - 1279px`;
- preserve true mobile `<768px` drawer trigger, backdrop, Escape close, and
  page-selection close behavior;
- do not change Task Center, Run Detail, enhanced select/date controls,
  `.drawer-scroll-body`, owner/report scope, or any backend/API behavior.

Scope boundary:

- Frontend-only final-cascade regression fix for the formal console shell.
- No navigation IA, page route, Task Center, Run Detail, overlay, dropdown,
  date picker, permission, API, crawler, AI, SMTP, scheduler, database, or
  deployment changes.

Non-goals:

- Do not remove the sidebar collapse button.
- Do not convert tablet/narrow desktop back to a mobile drawer.
- Do not change `/monitor` route or hash routing behavior.
- Do not alter the Run Detail tabs, overlay scroll ownership, or drawer close
  contracts.

Related tasks:

- CR-085 Narrow Tablet Inline Cascade Side Rail Regression Fix in `TASKS.md`
- CR-084 Tablet Side Rail Narrow-Width Collapse Regression Fix in `TASKS.md`
- CR-075 Responsive Navigation Interaction Consistency in `TASKS.md`

Acceptance:

- at an in-app panel width around `809px`, `body.sidebar-collapsed` renders the
  shell grid as `68px` plus content, with no right-side reserved blank area;
- the mobile navigation button is not painted at `768px - 1279px`;
- the sidebar collapse button remains painted and usable at `768px - 1279px`;
- `1024x768` keeps the same persistent icon side rail;
- `390x844` keeps the mobile hamburger drawer behavior;
- no document horizontal overflow is introduced.

Verification:

- Verified on 2026-06-20 with a red/green targeted regression test for the
  inline tablet cascade, in-app browser checks at the observed `innerWidth`
  around `809px`, `1024x768`, and `390x844`, plus static syntax and docs
  checks recorded in `docs/TEST_RESULTS.md`.

## CR-070 - Account Environment Export And Import Package

Date: 2026-06-19

Source: user requirement that login state, full account identity, and platform
account information should be exportable and importable into another
deployment in one operation.

Module: platform accounts, account identity, login state, profile storage,
deployment migration, sensitive-data governance

Type: New Capability

Status: Accepted

Background:

CR-047 defines one platform account as one `profile_key` plus one stable
account identity. That is enough to make login and crawling consistent inside
one deployment, but it does not yet define how to move a usable account
environment to another deployment.

The new requirement is broader than exporting visible account fields. The
operator wants an account package that can carry login state, necessary browser
profile state, CR-047 identity fields, and the platform-account metadata the
system has learned, so a new deployment can import the package and continue
from the same account environment where possible. The migration package should
be slim: it should include configuration, login/session state, and required
profile state, not raw whole-profile cache and temporary browser artifacts.

Purpose:

Add an administrator-only account environment export/import capability for
moving a platform account between deployments without manually recreating every
identity, profile, login, and platform-account metadata field.

Requirements:

- Support two package modes:
  - metadata-only package: exports account identity and platform-account
    metadata, but no cookies or browser profile traces; import requires
    re-login before use. If the metadata package contains real identity
    details such as fingerprint seed, runtime snapshot summary, recognized
    platform account ID, or profile-derived metadata, the recommended V1
    default is the same encrypted `.maepkg` envelope rather than plaintext.
  - slim login-state migration package: exports account identity, encrypted
    login material, proxy endpoint hint without credentials, and the necessary
    profile state needed to attempt login-state reuse.
- A slim login-state migration package must include:
  - a manifest with package version, source app/schema identity version,
    package type, created time, source workspace/account/platform, source
    `profile_key`, platform, account display name, login type, status, and
    redacted package checksum evidence;
  - CR-047 identity fields such as environment region, browser platform,
    identity template, fingerprint seed, UA, timezone, locale,
    accept-language, screen/viewport/device flags, generator metadata,
    lock/re-login state, and redacted runtime snapshot summary;
  - slim profile state under the account `profile_key`, including provider-
    owned cookies, localStorage, IndexedDB, preferences, login-relevant
    service-worker/session records, and session state where the active
    provider stores them;
  - encrypted Cookie/login material stored by the project, if present;
  - platform account metadata captured by the project, such as recognized
    platform account ID/name/display name, avatar metadata, latest login and
    check timestamps, customer-safe status, and last customer-safe error;
  - proxy binding metadata as a target-side mapping requirement, redacted
    region snapshot, and encrypted host/IP plus port hint, but no proxy
    username, password, token, authentication header, or provider secret.
- V1 migration packages use passphrase-based encryption. They must not rely
  only on the source deployment encryption key because the target deployment
  may not have that key. Target-deployment public-key encryption is future
  scope.
- Import must be administrator-only and must verify package integrity,
  package version, manifest schema, checksum, platform, provider compatibility,
  identity environment version, profile path safety, and target proxy mapping
  before writing any account as active.
- Import creates a new target account/profile by default, with a new target
  `profile_key` based on the target deployment's account ID. Preserving or
  overwriting an existing account requires an explicit conflict policy.
- Export and import must have explicit operation states, terminal states,
  timeouts, cancellation/interruption cleanup, operation locks, and idempotent
  finalization so a package operation cannot leave an account/profile lock
  stuck.
- After import, the system must run a login-state verification for the account.
  If verification fails, the imported account is marked `requires_relogin` or
  equivalent and must not be silently used for crawling.
- Export and import actions must be audited without recording raw cookies,
  profile paths, proxy credentials, proxy endpoint hints, CDP endpoints, noVNC
  tokens, or package passphrases.

Scope boundary:

- This is an account-environment migration capability, not a general database
  backup/restore feature.
- It covers the Platform Accounts resource and the account's browser profile
  environment. Monitoring tasks, crawl runs, reports, AI traces, email
  delivery logs, users, runtime settings, full database backup content, and
  customer business data remain outside the default account package unless a
  later export product requirement explicitly adds them.
- It builds on CR-047 account identity fields and the existing server-side
  profile root. It must not bypass CR-047 identity validation, locks,
  re-login rules, or proxy consistency.

Non-goals:

- Do not promise that an imported login state will always remain valid on a
  different server, IP, browser build, or time window; platforms may invalidate
  sessions after migration.
- Do not export plaintext cookies, proxy credentials, platform tokens, local
  profile paths, server command lines, CDP endpoints, noVNC tokens, or
  deployment encryption keys.
- Do not export a raw whole browser profile by default. Cache, GPU cache, code
  cache, media cache, crash reports, downloads, screenshots, temporary files,
  and regenerable browser artifacts are excluded unless a later provider-
  specific review explicitly requires one of them.
- Do not bypass captcha, SMS, slider, device verification, or platform risk
  checks.
- Do not turn this into gray account trading, shared account marketplace, or
  bulk account rotation behavior.
- Do not overwrite an existing target account or profile directory without an
  explicit administrator conflict decision and audit record.
- Do not include cached avatar image bytes in V1; export avatar metadata only.
- Do not leave package artifacts as long-term application storage by default.
  Generated package bytes are runtime artifacts with short retention and
  cleanup behavior.

Confirmed V1 decisions:

- V1 supports metadata-only export and slim encrypted login-state migration
  package.
- V1 uses passphrase-based package encryption.
- V1 may include source proxy host/IP plus port as an encrypted endpoint hint,
  but must not export proxy username, password, token, authentication header,
  or provider secret.
- V1 imports create a new target account/profile by default; replace, merge,
  and overwrite are future scope.
- V1 exports avatar metadata only, not cached avatar image bytes.

Related tasks:

- CR-070 Account Environment Export And Import Package in `TASKS.md`
- CR-047 Account Identity Fidelity in `TASKS.md`
- Account Environment Export And Import Tests in `TEST_PLAN.md`

Acceptance:

- Administrator can export a metadata-only package without cookies or profile
  traces.
- Administrator can export a slim encrypted login-state migration package
  containing account identity, login/session material, necessary profile state,
  proxy endpoint hint without credentials, and platform-account metadata needed
  for target-side import.
- The package manifest is versioned, checksummed, and redacted.
- Package generation and import follow explicit state machines and terminate as
  ready/completed, failed, cancelled, expired, active, requires-relogin, or
  rolled-back without leaving locks stuck.
- Import validates integrity, compatibility, target profile safety, and proxy
  mapping before activation.
- Imported accounts use a target deployment `profile_key` and never write
  outside the configured profile root.
- Import runs login-state verification. Verified accounts may become active;
  failed accounts become `requires_relogin` and are not used silently.
- Export/import audit logs are present and contain no raw secrets or paths.
- Normal users cannot export or import account environment packages.
- Tests fail if an export package or log contains raw cookies, proxy
  credentials, proxy endpoint hints outside the encrypted payload, profile
  paths, package secrets, CDP endpoints, noVNC tokens, raw whole-profile cache,
  or traversal paths.

## CR-091 - Open Todo MECE Rebaseline And Phase 5.1 Preflight Gate

Date: 2026-06-19

Source: user request to reorganize the current open todo set before starting
Phase 5.1 implementation, with Phase 21 already running in a separate
worktree.

Module: documentation governance, roadmap sequencing, account-environment
planning

Type: Documentation Governance

Status: Verified

Background:

The current open work has several nearby but different concerns: Phase 21
frontend visual refinement, CR-047 / Phase 5.1 account identity fidelity,
container/server-like validation, BrowserEnvironmentProvider compatibility,
MediaCrawler CDP integration, and CR-070 account-environment export/import.
Those items must not be merged into one broad task because they have different
owners, risk profiles, tests, and rollback boundaries.

Purpose:

Rebaseline the active todo list into a MECE execution sequence before starting
Phase 5.1 code work. The immediate goal is to make Phase 5.1 begin with a
read-only runtime compatibility preflight, then proceed to account identity
implementation only after the current login/crawl/MediaCrawler/CDP paths can
share one provider boundary and one requested/effective runtime snapshot
contract.

Requirements:

- Keep Phase 21 as the current frontend visual-only lane. It may refine
  colors, contrast, spacing, density, loading/empty/error/focus states, and
  responsive wrapping, but it must not change the current Task Center, Run
  Detail, drawer, modal, select/date, close, scroll, or routing logic without a
  separate accepted CR.
- Add a Phase 5.1 Preflight lane before Phase 5.1 implementation. The preflight
  is documentation/read-only compatibility work that maps current QR login,
  Cookie validation, login-state checks, manual run, scheduler run, runner, and
  MediaCrawler CDP launch/reconnect entry points.
- Treat BrowserEnvironmentProvider as the Phase 5.1 provider boundary, not as a
  separate parallel product line. QR login, Cookie validation, login-state
  checks, manual runs, scheduler runs, and MediaCrawler CDP launch/reconnect
  must use the same provider output before Phase 5.1 can be accepted.
- Treat container/server-like validation as the Phase 5.1 development and
  acceptance baseline. Local Chrome auto-detection, local-window login, and
  CDP connect-existing are development fallbacks only and cannot prove locked
  or active account identity.
- Keep Phase 5.1 implementation scoped to account identity fields, generator,
  validator, state machine, locking, reset/re-login, and runtime binding after
  preflight passes.
- Keep Phase 5.1 acceptance scoped to requested/effective runtime snapshot,
  provider metadata, proxy effect proof or fail-closed behavior, and
  server-like/container verification.
- Defer CR-070 / Phase 5.2 until CR-047 provider binding and effective runtime
  snapshot are implemented and verified.
- Keep CR-037 role-based email governance, the unrendered Users And
  Permissions page, and Phase 7.1D historical repair as separate deferred or
  operator-gated items.

Scope boundary:

- Documentation-only roadmap and task sequencing update.
- Update `TASKS.md`, `CURRENT_STATE.md`, `TEST_PLAN.md`, and
  `TRACEABILITY.md` to reflect the new ordering and gates.
- Do not change code, UI, database schema, runtime data, account profiles,
  cookies, proxy configuration, crawler behavior, deployment configuration, or
  production state.

Non-goals:

- Do not implement Phase 21, Phase 5.1, BrowserEnvironmentProvider, container
  packaging, MediaCrawler integration changes, or CR-070 export/import code in
  this batch.
- Do not redefine Phase 21 as backend, deployment, or account-environment work.
- Do not start CR-070 before CR-047 provider/effective snapshot verification.
- Do not turn containerization into an independent parallel big task; it is the
  Phase 5.1 development and acceptance baseline.
- Do not reopen completed historical phases. New structure issues are owned by
  this documentation-governance CR.

Related tasks:

- CR-091 Open Todo MECE Rebaseline in `TASKS.md`
- CR-047 Account Identity Fidelity in `TASKS.md`
- CR-070 Account Environment Export And Import Package in `TASKS.md`

Acceptance:

- `TASKS.md` separates the active Phase 21 visual lane, Phase 5.1 Preflight,
  Phase 5.1 implementation, Phase 5.1 acceptance, Phase 5.2 / CR-070, and
  deferred independent items.
- `CURRENT_STATE.md` lists the next allowed implementation order as Phase 21
  merge, Phase 5.1 Preflight, Phase 5.1 implementation, then CR-070 /
  Phase 5.2 only after Phase 5.1 provider/effective snapshot verification.
- `TEST_PLAN.md` states that Phase 5.1 cannot be accepted by database fields
  alone and must validate QR login, Cookie validation, login-state checks,
  manual run, scheduler run, and MediaCrawler CDP launch/reconnect against one
  provider output in a container/server-like baseline.
- `TRACEABILITY.md` links CR-047 to Phase 5.1 Preflight and links CR-070 to
  CR-047 provider/effective snapshot completion.
- Documentation consistency and plan-cross-validation review pass without
  blocking findings.

## CR-092 - Frontend Stack Migration Evaluation And Monitor Next Plan

Date: 2026-06-19

Source: user requirement to record a future frontend technology migration and
gradual rebuild plan without changing the active Phase 21 worktree.

Module: frontend architecture, monitor console migration planning

Type: Existing Feature Optimization / Architecture Planning

Status: Needs Confirmation

Background:

The current formal `/monitor` console is still implemented through the
existing no-build Vanilla JavaScript path, mainly `api/monitor_web/index.html`
plus local monitor CSS/JS assets. That path remains the accepted baseline for
Phase 21 visual refinement, but it is not the preferred long-term shape for a
more complex product if future work needs stronger typing, component
boundaries, route guards, API-client structure, and test isolation.

Purpose:

Record a future architecture planning lane for evaluating and gradually
rebuilding the monitor console under an independent entry such as
`/monitor-next`, while keeping the current `/monitor` product stable until a
separate replacement gate is satisfied.

Requirements:

- Keep the current `/monitor` and Phase 21 workstreams on the existing
  Vanilla/no-build baseline until a later accepted CR changes that.
- Evaluate Vite plus TypeScript before implementation starts.
- Treat Vue 3 and React, plus suitable Chinese ToB component libraries or
  headless component options, as candidates only until a technology decision
  is confirmed.
- Plan `/monitor-next` or an equivalent independent frontend entry that can
  coexist with the existing `/monitor`.
- Default the new frontend to the existing `/api/auth/...` and
  `/api/monitor/...` backend contracts.
- Prohibit direct frontend calls to MediaCrawler raw surfaces such as
  `/api/crawler/...`, `/api/data/...`, old websocket endpoints, or any crawler
  control plane outside the monitor API boundary.
- Require a frontend architecture document before page migration begins. It
  must cover entry/deployment boundary, technology choice, directory layering,
  route and permission matrix, API client, state boundaries, component
  layering, design tokens, responsive strategy, migration compatibility,
  replacement gate, rollback, and tests.
- Preserve the current Task Center, Run Detail, drawer, modal, enhanced
  select/date, report download, email delivery, routing, owner-scope, and
  permission behavior until explicit page-equivalence migration work verifies
  replacement.

Scope boundary:

- Documentation and future architecture planning only.
- No frontend project, Node build pipeline, package dependency, route, API,
  UI, schema, permission, crawler, or deployment change is part of this CR.
- This CR does not block Phase 21, Phase 5.1P, CR-047, CR-070, CR-093, or
  CR-094.

Non-goals:

- Do not implement `/monitor-next` in this CR.
- Do not replace `/monitor`.
- Do not select Vue, React, a component library, Tailwind, or any build tool as
  final without a later accepted decision.
- Do not restore the older separate top-level Run Center or Report Center
  information architecture.
- Do not use frontend migration to change backend APIs implicitly. Missing
  monitor API support must be recorded as a separate API CR.

Dependencies:

- CR-092 depends on no current implementation task.
- Any later implementation must coordinate with the active Phase 21 baseline
  and must not edit the same `/monitor` files in parallel unless explicitly
  coordinated.

Implementation steps:

- Create and maintain `MONITOR_NEXT_FRONTEND_PLAN.md` as the planning source.
- Compare candidate stacks and component libraries against Chinese ToB console
  needs, testing, deployment complexity, accessibility, table/form/drawer/modal
  maturity, and dependency weight.
- Define route/permission, API-client, component, state, design-token,
  responsive, testing, compatibility, replacement, and rollback requirements.
- Split future page migration into separate page or feature CRs only after the
  planning document and stack decision are accepted.

Acceptance:

- The future frontend plan is recorded without changing current `/monitor`.
- The plan states that `/monitor-next` must coexist with `/monitor` until
  functional, permission, interaction, responsive, and regression equivalence
  are proven.
- The plan states that replacing `/monitor` requires a later replacement gate
  and rollback path.
- The plan does not mark a frontend stack as decided.

Tests:

- Frontend migration tests in `TEST_PLAN.md`.
- Traceability row for CR-092 in `TRACEABILITY.md`.

## CR-093 - MediaCrawler Internalization And Public Exposure Boundary

Date: 2026-06-19

Source: user requirement to treat MediaCrawler as an internal engine rather
than a public product cockpit.

Module: product boundary, deployment exposure, API authorization, route
governance

Type: Existing Feature Optimization / Security And Product Boundary Hardening

Status: Accepted

Pending decisions:

The product boundary is accepted. The exact production mount strategy, reverse
proxy deny rules, and whether old routes return 404, 403, or are not mounted
need confirmation after a read-only route audit.

Background:

The product has grown from a MediaCrawler-based project into a law-firm public
opinion monitoring system. MediaCrawler remains an important internal source
of collection, login, account-check, and output-parsing capability, but the
formal product should not expose raw MediaCrawler WebUI, raw crawler APIs,
raw data files, old websocket diagnostics, command-line concepts, debug logs,
local paths, or MediaCrawler branding to public users.

Purpose:

Define a future product-boundary and security-hardening lane that keeps
MediaCrawler as an internal engine while the public product surface remains
the Legal Sentiment Monitor web UI and monitor APIs.

Requirements:

- Public product entry points should be limited to `/monitor`,
  `/api/auth/...`, `/api/monitor/...`, monitor-specific static assets, and
  necessary authenticated downloads or same-origin cached resources.
- Audit current FastAPI routers and static mounts before changing any route.
- Classify routes as formal product, administrator diagnostic, internal
  dependency, historical/development, or production-disabled.
- Production exposure must default to not exposing old MediaCrawler WebUI,
  `/api/crawler/...`, `/api/data/...`, old websocket log/status endpoints,
  old generic assets/logos/static paths, raw file browsing/download/preview,
  and direct crawler start/stop/control surfaces.
- If a formal monitor workflow still depends on an old route, record the
  dependency and replacement path before disabling it.
- User-visible product text must avoid MediaCrawler, Command Center,
  command-line, local path, environment variable, debug, self-test, mock, and
  prototype wording except in trusted administrator diagnostics where needed.
- Preserve current task running, platform login, account checks, output
  parsing, Task Center, Run Detail, permissions, drawer/dropdown/date, and
  scroll behavior.

Scope boundary:

- Documentation, route-audit planning, and future exposure governance only.
- No route, mount, reverse proxy, API, UI, schema, crawler, deployment, or
  runtime configuration change is part of this CR.
- This CR does not block Phase 21, Phase 5.1P, CR-047, CR-070, CR-092, or
  CR-094.

Non-goals:

- Do not delete MediaCrawler code.
- Do not replace the crawler implementation.
- Do not change task running, login, account checks, output parsing, report
  generation, email delivery, or permission behavior.
- Do not hide or remove a route that the formal monitor UI/API still depends
  on without a replacement plan and a later implementation CR.

Dependencies:

- A future implementation must start with a read-only route and mount audit.
- Production deny/not-mounted behavior requires deployment strategy
  confirmation before implementation.

Implementation steps:

- Audit all FastAPI routers and static mounts.
- Classify every public path and websocket/static surface.
- Define the formal public allowlist and authentication/administrator
  requirements.
- Design development-only or internal-only behavior for old crawler/data/ws
  surfaces.
- Define reverse proxy deny/not-mounted rules for production.
- Search and clean formal user-facing wording only within a later accepted
  implementation CR.
- Add route exposure, regression, and product-wording tests.

Acceptance:

- Documentation clearly states that MediaCrawler is the internal collection
  engine, not the public product cockpit.
- Future implementation cannot disable old routes until dependency and
  replacement paths are documented.
- Production exposure tests specify which old routes must be unavailable and
  what the fixed expected result is after the implementation strategy is
  confirmed.
- Existing monitor workflows remain protected as must-not-break behavior.

Tests:

- Public exposure boundary tests in `TEST_PLAN.md`.
- Traceability row for CR-093 in `TRACEABILITY.md`.

## CR-094 - Crawler Engine Provider Architecture

Date: 2026-06-19

Source: user requirement to plan a future crawler-engine abstraction without
letting new engines bypass current task, account, proxy, profile, report, or
Run Detail systems.

Module: crawler architecture, provider contract, account/profile boundary,
server-like runtime

Type: Architecture Planning / Future Extensibility

Status: Needs Confirmation

Background:

The current collection capability mainly comes from MediaCrawler and the
existing Playwright/CDP provider path. CR-047 / Phase 5.1P already owns the
near-term compatibility check for current QR login, Cookie validation,
login-state checks, manual runs, scheduler runs, runner behavior, and
MediaCrawler CDP launch/reconnect. A broader multi-engine provider
architecture is a separate future concern.

Purpose:

Record a future architecture lane for a Crawler Engine Provider contract so
MediaCrawler can remain the current default provider while future engines can
be evaluated without creating parallel task, account, proxy, report, or
frontend systems.

Requirements:

- Treat MediaCrawler as the current default provider, not as the permanent only
  possible provider.
- Define provider declarations for provider id/name, supported platforms,
  login types, account checks, comments, time filters, proxy support, account
  binding, container/server-like support, output version, error version, and
  capability limits.
- Map existing monitoring tasks into provider input without changing the
  upper-layer task model.
- Normalize provider output into the existing content, AI evaluation, report,
  Task Center, and Run Detail model.
- Normalize provider errors and lifecycle states such as unavailable, launch
  failed, login expired, verification required, proxy failed, timeout,
  cancelled, interrupted, partial success, no result, output parse failed,
  unsupported capability, rate limited, platform changed, and unknown error.
- Preserve `profile_key` as the upper-layer account identity while allowing
  provider-specific profile material under controlled bindings.
- Require production providers to be server-like/container-compatible,
  observable, stoppable, persistent where needed, resource-cleaning, and
  governed by existing account/profile/proxy locks.
- Forbid new providers from adding parallel task, account, profile, report,
  permission, or frontend entry systems.

Scope boundary:

- Documentation and architecture planning only.
- No provider abstraction, schema, code, UI, runtime data, crawler, profile,
  account, proxy, or deployment change is part of this CR.
- This CR is not part of Phase 5.1P. The verified Phase 5.1P map remains the
  MediaCrawler/CDP/BrowserEnvironmentProvider compatibility boundary for
  CR-047 only.
- This CR does not block Phase 21, Phase 5.1P, CR-047, CR-070, CR-092, or
  CR-093.

Non-goals:

- Do not replace MediaCrawler.
- Do not implement a new provider.
- Do not introduce provider tables, profile-binding tables, or capability
  schema without a later accepted data-model/migration CR.
- Do not expose provider-private profile material, cookies, proxy credentials,
  raw paths, CDP endpoints, command lines, or debug fields to normal users.

Dependencies:

- A future implementation must first complete or explicitly coordinate with
  CR-047 provider/effective snapshot behavior.
- Any schema change requires a separate data model and migration CR.

Implementation steps:

- Maintain `CRAWLER_PROVIDER_ARCHITECTURE.md` as the planning source.
- Audit the existing MediaCrawler login, account check, task run, output
  parsing, error, profile, proxy, and Run Detail chains.
- Draft provider input, output, capability, profile-binding, error, lifecycle,
  security, and server-like acceptance contracts.
- Plan how a future `MediaCrawlerProvider` would map current behavior into the
  contract without changing current runtime behavior.
- Add provider-architecture tests before any implementation starts.

Acceptance:

- Documentation clearly separates CR-094 from Phase 5.1P.
- Documentation states that new providers cannot bypass the existing monitor
  task/account/proxy/profile/report/Run Detail/permission systems.
- Documentation states that formal providers must be server-like and cannot
  rely on an operator's local desktop browser for production.
- Tests and traceability are connected before implementation.

Tests:

- Crawler provider architecture tests in `TEST_PLAN.md`.
- Traceability row for CR-094 in `TRACEABILITY.md`.

## CR-095 - Atomic Goal Execution Governance And Readiness Gate

Date: 2026-06-19

Source: user request to audit and optimize the current todo system in goal
mode so open work is boundary-clear, atomic, MECE, ordered, testable, and
acceptance-ready.

Module: documentation governance, agent workflow, roadmap execution, test
iteration, acceptance standards

Type: Documentation Governance

Status: Verified

Background:

CR-091 separated the current open roadmap into Phase 21, Phase 5.1P,
Phase 5.1, CR-070 / Phase 5.2, future CR-092 through CR-094, and deferred
operator-gated items. The next risk is not only whether the lanes are MECE, but
whether each lane can be opened as a small executable goal without drifting
into neighboring scope.

Purpose:

Add a goal-readiness and execution-governance layer that turns the open todo
roadmap into atomic, serial, reviewable goal packets. The rule is:
one goal owns one boundary, one risk area, one test loop, and one acceptance
gate before the next goal starts.

Requirements:

- Add `docs/GOAL_EXECUTION_GUIDELINES.md` as the source for goal packet
  structure, atomicity rules, current execution lanes, test iteration loop,
  acceptance standards, and stop conditions.
- Keep CR-091 as the owner of MECE open-todo lane separation. CR-095 owns how
  those lanes become executable goals.
- Require every non-trivial future goal to state owner CR/phase, current
  baseline, in scope, out of scope, hard boundaries, dependencies, expected
  touch surface, execution steps, test loop, acceptance criteria, rollback or
  recovery, documentation updates, and stop conditions.
- Preserve the current execution order: Phase 21 is merged and closed on
  `main`, Phase 5.1P read-only preflight is next, then Phase 5.1A-D
  implementation, Phase 5.1 acceptance, and CR-070 / Phase 5.2 only after
  CR-047 provider/effective snapshot verification.
- Split Phase 5.1 into goal-ready serial units: preflight, data model,
  generator/validator, locking/re-login, runtime binding, and acceptance gate.
- Split CR-070 / Phase 5.2 into goal-ready serial units: package contract and
  security model, export flow, import flow, post-import verification/recovery,
  and test-safety verification.
- Keep Phase 21 visual-only work from touching backend APIs, schema,
  permissions, runtime behavior, crawler behavior, account identity, deployment,
  Task Center structure, Run Detail structure, drawer/modal behavior,
  select/date behavior, close behavior, scroll ownership, refresh logic, or
  routing without a separate accepted CR.
- Keep CR-092, CR-093, and CR-094 as future independent backlog lanes, not
  hidden prerequisites for Phase 21, Phase 5.1P, Phase 5.1, or CR-070.
- Define the test iteration loop as pre-check, implementation, targeted tests,
  fix/rerun, broader checks, documentation sync, documentation consistency
  check, and read-only cross-review when risk warrants it.

Scope boundary:

- Documentation-only governance update.
- No code, UI, database schema, runtime data, account profile, cookie, proxy,
  crawler, route, deployment, production, or worktree state change is part of
  this CR.
- This CR may update `CHANGE_REQUESTS.md`, `TASKS.md`, `CURRENT_STATE.md`,
  `AGENT_WORKFLOW.md`, `DOCUMENTATION_CHECKS.md`, `TEST_PLAN.md`,
  `TRACEABILITY.md`, `TEST_RESULTS.md`, and add
  `GOAL_EXECUTION_GUIDELINES.md`.

Non-goals:

- Do not implement Phase 21, Phase 5.1P, Phase 5.1, CR-070, CR-092, CR-093,
  or CR-094.
- Do not reopen completed historical phases.
- Do not turn `Needs Confirmation` items into implementation-ready tasks.
- Do not create a new branch, worktree, runtime package, provider abstraction,
  container strategy, frontend stack, route exposure change, or schema change.

Related tasks:

- CR-095 Atomic Goal Execution Governance in `TASKS.md`
- Goal execution guidance in `AGENT_WORKFLOW.md`
- Goal readiness tests in `TEST_PLAN.md`

Acceptance:

- `GOAL_EXECUTION_GUIDELINES.md` defines the goal packet template, atomicity
  rules, current execution lanes, test loop, acceptance standards, and stop
  conditions.
- `TASKS.md` records CR-095 as a documentation-governance batch and keeps the
  current open lanes in the same priority order.
- `CURRENT_STATE.md` states that future open work must be opened with the
  CR-095 goal packet and must not skip the documented order.
- `AGENT_WORKFLOW.md` points agents to the goal execution guidelines before
  approving or starting a non-trivial goal.
- `TEST_PLAN.md` contains goal-readiness and execution-governance tests.
- `TRACEABILITY.md` links CR-095 to its task and test areas.
- Documentation consistency, whitespace check, and full open-todo
  cross-review finish with no blocking findings.

Tests:

- Goal readiness and execution governance tests in `TEST_PLAN.md`.
- `uv run python scripts/check_docs.py`.
- `git diff --check`.
- Read-only full open-todo cross-review.

## CR-097 - Operations Home Visual Density Reduction

Date: 2026-06-21

Source: user request to make the operations home much more visual, much less
wordy, easier to read at a glance, and bounded so the desktop/tablet overview
does not run longer than the left navigation.

Module: monitor web frontend dashboard surface, responsive CSS, and dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

The current Operations Home already exposes the right real data surface, but
the first viewport still reads too much like a text-first status page. The user
wants the page to feel more like a cockpit: mostly charts, bars, blocks, and
numeric signals, with the minimum possible explanatory copy.

Purpose:

Reduce visible wording on the Operations Home while preserving the same
underlying data contract, role safety, and drilldown paths.

Requirements:

- Keep the existing Operations Home data contract and drilldown destinations.
- Reduce explanatory text density on the first screen.
- Prefer visual encodings such as meter bars, segmented blocks, and compact
  numeric summaries over prose.
- Keep the first viewport chart-first: five compact KPI meters, one dominant
  flow chart, platform breakdown with heatmap blocks, delivery/lead
  composition, and a compact visual priority panel.
- Keep desktop and tablet Operations Home height within the shell/navigation
  height; do not leave a large shortcut/detail row below the visual dashboard.
- Keep the shortcut dock as a lightweight mobile affordance only.
- Keep normal-user and administrator visibility boundaries intact.
- Preserve tablet and mobile readability.

Scope boundary:

- Frontend-only visual refinement of the current `/monitor` Operations Home.
- No backend API, schema, permission, crawler, AI, email, or deployment change
  is part of this CR.
- No new route or new product surface is introduced.

Non-goals:

- Do not change the real metrics, their source fields, or drilldown behavior.
- Do not add new chart dependencies or a new frontend stack.
- Do not widen the product scope beyond the existing home, resource, and
  diagnostics surfaces.

Related tasks:

- CR-097 Operations Home Visual Density Reduction in `TASKS.md`
- Phase 13 overview operations home tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The Operations Home first viewport is visually denser and less prose-heavy.
- The home still shows task health, run activity, report/review, email
  delivery, lead risk, and resource health signals.
- The dashboard does not expose raw field names such as `job_id`, `run_id`,
  `report_id`, `summary.platform_results`, `collection_progress`,
  `ai_progress`, `job_snapshot_json`, or `email_delivery_logs` as primary
  labels.
- Tablet and mobile layouts remain readable without overflow or overlap.
- Desktop and tablet layouts fit in the same first-screen height as the left
  navigation, with no page-length overrun caused by the overview itself.
- The dominant flow chart avoids visible stretched labels or circular markers
  on desktop/tablet, and the page uses visual encodings rather than table-like
  filler.
- Existing drilldowns and role boundaries still pass regression tests.

Tests:

- Phase 13 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k \"phase_13b or phase_13c\"`.
- `uv run python scripts/check_docs.py`.

## CR-098 - Operations Home Data-First Visual Refit

Date: 2026-06-22

Source: user feedback after the CR-097 prototype that the overview still felt
ugly, too text-heavy, and too long; the refined dashboard must follow the
current project design system rather than a detached prototype style.

Module: monitor web frontend dashboard surface, responsive CSS, and
dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-097 reduced the original text-heavy Operations Home and verified the first
height boundary. The follow-up feedback requires a stricter visual refit:
preserve the project shell, color, typography, and interaction rules while
making the home page read as charts and data blocks first, with minimal copy
and no page-length overrun beyond the left navigation on desktop/tablet.

Purpose:

Make the current `/monitor` Operations Home a data-first operational dashboard
inside the existing design system, without changing product scope or backend
contracts.

Requirements:

- Keep the current Phase 21 light enterprise visual language: neutral surface,
  teal accent, restrained risk color, compact type, and modest radii.
- Keep the page focused on visual evidence: KPI micro bars, a five-stage flow
  chart, compact priority bars, platform/delivery breakdowns, and resource
  bars.
- Remove or hide prose, shortcut, table-like, and status-heavy elements that do
  not help the first-screen read.
- Keep desktop `1440x900` and tablet `1024x768` Operations Home content within
  the left navigation/shell height.
- Keep mobile readable with a chart-first vertical order and no duplicated
  page-kicker copy.
- Preserve administrator/normal-user boundaries, drilldown destinations, and
  existing data fields.

Scope boundary:

- Frontend-only refit of the existing `/monitor` Operations Home.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.
- No new route, frontend stack, chart dependency, or Open Design artifact is
  introduced.

Non-goals:

- Do not replace the whole console shell.
- Do not introduce a detached visual style that conflicts with the existing
  project design guidelines.
- Do not add new metrics that require backend fields.
- Do not reopen CR-097 as incomplete; CR-098 is a follow-up refinement.

Related tasks:

- CR-098 Operations Home Data-First Visual Refit in `TASKS.md`
- CR-098 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The first screen reads primarily through charts, bars, and numbers rather
  than prose or tables.
- Desktop and tablet Operations Home do not extend below the left navigation.
- The shortcut dock is hidden by the final CR-098 cascade so it no longer adds
  page height.
- The stage flow uses uniform teal fill with risk shown as an alert overlay,
  preventing multiple competing palette meanings.
- The priority panel shows only the most important exceptions as compact bars.
- Platform heatmap blocks are hidden when they add visual noise rather than
  insight.
- Existing role gating and drilldowns still pass regression tests.

Tests:

- CR-098 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k \"phase_13b or phase_13c\"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/Playwright checks at `1440x900`, `1024x768`, and `390x844`.
- `uv run python scripts/check_docs.py`.

## CR-099 - Operations Home Legend-First Visual Clarity

Date: 2026-06-22

Source: user feedback after the CR-098 pass that the charts still lacked
visible legends, icon sizes felt awkward, and the palette needed to move
closer to the supplied reference image without copying it directly.

Module: monitor web frontend dashboard surface, responsive CSS, and
dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-098 fixed the one-screen data-first layout and kept the dashboard inside the
existing design system, but some charts still required guesswork because their
meaning was not visible at first glance. The next pass needed to make the
overview self-explanatory through visible keys, calmer icon scale, and clearer
color-role separation.

Purpose:

Improve the current `/monitor` Operations Home readability by making the
primary charts explain themselves without hover text or extra prose.

Requirements:

- Keep the current dashboard data contract, role boundaries, drilldowns,
  one-screen height boundary, and existing console shell.
- Add visible legend or direct-key treatment to the flow chart, delivery/review
  breakdown, attention panel, and resource panel.
- Normalize KPI and alert icon sizes so they support scanning instead of
  dominating card content.
- Separate color roles: semantic status colors for normal/live/review/risk and
  category colors only for the platform composition breakdown.
- Move the platform breakdown closer to the supplied figure direction with a
  donut plus labeled bar list, while staying inside the current project design
  language.

Scope boundary:

- Frontend-only refinement of the existing `/monitor` Operations Home.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.
- No new chart library, build step, route, or detached prototype is
  introduced.

Non-goals:

- Do not replace the current console shell or page structure.
- Do not reintroduce long descriptive copy, table-heavy summary blocks, or a
  second prototype visual language.
- Do not change the meaning of existing dashboard aggregates or invent new
  backend fields.
- Do not reopen CR-098 as incomplete; CR-099 is a follow-up refinement.

Related tasks:

- CR-099 Operations Home Legend-First Visual Clarity in `TASKS.md`
- CR-099 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- Operators can read chart meaning from visible legend/direct labels without
  guessing what each color means.
- KPI and alert icons use one consistent compact scale across cards and
  attention rows.
- Platform composition uses a category palette and donut-plus-list treatment,
  while status-oriented charts keep semantic status colors.
- Desktop/tablet keep the CR-098 height boundary and mobile remains chart-first
  without overflow or one-character text columns.
- Existing role gating, drilldowns, and dashboard data compatibility still
  pass regression tests.

Tests:

- CR-099 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/Playwright checks at `1440x900`, `1024x768`, and `390x844`.
- `uv run python scripts/check_docs.py`.

## CR-100 - Operations Home Dense Visual Composition

Date: 2026-06-22

Source: user feedback after the CR-099 pass that the dashboard still felt too
empty even after legends, icons, and palette roles were corrected.

Module: monitor web frontend dashboard surface, responsive CSS, and
dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-099 made the Operations Home easier to decode, but the current
desktop/tablet layout still stretched sparse data into large white panels. The
next pass needed to make the same data feel denser without adding prose,
tables, or invented metrics.

Purpose:

Reduce empty visual surface on the current `/monitor` Operations Home by making
the layout content-sized and by giving the main flow chart a denser graphical
substrate.

Requirements:

- Keep the current dashboard data contract, role boundaries, drilldowns, and
  one-screen maximum height boundary.
- Prefer content-sized dashboard composition over viewport-filling empty
  panels when real data is sparse.
- Keep the first screen chart-first and low-text.
- Add denser visual structure to the flow chart without changing its meaning or
  inventing new backend fields.
- Preserve the current project design system rather than introducing a detached
  prototype style.

Scope boundary:

- Frontend-only refinement of the existing `/monitor` Operations Home.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.

Non-goals:

- Do not add new dashboard metrics that require backend changes.
- Do not reintroduce long descriptive copy, tables, or status walls to fill
  space.
- Do not reopen CR-099 as incomplete; CR-100 is a follow-up refinement.

Related tasks:

- CR-100 Operations Home Dense Visual Composition in `TASKS.md`
- CR-100 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- Desktop/tablet Operations Home reads denser and less vacant with the same
  underlying data.
- The flow chart uses a fuller graphical substrate rather than leaving a large
  empty center field.
- Sparse states still stay compact, chart-first, and visually intentional.
- Desktop/tablet remain within the left navigation/shell height boundary, and
  mobile remains readable without horizontal overflow.
- Existing role gating, drilldowns, and dashboard compatibility still pass
  regression tests.

Tests:

- CR-100 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/Playwright checks at `1440x900`, `1024x768`, and `390x844`.
- `uv run python scripts/check_docs.py`.

## CR-101 - Operations Home Flow Chart Layer Separation

Date: 2026-06-22

Source: user in-app browser review of the current `/monitor` Operations Home
flow chart after CR-100.

Module: monitor web frontend dashboard surface, flow-chart structure, and
dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-100 made the Operations Home denser, but the user review on the live page
found that the `流程总览` card still read as one mixed block. The problem was
not the outer card radius itself. The issue was that title, legend, backdrop,
connector line, and stage nodes sat too close in one visual layer, so the
chart did not read like a separated plot area.

Purpose:

Keep the current dashboard data contract and one-screen shell boundary, but
separate the flow chart into clearer internal layers so the chart reads as a
proper visual surface instead of a stacked mixed block.

Requirements:

- Keep the current dashboard data contract, role boundaries, drilldowns, and
  one-screen maximum height boundary.
- Keep the existing modest radius system and current project design language;
  do not switch the flow chart to a detached prototype style.
- Split the flow chart into a clear head layer and a separate internal plot
  area.
- Weaken the background stage columns so they behave as substrate rather than
  competing cards.
- Raise stage nodes as the foreground layer so labels, counts, and pending
  state are visually legible.
- Do not add prose, tables, or new backend metrics to explain the chart.

Scope boundary:

- Frontend-only refinement of the existing `/monitor` Operations Home flow
  chart.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.

Non-goals:

- Do not redesign the rest of Operations Home.
- Do not change the platform/resource/attention cards as part of this follow-up.
- Do not reopen CR-100 as incomplete; CR-101 is a follow-up refinement after
  live browser review.

Related tasks:

- CR-101 Operations Home Flow Chart Layer Separation in `TASKS.md`
- CR-101 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The flow chart head and plot area are visibly separated inside the existing
  Operations Home card.
- Stage backdrop columns read as low-noise substrate rather than competing
  mini-cards.
- Stage nodes read as foreground data markers and no longer feel visually
  mixed into the same layer as the backdrop.
- Desktop/tablet remain within the left navigation/shell height boundary, and
  mobile remains readable without horizontal overflow.
- Existing role gating, drilldowns, and dashboard compatibility still pass
  regression tests.

Tests:

- CR-101 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/in-app checks at desktop review width plus shell-height boundary
  confirmation.
- `uv run python scripts/check_docs.py`.

## CR-102 - Operations Home Flow Chart Node Simplification

Date: 2026-06-22

Source: user live review of the current `/monitor` Operations Home after
CR-101.

Module: monitor web frontend dashboard surface, flow-chart node composition,
and dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-101 separated the `流程总览` chart into a head layer and plot area, but the
live review still showed the stage nodes reading as crowded mini-compositions.
The issue shifted from plot layering to node density: each stage still carried
label, value, helper text, ring, backdrop, and bar in too small a space.

Purpose:

Keep the same dashboard data contract and one-screen shell boundary, but reduce
the node payload so the flow chart reads faster: label first, number second,
pending state as a small chip, and one compact state bar.

Requirements:

- Keep the current dashboard data contract, role boundaries, drilldowns, and
  one-screen maximum height boundary.
- Do not add prose, tables, extra legends, or new backend metrics.
- Remove the always-visible stage helper line such as `进行中` or `6 待处理`
  from the node body.
- Keep pending state visible only as a compact numeric chip when it exists.
- Tighten node spacing, orb size, line placement, and bar height so the chart
  reads as one coherent visual block instead of five crowded mini-cards.

Scope boundary:

- Frontend-only refinement of the existing `/monitor` Operations Home flow
  chart.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.

Non-goals:

- Do not redesign the rest of Operations Home.
- Do not replace the current light enterprise design language with a detached
  prototype style.
- Do not reopen CR-101 as incomplete; CR-102 is the next follow-up refinement
  after live browser review.

Related tasks:

- CR-102 Operations Home Flow Chart Node Simplification in `TASKS.md`
- CR-102 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The `流程总览` node body no longer contains a separate helper text row.
- Pending state remains visible through a compact chip only when non-zero.
- Desktop/tablet remain within the left navigation/shell height boundary, and
  mobile remains readable without horizontal overflow.
- Existing role gating, drilldowns, and dashboard compatibility still pass
  regression tests.

Tests:

- CR-102 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/in-app checks at desktop review width plus shell-height boundary
  confirmation.
- `uv run python scripts/check_docs.py`.

## CR-103 - Operations Home Flow Chart Semantic Trend Rebuild

Date: 2026-06-22

Source: user live review of the current `/monitor` Operations Home after
CR-102 and explicit request to make `流程总览` readable as a line-chart-style
view of monitoring status.

Module: monitor web frontend dashboard surface, flow-chart semantic rendering,
and dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-101 and CR-102 reduced layering noise and node density, but the live page
still read as several mixed mini-components inside one frame. The chart had
card, connector, orb, bar, and chip semantics at the same time, so the user
could not tell what the block was meant to say at a glance.

Purpose:

Keep the existing dashboard data contract and one-screen boundary, but rebuild
`流程总览` as a single semantic monitoring-stage trend chart: one primary line
for total stage volume and one secondary line for abnormal or pending load,
with the five monitoring stages as the fixed x-axis.

Requirements:

- Keep the current dashboard data contract, role boundaries, drilldowns, and
  one-screen maximum height boundary.
- Do not add backend fields, pseudo historical time-series data, prose-heavy
  explanations, or detached prototype styling.
- Rebuild the chart so it reads as one chart instead of five mixed node cards.
- Keep the visible legend explicit for `总量` and `异常 / 待处理`.
- Keep the five stage labels and key values readable with minimal text.
- Preserve current project design language, colors, typography, and overall
  `/monitor` layout conventions.

Scope boundary:

- Frontend-only refinement of the existing `/monitor` Operations Home flow
  chart.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.

Non-goals:

- Do not claim a real historical time-series view where the current data layer
  only provides current-stage aggregates.
- Do not redesign the rest of Operations Home.
- Do not reopen CR-101 or CR-102 as incomplete; CR-103 is the next semantic
  follow-up after live browser review.

Related tasks:

- CR-103 Operations Home Flow Chart Semantic Trend Rebuild in `TASKS.md`
- CR-103 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The `流程总览` card reads as a single chart-first monitoring-stage view.
- The chart keeps an explicit visible legend for `总量` and `异常 / 待处理`.
- The chart no longer presents each stage as an orb-plus-bar mini-card.
- Desktop/tablet remain within the left navigation/shell height boundary, and
  mobile remains readable without horizontal overflow.
- Existing role gating, drilldowns, and dashboard compatibility still pass
  regression tests.

Tests:

- CR-103 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/in-app checks at desktop review width plus shell-height boundary
  confirmation.
- `uv run python scripts/check_docs.py`.

## CR-104 - Operations Home Data Cockpit Moderate Rebuild

Date: 2026-06-22

Source: approved implementation plan to rebuild `/monitor` into a single-screen
data cockpit after repeated live review showed the current overview still felt
like a mixed status platter instead of a readable operations dashboard.

Module: monitor web frontend dashboard surface, chart-first overview
composition, and dashboard-focused regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-097 through CR-103 reduced wording, clarified legends, and improved the
main flow card, but the first screen still relied on several legacy visual
patterns at once. The user wanted a more direct reading path: first see
trend, then see problems, then see breakdowns. The page also needed to stay
inside the left-shell height at desktop, use the current project design
language, and avoid table-like or prose-heavy explanation blocks.

Purpose:

Keep the existing dashboard data contract, role boundaries, and drilldown
targets, but rebuild the current Operations Home into a chart-first data
cockpit: compact KPI strip, `监控走势` trend chart with 7/14 day switch,
`问题分布` issue bars, lower `平台分布` and `交付 / 复核` breakdowns, and
administrator-only compact resource/diagnostic entry.

Requirements:

- Keep `/api/monitor/dashboard` compatible and do not add backend fields.
- Add a frontend overview view-model that unifies `operations_home` and the
  existing KPI container.
- If the dashboard payload does not expose time buckets, use read-only
  frontend aggregation from `/runs` and `/reports` for 7-day and 14-day
  trend buckets.
- Desktop first viewport must stay inside the left navigation/shell height.
- Reduce text and remove stage-node/card mixtures in favor of direct chart
  shapes, legends, numbers, and short labels.
- Keep existing drilldowns to Monitoring, Task Center, resource pages, and
  System Diagnostics.
- Show compact administrator-only resource health entry; normal users must not
  keep a blank resource block.

Scope boundary:

- Frontend-only rebuild of the existing `/monitor` Operations Home.
- No backend API, schema, permission, crawler, AI, email, deployment, Task
  Center, Run Detail, drawer, modal, enhanced select/date, routing,
  owner-scope, or report-scope behavior change is part of this CR.

Non-goals:

- Do not expand this work to other first-level pages.
- Do not invent new persistent dashboard fields or change database schema.
- Do not reopen CR-097 through CR-103 as incomplete; CR-104 is the next
  accepted follow-up optimization.

Related tasks:

- CR-104 Operations Home Data Cockpit Moderate Rebuild in `TASKS.md`
- CR-104 tests in `TEST_PLAN.md`
- Operations Home implementation and responsive CSS in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`

Acceptance:

- The first screen reads as a chart-first data cockpit instead of status-card
  mixture.
- `监控走势` shows visible legend and 7/14 day switch with either payload
  buckets or read-only frontend aggregation.
- `问题分布` answers what needs action now with compact horizontal issue bars.
- Desktop/tablet stay within the left navigation/shell height boundary, mobile
  stays readable without horizontal overflow or deformed charts.
- Existing role gating, drilldowns, and dashboard compatibility still pass
  regression tests.

Tests:

- CR-104 operations home tests in `TEST_PLAN.md`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`.
- `node --check api/webui/monitor/monitor.js`.
- Inline monitor script parse from `api/monitor_web/index.html`.
- Browser/in-app checks at `1440x900`, `1024x768`, and `390x844`.
- `uv run python scripts/check_docs.py`.

Current follow-up:

- CR-105 is the current implemented and verified Operations Home ECharts
  baseline. CR-097 through CR-104 are verified historical predecessors.
- The CR-097 no-chart-dependency constraint and CR-101 through CR-103
  `流程总览` / `operations-stage-*` DOM expectations are historical verification
  only. They do not constrain the current ECharts implementation.

## CR-105 - Operations Home ECharts Dashboard Rebaseline

Date: 2026-06-22

Source: user request for a chart-style Operations Home dashboard plan covering
color, visualization types, layout, container sizing, current and future
monitoring-task data, responsiveness, legends, component-library choice,
viewport UX, interactions, goals, acceptance, and cleanup of stale duplicate
requirements that would affect the redesign.

Module: monitor web frontend dashboard surface, visualization system,
dashboard requirement baseline, and dashboard-specific regression tests

Type: Existing Feature Optimization

Status: Verified

Background:

CR-097 through CR-104 iterated the Operations Home from a text-heavy overview
into the current CR-104 chart-first data cockpit. The remaining issue is that
the page still relies on handcrafted card/SVG fragments and carries historical
requirements for earlier flow-chart attempts. Those requirements can mislead a
future implementation into preserving old `流程总览` or `operations-stage-*`
structures even though the accepted direction is now a cleaner chart-library
dashboard.

Purpose:

Rebaseline the Operations Home around a true chart dashboard: KPI strip,
trend chart, issue distribution, platform breakdown, delivery/review
composition, and administrator-only resource health. The goal is a readable
public-opinion monitoring instrument panel, not a status-card platter or a
diagram of previous implementation stages.

The page has one product goal: help the user decide within about 10 seconds
whether today's monitoring operation is normal, where the risk is, and where
to click next. The intended reading path is:

```text
overall state -> recent trend -> problems to handle -> source platform or
workflow link -> destination for action
```

Requirements:

- Keep `/api/monitor/dashboard` compatible and preserve the current
  `operations_home` data contract where possible.
- Treat CR-104 as the implementation baseline and CR-097 through CR-103 as
  historical/archive-only design iterations, not current DOM or visual
  constraints.
- Use Apache ECharts for the core CR-105 dashboard charts in the current
  no-build `/monitor` dashboard. It must be vendored locally under the
  existing static asset path, not loaded from a CDN. The expected local vendor
  file is `api/webui/monitor/vendor/echarts.min.js`, referenced by `/monitor`
  through `/static/monitor/vendor/echarts.min.js`.
- Do not continue handcrafted SVG path geometry or custom DOM chart layout
  calculations for the core CR-105 charts. `监控走势`, `问题分布`, `平台分布`,
  and `交付 / 复核` should be rendered by ECharts chart instances. The current
  CR-104 `operationsTrendLinePath()`, `operationsTrendAreaPath()`, and
  `.operations-trend-svg` fragments are the baseline to replace, not the
  pattern to continue. SVG icons and ECharts internal SVG/canvas rendering are
  allowed; the boundary is application-layer chart geometry for dashboard
  charts.
- Keep administrator and normal-user views different:
  - administrators see workspace-wide operations, resource health, and system
    exceptions;
  - normal users see only their own tasks, reports, leads, and delivery status;
  - normal users must not see account, proxy, AI, SMTP, session, or other
    administrator resource details.
- First implementation should reuse existing data before adding backend fields:
  tasks total/enabled/paused/attention, today's runs/running/failed/skipped
  and platform distribution, report total/generated/pending review, email sent
  / failed / unsent, suspected negative and high-risk leads, pending manual
  review, and administrator-only account/proxy/AI/session/SMTP health.
- 7/14-day trend buckets may be derived by the frontend from existing `/runs`
  and `/reports` data when the dashboard payload lacks buckets. A 30-day
  window is an accepted interaction target and should also use bounded
  frontend read-only aggregation when existing paginated data can support it
  without excessive requests. If that cannot be done cleanly in the first
  CR-105 implementation, keep the first shipped controls to 7/14 days and
  defer backend-provided 30-day buckets to a later accepted CR instead of
  adding new backend fields opportunistically.
- Future enhancement data is explicitly deferred: task funnel, platform risk
  matrix, keyword heat, AI quality metrics, and task ranking by high risk,
  failures, or mail failures. These must not be invented as persisted metrics
  to fill the first CR-105 screen, and the frontend must not render placeholder
  "future" panels for those deferred enhancements.
- Use the restrained ToB operations color ledger:
  - background `#F6F8FA`;
  - cards `#FFFFFF`;
  - teal `#0F766E` for normal/completed/business-total signals;
  - blue `#2563EB` for running/realtime/platform-comparison signals;
  - amber `#D97706` for pending review or pending action;
  - red `#DC2626` for failure/exception;
  - dark red `#991B1B` for high-risk public-opinion leads;
  - neutral gray `#64748B` and `#CBD5E1` for context, borders, and muted text.
  Platform category colors may appear only inside the platform distribution
  module and must not override the page-wide semantic color meaning.
- Use six stable first-screen modules:
  - KPI strip: five equal metric cards for tasks, runs, reports, mail, and
    leads, with small bar/spark treatment.
  - Monitoring trend: dual-line or line-plus-area chart for business volume
    and exception/pending volume across 7/14 days, with 30 days only when
    bounded frontend aggregation from existing data remains clean.
  - Issue distribution: horizontal bars for run failure, mail failure,
    pending review, high risk, and resource exceptions.
  - Platform distribution: horizontal bars with optional donut only when useful
    for Douyin, Xiaohongshu, Kuaishou, Weibo, Bilibili, and other platform
    buckets. Do not default to heatmap blocks unless platform count and data
    density justify them.
  - Delivery / review: stacked bars for report, mail, and review status across
    completed, pending, and exceptional states.
  - Resource health: compact segmented bars for accounts, proxies, AI, and
    SMTP/session health; administrator-only and hidden without an empty hole
    for normal users.
- Desktop layout at `>=1280px` should use:
  - KPI strip as five equal columns, about `64px - 76px` high;
  - trend and issue distribution in a `65% / 35%` row, about `280px - 320px`
    high;
  - platform distribution, delivery/review, and resource health in three
    equal lower columns, about `180px - 220px` high;
  - card radius `8px`, card padding `12px - 16px`, and chart title regions
    about `32px` high.
- Align every dashboard module as a strict grid, not as independent floating
  cards. Card outer edges, row gutters, title regions, headline numbers,
  legends, direct labels, chart plot areas, and bottom-module heights should
  line up within each row. KPI cards should align their label, value, and
  micro-chart positions across all five cards. When `资源健康` is hidden for
  normal users, the remaining lower modules must reflow on the same grid
  without a blank slot or uneven gutter. The dashboard should align with the
  existing console shell width, not introduce marketing-page whitespace.
- Tablet `768px - 1279px` should allow KPI `5` columns or `3+2`, make the
  main trend full width, and use one- or two-column lower sections. Mobile
  `<768px` should use two-column KPI cards, trend first at about
  `220px - 260px`, then issue distribution, platform distribution,
  delivery/review, and administrator-only resource health.
- When normal-user views hide `资源健康`, the remaining lower modules should
  reflow to fill available width, normally as two equal columns on desktop and
  a single column on narrower screens. Do not leave a blank third slot.
- Use chart types intentionally:
  - KPI cards with small bar/sparkline treatment for task, run, report, mail,
    and lead signals.
  - Dual-line or line-plus-area trend chart for 7/14-day business volume and
    exception/pending volume, with optional 30-day mode only when existing data
    can support bounded frontend aggregation.
  - Horizontal bar chart for issue distribution.
  - Horizontal bar or donut-plus-bar chart for platform distribution.
  - Stacked bar chart for report delivery, mail delivery, and review state.
  - Compact segmented bars for administrator resource health.
  - Future optional heatmap or matrix only when task/platform/risk data
    density makes it meaningful.
- Keep essential values, legends, and direct labels visible without hover.
  Tooltips may add detail but cannot be the only way to read the chart.
- Mobile has no hover dependency: chart points and bars must support tap/click
  detail, legends should be visible, and horizontal bars should link to the
  relevant filtered Task Center, run-record, Run Detail, or resource page.
- Basic interactions should include time-window switching for 7/14 days, 30-day
  switching when supported by bounded existing-data aggregation, KPI
  click-throughs, issue-bar click-throughs, platform-bar click-throughs,
  high-risk/pending-review drilldowns, and tooltips that explain value/date/
  status without hiding the core value.
- Loading, empty, stale, and error states must keep container dimensions
  stable. Empty charts should render zero-value chart surfaces instead of long
  prose; stale views show last-updated time; one chart failure must not blank
  the rest of the dashboard.
- Keep ordinary users scoped to their own tasks/runs/reports/leads and hide
  administrator resource details without leaving a blank panel.
- Preserve existing drilldowns to Monitoring, Task Center grouped view, Task
  Center run records, Run Detail, resource pages, and System Diagnostics.
- Preserve Task Center, Run Detail, drawer, modal, enhanced select/date,
  routing, owner-scope, report-scope, and top-bar refresh behavior.
- Keep desktop and tablet dashboard content inside the shell/navigation height
  where practical, and keep mobile chart-first without horizontal overflow.

Scope boundary:

- In scope: Operations Home requirements, visualization plan, dependency
  decision, current `/monitor` dashboard DOM/CSS/JS implementation when the
  implementation batch starts, and dashboard-specific tests.
- Out of scope: backend schema changes, new persistent dashboard fields,
  `/monitor-next`, replacing the console shell, changing Task Center or Run
  Detail behavior, changing permissions, crawler behavior, AI provider logic,
  report generation, or email delivery behavior.

Non-goals:

- Do not preserve earlier `流程总览`, `operations-stage-*`, heatmap-block, or
  no-chart-library constraints merely because they appeared in CR-097 through
  CR-103.
- Do not continue using a process-node diagram as the main dashboard chart.
  The earlier flow/stage diagram repeatedly read as stitched mini-cards and is
  superseded by the CR-105 chart-dashboard structure.
- Do not add decorative charts that do not answer an operational question.
- Do not introduce React, Vue, a build pipeline, or a component framework for
  this current `/monitor` change.
- Do not invent new persisted metrics to fill visual space.

Related tasks:

- CR-105 Operations Home ECharts Dashboard Rebaseline in `TASKS.md`
- CR-105 tests in `TEST_PLAN.md`
- CR-105 row in `TRACEABILITY.md`
- ECharts dependency decision in `DECISIONS.md`

Acceptance:

- Documents clearly classify CR-097 through CR-104 as historical/archive-only
  predecessors and CR-105 as the current verified dashboard baseline.
- No current planning or test text requires preserving `流程总览` or
  `operations-stage-*` DOM for the current chart-library dashboard.
- The verified dashboard plan names the chart families, color roles,
  container hierarchy, responsive behavior, legends, interactions, component
  library, role boundaries, and non-goals.
- Implementation uses local ECharts for the core dashboard charts while
  preserving the dashboard API, role gating, drilldowns, and shell behavior.
  CR-105 acceptance should fail if the new core charts continue the CR-104
  handwritten `.operations-trend-svg` / path-calculation pattern instead of
  replacing it with chart-library rendering.
- The resulting first screen reads as a chart-type dashboard rather than a
  state-card collage; within about 10 seconds a user can answer whether today
  is normal, where the exception/risk is, and where to click next.
- All six modules align as one dashboard system: equal gutters, consistent
  title/header heights, aligned chart plot origins, aligned KPI internals, and
  equal-height lower cards on desktop. Browser review should fail visible card
  drift, staggered title baselines, mismatched plot starts, or lower modules
  that look uneven after the normal-user resource block is hidden.
- Desktop first viewport stays within the console shell height, while mobile
  has no horizontal scroll, no one-character Chinese text columns, and no
  chart labels squeezed into unreadable stacks.
- Normal users never see administrator resource details and do not see an
  empty placeholder where the resource-health module was hidden.
- Red is used only for exception/high-risk meaning, and platform category
  colors stay inside the platform distribution module.
- Key numbers, legends, and labels remain visible without hover.
- Documentation consistency passes after the rebaseline.

Tests:

- CR-105 operations home tests in `TEST_PLAN.md`.
- `uv run python scripts/check_docs.py`.
- During implementation: targeted operations-home static tests, JavaScript
  parse checks, browser checks at `1440x900`, `1024x768`, and `390x844`, and
  role checks for administrator and normal-user views.

## CR-106A - Operations Home Data-Aware Signal Refinement

Date: 2026-06-22

Source: user request to turn the post-CR-105A design/data review into a
documented optimization plan before any code changes, with plan cross
validation.

Module: monitor web frontend dashboard surface, Operations Home data mapping,
dashboard-specific UX rules, and dashboard plan verification

Type: Existing Feature Optimization

Status: Verified

Background:

CR-105A completed the ECharts dashboard rebaseline. A follow-up read-only
review against the current local dashboard data showed that the first screen
can be made more decisive without reopening CR-105A or adding new persisted
fields. The useful current signals include task/run/report counts, report-level
mail state, AI high-risk and pending-review counts, platform results in run
summaries, and administrator resource status.

Purpose:

Refine the Operations Home reading path so the first screen more directly
answers: whether today's monitoring is normal, where exception/high-risk or
pending work exists, and which existing destination the user should open next.

Requirements:

- Preserve CR-105A as the verified ECharts dashboard baseline. Do not reopen
  CR-105A, reintroduce CR-104 handcrafted chart geometry, or restore
  historical CR-097 through CR-103 flow-chart constraints.
- Keep the existing no-build `/monitor` frontend and locally vendored ECharts.
  Do not introduce React, Vue, a component framework, or remote chart assets.
- Do not add backend schema fields or new persisted dashboard metrics for
  CR-106A.
- Preserve `/api/monitor/dashboard` compatibility, role gating, drilldowns,
  Task Center, Run Detail, drawer, modal, enhanced select/date behavior,
  routing, owner-scope, report-scope, and top-bar refresh behavior.
- Add or document a read-only local data baseline for planning evidence. The
  observed local data sample is evidence of available signal types, not an
  acceptance constant; runtime counts can change.
- Refine the top Operations Home status so today's health is readable in one
  concise summary before the user decodes every chart.
- Make `问题分布` prioritize action severity over raw count when needed:
  high-risk leads, pending review, mail failure, then run failure/skip.
- Make `平台分布` distinguish platform volume from platform failure signals
  using existing run summary fields such as `platform_results` and
  `failed_platforms` when available.
- Clarify the `邮件` module's CR-106A data source as report-level delivery
  state from `reports.email_status`. Do not silently treat it as the complete
  delivery-attempt history.
- Make administrator `资源健康` more action-oriented while preserving the
  normal-user boundary. Administrators may see account, proxy, AI, mail, and
  session health cues; normal users must not see account/proxy/AI/SMTP/session
  details or an empty resource placeholder.
- Improve mobile first-screen density so KPI cards do not dominate before
  `监控走势` and `问题分布`.
- Keep red reserved for failure/exception/high-risk meaning; platform category
  colors remain confined to platform distribution.

Scope boundary:

- In scope: Operations Home view-model mapping from already available
  dashboard/runs/reports data, chart option semantics, copy/labels, role-safe
  resource-health presentation, mobile first-screen density, and related tests
  and docs.
- Out of scope: backend schema changes, new persisted fields, new task funnel
  or ranking metrics, 30-day backend trend buckets, Task Center/Run Detail
  behavior, permissions, crawler behavior, AI provider behavior, report
  generation, and email-delivery execution behavior.

Non-goals:

- Do not use local sample counts as hard product expectations.
- Do not fetch or display sensitive values such as recipients, SMTP secrets,
  proxy URLs, cookies, profile paths, account names, or raw error details on
  Operations Home.
- Do not make `email_delivery_logs` the source of the Operations Home mail
  health in CR-106A. That candidate is tracked separately by CR-106B.

Related tasks:

- CR-106A Operations Home Data-Aware Signal Refinement in `TASKS.md`.
- CR-106A tests in `TEST_PLAN.md`.
- CR-106A row in `TRACEABILITY.md`.
- CR-106A frontend/data-source notes in `FRONTEND_ARCHITECTURE.md` and
  `UI_UX_GUIDELINES.md`.

Acceptance:

- Documents keep CR-105A verified and identify CR-106A as a follow-up
  optimization rather than a rewrite or reopened baseline.
- CR-106A implementation can proceed without guessing whether
  `email_delivery_logs` belongs in the dashboard payload.
- The plan states exactly which existing data sources are in scope and which
  mail-delivery aggregation choice is pending.
- Dashboard data-source tests verify `问题分布`, `平台分布`, and `邮件` use only
  dashboard/runs/reports data; `email_delivery_logs` queries belong to
  CR-106B.
- The `邮件` module displays report-level state from `reports.email_status`;
  any use of `email_delivery_logs` aggregation is a CR-106B scope violation.
- Browser checks for normal-user sessions confirm `资源健康` is not rendered,
  lower modules reflow without empty placeholders, and no administrator
  resource terms appear in Operations Home copy.
- Implementation tests use bounded fixtures or safe aggregates. They must not
  hard-code local sample counts as product acceptance constants.
- The plan protects normal-user role boundaries and existing Task Center/Run
  Detail/overlay behavior.
- Plan validation and documentation consistency checks pass before code work
  begins.

Tests:

- CR-106A Operations Home tests in `TEST_PLAN.md`.
- `uv run python scripts/check_docs.py`.
- During implementation: targeted operations-home static tests, JavaScript
  parse checks, inline monitor script parse, browser checks at `1440x900`,
  `1024x768`, and `390x844`, and administrator/normal-user role checks.

## CR-106B - Email Delivery Log Dashboard Aggregation

Date: 2026-06-22

Source: follow-up from CR-106A planning after read-only local data review found
that report-level `reports.email_status` and detailed `email_delivery_logs`
can tell different stories.

Module: Operations Home mail-health aggregation and dashboard data contract

Type: Existing Feature Optimization

Status: Needs Confirmation

Background:

The schema already contains `email_delivery_logs`, and Run Detail/report
delivery history can use those records. However, CR-105A and CR-106A keep the
Operations Home mail module on the existing report-level dashboard contract.
Aggregating `email_delivery_logs` into `/api/monitor/dashboard` would not
require a new schema field, but it would be a backend aggregation and product
semantics change.

Purpose:

If accepted later, make Operations Home mail health reflect true delivery
attempt history while preserving the current report-level status as a
compatible signal.

Candidate requirements pending confirmation:

- Aggregate existing `email_delivery_logs` into Operations Home mail-health
  counts with the same workspace/owner scope rules as reports.
- Preserve report-level `reports.email_status` compatibility and label the two
  sources clearly enough for operators to diagnose discrepancies.
- Do not expose recipients, SMTP secrets, proxy URLs, cookies, profile paths,
  account details, or raw sensitive error text in Operations Home.
- Keep normal-user scope filtering consistent with existing report ownership.
- Add tests proving the aggregation uses safe counts/statuses only and does not
  leak delivery-history sensitive fields.

Scope boundary:

- Not part of CR-106A implementation.
- Requires explicit acceptance before code or dashboard-data contract changes.

Acceptance:

- This CR remains `Needs Confirmation` until the user accepts the dashboard
  mail-health source change.
- Current-state documentation must not describe CR-106B as ready to start or
  unblocked while it still needs confirmation.

## CR-086 - Explanatory Helper Copy Tooltip Consolidation

Date: 2026-06-20

Source: user in-app browser review of formal console helper text density

Module: formal console page headers, resource lists, form fields, and overlay
helper copy

Type: Existing Feature Optimization

Status: Verified

Background:

Several formal console pages still showed explanatory helper sentences directly
inside table cells, panel headers, form fields, or overlay action areas. The
copy was useful, but always-visible small text made dense resource pages feel
crowded and could widen columns or make mobile layouts harder to scan.

Purpose:

Keep the original explanatory meaning available while reducing visual noise:
move targeted helper copy into a uniform small question-mark affordance beside
the relevant title, label, or field.

Requirements:

- Replace targeted always-visible helper sentences with a consistent `?`
  helper icon next to the related label/title/section heading.
- The helper icon should use one neutral gray style, about `16x16px`, and be
  usable by hover, keyboard focus, and click/focus on touch devices.
- Tooltip content should preserve the original helper copy, including long or
  multiline text where needed.
- Apply the first accepted pass to the selectors and actual DOM surfaces raised
  by the user: account platform/login hints, selected account-list helper
  cells, account completion copy, proxy/AI/rule/template/Task Center list
  headers, the Monitoring collection-rule help, and equivalent verified helper
  text in those surfaces.
- Keep status values, actual data, empty states, warnings, errors, and action
  feedback visible when they are operational state rather than explanatory
  helper copy.

Scope boundary:

- Frontend-only visual-density optimization for the formal `/monitor` console.
- No backend API, database, permission, crawler, AI-provider, SMTP, scheduler,
  deployment, owner-scope, or report-scope changes.
- No change to Task Center information architecture, Run Detail six sections,
  drawer/modal/floating-menu workflow categories, `.drawer-scroll-body`, close
  behavior, enhanced select behavior, or date-picker behavior.

Non-goals:

- Do not remove fields, buttons, filters, row actions, batch actions, downloads,
  copy actions, refresh actions, confirmations, or save/test flows.
- Do not hide operational state such as errors, warnings, empty states, status
  labels, test results, or loading feedback inside tooltips.
- Do not introduce a new frontend framework, component library, or build step.

Related tasks:

- CR-086 Explanatory Helper Copy Tooltip Consolidation in `TASKS.md`
- CR-086 Helper Tooltip Consolidation Tests in `TEST_PLAN.md`
- Phase 21 visual refinement preservation rules in
  `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md`

Acceptance:

- Targeted explanatory helper text no longer appears as always-visible small
  copy in the affected headers, fields, table cells, and action-helper areas.
- The same text remains reachable from a consistent `?` tooltip adjacent to the
  related label/title/field.
- Browser checks confirm representative tooltips open on hover/focus/click and
  do not create console errors, horizontal overflow, one-character Chinese text
  columns, or overlay scroll regressions.
- Task Center, Run Detail, enhanced selects/date pickers, drawer/modal close
  behavior, `.drawer-scroll-body`, top-bar refresh, owner/report scope, and all
  listed actions remain unchanged.

Verification:

- Verified on 2026-06-20 with static regression coverage, syntax checks, docs
  consistency, and in-app browser checks at desktop, tablet, and mobile widths.
  Targeted helper copy now lives behind consistent `?` tooltips, while
  operational state text remains visible and Task Center, Run Detail,
  enhanced selects/date pickers, `.drawer-scroll-body`, close behavior, and
  top-bar refresh semantics are preserved.

Superseded by:

- CR-087 removes the `?` tooltip affordance after user acceptance review found
  that the question marks themselves still added visual noise. CR-086 remains a
  historical verified attempt and is not the current UI rule.

## CR-087 - Explanatory Helper Tooltip Removal

Date: 2026-06-20

Source: user in-app browser acceptance review after CR-086

Module: formal console page headers, resource lists, form fields, account
cells, Task Center, and representative overlays

Type: Existing Feature Optimization

Status: Verified

Background:

CR-086 moved explanatory helper copy from visible small text into `?` tooltips.
During acceptance review, the user clarified that the question-mark affordances
should also be removed and the removed small helper copy should not be restored.

Purpose:

Reduce dense-formal-console visual noise further: remove the helper-tooltip
question marks entirely while keeping operational state, data, errors, loading,
empty states, fields, buttons, and actions visible.

Requirements:

- Remove the `?` helper tooltip markup, CSS, and JavaScript behavior from the
  formal `/monitor` console.
- Do not restore the explanatory small helper sentences that CR-086 had moved
  into tooltips.
- Keep operational state text visible when it represents real data, validation,
  errors, warnings, empty/loading feedback, counts, login prompts, password
  status, or action feedback.
- Preserve page headers, labels, fields, filters, buttons, tables, row actions,
  batch actions, downloads, copy actions, refresh actions, save/test flows, and
  destructive confirmations.

Scope boundary:

- Frontend-only visual-density follow-up to CR-086 and Phase 21.
- No backend API, database, permission, crawler, AI-provider, SMTP, scheduler,
  deployment, owner-scope, or report-scope changes.
- No change to Task Center information architecture, Run Detail six sections,
  enhanced select/date behavior, drawer/modal/floating-menu workflow
  categories, `.drawer-scroll-body`, close behavior, or top-bar refresh.

Non-goals:

- Do not replace the `?` affordance with another icon or hidden tooltip system
  for the removed helper copy.
- Do not remove real operational explanations that are part of current action
  feedback, error recovery, empty states, or safety guardrails.
- Do not rewrite completed Phase 21 or CR-086 historical records as incomplete.

Related tasks:

- CR-087 Explanatory Helper Tooltip Removal in `TASKS.md`
- CR-087 Helper Tooltip Removal Regression Tests in `TEST_PLAN.md`
- CR-086 Explanatory Helper Copy Tooltip Consolidation as the superseded
  historical attempt

Acceptance:

- No `.helper-tooltip`, `data-tooltip`, `helperTooltip`, helper open/close
  handlers, or helper-specific CSS remains in the formal frontend.
- The targeted explanatory helper copy removed in CR-086 does not return as
  visible `.small`, `.inline-help`, field hint, header paragraph, or tooltip
  content.
- Operational state and required actions remain visible and reachable.
- Task Center, Run Detail six sections, enhanced selects/date pickers,
  drawer/modal close behavior, `.drawer-scroll-body`, top-bar refresh,
  owner/report scope, and listed actions remain unchanged.

## CR-088 - AI Rule Modal Residual Helper Text Removal

Date: 2026-06-20

Source: user in-app browser follow-up on the `AI 评估规则` modal after CR-087.

Module: formal console AI rule modal, result panel copy

Type: Existing Feature Optimization

Status: Verified

Background:

After CR-087 removed helper-tooltips and their restored explanatory copy, the
`AI 评估规则` modal still retained a few always-visible explanatory sentences:
the `AI 状态` line, the old prompt-load notice, and the default result hint.
Those lines were harmless but still made the modal feel busier than needed.

Purpose:

Remove the remaining always-visible explanatory helper text from the AI rule
modal so the rule editor reads as a compact edit-and-test surface while keeping
the rule fields, sample inputs, test button, save button, and test result area.

Requirements:

- Remove the `AI 状态` explanatory line from the rule modal.
- Remove the old prompt-load notice shown when a legacy prompt is parsed.
- Clear the default empty result hint so the result panel starts visually empty
  until a test is run.
- Preserve the existing rule sections, sample inputs, test action, save action,
  and result rendering behavior.

Scope boundary:

- Frontend-only visual-density cleanup for the accepted Phase 21 AI rule
  modal.
- No backend API, database, permission, crawler, AI-provider, SMTP, scheduler,
  deployment, Task Center, Run Detail, drawer, modal category, or enhanced
  select/date behavior changes.

Non-goals:

- Do not change rule semantics, test behavior, or save behavior.
- Do not add new helper icons, tooltips, or alternate explanation surfaces.
- Do not change the result payload shown after a real test.

Related tasks:

- CR-087 Explanatory Helper Tooltip Removal in `TASKS.md`
- CR-087 Helper Tooltip Removal Regression Tests in `TEST_PLAN.md`
- Phase 21 visual-density rules in `UI_UX_GUIDELINES.md`

Acceptance:

- The `AI 评估规则` modal no longer shows the `AI 状态` helper sentence.
- The modal no longer shows the legacy-prompt notice or the default empty
  result hint.
- Rule configuration, sample inputs, test action, save action, and rendered
  test output remain intact.
- Browser checks at desktop, tablet, and mobile widths show the modal is still
  reachable and the table/layout does not re-expand because of the removed
  helper text.

Verification:

- Verified on 2026-06-20 with targeted frontend regression coverage, inline
  script parse, docs consistency, and in-app browser checks at desktop,
  tablet, and mobile widths.

## CR-089 - Mail Template Row Helper Text And Update-Time Compactness

Date: 2026-06-20

Source: user in-app browser follow-up on the `邮件模板` table after CR-088.

Module: formal console mail template list

Type: Existing Feature Optimization

Status: Verified

Background:

The mail template list still showed a row-level helper sentence under the
template name, and the `更新时间` cell used a taller timestamp style than the
compact AI rule update-time treatment. Both details made the table feel wider
and busier than the surrounding Phase 21 surfaces.

Purpose:

Trim the mail template list by removing the redundant row helper sentence and
reusing the compact update-time treatment so the table stays dense without
changing the available actions, template workflow, or placeholder guardrail.

Requirements:

- Remove the visible `正文占位符已保留` helper sentence from the mail template
  row.
- Keep the body-placeholder guardrail logic in the editor intact.
- Make the `更新时间` cell use a compact, wrap-safe treatment aligned with the
  AI rule update-time display so the table does not widen because of long
  timestamps.
- Preserve add, refresh, view mail config, search/status filters, row edit,
  set current where available, delete, save, refresh preview, clear, close, and
  iframe preview.

Scope boundary:

- Frontend-only visual-density cleanup for the accepted Phase 21 mail template
  list.
- No backend API, database, permission, crawler, AI-provider, SMTP, scheduler,
  deployment, Task Center, Run Detail, drawer, modal category, or enhanced
  select/date behavior changes.

Non-goals:

- Do not remove the template placeholder guardrail or change save validation.
- Do not change template semantics, preview behavior, or delivery provenance.
- Do not add new help icons or restore the removed helper sentence elsewhere.

Related tasks:

- Phase 21J Mail Templates in `TASKS.md`
- CR-089 mail-template regression checks in `TEST_PLAN.md`
- Phase 21 visual-density rules in `UI_UX_GUIDELINES.md`

Acceptance:

- The mail template list no longer shows the `正文占位符已保留` row helper
  sentence.
- The `更新时间` cell stays compact and no longer widens the table.
- Template edit, preview, save, delete, and current-template behavior remain
  intact.
- Browser checks at desktop, tablet, and mobile widths show the mail template
  table remains readable without new overflow or one-character text columns.

Verification:

- Verified on 2026-06-20 with targeted frontend regression coverage, inline
  script parse, docs consistency, and live browser checks on the mail
  template page at desktop, tablet, and mobile widths.

## CR-090 - AI Rule List And Modal Field Width Compactness

Date: 2026-06-20

Source: user in-app browser follow-up on the `AI 评估规则` page after CR-088.

Module: formal console AI rule list and rule modal

Type: Existing Feature Optimization

Status: Verified

Background:

The AI rule list and its modal still read visually loose after the Phase 21H
compactness pass. The list table leaves too much white space in the test and
update-time columns, and the modal's internal field widths are not yet balanced
enough for a denser scan. The page feels wider than the surrounding Phase 21
surfaces even though the actions and rule workflow are already correct.

Purpose:

Tighten the AI rule list and modal field widths so the page reads as a compact
configuration surface without changing rule semantics, test behavior, or
available actions.

Requirements:

- Narrow the AI rule list's visual width so the `规则名称`, `最近测试`, and
  `更新时间` cells do not waste horizontal space.
- Keep `详情` and `更多` reachable and visible.
- Rebalance the rule modal's inner field widths so the basic info, rule
  configuration, schema, sample, and result areas feel more proportional.
- Preserve the existing rule fields, test action, save action, restore-default
  action, modal close behavior, and rendered test result behavior.

Scope boundary:

- Frontend-only visual-density cleanup for the accepted Phase 21 AI rule page.
- No backend API, database, permission, crawler, AI-provider, SMTP, scheduler,
  deployment, Task Center, Run Detail, drawer category, or enhanced
  select/date behavior changes.

Non-goals:

- Do not change rule semantics, sample semantics, or result payloads.
- Do not remove required actions or add new workflow controls.
- Do not change row action categories or open/close behavior.

Related tasks:

- Phase 21H AI Evaluation Rules in `TASKS.md`
- CR-090 AI rule width regression checks in `TEST_PLAN.md`
- Phase 21 visual-density rules in `UI_UX_GUIDELINES.md`

Acceptance:

- The AI rule table no longer feels overly wide at desktop.
- The rule modal keeps its existing sections and actions while reading more
  compactly.
- Browser checks at desktop, tablet, and mobile widths show the page remains
  readable without horizontal overflow or one-character text columns.

Verification:

- Verified on 2026-06-20 with targeted frontend regression coverage,
  `node --check api/webui/monitor/monitor.js`, `uv run python scripts/check_docs.py`,
  and live browser checks on `http://127.0.0.1:19221/monitor#ai_rules` at
  desktop, tablet, and mobile widths.
- The AI rule list now stays visually denser at desktop, and the rule modal
  uses a more balanced editor-versus-test split while preserving the existing
  sections, row actions, test/save/restore controls, close behavior,
  `.drawer-scroll-body`, and responsive single-column fallback below the
  desktop breakpoint.

## CR-055 - Task Center Status Column Visual Refinement

Date: 2026-06-18

Source: user in-app browser review of Task Center status column

Module: formal console Task Center run table

Type: Existing Feature Optimization

Status: Verified

Background:

After CR-054 shortened the status text, the Task Center status cell still
looked visually heavy because it reused the global `.status` pill treatment and
the table did not have a dedicated status-column class. This made the first-
level status cell feel like a status bar instead of a small lifecycle marker.

Purpose:

Keep the Task Center first-level table easy to scan: task/run identifiers remain
prominent, while status is a short, stable visual marker.

Requirements:

- The Task Center table helper must mark `状态` columns with a stable
  `col-status` class instead of relying on column position.
- The first-level run status badge must use Task Center-specific styling, not
  the global `.status` pill class.
- The badge should be visually compact with a small state dot and short label.
- The status column must stay narrow in grouped and flat modes.
- Existing grouping, field order, single `详情` action, Run Detail entry, and
  progress semantics must remain unchanged.

Scope boundary:

- Frontend-only visual refinement linked to CR-053 and CR-054.
- No backend API, data model, run lifecycle, AI trace, report, email, permission,
  or scheduler changes.

Non-goals:

- Do not redesign Task Center.
- Do not hide required run fields.
- Do not reintroduce report center or duplicate row actions.

Related tasks:

- CR-055 Task Center Status Column Visual Refinement in `TASKS.md`
- CR-054 Task Center Status Badge Compactness Regression Fix in `TASKS.md`

Acceptance:

- Status cells render as a narrow small badge, not a full-width or heavy pill.
- `任务 ID` / `运行 ID` keep priority before status in flat mode, while grouped
  mode keeps duplicated task identity hidden.
- Active progress remains a short helper line below the badge only when needed.
- Desktop, tablet, and mobile browser checks show no severe overlap, truncation,
  or hidden `详情` action caused by the status column.

Verification:

- Verified on 2026-06-18 with targeted frontend regression coverage, syntax
  checks, docs check, and browser inspection of the local `/monitor` page.
