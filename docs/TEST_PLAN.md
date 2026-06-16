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
- QR session failure, timeout, or disappeared browser-session states are
  reconciled against the same account/Profile; if MediaCrawler account
  validation passes, the session must display login success.
- Douyin, Xiaohongshu, and Kuaishou use the same login-success reconciliation
  behavior without bypassing captcha, slider, SMS, or manual verification.
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

## Phase 7.1 Run Lifecycle Stuck Recovery Regression Tests

Phase 7.1 is a follow-up regression-fix test set. It does not rewrite the
historical Phase 7 verification; it adds coverage for the newly observed stuck
run class.

### Phase 7.1A Run Identity Compatibility Tests

- New runs persist `crawl_runs.job_id` in the column.
- New run creation fails safe or logs a redacted actionable error if `job_id`
  cannot be persisted, instead of silently creating a new gap.
- Running-run lookup finds rows by real `job_id`.
- Legacy running-run lookup finds rows by `summary.job_id` when the column is
  null and the task still exists.
- Stopping by `run_id` works when `job_id` is null.
- Safe backfill dry-run lists only rows whose `summary.job_id` resolves to an
  existing `monitor_jobs.id`.
- Backfill skips unresolved historical rows without mutating them.

### Phase 7.1B Finalization And Recovery Tests

- Repeated finalization calls for the same `run_id` are idempotent.
- Concurrent finalization calls write only one terminal state and do not revert
  a terminal row to `running`.
- Resource-lock release is safe when finalization is repeated.
- Background task exceptions are logged with `run_id`, compatible `job_id`,
  phase/progress snapshot, and redacted error text.
- Step-level run summary records phase, phase started time, progress heartbeat,
  retry state, last safe result or return value, and redacted last error for
  frontend diagnosis.
- Stale recovery does not mark a run interrupted from elapsed time alone; it
  checks live task evidence, resource locks, heartbeat age, retry state, and
  last step result/error.
- Retryable platform/browser/network failures follow the confirmed retry policy
  before timeout or fallback finalization.
- Stale-heartbeat grace period defaults to 10 minutes and can be configured
  through the confirmed runtime setting.
- Stale running run before `deadline_at` with no locks and old heartbeat is
  marked `interrupted` after the confirmed evidence checks and grace period.
- Service restart during AI evaluation triggers startup/scheduler recovery when
  no live task evidence remains.
- Existing deadline timeout behavior still marks overdue runs as `timeout`.

### Phase 7.1C AI Fallback And Partial Report Tests

- AI invalid JSON saves `pending_review` and continues.
- AI per-item timeout defaults to 120 seconds, is capped by the remaining run
  deadline, retries according to the confirmed AI item retry budget, then saves
  `pending_review` and continues.
- AI unexpected per-item exception saves `pending_review` and continues.
- AI progress counts include total candidates, successful evaluations,
  failed/fallback evaluations, pending-review items, and unresolved items.
- A simulated run with 271 collected content IDs and interruption at item 251
  must not remain `running`.
- A full AI provider failure still generates a report with manual-review leads
  when collected content exists.
- Report-generation failure after AI progress produces a terminal redacted
  failure state.
- Partial report reads preserve owner/workspace scope for normal users and
  administrator-wide visibility for administrators.
- Progress messages and finalization exception logs redact API keys, cookies,
  proxy credentials, profile paths, provider endpoints, local paths, and
  commands.

### Phase 7.1D Current Run Remediation Tests

- Historical run remediation requires explicit operator confirmation.
- Remediation scripts or helpers support a dry-run or preview mode.
- Remediation instructions require database backup and rollback steps before
  modifying run `8317`.
- Repair mode can create pending-review rows for the remaining 21 contents and
  generate a partial report only after code safety is verified.

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
- Platform Account, Monitoring Task, and AI Evaluation Rule row menus render
  popup content from page-level floating containers, not inline table rows.
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
- Effective-recipient resolution is tested for both cases: task recipients
  override global default recipients, and global default recipients are used
  only when the task recipient list is empty.
- Delivery logs record the final effective recipients and the recipient source
  without exposing SMTP secrets.

### Phase 17B Email Delivery History Frontend Tests

- Report center shows latest delivery state and delivery history.
- Normal-user resend permissions remain owner-scoped.
- Administrator can inspect delivery failures without seeing SMTP secrets.
- Manual resend UI requires confirmation and updates the latest status/history.
- Desktop, tablet, and mobile report-center delivery surfaces remain usable.

## Phase 17.1 Email Delivery Safety Regression Tests

Phase 17.1 is a follow-up regression-fix test set. It does not rewrite the
historical Phase 17 verification; it adds coverage for real SMTP side-effect
safety in tests, local diagnostics, and explicitly opted-in production/pilot
delivery.

### Phase 17.1A Real SMTP Safety Gate Tests

- Routine automated tests and local diagnostics cannot create hidden real SMTP
  side effects.
- With a complete real SMTP configuration in the active database but no
  `MONITOR_ALLOW_REAL_EMAIL_SEND=true`, automatic report delivery is skipped
  with a customer-safe reason and report generation still succeeds.
- With `MONITOR_ALLOW_REAL_EMAIL_SEND=true`, production/pilot automatic
  delivery or a dedicated real-mail validation action can call the real mailer
  when SMTP configuration is complete.
- Manual resend follows the confirmed safety-gate behavior for local/test and
  production/pilot modes.
- Mail test follows the confirmed safety-gate behavior and never exposes SMTP
  passwords, authorization data, or full provider errors.

### Phase 17.1B Test Isolation Tests

- `test_run_job_blocks_platform_when_login_window_is_open` cannot reach real
  SMTP while still verifying that a login-window-open platform is blocked and
  summarized in the report.
- A suite-level SMTP tripwire fails the test if `smtplib.SMTP` or
  `smtplib.SMTP_SSL` is reached without explicit opt-in.
- `run_monitor_job` tests that are not testing email delivery use mocked or
  skipped delivery outcomes.
- The full monitoring test suite can run with real-looking SMTP configuration
  and default recipients present in the database without sending external mail.
- A real-mail validation test path or runbook is skipped by default and
  requires explicit opt-in before sending.

### Phase 17.1C Effective Recipient Traceability Tests

- Delivery logs record final effective recipients for task-specific recipients.
- Delivery logs record final effective recipients when the system falls back to
  global default recipients.
- Delivery logs distinguish `recipients_json` as the task/request recipient
  snapshot from `effective_recipients_json` as the final resolved recipient
  list.
- Delivery logs record `effective_recipient_source` as `task_recipients`,
  `global_default_fallback`, test target, or another confirmed source.
- Delivery logs record trigger source for scheduler auto-send, manual resend,
  mail test, diagnostic, or explicit validation paths.
- Skipped deliveries caused by the safety gate record the effective-recipient
  source or a confirmed customer-safe equivalent without SMTP secrets.
- Existing automatic-send idempotency by schedule window remains unchanged.

### Phase 17.1D Historical Orphan Evidence Tests

- A read-only orphan-review helper or checklist can identify delivery logs
  whose `job_id` or `report_id` no longer resolves to active rows.
- `docs/SERVER_DEPLOYMENT.md` and `docs/deployment_runbook.md` describe the
  operator path for preserving unexpected-email evidence, backing up before
  mutation, obtaining approval, and recording rollback steps.
- Historical orphan evidence is preserved by default. Any remediation requires
  database backup and explicit operator approval before mutation.
- Existing non-orphan report-center delivery history remains readable after the
  safety fix.

## Phase 17.2 Report Email Template Governance Tests

### Phase 17.2A Effective Template Provenance Tests

- A task-bound email template takes precedence over the active global template,
  and the report snapshot records the task-bound template id, name, subject
  template, and source.
- When a task has no bound template, delivery uses the active global template
  and records the fallback source in the report snapshot and delivery log.
- Phase 17.2A provenance fields can be verified in the same metadata migration
  as Phase 17.1C without requiring the preset-style UI work to be complete.
- Editing or activating another template after delivery does not change the
  historical template metadata shown for the already delivered report.
- Template provenance logs do not store SMTP secrets, API keys, cookies, proxy
  credentials, profile paths, or unsafe raw local paths.

### Phase 17.2B Template Body Guardrail Tests

- A template with neither `{report_html}` nor `{report_body}` is blocked or
  produces a clear warning before it can be used for real report delivery.
- Template editor preview clearly uses sample data, while report-email preview
  or real delivery uses the generated report HTML for the selected run.
- Subject templates continue to interpolate supported fields such as law firm
  name and date.

### Phase 17.2C Preset Style Tests

- Preset email styles render the same system-generated report body with
  different visual wrappers.
- Operators can select a preset style without editing raw HTML.
- Historical free-form templates remain readable for compatibility, but new
  governed presets cannot omit required report sections.

## Deferred Email Delivery Role Governance Tests

CR-037 is deferred and should not block CR-036/Phase 17.1.

- Future administrator email-governance settings distinguish administrator
  authority from normal-user send/resend permissions.
- Normal-user send/resend attempts respect the configured quota or disabled
  policy and return customer-safe messages when blocked.
- Send quota counters are auditable and do not expose SMTP secrets.
- Automatic scheduled delivery and manual resend follow their confirmed
  policy boundaries without breaking existing delivery logs.

## Phase 17.1C Effective Recipient Traceability Tests

- Preflight and delivery UI make recipient precedence understandable: SMTP
  sender is the from-address, task recipients are task-specific targets, and
  global default recipients are fallback-only.
- When task recipients are present, real/fake delivery and logs use only the
  task recipient list as the effective recipients.
- When task recipients are empty, delivery falls back to global default
  recipients and logs that fallback source clearly.
- Existing automatic-send idempotency remains keyed by job/window/send type and
  is not changed by recipient-source display.

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

## Formal Console Full-Coverage Positive UI Optimization Tests

- All formal logged-in pages remain reachable: dashboard, monitoring tasks,
  platform accounts, proxies, AI access, AI evaluation rules, mail
  configuration, mail templates, runtime strategy, run center, report center,
  and system diagnostics.
- Desktop 1440px page sweep has no browser console errors and no horizontal
  page overflow.
- Tablet 1024px and mobile 390px navigation can open, select pages, and close
  automatically after page selection.
- Dashboard shows data and closed-loop status before the 01-05 shortcut flow;
  mobile dashboard uses compressed metrics and closed-loop status.
- Platform account page keeps filters, attention filter, batch actions, row
  details, more menu, QR login, browser login, Cookie login, and login history.
- Monitoring task drawer keeps target, collection, filtering, administrator
  advanced settings, schedule, AI, report, sample-fill, clear, save, and close
  actions.
- Proxy, AI access, AI connection test, AI rule, mail config, mail test, email
  template, run log, and report preview secondary surfaces open and close
  within viewport safe margins.
- Report row more menu keeps delivery history, resend, HTML, Excel, and
  Markdown actions.
- Loading states render as page-shaped skeletons or page-local loading notes
  instead of a single generic spinner.
- Secondary drawers and modals provide button-level loading feedback for
  account QR/Cookie login, login continuation, resource saves, AI tests, mail
  tests, and template preview without removing the original controls.

## Phase 19 Run Center Realtime Progress Tests

### Phase 19A Requirement Intake Classification Tests

- New CR entries from CR-031 onward include a requirement type.
- Existing feature optimization CRs include background, purpose, preserved
  behavior, scope boundary, and acceptance criteria.
- `AGENTS.md`, `AGENT_WORKFLOW.md`, `CHANGE_REQUESTS.md`, and
  `DOCUMENTATION_CHECKS.md` agree on where requirement-classification rules
  live.
- `uv run python scripts/check_docs.py` passes after documentation updates.

### Phase 19B Run Center Progress Data Layer Tests

- A simulated long-running platform crawler with growing JSON or JSONL output
  updates provisional collection progress before the subprocess exits.
- Missing output files, empty files, partially written files, and malformed
  JSON/JSONL are tolerated without crashing the run or marking final counts.
- Provisional progress is stored in `crawl_runs.summary` with a clear marker
  that it is not final ingestion output.
- After the platform attempt exits, final `raw_contents`,
  `filtered_contents`, `excluded_contents`, and `new_contents` values match the
  existing collect-and-ingest semantics.
- Final ingestion does not duplicate existing `raw_contents` rows and still
  respects deduplication, exclusion words, and time-window filtering.
- Timeout runs preserve partial progress and customer-safe timeout wording.

### Phase 19C AI Evaluation Progress Tests

- AI evaluation progress records evaluated count and total candidate count
  during long evaluation batches.
- Suspected negative, high-risk, and manual-review counts update in batches or
  time intervals while AI evaluation is active.
- AI provider failure still marks content for manual review and does not block
  report generation.
- Final AI counts remain exact after the full evaluation loop completes.

### Phase 19D Run Center Frontend Progress And Polling Tests

- Run Center polling continues while visible runs remain active and stops
  after active runs finish, fail, time out, or are cancelled.
- Running rows distinguish collecting, ingesting, AI evaluating, report
  generating, email sending, timed out, cancelled, and complete states where
  the backend provides those states.
- Provisional collection progress is visually distinguishable from final
  counts and is not represented as a false final zero.
- Stop and log actions remain reachable while progress refreshes.
- Administrator and normal-user owner/workspace scope remains intact.
- Desktop 1440px, tablet 1024px, and mobile 390px Run Center layouts have no
  severe overlap, clipped actions, hidden progress, or unreadable status text.

## Phase 20 Run Detail And AI Evaluation Traceability Tests

Phase 20 is blocked until CR-034 confirmation items are resolved. After
confirmation, use the following tests as the implementation gate.

**Do not implement or execute Phase 20A-20E implementation tests until CR-034
changes from Needs Confirmation to Accepted.** Documentation review of the
blocked plan is allowed; code/schema/API changes are not.

### Phase 20A Confirmation And Data Model Tests

- Confirmed permission rules distinguish normal-user business-safe evaluation
  detail from administrator debug detail.
- Confirmed retention and size limits are documented before trace snapshots are
  stored.
- The accepted schema creates the chosen trace-storage shape and keeps old
  `ai_evaluations` rows readable.
- Migration does not expose API keys, authorization headers, cookies, proxy
  credentials, profile paths, or server-local paths.

### Phase 20B AI Trace Persistence Tests

- A new successful AI evaluation persists a trace snapshot with business input
  payload, prompt/request snapshot, provider/model metadata, structured output,
  raw/redacted response, duration, and timestamps.
- A failed or fallback AI evaluation persists the error/fallback detail needed
  for operator diagnosis without leaking secrets.
- Old evaluations without trace snapshots return an explicit limited-context
  state rather than reconstructed "exact" input.
- Stored prompt/request/response fields are capped or truncated according to
  the confirmed size policy.

### Phase 20C Run Detail API Tests

- Run detail API returns lifecycle summary, crawler logs, content list, AI
  evaluation list, and report/email links for the selected `run_id`.
- AI evaluation list supports pagination and filters for status, risk,
  platform, keyword, and content title.
- Per-evaluation detail API returns input/output trace fields according to the
  caller's role and owner/workspace scope.
- Normal users cannot read other users' run details or administrator-only debug
  fields.

### Phase 20D Run Detail Frontend Tests

- Run Center row has a clear "details" entry for the selected run.
- Run detail view groups Overview, Collection Logs, Collected Contents, AI
  Evaluation, Report, and Email Delivery in one surface.
- AI Evaluation tab lists every evaluation candidate/result for the run before
  and after report generation.
- Evaluation detail drawer/page shows business input and structured output for
  normal users and confirmed debug fields for administrators.
- Desktop 1440px, tablet 1024px, and mobile 390px views keep run detail,
  evaluation list, and evaluation detail readable.

### Phase 20E Report Center Lead Entry Tests

- Report rows or report groups expose an explicit "view leads" action separate
  from report preview.
- Report lead detail can link back to the originating run detail when `run_id`
  is available.
- Report Center remains focused on final report artifacts, downloads, email
  delivery history, and report-scoped leads.

## CR-038 Sticky Drawer Close Control Tests

- In a long task edit drawer, scrolling to the middle and bottom keeps the
  top-right close button visible and clickable.
- Backdrop click-to-close remains available where the drawer already supports
  it.
- Bottom save/close action bars remain reachable and do not overlap with the
  sticky drawer header.
- Account, proxy, AI profile, mail config, mail template, run log, and report
  preview drawers keep close controls reachable when their content scrolls.
- A long task drawer with an in-drawer dropdown or floating menu open does not
  let the sticky header cover the dropdown, and the dropdown does not hide the
  close button when closed.
- Desktop 1440px, tablet 1024px, and mobile 390px checks show no severe overlap,
  clipped close controls, or hidden form content caused by the sticky header.

## Phase 21 Formal Console Page-Level UI/UX Refinement Tests

Phase 21 is an accepted frontend-only refinement phase for the formal
`/monitor` console. These tests are the implementation gate for Phase 21A-21P.
Before making Phase 21 code changes, implementers must read
`docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md`; it defines the per-page
preservation rules, allowed refinements, forbidden changes, and acceptance
standards. Phase 21 must be implemented as small workstreams A-O with local
smoke checks, then finalized through Phase 21P cross-page verification.

### Phase 21 Planning Document Tests

- `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` exists.
- The plan identifies the formal frontend baseline files.
- The plan states that the static prototype is visual reference only.
- The plan lists hard boundaries: no backend API, database, permission,
  crawler, AI-provider, SMTP, scheduler, deployment, framework, or build-step
  changes.
- The plan covers every existing formal page:
  login, dashboard, monitoring tasks, platform accounts, proxies, AI access,
  AI evaluation rules, mail configuration, mail templates, runtime strategy,
  run center, report center, and system diagnostics.
- The plan covers major secondary surfaces:
  task drawer, account dialog, proxy drawer, AI connection-test modal, AI
  profile drawer, AI rule modal, mail config modal, mail test modal, email
  template drawer, run log drawer, report preview drawer, and row more menus.
- The plan states preserved behavior, allowed refinement, forbidden changes,
  verification method, and acceptance standard for each page or workstream.
- The plan explicitly excludes the currently unrendered `Users And Permissions`
  page from Phase 21 and requires a separate new-capability CR if that page is
  later implemented.

### Phase 21 Static Verification Tests

- `node --check api/webui/monitor/monitor.js` passes.
- Inline script parse check for `api/monitor_web/index.html` passes.
- `uv run python scripts/check_docs.py` passes.
- Targeted frontend tests covering formal console pages, CR-033 regressions,
  secondary overlay loading feedback, floating menus, and responsive hooks pass.

### Phase 21 Functional Coverage Tests

- All formal logged-in pages remain reachable:
  dashboard, monitoring tasks, platform accounts, proxies, AI access, AI
  evaluation rules, mail configuration, mail templates, runtime strategy, run
  center, report center, and system diagnostics.
- Login page preserves email, password, login, loading, and failed-login
  feedback.
- Operations Home preserves all five shortcuts while prioritizing operational
  data and urgent state.
- Monitoring preserves filters, row actions, task more menu, task drawer
  fields, sample fill, clear, save, and close.
- Platform Accounts preserves QR login, local-window fallback where allowed,
  Cookie login, login records, account details, attention filter, filters,
  batch actions, row detail, and row more menu.
- Proxies preserve add, refresh, filters, edit, delete, drawer fields, save,
  clear, and close.
- AI Access preserves model list fetch, connection test modal, default switch,
  delete, drawer fields, save, clear, and close.
- AI Evaluation Rules preserve row more menu, test, set default, delete, rule
  modal sections, prompt preview, test sample, result, restore default, save,
  and close.
- Mail Configuration preserves edit, test, refresh, delivery shortcut, masked
  password, save, cancel, and close.
- Mail Templates preserve list filters, edit, set current where available,
  delete, variables, HTML editor, iframe preview, save, refresh preview, clear,
  and close.
- Runtime Strategy preserves grouped tables, current value, input, range, apply
  scope, lock state, refresh, save, and diagnostics shortcut.
- Run Center preserves all filters, pagination, log drawer, stop, archive,
  restore, refresh logs, copy logs, download logs, and close.
- Report Center preserves filters, grouping, preview, lead detail, delivery
  history, resend, HTML/Excel/Markdown downloads, refresh status, refresh
  history, and report preview drawer.
- System Diagnostics preserves rerun diagnosis, run system diagnosis, handle
  account resources, readiness/action cards, runtime state, scheduler state,
  and platform state.

### Phase 21 Browser And Responsive Tests

Desktop `1440x900`:

- administrator can visit every page and open every major drawer/modal/menu;
- normal user sees only permitted pages;
- no browser console errors;
- no horizontal page overflow;
- row more menus are not clipped;
- dashboard closed-loop, shortcut, metric, and resource-health cards do not
  squeeze labels into one-character vertical columns, overlap content, or hide
  primary actions.

Tablet `1024x768`:

- navigation opens, selects nested pages, and closes;
- page headers and toolbars wrap without hidden primary actions;
- drawers and modals fit inside viewport safe margins;
- floating menus remain reachable and unclipped;
- four-column or dense card groups wrap, stack, or switch to compact rows before
  text becomes unreadable.

Mobile `390x844`:

- Operations Home shows key status and next action before long guidance;
- navigation reaches all allowed core pages;
- task drawer, account dialog, run log drawer, and report preview drawer can
  scroll and close;
- report preview and delivery history remain readable;
- no overlapping text, one-character-per-line wrapping, unreachable action
  buttons, or horizontal overflow.

Layout stress inputs:

- Test long law-firm names, platform names, external account labels, failure
  reasons, email status text, report titles, and run summaries.
- Check dashboard cards, closed-loop/trajectory cards, metric cards, resource
  cards, run/report dense cards, and loading/empty/error states.
- Pass example: on mobile `390x844`, `北京市海淀区恒泰律师事务所` wraps as readable
  multi-character lines inside an Operations Home card and the card action
  remains reachable.
- Pass example: on desktop `1440x900`, a task -> run -> report -> email
  closed-loop track wraps or switches to compact rows before step labels become
  narrow columns.
- Fail example: labels render as vertical single-character columns such as
  `任 / 务 / 配 / 置`, content overlaps neighboring cards, required buttons are
  clipped, or the page requires horizontal scroll.
- The batch fails if any module shows text as one Chinese character per line,
  clips action buttons, overlaps neighboring content, or requires horizontal
  page scroll at the accepted viewports.

### Phase 21 Acceptance Tests

- No page, button, drawer, modal, floating menu, filter, batch action, row
  action, confirmation flow, or download action is removed without a separate
  accepted CR.
- Visual hierarchy is measurably clearer than the CR-033 baseline in browser
  screenshots or review notes.
- Operations Home reads as a daily operations cockpit rather than onboarding.
- Platform Accounts remains a complete account-maintenance workflow.
- Run Center and Report Center remain usable under dense operational data.
- Dashboard, run/report, resource, and overlay screenshots demonstrate layout
  resilience: readable text, stable card widths, reachable buttons, no text
  collapse, and no horizontal overflow at `1440x900`, `1024x768`, and
  `390x844`.
- All implementation verification is recorded in `docs/TEST_RESULTS.md` after
  code changes are actually made and tested.
