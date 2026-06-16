# Implementation Tasks

Status legend:

- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[!]` blocked

## Phase 0 - Project Governance

- [x] Create project governance document set.
- [x] Add agent entry file.
- [x] Define documentation update mechanism.
- [x] Define UI/UX consistency rules.
- [x] Add menu-level product requirements.
- [x] Add change request intake document.
- [x] Add requirement/task/test traceability matrix.
- [x] Add detailed agent workflow document.
- [x] Add confirmation gate for ambiguous high-impact requirements.
- [x] Add roles and permissions specification.
- [x] Add account environment specification.
- [x] Add runtime settings specification.
- [x] Add target data model planning document.
- [x] Add permissions confirmation pack.
- [x] Add compatible schema migration plan.
- [x] Add `monitor.example.yaml`.
- [x] Add API authentication and authorization implementation guide.
- [x] Add server deployment and server-like validation guide.
- [x] Add documentation consistency check specification.
- [x] Add a documentation check script during Phase 1 close-out, after Phase
      0.5 schema foundation and basic auth/session implementation are verified.

## Phase 0.5 - Schema Foundation

Blocking prerequisite:

Phase 0.5 must be completed before starting Phase 1-9 implementation. Without
these tables and fields, authentication, permissions, workspace filtering,
runtime settings, and profile-key migration cannot function safely.

This phase is the required implementation foundation before full Phase 1 user
and permission work.

- [x] Create `workspaces`, `users`, `user_sessions`, `system_settings`, and
      minimal `audit_logs` tables.
- [x] Add `workspace_id`, `created_by`, and `updated_by` to priority business
      tables.
- [x] Add `profile_key` to `social_accounts` and `login_sessions`.
- [x] Add run-level timeout fields to `crawl_runs`: `timeout_seconds`,
      `deadline_at`, and `timeout_reason`.
- [x] Add account/profile lock fields to `social_accounts`.
- [x] Create `resource_locks` for proxy concurrency.
- [x] Backfill existing data into the default workspace with `workspace_id = 1`.
- [x] Keep old fields during the first migration step, but stop using
      `profile_path` as the identity for new account environments.
- [x] Verify existing tasks, accounts, runs, and reports still load after the
      schema foundation change.

## Phase 1 - Users And Permissions

- [x] Add user model.
- [x] Add role model with administrator and normal user.
- [x] Add workspace field to core business tables.
- [x] Add login/session flow.
- [x] Hide administrator-only menus from normal users.
- [x] Restrict normal users to their own workspace data.
- [x] Implement `scripts/check_docs.py` before closing Phase 1.

## Phase 2 - System Settings Center

- [x] Add runtime settings storage.
- [x] Add settings precedence: defaults, config file, database, environment lock.
- [x] Add runtime strategy page for administrators.
- [x] Add read-only deployment diagnostics.
- [x] Support configurable global concurrency, platform concurrency, timeouts,
      retries, QR timeout, session TTL, and retention days.
- [x] Treat `crawler_timeout_seconds` as a run-level wall-clock deadline for
      newly started runs.
- [x] Add `lock_cleanup_buffer_seconds` for stale-lock recovery.
- [x] Replace hard-coded global crawl semaphore with
      `global_crawl_concurrency` from runtime settings.
- [x] Replace hard-coded platform locks/concurrency with per-platform runtime
      settings.
- [x] Replace hard-coded scheduler tick interval with `scheduler_tick_seconds`.

## Phase 3 - Administrator Resource Center

- [x] Refine platform account pool page.
- [x] Refine proxy resource page.
- [x] Refine AI access page.
- [x] Refine mail configuration page.
- [x] Refine email template page.
- [x] Ensure all create/edit/test actions use consistent modal interactions.

## Phase 4 - Normal User Task Wizard

- [x] Replace complex task form for normal users with a simplified wizard.
- [x] Include law firm, aliases, platform search terms, platforms, frequency,
      crawl range, comments, and recipient emails.
- [x] Explain crawl range boundaries: max items is a cap, max pages is
      approximate, start page and time window depend on platform support.
- [x] Hide account, proxy, AI profile, template, and browser options from normal
      users.
- [x] Keep administrator advanced task settings available.

## Phase 5 - Account Environment

- [x] Add `profile_key` and runtime path resolver.
- [x] Stop exposing real profile paths in the customer-facing UI.
- [x] Create one profile per platform account.
- [x] Ensure account name is display-only and not the profile identity.
- [x] Add account lock.
- [x] Add profile lock.
- [x] Add proxy concurrency control.
- [x] Add startup and scheduler recovery for stale running runs and expired
      locks.
- [x] Ensure login and crawling use the same account proxy when configured.

## Phase 6 - Server Login Flow

- [x] Make server-side QR login the primary flow.
- [x] Return structured login states to the frontend.
- [x] Support waiting QR, waiting scan, waiting confirmation, success,
      verification required, QR failure, timeout, and platform error.
- [x] Persist profile after successful login.
- [x] Verify profile reuse after browser close.
- [x] Hide local-window login from production mode.

## Phase 7 - Runs, Reports, And AI

- [x] Ensure tasks run even when AI is missing.
- [x] Mark AI failures as manual-review leads.
- [x] Ensure tasks run and reports generate even when email is missing.
- [x] Keep report wording as suspected negative leads.
- [x] Verify report preview switches correctly across reports.
- [x] Ensure logs can be refreshed, copied, and downloaded.

## Phase 8 - Server-Like Validation

- [x] Add a container or server-like deployment path.
- [x] Verify the web QR/status login path is primary in the server-like
      environment with local-window login disabled.
- [x] Verify profile metadata persistence across service restart.
- [x] Verify multiple same-platform accounts use separate profiles.
- [x] Verify account/profile/proxy concurrency limits.
- [x] Verify no local Chrome is required for automated server-like
      validation.

## Phase 9 - Security And Operations

- [x] Add audit log for administrator operations.
- [x] Mask sensitive values in UI and logs.
- [x] Add backup notes for database, profiles, reports, and encryption key.
- [x] Add account invalidation alert path.
- [x] Add proxy error alert path.
- [x] Add disk and retention diagnostics.

## Phase 10 - Frontend Architecture And Technology Decision

Planning status:

Phase 10 is complete as a documentation and architecture decision phase. It did
not implement UI code changes.

- [x] Create and maintain `FRONTEND_ARCHITECTURE.md` as the frontend
      architecture source of truth.
- [x] Confirm the frontend stack before UI implementation.
- [x] Keep the accepted stack as Vanilla JavaScript plus CSS custom properties,
      with optional lightweight libraries only for focused charting or floating
      menu placement.
- [x] Keep the no-build deployment path unless a later CR changes it.
- [x] Update `AGENTS.md`, `AGENT_WORKFLOW.md`, and `scripts/check_docs.py` so
      agents discover `FRONTEND_ARCHITECTURE.md`.
- [x] Audit the current frontend file structure and decide the first redesign
      pass keeps `/monitor` as the entry while introducing local static CSS/JS
      module boundaries for Phase 11.

## Phase 10.5 - Phase 10-18 Global Plan Review Gate

Planning status:

Phase 10.5 is complete as a documentation-only review gate before Phase 11
implementation. It reviewed Phase 10-18 as one connected roadmap, not as
isolated phase readiness checks, and found no P0/P1 blockers after the
Phase 13, Phase 17, and Phase 18 granularity refinements.

- [x] Review whether Phase 10-18 as a whole can reach the final console goal:
      a task-loop-centered operations console covering task creation, runs,
      reports, and email delivery.
- [x] Review cross-phase dependencies and ordering, especially Phase 11 -> 12
      -> 13, Phase 14 -> 15, Phase 16 -> 17, and Phase 18 dependencies on
      frontend foundation and report snapshot data.
- [x] Review whether each phase and sub-phase has enough implementation
      granularity: clear files or data areas, allowed changes, forbidden
      changes, verification steps, and rollback path.
- [x] Review cross-phase impact risks: frontend module split, navigation
      rewrite, responsive behavior, run archive/noise fields, email delivery
      logs, report grouping, role visibility, and owner/workspace scope.
- [x] Review whether implementation batches protect existing core flows:
      login/logout, navigation, task wizard, run logs, report preview,
      account login, resource pages, modal behavior, and toasts.
- [x] Review whether data-model phases include compatible migration and
      backfill plans before frontend phases depend on new fields.
- [x] Record any accepted planning fixes in `TASKS.md`,
      `FRONTEND_ARCHITECTURE.md`, `TEST_PLAN.md`, `TRACEABILITY.md`, and
      `TEST_RESULTS.md` before generating a phase-specific execution goal.
- [x] Do not generate a Phase 11A-only execution goal until the global
      Phase 10-18 plan review has no P0/P1 blockers.

## Phase 11 - Frontend Design System

Planning status:

Phase 11 is planned and depends on Phase 10 and the completed Phase 10.5
global plan review gate. Do not implement Phase 11 as one large goal. Execute
it as Phase 11A-11D so each batch has a clear file boundary, verification
scope, and rollback path.

### Phase 11A - Frontend Module Boundary And CSS Token Layer

- [x] Create `api/webui/monitor/monitor.css`.
- [x] Create `api/webui/monitor/monitor.js`.
- [x] Reference the new local CSS/JS assets from `api/monitor_web/index.html`
      without removing existing inline CSS/JS.
- [x] Load `monitor.css` before the existing inline `<style>` block and load
      `monitor.js` after the existing inline `<script>` block.
- [x] Define CSS custom-property tokens for colors, typography, spacing,
      radius, shadows, z-index, status colors, and breakpoint values.
- [x] Use namespaced token variables such as `--color-*`, `--space-*`, and
      `--font-*`; do not define legacy aliases such as `--bg` or `--primary`
      in Phase 11A.
- [x] Keep `monitor.js` as a quiet module boundary with no console logging and
      no global variable/function definitions or UI behavior in Phase 11A.
- [x] Keep the visible UI unchanged in this batch.
- [x] Verify `/monitor` loads and the new CSS/JS assets return HTTP 200.
- [x] Verify login, navigation, task list, run center, and report preview still
      work through a browser smoke check.
- [x] Verify 1440px desktop, 1024px tablet, and 390px mobile layouts are
      unchanged.

### Phase 11B - Base Layout And Navigation Visual Foundation

- [x] Move base layout, shell, header, navigation, button, card, and toolbar
      styling into `monitor.css`.
- [x] Keep page structure and business data flow unchanged.
- [x] Apply the accepted Apple-style visual foundation to desktop layout and
      navigation.
- [x] Keep administrator and normal-user menu visibility unchanged.
- [x] Verify desktop 1440px navigation, page switching, login/logout, and core
      pages have no visible regressions.

### Phase 11C - Interaction Components And Floating Menu Fix

- [x] Add standard toast, loading, empty-state, modal, and action-menu styles
      to `monitor.css`.
- [x] Add a `MonitorUI` helper boundary in `monitor.js` for toast, loading,
      empty-state, menu close, and floating menu positioning helpers.
- [x] Replace clipped row action menu behavior with fixed or portal-style
      positioning.
- [x] Implement or equivalent `positionFloatingMenu(triggerEl, menuEl)`
      behavior.
- [x] Decide whether a local helper is enough or a lightweight floating
      positioning library is needed; record any new dependency in
      `DECISIONS.md` before adding it.
- [x] Ensure menus close on outside click, escape, page change, and successful
      action.
- [x] Verify account, proxy, report, AI, mail-template, and modal-contained row
      menus are not clipped by scroll containers or modal boundaries.
      Account, monitoring-task, AI-rule, and report row menus were verified
      with fixed viewport placement. Proxy, AI access, and mail-template
      surfaces currently expose direct edit/test/preview actions rather than
      row menus, so no clipped row-menu surface exists there in Phase 11C.

### Phase 11D - Responsive Foundation

- [x] Implement the accepted breakpoints: mobile `< 768px`, tablet
      `768px - 1279px`, desktop `>= 1280px`.
- [x] Add mobile navigation using a top-left hamburger button and left-side
      drawer, or document an equivalent touch-safe alternative before
      implementation.
- [x] Make toolbars, form grids, metric grids, modals, and dense tables usable
      on tablet and mobile.
- [x] Keep dense operational tables at least scroll-safe on mobile; page-level
      card conversions can be completed in the later page-specific phases.
- [x] Verify 1440px desktop, 1024px tablet, and 390px mobile layouts have no
      severe overlap, hidden primary actions, or hover-only required paths.

## Phase 12 - Navigation And Page Entry Redesign

Planning status:

Phase 12 is planned and depends on Phase 11. Execute it as Phase 12A-12B.

### Phase 12A - Navigation Structure And Login Landing

- [x] Route login success to Operations Home.
- [x] Move authenticated user identity and logout into one top-right control
      group on desktop and a predictable account area on mobile.
- [x] Replace Resource Management and System Configuration popover navigation
      with expandable navigation groups.
- [x] Preserve administrator and normal-user menu visibility rules.
- [x] Verify login, logout, session restore, and page switching.

### Phase 12B - Page Entry And Role Flow

- [x] Rebuild page entries around the monitoring task loop: Operations Home,
      Monitoring, Run Center, Report Center, Email Delivery status, and
      administrator resource support.
- [x] Standardize page title, description, primary action, and toolbar areas.
- [x] Add task-loop shortcuts where useful: create task, view runs, view
      reports, inspect email delivery, and resolve resource issues.
- [x] Verify administrator and normal-user paths separately.
- [x] Confirm no hidden administrator resource details leak into normal-user
      entry points.

## Phase 13 - Overview Operations Home Redesign

Planning status:

Phase 13 is planned and depends on Phase 10-12. Execute it as Phase 13A-13C.
Do not rebuild data aggregation, desktop visual layout, and responsive/role
views in one goal.

### Phase 13A - Operations Home Data Layer

- [x] Define the operations-home API contract under the existing monitor API
      surface, reusing `api/routers/monitor.py` unless a small helper module is
      justified.
- [x] Define data sources for task health, run activity, report activity,
      email delivery status, suspected lead metrics, and resource health.
- [x] Reuse existing tables where possible and document any missing metric as
      a later enhancement instead of fabricating data.
- [x] Preserve administrator and normal-user owner/workspace scope in every
      aggregate.
- [x] Keep the existing `/api/monitor/dashboard` response compatible until the
      frontend migration is complete, or document the response versioning
      strategy before changing it.
- [x] Verify API results for administrator and normal-user data scopes.

### Phase 13B - Operations Home Desktop Visual Metrics

- [x] Replace the text-heavy overview content with a desktop operations home
      using Phase 11 design tokens and component patterns.
- [x] Add visual task, run, report, email delivery, suspected lead, and concise
      resource-health metric sections.
- [x] Add drilldown links into Monitoring, Run Center, Report Center, Email
      Delivery status, and administrator resource pages where permitted.
- [x] Decide whether a chart library is needed; record any chart dependency in
      `DECISIONS.md` before adding it.
- [x] Keep long system-running, scheduler, platform, browser, and deployment
      diagnostic blocks out of the default home page.
- [x] Verify desktop 1440px layout, drilldowns, and role-safe metric wording.

### Phase 13C - Operations Home Responsive And Role Views

- [x] Adapt the operations home for 1024px tablet and 390px mobile layouts.
- [x] Ensure normal users see only own tasks, runs, reports, and business-safe
      health signals.
- [x] Ensure administrators see resource health as concise signals with
      drilldowns to the correct resource pages.
- [x] Move detailed system diagnostics to System Diagnostics or keep only a
      compact health summary on the home page.
- [x] Verify no horizontal overflow, overlapping metric cards, hidden primary
      actions, or role leakage on tablet and mobile.

## Phase 14 - Run Center Data Model Preparation

Planning status:

Phase 14 is complete and verified. It only prepared the run-center data model;
Phase 15 must still implement pagination, filters, archive/restore APIs, and
frontend governance.

- [x] Add `crawl_runs.visibility` with values `visible` and `archived`.
- [x] Add `crawl_runs.run_type` with values `scheduled`, `manual`, and `test`.
- [x] Add `crawl_runs.archived_at`.
- [x] Add `crawl_runs.archived_by`.
- [x] Backfill existing runs with `visibility = visible` and
      `run_type = scheduled`.
- [x] Add recommended indexes for visibility/date and run type/status filters,
      following `SCHEMA_MIGRATION.md`.
- [x] Update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md` with migration details.

## Phase 15 - Run Center Governance And Frontend

Planning status:

Phase 15 depends on Phase 14. Phase 15A and Phase 15B are complete and
verified. Phase 16 is the next implementation batch.

### Phase 15A - Run Center API And Data Governance

- [x] Add run pagination at the API/query layer.
- [x] Add filters for task, law firm, status, run type, visibility, date, and
      platform.
- [x] Add archive and restore APIs.
- [x] Hide archived records from default API/list behavior while preserving
      administrator access through explicit filters.
- [x] Preserve the existing run-list response fields while adding pagination,
      filter metadata, visibility, and run-type fields.
- [x] Preserve run logs, report links, owner/workspace scope, and existing
      status values.
- [x] Verify API tests for pagination, filters, archive, restore, and default
      visibility behavior.

### Phase 15B - Run Center Frontend Refinement

- [x] Add pagination UI.
- [x] Add task/law-firm, status, platform, run type, visibility, and date
      filters.
- [x] Add archive and restore row actions with confirmation.
- [x] Separate operational records from test/noise records in the default view.
- [x] Keep run logs refreshable, copyable, and downloadable.
- [x] Verify desktop, tablet, and mobile run-center layouts.

## Phase 16 - Email Delivery Data Model Preparation

Planning status:

Phase 16 is planned before email governance implementation.

- [ ] Add `email_delivery_logs`.
- [ ] Store `workspace_id`, `job_id`, `report_id`, `send_window_key`,
      `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
      `recipients_json`, and `created_at`.
- [ ] Use `send_type = auto` for scheduler sends and
      `send_type = manual_resend` for explicit resend.
- [ ] Use `daily` window keys as `{job_id}_{YYYY-MM-DD}`.
- [ ] Use `6h`, `12h`, and `cron` window keys as
      `{job_id}_{YYYY-MM-DD}_{HH}`.
- [ ] Add indexes or uniqueness rules needed for automatic-send idempotency.
- [ ] Update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`.

## Phase 17 - Email Delivery Governance

Planning status:

Phase 17 is planned and depends on Phase 16. Execute it as Phase 17A-17B so
delivery logic and report-center UI are verified separately.

### Phase 17A - Email Idempotency And Delivery Logic

- [ ] Implement `send_window_key` generation for `daily`, `6h`, `12h`, and
      `cron` using the accepted rules in `DATA_MODEL.md` and
      `SCHEMA_MIGRATION.md`.
- [ ] Add automatic-send idempotency by `workspace_id + job_id +
      send_window_key + send_type=auto`.
- [ ] Record automatic delivery attempts, successes, failures, recipient
      summaries, and customer-safe error messages in `email_delivery_logs`.
- [ ] Allow manual resend while recording a separate
      `send_type = manual_resend` delivery log.
- [ ] Preserve report generation when SMTP is unavailable.
- [ ] Keep existing latest-state report fields readable until the frontend is
      migrated to delivery history.
- [ ] Verify repeated scheduler triggers do not send duplicate automatic
      emails and manual resend creates a separate delivery record.

### Phase 17B - Email Delivery History Frontend

- [ ] Surface latest delivery status and delivery history in the report center
      without exposing SMTP secrets.
- [ ] Add manual resend UI with confirmation and clear success/failure
      feedback.
- [ ] Show send type, status, time, recipient summary, and customer-safe error
      message.
- [ ] Preserve report preview, lead detail switching, and report downloads.
- [ ] Verify administrator and normal-user owner/workspace scope for delivery
      history and manual resend.
- [ ] Verify desktop, tablet, and mobile report-center delivery surfaces.

## Phase 18 - Report Center Task Grouping

Planning status:

Phase 18 is planned and depends on Phase 10-11 and the accepted report snapshot
data model. Execute it as Phase 18A-18B so snapshot persistence lands before
frontend grouping consumes it.

### Phase 18A - Report Job Snapshot Data Model

- [ ] Add `reports.job_snapshot_json`.
- [ ] Save law firm, platforms, search keywords, frequency, task ID, and
      deleted-task context into the report snapshot for newly generated
      reports.
- [ ] Backfill `job_snapshot_json` for existing reports whose `job_id` still
      resolves to a monitoring task.
- [ ] Leave unrecoverable old reports visible with a limited-context fallback
      instead of blocking reads.
- [ ] Preserve `job_id` for active task relations and never use snapshot
      content to bypass owner/workspace permissions.
- [ ] Verify new reports contain snapshots, backfilled reports remain readable,
      and reports still load after their task is deleted or missing.

### Phase 18B - Report Center Task Grouping Frontend

- [ ] Group reports by monitoring task when `job_id` resolves.
- [ ] Group orphan or deleted-task reports using `job_snapshot_json`.
- [ ] Show deleted-task or limited-context labels where appropriate.
- [ ] Preserve report preview and lead detail switching by selected report.
- [ ] Preserve download links, email delivery status/history, and row actions.
- [ ] Verify grouped report behavior for active, deleted, missing-task, and
      limited-context reports on desktop, tablet, and mobile.
