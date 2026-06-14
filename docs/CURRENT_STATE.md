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
- Phase 2 - System Settings: can begin after the schema/settings foundation is
  available.
- Phase 5/6 - Account Environment and Server Login: blocked by CR-012A,
  CR-012B, and CR-012C before coding profile/lock behavior.

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
- Phase 5/6 still need user confirmation for CR-012A final `profile_key`
  format, CR-012B lock timeout behavior, and CR-012C lock storage strategy
  before coding the account/profile/proxy locking layer.

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
9. Before starting Phase 5/6 implementation, confirm:
   - CR-012A `profile_key` format, recommended:
     `{workspace_id}/{platform}/acc_{account_id}`;
   - CR-012B lock timeout strategy, recommended:
     task timeout plus cleanup buffer;
   - CR-012C lock storage strategy, recommended:
     inline fields for account/profile locks and `resource_locks` for proxy
     concurrency.
10. Until CR-012A/B/C are confirmed, prioritize Phase 0.5, Phase 1, Phase 2,
    Phase 3, Phase 4, Phase 7, Phase 8, and Phase 9 work that does not depend
    on account/profile/proxy lock details.

## Latest Verification

No server-like acceptance run has been completed for the new plan yet.
