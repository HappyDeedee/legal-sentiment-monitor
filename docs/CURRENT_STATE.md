# Current State

Last updated: 2026-06-14

## Current Phase

Phase 0 documentation is complete. Phase 0.5 - Schema Foundation must be
implemented before Phase 1-9 work can begin. Current code does not yet provide
the `users`, `workspaces`, `user_sessions`, `system_settings`, or `audit_logs`
tables required by the target V1 model.

## Implementation Status

- Phase 0 - Documentation: complete.
- Phase 0.5 - Schema Foundation: not started; required before Phase 1.
- Phase 1 - Users And Permissions: blocked by Phase 0.5 implementation, not
  by permission decisions.
- Phase 2 - System Settings: blocked by Phase 0.5 implementation until the
  `system_settings` foundation exists.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; implementation is still blocked by
  Phase 0.5 schema foundation and the preceding account/session groundwork.

All Phase 1-9 implementation work depends on Phase 0.5. Phase-specific planning
may continue, but code changes for those phases should not bypass the schema
foundation.

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

## In Progress

- Preparing for implementation phases that use the documentation loop as the
  source of truth.

## Known Risks

- Current code still exposes or handles real profile paths in places.
- Current code still uses `profile_path` as a primary account/profile identity
  in places; Phase 5 will migrate new account environments to `profile_key`.
- Current database schema does not have `profile_key` yet; Phase 0.5 adds the
  column, and Phase 5 changes runtime behavior to use it.
- Current frontend does not have role-based menu rendering, login page,
  session checks, or `/api/auth/*` flows yet.
- Scheduler tick interval and global/platform concurrency are still hard-coded
  in places; Phase 2 moves these values into runtime settings.
- Current crawler timeout is applied to individual MediaCrawler subprocess
  attempts; Phase 2 changes the target behavior to one run-level wall-clock
  deadline with remaining-time allocation.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR login and profile persistence need container/server validation.
- Runtime settings are still partly hard-coded or environment-driven.
- Existing UI may still mix administrator resource management and normal-user
  task creation.
- The newly added product documents are initial versions and should be refined
  during implementation.
- Profile migration strategy has been clarified: existing low-volume
  `profile_path` accounts do not need long-term compatibility and can be reset
  or re-logged in under the new `profile_key` model.
- Phase 5/6 account/profile/proxy behavior has accepted decisions, but code
  still needs run-level timeout tracking, persisted lock fields, proxy lock
  records, and startup/scheduler recovery.
- Phase 2 Runtime Strategy layout is accepted as administrator-only grouped
  tables, but the settings UI and database-backed settings layer are not yet
  implemented.

## Next Step

Implement Phase 0.5 first, then Phase 1 and Phase 2 in small increments:

1. add schema foundation tables and fields;
2. add user and role foundation;
3. add menu/route permission controls;
4. add runtime settings storage and administrator UI;
5. keep normal-user task creation simple.
6. for every new requirement, add or update `CHANGE_REQUESTS.md`,
   `TASKS.md`, `TRACEABILITY.md`, and `TEST_RESULTS.md`.
7. ask for user confirmation before accepting ambiguous assumptions in
   permissions, deployment, account environment, security, or data model.
8. Phase 1 can proceed after Phase 0.5 creates the schema foundation.
9. Accepted Phase 5/6 decisions:
   - `profile_key` format is `{workspace_id}/{platform}/acc_{account_id}`;
   - task timeout is a run-level wall-clock deadline controlled by
     administrator Runtime Strategy;
   - lock expiry is the run deadline plus cleanup buffer;
   - account/profile locks use inline `social_accounts` fields;
   - proxy concurrency uses `resource_locks`.
10. Before Phase 5/6 coding, complete Phase 0.5 schema foundation and verify
    that run timeout fields, profile keys, lock fields, and `resource_locks`
    exist.

## Latest Verification

No server-like acceptance run has been completed for the new plan yet.
