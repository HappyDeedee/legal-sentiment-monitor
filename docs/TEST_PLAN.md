# Test Plan

## General Rule

Production acceptance must run in a server-like environment. Local Chrome on
the operator's computer is not a valid acceptance path.

## Phase 0 Documentation Review Tests

- Governance documents exist and can be followed from `AGENTS.md`.
- Accepted change requests are connected to `TASKS.md`, `TRACEABILITY.md`, and
  verification notes.
- Specialist documents referenced by `AGENTS.md` exist.
- Documentation consistency checks can be run with `python scripts/check_docs.py`
  once the Phase 1 close-out script is implemented.

## Phase 0.5 Schema Foundation Tests

- Foundation tables exist: `workspaces`, `users`, `user_sessions`,
  `system_settings`, and `audit_logs`.
- Priority business tables have `workspace_id`, `created_by`, and `updated_by`
  columns.
- `social_accounts` and `login_sessions` have `profile_key`.
- `crawl_runs` has `timeout_seconds`, `deadline_at`, and `timeout_reason`.
- `social_accounts` has account/profile lock fields:
  `locked_by_run_id`, `locked_at`, and `lock_expires_at`.
- `resource_locks` exists for proxy concurrency.
- Existing `monitor_jobs`, `social_accounts`, `crawl_runs`, and `reports`
  still load without runtime errors.
- Default workspace exists with `id = 1` or equivalent configured default.
- Existing `profile_path` data is preserved during the first schema foundation
  step but is not used for new account environments.
- Existing MVP monitoring pages still load after migration.
- Existing monitoring list API returns without runtime errors.
- A test monitoring job can still be created through the existing API.
- Scheduler can still load jobs after migration.
- Runs and reports pages load without runtime errors after migration.
- Existing monitoring API JSON response shapes remain compatible for job list,
  job detail, run list, report list, and scheduler status endpoints.
- Existing job creation payloads do not need new required fields from the
  schema foundation; missing workspace/user fields are backfilled or defaulted.
- Existing legacy `crawl_runs.summary` JSON remains readable for runs created
  before Phase 0.5.
- Existing stop, resend, refresh, and diagnostics APIs return customer-safe
  errors instead of stack traces after migration.

## Role And Permission Tests

- Bootstrap administrator is created from `MONITOR_ADMIN_EMAIL` and
  `MONITOR_ADMIN_PASSWORD` when no administrator exists.
- Bootstrap administrator can log in with the configured credentials.
- Administrator can see all menus.
- Normal user sees only overview, monitoring, run center, and report center.
- Normal user cannot access account pool, proxy resources, AI access, mail
  configuration, runtime strategy, or system diagnostics.
- Normal user can only view own workspace tasks, runs, and reports.
- Administrator can view and manage workspace resources.

## Normal User Task Tests

- Normal user can create a task with law firm name, platforms, platform search
  terms, range, frequency, and recipient emails.
- Normal user can create a task without selecting accounts, proxies, AI access,
  or templates.
- Normal user sees understandable messages if a selected platform lacks
  available resources.

Use the standard test subject:

- law firm: `海安律所`
- search terms: `海安律所避雷`, `海安律所退费`, `海安律所投诉`

Use the standard permission test data:

- administrator: `admin@example.com`;
- normal user 1: `user1@example.com`;
- normal user 2: `user2@example.com`;
- law firm 1: `海安律所`, created by normal user 1;
- law firm 2: `恒泰律所`, created by normal user 2;
- verify normal user 1 cannot see normal user 2's tasks, runs, or reports.

## Administrator Resource Tests

- Administrator can create, edit, disable, and delete platform accounts.
- Administrator can create, edit, disable, and delete proxies.
- Administrator can create and test AI access without exposing raw API keys.
- Administrator can configure SMTP and templates without exposing passwords.
- Administrator can update runtime strategy.

## Server Login Tests

- QR login is initiated from the web UI.
- QR code or structured status is returned to the web UI.
- Structured login-session statuses include `preparing`, `waiting_qrcode`,
  `waiting_scan`, `waiting_confirm`, `success`, `needs_verification`,
  `qrcode_failed`, `timeout`, and `platform_error`.
- Scanning succeeds without using the operator's local Chrome.
- Verification states are returned when the platform requires captcha, slider,
  SMS, or manual confirmation.
- Successful login persists the account profile on the server.
- Closing the browser does not delete login state.
- Restarting the service/container does not delete login state.
- Login flow uses server-side Playwright with headless mode enabled in
  server/container deployment.
- Server deployment sets `MONITOR_LOGIN_QR_HEADLESS=true` or equivalent
  production behavior.
- Server deployment sets `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`, and the
  local-window login endpoint is unavailable in production mode.
- QR login works in a container/server-like environment without X11 or desktop
  GUI dependency.

## Account Environment Tests

- Each platform account has a unique profile.
- Profile key format is `{workspace_id}/{platform}/acc_{account_id}`.
- Creating a second account on the same platform does not reuse the first
  profile.
- Same account cannot run two tasks at the same time.
- Same profile cannot run two tasks at the same time.
- Task-bound proxy overrides account proxy.
- Account proxy is used when task proxy is absent.
- Proxy concurrency limit is respected.
- Account/profile locks are acquired through inline `social_accounts` fields.
- Proxy locks are acquired through `resource_locks`.
- Expired account/profile locks are not reused until recovery verifies the
  owning run state.
- Startup recovery reconciles persisted `running` runs and locks after service
  restart.
- Scheduler recovery marks stale running runs as `timeout` or `interrupted`
  before releasing locks.

## Runtime Strategy Settings Tests

- Administrator can edit runtime settings in grouped tables for Crawling,
  Login, Scheduler, and Retention.
- `crawler_timeout_seconds` applies to newly started runs as a run-level
  wall-clock deadline.
- `lock_cleanup_buffer_seconds` is added to the run deadline when calculating
  lock expiry.
- Environment-locked settings are read-only and show a lock indicator.
- Normal users cannot access Runtime Strategy.

## Run And Report Tests

- A task can run with AI configured.
- A task can run without AI and mark leads as manual review.
- A task can run without email and still generate a report.
- One platform failure does not block other platforms.
- Run logs can be refreshed, copied, and downloaded.
- Different report previews switch correctly.
- Report wording uses suspected negative leads and avoids factual conclusions.
- A run that exceeds `deadline_at` is marked `timeout`, not generic `failed`.
- Timeout runs preserve already collected partial results.
- Timeout reports show a customer-safe message that the task reached the system
  time limit.
- Multi-platform runs share one run-level deadline; each platform attempt uses
  remaining run time rather than a fresh full timeout budget.
- Retry does not start when the run deadline has already passed.

## Crawl Range Tests

- Normal users can set `max_items`, `start_page`, `max_pages`, and time window
  in the task wizard.
- `max_items` is validated as a content-count cap.
- `max_pages` is treated as approximate and does not require exact platform page
  parity.
- Time-window behavior is tested as platform-native where supported and as
  monitoring-layer filtering where native support is missing.
- UI copy does not promise exact cross-platform page or time-window behavior.

## Security Tests

- API keys are masked.
- SMTP passwords are masked.
- Proxy URLs are masked.
- Cookies are not displayed after save.
- Logs do not contain raw API keys, cookies, SMTP passwords, or proxy passwords.
- Normal users cannot call administrator-only APIs.
- Administrator resource operations write audit logs without storing plaintext
  secrets.
- Readiness surfaces account invalidation and proxy-error alert paths with
  customer-safe wording.
- System diagnostics include disk-space, backup-set, and retention-setting
  checks.

## Server-Like Acceptance Tests

- Start the system in a container or Linux server-like environment.
- Access the web UI through an HTTP domain or localhost server URL.
- Complete QR login through the web UI.
- Run a task using the server-side browser/profile.
- Restart service/container and verify profile reuse.
- Verify no acceptance step depends on local Chrome.

## Phase 10 Frontend Architecture Tests

- `FRONTEND_ARCHITECTURE.md` exists and is referenced by `AGENTS.md`,
  `AGENT_WORKFLOW.md`, and `scripts/check_docs.py`.
- Accepted frontend stack is Vanilla JavaScript plus CSS custom properties.
- No Phase 10-18 planning document requires Tailwind, Alpine.js, Petite-Vue,
  React, Vue, or a new build pipeline.
- Optional lightweight libraries are limited to focused charting or floating
  menu placement and require a recorded decision before implementation.
- `uv run python scripts/check_docs.py` passes after documentation updates.

## Phase 10.5 Global Plan Review Tests

- The Phase 10-18 roadmap is reviewed as one connected plan before any
  Phase 11A-only execution goal is generated.
- The review covers final-goal fit, phase ordering, cross-phase dependencies,
  implementation granularity, rollback boundaries, and verification coverage.
- The review identifies whether Phase 11 changes affect later navigation,
  operations-home, run-center, email-delivery, or report-grouping work.
- The review identifies whether Phase 14, Phase 16, or Phase 18 data-model
  decisions need migration, backfill, or compatibility notes before frontend
  work continues.
- The review rejects any plan that can only prove one batch is safe while
  leaving the overall roadmap too coarse or disconnected to reach the final
  console goal.

## Phase 11 Frontend Design System Tests

Phase 11 must be verified in smaller batches.

### Phase 11A Module Boundary And Token Tests

- `api/webui/monitor/monitor.css` exists.
- `api/webui/monitor/monitor.js` exists.
- `/monitor` loads the local CSS and JS assets with HTTP 200.
- Existing inline CSS/JS remains in place unless the batch explicitly migrates
  a section.
- CSS custom-property tokens exist for color, typography, spacing, radius,
  shadow, z-index, status colors, and breakpoints.
- Phase 11A token variables use new namespaces such as `--color-*`,
  `--space-*`, and `--font-*`.
- Phase 11A does not define legacy inline aliases such as `--bg`, `--surface`,
  `--primary`, or `--radius`.
- `monitor.css` is loaded before the inline style block so Phase 11A cannot
  override current visible UI.
- `monitor.js` is loaded after the inline script block.
- `monitor.js` does not execute visible UI logic in Phase 11A.
- `monitor.js` does not define global variables or functions in Phase 11A.
- No intentional visible UI change is introduced in Phase 11A.
- Desktop 1440px layout is unchanged.
- Tablet 1024px layout is unchanged.
- Mobile 390px layout is unchanged.
- Login, logout, navigation, task list, run center, and report preview still
  work.

### Phase 11 Core Function Protection Checklist

Run the relevant parts of this checklist after each Phase 11 batch:

- authentication:
  - administrator login/logout;
  - normal-user login/logout where test credentials are available;
  - session restore.
- navigation:
  - page switching across core pages;
  - administrator menu visibility;
  - normal-user menu visibility;
  - Resource Management and System Configuration entry behavior until Phase 12
    replaces the current structure.
- monitoring tasks:
  - task list loading;
  - task creation wizard entry;
  - task editing where available;
  - task deletion confirmation;
  - manual run trigger.
- run center:
  - run list loading;
  - run status display;
  - run log modal;
  - run log refresh, copy, and download.
- report center:
  - report list loading;
  - report preview switching;
  - report download links;
  - lead detail inspection.
- administrator resources:
  - account list and account detail modal;
  - account QR login entry;
  - proxy list and edit/test flows where available;
  - AI access and AI rule pages;
  - mail configuration and mail-template pages;
  - runtime settings and system diagnostics pages.
- overlays and feedback:
  - modal open/close;
  - form validation messages;
  - confirmation dialogs;
  - toast notifications.
- end-to-end smoke paths:
  - create task entry -> run center -> report center;
  - administrator account login entry -> account status;
  - mail test entry -> result feedback.

### Phase 11B Base Layout And Navigation Visual Tests

- Base shell, header, navigation, button, card, and toolbar styling loads from
  `monitor.css`.
- Desktop 1440px layout is visually stable and follows the accepted
  low-noise Apple-style direction.
- Administrator and normal-user menu visibility remain unchanged.
- Navigation switching, login/logout, task list, run center, and report center
  remain usable.
- There are no obvious regressions in modal layout or table scrolling on
  desktop.

### Phase 11C Interaction And Floating Menu Tests

- Standard toast, loading, empty-state, modal, and action-menu styles exist.
- `MonitorUI` or an equivalent helper boundary exists for shared UI behavior.
- Floating row menus use fixed or portal-style positioning rather than being
  clipped inside table scroll containers.
- Row menus close on outside click, escape, page change, and successful action.
- Account, proxy, report, AI, mail-template, and modal-contained row menus are
  not clipped.
- Existing toast, modal, save/test/run/stop/resend, and report-download flows
  still work.
- If a lightweight floating library is introduced, it is recorded in
  `DECISIONS.md` before implementation.

### Phase 11D Responsive Foundation Tests

- Responsive rules cover desktop `>= 1280px`, tablet `768px - 1279px`, and
  mobile `< 768px`.
- Desktop 1440px, tablet 1024px, and mobile 390px views have no severe
  overlapping text or controls.
- Mobile navigation is usable by touch and does not depend on hover.
- Mobile navigation opens from a hamburger button and closes predictably, or
  the chosen equivalent touch-safe pattern is documented before implementation.
- Toolbars, form grids, metric grids, modals, and dense tables remain usable on
  tablet and mobile.
- Dense tables are at least scroll-safe on mobile; page-specific card
  conversion can be completed in later phases.
- Primary actions and modal action buttons remain reachable on mobile.

## Phase 12 Navigation And Page Entry Tests

### Phase 12A Navigation Structure And Login Landing Tests

- Login success opens the operations home.
- Session restore opens an allowed page and can return to operations home.
- Administrator navigation includes operations home, monitoring, run center,
  report center, resource management, and system configuration.
- Normal-user navigation includes only permitted user-facing pages.
- Resource Management and System Configuration use expandable navigation
  groups instead of detached hover-only popovers.
- User identity and logout are grouped in the top-right account area on
  desktop and remain reachable on mobile.
- Mobile navigation can open, close, select nested pages, and preserve active
  state without clipped menus.

### Phase 12B Page Entry And Role Flow Tests

- Page title, description, primary action, and toolbar structure are consistent
  across core pages.
- Task-loop shortcuts lead to create task, run center, report center, email
  delivery status, and relevant resource issue pages.
- Administrator and normal-user paths are tested separately.
- Normal users do not see hidden administrator resource details through page
  entries, shortcuts, or empty states.
- Existing role and owner-scope tests still pass.

## Phase 13 Overview Operations Home Tests

### Phase 13A Operations Home Data Layer Tests

- Operations-home API returns task health, run activity, report activity,
  email delivery status, suspected lead metrics, and concise resource health
  using real persisted data or documented empty states.
- Administrator aggregates can include workspace-wide resource health.
- Normal-user aggregates are scoped to the user's own tasks, runs, reports,
  and business-safe signals.
- Existing `/api/monitor/dashboard` consumers remain compatible during the
  migration or the response version is documented.
- Missing metrics are represented as unavailable or empty, not fabricated.

### Phase 13B Operations Home Desktop Visual Tests

- Operations home shows task health, run activity, report activity, email
  delivery status, suspected lead metrics, and resource health summary.
- Long scheduler, platform, browser, or deployment diagnostic blocks do not
  dominate the home page.
- Metrics provide drilldown links to Monitoring, Run Center, Report Center, or
  administrator resource pages.
- Page-level refresh updates operations-home data and shows last-updated time.

### Phase 13C Operations Home Responsive And Role Tests

- Normal users only see own task/report/run health and business-safe resource
  signals.
- Desktop 1440px, tablet 1024px, and mobile 390px layouts have no severe
  overlap, hidden primary actions, or unreadable metric cards.
- Administrator resource health drilldowns remain hidden from normal users.

## Phase 14 Run Center Data Model Tests

- `crawl_runs` has `visibility`, `run_type`, `archived_at`, and `archived_by`.
- Existing runs are backfilled with `visibility = visible` and
  `run_type = scheduled`.
- Valid `visibility` values are `visible` and `archived`.
- Valid `run_type` values are `scheduled`, `manual`, and `test`.
- Migration keeps existing runs, logs, report links, and current status values
  readable.

## Phase 15 Run Center Governance Tests

### Phase 15A Run Center API And Data Governance Tests

- Run API/query layer supports pagination.
- Run API/query layer supports filters for task/law firm, status, platform, run
  type, visibility, and date.
- Default list hides archived records.
- Administrators can view archived records through an explicit filter.
- Archive changes visibility without physically deleting the run.
- Restore returns the run to the default visible list.
- Owner/workspace scope is preserved for paginated and filtered results.
- Existing run logs, report links, and status values remain readable.

### Phase 15B Run Center Frontend Tests

- Run center shows pagination controls.
- Run center exposes filters for task/law firm, status, platform, run type,
  visibility, and date.
- Archive and restore row actions require confirmation.
- Test/noise records can be filtered separately from scheduled/manual runs.
- Run logs remain refreshable, copyable, and downloadable.
- Desktop, tablet, and mobile layouts keep status and actions reachable.

## Phase 16 Email Delivery Data Model Tests

- `email_delivery_logs` exists with workspace, job, report, window key, send
  type, sender, sent time, status, error, recipients, and created time fields.
- Automatic send rows use `send_type = auto`.
- Manual resend rows use `send_type = manual_resend`.
- `daily` send-window keys use `{job_id}_{YYYY-MM-DD}`.
- `6h`, `12h`, and `cron` send-window keys use
  `{job_id}_{YYYY-MM-DD}_{HH}`.
- Existing `reports.email_status` and `reports.email_error` remain readable as
  latest-state compatibility fields.
- Delivery logs do not store SMTP secrets.

## Phase 17 Email Delivery Governance Tests

### Phase 17A Email Idempotency And Delivery Logic Tests

- Repeating the same automatic scheduler window does not send duplicate emails
  for the same job and `send_window_key`.
- Manual resend is allowed after an automatic send and creates a separate
  delivery log.
- Failed automatic delivery is recorded and does not block report generation.
- `send_window_key` generation matches `daily`, `6h`, `12h`, and `cron`
  rules.
- Delivery logs store recipient summaries and customer-safe errors without SMTP
  secrets.

### Phase 17B Email Delivery History Frontend Tests

- Report center shows latest delivery state and delivery history.
- Normal-user resend permissions remain owner-scoped.
- Administrator can inspect delivery failures without seeing SMTP secrets.
- Manual resend UI requires confirmation and updates the latest status/history.
- Desktop, tablet, and mobile report-center delivery surfaces remain usable.

## Phase 18 Report Center Task Grouping Tests

### Phase 18A Report Job Snapshot Data Model Tests

- `reports.job_snapshot_json` is created for new reports.
- Existing reports with resolvable `job_id` are backfilled with recoverable task
  context.
- Reports with unrecoverable context remain readable as limited-context
  historical reports.
- Snapshot content never bypasses owner/workspace filtering.

### Phase 18B Report Center Task Grouping Frontend Tests

- Active-task reports group under their monitoring task.
- Deleted or missing-task reports group using `job_snapshot_json`.
- Orphan reports show law firm, platform, keyword, frequency, and deleted-task
  context when available.
- Reports with no recoverable snapshot remain visible as historical reports
  with limited context.
- Switching selected reports still updates preview and lead details.
- Owner/workspace filtering is enforced for grouped and orphan reports.
- Report downloads, email delivery status/history, and row actions continue to
  work after grouping.
- Desktop, tablet, and mobile grouped-report layouts keep report selection and
  primary actions reachable.
