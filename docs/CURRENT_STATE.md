# Current State

Last updated: 2026-06-14

## Current Phase

Phase 0 is complete for planning purposes. The next implementation foundation
is Phase 0.5 - Schema Foundation.

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
- Permission, workspace, authentication, initial administrator, disabled-user
  behavior, audit-log timing, and runtime settings storage decisions have been
  accepted using the V1 recommended options.

## In Progress

- Preparing for implementation phases that use the documentation loop as the
  source of truth.

## Known Risks

- Current code still exposes or handles real profile paths in places.
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
- Phase 5/6 still need user confirmation for final `profile_key` format, lock
  timeout behavior, and lock table vs lock fields before coding the
  account/profile locking layer.

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
9. For Phase 5/6, still confirm profile key format, lock timeout details, and
   lock storage strategy before coding the account/profile locking layer.

## Latest Verification

No server-like acceptance run has been completed for the new plan yet.
