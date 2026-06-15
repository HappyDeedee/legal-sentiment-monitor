# Test Results

This file records verification outcomes. Add new entries at the top.

How to read this file:

- entries are reverse chronological, newest first;
- use the topmost relevant entry for current status;
- older entries are historical snapshots and may mention states that were later
  superseded by newer entries above them;
- use `docs/CURRENT_STATE.md`, `docs/CHANGE_REQUESTS.md`, and
  `docs/TRACEABILITY.md` for final current-state decisions.

## 2026-06-14 - Phase 9 Security And Operations Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and automated readiness/doctor
diagnostic checks.

Result:

- Added minimal administrator-operation audit logging for resource and
  security-sensitive operations, including platform login configuration,
  platform accounts, login sessions, proxy resources, AI profiles/rules, mail
  configuration/templates, runtime settings, and administrator-triggered report
  resend.
- Kept audit details intentionally small and non-secret; tests verify API keys,
  SMTP passwords, proxy credentials, and cookies are not written to audit
  logs.
- Hardened sensitive text redaction for encrypted-field names, proxy URLs, and
  Chinese secret labels such as password, key, token, cookie, and proxy address.
- Added account invalidation and proxy-error alert paths to readiness checks.
- Added disk-space, retention-setting, backup-set, and resource-alert checks to
  doctor diagnostics.
- Updated deployment guidance so database, account profiles, reports,
  encryption key, and deployment configuration are explicit backup targets.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_9 or doctor_reports_deployment_diagnostics or readiness_status_reports_checks or sensitive_text_is_redacted"`
- Result: 6 passed, 210 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 216 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed.

Limitations:

- Phase 9 does not add automated retention cleanup jobs; retention settings and
  diagnostics are visible, while cleanup execution remains future operations
  work.
- Real account invalidation, proxy-provider behavior, SMTP delivery, AI
  provider behavior, and platform crawling still require live pilot validation.

## 2026-06-14 - Phase 8 Server-Like Validation Verified

Environment: isolated server-like service process in local worktree
`E:\myproject\MediaCrawler-worktrees\v1-roadmap` using `uv run`, a temporary
persistent data directory, real FastAPI/uvicorn HTTP service startup,
production login flags, and headless Playwright Chromium.

Result:

- Added `scripts/server_like_validation.py` to start the real FastAPI app with
  isolated persistent data/profile roots and production-oriented environment
  flags.
- Verified `/monitor` is reachable over HTTP and a bootstrap administrator can
  log in through the API.
- Verified web QR/status login capability is advertised as the primary
  `server_qrcode` flow while local-window login is hidden and blocked with
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.
- Verified two same-platform accounts receive separate `profile_key` values
  and runtime profile paths under the persistent account-profile root.
- Verified profile metadata survives service restart.
- Verified account/profile locks and proxy concurrency limits through the
  runtime lock APIs, with proxy locks backed by `resource_locks`.
- Verified the automated validation path does not require the operator's local
  Chrome and that Playwright Chromium can launch headless.

Verification:

- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed.

Limitations:

- Docker/container validation could not be performed on this machine, so Phase
  8 used an isolated real service process as the server-like path.
- The automated run verifies the web QR/status path and production local-login
  gating, but it does not complete a real platform QR scan or real platform
  crawl with a live account.
- Real AI provider, SMTP, platform login, and platform crawling behavior remain
  deployment/pilot validation risks.

## 2026-06-14 - Phase 7 Runs Reports And AI Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Verified that a monitoring run can finish and generate a report when AI is
  disabled and email sending is unavailable.
- Verified AI-disabled or AI-failure content is stored as `pending_review`
  manual-review material instead of blocking report generation.
- Verified report wording keeps "疑似负面线索" and "AI 仅作线索筛查，不代表事实认定"
  semantics.
- Verified selected report previews load leads scoped by `report_id`.
- Verified run-log UI keeps refresh, copy, and download controls and log API
  output remains customer-safe.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 213 passed, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7 or pending_review or report_scope or monitor_page_uses_tob"`
- Result: 4 passed, 209 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 7 verification uses local and mocked execution paths where external
  platform, AI provider, or SMTP behavior would otherwise be required.
- Real provider/SMTP reliability and end-to-end server deployment remain pilot
  and Phase 8 validation risks.

## 2026-06-14 - Phase 6 Server Login Flow Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Made server-side QR login the primary administrator account-login flow.
- Added structured login-session states: `preparing`, `waiting_qrcode`,
  `waiting_scan`, `waiting_confirm`, `success`, `needs_verification`,
  `qrcode_failed`, `timeout`, and `platform_error`.
- Normalized legacy login states for compatibility while returning structured
  states to the API and frontend.
- Kept login sessions tied to Phase 5 `profile_key` runtime paths, closed the
  server browser after successful login, and re-checked existing profiles
  before marking accounts active.
- Hid local-window login controls and blocked the local-window login endpoint
  when `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.
- Updated deployment and account-environment documentation for the production
  login boundary.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 212 passed, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "login_session or qrcode or phase_6 or local_login"`
- Result: 34 passed, 178 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m py_compile api/monitoring/database.py api/monitoring/login_qrcode.py api/monitoring/login_status.py api/routers/monitor.py`
- Result: Python compile check passed.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 6 verification is local and mocked where platform login would require
  real QR scanning. It does not replace Phase 8 server-like acceptance.
- Service/container restart validation, no-local-Chrome production acceptance,
  and real profile reuse across restart remain Phase 8 tasks.

## 2026-06-14 - Phase 5 Account Environment Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Added a `profile_key` runtime path resolver for
  `{workspace_id}/{platform}/acc_{account_id}` account profiles.
- Changed new account environments so arbitrary submitted profile paths are not
  the account identity; account names remain display-only.
- Kept real profile paths internal to crawler/login/check code paths while
  customer-facing account, run, and login-session responses use profile-key or
  configured-state wording instead of raw server paths.
- Added account/profile lock acquisition and release through
  `social_accounts.locked_by_run_id`, `locked_at`, and `lock_expires_at`.
- Added proxy concurrency control through `resource_locks` with
  `proxy_profiles.max_concurrency`.
- Added startup and scheduler recovery for timed-out running runs and persisted
  locks, releasing locks only after the owning run is terminal or recovered.
- Ensured account-bound proxy information is passed into both login command
  preparation and crawler execution.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 211 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 5 does not implement the full Phase 6 structured server-login state
  machine or production-mode local-login hiding.
- Phase 5 does not complete server-like acceptance validation; profile reuse
  across service/container restart remains Phase 8 acceptance work.

## 2026-06-14 - Phase 4 Normal User Task Wizard Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Replaced the normal-user task creation experience with a four-step wizard:
  target, collection content, schedule, and report.
- Included law firm, aliases, platform search terms, selected platforms, crawl
  range, comment collection, frequency/send time, enabled state, and recipient
  emails in the normal-user path.
- Added crawl range copy explaining that max items is a content-count cap,
  start page and max pages depend on platform behavior, and task timeout is
  controlled by administrator Runtime Strategy.
- Hid account binding, proxy binding, AI access override, email template
  override, output mode, target type, and browser mode from normal users.
- Added API-side normal-user payload cleanup so advanced task fields are
  ignored even if a normal user submits them directly.
- Kept administrator advanced task settings available and verified that
  administrator submissions still persist advanced bindings.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 207 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 4 does not implement Phase 5 account/profile/proxy runtime locking or
  `profile_key` path resolution.
- Phase 4 does not make server-side QR login the primary production login
  flow; that remains Phase 6 after the account environment is complete.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Phase 3 Administrator Resource Center Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Refined the administrator resource center UI for platform accounts, proxy
  resources, AI access, mail configuration, and mail templates.
- Kept platform accounts in the existing account-detail dialog with account
  resource metrics, filters, login maintenance, Cookie maintenance, proxy
  binding, bulk actions, and customer-safe login state text.
- Added proxy resource summary cards, search/status filters, and consistent
  modal action footer for create/edit.
- Added AI access summary cards, search/protocol/test-status filters,
  consistent modal action footer for create/edit, and retained the dedicated
  connection-test dialog without exposing raw API keys.
- Changed mail configuration to use edit/test dialogs, summary cards, masked
  password behavior, and a test console that records success or failure without
  blocking report generation.
- Added mail-template summary cards, search/status filters, live preview, and
  consistent modal actions.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 206 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 3 is a resource-center UI and interaction refinement. It does not
  implement Phase 4 simplified normal-user task wizard, Phase 5
  profile-key/lock runtime behavior, Phase 6 primary server-side login flow, or
  Phase 8 server-like acceptance validation.
- Proxy connection testing remains outside Phase 3 because the current product
  and API surface only define create/edit/disable/delete for proxy resources;
  no new proxy test requirement was accepted in this phase.

## 2026-06-14 - Phase 2 System Settings Center Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Added database-backed runtime settings with defaults, `monitor.yaml` loading,
  database overrides, validation ranges, apply scopes, environment locks, and
  audit logging.
- Added administrator-only `/api/monitor/runtime-settings` read/update APIs and
  a grouped Runtime Strategy page for Crawling, Login, Scheduler, and
  Retention settings.
- Kept Runtime Strategy inaccessible to normal users through both API role
  checks and menu permissions.
- Moved scheduler tick/disable, global crawl concurrency, per-platform
  concurrency, crawler timeout, crawler retry count/delay, QR timeout, login
  session TTL, lock cleanup buffer, and retention settings into the runtime
  settings layer.
- Changed newly started crawl runs to store `timeout_seconds` and
  `deadline_at`, allocate remaining run time to platform crawler attempts, and
  mark deadline-exceeded runs as `timeout` while preserving partial platform
  summaries.
- Updated safe environment examples with the deployment-lock variables for
  Phase 2 runtime settings.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 206 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 2 does not implement Phase 3 administrator resource-page refinements,
  Phase 4 simplified normal-user task wizard, Phase 5 persisted
  account/profile/proxy lock acquisition, or Phase 6 primary server-login flow.
- Retention settings are configurable and visible, but automated cleanup jobs
  remain for later operations work.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Phase 1 Users And Permissions Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Implemented environment-bootstrap administrator creation and bcrypt password
  hashing.
- Added session-based authentication with HTTP-only `monitor_session` cookie
  and hashed session tokens in `user_sessions`.
- Added `/api/auth/login`, `/api/auth/logout`, `/api/auth/session`, and
  administrator-only `/api/users` management endpoints.
- Added shared FastAPI authentication and role dependencies.
- Protected `/api/monitor/*` routes with session authentication.
- Restricted platform accounts, proxies, AI, mail, login sessions, system
  diagnostics, smoke/system checks, and resource operations to administrators.
- Scoped normal-user jobs, runs, reports, and leads to the owning user in the
  default workspace.
- Added frontend login screen, session check, current-user badge, logout, and
  role-based navigation/menu visibility.
- Implemented `scripts/check_docs.py`.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 200 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 1 does not implement runtime settings, simplified normal-user task
  wizard, profile-key runtime resolver, server-side QR login primary flow, or
  server-like acceptance validation. These remain for Phase 2 and later phases.
- Local development cookie settings still use `secure=false`; production HTTPS
  cookie behavior remains part of server-like validation and deployment work.

## 2026-06-14 - Phase 0.5 Schema Foundation Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run` and the monitoring SQLite database.

Result:

- Implemented Phase 0.5 foundation schema in `api/monitoring/database.py`.
- Created `workspaces`, `users`, `user_sessions`, `system_settings`,
  `audit_logs`, and `resource_locks`.
- Added `workspace_id`, `created_by`, and `updated_by` to priority business
  tables.
- Added `profile_key` to `social_accounts` and `login_sessions`, including
  default key backfill and inheritance for new account login sessions.
- Added run timeout fields to `crawl_runs`: `timeout_seconds`, `deadline_at`,
  and `timeout_reason`.
- Added account/profile lock fields to `social_accounts`:
  `locked_by_run_id`, `locked_at`, and `lock_expires_at`.
- Verified default workspace backfill with `workspace_id = 1`.
- Verified existing MVP tasks, social accounts, login sessions, runs, and
  reports still load after migration.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 198 passed, 3 warnings.

Limitations:

- Phase 0.5 adds schema and minimal profile-key persistence only. Full
  authentication, RBAC, runtime settings UI, runtime lock acquisition,
  timeout enforcement, and server-like login validation remain for later
  phases.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Documentation Review Follow-Up For Timeout And Range

Environment: local repository documentation update.

Result:

- Added a concrete run-level timeout example showing remaining-time allocation
  across platform crawler attempts.
- Clarified that current MVP timeout is subprocess-level and Phase 2 should
  migrate it to a run-level wall-clock deadline.
- Added startup and scheduler recovery implementation guidance for stale
  running runs and persisted locks.
- Added crawl range platform capability matrix for Douyin, Xiaohongshu, and
  Kuaishou.
- Added Phase 0.5 monitoring API response-shape regression checks.
- Added YAML-to-database runtime settings mapping.

Limitations:

- No code or runtime validation was performed.
- The review item claiming CR-012A/B/C were missing from `TRACEABILITY.md` was
  not applied because the current matrix already contains separate accepted
  CR-012A, CR-012B, and CR-012C rows.

## 2026-06-14 - CR-012 Timeout Lock And Crawl Range Documentation

Environment: local repository documentation update.

Result:

- Accepted CR-012A profile key format:
  `{workspace_id}/{platform}/acc_{account_id}`.
- Accepted CR-012B as run-level wall-clock timeout plus lock cleanup buffer.
- Accepted CR-012C as inline account/profile locks plus `resource_locks` for
  proxy concurrency.
- Accepted CR-017 Runtime Strategy administrator-only grouped table layout.
- Added CR-018 for crawl range capability boundaries.
- Updated data model, schema migration, system settings, product requirements,
  UI guidelines, traceability, tasks, and tests.

Limitations:

- No code or runtime validation was performed.
- Phase 0.5 schema foundation is still not implemented.

## 2026-06-14 - Review Follow-Up Minor Documentation Gaps

Environment: local repository documentation update.

Result:

- Clarified documentation check script timing as Phase 1 close-out.
- Added bootstrap administrator login checks to the test plan.
- Added recommended container base image guidance.
- Added `.gitignore` validation for `monitor.yaml`.
- Added Quick Index maintenance and superseded-decision rules to agent
  workflow.
- Added CR-017 for Runtime Strategy page layout confirmation.

Limitations:

- No code or runtime validation was performed.
- CR-017 remains pending user confirmation before Phase 2 UI implementation.

## 2026-06-14 - Attached Review Follow-Up

Environment: local repository documentation update.

Result:

- Strengthened Phase 0.5 wording as a blocking prerequisite before Phase 1-9.
- Added explicit current-code gaps for missing auth/workspace/settings/profile
  schema and hard-coded scheduler/concurrency settings.
- Added migration regression checks for existing monitoring APIs, scheduler,
  runs, and reports.
- Added server QR login headless/container validation checks.
- Added code-document consistency checks to `DOCUMENTATION_CHECKS.md`.
- Added container build requirements and current frontend technology-stack
  guidance.
- Added CR quick index and CR-016 to preserve the review follow-up in the
  documentation loop.

Limitations:

- No code or runtime validation was performed.
- Phase 0.5 schema foundation is still not implemented.
- Phase 5/6 still need CR-012A, CR-012B, and CR-012C confirmation.

## 2026-06-14 - Review Follow-Up Documentation Hardening

Environment: local repository documentation update.

Result:

- Clarified implementation status: Phase 0.5 is not started and is required
  before Phase 1.
- Split CR-012 into CR-012A, CR-012B, and CR-012C for profile key format, lock
  timeout, and lock storage confirmation.
- Added Phase 0.5 schema foundation tests and standard permission test data.
- Added `DOCUMENTATION_CHECKS.md` as the future documentation consistency
  script specification.
- Added parallel-document merge protocol, authentication/error UI states,
  runtime settings page layout, and encryption key management guidance.

Limitations:

- No code or runtime validation was performed.
- Phase 5/6 remain blocked until CR-012A, CR-012B, and CR-012C are confirmed.

## 2026-06-14 - Phase 0.5 Documentation Alignment

Environment: local repository documentation update.

Result:

- Added Phase 0.5 schema foundation to the implementation task list.
- Updated current-state wording so Phase 1 is no longer shown as blocked by
  accepted permission decisions.
- Split accepted account/profile migration direction from still-unconfirmed
  account/profile/proxy lock details.
- Aligned runtime settings documentation with `monitor.example.yaml`, including
  `scheduler.disabled`.
- Clarified that MVP includes minimal audit logs and session-based
  authentication fields.
- Added `API_AUTHENTICATION.md` and `SERVER_DEPLOYMENT.md` for Phase 1 and
  Phase 8 implementation guidance.

Limitations:

- No application runtime validation was performed.
- Phase 5/6 still need confirmation for final `profile_key` format, lock
  timeout behavior, and lock table vs lock fields.

## 2026-06-14 - Permission Confirmation Accepted

Environment: local repository documentation update.

Result:

- Marked permission confirmation items C-001 to C-007 as accepted.
- Confirmed single-workspace V1, session auth, environment bootstrap admin,
  normal-user task deletion, normal-user report resend, disabled-user task
  behavior, and minimal MVP audit log.
- Confirmed flexible key-value system settings table.

Limitations:

- Profile key format and lock timeout details still need confirmation before
  coding the account/profile locking layer.
- No code or runtime validation was performed.

## 2026-06-14 - Profile Migration Decision Updated

Environment: local repository documentation update.

Result:

- Updated account environment and schema migration documents to reflect the
  confirmed direct-new-profile migration direction.
- Added workspace explanation to the permission confirmation document.

Limitations:

- At the time of this entry, workspace strategy was not yet confirmed; it was
  later accepted as single-workspace V1.
- No code or runtime validation was performed.

## 2026-06-14 - Review Follow-Up P0 Additions

Environment: local repository documentation update.

Result:

- Added permission confirmation pack.
- Added compatible schema migration plan.
- Added `monitor.example.yaml`.
- Updated document routing, traceability, current state, decisions, and tasks.

Limitations:

- Confirmation items remain unresolved.
- No code or runtime validation was performed.

## 2026-06-14 - P0 Specialist Documents Added

Environment: local repository documentation update.

Result:

- Added roles and permissions specification.
- Added account environment specification.
- Added runtime settings specification.
- Added target data model planning document.
- Updated document routing and traceability.

Limitations:

- Several high-impact assumptions remain marked as needing user confirmation.
- No application runtime validation was performed.

## 2026-06-14 - Confirmation Gate Added

Environment: local repository documentation update.

Result:

- Added confirmation-gate rule to agent workflow.
- Updated agent entry instructions.
- Added CR-004 and traceability entry.

Limitations:

- No application runtime validation was performed.

## 2026-06-14 - Documentation Loop Expansion

Environment: local repository documentation update.

Result:

- Added menu-level product requirements.
- Added change request intake document.
- Added traceability matrix.
- Added detailed agent workflow document.
- Updated agent entry rules and current state.

Limitations:

- No application runtime validation was performed.
- No server-like acceptance validation has been completed yet.

## 2026-06-14 - Documentation Bootstrap

Environment: local repository inspection only.

Result:

- Added initial governance documents.
- No application runtime validation was performed in this step.
- No server-like acceptance validation has been completed yet.

Next required verification:

- confirm documents are committed to Git;
- run existing tests after the next implementation change;
- create or use a server-like environment for login/profile validation before
  production acceptance.
