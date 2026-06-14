# Test Plan

## General Rule

Production acceptance must run in a server-like environment. Local Chrome on
the operator's computer is not a valid acceptance path.

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

## Server-Like Acceptance Tests

- Start the system in a container or Linux server-like environment.
- Access the web UI through an HTTP domain or localhost server URL.
- Complete QR login through the web UI.
- Run a task using the server-side browser/profile.
- Restart service/container and verify profile reuse.
- Verify no acceptance step depends on local Chrome.
