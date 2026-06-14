# Current State

Last updated: 2026-06-14

## Current Phase

Phase 0 documentation is complete. Phase 0.5 - Schema Foundation is complete
and verified. Phase 1 - Users And Permissions is complete and verified. Phase
2 - System Settings Center is complete and verified. Phase 3 - Administrator
Resource Center is complete and verified. Phase 4 - Normal User Task Wizard is
complete and verified. The active SQLite schema now provides the foundation
tables and columns required before later implementation work, and the web/API
layer now has session login, administrator/normal-user roles, menu visibility,
owner-scoped business data access, administrator-managed runtime strategy
settings, administrator resource pages with consistent summary, toolbar, modal,
and test interactions, and a normal-user task wizard with administrator-only
advanced options.

## Implementation Status

- Phase 0 - Documentation: complete.
- Phase 0.5 - Schema Foundation: complete and verified.
- Phase 1 - Users And Permissions: complete and verified.
- Phase 2 - System Settings: complete and verified.
- Phase 3 - Administrator Resource Center: complete and verified.
- Phase 4 - Normal User Task Wizard: complete and verified.
- Phase 5 - Account Environment: next unblocked implementation phase.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; runtime implementation can now begin
  with Phase 5 account environment work before Phase 6 login-flow changes.

Phase 5 can begin next. Phase 6-9 implementation must still proceed in order
and must not bypass unfinished earlier phases.

## Completed

- Project direction has been clarified as a server-deployed ToB law-firm
  public-opinion monitoring system.
- The first-version boundary has been clarified as single-server,
  low-concurrency, administrator-managed resources, and normal-user task
  creation.
- The role split has been clarified:
  - system administrator maintains account pool, proxies, AI, email, templates,
    runtime strategy, and users;
  - normal user configures platforms, content, frequency, and recipient emails.
- The account-environment model has been clarified:
  task -> platform account -> profile -> proxy -> server browser.
- Server-like validation has been made mandatory for production acceptance.
- Initial governance documents have been added.
- Menu-level product requirements have been documented.
- Change request intake, traceability, and agent workflow documents have been
  added.
- A confirmation gate has been added: ambiguous high-impact requirements must
  be confirmed by the user before becoming accepted product or architecture
  decisions.
- P0 implementation specifications for roles, account environment, runtime
  settings, and data model have been added as planning documents.
- A permission confirmation pack, compatible schema migration plan, and runtime
  configuration example have been added.
- API authentication/authorization and server deployment guides have been
  added.
- Documentation consistency check specification and Phase 0.5 test coverage
  have been added.
- Permission, workspace, authentication, initial administrator, disabled-user
  behavior, audit-log timing, and runtime settings storage decisions have been
  accepted using the V1 recommended options.
- Phase 0.5 schema foundation has been implemented in
  `api/monitoring/database.py`: default workspace, user/session/settings/audit
  tables, ownership columns, profile keys, run timeout fields, account lock
  fields, and proxy `resource_locks`.
- Existing monitoring MVP task/account/login/run/report records still load
  after the schema foundation migration.
- Phase 1 user and permission foundation has been implemented:
  environment-bootstrap administrator creation, bcrypt password hashes,
  session-token cookies backed by `user_sessions`, user management APIs,
  shared FastAPI auth/role dependencies, administrator-only resource APIs,
  normal-user owner scope for jobs/runs/reports/leads, and frontend login/menu
  visibility.
- `scripts/check_docs.py` has been implemented and currently passes.
- Phase 2 runtime strategy has been implemented:
  `api/monitoring/settings.py` defines runtime defaults, YAML mapping,
  validation ranges, apply scopes, and environment locks; `system_settings`
  stores database overrides with audit logging; administrators can edit grouped
  Runtime Strategy tables; normal users cannot access runtime settings APIs;
  scheduler tick/disable, crawl concurrency, crawler retry, run-level timeout,
  QR timeout, login session TTL, lock cleanup buffer, and retention settings
  now read through the runtime settings layer.
- Newly started crawl runs copy `crawler_timeout_seconds` into
  `crawl_runs.timeout_seconds`, compute `deadline_at`, allocate remaining run
  time to platform crawler attempts, and mark deadline-exceeded runs as
  `timeout` while preserving partial platform results.
- Phase 3 administrator resource center has been refined:
  platform accounts keep the single account-detail dialog, proxy resources have
  summary cards plus search/status filters, AI access has summary cards plus
  protocol/test-status filters and a connection-test dialog, mail configuration
  uses edit/test dialogs with masked password behavior, and mail templates have
  summary cards plus search/status filters and live preview.
- Phase 4 normal-user task creation has been simplified:
  normal users see a four-step task wizard for target, collection content,
  schedule, and report recipients; crawl range copy explains the actual V1
  boundaries; account/proxy/AI/template/browser fields are hidden from normal
  users; the API also clears those advanced fields for normal-user create/edit
  requests; administrators still keep advanced task binding controls.

## In Progress

- Phase 5 - Account Environment is ready to start.

## Known Risks

- Current code still exposes or handles real profile paths in places.
- Current code still uses `profile_path` as a primary account/profile identity
  in places; Phase 5 will migrate new account environments to `profile_key`.
- Current database schema has `profile_key`, but current runtime code still
  uses `profile_path` in places; Phase 5 changes runtime behavior to use
  `profile_key` consistently.
- Phase 4 normal-user wizard is implemented, but Phase 5 still needs runtime
  account/profile/proxy environment behavior.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR login and profile persistence need container/server validation.
- Account/profile/proxy runtime use still needs Phase 5 lock and profile-key
  implementation.
- The newly added product documents are initial versions and should be refined
  during implementation.
- Profile migration strategy has been clarified: existing low-volume
  `profile_path` accounts do not need long-term compatibility and can be reset
  or re-logged in under the new `profile_key` model.
- Phase 5/6 account/profile/proxy behavior has accepted decisions, but runtime
  code still needs persisted account/profile lock acquisition, proxy lock
  usage, and startup/scheduler recovery.
- Phase 2 retention settings are configurable and stored, but automated
  retention cleanup jobs remain for later operations work.

## Next Step

Implement Phase 5 in small increments:

1. add the `profile_key` runtime path resolver;
2. stop exposing real profile paths in customer-facing UI/API paths touched by
   Phase 5;
3. ensure each platform account resolves to one server profile keyed by
   `{workspace_id}/{platform}/acc_{account_id}`;
4. add account/profile lock acquisition and release around runs;
5. add proxy concurrency control through `resource_locks`;
6. add startup and scheduler recovery for stale running runs and expired locks;
7. ensure login and crawling use the same account proxy when configured;
8. for every new requirement, add or update `CHANGE_REQUESTS.md`,
   `TASKS.md`, `TRACEABILITY.md`, and `TEST_RESULTS.md`;
9. ask for user confirmation before accepting ambiguous assumptions in
   permissions, deployment, account environment, security, or data model;
10. Accepted Phase 5/6 decisions:
   - `profile_key` format is `{workspace_id}/{platform}/acc_{account_id}`;
   - task timeout is a run-level wall-clock deadline controlled by
     administrator Runtime Strategy;
   - lock expiry is the run deadline plus cleanup buffer;
   - account/profile locks use inline `social_accounts` fields;
   - proxy concurrency uses `resource_locks`.
11. Before Phase 5/6 coding, re-verify that run timeout fields, profile keys,
    lock fields, and `resource_locks` exist in the active database.

## Latest Verification

Phase 4 local verification passed on 2026-06-14:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 207 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for `api/monitor_web/index.html` script block
- Result: monitor web script parses.

No server-like acceptance run has been completed for the new plan yet.
