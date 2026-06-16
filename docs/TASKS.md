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
- [x] Reconcile QR-session failures with same-account MediaCrawler login-state
      checks before showing login failure.

## Phase 7 - Runs, Reports, And AI

- [x] Ensure tasks run even when AI is missing.
- [x] Mark AI failures as manual-review leads.
- [x] Ensure tasks run and reports generate even when email is missing.
- [x] Keep report wording as suspected negative leads.
- [x] Verify report preview switches correctly across reports.
- [x] Ensure logs can be refreshed, copied, and downloaded.

## Phase 7.1 - Runs, Reports, And AI Stuck Recovery Follow-up

Planning status:

Phase 7.1 is an accepted follow-up regression fix for CR-035. It does not
rewrite Phase 7's historical completion record. It restores the Phase 7
guarantee that AI failure or interruption must not block report generation or
leave a run indefinitely `running`.

Confirmed CR-035 decision summary:

- [x] Confirm whether `interrupted` becomes a first-class terminal
      `crawl_runs.status`.
- [x] Confirm the stale-recovery algorithm should inspect step-level progress,
      live task evidence, resource locks, retry state, last safe return value,
      and redacted last error before marking a run interrupted.
- [x] Confirm retry policy should reuse existing crawler retry controls for
      platform/browser/network failures and apply a separate AI item retry
      budget within the run deadline.
- [x] Confirm `ai_item_timeout_seconds` should default to 120 seconds and be
      capped by the remaining run deadline.
- [x] Confirm future `crawl_runs.job_id` gaps must be prevented first, while
      dry-run-first historical `job_id` backfill from `summary.job_id` is only
      a fallback for rows whose task still exists.
- [x] Confirm active finalization may create `pending_review` rows for known
      unresolved AI candidates, while stale recovery does not rewrite AI rows
      unless an explicit repair workflow is invoked.
- [x] Confirm run summaries should include AI evaluation counts for total
      candidates, successful evaluations, failed/fallback evaluations,
      pending-review items, and unresolved items where available.

### Phase 7.1A - Run Identity Compatibility

- [ ] Verify active runtime writes `crawl_runs.job_id` for new runs.
- [ ] Add compatible reads for legacy rows where `crawl_runs.job_id` is null
      but `summary.job_id` resolves to an existing task.
- [ ] Update running-run lookup, stop/cancel behavior, and safe backfill logic
      for compatible legacy rows.
- [ ] Ensure backfill is dry-run capable and skips unresolved historical rows.

### Phase 7.1B - Idempotent Finalization And Recovery

- [ ] Add one idempotent finalization helper for success, failure, timeout,
      cancellation, interruption, and partial AI/report paths.
- [ ] Protect terminal status transitions from repeated or concurrent writers.
- [ ] Release resource locks safely after finalization attempts, with repeated
      release as a harmless no-op.
- [ ] Persist step-level run lifecycle progress in `crawl_runs.summary`,
      including phase, phase started time, progress heartbeat, retry state,
      last safe return value or customer-safe result, and redacted last error.
- [ ] Log background task exceptions with `run_id`, compatible `job_id`, phase,
      progress snapshot, and redacted error.
- [ ] Recover stale `running` rows before the wall-clock deadline only after
      evaluating live task evidence, resource locks, progress heartbeat, retry
      state, last step result, and redacted interruption cause.
- [ ] Ensure startup/scheduler stale recovery does not auto-repair historical
      stuck runs such as `8317`; historical repair must use the Phase 7.1D
      approval workflow.

### Phase 7.1C - AI Fallback And Partial Report Generation

- [ ] Add per-item AI timeout/failure/invalid-JSON fallback to
      `pending_review` when the run can safely continue.
- [ ] During active finalization, create `pending_review` rows for known
      not-yet-evaluated candidates when safe before report generation.
- [ ] Track AI evaluation progress counts for total candidates, successful
      evaluations, failed/fallback evaluations, pending-review items, and
      unresolved items.
- [ ] Generate reports from partial AI/manual-review state when collected
      content exists.
- [ ] Finalize report-generation failures into a terminal redacted failure
      state instead of leaving the run `running`.

### Phase 7.1D - Current Run Remediation Gate

- [ ] Do not modify historical run `8317` without explicit operator
      confirmation.
- [ ] Before repair, back up the database and document rollback steps.
- [ ] Provide a dry-run-first repair helper or operator checklist for run
      `8317`, showing proposed terminal status, unresolved AI counts,
      pending-review rows to create, report-generation effect, and rollback
      path before any mutation.
- [ ] After code safety is verified, choose either preserving run `8317` as
      `interrupted` or repairing it into a partial report with the remaining
      21 contents marked for manual review.

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
- [x] Move account, monitoring-task, and AI-rule row "more" menu content into
      page-level floating containers so table scroll areas and sticky action
      columns cannot cover the popup content.

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
verified. Phase 16, Phase 17A, Phase 17B, Phase 18A, and Phase 18B are also
complete and verified.

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

Phase 16 is complete and verified. It only prepared the email delivery data
model; Phase 17A connected delivery logic, scheduler idempotency, and manual
resend logging to this foundation.

- [x] Add `email_delivery_logs`.
- [x] Store `workspace_id`, `job_id`, `report_id`, `send_window_key`,
      `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
      `recipients_json`, and `created_at`.
- [x] Use `send_type = auto` for scheduler sends and
      `send_type = manual_resend` for explicit resend.
- [x] Use `daily` window keys as `{job_id}_{YYYY-MM-DD}`.
- [x] Use `6h`, `12h`, and `cron` window keys as
      `{job_id}_{YYYY-MM-DD}_{HH}`.
- [x] Add indexes or uniqueness rules needed for automatic-send idempotency.
- [x] Update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`.

## Phase 17 - Email Delivery Governance

Planning status:

Phase 17 depends on Phase 16. Phase 17A and Phase 17B are complete and
verified. Phase 17B kept report-center delivery-history UI separate from the
backend delivery-governance work and did not implement Phase 18 report
grouping.

### Phase 17A - Email Idempotency And Delivery Logic

- [x] Implement `send_window_key` generation for `daily`, `6h`, `12h`, and
      `cron` using the accepted rules in `DATA_MODEL.md` and
      `SCHEMA_MIGRATION.md`.
- [x] Add automatic-send idempotency by `workspace_id + job_id +
      send_window_key + send_type=auto`.
- [x] Record automatic delivery attempts, successes, failures, recipient
      summaries, and customer-safe error messages in `email_delivery_logs`.
- [x] Allow manual resend while recording a separate
      `send_type = manual_resend` delivery log.
- [x] Preserve report generation when SMTP is unavailable.
- [x] Keep existing latest-state report fields readable until the frontend is
      migrated to delivery history.
- [x] Verify repeated scheduler triggers do not send duplicate automatic
      emails and manual resend creates a separate delivery record.

### Phase 17B - Email Delivery History Frontend

- [x] Surface latest delivery status and delivery history in the report center
      without exposing SMTP secrets.
- [x] Add manual resend UI with confirmation and clear success/failure
      feedback.
- [x] Show send type, status, time, recipient summary, and customer-safe error
      message.
- [x] Preserve report preview, lead detail switching, and report downloads.
- [x] Verify administrator and normal-user owner/workspace scope for delivery
      history and manual resend.
- [x] Verify desktop, tablet, and mobile report-center delivery surfaces.

## Phase 17.1 - Email Delivery Safety Follow-up

Planning status:

Phase 17.1 is an accepted follow-up regression fix for CR-036. It does not
rewrite Phase 17's historical completion record. It restores the intended
safety boundary that automated tests, local diagnostics, and accidental local
execution must not send hidden real external report emails.

Confirmed CR-036 decision summary:

- [x] Confirm the explicit real-email validation model must allow intentional
      production/pilot SMTP validation while preventing routine automated tests
      and local diagnostics from sending hidden real mail.
- [x] Confirm `MONITOR_ALLOW_REAL_EMAIL_SEND` should be environment-controlled
      and surfaced read-only in runtime settings.
- [x] Confirm local manual-resend behavior under the safety gate should be
      allowed only when the explicit real-mail validation policy allows it;
      otherwise it remains a non-sending validation path.
- [x] Confirm historical handling for orphan delivery-log rows `60` and `81`
      and their report artifacts. Do not mutate them without operator approval.

### Phase 17.1A - Real SMTP Safety Gate

- [ ] Add one shared delivery-safety helper used before real SMTP side effects.
- [ ] Prevent routine automated tests and local diagnostics from hidden real
      SMTP side effects unless the confirmed explicit validation path is used.
- [ ] Apply the safety helper consistently to automatic report delivery, manual
      resend, and mail-test paths according to the confirmed scope.
- [ ] When delivery is blocked by the safety gate, preserve report generation
      and write a customer-safe skipped delivery state.
- [ ] Keep production/pilot real email delivery and explicit real-mail
      validation working when the confirmed allow conditions and SMTP
      configuration are complete.

### Phase 17.1B - Test Isolation And Regression Coverage

- [ ] Update `test_run_job_blocks_platform_when_login_window_is_open` so it
      cannot invoke real SMTP while still verifying the platform-blocking
      behavior.
- [ ] Add a test-level SMTP tripwire that fails if the automated suite reaches
      `smtplib.SMTP` or `smtplib.SMTP_SSL` without explicit opt-in.
- [ ] Audit `run_monitor_job` tests and report-generation tests for unmocked
      email delivery paths.
- [ ] Verify the full test suite can run with a real SMTP config in the active
      database without sending external mail.
- [ ] Add a separate real-mail validation test path or runbook that is skipped
      by default and can only send when the confirmed explicit validation
      conditions are present.

### Phase 17.1C - Effective Recipient Traceability

- [ ] Centralize effective-recipient resolution so report delivery and delivery
      logs use the same recipient list.
- [ ] Keep recipient precedence explicit in code and UI: task recipients win,
      global default recipients are fallback-only, and SMTP sender is not a
      delivery target.
- [ ] Record final effective recipients in `email_delivery_logs`, including
      recipients inherited from global default-recipient fallback.
- [ ] Define and persist recipient metadata consistently:
      `recipients_json` for the task/request snapshot,
      `effective_recipients_json` for final resolved recipients,
      `effective_recipient_source` for recipient origin, and `trigger_source`
      for the send trigger.
- [ ] Record delivery trigger source so future role policy and quota logic can
      distinguish automatic, manual, test, diagnostic, and explicit validation
      sends.
- [ ] Show the effective-recipient source in preflight/delivery surfaces, e.g.
      task recipients versus global default-recipient fallback.
- [ ] Update email-configuration and task-configuration copy so operators can
      see that filling task recipients overrides the global default recipients.
- [ ] Preserve customer-safe recipient display without storing SMTP secrets.
- [ ] Keep automatic-send idempotency by `workspace_id + job_id +
      send_window_key + send_type=auto` unchanged.

### Phase 17.1D - Historical Orphan Evidence And Operations Notes

- [ ] Document the observed orphan evidence from `job_id` 9686 and 9759:
      sent delivery-log rows, existing report artifacts, and missing
      job/run/report rows.
- [ ] Provide a dry-run-first helper or operator checklist for reviewing
      orphan delivery logs and report artifacts.
- [ ] Add or link an operator runbook for orphan email evidence review,
      backup-before-mutation, approval, and rollback.
- [ ] Require database backup and explicit operator approval before deleting,
      annotating, or otherwise mutating historical delivery evidence.
- [ ] Ensure report-center delivery-history and run/report grouping remain
      readable for existing non-orphan reports.

## Phase 17.2 - Report Email Template Governance

Planning status:

CR-039 is an accepted existing-feature optimization for report email template
predictability and historical diagnosis. Phase 17.2A overlaps with CR-036's
delivery-log metadata work and should be implemented with Phase 17.1C when
practical to avoid repeated `email_delivery_logs` schema churn. Phase 17.2B-C
remain follow-up product governance work and should not block the immediate
CR-036 safety fix.

### Phase 17.2A - Effective Template Provenance

- [ ] Centralize effective-template resolution so report delivery, preview, and
      logs agree on task-bound versus active-global fallback behavior.
- [ ] Record effective email template id, template name, subject template, and
      template source in report snapshots.
- [ ] Record effective template metadata in email delivery logs without storing
      secrets or unsafe raw HTML.
- [ ] Make historical report/email detail able to explain why a delivered email
      differed from the currently previewed or currently active template.

### Phase 17.2B - Template Body Guardrails

- [ ] Validate or warn/block custom templates that omit `{report_html}` and
      `{report_body}` so delivered emails cannot silently drop the generated
      report body.
- [ ] Clarify in the mail-template UI that editor preview uses sample data and
      real sends use the generated report HTML for the actual run.
- [ ] Preserve subject-template flexibility while keeping required body content
      system-controlled.

### Phase 17.2C - Preset Style Direction

- [ ] Replace the long-term product direction of unrestricted HTML editing with
      administrator-selectable preset report-email styles.
- [ ] Ensure preset styles wrap the system-generated report body instead of
      letting users remove required report sections.
- [ ] Keep old templates readable for compatibility, but do not require normal
      users to edit HTML.

## Deferred Backlog - Email Delivery Role Governance

Planning status:

CR-037 is deferred. It records the user's broader direction that email sending
and resend should eventually be governed by role, administrator policy, and
possibly per-user or per-day quotas. It should not be implemented as part of
CR-036/Phase 17.1.

- [!] Confirm the future UI location for administrator email governance:
      Users And Permissions, Runtime Strategy, or a dedicated Email Governance
      section.
- [!] Confirm whether normal-user send and resend quotas are per user, per
      task, per report, per day, or a combination.
- [!] Confirm whether automatic scheduled delivery and manual resend use the
      same policy or separate policies.

## Phase 18 - Report Center Task Grouping

Planning status:

Phase 18 depends on Phase 10-11 and the accepted report snapshot data model.
Execute it as Phase 18A-18B so snapshot persistence lands before frontend
grouping consumes it. Phase 18A and Phase 18B are complete and verified.

### Phase 18A - Report Job Snapshot Data Model

- [x] Add `reports.job_snapshot_json`.
- [x] Save law firm, platforms, search keywords, frequency, task ID, and
      deleted-task context into the report snapshot for newly generated
      reports.
- [x] Backfill `job_snapshot_json` for existing reports whose `job_id` still
      resolves to a monitoring task.
- [x] Leave unrecoverable old reports visible with a limited-context fallback
      instead of blocking reads.
- [x] Preserve `job_id` for active task relations and never use snapshot
      content to bypass owner/workspace permissions.
- [x] Verify new reports contain snapshots, backfilled reports remain readable,
      and reports still load after their task is deleted or missing.

### Phase 18B - Report Center Task Grouping Frontend

- [x] Group reports by monitoring task when `job_id` resolves.
- [x] Group orphan or deleted-task reports using `job_snapshot_json`.
- [x] Show deleted-task or limited-context labels where appropriate.
- [x] Preserve report preview and lead detail switching by selected report.
- [x] Preserve download links, email delivery status/history, and row actions.
- [x] Verify grouped report behavior for active, deleted, missing-task, and
      limited-context reports on desktop, tablet, and mobile.

## Phase 19 - Run Center Realtime Progress And Requirement Intake Governance

Planning status:

Phase 19 is the next planned optimization batch after the completed Phase
10-18 console roadmap. It covers one documentation-governance rule update and
one product optimization for active run progress visibility. Phase 19 must not
change MediaCrawler platform implementations, add high-concurrency worker
architecture, or expose raw crawler paths/secrets unless a later accepted CR
changes those boundaries.

Phase 19B-19D should be implemented after the CR-035/Phase 7.1 run-lifecycle
regression fix is implemented and verified, or deliberately split into a
smaller safe batch.
Phase 19 progress display may depend on Phase 7.1 fields such as phase,
heartbeat, terminal `interrupted` state, and AI progress fallback behavior.

### Phase 19A - Requirement Intake Classification Rules

- [x] Add a CR classification rule for new capabilities, existing feature
      optimizations, regression fixes, and documentation-governance changes.
- [x] Document required future CR fields: background, purpose, type, scope
      boundary, non-goals when useful, related tasks, and acceptance criteria.
- [x] Update `AGENTS.md`, `AGENT_WORKFLOW.md`, `CHANGE_REQUESTS.md`, and
      `DOCUMENTATION_CHECKS.md` so future agents can find and apply the rule.

### Phase 19B - Run Center Progress Data Layer

- [ ] Treat Phase 7.1 lifecycle fields as the preferred dependency for active
      progress storage: `phase`, `phase_started_at`, `progress_updated_at`,
      retry state, last safe result, and progress snapshots in
      `crawl_runs.summary`.
- [ ] If Phase 19B is deliberately implemented before Phase 7.1, use only a
      small compatible provisional-progress shape and document how it will
      merge into the Phase 7.1 summary structure. Do not add a conflicting
      second progress model.
- [ ] Add a safe progress snapshot mechanism for running crawler attempts,
      using MediaCrawler output files or equivalent progress signals while the
      subprocess is still alive.
- [ ] Store provisional progress in `crawl_runs.summary` without marking it as
      final ingested counts.
- [ ] Tolerate missing, in-flight, partially written, or malformed JSON/JSONL
      output files without crashing the run.
- [ ] Preserve the existing final collect-and-ingest semantics for
      `raw_contents`, `filtered_contents`, `excluded_contents`, and
      `new_contents`.
- [ ] Preserve owner/workspace scope, logs, stop action, archive/restore,
      timeout handling, and customer-safe wording.

### Phase 19C - AI Evaluation Progress Updates

- [ ] Update AI evaluation progress in batches or time intervals while the
      evaluation loop is running.
- [ ] Track evaluated count, total evaluation candidates, suspected negative
      count, high-risk count, and manual-review count without waiting for the
      full AI batch to finish.
- [ ] Preserve AI-failure fallback to manual review and report generation.
- [ ] Ensure final AI counts remain exact after the evaluation loop completes.

### Phase 19D - Run Center Frontend Progress Display And Polling

- [ ] Keep Run Center polling active while visible runs remain active instead
      of stopping after a short fixed polling window.
- [ ] Display active collection, ingestion, AI evaluation, report generation,
      email delivery, timeout, and completion states clearly.
- [ ] Distinguish provisional collection progress from final ingested counts.
- [ ] Keep desktop, tablet, and mobile layouts usable without overlap, clipped
      actions, or hidden stop/log controls.
- [ ] Verify normal users only see own scoped progress and administrators keep
      workspace-wide visibility.

## Phase 20 - Run Detail And AI Evaluation Traceability

**BLOCKED - DO NOT IMPLEMENT**

Planning status:

Phase 20 is proposed and blocked until CR-034 confirmation items are resolved.
It should not be implemented until role visibility, raw/redacted response
visibility, trace retention, and storage shape are confirmed. This phase is
separate from Phase 19 because it adds historical AI traceability and likely
requires data-model and API changes, while Phase 19 focuses on run progress
visibility.

Required confirmations before any implementation:

- normal-user versus administrator visibility for prompt snapshots, request
  payloads, raw/redacted responses, and debug metadata;
- trace retention and maximum stored size for prompt, request, response, and
  sampled comments;
- final storage shape, including whether `ai_evaluation_traces` is accepted.

### Phase 20A - Traceability Confirmation And Data Model Design

- [!] Confirm the normal-user versus administrator visibility boundary for
      prompt snapshots, request payloads, raw/redacted responses, and debug
      metadata.
- [!] Confirm trace retention and maximum stored size for prompt, request,
      response, and sampled comments.
- [!] Confirm storage shape: proposed `ai_evaluation_traces` table with
      redacted/capped JSON fields, linked to `run_id`, `raw_content_id`, and
      `ai_evaluations.id`.
- [ ] After confirmation, update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`
      from proposed notes to accepted implementation details.

### Phase 20B - AI Evaluation Trace Persistence

- [ ] Persist new AI evaluation trace snapshots at evaluation time, including
      business input payload, prompt/request snapshot, provider/model metadata,
      structured output, raw/redacted response, fallback/error detail, duration,
      and timestamps.
- [ ] Preserve existing `ai_evaluations` final-result behavior and keep
      historical rows readable.
- [ ] Show an explicit limited-context state for old evaluations that do not
      have trace snapshots.
- [ ] Ensure trace persistence redacts secrets, authorization headers, cookies,
      proxy credentials, profile paths, and server-local paths.

### Phase 20C - Run Detail And AI Evaluation API

- [ ] Add or extend run-detail APIs so a run can return lifecycle summary,
      crawler logs, content list, AI evaluation list, and report/email links in
      one scoped response.
- [ ] Add paginated/filterable AI evaluation detail reads by `run_id`, status,
      risk level, platform, keyword, and content title.
- [ ] Add a per-evaluation detail endpoint for input/output trace snapshots
      with role-safe field filtering.
- [ ] Preserve owner/workspace scope and administrator-only access to confirmed
      debug fields.

### Phase 20D - Run Detail Frontend

- [ ] Add a Run Center "详情" action that opens a per-run detail drawer or
      page grouped by `run_id`.
- [ ] Show tabs or sections for Overview, Collection Logs, Collected Contents,
      AI Evaluation, Report, and Email Delivery.
- [ ] In the AI Evaluation tab, list every evaluation candidate/result for the
      run and allow opening a single evaluation's input/output detail.
- [ ] Keep crawler logs visible in the same run-detail surface instead of
      making operators choose between logs and AI details.
- [ ] Verify desktop, tablet, and mobile layouts keep the run detail readable
      without hiding stop/log/detail actions.

### Phase 20E - Report Center Lead Detail Clarity

- [ ] Add an explicit "view leads" action to report rows or report groups so
      line details are not hidden behind the report preview action.
- [ ] Link report leads back to the originating run detail when `run_id` is
      available.
- [ ] Keep Report Center focused on final reports, report leads, downloads, and
      email delivery history rather than running-process observability.

## Formal Console Full-Coverage Positive UI Optimization

Planning status:

This is a verified frontend-only optimization pass after the completed Phase
10-18 console roadmap. It preserves the latest formal `/monitor` frontend
functions and does not implement Phase 19B-19D run-progress product changes.

- [x] Keep the formal navigation structure unchanged: dashboard, monitoring,
      run center, report center, resource management, and system configuration
      remain separate pages.
- [x] Preserve existing account, task, resource, AI, mail, run, report, and
      diagnostics buttons, filters, batch actions, more menus, drawers, and
      modals.
- [x] Apply a cleaner low-noise enterprise visual layer without adding a new
      framework or build step.
- [x] Reprioritize the dashboard so operations data and closed-loop status
      appear before the 01-05 shortcut flow.
- [x] Add page-shaped skeleton/loading states for dashboard, accounts,
      resources, AI, mail, runtime, runs, reports, and diagnostics.
- [x] Add stable button-level loading feedback for secondary drawers and
      modals, including account QR/Cookie login, resource saves, AI tests,
      mail tests, and template preview.
- [x] Keep row more menus as floating menus that are not clipped by table
      scroll containers.
- [x] Compress the mobile dashboard so key metrics and closed-loop status
      remain usable at 390px without horizontal overflow.
- [x] Verify desktop 1440px, tablet 1024px, and mobile 390px browser behavior
      for page reachability, core modals, floating menus, and overflow.

## Formal Console Drawer Close Accessibility Follow-up

Planning status:

CR-038 is an accepted frontend-only follow-up to the verified formal console
optimization pass. It fixes scrollable drawer close accessibility without
reopening CR-033 or changing backend behavior.

- [ ] Make shared drawer/modal headers sticky within scrollable drawers so the
      top-right close button remains visible while content scrolls.
- [ ] Preserve backdrop click-to-close, Escape close where supported, and
      existing bottom save/close action bars.
- [ ] Add visual separation for sticky headers using solid background and
      border/shadow treatment so form content cannot bleed through.
- [ ] Verify task edit, account, proxy, AI profile, mail config, mail template,
      run log, and report preview drawers for reachable close controls.
- [ ] Verify desktop, tablet, and mobile layouts avoid overlapping sticky
      header controls with content, scrollbars, or footer action bars.

## Phase 21 - Formal Console Page-Level UI/UX Refinement

Planning status:

CR-040 is an accepted frontend-only page-level UI/UX refinement phase for the
formal `/monitor` console. This phase must not reopen CR-033, must not replace
the formal console with the static prototype, and must not mark any UI code
work complete until implementation and verification are actually done. The
implementation baseline is the latest formal `/monitor` console.

- [x] Create `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` with complete
      execution guidance for what to do, where to do it, how to test it, how to
      verify it, what target experience to reach, and how acceptance will be
      judged.
- [x] Confirm CR-040 as the accepted Phase 21 implementation scope.
- [x] Confirm that the currently unrendered `Users And Permissions` surface is
      out of Phase 21 scope. If the user wants it implemented later, record a
      separate new-capability CR instead of treating it as visual refinement.
- [ ] Implement Phase 21 in small frontend workstreams A-O with local
      smoke-checks before the final Phase 21P cross-page verification gate.

### Phase 21A - Global Shell And Design Tokens

- [ ] Refine formal-console neutral, primary, border, background, text,
      status, focus, disabled, toast, empty-state, error-state, skeleton, and
      modal base styles in the formal frontend.
- [ ] Keep the no-build Vanilla JavaScript plus CSS custom-property stack.
- [ ] Verify login and all logged-in pages still render without console errors
      or horizontal overflow.

### Phase 21B - Navigation Hierarchy

- [ ] Strengthen the visual difference between first-level task-loop pages and
      second-level Resource Management/System Configuration pages.
- [ ] Preserve administrator and normal-user menu visibility.
- [ ] Verify desktop, tablet, and mobile navigation open, close, switch pages,
      and preserve active state.

### Phase 21C - Operations Home Refinement

- [ ] Reduce the onboarding feeling of the `01-05` quick-entry block while
      preserving all five shortcuts.
- [ ] Prioritize operational data, urgent exceptions, report output, email
      delivery, and resource impact before guidance content.
- [ ] Add layout-resilience safeguards for Operations Home closed-loop,
      shortcut, metric, and resource-health sections so desktop, tablet, and
      mobile views wrap or collapse before text becomes one-character vertical
      columns.
- [ ] Verify administrator and normal-user Operations Home views remain
      role-safe and usable at `1440x900`, `1024x768`, and `390x844`.
- [ ] Capture or record dashboard layout checks proving no text overlap,
      unreadable card labels, hidden primary actions, horizontal overflow, or
      one-character-per-line wrapping.

### Phase 21D - Monitoring Tasks And Task Drawer

- [ ] Refine the Monitoring page and task drawer hierarchy without removing
      any formal fields, filters, row actions, more-menu actions, or drawer
      actions.
- [ ] Preserve normal-user simplified task creation and administrator advanced
      task settings.
- [ ] Verify task create/edit, sample fill, clear, save, close, run, stop,
      pause/resume, and delete flows.

### Phase 21E - Platform Accounts

- [ ] Refine the Platform Accounts page and account dialog as a complete
      account-maintenance workflow, not a generic configuration modal.
- [ ] Preserve QR login, local-window fallback where allowed, Cookie login,
      login records, account identity/details, filters, attention filter,
      batch actions, row detail, and row more menu.
- [ ] Verify every login status, batch action, row-menu action, save, delete,
      and close path at desktop, tablet, and mobile widths.

### Phase 21F - Proxy Resources

- [ ] Refine proxy list density, masked-secret readability, health/error
      scanning, and proxy drawer layout.
- [ ] Preserve add, refresh, view accounts, search, status filter, clear
      filters, row edit/delete, clear, save, and close.

### Phase 21G - AI Access

- [ ] Refine AI Access resource layout, model selection, model-list loading,
      default state, delete action, and connection-test feedback.
- [ ] Preserve add, refresh, view rules, search, protocol/test filters, clear
      filters, edit, test, set default, delete, model list, save, and close.

### Phase 21H - AI Evaluation Rules

- [ ] Refine the AI rule editor into clearer sections while preserving every
      rule field, prompt preview, sample test field, result area, row action,
      and more-menu action.
- [ ] Preserve rule testing, default switching, restore default, save, delete,
      and close flows.

### Phase 21I - Mail Configuration

- [ ] Refine SMTP form layout, sender/recipient wording, default-recipient
      explanation, masked password display, and mail-test feedback.
- [ ] Preserve edit config, send test mail, refresh config, view delivery
      status, save, cancel, close, and test-console behavior.

### Phase 21J - Mail Templates

- [ ] Refine mail-template list, variable hints, active/current state, raw HTML
      editor, subject field, and iframe preview stability.
- [ ] Preserve add, refresh, view mail config, search/status filters, row edit,
      set current where available, delete, save, refresh preview, clear, close,
      and iframe preview.
- [ ] Keep CR-039 governed preset direction as future product work and do not
      remove free-form HTML editing in this visual refinement batch.

### Phase 21K - Runtime Strategy

- [ ] Refine grouped runtime-setting tables for scanability, locked-state
      readability, valid range, apply scope, and save feedback.
- [ ] Preserve refresh strategy, save strategy, view diagnostics, grouped
      tables, current values, inputs, valid ranges, apply scopes, and lock
      states.

### Phase 21L - Run Center

- [ ] Refine Run Center filters, pagination, table density, status/failure
      scanning, and log drawer visual structure without adding Phase 19 data
      requirements.
- [ ] Preserve all filters, filter summary, pagination, view logs, stop,
      archive, restore, refresh logs, copy logs, download logs, and close.

### Phase 21M - Report Center

- [ ] Refine grouped report archive, selected report relationship, lead detail,
      delivery history, preview drawer, and row more menu visual hierarchy.
- [ ] Preserve report filters, refresh report, refresh email status, refresh
      history, preview, more menu, delivery history, resend, HTML/Excel/
      Markdown downloads, lead detail, and preview iframe.

### Phase 21N - System Diagnostics

- [ ] Refine diagnostics into clearer summary, impact, next action, runtime
      state, scheduler state, platform state, and action-card hierarchy.
- [ ] Preserve rerun diagnosis, run system diagnosis, process account
      resources, readiness/action cards, and customer-safe diagnostic wording.

### Phase 21O - Login Page

- [ ] Refine login trust, focus, loading, and error states without changing the
      session/authentication flow.
- [ ] Preserve email, password, login, error feedback, and route-to-Operations
      Home behavior after successful login.

### Phase 21P - Cross-Page Verification

- [ ] Run static checks: `node --check api/webui/monitor/monitor.js`, inline
      script parse check for `api/monitor_web/index.html`, and
      `uv run python scripts/check_docs.py`.
- [ ] Run targeted frontend regression tests covering CR-033, formal console
      pages, secondary overlays, loading feedback, and floating menus.
- [ ] Run browser verification at `1440x900`, `1024x768`, and `390x844` for
      administrator and normal-user paths.
- [ ] Stress-check card/grid layouts with long law-firm names, platform names,
      account labels, failure reasons, and status text across dashboard, runs,
      reports, resources, and secondary overlays; fail the batch if any module
      collapses text into one-character vertical columns or hides actions.
- [ ] Record implementation verification in `docs/TEST_RESULTS.md` only after
      code changes are actually implemented and tested.
