# Current State

Last updated: 2026-06-14

## Current Phase

Phase 0 documentation is complete. Phase 0.5 - Schema Foundation is complete
and verified. Phase 1 - Users And Permissions is complete and verified. Phase
2 - System Settings Center is complete and verified. Phase 3 - Administrator
Resource Center is complete and verified. Phase 4 - Normal User Task Wizard is
complete and verified. Phase 5 - Account Environment is complete and verified.
The active SQLite schema now provides the foundation tables and columns
required before later implementation work, and the web/API layer now has
session login, administrator/normal-user roles, menu visibility,
owner-scoped business data access, administrator-managed runtime strategy
settings, administrator resource pages with consistent summary, toolbar, modal,
and test interactions, a normal-user task wizard with administrator-only
advanced options, and profile-key based account environments with persisted
account/profile/proxy locks and stale-run recovery.

## Implementation Status

- Phase 0 - Documentation: complete.
- Phase 0.5 - Schema Foundation: complete and verified.
- Phase 1 - Users And Permissions: complete and verified.
- Phase 2 - System Settings: complete and verified.
- Phase 3 - Administrator Resource Center: complete and verified.
- Phase 4 - Normal User Task Wizard: complete and verified.
- Phase 5 - Account Environment: complete and verified.
- Phase 6 - Server Login Flow: next unblocked implementation phase.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; Phase 5 account environment runtime is
  complete, and Phase 6 login-flow changes can now begin.

Phase 6 can begin next. Phase 7-9 implementation must still proceed in order
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
- Phase 5 account environment runtime has been implemented:
  account profile runtime paths are derived from stable `profile_key` values,
  new account environments ignore arbitrary customer-provided profile paths,
  account names are display labels only, account/profile summaries no longer
  expose real server paths, account/profile locks use inline
  `social_accounts` fields, proxy concurrency uses `resource_locks`, run
  cleanup releases locks, and startup/scheduler recovery reconciles timed-out
  running runs before releasing persisted locks.

## In Progress

- Phase 6 - Server Login Flow is ready to start.

## Known Risks

- Phase 5 still stores `profile_path` as a transition-only internal runtime
  field for existing login/crawler code paths, but new identity and path
  resolution are `profile_key` based and customer-facing responses mask real
  paths.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR login and profile persistence need container/server validation.
- The newly added product documents are initial versions and should be refined
  during implementation.
- Profile migration strategy has been clarified: existing low-volume
  `profile_path` accounts do not need long-term compatibility and can be reset
  or re-logged in under the new `profile_key` model.
- Phase 6 still needs the primary server-side QR login state machine and
  browser-session UX; Phase 5 only aligned account profile path resolution,
  proxy reuse, locking, and recovery primitives.
- Phase 2 retention settings are configurable and stored, but automated
  retention cleanup jobs remain for later operations work.

## Next Step

Implement Phase 6 in small increments:

1. make server-side QR login the primary administrator flow;
2. return structured login states to the frontend;
3. support waiting QR, waiting scan, waiting confirmation, success,
   verification required, QR failure, timeout, and platform error states;
4. persist the profile after successful login using the Phase 5
   `profile_key` runtime path;
5. verify profile reuse after browser close;
6. hide local-window login from production mode;
7. for every new requirement, add or update `CHANGE_REQUESTS.md`,
   `TASKS.md`, `TRACEABILITY.md`, and `TEST_RESULTS.md`;
8. ask for user confirmation before accepting ambiguous assumptions in
   permissions, deployment, account environment, security, or data model.

## Latest Verification

Phase 5 local verification passed on 2026-06-14:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 211 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for `api/monitor_web/index.html` script block
- Result: monitor web script parses.

No server-like acceptance run has been completed for the new plan yet.
