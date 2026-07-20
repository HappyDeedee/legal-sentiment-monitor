# Test Plan

## General Rule

Production acceptance must run in a server-like environment. Local Chrome on
the operator's computer is not a valid acceptance path.

## Goal Readiness And Execution Governance Tests

CR-095 governs how open todos become executable goals. These tests apply before
starting or approving any non-trivial implementation or documentation
governance goal.

- A read-only todo baseline review compares open todo/CR/current-state/
  traceability/test-plan items against current `main`, local worktree state,
  accepted decisions, and relevant code/schema/UI/runtime evidence.
- Active or next items are classified as current, already completed, stale,
  duplicate, future-only, deferred, `Needs Confirmation`, operator-gated, or
  historical/archive-only before implementation starts.
- `CHANGE_REQUESTS.md` and `TRACEABILITY.md` use unique CR identifiers for
  separate current entries; completed historical Phase 21 CRs are preserved and
  conflicting governance/future backlog entries are renumbered instead.
- A goal packet exists or is explicitly confirmed from
  `docs/GOAL_EXECUTION_GUIDELINES.md`.
- The packet names one owner CR or phase and one primary risk area.
- The packet states current baseline, in scope, out of scope, hard boundaries,
  start gate, dependencies, expected touch surface, execution steps, test loop,
  acceptance criteria, rollback or recovery, documentation updates, and stop
  conditions.
- The packet follows the current execution order unless a later accepted
  decision changes it: Phase 21, Phase 5.1A-D, and CR-114 are merged and
  verified; CR-047 Linux/server-like acceptance remains operator-gated;
  accepted CR-112 Packet B/C/D run serially; then CR-070 / Phase 5.2 starts
  only after CR-112 Packet D verification.
- Phase 21 packets remain frontend-visual only and preserve Task Center, Run
  Detail, drawer, modal, row-menu, select/date, close, scroll, refresh,
  routing, owner-scope, and permission behavior unless a separate accepted CR
  changes those surfaces.
- Phase 5.1P packets are read-only compatibility mapping only. They must not
  create or change code, schema, provider implementation, runtime data,
  profiles, cookies, proxies, crawler behavior, deployment configuration, or
  database state.
- Phase 5.1 implementation packets run in order and do not start until
  the verified Phase 5.1P map confirms the BrowserEnvironmentProvider and
  requested/effective snapshot boundary.
- CR-070 / Phase 5.2 packets do not start before CR-112 Packet D is verified.
  They consume only committed account/Profile state and exclude CR-112
  operation and connector secrets.
- CR-092, CR-093, and CR-094 packets remain future independent backlog work and
  are not treated as hidden prerequisites for Phase 21, Phase 5.1P, Phase 5.1,
  or CR-070.
- `Needs Confirmation` CRs can receive read-only planning or review only; tests
  fail if they are described as ready for implementation.
- External side-effect packets identify email, crawler, platform login, proxy,
  account profile, package export/import, file deletion, production route, AI
  provider, webhook, or other durable exits, and define opt-in gates or
  tripwires before implementation.
- The required iteration loop is documented and followed: pre-check, implement
  only the packet, targeted checks, fix and rerun, broader checks proportional
  to blast radius, documentation sync, documentation consistency, and read-only
  cross-review for roadmap, acceptance, provider, deployment, permission,
  account, or external-side-effect goals.
- Documentation-only governance goals pass
  `uv run python scripts/check_docs.py`, `git diff --check`, and a read-only
  full open-todo cross-review with no blocking findings before completion.

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
- Normal user sees only overview, monitoring, and Task Center.
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
- Platform account identity display can show a recognized avatar through a
  same-origin cached URL without exposing signed platform image URLs.
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
- Scan-time login confirmation does not cancel the same-account cookie/session
  fallback when the platform login-state method itself times out.
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
- Before CR-047 locked browser-environment rules are active, task-bound proxy
  overrides account proxy according to the Phase 5 baseline.
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

### Account Identity Fidelity Tests

CR-047 / Phase 5.1 must verify that account profile traces are paired with a
stable, self-consistent account identity instead of relying on changing process
defaults.

Phase 5.1 cannot be accepted by database fields, UI summaries, requested launch
options, or isolated generator tests alone. Its first gate, the Phase 5.1P
runtime compatibility preflight, is verified in
`docs/phase-5.1p-browser-entrypoint-map.md`; implementation and final
acceptance must now prove the mapped QR, Cookie, login-state, manual,
scheduler, runner, and MediaCrawler CDP paths share one provider output and
requested/effective runtime snapshot contract.

- Verified Phase 5.1P review evidence maps every current login and crawl
  entrypoint before Phase 5.1A schema/code implementation starts.
- Phase 5.1A fresh-schema tests verify all 24 accepted account identity fields,
  their exact safe defaults, and three non-unique workspace-scoped indexes
  with the documented column order.
- Phase 5.1A existing-schema tests run the additive helper twice and verify it
  preserves account status, `profile_key`, legacy Profile path, proxy binding,
  encrypted Cookie value, and timestamps without guessed identity backfill.
- Phase 5.1A read tests verify false SQLite flags become Python booleans,
  nullable dimension/scale fields remain `None`, and masked detail/list reads
  do not expose raw Profile paths.
- Phase 5.1B exact-catalog tests cover all six accepted templates, documented
  catalog order, exact UA/screen/viewport/scale/device/region fields, automatic
  and family-filtered selection, stable/differentiated HMAC output, and exact
  deployment-key domain separation.
- Phase 5.1B persistence/validator tests verify new-account INSERT-only
  generation, transaction rollback, no legacy UPDATE backfill, request-field
  ownership, missing/contradictory field rejection, declared region bundles,
  missing bound proxy rejection, relogin/locked-proxy reasons, safe API/UI
  surfaces, and blocked-by-default account Playwright entrypoints.
- Phase 5.1C lifecycle tests verify SQLite-authoritative prepare/completion,
  all eight persisted states, QR-only lock after account-level verification,
  Cookie/Profile lock reasons, unlocked failure recovery to `validated`,
  locked maintenance recovery to `active`, and concurrent/relogin/reset
  conflict behavior.
- Phase 5.1C route tests verify QR and visible-browser prepare before launch,
  terminal QR and verification-code recovery, explicit session deletion,
  standalone and continued administrator checks, locked-safe configuration
  changes, draft confirmation, reset HTTP 409 mapping, and CR-113 exact safe
  field forwarding.
- Phase 5.1C reset/audit tests verify Profile key, legacy Profile metadata,
  encrypted Cookie, platform identity, and account ID survive reset; generated
  fields and lock metadata are rebuilt; audit details use an exact safe
  allowlist and preserve explicit `null` when a locked proxy is cleared.
- Phase 5.1C UI tests verify safe environment summary/state labels, pre-login
  editing, explicit locked change/reset flow, and login/check disabling for
  `requires_relogin` and `resetting`, with no seed, runtime snapshot, Cookie,
  raw Profile path, proxy credential, CDP, or noVNC exposure.
- Phase 5.1D provider tests verify exact executable precedence, `profile_key`
  path derivation, all-eight-state managed/legacy boundaries, locked proxy
  override rejection, explicit direct policy, bound-proxy availability, and
  no managed local-browser auto-detection.
- Phase 5.1D snapshot tests verify recursive secret/path rejection, exact safe
  shape and size, account/resolution/attempt binding, field-scoped mismatch
  values, safe persistence, and compact administrator API/UI output.
- Phase 5.1D direct browser tests verify QR, Profile, Cookie, and visible login
  consume the same plan; proxy proof finishes before a context is returned;
  mismatches, proof errors, and browser disconnects persist safe failure and
  stop before login/crawl continuation.
- Phase 5.1D Runner tests verify manual and scheduler triggers resolve the same
  account environment after locks, each retry gets a unique attempt, the
  internal plan is at most 8192 UTF-8 bytes and absent from argv/log summaries,
  process proxy/default Profile variables are removed, result files are
  atomic/fresh/bound, and output ingest waits for successful persistence.
- Phase 5.1D CDP/platform tests verify the exact awaited pre-navigation CDP
  command sequence, exact executable/Profile/proxy/headless launch, all seven
  platform cores using the managed proxy/context/prepare/verify adapters, no
  dynamic proxy pool, and no managed CDP-to-standard fallback.
- Phase 5.1D deployment/static tests verify only the executable and proxy-probe
  operator settings appear in environment examples; internal plan/result
  handoff variables remain absent. Inline monitor JavaScript must parse after
  the compact runtime summary is added.
- CR-114 deterministically simulates repeated numeric object IDs and verifies
  two BrowserContexts retain separate plans while both CDP Pages execute their
  own pre-navigation preparation. The test must fail against the merged
  Phase 5.1D ID-keyed collections and pass with object-scoped bindings.
- CR-116 mirrors Playwright persistent-context behavior where
  `BrowserContext.browser` is `None`. The regression must fail on the merged
  Phase 5.1D version lookup, obtain the effective version from the exact page's
  CDP `Browser.getVersion` product after the fix, detach the temporary CDP
  session, and preserve fail-closed malformed/missing proof plus field-scoped
  browser-version mismatch evidence.
- CR-116 also reads Playwright's installed `browsers.json` without launching a
  browser and proves every current catalog UA version matches the default
  bundled Chromium version. Catalog `accept_language` must equal the locale
  that Playwright exposes in both request and navigator probes; old v1 metadata
  must return `account_identity_requires_relogin` without silent mutation.
- Phase 5.1 acceptance-checker tests verify the incomplete template and example,
  exact QR/Cookie/Profile/manual/scheduler/`cli_manual` action matrix, unique
  references, chronology, restart lock/digest stability, managed provider
  modes, positive crawl bounds, redaction surfaces, sensitive-value rejection,
  and the checker-only proof boundary without any real external action.
- Acceptance-checker CLI tests require an explicit full lowercase 40-character
  deployed commit for `--check`, reject missing, empty, abbreviated, uppercase,
  non-hex, and mismatched values, and pass only when it equals
  `baseline.commit`. Pure synthetic validation may omit that runtime argument.
- Checker boundary tests reject unreadable/invalid/non-object evidence with
  structured path-safe errors; reject non-acceptance browser sources, action
  source drift, duplicate/whitespace-equivalent account references, reordered
  login/restart/crawl actions, out-of-window lock timestamps, URLs, CDP
  endpoints, and Windows/UNC/Unicode Unix paths; and preserve ordinary
  slash-delimited attestation text.
- QR login, Cookie validation, and login-state checks resolve the same
  `profile_key`, account identity, proxy policy, user agent, timezone, locale,
  accept-language, viewport/screen, device flags, and provider mode.
- Manual run and scheduler run paths resolve the same provider output as the
  login paths and do not rebuild identity values from process defaults.
- MediaCrawler CDP launch/reconnect receives the provider-resolved account
  environment when Phase 5.1 identity exists, while pre-Phase-5.1 accounts can
  keep existing MediaCrawler defaults until re-login or identity generation.
- Container/server-like execution is the Phase 5.1 development and acceptance
  baseline. Local Chrome/Edge auto-detection, local-window login, and CDP
  connect-existing are development fallbacks only and cannot prove locked or
  active account identity.
- Provider preflight records which Playwright/CDP fields can be honored and
  probed in V1, which surfaces are unsupported or not-managed, and which
  mismatches fail closed.
- Proxy acceptance requires proof that the provider used the resolved account
  proxy policy, or a fail-closed result. A hidden task-level proxy override,
  default-network fallback, or unproven proxy effect must not mark an account
  identity as locked or active.
- New platform accounts receive a deterministic `profile_key` and persisted
  account identity fields before first QR login or accepted Cookie
  validation.
- The Account Identity Generator is deterministic for the same workspace,
  platform, account, proxy/region policy, automatic template selection or
  pre-login administrator template-family choice, and seed salt.
- Generator tests prove that automatic template selection uses the documented
  template-selection seed and catalog order, not runtime randomness or
  Playwright/process defaults.
- Normal-user API/UI tests prove normal users cannot choose identity templates
  or browser-environment fields.
- Administrator UI/API tests prove ordinary account creation can leave
  template selection automatic, while the advanced pre-login path can select
  only a template family and cannot edit individual UA, viewport, screen,
  timezone, locale, accept-language, device-scale, mobile, or touch fields.
- Generator tests cover exact template expansion for `CN_WIN_CHROME_1920`,
  `CN_WIN_CHROME_1536`, `CN_MAC_CHROME_1440`, `CN_ANDROID_CHROME`,
  `HK_DESKTOP_CHROME`, and `SG_DESKTOP_CHROME`, including exact UA,
  screen/viewport, scale factor, mobile/touch, timezone, locale, and
  accept-language values.
- Generator tests prove that the HMAC-SHA256 seed derivation in
  `ACCOUNT_ENVIRONMENT.md` is stable: same canonical input plus salt produces
  identical `fingerprint_seed`, while different account IDs normally differ.
- Same-platform accounts normally receive different fingerprint seeds and
  identity values unless an administrator explicitly clones a safe template
  before first login.
- Generated identity values are self-consistent: browser platform, UA,
  timezone, locale, accept-language, screen, viewport, device scale factor,
  mobile flag, touch flag, and proxy region describe the same plausible device
  and region.
- China mainland proxy identities default to `environment_region =
  CN_MAINLAND`, `timezone = Asia/Shanghai`, `locale = zh-CN`, and
  `accept_language = zh-CN` for catalog v2, with coherent desktop or mobile device
  templates.
- The Account Identity Validator rejects missing or contradictory identity
  fields and does not let locked accounts fall back to Playwright or process
  defaults.
- Validation tests treat NULL and empty strings as missing required fields for
  locked identities.
- Validation tests reject missing or invalid template IDs, missing proxy region
  snapshots, missing account-bound proxy records, contradictory desktop/mobile
  UA and touch flags, and mismatched region/timezone/locale bundles.
- Successful QR login or accepted Cookie validation locks the account browser
  environment.
- State-machine tests cover `draft -> generated -> validated ->
  login_in_progress -> locked -> active`, `locked -> requires_relogin`, and
  `requires_relogin -> resetting -> draft`.
- State-machine tests cover template-family changes: allowed in `draft`,
  returning `generated` and `validated` accounts to `draft`, rejected during
  `login_in_progress`, and requiring `requires_relogin` plus reset/re-login
  after `locked` or `active`.
- Repeated login-state checks and crawl runs for the same account use the same
  stored `profile_key`, `browser_platform`, `fingerprint_seed`, `user_agent`,
  `timezone`, `locale`, `accept_language`, screen/viewport/device fields, and
  effective proxy policy.
- Provider-boundary tests verify requested versus effective Playwright/CDP
  values for `navigator.userAgent`, `navigator.language`,
  `navigator.languages`, `Intl.DateTimeFormat().resolvedOptions().timeZone`,
  `window.screen`, `window.innerWidth/innerHeight`,
  `window.devicePixelRatio`, and `navigator.maxTouchPoints` where available.
- Runtime snapshot tests verify that `identity_runtime_snapshot_json` records
  requested/effective values, provider metadata, unsupported fields, and
  `fallback_used = false`, without cookies, proxy credentials, raw profile
  paths, CDP endpoints, or noVNC tokens.
- Attempts to silently edit a locked browser environment are rejected; the
  explicit reset/re-login path records an audit log and makes consequences
  visible to the administrator.
- Task-level proxy override handling follows the confirmed policy exactly:
  locked account environments reject the override; the test fails if a hidden
  process-default fallback, explicit exception path, or silent proxy swap is
  used.
- Empty or partially configured persisted account identity values fail
  closed before login/crawl launch instead of being auto-filled from process
  defaults.
- Test tripwires fail if automated tests or local diagnostics touch real
  profile roots, real cookies, real proxy credentials, or real platform login
  sessions without `TEST_ALLOW_REAL_ACCOUNT_IDENTITY=true`,
  `TEST_ALLOW_REAL_PROXY=true`, or `TEST_ALLOW_REAL_PLATFORM_LOGIN=true`.
- Service restart, scheduler run, and manual run paths do not change the stored
  account identity.
- Changing identity template, proxy region, or locked identity inputs marks the
  account as needing explicit reset/re-login instead of silently changing
  future crawl launches.
- Changing the template family after the account identity is locked is rejected
  or moves through the explicit reset/re-login flow with audit evidence; it
  must not silently regenerate future launch fields.
- Platform Accounts UI/API show only customer-safe account identity summaries
  and never expose raw profile paths, cookies, proxy credentials, CDP endpoints,
  noVNC sessions, or fingerprint-debug output.
- V1 tests must verify that Canvas, WebGL, font inventory, plugins, extensions,
  and long browsing history are not claimed as fully managed by the
  Playwright/CDP provider. They may be recorded as unsupported,
  not-managed, or future/provider-dependent.
- If a CloakBrowser-style provider or other high-fidelity browser-persona
  provider is evaluated later, tests or review evidence must cover
  license/deployment fit, authentication, noVNC access control,
  sensitive-data redaction, effective-value probes, runtime snapshots, and
  compatibility with existing account/profile/proxy locks before the provider
  can be enabled.

### Future Frontend Migration Tests

CR-092 tests are planning gates for a future `/monitor-next` lane. They are
not Phase 21 tests and must not be used to change the current `/monitor`
console.

- `/monitor-next` must coexist with `/monitor` until a later replacement gate
  is accepted.
- The new frontend must default to `/api/auth/...` and `/api/monitor/...` and
  must not call `/api/crawler/...`, `/api/data/...`, old websocket endpoints,
  or raw MediaCrawler control surfaces.
- Technology selection tests or review evidence must compare TypeScript/Vite
  candidates and selected component libraries against Chinese ToB console
  needs, table/form/drawer/modal maturity, accessibility, testing, deployment
  complexity, and dependency weight.
- Route tests must prove menu visibility and direct-route authorization use
  the same permission source.
- Migration-equivalence tests must cover login, Operations Home, Monitoring,
  Platform Accounts, Proxy Resources, AI Access, AI Evaluation Rules, Mail
  Configuration, Mail Templates, Runtime Strategy, System Diagnostics, Task
  Center default grouping, the `运行记录` subview, Run Detail six sections,
  report downloads, and email delivery.
- Responsive tests must cover `1440x900`, `1024x768`, and `390x844`.
- Replacement cannot be accepted until current buttons, filters, drawers,
  modals, enhanced selects, date pickers, scroll ownership, permission scope,
  downloads, and delivery actions have equivalent behavior or an explicit
  accepted change request.
- Rollback tests must prove the old `/monitor` or a deploy rollback remains
  available during the replacement window.

### Public Exposure Boundary Tests

CR-093 tests are planning gates for future MediaCrawler internalization and
production exposure hardening.

- A route audit must list every FastAPI router and static mount before any
  route is disabled.
- Production public allowlist tests must cover `/monitor`, `/api/auth/...`,
  `/api/monitor/...`, monitor-specific static assets, and necessary
  authenticated downloads or same-origin cached resources.
- Production deny/not-mounted tests must cover old MediaCrawler WebUI,
  `/api/crawler/...`, `/api/data/...`, old websocket log/status routes, old
  assets/logos/static paths, raw file browsing/download/preview, and direct
  crawler start/stop/control routes. The expected result must be fixed as 404,
  403, or unmounted after the implementation strategy is confirmed.
- Regression tests must prove login, task creation, task run, platform login,
  account check, output parsing, report generation, Run Detail, Task Center,
  report download, and email delivery still work through monitor APIs.
- Permission tests must prove normal users cannot access administrator
  resources, diagnostics, old crawler controls, or raw data surfaces.
- User-visible wording checks must fail if formal product surfaces expose
  MediaCrawler, Command Center, command-line, local path, environment variable,
  debug, self-test, mock, or prototype wording outside trusted administrator
  diagnostics.
- Internal engine tests must prove MediaCrawler can still be invoked by the
  monitor backend as an internal dependency after public exposure is narrowed.

### Crawler Provider Architecture Tests

CR-094 tests are planning gates for future provider architecture. They are not
Phase 5.1P tests; the verified Phase 5.1P result remains the current
MediaCrawler/CDP compatibility boundary for CR-047 implementation.

- Provider contract tests must cover provider id/name, supported platforms,
  login types, account checks, comment support, time filtering, proxy support,
  account binding, container/server-like support, output version, error
  version, and capability limits.
- Provider input tests must prove existing monitoring task fields map into the
  provider without creating a parallel task system.
- Output normalization tests must prove provider results become the existing
  content, AI evaluation, report, Task Center, and Run Detail model.
- Error normalization tests must cover unavailable, launch failed, login
  expired, verification required, proxy failed, timeout, cancelled,
  interrupted, partial success, no result, output parse failed, unsupported
  capability, rate limited, platform changed, and unknown error states.
- Profile binding tests must prove `profile_key` remains the upper-layer
  account identity and provider-specific profile material is hidden from
  normal users.
- Lock tests must prove a provider cannot bypass account/profile/proxy locks.
- Server-like tests must prove production providers can run without relying on
  an operator's local desktop browser.
- Redaction tests must fail if provider outputs, logs, APIs, UI, reports, or
  Run Detail expose raw cookies, proxy credentials, profile paths, CDP
  endpoints, command lines, provider secrets, or private debug fields.
- Architecture review must confirm no provider introduces parallel task,
  account, profile, report, permission, or frontend entry systems.

### Account Environment Export And Import Tests

CR-070 must verify that account migration packages are controlled sensitive
artifacts, not raw profile-folder copies.

- Metadata-only export contains manifest, account identity fields, and
  platform-account metadata, but no cookies, localStorage, IndexedDB, browser
  profile traces, proxy credentials, profile paths, or login tokens.
- Metadata-only export is treated as sensitive when it contains
  `fingerprint_seed`, detailed identity runtime snapshots, recognized platform
  account IDs, or profile-derived metadata. Tests should expect the default V1
  `.maepkg` encrypted envelope unless a later redacted diagnostic export is
  explicitly confirmed.
- Slim login-state migration export is administrator-only and produces a
  passphrase-encrypted package containing the account identity, encrypted login
  material, necessary profile state, proxy endpoint hint without credentials,
  and platform-account metadata for one selected account environment.
- Slim package tests verify whole-profile cache and temporary browser artifacts
  are excluded by default, including cache, GPU cache, code cache, media cache,
  crash dumps, downloads, screenshots, and temporary files.
- Account package tests prove package scope is limited to one selected
  platform account environment and excludes monitoring tasks, crawl runs,
  reports, AI traces, email delivery logs, users, runtime settings, full
  database backup content, and customer business history.
- Export is rejected or delayed when the account is locked by an active run,
  login session, or reset workflow.
- Export is rejected when another package operation owns the same account.
- Export state-machine tests cover preflight, locked, reading_metadata,
  snapshotting_profile, building_payload, encrypting, ready_for_download,
  failed, cancelled, expired, and deleted states.
- Export finalization tests prove locks are released and staged files are
  deleted after failure, cancellation, timeout, process interruption recovery,
  expiry, or deletion.
- Export detects account state changes after preflight and fails with a
  customer-safe `account_package_state_changed` reason instead of producing an
  inconsistent package.
- Package manifest tests verify package version, package mode, source
  platform/account, source `profile_key`, identity environment version,
  provider compatibility fields, redacted checksum evidence, and platform
  account metadata summary.
- Exact schema tests verify the decrypted logical package structure:
  `manifest.json`, `account/account.json`,
  `account/identity_runtime_snapshot_redacted.json`, optional
  `profile/slim_profile.zip`, and `checksums/sha256.json`.
- Encryption tests verify package outer header, encryption mode, KDF metadata,
  Argon2id parameters when passphrase mode is used, AES-256-GCM authentication,
  random salt/nonce behavior, wrong-passphrase failure, and the absence of
  stored package passphrases.
- Package integrity tests reject corrupted manifests, mismatched checksums,
  unsupported package versions, missing required sections, and unknown package
  modes.
- Package retention tests verify package bytes are runtime artifacts only,
  temporary files expire or are deleted after download, and persisted metadata
  rows use `expires_at` without storing plaintext content.
- Secret-leakage tests inspect package metadata, audit logs, API responses, and
  diagnostics and fail on plaintext cookies, platform tokens, proxy
  credentials, proxy endpoint hints outside the encrypted payload, profile
  paths, package passphrases, CDP endpoints, noVNC tokens, command lines, or
  deployment encryption keys.
- Import preflight rejects traversal paths, absolute paths, corrupt archives,
  source profile paths outside the package root, and profile writes outside the
  configured target profile root.
- Profile snapshot safety tests also reject drive-letter paths, UNC paths,
  empty path components, Windows alternate data streams, reserved device names,
  symlinks, junctions, hardlinks, duplicate paths with conflicting checksums,
  unsupported compression, unknown snapshot versions, over-quota package size,
  over-quota file count, and insufficient disk space.
- Import creates a target-side account/profile by default and derives a target
  `profile_key` from target workspace/platform/account ID rather than copying
  the source raw path.
- Import conflict tests prove V1 does not replace, merge, or overwrite an
  existing target account/profile. Duplicate detection may warn but must stop
  or create a new account according to the confirmed V1 policy.
- Import state-machine tests cover preflight, preflight_failed, decrypting,
  extracting_profile, writing_database, verifying_login, active,
  requires_relogin, failed, and rolled_back states.
- Import rollback/idempotency tests prove repeated cleanup cannot reopen an
  active, requires_relogin, failed, or rolled_back terminal result and cannot
  leave package/profile locks stuck.
- Metadata-only import results in an account that requires login before crawl
  use.
- Slim login-state package import runs login-state verification before
  activation.
- If login-state verification succeeds, the imported account can become active
  under target deployment locks and identity validation.
- If login-state verification fails, the imported account is marked
  `requires_relogin` or equivalent and scheduler/manual runs cannot silently
  use it.
- Import requires target-side proxy mapping when the package references a
  proxy policy. Missing or mismatched mapping fails closed or marks the account
  as needing re-login; it must not fall back silently to no proxy.
- Proxy mapping tests cover missing target proxy, target proxy in another
  workspace, inactive target proxy, region mismatch, and silent fallback to
  direct/default network.
- Proxy endpoint hint tests verify source host/IP plus port can be read only
  from the decrypted package preflight, cannot be used as a credential, and is
  absent from audit logs, manifest summaries, ordinary API responses, and
  diagnostics.
- Import preserves CR-047 identity fields only when provider and identity
  environment compatibility pass; otherwise it requires reset/re-login.
- Normal users cannot call export or import endpoints or see package actions.
- Audit tests verify export/import events include actor, account, package mode,
  version, redacted checksum, compatibility result, operation status, trigger
  source, and login verification result without raw secrets.
- Audit example tests prove safe audit details match the redacted shape in
  `ACCOUNT_ENVIRONMENT.md` and reject raw cookies, raw profile keys or paths,
  proxy credentials, proxy endpoint hints, package passphrases, CDP endpoints,
  noVNC tokens, command lines, and deployment encryption keys.
- Test tripwires fail if automated tests access real account packages, real
  profile roots, real cookies, real proxy credentials, or live platform login
  sessions without explicit opt-in.
- CR-070 tripwire tests require
  `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_EXPORT=true` before any test exports a real
  account package and `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_IMPORT=true` before any
  test imports into a non-disposable workspace.

### Platform Account Avatar Safety Tests

- A signed platform avatar URL stored after account identity detection is not
  exposed in the social-account API response.
- The social-account API returns a same-origin avatar endpoint for
  administrators when a platform avatar source exists.
- The avatar endpoint lazily fetches, validates, caches, and serves image bytes
  from runtime storage.
- Normal users cannot access platform-account avatars.
- Traversal attempts against the cached-avatar endpoint are rejected.
- If avatar fetching fails, the frontend can keep the placeholder and the
  account row remains usable.

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

## Phase 7.2 AI Evaluation Accuracy And Lead Status Tests

CR-045 is a follow-up regression-fix test set for AI evaluation safety and
lead-status clarity. It does not reopen the historical Phase 7 or Phase 7.1
verification records.

### Phase 7.2A Unevaluated Lead Status Tests

- Leads with no matching `ai_evaluations` row are returned as unevaluated or
  limited-context, not as no-risk.
- Report Center status rendering distinguishes unrelated, evaluated no-risk,
  suspected negative, high-risk, pending manual review, and unevaluated rows.
- Risk filters do not include unevaluated rows in the no-risk bucket.
- Normal-user and administrator scopes remain unchanged for unevaluated rows.

### Phase 7.2B Timeout And Partial-Finalization Fallback Tests

- A timeout run with known unresolved AI candidate IDs creates
  `pending_review` fallback rows before report generation when safe.
- Repeated timeout/partial finalization remains idempotent and does not
  duplicate `ai_evaluations` rows.
- If safe mutation is not possible, the run/report API exposes an explicit
  limited-context or unevaluated state instead of implying no risk.
- Existing AI provider failure and invalid-output fallback tests still pass.

### Phase 7.2C AI Relevance And Prompt Hardening Tests

- The default prompt states that `source_keyword` is recall provenance only and
  should not by itself prove target-law-firm relatedness.
- Valid AI output is preserved after format validation. Application
  postprocessing must not use hardcoded `source_keyword`, target-name, alias,
  or quote matching to force a result to unrelated.
- Homonym, geography-only, broad refund/legal, title evidence, and
  comment-evidence fixtures verify current model-output preservation and keep
  CR-045's historical prompt-calibration coverage visible.
- A fixture with the target law firm or alias in title, description, author, or
  sampled comments plus a complaint/refund/avoidance signal remains eligible
  for suspected-negative or high-risk classification.
- Comment evidence is considered only when comments are collected and passed to
  the AI payload; empty comments do not invent relatedness or evidence.

### Phase 7.2D Calibration And Regression Tests

- Add a small pilot-derived or fixture-based calibration set covering broad
  refund/legal noise, unrelated law firms, homonym geography, true target
  mentions, and comment-only target references.
- A `source_keyword`-only fixture with valid model output is preserved as model
  output; applications may not silently rewrite it to `irrelevant` through
  hardcoded postprocessing.
- Tests assert structured AI output normalization remains compatible with the
  existing fields unless a documented schema extension is accepted.
- Documentation consistency passes after CR-045 task and traceability updates.

### CR-096 AI Evaluation Postprocessing Scope Reduction Tests

- Valid model output is preserved for `is_related`, `is_negative`,
  `risk_level`, `reason`, `evidence_quotes`, and `recommended_action` after
  parsing and format validation.
- `law_firm_name=北京海安律所`, no aliases, title text containing
  `北京海安律师事务所骗了`, and valid model high-risk output remains high-risk.
- Invalid JSON, missing required fields, invalid `risk_level`, provider
  failures, and timeouts still save `pending_review` fallback rows.
- Phase 20B trace tests continue to prove API keys, Authorization, cookies,
  proxy credentials, profile/local/server paths, and other sensitive data are
  redacted.
- Oversized prompt/request/response/comment snapshots remain truncated with
  explicit truncation metadata and do not block AI evaluation.

### CR-050 Report Center Lead Status Filter Precision Tests

- `/api/monitor/leads?risk=high` returns only exact high-risk rows.
- `/api/monitor/leads?risk=negative` returns only exact suspected-negative
  rows and does not include high-risk rows.
- `/api/monitor/reports?risk=negative` uses exact suspected-negative summary
  count rather than total negative count.
- A high-risk-only report is not returned by the suspected-negative filter.
- A suspected-negative-only report is not returned by the high-risk filter.
- Unrelated, evaluated no-risk, pending-review, and unevaluated filters remain
  split and continue to exclude each other.

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
- CR-115 synthetic cleanup tests simulate transient Windows deletion locks and
  prove the lower-strength validator retries generated temporary data removal,
  reports path-safe cleanup status, and does not treat residual SQLite/WAL
  files as success. Explicit `--data-dir` and `--keep-data` remain retained by
  design.

## Minimum Usable Pilot Acceptance Tests

CR-041 defines the hard gate for "the system can be used first" in a small
pilot. These tests narrow pilot readiness to safety, run lifecycle, and one
real server-like workflow. They do not require Phase 21 UI refinement, Phase
19 realtime progress, Phase 20 AI traceability, CR-038 sticky drawer close
controls, or CR-037 role/quota governance unless a later accepted P0 regression
changes that boundary.

### Pilot Gate A Email Safety Tests

- The full automated test suite can run with real-looking SMTP host, sender,
  password, and default recipients present in the active database without
  sending external email.
- Without explicit real-email opt-in, automatic report delivery, manual resend,
  and mail-test paths do not instantiate `smtplib.SMTP` or
  `smtplib.SMTP_SSL`.
- The SMTP tripwire fails loudly if tests reach the real SMTP implementation
  without explicit opt-in.
- Blocked delivery still allows report generation and records a customer-safe
  skipped delivery state or confirmed equivalent.
- With explicit real-email opt-in and complete SMTP configuration,
  pilot/production validation can send through the real mailer and record the
  trigger source and effective recipients when Phase 17.1C is included.

### Pilot Gate B Run Lifecycle Tests

- New runs persist `crawl_runs.job_id` in the column and keep compatible reads
  for legacy rows whose `summary.job_id` resolves to an existing task.
- Success, failure, timeout, cancellation, interruption, and partial-result
  paths use idempotent finalization and cannot be reopened by stale writers.
- Repeated or concurrent finalization releases account/profile/proxy locks as
  a harmless no-op after the first release.
- AI item timeout, exception, and invalid JSON save `pending_review` and
  continue when the run can safely continue.
- A simulated run with 271 collected contents and AI interruption after item
  250/251 cannot remain indefinitely `running`.
- Collected partial results can produce a report when AI is unavailable,
  partially interrupted, or degraded to manual review.

### Pilot Gate C Server-Like Real Workflow Tests

- A server-like environment starts the service, web UI, server-side browser,
  database, report root, and account profile root without relying on the
  operator's local Chrome.
- `uv run python scripts/pilot_gate_c_evidence.py --write-template
  docs/pilot_gate_c_evidence.example.json` creates a redacted operator
  evidence template and does not start services, crawl platforms, call AI,
  mutate databases, or send email.
- The generated template is intentionally incomplete and
  `uv run python scripts/pilot_gate_c_evidence.py --check
  docs/pilot_gate_c_evidence.example.json` must fail until real operator
  evidence is filled.
- Administrator web login works through the web UI.
- At least one real platform account completes QR/status login through the web
  UI and persists a server-side profile.
- At least one real monitoring task completes a platform crawl using the
  server-side profile.
- AI unavailable or provider failure does not block report generation.
- Explicit-opt-in SMTP submission succeeds in pilot/production validation,
  while local/test/diagnostic defaults remain non-sending.
- A successful SMTP `sent` delivery-log record is treated as SMTP server
  acceptance only. Pilot Gate C is not complete until an approved recipient
  manually confirms the report email arrived in inbox or spam/quarantine.
- Logs, reports, delivery records, and UI surfaces do not expose API keys,
  SMTP passwords, cookies, proxy credentials, raw profile paths, provider
  endpoints, local paths, or command lines.
- A completed redacted Pilot Gate C evidence JSON must pass
  `uv run python scripts/pilot_gate_c_evidence.py --check <evidence.json>`
  before CR-041 is closed. The checker must reject missing real-workflow
  evidence, missing recipient receipt confirmation, unchecked redaction
  surfaces, placeholder fields, secret-looking values, raw local paths, proxy
  credentials, cookies, provider endpoints, and sensitive evidence keys such as
  password, token, API key, proxy URL, or profile path.

### Pilot Gate D Non-Blocker Boundary Tests

- Phase 21, CR-038, Phase 19B-D, Phase 20, and CR-037 are not listed as first
  usable pilot blockers unless a later accepted P0 safety, security, or
  core-flow regression changes the boundary.
- Historical run `8317` remediation and orphan delivery evidence cleanup remain
  dry-run, backup, rollback, and explicit-operator-approval gated.

## Administrator Frontend Real Email Send Toggle Tests

CR-043 supersedes the rejected CR-042 validation-window design. The accepted
implementation is one persisted administrator switch on Mail Configuration.

- Mail Configuration shows one "真实邮件发送" switch and does not show separate
  open/close validation-window buttons.
- The switch writes the `real_email_delivery` runtime setting, defaults off,
  and remains persisted across refreshes/service reads.
- Normal users cannot read the Mail Configuration state or update
  `real_email_delivery`.
- Runtime Strategy does not show a second Email group for the same switch.
- Mail test is blocked with customer-safe wording when the switch is off.
- Manual resend records a non-sending skipped/failure result when the switch is
  off and may submit mocked SMTP when the administrator switch is on.
- Automatic report delivery follows the same switch: no real SMTP while off,
  real SMTP allowed while on and SMTP configuration is complete.
- The switch does not require deployment frontend gates, scheduler exclusion,
  expiry, or single-use validation-window state.
- The SMTP tripwire still fails the automated suite if real `smtplib.SMTP` or
  `smtplib.SMTP_SSL` is reached outside the explicit mocked/allowed test path.
- Frontend and delivery-history wording must say SMTP acceptance is not
  recipient inbox proof.

## Mail Test Recipient Coverage And SMTP Acceptance Tests

CR-044 fixes the Mail Configuration test-mail path so administrator validation
matches the configured default-recipient list.

- With `real_email_delivery` off, test mail remains blocked and no SMTP client
  is instantiated.
- With `real_email_delivery` on and two global default recipients configured,
  the test-mail path submits one message addressed to both recipients when no
  explicit test target is supplied.
- The test-mail API returns the submitted recipient count and recipient source
  without exposing SMTP passwords.
- The Mail Configuration frontend success message shows the submitted
  recipient count and states that SMTP acceptance is not inbox proof.
- Mocked-SMTP automated tests cover the multi-recipient path without sending
  external email.

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
  - create task entry -> Task Center task grouping -> run records / Run Detail;
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
- Administrator navigation includes operations home, monitoring, Task Center,
  resource management, and system configuration.
- Normal-user navigation includes only permitted user-facing pages.
- Resource Management and System Configuration use expandable navigation
  groups instead of detached hover-only popovers.
- User identity and logout are grouped in the top-right account area on
  desktop and remain reachable on mobile.
- CR-075 verifies one coherent responsive navigation model: desktop `>=1280px`
  uses the full/collapsible sidebar, tablet/narrow desktop `768px - 1279px`
  keeps a persistent collapsed icon rail without the top-left mobile trigger,
  and mobile `<768px` keeps the top-left drawer trigger with backdrop, Escape,
  and page-selection close behavior.
- CR-076 verifies the mobile header layout inside that same model: at
  `390x844`, navigation, refresh, and account controls must not squeeze the
  product title; the title and status chips use their own readable rows.
- CR-077 verifies the final loaded cascade for that same mobile header: tests
  inspect all inline style blocks and browser checks confirm the computed
  mobile layout still keeps the title horizontal after `monitor.css` and page
  inline styles both load.
- CR-078 verifies the responsive shell after the final loaded cascade: mobile
  resource pages keep the title horizontal and page width inside the viewport,
  the closed drawer remains off-canvas, and the tablet collapsed side rail keeps
  its final navigation item out of the bottom collapse-button hit area.
- CR-079 verifies the compact mobile header rail after further phone browser
  review: the mobile navigation trigger keeps its accessible open-navigation
  control but visually occupies a stable 40px icon-button column, the product
  title stays in the first-row main column, and status chips move to a
  full-width wrapping row so resource pages cannot squeeze the title into
  one-character columns.
- CR-080 verifies the tablet/narrow-desktop side rail after browser review:
  `768px - 1279px` keeps the persistent collapsed icon rail and existing
  collapse button, but does not expose a bottom horizontal scrollbar; the
  navigation row remains vertically scrollable and the final permitted entry
  remains reachable.
- CR-085 verifies the final inline cascade for narrower in-app tablet panels:
  around `809px`, `body.sidebar-collapsed .shell` must still compute to a
  `68px` icon rail plus content column, the top-left mobile trigger must not be
  painted, and the sidebar collapse button must remain visible.
- Mobile navigation can open, close, select nested pages, and preserve active
  state without clipped menus.

### Phase 12B Page Entry And Role Flow Tests

- Page title, description, primary action, and toolbar structure are consistent
  across core pages.
- Task-loop shortcuts lead to create task, Task Center task grouping, Task
  Center run records, and relevant resource issue pages.
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
- Metrics provide drilldown links to Monitoring, Task Center task grouping,
  Task Center run records, or administrator resource pages.
- Page-level refresh updates operations-home data and shows last-updated time.

### Phase 13C Operations Home Responsive And Role Tests

- Normal users only see own task/report/run health and business-safe resource
      signals.
- Desktop 1440px, tablet 1024px, and mobile 390px layouts have no severe
      overlap, hidden primary actions, or unreadable metric cards.
- Administrator resource health drilldowns remain hidden from normal users.

## CR-097 Operations Home Visual Density Reduction Tests

- The Operations Home first viewport remains focused on visual signals rather
  than prose.
- Task health, run activity, report/review, email delivery, lead risk, and
  resource health remain represented by compact metrics and bars.
- The home includes one dominant flow chart plus compact platform bars/heatmap
  blocks and delivery/lead breakdowns without introducing a chart dependency.
- Desktop and tablet checks must confirm the flow chart has no visibly
  stretched Chinese labels or circular markers.
- The visual priority panel uses short business labels and does not expose raw
  fields such as `job_id`, `run_id`, `report_id`, `summary.platform_results`,
  `collection_progress`, `ai_progress`, `job_snapshot_json`, or
  `email_delivery_logs`.
- Desktop 1440px, tablet 1024px, and mobile 390px layouts remain readable
  after the visual-density reduction.
- Desktop 1440x900 and tablet 1024x768 checks must confirm the Operations Home
  bottom does not exceed the left navigation/shell viewport height; the
  shortcut dock is hidden on those widths and remains available only on mobile.
- Administrator diagnostics remain gated and do not leak into normal-user
  views.

## CR-098 Operations Home Data-First Visual Refit Tests

- The Operations Home follows the existing project design system: light
  enterprise shell, teal accent, compact type, modest radii, and risk color
  reserved for exception overlays.
- The first screen prioritizes charts, bars, and numbers over prose, tables, or
  status-heavy blocks.
- The stage flow is present as five visual stages and uses uniform teal fill
  with risk represented by an alert overlay rather than competing fill colors.
- The priority panel shows only compact exception bars and limits the visible
  queue to the most important issues.
- The shortcut dock is hidden by the final CR-098 cascade and does not add page
  height on desktop, tablet, or mobile.
- Platform heatmap blocks are hidden when the platform bar chart already gives
  the needed breakdown.
- Desktop `1440x900` and tablet `1024x768` checks confirm the Operations Home
  bottom stays within the left navigation/shell height.
- Mobile `390x844` checks confirm chart-first ordering, no duplicated
  page-kicker copy, no horizontal overflow, and no narrow one-character Chinese
  text columns.
- Role boundaries, drilldowns, dashboard API compatibility, Task Center, Run
  Detail, drawer, modal, enhanced select/date, routing, owner-scope, and
  report-scope behavior remain unchanged.

## CR-099 Operations Home Legend-First Visual Clarity Tests

- The Operations Home exposes visible legend or direct-key treatment for the
  flow chart, delivery/review chart, attention panel, and resource chart.
- KPI cards and attention rows use normalized icon sizes rather than oversized
  decorative marks.
- Platform composition uses a category palette and donut-plus-list breakdown,
  while status-driven charts keep semantic status colors.
- Desktop `1440x900` and tablet `1024x768` checks still confirm the Operations
  Home bottom stays within the left navigation/shell height.
- Mobile `390x844` checks still confirm no horizontal overflow, no narrow
  one-character Chinese text columns, and chart-first vertical ordering.
- Role boundaries, drilldowns, dashboard API compatibility, Task Center, Run
  Detail, drawer, modal, enhanced select/date, routing, owner-scope, and
  report-scope behavior remain unchanged.

## CR-100 Operations Home Dense Visual Composition Tests

- Desktop/tablet Operations Home uses content-sized composition rather than
  stretching sparse data into large empty panels.
- The flow chart includes denser graphical structure while preserving the same
  stage meaning and drilldown behavior.
- Desktop `1440x900` and tablet `1024x768` checks still confirm the Operations
  Home bottom stays within the left navigation/shell height boundary.
- Mobile `390x844` checks still confirm no horizontal overflow, no narrow
  one-character Chinese text columns, and chart-first vertical ordering.
- Role boundaries, drilldowns, dashboard API compatibility, Task Center, Run
  Detail, drawer, modal, enhanced select/date, routing, owner-scope, and
  report-scope behavior remain unchanged.

## CR-101 Operations Home Flow Chart Layer Separation Tests

- Historical/archive-only after CR-105. These checks describe the old
  handcrafted flow-chart implementation and must not be used to require
  `流程总览`, `.operations-stage-head`, `.operations-stage-plot`, or other
  `.operations-stage-*` DOM in a future ECharts dashboard.
- Use these notes only when inspecting the verified CR-101 historical
  implementation. The verified CR-105 implementation is tested against the six
  chart-dashboard containers instead.

## CR-102 Operations Home Flow Chart Node Simplification Tests

- Historical/archive-only after CR-105. These checks describe the old
  handcrafted flow-chart node simplification and must not be used to require
  `.operations-stage-node-top`, `.operations-stage-chip`, or any
  `.operations-stage-*` DOM in a future ECharts dashboard.
- Use these notes only when inspecting the verified CR-102 historical
  implementation. The verified CR-105 implementation is tested against the six
  chart-dashboard containers instead.

## CR-103 Operations Home Flow Chart Semantic Trend Rebuild Tests

- Historical/archive-only after CR-105. These checks describe the old
  handcrafted `流程总览` semantic-trend implementation and must not be used to
  require `.operations-stage-chart`, `.operations-stage-line-primary`,
  `.operations-stage-line-secondary`, or any `.operations-stage-*` DOM in a
  future ECharts dashboard.
- Use these notes only when inspecting the verified CR-103 historical
  implementation. The verified CR-105 implementation is tested against the six
  chart-dashboard containers instead.

## CR-104 Operations Home Data Cockpit Moderate Rebuild Tests

- Historical verified baseline before CR-105: these checks describe the
  superseded handcrafted chart-first cockpit. They remain historical
  regression evidence and do not require the current ECharts dashboard to
  preserve the old internal chart DOM.
- After CR-105 implementation, `.operations-trend-svg`,
  `.operations-trend-line-primary`, `.operations-trend-line-secondary`, and
  handcrafted trend-path assertions are CR-104 regression-only checks, not
  acceptance criteria for the new dashboard. CR-105 tests should verify
  ECharts-backed chart containers and options instead of requiring the
  handwritten SVG fragments to remain.
- The historical CR-104 Operations Home kept the existing dashboard data
  contract and drilldown behavior while reading as a chart-first data cockpit.
- The historical CR-104 chart DOM included `.operations-cockpit-trend`,
  `.operations-window-toggle`, `.operations-trend-svg`,
  `.operations-trend-line-primary`, and `.operations-trend-line-secondary`.
- The trend chart should expose visible legend items for `业务总量` and
  `异常 / 待处理`, plus a 7-day / 14-day switch.
- If the dashboard payload does not include trend buckets, the frontend should
  use read-only aggregation from `/runs` and `/reports` without changing the
  backend contract.
- The issue panel should render compact horizontal issue bars rather than
  mixed icon/status cards.
- The lower area should keep `平台分布` and `交付 / 复核` as chart-first
  breakdowns without explanatory paragraphs or tables.
- Administrator view should keep compact resource and system-diagnostic entry;
  normal-user view should not leave a blank resource area.
- Desktop `1440x900` and tablet `1024x768` checks should still confirm the
  Operations Home bottom stays within the left navigation/shell height.
- Mobile `390x844` checks should confirm no overlap, no horizontal overflow,
  and no chart deformation.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"`,
  `node --check api/webui/monitor/monitor.js`, inline monitor script parse,
  in-app browser review, and `uv run python scripts/check_docs.py` must pass.

## CR-105 Operations Home ECharts Dashboard Rebaseline Tests

- The requirement baseline classifies CR-097 through CR-104 as verified
  historical predecessors and CR-105 as the current verified ECharts dashboard
  baseline.
- No current planning or test text requires preserving `流程总览`,
  `.operations-stage-*`, heatmap-block, or earlier no-chart-library
  constraints for the current dashboard.
- Apache ECharts is vendored locally under the existing static asset path and
  is not loaded from a CDN.
- The expected ECharts vendor file is
  `api/webui/monitor/vendor/echarts.min.js`, served through
  `/static/monitor/vendor/echarts.min.js`. Static tests should fail if
  `/monitor` references `https://`, `http://`, `cdn`, `unpkg`, `jsdelivr`, or
  another remote script for ECharts, and HTTP checks should confirm the local
  vendor path returns 200.
- Core CR-105 chart tests should fail if `监控走势`, `问题分布`, `平台分布`,
  or `交付 / 复核` continue to use handwritten SVG path geometry or custom DOM
  percentage-bar chart structures instead of ECharts chart instances. SVG
  icons and ECharts internal rendering are allowed; application code should not
  preserve CR-104 path helpers such as `operationsTrendLinePath()` as the chart
  renderer.
- The verified dashboard covers KPI micro charts, required 7/14-day trend
  controls, optional 30-day trend only when bounded existing-data aggregation is
  clean, issue distribution, platform/source breakdown, delivery/review
  composition, administrator resource health, color-role ledger, visible
  legends/direct labels, desktop/tablet/mobile order, and role boundaries.
- The implementation exposes six stable modules: KPI strip, `监控走势`,
  `问题分布`, `平台分布`, `交付 / 复核`, and administrator-only `资源健康`.
- Desktop `>=1280px` checks cover five equal KPI cards, a `65% / 35%` trend
  and issue row, and three equal lower modules. The dashboard aligns titles,
  key numbers, legends, and direct labels on consistent left edges.
- Browser or screenshot checks must treat module alignment as a hard
  acceptance gate: card outer edges, row gutters, title/header heights,
  headline numbers, legend starts, chart plot origins, KPI label/value/
  micro-chart positions, and lower-card heights should visibly line up. Fail
  the review for staggered title baselines, mismatched plot starts, uneven
  gutters, or lower modules that drift after `资源健康` is hidden for normal
  users.
- Tablet checks cover KPI `5` columns or `3+2`, full-width main trend, and
  one- or two-column lower modules. Mobile `390x844` checks cover two-column
  KPI cards, trend first at readable height, no hover dependency, no
  horizontal overflow, and no one-character Chinese text columns.
- Color tests or visual review should verify the semantic ledger:
  `#0F766E` normal/completed/business-total, `#2563EB` running/realtime,
  `#D97706` pending review/action, `#DC2626` failure/exception,
  `#991B1B` high risk, and platform category colors only inside platform
  distribution.
- Current implementation data checks reuse existing tasks, runs, reports,
  mail state, AI lead/review, platform, and administrator resource data. Task
  funnel, platform risk matrix, keyword heat, AI quality, and task rankings are
  future enhancements and must not be required persisted fields.
- Dashboard API and frontend tests should fail if the current CR-105
  implementation adds or requires fields such as `task_funnel`, `risk_matrix`,
  `keyword_heat`, `ai_quality_score`, or `task_ranking`, or renders placeholder
  "future enhancement" panels for them.
- Missing trend buckets are handled through frontend read-only aggregation from
  existing `/runs` and `/reports` in the current implementation.
  Backend-provided trend buckets are a later enhancement unless a separate CR
  accepts them.
- Loading, empty, stale, and chart-local error states keep container dimensions
  stable. Empty charts render zero-value chart surfaces; stale views show last
  updated time; one failed chart does not blank the rest of the dashboard.
- Interaction checks cover 7/14-day time window controls and, when implemented
  from bounded existing data, 30-day controls. If 30-day aggregation cannot be
  supported cleanly without backend buckets, the first CR-105 implementation may
  ship 7/14 only and defer 30-day buckets to a later accepted CR. KPI
  click-through, issue-bar click-through, platform-bar click-through,
  high-risk/pending-review drilldowns, and tap/click detail on mobile must not
  rely on hover.
- The dashboard must answer within about 10 seconds whether today's monitoring
  is normal, where exception/high-risk/pending work exists, and where the user
  should click next. Browser review should fail a state-card collage or
  process-node diagram even if individual numbers render.
- Future implementation checks must preserve `/api/monitor/dashboard`
  compatibility, role gating, drilldowns, Task Center, Run Detail, drawer,
  modal, enhanced select/date, routing, owner-scope, report-scope, and
  top-bar refresh behavior.
- Future browser checks at `1440x900`, `1024x768`, and `390x844` must confirm
  readable charts, visible essential values without hover, no horizontal
  overflow, and no one-character Chinese text columns.
- Normal-user checks must confirm administrator resource health is hidden
  without leaving an empty module, and account/proxy/AI/SMTP/session details
  are not exposed. On desktop, the remaining lower modules should reflow to two
  equal columns or otherwise fill the hidden resource-health space without a
  blank third slot.

## CR-106A Operations Home Data-Aware Signal Refinement Tests

- Documentation tests should confirm CR-105A remains the verified ECharts
  dashboard baseline and CR-106A is a follow-up optimization, not a reopened
  CR-105 implementation.
- CR-106A static tests should verify the plan and implementation continue to
  preserve `/api/monitor/dashboard` compatibility, local ECharts, role gating,
  Task Center, Run Detail, drawer/modal/select/date behavior, routing,
  owner-scope, report-scope, and top-bar refresh behavior.
- Data-source tests should use bounded fixtures or safe local aggregates to
  prove the top status, issue distribution, platform distribution, mail module,
  and resource health are derived from existing dashboard/runs/reports data.
  Tests must not require local sample counts as hard constants.
- `问题分布` tests should prove action severity is visible: high-risk leads,
  pending review, mail failure, and run failure/skip remain separately
  readable and clickable.
- `平台分布` tests should prove platform volume is not confused with platform
  failure signals when existing run summary fields contain `platform_results`
  or `failed_platforms`.
- Mail-module tests should confirm CR-106A labels or maps the module as
  report-level delivery state from `reports.email_status`; CR-106A must not
  silently aggregate `email_delivery_logs` as the dashboard mail-health source.
- Resource-health tests should confirm administrators can see action-oriented
  account/proxy/AI/mail/session health cues while normal users do not see
  account/proxy/AI/SMTP/session details or an empty resource placeholder.
- Mobile browser checks at `390x844` should confirm KPI cards do not dominate
  the first screen before `监控走势` and `问题分布`, and there is no horizontal
  overflow, text overlap, or one-character Chinese column.
- Desktop/tablet browser checks at `1440x900` and `1024x768` should confirm
  the dashboard still reads as one aligned chart cockpit and not a state-card
  collage.
- Sensitive-data checks should fail if Operations Home exposes recipients,
  SMTP secrets, proxy URLs, cookies, profile paths, account names, raw delivery
  errors, or other administrator-only resource details to normal users.
- Dashboard data-source tests should prove `问题分布`, `平台分布`, and `邮件`
  derive from existing dashboard/runs/reports fields without querying
  `email_delivery_logs`.
- Implementation tests should use bounded fixtures or safe aggregates. They
  must not hard-code local sample counts as acceptance constants.
- Normal-user browser checks at `1440x900`, `1024x768`, and `390x844` should
  confirm `资源健康` is not rendered, lower modules reflow, and no
  administrator resource terms appear.
- Standard checks for an implementation batch remain: targeted Operations Home
  pytest coverage, `node --check api/webui/monitor/monitor.js`, inline monitor
  script parse, `uv run python scripts/check_docs.py`, `git diff --check`, and
  role/browser checks for administrator and normal-user sessions.

## CR-106B Email Delivery Log Dashboard Aggregation Tests

- CR-106B remains `Needs Confirmation`; no implementation tests are required
  until the requirement is accepted.
- If accepted later, tests must prove any dashboard aggregation from
  `email_delivery_logs` uses scoped safe counts/statuses only, preserves
  report-level `reports.email_status` compatibility, follows owner/workspace
  scope rules, and does not expose recipients, SMTP secrets, proxy URLs,
  cookies, profile paths, account details, or raw sensitive delivery errors.

## CR-107 Windows One-Click Local Startup Launcher And Browser URL Separation Tests

- The launcher must keep the service bind host and browser open URL as distinct
  values.
- The default browser URL should resolve to the local machine URL even when the
  service bind host is `0.0.0.0`.
- An explicit browser URL override should be honored without changing the bind
  host.
- Existing service-only startup commands must remain available and documented.
- The launcher should be covered by a lightweight Python unit test that does
  not start a real browser or open a real port.
- Documentation tests should confirm the quick-start instructions mention the
  one-click Windows launcher and the remote-access override behavior.

## CR-121 Crawler Account Identity Snapshot Header Tests

- A prepared managed page and an unprepared background page must not share
  request-header evidence. A background `en-US,en` request must not overwrite
  a prepared `zh-CN` request.
- A mismatch emitted by the prepared page itself must still produce
  `account_identity_snapshot_mismatch` with field-scoped safe evidence.
- The child crawler plan/result binding, persisted runtime snapshot, and
  account/profile/platform identity checks remain strict and unchanged.
- A real designated-account run must finish with a successful Douyin platform
  result and at least one persisted content row; a failed run must retain its
  safe error evidence for diagnosis.
- Final gates include focused provider/runner tests, the complete monitoring
  regression, Python compile, documentation consistency/regression,
  `git diff --check`, and independent read-only review.

## CR-120 Local Visible Login Automatic Reconciliation Tests

- The account-specific visible-login route must return the same browser,
  `profile_key`, Profile, proxy policy, and platform binding used by QR and
  crawl plans.
- A loopback CDP probe must inspect only the recorded live process and return
  a waiting result while the platform still requires manual verification.
- Concurrent visible-login requests for different accounts on one platform
  must serialize; only one window may open on the platform's fixed debug port.
- CDP browser process information must match the recorded PID before login
  inspection or browser close, and an unrelated page must not become a target
  platform fallback.
- A detected logged-in state must close only the owned browser, wait for
  Profile release, and invoke the normal account-level Profile check once.
- A window closed before detection must trigger one automatic final check;
  an unrelated/mismatched process or debug port must fail closed.
- A completed window result is idempotent, and an unreachable endpoint after
  the startup grace period returns an actionable failure instead of indefinite
  verification guidance.
- Frontend reconciliation uses serial `setTimeout` scheduling, bounded
  attempts, stale-account/session guards, and remains active if the drawer is
  closed. It must not use an overlapping `setInterval` loop.
- Generic platform login without an account binding remains status-only, and
  production/server QR behavior remains unchanged. Production mode rejects
  both visible-window open and reconciliation routes.
- Live local verification must prove automatic detection and safe account
  state persistence without recording raw Cookie values, Profile paths, or
  platform secrets in logs or documentation.
- Final gates include focused login-browser/route tests, the complete
  monitoring regression, inline JavaScript parse, documentation consistency,
  `git diff --check`, browser checks, and independent read-only review.

## CR-119 Platform Account Recent Error Compactness Tests

- The labelled `.account-summary-recent-error` card and basic-form
  `social_account_error_summary` each use one visible line with
  `overflow: hidden`, `text-overflow: ellipsis`, and `white-space: nowrap`
  without widening the account drawer.
- Populated displays expose their complete customer-safe display text through
  titles. The basic-form empty state removes any stale title and remains
  `最近暂无异常。`.
- The advanced `social_account_last_error` textarea keeps the complete value;
  save payloads, account list rows, warning state, login controls, and account
  actions remain unchanged.
- Browser checks cover desktop and narrow widths, verify stable heights for
  both displays, no document horizontal overflow or overlap, reachable
  advanced full text, and reachable fixed-footer actions.
- Final gates include focused frontend coverage, complete monitoring
  regression, inline JavaScript parse, documentation consistency/regression,
  `git diff --check`, and independent read-only review.

## CR-118 QR Login Success Monotonicity And Profile Restart Tests

- Persisted `success` is a monotonic login-session terminal state. A later
  `qrcode_failed`, timeout, or platform-error update returns the existing row
  without changing status, message, QR image, or `updated_at`.
- GET of an already terminal login session returns its persisted result and
  current account state without calling the QR browser poller or account check.
- Concurrent GETs for one pending session share one serialized poll and account
  verification. A second request that starts during the first verification
  must read the resulting terminal success instead of polling a closed browser.
- Verification-code submission and request POSTs share the same session lock
  with GET. A GET started during either POST's successful verification must not
  poll the already-closed browser. QR creation and deletion use the same lock.
- Pending login sessions retain existing QR polling, verification, failure
  reconciliation, and successful account-level Profile-check behavior.
- QR startup checks an already authenticated persistent Profile before
  preparing a login dialog or QR code.
- A bounded QR polling timeout/cancellation cancels and awaits its child task;
  browser cleanup produces no unobserved `TargetClosedError` task.
- The frontend login-session loop uses one serial timeout only after the prior
  request settles; it has no asynchronous `setInterval` in that loop. If a new
  login session starts while an older request is in flight, the stale callback
  must return without clearing the new session's active ID or timer.
- Real local verification restarts the service before checking the designated test account,
  then proves the same `profile_key`, persistent Profile, browser source,
  `fallback_used=false`, active identity, and `requires_relogin=false`.
- The real check records only safe counts, states, versions, and timestamps.
  Cookie values, raw Profile paths, QR data, and platform secrets stay outside
  documentation and logs.
- Final gates include adjacent QR tests, Phase 5.1 focused tests, complete
  monitoring regression, compile, documentation consistency/regression,
  `git diff --check`, and independent read-only review.

## CR-117 Windows Local Browser Selection And Chromium Bootstrap Tests

- A clean local deployment must choose valid explicit configuration, Chrome,
  Edge, supported Chromium, installed Playwright Chromium, then Playwright
  installation in that order. Chrome must win when Chrome and Edge both exist.
- The versioned manifest must be written atomically and reused before discovery.
  Later browser installation must not alter it. Missing saved system/explicit
  browsers and explicit conflicts with Profile data must fail closed.
- The complete read/select/write transaction must be cross-process locked. A
  concurrent local-system selection and service-only Playwright selection must
  return one identical persisted result.
- Existing Profile data without a manifest must preserve a valid explicit
  executable or bind to Playwright Chromium, never a newly detected browser.
- A missing selected Playwright Chromium must run the active interpreter with
  `-m playwright install chromium`, keep output attached to the console, then
  re-resolve and verify the executable before service spawn.
- Installer nonzero exit, launch error, post-install probe error, and
  post-install absence must stop without starting a service and must include
  the exact manual retry command.
- A valid runtime browser version different from the generated UA version must
  be recorded as effective evidence without a mismatch or re-login result.
  Chrome and Edge `Edg/...` CDP products must both parse. Missing/malformed
  version evidence and other field mismatches remain errors.
- Tests must use temporary manifests, fake paths, and subprocess results. They
  must not
  download a browser, open a browser, bind a port, start FastAPI, inspect user
  browser profiles, or alter Playwright's real cache.
- Existing `windows_oneclick_launcher` tests must remain green. Static tests
  must prove both local batch launchers check `uv` and run the shared preflight
  while service-only/Docker entry points remain unchanged.
- Final gates are focused CR-107/CR-117 tests, complete monitoring regression,
  Python compile, documentation consistency/regression, `git diff --check`,
  and independent read-only full-diff review including artifact leakage.

## CR-108 Local/Server Login Initialization And Verification Flow Hardening Tests

Documentation gate:

- `CHANGE_REQUESTS.md`, `TASKS.md`, `CURRENT_STATE.md`, `TEST_PLAN.md`, and
  `TRACEABILITY.md` record CR-108 with the current mainline number.
- Old worktree CR-107/CR-108 server-login documents are not copied with their
  old numbering; their useful evidence is remapped into current CR-108.
- `uv run python scripts/check_docs.py` and `git diff --check` pass before
  non-document code changes begin.

Docker/server packaging:

- `docker compose config` succeeds after selectively migrating Docker files.
- Docker defaults use server-like login behavior:
  `MONITOR_LOGIN_QR_HEADLESS=true` and
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.
- Docker documentation states that Compose configuration validity does not
  prove host Docker Desktop, WSL, or `vmcompute` health.

Profile contention:

- Starting a QR login for an account whose runtime profile is already occupied
  by a local login window returns a clear customer-safe conflict state/message
  instead of raw `TargetClosedError` or raw profile path text.
- Opening a local login window for an account with an active QR session closes
  or supersedes that session and tells the operator which login path is active.
- Same-account profile contention tests cover both `profile_key` and resolved
  runtime path matching.
- Server/production mode keeps local-window login unavailable when
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.

QR initialization hang regression:

- A QR startup that reaches Playwright/browser context creation and then hangs
  before QR discovery must return `qrcode_failed` with a customer-safe timeout
  message within the configured QR timeout instead of blocking the API request
  indefinitely.
- The timeout path must close any half-initialized Playwright/browser context
  and must not leave the session in the in-process active QR session registry.
- Polling a fresh database `preparing` session before an in-process QR handle
  exists must keep the session pending during the QR startup timeout window.
- Polling a stale `preparing` session without an in-process QR handle after
  the timeout window may convert it to `qrcode_failed` with a customer-safe
  retry/manual-window message.
- After the QR image has been generated, each poll step must be bounded:
  MediaCrawler login-state checks, QR rediscovery, page preparation, and manual
  verification detection must not block the `/login-sessions/{id}` response.
- If a scan-time poll substep times out, the session should stay active and
  return `waiting_confirm` with a customer-safe "continue confirmation" message
  instead of closing the browser or marking the login failed.

Local Windows first-run login:

- A newly cloned Windows local setup can reach a documented first-run path:
  create/select platform account, start QR or allowed manual login, complete
  platform verification manually when required, close the browser window, and
  run account check/continue confirmation.
- The UI and API keep captcha, slider, SMS, and device checks as
  `needs_verification` or manual-action states; tests must not assume bypass.
- Customer-facing responses do not expose `profile_path`, cookies,
  verification codes, QR payloads, local commands, proxy credentials, or raw
  browser profile directories.

Selective SMS/diagnostic migration:

- If Douyin SMS submission precision is migrated, a
  `#uc-second-verify` overlay containing send/resend controls and an exact
  `验证` submit control must click only the exact visible `验证` control while
  submitting a received code.
- If login diagnostics UI is migrated, default modal text shows current state
  and next action first; technical page URLs, titles, backend polling records,
  and platform navigation noise stay collapsed.

Required code-stage checks:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "windows_oneclick_launcher or login_session or qrcode or login_browser or verification_code or manual_sms"`
- `node --check api/webui/monitor/monitor.js`
- existing inline monitor script parse check
- `uv run python scripts/check_docs.py`
- `git diff --check`

## CR-109 Monitoring Task Collection Rule Explanation Removal Tests

- The Monitoring / 舆情监控 task section must not render the "采集规则说明"
  disclosure block below the task table.
- Static frontend coverage should assert the removed text is absent from the
  task section while preserving filters, task table, drawer, and workflow
  markers.
- Task-page CSS should not keep rules that only target the removed
  `#jobs details.advanced` disclosure.
- Required checks:
  - `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_21d_monitoring_tasks_and_task_drawer_visual_pass_preserves_workflow"`
  - `node --check api/webui/monitor/monitor.js`
  - `uv run python scripts/check_docs.py`
  - `git diff --check`

## CR-110 QR Login SMS Verification Manual Submission Regression Tests

- Backend login-session routes must expose manual SMS verification submission
  and SMS send-request actions for active QR browser sessions.
- The backend must reject malformed SMS codes without exposing sensitive
  state, and must keep the session in `needs_verification` for inline retry.
- Server-side QR browser helpers must fill a manually received code into the
  visible verification input and submit it.
- Douyin `#uc-second-verify` overlays must prefer exact visible `验证` submit
  controls before broader confirmation selectors, so send/resend controls are
  not clicked as submit.
- SMS send-request helpers must click visible send-code controls without
  receiving, reading, or automating the SMS.
- The frontend login session panel must show send, input, inline validation,
  submit, and continue-confirm actions when `verification_type` is `sms`.
- The frontend must preserve a typed code while the login session panel
  re-renders, and polling must stop on `needs_verification` so input is not
  repeatedly overwritten.
- Required checks:
  - `uv run python -m pytest tests/test_monitoring_mvp.py::test_login_session_verification_code_route_submits_sms_code tests/test_monitoring_mvp.py::test_login_session_verification_code_request_route_sends_sms_code tests/test_monitoring_mvp.py::test_qrcode_manual_sms_verification_submission_fills_server_page tests/test_monitoring_mvp.py::test_frontend_sms_verification_has_manual_code_submission tests/test_monitoring_mvp.py::test_frontend_sms_verification_has_send_request tests/test_monitoring_mvp.py::test_frontend_sms_verification_preserves_input_during_polling tests/test_monitoring_mvp.py::test_frontend_sms_verification_panel_is_structured_and_inline_validated`
  - `uv run python -m pytest tests/test_monitoring_mvp.py -k "login_session or qrcode or login_browser or verification_code or manual_sms"`
  - `uv run python -m py_compile api/monitoring/login_qrcode.py api/routers/monitor.py`
  - `node --check api/webui/monitor/monitor.js`
  - inline monitor script parse check
  - `uv run python scripts/check_docs.py`
  - `git diff --check`

## CR-111 Current-Main Documentation State Synchronization Tests

- Use clean `main@abb4d66` as the baseline; unmerged worktrees are historical
  evidence only and cannot establish current-main completion.
- Compare every CR lifecycle label in `CHANGE_REQUESTS.md` with completed task
  evidence, `TRACEABILITY.md`, `CURRENT_STATE.md`, `TEST_RESULTS.md`, and
  relevant code/tests before promoting it.
- Verify CR-107 no longer has unchecked planning duplicates beside its
  completed implementation checklist.
- Verify CR-052 has a traceability row and CR-066 has an explicit lifecycle
  status.
- Verify Phase 21 and CR-107 through CR-110 are described as merged/current-main
  history, not active working-tree implementation.
- Verify Phase 5.1P remains the first unblocked lane; Phase 5.1A-D, Phase 5.2,
  CR-092, CR-093, CR-094, CR-106B, CR-037, and Phase 7.1D keep their dependency,
  future, confirmation, deferred, or operator gates.
- Verify no product code, schema, runtime data, sensitive files, or old
  worktree content changes in CR-111.
- A regression fixture with verified CR-095 followed by `Needs Confirmation`
  CR-106B must not attribute CR-106B's status to CR-095; the real pending CR
  still remains detectable within its own section.
- Run `uv run python scripts/check_docs.py`, plugin Markdown consistency audit,
  machine-readable documentation dry-run export/validation, relevant pytest
  coverage, `docker compose config --quiet`, and `git diff --check`.
- Treat documentation checks as structural evidence, tests as code-regression
  evidence, Compose config as packaging evidence, and existing real-pilot
  records as historical pilot evidence; do not merge those proof levels.

## CR-112 Local Browser Auto-Sync Cookie Acquisition Tests

Documentation-stage checks:

- Verify CR-112 is classified as a `New Capability` with status `Accepted /
  Dependency-Gated` in `CHANGE_REQUESTS.md`, `TASKS.md`,
  `CURRENT_STATE.md`, and `TRACEABILITY.md`.
- Verify the five plan artifacts and
  `docs/cookiebridge-compatibility-spike-result.md` are linked from formal
  governance documents and preserve packet status boundaries.
- Before Packet C, verify the Packet B result, material plan update, and every
  CR-112 formal reference including `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`
  are staged in one atomic Packet B commit.
- Verify Phase 5.1P and Phase 5.1A-D plus current follow-up regressions remain
  recorded as verified and merged, the separate CR-047 Linux/server-like real
  acceptance remains operator-gated, and accepted sequencing places CR-112
  before CR-070 without claiming that local evidence closes CR-047.
- Verify CR-112 is `Accepted / Verified (Packet B)`, Packet C/D remain
  dependency-gated, and the current server-first QR acceptance boundary is
  unchanged before implementation evidence exists.
- Verify `DECISIONS.md`, CR-112, account-environment guidance, and all five
  plan files agree on the confirmed sub-decision: both login modes converge on
  one account-bound persistent Profile, encrypted Cookie is
  bootstrap/refresh/recovery/migration material, failed refresh preserves the
  prior Profile and Cookie, and managed crawler child argv contains no raw
  Cookie after Packet C.
- Verify every formal CR-112 document and Packet B/C/D agrees on same-machine
  Windows scope, reuse-first/minimal-adaptation evaluation, Packet-B-selected
  direct managed-context ownership, administrator full-Cookie reveal/copy security boundary,
  mandatory Douyin/Xiaohongshu real acceptance, and Kuaishou Deferred status.
- Run `uv run python scripts/check_docs.py`, `git diff --check`, a trailing
  whitespace/end-of-file check for the five new plan files, and focused
  independent read-only review.

Packet C fake/unit/integration tests after its start gates pass:

- Feature disabled by default starts no acquisition browser and shows no active
  auto-sync action. The rejected Cookie-bridge route remains unmounted in both
  feature states: normal HTTP returns 404 and the pinned Starlette/Uvicorn
  baseline rejects unmatched WebSocket upgrade with 403 before acceptance.
  Baseline assertions use FastAPI `0.110.2`, Uvicorn `0.29.0`, and locked
  Starlette `0.37.2`; dependency changes require re-audit while route absence
  and zero WebSocket protocol state remain invariant.
- Provider tests must prove valid explicit executable, Chrome, Edge, and
  supported Chromium precedence and reject invalid explicit paths or locked
  account fallback to another browser, Profile, proxy, user agent, or network.
- Acquisition-binding tests must cover stale/replayed request, wrong account,
  `profile_key`, login session, promotion, provider resolution, attempt ID,
  platform, generation, missing/closed context handle, and caller-supplied raw
  Profile path rejection.
- Route tripwires must prove no Cookie-bridge HTTP/WebSocket route is mounted
  and that production-like proxy/host headers do not create one.
- State-machine tests must cover success, failure, timeout, cancellation,
  browser close, browser unavailable, service restart/interruption, late
  result rejection, idempotent finalization, lock release, and acquisition-
  context cleanup.
- Promotion-state tests must cover every transition from `preparing` through
  `committed`/`rolled_back`, including cancellation at/after `swapping`, service
  kill before and after each directory move/database transaction, and startup
  recovery before account use.
- Recovery-table tests must cover every permitted committed/non-committed
  fixed/candidate/rollback shape, one-checkpoint-lag after each rename, wrong or
  missing operation marker, checkpoint-ahead evidence, and every contradictory
  shape entering `recovery_required` without deleting a directory.
- Multi-account tests must run Account A/Profile A/context X and Account
  B/Profile B/context Y concurrently with reversed completion order and prove
  no first/newest/only-context selection or Cookie leakage.
- Cookie validation/persistence tests must reject wrong-platform or wrong-account
  material, initialize an account-bound persistent Profile, preserve the
  previous fixed active Profile and verified Cookie through journaled
  candidate/rollback recovery, and commit verified ciphertext, source,
  identity snapshot, profile-ready metadata, account status, and
  journal state together after the active-path recheck.
- Promotion filesystem tests must cover new-account/no-active-path, existing
  active Profile, same-volume enforcement, disk full, open handles,
  antivirus/permission rename failure, missing/duplicate directories, cleanup
  failure, at-most-one rollback copy, and never deleting the only usable
  Profile. Contradictory evidence produces `recovery_required` and blocks use.
- Cleanup tests must trigger rollback deletion after the first successful run,
  through startup/periodic `cleanup_after` scan with an idle account, and before
  a new promotion/export/backup; failed cleanup retains one artifact and blocks
  refresh/export rather than packaging an operation marker.
- Candidate-isolation tests must prove the fresh candidate uses the locked
  Phase 5.1 inputs without cloning or mutating active Profile storage before
  `swapping`. Cleanup closes acquisition handles and reopens the fixed path
  through the normal provider without capture hooks or Cookie injection.
- Restart tests must prove a successfully initialized Cookie Profile remains
  usable after browser and monitor restart and is the Profile reused by manual
  and scheduled crawler runs.
- Internal profile-only tests must prove missing/expired/unverified Profile,
  child login-state failure, CDP/provider mismatch, generic Profile fallback,
  default network, empty/stale Cookie, and unexpected QR all fail before crawl
  with typed `requires_relogin` behavior for migrated `login_type=cookie`
  accounts. Existing QR/Profile execution remains a separate regression path.
- Parent/child contract tests must prove `--lt cookie` plus hidden
  `--monitor_profile_only true`, no `--cookies`, no Cookie environment value,
  exact provider/account/promotion metadata, explicit/default Cookie clearing,
  and reserved exit code `42` mapping only for `ProfileLoginRequired`.
- C.3 cutover tests pause new runs, recover an interrupted migration, require
  zero runnable version-0 Cookie accounts before activation, route version 1
  through profile-only, and reject version 0 before child spawn with no argv
  fallback.
- C.1/C.2/C.3 tests must prove the browser-sync flag controls C.2 only: no
  acquisition browser/UI when off, advanced manual Cookie still works through C.1, accepted profile-only
  runs still use C.3, and raw argv is not restored.
- Flag-ownership tests instrument configuration reads/imports and prove only
  C.2 router/UI/readiness/managed-browser code reads
  `MONITOR_BROWSER_COOKIE_SYNC_ENABLED`; C.1 and
  C.3 import and execute successfully while it is false.
- Structured Cookie Protocol V1 tests must cover protocol version, request and
  session-generation correlation, platform domain allowlist, distinct name/domain/path/
  partition tuples, exact duplicates, malformed scope, unsupported required
  attributes, structured-to-Profile fidelity, and Packet B-fixed record/frame
  limits. Advanced manual strings must canonicalize into the shared validator
  without claiming unavailable attributes.
- A global tripwire must prove standard tests cannot reach real browsers, real
  platform accounts, or real Cookie material even
  when production-like environment variables are present.
- Process inspection must prove raw Cookie is absent from managed crawler child
  argv after the persistent-Profile transition. Command builders, diagnostics,
  logs, and failure output must not contain the raw value.
- Administrator Cookie reveal tests must prove the dedicated POST endpoint
  returns the exact selected-account Cookie only to administrators, returns
  HTTP 403 to normal users, applies `Cache-Control: no-store, private` and
  `Pragma: no-cache`, and leaves standard account responses masked. Frontend
  tests must prove default mask, eye reveal/hide, copy feedback, transient
  clearing, no normal-user entry, and no Cookie in localStorage,
  sessionStorage, IndexedDB, URL, logs, audit details, diagnostics, argv, or
  environment.

Packet B/D opt-in and real acceptance tests after their start gates pass:

- Chrome and Edge tests require `MONITOR_ALLOW_REAL_BROWSER_TESTS=1` and use
  synthetic Cookie fixtures. Each browser must prove exact managed-context
  binding, structured Cookie fidelity, Profile restart, two-Profile isolation,
  and temporary cleanup.
- Clean-Windows acceptance must prove the standard monitor installation uses
  the existing Playwright/CDP runtime; the operator performs no Extension/
  Connector placement, personal Chrome Profile setup, Google login, or Python
  3.12 installation.
- The same clean-computer matrix must prove direct acquisition under paths with
  spaces/Chinese characters and crawler-equivalent Profile restart without
  capture hooks.
- Route probes must prove `/api/monitor/cookie-bridge/` remains absent for HTTP
  and WebSocket in both feature states.
- Packet D requires explicit `DESIGNATED_DY_ACCOUNT_ID` and
  `DESIGNATED_XHS_ACCOUNT_ID`. For each account serially, acquire the real
  Cookie through the selected direct managed-context service from the project-managed Profile, verify exact
  platform/account identity, exercise administrator reveal/copy, inject only
  that Cookie into a fresh candidate with no predecessor LocalStorage/cache/
  Service Worker copy, restart and recheck identity, and persist at least one
  real content item through the normal monitor entry.
- Both required real platform runs must prove `fallback_used=false`, no
  anonymous/generic/other-account/default-network fallback, and no plaintext
  Cookie in child argv or environment. After acquisition-state cleanup and
  service restart, Profile checks and one bounded crawl per required platform
  must still pass. Kuaishou is Deferred and does not fail Packet D.
- Server-like regression must keep browser sync disabled by default
  and verify server-started QR login, manual SMS handling, Profile persistence,
  account checks, C.1 advanced manual Cookie, C.3 profile-only Cookie-account
  manual/scheduler runs, no raw argv, unchanged QR-account execution, and
  crawler execution.
- Headless direct-acquisition results are reported separately as supported or unsupported;
  they do not replace the server QR production acceptance boundary.

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
- With a complete real SMTP configuration in the active database but
  `real_email_delivery=false`, automatic report delivery is skipped with a
  customer-safe reason and report generation still succeeds.
- With `real_email_delivery=true`, production/pilot automatic delivery or a
  dedicated real-mail validation action can call the real mailer when SMTP
  configuration is complete.
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

- `scripts/review_orphan_email_evidence.py` can identify delivery logs
  whose `job_id` or `report_id` no longer resolves to active rows.
- The dry-run helper is no-op only: preview mode may inspect orphan evidence,
  but it must not delete, annotate, or rewrite delivery logs, report artifacts,
  or historical rows.
- The helper output includes `mode=dry_run`, `mutations_attempted=0`,
  classification, artifact existence, and the required database-backup,
  artifact/email-backup, explicit-approval, and rollback gates.
- `docs/SERVER_DEPLOYMENT.md` and `docs/deployment_runbook.md` describe the
  operator path for preserving unexpected-email evidence, backing up before
  mutation, obtaining approval, and recording rollback steps.
- Mutation helpers refuse to run without backup plus explicit operator
  approval, and the preview output must show the proposed terminal effect and
  rollback path before any write is allowed.
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
- Saving a new custom HTML template without `{report_html}` or `{report_body}`
  is rejected with a customer-safe validation message.
- Historical templates that already lack the placeholder remain readable, and
  preview/send rendering appends the generated report body instead of silently
  sending a wrapper-only email.
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

## CR-051 Task Center Consolidation Tests

- The formal console exposes one top-level `任务中心` navigation entry for the
  former run/report operational surface.
- The separate top-level Report Center section and `report_center` menu key do
  not render in the current console.
- Legacy `reports` shortcut calls normalize to Task Center's task-group view.
- Task Center opens on task/report grouping and keeps grouped report rows
  visible by monitoring task.
- Task Center has a `运行记录` subview that preserves run filters, pagination,
  stop, log, archive, restore, and Run Detail actions.
- The first-level task-group view prioritizes monitoring-task identity and
  result summary rather than displaying every run-record field.
- Run ID, task ID, run type, visibility, duration, and full failure reason
  remain available in the run-record subview or Run Detail.
- Report preview, report-scoped lead inspection, delivery history, resend, and
  downloads remain reachable from task-group row actions or the `更多` menu.
- CR-048/CR-049 scoped lead and delivery-history drawers remain secondary
  detail and do not become first-level global panels.
- After CR-069, report-scoped lead inspection is reached by switching into Run
  Detail's `AI 评估` tab with a report filter, not by opening a second lead
  table.

## CR-053 Task Center Field Priority And Select Alignment Tests

- Flat Task Center run rows begin with `任务 ID`, `运行 ID`, and compact
  `状态`.
- Grouped Task Center run rows hide duplicated `任务 ID` and begin with
  `运行 ID`, then compact `状态`, because task identity is already visible in
  the group header.
- Completed rows do not append long ingestion/progress text inside the status
  cell; active rows may show one short progress cue.
- Status badges in Task Center are compact and text-sized, not full-width bars.
- Task Center exposes only one page-level refresh button; the filter toolbar
  keeps `筛选` and `清空`.
- The main content container keeps native select/dropdown overlays aligned and
  unclipped across console pages.

## CR-054 Task Center Status Badge Compactness Regression Tests

- Task Center status badges must render normalized short lifecycle labels, not
  raw long `display_status` strings.
- Completed rows must stay `已完成` even when backend summary text contains
  ingestion detail.
- Active rows may show one short progress cue below the badge, but the badge
  itself must remain compact and text-sized.
- Browser inspection should confirm the first-level status cell does not read
  like a full-width progress bar.

## CR-055 Task Center Status Column Visual Refinement Tests

- Task Center table rendering adds a stable `col-status` class to `状态`
  headers and cells.
- First-level run status badges do not reuse the global `.status` pill class.
- Status badges render as narrow state-dot labels, with active progress limited
  to one short helper line below the badge.
- Flat mode keeps `任务 ID`, `运行 ID`, then status priority; grouped mode keeps
  duplicated task identity hidden and starts rows with run ID then status.
- Browser inspection at desktop, tablet, and mobile widths confirms the status
  column does not dominate the first-level table or hide the `详情` action.

## CR-056 Filter Dropdown Alignment Regression Tests

- Filter-region selects are enhanced only inside `.page-filter-region`; ordinary
  form/configuration selects remain native.
- The visible filter dropdown menu uses fixed positioning and is appended
  outside table or drawer scroll containers.
- Selecting an option updates the original select value and dispatches the same
  `change` event that existing filters use.
- Programmatic value updates such as `clearRunFilters()` or normal-user
  visibility enforcement update the visible filter button text.
- Browser inspection at `1440x900` confirms Task Center filter dropdowns align
  with their trigger control and stay within the viewport.
- Browser inspection at `1440x900` confirms at least one non-Task-Center page
  filter dropdown follows the same alignment behavior.

## CR-057 Task Center Group Summary Metric Chip Tests

- Grouped Task Center headers render aggregate run values as compact labeled
  metric chips rather than a long slash-separated summary sentence.
- Metric chips preserve run count, collected count, new count, suspected
  negative, high risk, manual-review, and unevaluated values.
- Non-zero risk/review/unevaluated chips use restrained warning or danger
  emphasis; zero values remain visually quiet.
- Limited-context, deleted-task, and historical-context explanations remain as
  short notes and do not replace the metric chips.
- Browser inspection at `1440x900` confirms grouped headers remain readable and
  do not collide with the table or CR-056 filter dropdown menus.

## CR-058 Filter Date Picker Alignment Regression Tests

- Filter-region date inputs are enhanced only inside `.page-filter-region`;
  ordinary form/configuration date inputs remain native.
- The visible date picker menu uses fixed positioning and is appended outside
  table or drawer scroll containers.
- Selecting a date updates the original date input value and dispatches the
  same `change` event that existing filters use.
- Clearing a date resets both the original date input value and visible filter
  date label.
- Programmatic value updates such as `clearRunFilters()` update the visible
  date button text.
- Browser inspection at the desktop review viewport confirms Task Center date
  picker menus align with their trigger control and stay within the viewport.
- Browser inspection must cover both left-side and right-side date filters:
  current date menus should match the clicked trigger width when usable, show a
  top anchor marker aligned to the clicked trigger center, and use viewport
  clamping only as the final overflow fallback.
- Browser inspection and CSS regression coverage must confirm the calendar
  grid does not clip weekday labels or two-digit day numbers; date cells should
  not horizontally overflow their grid cells at desktop, tablet, or mobile
  widths.

## CR-066 Filter Date Picker Trigger-Attached Dropdown Alignment Regression Tests

- Filter-region date inputs are enhanced only inside `.page-filter-region`;
  ordinary form/configuration date inputs remain native.
- The visible date picker menu uses fixed positioning and is appended outside
  table or drawer scroll containers.
- Selecting a date updates the original date input value and dispatches the
  same `change` event that existing filters use.
- Clearing a date resets both the original date input value and visible filter
  date label.
- Programmatic value updates such as `clearRunFilters()` update the visible
  date button text.
- Browser inspection at the desktop review viewport confirms Task Center date
  picker menus read like normal attached dropdowns.
- Browser inspection must cover both left-side and right-side date filters:
  date menus should use a readable compact calendar width, keep the top anchor
  marker aligned to the clicked trigger center, open from the clicked trigger's
  left edge when space allows, and shrink before clamping only when the
  readable width would overflow the visual viewport.
- Browser inspection and CSS regression coverage must confirm the calendar
  grid does not clip weekday labels or two-digit day numbers; date cells should
  not horizontally overflow their grid cells at desktop, tablet, or mobile
  widths.

## CR-067 Filter Date Picker Trigger-Width Visual Attachment Regression Tests

- Filter-region date inputs are enhanced only inside `.page-filter-region`;
  ordinary form/configuration date inputs remain native.
- The CR-067 historical visible date picker menu used fixed positioning and
  matched the clicked trigger width; this is superseded by CR-068's local
  attached menu rule.
- Selecting a date updates the original date input value and dispatches the
  same `change` event that existing filters use.
- Clearing a date resets both the original date input value and visible filter
  date label.
- Programmatic value updates such as `clearRunFilters()` update the visible
  date button text.
- Browser inspection at the desktop review viewport confirms Task Center date
  picker menus match the clicked trigger width when the trigger is wide enough,
  align the menu left edge to the trigger left edge, and keep the top anchor
  marker aligned to the trigger center.
- Browser inspection must cover both left-side and right-side date filters:
  the right-side `结束日期` menu must not extend beyond the trigger width at the
  desktop review viewport unless a much narrower trigger requires the minimum
  readable width fallback.
- Browser inspection and CSS regression coverage must confirm the calendar
  grid does not clip weekday labels or two-digit day numbers; date cells should
  not horizontally overflow their grid cells at desktop, tablet, or mobile
  widths.

## CR-068 Filter Date Picker Local Attached Menu Regression Tests

- Filter-region date inputs are enhanced only inside `.page-filter-region`;
  ordinary form/configuration date inputs remain native.
- The active date menu is mounted inside the clicked `.filter-date-enhanced`
  wrapper while open.
- The menu uses wrapper-local `position: absolute`, `left: 0`, and
  `top: calc(100% + 4px)` rather than document-body fixed-position viewport
  coordinates.
- Selecting a date updates the original date input value and dispatches the
  same `change` event that existing filters use.
- Clearing a date resets both the original date input value and visible filter
  date label.
- Programmatic value updates such as `clearRunFilters()` update the visible
  date button text.
- Browser inspection at the desktop review viewport confirms both `开始日期`
  and `结束日期` menus are children of their clicked wrapper, align to the
  wrapper left edge, keep a stable small top gap below the field, and match
  the clicked trigger width within browser sub-pixel tolerance.
- Browser inspection and CSS regression coverage must confirm the calendar
  grid does not clip weekday labels or two-digit day numbers; date cells should
  not horizontally overflow their grid cells at desktop, tablet, or mobile
  widths.

## Formal Console Full-Coverage Positive UI Optimization Tests

- All formal logged-in pages remain reachable: dashboard, monitoring tasks,
  platform accounts, proxies, AI access, AI evaluation rules, mail
  configuration, mail templates, runtime strategy, Task Center, and system
  diagnostics.
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
- If the crawler subprocess disappears mid-step or stops emitting output, the
  last safe provisional snapshot is preserved and the run still finalizes
  cleanly instead of hanging on live progress.

### Phase 19C AI Evaluation Progress Tests

- AI evaluation progress records evaluated count and total candidate count
  during long evaluation batches.
- Suspected negative, high-risk, and manual-review counts update in batches or
  time intervals while AI evaluation is active.
- AI provider failure still marks content for manual review and does not block
  report generation.
- Final AI counts remain exact after the full evaluation loop completes.
- Late or repeated progress updates do not regress final AI counts or reopen a
  terminal run.

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

Phase 20B-E is implemented and verified. Keep the following tests as the
regression gate for future changes to AI trace persistence, run-detail APIs,
run-detail frontend, and report-to-run backlinks.

### Phase 20A Confirmation And Data Model Tests

- Confirmed permission rules distinguish normal-user business-safe evaluation
  detail from administrator debug detail.
- Confirmed retention is implemented as an administrator-configurable runtime
  setting with a 30-day default before trace snapshots are stored.
- Confirmed default size limits are enforced before trace snapshots are stored:
  each trace is about 64KB, prompt snapshot up to 16KB, request snapshot up to
  24KB, response snapshot up to 24KB, and sampled comments up to 20 comments
  with per-comment truncation.
- The accepted schema creates `ai_evaluation_traces` and keeps old
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
- Truncated prompt, request, response, or sampled-comment snapshots include a
  `truncated=true` marker or equivalent trace metadata.
- Oversized trace snapshots do not block AI evaluation, report generation, or
  terminal run finalization.
- Trace write failures or retention cleanup must not mutate `ai_evaluations`,
  report rows, or delivery logs; only trace rows and redacted diagnostics may
  change.
- `ai_trace_retention_days` is visible in administrator runtime settings and
  follows the same database override and environment-lock behavior as other
  runtime retention settings once implemented.

### Phase 20C Run Detail API Tests

- Run detail API returns lifecycle summary, crawler logs, content list, AI
  evaluation list, and report/email links for the selected `run_id`.
- AI evaluation list supports pagination and filters for status, risk,
  platform, keyword, and content title.
- Per-evaluation detail API returns input/output trace fields according to the
  caller's role and owner/workspace scope.
- Normal users cannot read other users' run details or administrator-only debug
  fields.
- Normal-user evaluation detail responses include only business-safe summaries
  and do not include full prompt snapshots, request payload snapshots, or
  administrator debug metadata.
- Normal-user evaluation detail responses do not include raw model response
  fields.
- Administrator evaluation detail responses may include redacted raw model
  response fields, but never unredacted raw responses, API keys, authorization
  headers, cookies, proxy credentials, profile paths, or server-local paths.
- Collection logs and trace text redact Windows paths with spaces, Unix
  absolute paths, residual path fragments, and implementation field names such
  as `profile_path`.

### Phase 20D Run Detail Frontend Tests

- Run Center row has a clear "details" entry for the selected run.
- Run Detail is the primary operational entry for run-scoped leads and AI
  evaluation records, including records that exist before a report is
  generated.
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
  from report preview when the report artifact needs a shortcut.
- After CR-069, the report "view leads" action switches to Run Detail's
  `AI 评估` tab and applies the selected `report_id` filter instead of opening
  a standalone lead drawer.
- Run Detail `AI 评估` supports report, status, risk, platform, keyword, and
  title filters while preserving pagination and role scope.
- The visible AI Evaluation scope distinguishes all-run candidates from a
  selected-report filter.
- The `报告范围` control is selectable only when the selected run has multiple
  reports; zero-report and single-report runs show a read-only scope note.
- Run Detail AI Evaluation dropdown filters use the same page-filter enhanced
  dropdown behavior as Task Center first-level filters.
- Default Task Center report grouping does not present an unlabeled flat lead table
  that could be mistaken for all leads.
- Default Task Center loading fails validation if an unlabeled lead table is
  rendered outside Run Detail's AI Evaluation scope.
- Lead-state filtering belongs inside Run Detail `AI 评估`; the first-level
  Task Center toolbar must not become a global lead workbench filter surface.
- Empty states distinguish no AI candidates from no matches for the current AI
  Evaluation filters.
- Task Center's task-group view remains focused on final report artifacts,
  downloads, email delivery history, and report-scoped leads.

## CR-069 Run Detail AI Evaluation Lead Entry Consolidation Tests

- Run Detail API accepts `report_id` with existing AI filters and rejects a
  report outside the selected run or actor scope.
- Report `查看线索` in Run Detail's `报告` section switches to `AI 评估` with
  the report filter applied.
- Run Detail `AI 评估` shows report scope as a dropdown only for multi-report
  runs and as a read-only scope note for zero-report or single-report runs.
- The current UI does not render a separate report-lead drawer/table or legacy
  report-lead filter controls.
- `AI 评估` keeps per-evaluation details, limited-context labels, and
  sensitive-field redaction unchanged for administrator and normal-user roles.

## CR-071 Drawer And Modal Select Dropdown Consistency Tests

- Monitoring task edit drawer select fields for schedule, advanced collection,
  account binding, proxy binding, AI access, and email template opt into the
  existing `.page-filter-region select` enhancement.
- Platform account detail drawer select fields for platform, account status,
  and proxy binding opt into the same enhancement while preserving locked
  platform disabled state for existing accounts.
- Proxy edit drawer, AI Access edit drawer, AI Evaluation Rule edit modal,
  Mail Configuration edit drawer, and Mail Template edit drawer select fields
  opt into the same `.filter-select-*` classes and menu behavior.
- AI Access `模型名称` remains the existing free-text/model-list combobox and
  is not converted into a filter dropdown.
- Task edit drawer custom start/end date fields remain native form date inputs
  and are not accidentally converted by the select consistency work.
- Dynamic option refreshes for account, proxy, AI profile, email template, and
  platform login choices update the visible enhanced button labels and disabled
  state.
- Drawer/modal opt-in regions do not inherit the heavy page-filter toolbar
  panel background or border.
- Selecting a drawer/modal dropdown option keeps the original select value and
  dispatches the same `change` behavior as the native select.
- Browser checks should open representative surfaces at desktop, tablet, and
  mobile widths and confirm dropdown menus stay aligned, visible, and usable:
  Monitoring task edit, Platform Account detail, Proxy edit, AI Access edit,
  AI Rule edit, Mail Configuration edit, and Mail Template edit.

## CR-072 Task Edit Custom Date Picker Consistency Tests

- Monitoring task edit drawer `custom_start` and `custom_end` opt into the
  existing `.page-filter-region input[type="date"]` enhancement.
- Both custom date fields render with `.filter-date-enhanced` wrappers and
  `.filter-select-button.filter-date-button` triggers.
- Clicking each trigger opens the existing `.filter-date-menu` locally attached
  below the clicked trigger, with width matching the trigger.
- The date menu includes month title, previous/next month buttons, weekday row,
  date grid, `今天`, and `清空`.
- Selecting a day, selecting `今天`, or clearing updates the underlying
  original input value and dispatches the existing `change` behavior.
- Opening an existing task with saved `custom_start` / `custom_end` values
  synchronizes the visible date-button labels.
- Resetting or sample-filling the task form synchronizes the visible
  date-button labels back to placeholders.
- CR-071 preserved exclusions remain intact: AI Access `模型名称` keeps its
  combobox and selected drawer/modal selects keep the enhanced select menu.
- Ordinary edit/configuration date fields outside explicit opt-in scopes remain
  native unless separately accepted.

## CR-073 Scrollable Drawer Corner Radius Regression Tests

- Shared `.drawer` surfaces keep top-right `border-radius` on the outer shell
  and use `overflow: hidden` so browser scrollbar chrome cannot paint into the
  rounded corner.
- Content after `.drawer-head` / `.modal-head` is normalized into
  `.drawer-scroll-body`, which owns vertical scrolling and begins below the
  header area.
- Scrollbar thumbs remain rounded inside `.drawer-scroll-body` and read as a
  content scrollbar, not a full-height outer-frame rail.
- The close button remains in the top-right header position and is not moved
  inward or toward the center as a workaround.
- Sticky header, backdrop close, Escape close, enhanced drawer/modal selects,
  and task edit custom date picker behavior remain unchanged.
- Browser checks should open a long Monitoring task drawer and at least one
  run/detail or report-style drawer and confirm the visible scrollbar begins
  below the header, the rounded corner remains intact, and the close button is
  reachable.

## CR-081 Scrollable Drawer Fixed Footer Boundary Regression Tests

- Shared drawer normalization keeps `.drawer-scroll-body` as the only middle
  content scroll owner.
- Footer action groups are extracted from `.drawer-scroll-body` and attached as
  direct drawer children with `.drawer-fixed-footer`: `.form-actions`,
  `.resource-modal-actions`, `.account-flow-actions`, `.ai-test-actions`, and
  `.rule-modal-actions`.
- The old in-scroll sticky footer boundary using `top: calc(var(--drawer-padding-y) + 80px)`
  must not return.
- The visible scrollbar starts below the header and ends above the footer; it
  must not visually run through the top header or bottom action bar.
- Static tests cover task drawer, account drawer, proxy drawer, AI Access drawer,
  AI connection test modal, AI rule modal, Mail Configuration modal, mail test
  modal, and mail template drawer footer behavior.
- Browser checks should open representative long drawers/modals at `1440x900`,
  `1024x768`, and `390x844`, confirm save/close/test/clear buttons remain
  visible and clickable, and confirm backdrop/Escape close behavior is unchanged.

## CR-082 Drawer Scrollbar Header Footer Boundary Recheck Tests

- Every drawer/modal opener should route through `openDrawerChrome(...)` so
  shared normalization runs immediately before the overlay becomes active.
- Shared normalization should recheck already-normalized drawers, set
  `data-scroll-owner="drawer-content"` on `.drawer-scroll-body`, and toggle
  `has-fixed-footer` when a direct `.drawer-fixed-footer` exists.
- The outer `.drawer` should keep `overflow: hidden`, while only
  `.drawer-scroll-body` has vertical scrolling.
- Browser geometry checks should verify the header bottom equals scroll-body
  top and scroll-body bottom equals fixed-footer top, with zero visual gaps.
- Footer action buttons must not be descendants of `.drawer-scroll-body`.
- Representative checks should include Mail Configuration, Monitoring task
  drawer, Mail Template drawer, and at least one AI or proxy drawer across
  desktop/tablet/phone verification.
- Checks must confirm required footer actions remain visible and usable, no
  document horizontal overflow is introduced, and close/backdrop/Escape
  behavior is unchanged.

## Phase 21I Mail Configuration Visual Refinement Tests

- Mail Configuration keeps one page-level action group with edit configuration,
  send test mail, Task Center shortcut, compact real-email switch, and the
  shared top-bar refresh; no duplicate page-local refresh button may return.
- The SMTP/defaults summary remains a status surface and must not repeat the
  primary edit/test actions or the removed large `SMTP 与发送默认值` panel.
- Summary cards show test status, sender identity, fallback default recipients,
  and subject template without one-character Chinese text columns at
  `1440x900`, `1024x768`, and `390x844`.
- The mail configuration drawer preserves SMTP host, port, encryption, sender,
  username, password, default recipients, subject template, save, cancel, close,
  and enhanced select behavior.
- The mail test drawer preserves the test console, start test, close action,
  explicit real-email prerequisite, SMTP-acceptance wording, and no-real-SMTP
  automated verification boundary.
- Mail configuration and mail test drawers must keep `.drawer-scroll-body` as
  the middle scroll owner, with footer actions outside the scroll body and
  visible scrollbars bounded between fixed header and fixed footer.
- Browser checks must confirm the page and both drawers open with no console
  errors, no document horizontal overflow, and no change to SMTP API, delivery,
  real-email switch, close/backdrop/Escape, Task Center, Run Detail,
  enhanced-select, date-picker, owner-scope, or report-scope behavior.

## CR-074 Console Refresh Action Deduplication Tests

- The authenticated console top bar exposes one current-page refresh icon with
  an accessible label and no visible Chinese refresh text.
- Overview, Platform Accounts, Proxy Resources, AI Access, AI Evaluation Rules,
  Mail Configuration, Mail Templates, Runtime Strategy, and Task Center do not
  render duplicate page-header refresh buttons that reload the same current
  page data.
- First-level filter toolbars do not repeat generic list refresh buttons when
  the top-bar current-page refresh already reloads the same list.
- Icon-only refresh buttons use the shared `#icon-refresh` SVG symbol and
  `.refresh-icon-button` styling.
- Clicking the top-bar current-page refresh disables that button, keeps the
  icon visible, applies the loading class, and spins the icon until
  `loadSectionData(activeTabId())` completes.
- Scoped refresh actions remain available for schedule-time recomputation,
  delivery-history refresh, email-template preview refresh, run-log refresh,
  and run-detail refresh, and they use the same icon-only loading treatment.
- System Diagnostics diagnostic actions remain explicit diagnostic actions and
  are not treated as redundant generic refresh buttons.
- Browser checks should cover at least Overview, Task Center, a resource page,
  Run Detail, run-log drawer, email-template drawer, and delivery-history
  drawer to confirm the icon is visible, spins on click, and does not create a
  second page-level refresh control.

## CR-087 Helper Tooltip Removal Regression Tests

- The formal console must not render the CR-086 helper-tooltip affordance:
  `.helper-tooltip`, `data-tooltip`, helper-specific CSS, and helper-specific
  JavaScript functions must be absent.
- Targeted explanatory helper copy removed during CR-086 must not return as
  visible `.small`, `.inline-help`, field-hint, page-header paragraph, table
  helper, or tooltip content.
- Operational state text must remain visible when it represents data, error,
  warning, loading, empty, status, count, login prompt, password state, or
  action feedback rather than explanatory helper copy.
- Static regression checks should prove Task Center, Run Detail six sections,
  `.drawer-scroll-body`, enhanced select/date controls, top-bar refresh, and
  representative save/test/close/filter actions are still present.
- Browser checks should verify representative pages at desktop, tablet, and
  mobile widths have no visible helper question marks, console errors,
  horizontal overflow, one-character Chinese text columns, or drawer
  scrollbar/header/footer regressions.

## CR-088 AI Rule Modal Residual Helper Text Removal Regression Tests

- The `AI 评估规则` modal must not render the always-visible `AI 状态`
  helper line.
- The modal must not render the legacy-prompt notice shown when old prompts
  are parsed.
- The empty result panel must start without the default explanatory hint; the
  result area should stay visually blank until a test runs.
- Rule configuration, sample inputs, `测试评估规则`, `恢复默认规则`,
  `保存规则`, and rendered test output remain reachable.
- Browser checks at desktop, tablet, and mobile widths should confirm the
  modal remains readable and the table/list layout does not re-expand because
  of the removed helper text.
- For the CR-090 follow-up, browser checks should also confirm the AI rule
  list no longer feels overwide at desktop, the basic-info card keeps
  `规则名称` as a full-width field, and the modal's sample/test split remains
  balanced while preserving the same actions and close behavior.

## CR-089 Mail Template Row Helper Text And Update-Time Compactness Regression Tests

- The mail template list must not render the `正文占位符已保留` helper sentence
  under the template name.
- The `更新时间` cell should use a compact, wrap-safe timestamp treatment so
  the table does not widen on long values.
- The template row must continue to expose add, refresh, view mail config,
  search/status filters, row edit, set current, delete, save, refresh
  preview, clear, close, and iframe preview actions.
- Browser checks at desktop, tablet, and mobile widths should confirm the
  mail template table remains readable and does not introduce horizontal
  overflow or one-character Chinese text columns.

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

Phase 21 is implemented, verified, merged, and closed for the formal `/monitor`
console through Phase 21A-P. These tests remain the regression gate for the
verified Phase 21 baseline. `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` records
the per-page preservation rules, allowed refinements, forbidden changes, and
acceptance standards. The current baseline is the Task Center / Run Detail
console, not the older separate Run Center and Report Center layout. New Phase
21 changes require a separate accepted follow-up CR rather than reopening these
historical workstreams.

### Phase 21 Planning Document Tests

- `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` exists.
- The plan identifies the formal frontend baseline files.
- The plan identifies the current behavior baseline: one top-level `任务中心`,
  default task/report grouping, `运行记录` subview, Run Detail six sections,
  enhanced drawer/modal selects, task edit date picker, `.drawer-scroll-body`,
  and shared top-bar refresh.
- The plan states that the static prototype is visual reference only.
- The plan lists hard boundaries: no backend API, database, permission,
  crawler, AI-provider, SMTP, scheduler, deployment, framework, or build-step
  changes.
- The plan explicitly forbids restoring separate top-level Run Center or
  Report Center pages during Phase 21.
- The plan states that Task Center, Run Detail, drawers, modals, row menus,
  enhanced selects, local date menus, close behavior, scroll containers, and
  routing logic are structure-frozen for Phase 21 unless a separate accepted CR
  changes them.
- The plan covers every existing formal page:
  login, dashboard, monitoring tasks, platform accounts, proxies, AI access,
  AI evaluation rules, mail configuration, mail templates, runtime strategy,
  Task Center, and system diagnostics.
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
  evaluation rules, mail configuration, mail templates, runtime strategy, Task
  Center, and system diagnostics.
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
- AI Evaluation Rules keep the list table compact and the modal fields
  proportional; the page should not feel overly wide from the rule name, last-
  test, update-time, or result columns.
- Mail Configuration preserves edit, test, refresh, delivery shortcut, masked
  password, save, cancel, and close.
- Mail Configuration keeps edit configuration, send test mail, refresh/status,
  delivery-status navigation, and compact real-email state in one page-level
  action bar without duplicating edit/test actions inside the SMTP/defaults
  summary.
- Mail Configuration DOM checks fail if the SMTP/defaults summary repeats the
  same edit/test labels that already exist in the page header.
- The real-email send state is visible as the single CR-043 switch, remains
  compact when off, and still requires explicit confirmation before enabling
  real SMTP.
- Mail Templates preserve list filters, edit, set current where available,
  delete, variables, HTML editor, iframe preview, save, refresh preview, clear,
  and close.
- Runtime Strategy preserves grouped tables, current value, input, range, apply
  scope, lock state, refresh, save, and diagnostics shortcut.
- Task Center preserves task-group filters, grouping, grouped metric chips,
  compact statuses, one top-bar page refresh, one first-level `详情` action,
  and the `运行记录` run-record subview.
- Task Center run records preserve all current run filters, pagination, stop,
  archive, restore, compact status, full failure/troubleshooting fields in the
  accepted subview, and Run Detail routing.
- Run Detail preserves the six sections `概览`, `采集日志`, `采集内容`,
  `AI 评估`, `报告`, and `邮件交付`.
- Report preview, report-scoped lead inspection, delivery history, resend,
  HTML/Excel/Markdown downloads, run logs, copy/download log actions, scoped
  refresh actions, and report/email evidence remain reachable from Run Detail
  or the accepted scoped secondary surfaces.
- Task Center lead detail tests fail if the page renders an unlabeled global
  lead table, omits the selected-report/selected-run scope label, exposes
  lead-state filters as first-level Task Center controls, or reintroduces a
  separate first-level report-lead drawer/table outside Run Detail.
- Overlay freeze tests fail if Run Detail tabs, task drawer sections, account/
  proxy/AI/mail/template drawer or modal categories, enhanced select/date
  controls, `.drawer-scroll-body`, close/backdrop/Escape behavior, or bottom
  action reachability changes as part of a visual polish batch.
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
- Task Center default grouping, `运行记录`, Run Detail, and scoped secondary
  surfaces remain reachable without restoring separate top-level Run Center or
  Report Center pages;
- dashboard closed-loop, shortcut, metric, and resource-health cards do not
  squeeze labels into one-character vertical columns, overlap content, or hide
  primary actions.

Tablet `1024x768`:

- navigation uses the persistent collapsed icon rail without the top-left
  mobile trigger; nested pages remain selectable and the final icon must not be
  overlapped by the bottom collapse button;
- the `sidebar-collapsed` rail must contract to the intended narrow icon-rail
  width rather than remaining visually close to the expanded fixed sidebar;
- the same `sidebar-collapsed` rail contract must hold for narrower in-app
  tablet panels around `809px`, including the final inline style cascade;
- page headers and toolbars wrap without hidden primary actions;
- drawers and modals fit inside viewport safe margins;
- floating menus remain reachable and unclipped;
- four-column or dense card groups wrap, stack, or switch to compact rows before
  text becomes unreadable.

Mobile `390x844`:

- Operations Home shows key status and next action before long guidance;
- navigation reaches all allowed core pages;
- the loaded header title remains horizontal and resource pages such as
  `代理资源` keep page width equal to document width, with dense tables scrolling
  only inside `.table-wrap`;
- task drawer, account dialog, run log drawer, and report preview drawer can
  scroll and close;
- report preview and delivery history remain readable;
- Task Center and Run Detail remain usable without horizontal overflow;
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
- Phase 21 does not restore the older separate Run Center / Report Center IA
  and does not change the current Task Center / Run Detail structure.
- Visual hierarchy is measurably clearer than the CR-033 baseline in browser
  screenshots or review notes.
- Operations Home reads as a daily operations cockpit rather than onboarding.
- Platform Accounts remains a complete account-maintenance workflow.
- Task Center remains usable under dense operational data, including grouped
  reports, `运行记录`, Run Detail, and secondary scoped drawers.
- Dashboard, run/report, resource, and overlay screenshots demonstrate layout
  resilience: readable text, stable card widths, reachable buttons, no text
  collapse, and no horizontal overflow at `1440x900`, `1024x768`, and
  `390x844`.
- All implementation verification is recorded in `docs/TEST_RESULTS.md` after
  code changes are actually made and tested.
