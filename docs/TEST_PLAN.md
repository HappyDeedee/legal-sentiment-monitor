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

## Role And Permission Tests

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
- Creating a second account on the same platform does not reuse the first
  profile.
- Same account cannot run two tasks at the same time.
- Same profile cannot run two tasks at the same time.
- Task-bound proxy overrides account proxy.
- Account proxy is used when task proxy is absent.
- Proxy concurrency limit is respected.

## Run And Report Tests

- A task can run with AI configured.
- A task can run without AI and mark leads as manual review.
- A task can run without email and still generate a report.
- One platform failure does not block other platforms.
- Run logs can be refreshed, copied, and downloaded.
- Different report previews switch correctly.
- Report wording uses suspected negative leads and avoids factual conclusions.

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
