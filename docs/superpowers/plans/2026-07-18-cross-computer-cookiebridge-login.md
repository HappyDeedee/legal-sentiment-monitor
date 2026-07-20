# Cross-Computer Browser Login And CookieBridge Roadmap

> Accepted roadmap with Packet B `Verified`. Packet C.1 implementation gates
> have passed within the synthetic/local proof boundary; C.2/C.3 and Packet D
> remain dependency-gated. Execute only the packet whose start gate is open in
> current project documents.

**Goal:** Add an optional local-desktop browser login flow that opens a
project-managed Chrome or Edge Profile, acquires structured Cookies from the
exact managed browser context selected by Packet B, verifies the exact account,
and saves it without manual Cookie copying. Preserve QR login as the primary
server path and manual Cookie input as a collapsed advanced option.

**Baseline:** rebaselined on 2026-07-21 against clean
`main@2ea2c1e96675297e302368b1226ec7aac05f2bb1`. Phase 5.1P, Phase 5.1A-D,
and CR-114 through CR-121 are merged and verified within their recorded proof
boundaries. The separate CR-047 Linux/server-like real acceptance remains
operator-gated and is not relabeled by this local Windows roadmap.

The roadmap touches browser processes, Cookie material, account identity,
durable state, multi-account isolation, deployment, and shared login/runtime
contracts.

## 1. Roadmap Status

This file is a gated master roadmap, not one implementation batch. A roadmap
can be ready for approval while later packets remain blocked by declared
evidence gates. A packet is implementation-ready only when every prerequisite
listed for that packet is verified in current project documents.

The current authoritative order is:

1. Keep Packet A, the verified Phase 5.1P read-only preflight under CR-047, as
   the provider compatibility boundary.
2. Preserve the completed Phase 5.1A-D implementation and run the latest-main
   local provider/preflight unit that is achievable on this Windows host. This
   scoped gate proves the inherited local browser/Profile authority only; it
   does not close the separate CR-047 Linux/server-like real acceptance.
3. Execute CR-112 before CR-070. Packet B is disposable and synthetic; Packet C
   and D implement and accept the same-machine Windows capability while local
   browser auto-sync remains disabled in server production by default.
4. Keep Packet B as verified evidence for the selected direct managed-browser
   acquisition path.
5. Execute Packet C using that selected path.
6. Execute Packet D, including mandatory real Douyin and Xiaohongshu
   acceptance. Kuaishou is deferred.
7. Execute CR-070 against only committed CR-112 Profile/account state.

Packet documents:

- `docs/superpowers/plans/2026-07-19-phase-5.1p-browser-provider-preflight.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-pairing-compatibility-spike.md`
- `docs/superpowers/plans/2026-07-19-local-browser-auto-sync-login.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-deployment-acceptance.md`

## 2. Current Baseline Diff

| Label | Current evidence | Classification | Documentation action | Protected behavior | Readiness |
|---|---|---|---|---|---|
| Phase 5.1P | `docs/TASKS.md` and `docs/phase-5.1p-browser-entrypoint-map.md` record verified completion | Completed read-only preflight | Keep as Packet A evidence and provider boundary | No code, schema, Profile, Cookie, proxy, or runtime mutation | Complete |
| Phase 5.1A-D | Merged provider, identity, lifecycle, runtime binding, and regression fixes through CR-121 on current main | Historical/already completed | Keep closed; consume the provider contract | One account/browser/Profile/proxy authority and requested/effective snapshots | Ready dependency |
| Phase 5.1 server-like acceptance | Task 3 is operator-gated because this host has no Docker/Linux runtime, dedicated proxy probe, or acceptance fixtures | Operator-gated CR-047 work | Keep open and separate; do not claim local evidence closes it | Server production remains QR-first and no diagnostic fallback is production proof | Operator-only |
| CR-112 | Accepted decisions and the scoped Windows gate are verified; Packet B and C.1 implementation gates are complete within their recorded proof boundaries | Accepted / In Progress (Packet C.1) | Open C.2 only after the C.1 delivery gate is complete | Existing QR, manual Cookie, Profile, and permission behavior | C.1 complete |
| CookieBridge reference | Temporary snapshot measured: Chrome loading fails, Edge roundtrip is flat/unauthenticated, and distribution/runtime do not fit | Historical evaluation evidence | Keep outside product paths; retain the result matrix | No product dependency on rejected reference behavior | Closed by Packet B evidence |
| Current schema/API/UI | No Cookie-to-Profile promotion schema or managed-browser acquisition service; account APIs strip Cookie and manual UI never reveals it; runner still uses `--cookies` | Current baseline gap | Implement only in Packet C using the selected direct context path | Existing storage encryption and administrator account boundary | Dependency-gated |
| CR-070 / Phase 5.2 | Accepted export/import capability, not implemented | Deferred behind CR-112 by accepted decision | Preserve ownership and consume only committed CR-112 state later | No export of operation or connector secrets | Future-only |
| CR-092 to CR-094 | Independent future architecture lanes | Future-only | Keep separate | No hidden prerequisite or parallel account/provider system | Future-only |

Browser and login evidence on the current baseline:

- CR-117 selects one deployment browser using explicit executable, Chrome,
  Edge, supported Chromium, installed Playwright Chromium, then automatic
  Playwright Chromium installation, and persists the choice locally.
- CR-120 binds local visible login to the selected browser, account
  `profile_key`, and owned CDP process. CR-121 preserves exact prepared-page
  identity evidence for real crawls.
- `runner.py` passes decrypted saved Cookie material through `--cookies` for
  `login_type=cookie`. Phase 5.1P mapped that current baseline without
  changing it; Packet C owns the later confirmed migration to persistent
  Profile preparation and no raw Cookie in managed crawler child argv.
- The evaluated CookieBridge extension hardcodes `ws://localhost:8274/ws`,
  generates a `client_id`, and registers without an account/Profile pairing
  claim. Its server accepts clients by `client_id`, keeps connection state in
  memory, and can choose a client when no exact identifier is supplied. Packet
  B measured that current branded Chrome does not load it and that its Edge
  response loses structured Cookie scope.
- The evaluated CookieBridge license is non-commercial-learning-only and its
  server declares Python `>=3.12`; the project runtime uses Python 3.11.

## 3. Accepted Planning Decisions

These decisions define the accepted roadmap. `Accepted` approves direction;
`In Progress` and `Verified` remain packet-specific evidence states.

### 3.1 Login model and UI order

Keep the backend login types:

```text
qrcode
cookie
```

For `login_type=cookie`, add provenance rather than a third login type:

```text
cookie_source=browser_sync
cookie_source=manual
```

User-facing order:

1. QR login is the default.
2. Browser login and automatic synchronization is the normal Cookie workflow
   when the local feature is enabled and healthy.
3. Manual Cookie input remains visible inside a collapsed advanced section.

Browser-sync health failure is a state of the browser auto-sync workflow. It does
not automatically open or promote manual Cookie input, and it never switches
the selected account.

### 3.2 Identity and login-material authority

- Account identity authority: `social_account` plus `profile_key`.
- QR and accepted Cookie login both converge on the application-managed
  persistent Profile resolved from `profile_key`. That Profile is the normal
  browser session and crawl environment for both modes.
- An auto-sync- or manually supplied Cookie is bootstrap, refresh, recovery, and
  migration material. It is injected into an account-bound persistent Profile
  and validated there before activation, and the verified value is also
  retained through the encrypted account store.
- An existing active Profile uses the fixed-active-path, same-volume
  candidate/rollback journal from `ACCOUNT_ENVIRONMENT.md`; a failed candidate
  restores the previous Profile/Cookie or blocks as `recovery_required`
  without guessing.
- The direct browser-context acquisition service is an acquisition/refresh
  channel only. It has no durable Cookie cache and is never login authority.

Auto-sync- or manually sourced Cookies must pass the same platform account check
inside the candidate persistent Profile before they are encrypted and
activated. The requested account/Profile lock must still be held when
validation and persistence commit. Later crawler runs reuse the promoted
Profile without raw Cookie in child-process arguments.

### 3.3 Browser selection and ownership

Use one provider precedence after Phase 5.1 establishes the shared contract:

```text
valid explicit MONITOR_BROWSER_EXECUTABLE
-> Google Chrome
-> Microsoft Edge
-> system Chromium
-> bundled Playwright Chromium only for the declared server/container mode
```

Chrome is preferred when Chrome and Edge both exist. Auto-sync launches a
visible application-managed persistent Profile derived from `profile_key`.
It does not open the user's ordinary default Profile and does not require a
Google account or a manually created Chrome personal Profile.

An invalid explicit executable fails with a customer-safe diagnostic; a locked
account does not silently fall back to another browser, Profile, proxy, user
agent, or default network.

### 3.4 V1 placement and transport

V1 browser auto-sync is local-desktop and same-machine Windows only:

```text
monitor service + managed browser
on the same Windows computer
```

Packet B selected direct acquisition from the exact Playwright/CDP browser
context retained by the parent account operation. No Extension, WebSocket
Connector, listening Cookie endpoint, connected-client registry, pairing
token, or browser-Origin trust boundary is part of V1. The parent operation
already holds the exact `social_account_id`, `profile_key`, `login_session_id`,
account/Profile lock, and browser-context handle, so an empty or mismatched
binding fails before Cookie capture.

The rejected `/api/monitor/cookie-bridge/` path remains absent. A normal HTTP
probe returns 404 and the pinned Starlette/Uvicorn baseline rejects an
unmatched WebSocket upgrade with 403. Reverse proxies expose no Cookie-bridge
path because the product mounts none.

Remote browser-sync topology, browser-on-operator/monitor-on-server topology, and
cross-host Cookie transport are outside V1. They require a separate decision
covering TLS, endpoint authentication, origin policy, network access control,
secret rotation, and deployment ownership.

Server production acceptance remains the existing server-started QR workflow.
Local Chrome/Edge auto-sync is not production proof. Headless direct
acquisition may be observed in Packet D but does not gate the V1 local feature
and does not replace the QR production baseline.

### 3.5 Distribution and runtime

The source under `.codex_tmp` is evaluation evidence only. Packet B begins with
reuse-first, minimal-adaptation analysis and assigns one result to each
Extension, Connector, and protocol component:

1. `direct reuse` when behavior, distribution, runtime, and license fit;
2. `minimal adaptation` when a bounded adapter can satisfy the accepted
   pairing/security contract without broad ownership transfer; or
3. `single-component replacement` when direct reuse/adaptation cannot meet the
   contract or distribution boundary.

Packet B selected the existing managed Playwright/CDP context as the Extension
replacement, an in-process account-bound acquisition service as the Connector
replacement, and a minimally adapted internal structured Cookie Protocol V1.
The reference source remains outside product paths. Product computers require
no Extension installation, Extension store/developer-mode step, Connector
process, listening Cookie route, or Python 3.12 runtime. A project-wide Python
upgrade, separately managed Connector, and remote Cookie transport are outside
CR-112.

### 3.6 Existing subprocess Cookie exposure

The current `runner.py --cookies` contract places decrypted Cookie material in
child-process arguments. OS process listings and diagnostics may expose that
value even though storage is encrypted and product logs/UI redact Cookies.

The 2026-07-19 decision fixes the target: the monitor prepares and validates
the persistent Profile before crawler launch, and managed-account crawler
children receive no raw Cookie through argv. Packet C owns the migration,
compatibility, rollback, and regression work. It remains closed until that
implementation plan is approved, and process inspection must prove the raw
Cookie is absent before acceptance. The current contract remains baseline
evidence until then, not the target behavior.

### 3.7 Administrator Cookie reveal

The normal account list/detail remains masked. An authenticated administrator
may explicitly request the complete Cookie for one selected account through a
dedicated POST reveal endpoint. The response uses `Cache-Control: no-store,
private`, `Pragma: no-cache`, and no validator; normal users receive HTTP 403.
The frontend keeps the value in transient page memory only, masks it by
default, reveals it through an eye control, copies only after an explicit
click, shows copy feedback, and clears the transient value on account change,
drawer close, navigation, or timeout.

The Cookie itself never enters URL/query text, browser local/session/IndexedDB
storage, logs, audit details, diagnostics, screenshots, subprocess argv, or
subprocess environment. A redacted audit event may record that an
administrator invoked reveal/copy for an account, but it contains no response
body, Cookie fragment, scope, or hash. Copying intentionally places the value
on the operating-system clipboard at the administrator's request; the UI must
state success without echoing the value.

## 4. Managed Browser Binding And Multi-Account Contract

The rejected reference `client_id` is not account identity. V1 routes no
connected clients: the monitor retains the exact browser-context handle created
inside one locked account operation and never selects the first, newest, or
only browser/Profile implicitly.

### 4.1 Acquisition binding

1. The authenticated monitor API reuses `create_draft_social_account` so a real
   account ID and `profile_key` exist before browser launch. It creates one
   browser-sync login session while holding the account/Profile lock.
2. The session records `login_session_id`, `social_account_id`, `profile_key`,
   platform, initiating actor, promotion ID, provider resolution ID, and
   browser attempt ID before creating a fresh managed candidate context.
3. The acquisition service receives the live context handle from the same
   operation. It does not accept a browser path, Profile path, client ID, or
   account ID supplied by the browser or frontend.
4. After user login, the service reads structured Cookie records directly from
   that exact context, validates the binding and operation generation again,
   and closes the context before candidate validation/promotion.
5. Existing active Profiles and their Cookie material remain untouched until
   the fixed-path promotion journal reaches `swapping`. No active Profile,
   browser storage, cache, or Service Worker is cloned into the fresh candidate.

There is no pairing token, Extension credential, client registry, WebSocket
cache, manifest identity, or ephemeral Extension directory. Opaque operation
IDs and safe status categories may be exposed; Cookie values and raw Profile
paths remain excluded from API status, logs, diagnostics, tests, and evidence.

### 4.2 Reconnect and revocation

- A browser or service restart closes the in-memory acquisition handle. It does
  not change committed account/Profile or verified Cookie state.
- A retry creates a new session generation under the same account/Profile lock;
  it cannot reuse a stale context handle or late result.
- Account reset, Profile reset, account deletion, or promotion rollback
  invalidates the session generation and rejects later acquisition results.
- One managed Profile binds to one social account. A context handle already
  associated with another account/session is rejected.

### 4.3 Cookie request

Each acquisition contains an operation-generated request ID, exact account,
Profile, session generation, platform, protocol version, and expiry. The
service accepts a result only from the retained context handle with the same
operation and generation. Duplicate, late, stale, malformed, or cross-account
results are discarded and audited without Cookie values.

The internal structured Cookie Protocol V1 defined in
`ACCOUNT_ENVIRONMENT.md` preserves domain/path/security attributes and
distinct tuples; it is never flattened to a Cookie-header string. Unrelated
domains, malformed scope, exact duplicate tuples, unsupported required
attributes, unsupported protocol versions, and over-limit payloads fail closed.
Advanced manual strings are canonicalized by C.1 into the same internal record
model before Profile injection.

There is no browser-facing Cookie-read endpoint. The administrator reveal
endpoint is the only explicit API that returns decrypted Cookie material, and
it is bound to one selected `social_account` through the existing authorization
boundary.

## 5. Browser-Sync And Profile-Promotion State Machines

Browser-sync states:

```text
created
-> preparing_profile
-> browser_starting
-> waiting_user_login
-> capturing_cookie
-> validating_candidate
-> candidate_ready
-> promoting_profile
-> validating_active
-> committing
-> succeeded
```

Terminal non-success session states:

```text
failed | timed_out | cancelled | browser_closed | browser_unavailable |
requires_relogin | recovery_required
```

The durable Profile operation has its own journal:

```text
preparing -> candidate_ready -> swapping -> active_recheck -> committed
                                      \-> rolling_back -> rolled_back
terminal failure: failed | recovery_required
```

The fixed active path remains derived only from `profile_key`. Candidate and
rollback directories are same-volume operation artifacts that the provider and
crawler never resolve. Every candidate is fresh from the locked Phase 5.1
provider inputs rather than a clone of the active Profile. The exact
swap/recovery matrix lives in `ACCOUNT_ENVIRONMENT.md` and is a required
Packet C contract.

Each same-volume rename completes before its following checkpoint write. The
checkpoint may therefore lag one rename; it is not competing authority. The
single account/Cookie/Profile plus `committed` database transaction decides old
versus new authority, while recovery uses the operation marker and exact
directory-shape table in `ACCOUNT_ENVIRONMENT.md` to perform that decision.

Every transition validates the account/Profile lock, session generation, and
promotion ID. Each non-terminal state has a deadline and restart rule.
Cancellation before `swapping` removes the closed candidate; cancellation at
or after `swapping` waits for safe commit or rollback before the session becomes
terminal. A service restart reconciles non-terminal promotion journals before
the affected account can be checked, reset, exported, logged in, or crawled.

One centralized, idempotent finalizer cancels polling, rejects late messages,
closes browser/Profile handles, releases locks, discards stale context handles,
and invokes journal recovery/cleanup. It never deletes the fixed active
Profile or the only rollback copy. Repeated finalization is a no-op.
Committed rollback cleanup is triggered by the first successful managed run,
by startup/periodic `cleanup_after` scanning, and before a new promotion. A
failed cleanup retains one artifact, blocks refresh, and alerts for operator
remediation rather than accumulating copies.

The database commit is atomic only for verified Cookie ciphertext, source,
identity snapshot, profile-ready metadata, account status, audit
linkage, and journal state. Filesystem promotion occurs before that transaction
and is made recoverable by the journal; documentation and code must not describe
the database and Profile directory as one atomic transaction.

Before `active_recheck`, all acquisition browser handles are closed. The fixed
active path is reopened through the normal provider without capture hooks or
Cookie injection so the check proves crawler-equivalent reuse.

Managed `login_type=cookie` runtime after C.3 uses an internal `profile_only`
contract, not a new customer login type. Missing/expired/unverified Profile,
child-side login check failure, CDP/provider mismatch, standard/generic Profile
fallback, empty Cookie injection, default-network fallback, and unexpected QR
opening all fail before crawl. No raw Cookie is passed through child argv or
environment. Existing QR/Profile child execution remains regression-protected
and is not silently reclassified by CR-112 V1.

The exact parent-child contract keeps `--lt cookie`, adds hidden
`--monitor_profile_only true`, omits `--cookies`, and supplies the provider
Profile/browser/proxy plus account/promotion/version metadata through the
internal environment. The child rejects explicit/default Cookie material,
checks login before any login-class construction, and maps only internal
`ProfileLoginRequired` to exit code `42`. C.3 pauses new runs, migrates or marks
every Cookie account, activates only with zero runnable version-0 accounts, and
thereafter rejects version 0 before child spawn.

## 6. Feature Flags And Defaults

```text
MONITOR_BROWSER_COOKIE_SYNC_ENABLED=false
MONITOR_ALLOW_REAL_BROWSER_TESTS=0
```

- Default-off means no C.2 browser acquisition session, schema-dependent API,
  capability, or UI auto-sync action is activated.
- `MONITOR_BROWSER_COOKIE_SYNC_ENABLED` controls only Packet C.2 acquisition,
  APIs, and UI. It does not disable C.1 advanced-manual
  Cookie-to-Profile service or C.3 profile-only runner behavior after those
  sub-packets are accepted.
- Only C.2 router inclusion, UI/capability/readiness, and managed-browser
  acquisition launch may read that flag. C.1 validation/promotion/recovery/manual Cookie
  and C.3 command/child/platform guards import and execute independently when
  it is false.
- The rejected Cookie-bridge WebSocket route remains unmounted in both feature
  states: a normal HTTP probe returns 404, while the pinned Starlette/Uvicorn
  baseline rejects an unmatched WebSocket upgrade with 403 before acceptance.
- Baseline evidence is FastAPI `0.110.2` and Uvicorn `0.29.0` from exact
  `pyproject.toml` pins plus Starlette `0.37.2` from `uv.lock`. Status codes are
  regression evidence; route absence and zero WebSocket protocol state are
  mandatory across reviewed dependency upgrades.
- Unit/integration tests use a fake acquisition service and temporary Profiles.
- Real Chrome/Edge and platform login tests require
  `MONITOR_ALLOW_REAL_BROWSER_TESTS=1` and remain separate from standard pytest.
- Missing/invalid browser, locked Profile, stale session generation, or closed
  context produces an explicit unavailable state; no default account, browser,
  Profile, Cookie, or network fallback is permitted.

## 7. Packet Gates

### Packet A: Phase 5.1P preflight

This packet is complete. It is read-only, produced
`docs/phase-5.1p-browser-entrypoint-map.md`, and made no CookieBridge
implementation decision.

**Exit:** all existing login/crawl/CDP entrypoints and requested/effective
provider fields are mapped without runtime mutation.

### Existing Phase 5.1A-D and scoped local gate

Phase 5.1A-D and their merged follow-up regressions are complete. Before
Packet B, rerun the currently achievable latest-main local provider/preflight
unit and record its proof boundary. The still-open Linux/server-like real
acceptance remains owned by CR-047 and is not presented as passed.

**Exit:** the local unit confirms one selected browser/Profile/provider
authority on this Windows host without mutating real account material. The
result explicitly says it is not CR-047 server production acceptance.

**2026-07-21 evidence:** `docker compose config --quiet` passed; the shared
one-click browser preflight resolved the persisted `chrome.exe`; isolated
`scripts/server_like_validation.py` passed all 12 checks including restart and
temporary-data cleanup; and the focused Phase 5.1/CR-116-121 regression passed
`234` tests. No real account, Cookie, Profile, proxy, or platform action ran.

### Packet B: compatibility and acquisition spike

Starts after CR-112 acceptance, the latest-main scoped local gate, and the
accepted CR-112-before-CR-070 sequencing decision. It may inspect the temporary
reference and run disposable black-box tests. It does not change
product schema, APIs, UI, Profiles, or deployment.

**Exit:** the component matrix records `direct reuse`, `minimal adaptation`, or
`single-component replacement` with evidence for Extension, Connector, and
protocol. Chrome and Edge prove the selected direct managed-context
acquisition, structured Cookie fidelity, restart, two-Profile isolation, and
temporary cleanup. The rejected WebSocket route remains absent with pinned
HTTP 404/WebSocket 403 evidence.

### Packet C: local browser auto-sync implementation

Starts only after Packet B passes, distribution/runtime decisions are accepted,
the persistent-Profile/no-raw-argv migration plan is approved, and a data-model
migration plan is approved.

Packet C is serial:

1. **C.1 Profile service:** shared auto-sync/manual canonicalization, candidate
   validation, promotion journal, fixed-path swap, restart recovery, cleanup,
   and account migration. No browser auto-sync API/UI is enabled.
2. **C.2 Browser acquisition:** direct exact-context capture, APIs, and UI,
   controlled only by `MONITOR_BROWSER_COOKIE_SYNC_ENABLED`.
3. **C.3 Profile-only runner:** migrate/mark every `login_type=cookie` account,
   add the
   explicit internal profile-only child contract, prohibit generic/QR/default
   fallback, prove no raw Cookie argv/env, and retire managed `--cookies` use.

**Exit:** C.1-C.3 pass in order; local Chrome and Edge workflows validate and
persist exact-account Cookies with no manual copy/paste or cross-account
fallback; advanced manual Cookie still works when browser sync is disabled; and
managed crawler children use the fixed verified Profile with no raw Cookie.

### Packet D: deployment and acceptance

Starts after Packet C targeted and integration tests pass.

**Exit:** clean Windows computer setup, browser matrix, failure/restart matrix,
rollback, and server QR non-regression are verified. Designated Douyin and
Xiaohongshu accounts each persist at least one real content item through the
normal monitor path with `fallback_used=false`; Kuaishou is deferred. Headless
direct acquisition remains a separate observation and does not weaken the
server-first boundary.

## 8. Verification Matrix

| Environment | Acquisition service | Browser | Real platform | Allowed by default | Required proof |
|---|---|---|---|---|---|
| Standard pytest | Fake exact-context adapter | Fake/temp Profile | No | Yes | State machine, generation binding, stale-result rejection, isolation, cleanup |
| Local diagnostics | Direct managed context | Installed browser | No | Yes | Provider resolution and synthetic structured acquisition |
| Opt-in browser smoke | Direct managed context | Chrome and Edge | No | Explicit opt-in | Exact context + structured fidelity + restart + isolation |
| Local pilot | Direct managed context | Managed visible browser | Yes | Operator opt-in and designated account ID | Exact account validation, encrypted Cookie persistence, Profile restart reuse, and no raw Cookie argv |
| Server-like regression | Disabled | Bundled/headless QR browser | Platform as existing plan permits | Existing gates | QR flow and crawl non-regression |
| Production | Disabled for V1 | Server-started browser | Yes | Existing server policy | QR login remains primary acceptance path |

Required negative tests include:

- stale/replayed acquisition request or session generation;
- context handle associated with the wrong account/Profile/session;
- implicit browser/Profile discovery or selection after the exact context is
  missing or closed;
- feature-disabled normal HTTP probe not returning 404, or unmatched WebSocket
  upgrade not returning the packaged-runtime pre-accept rejection (403 on the
  pinned Starlette/Uvicorn baseline);
- wrong Profile/session generation or stale acquisition result;
- simultaneous Account A and B login and crawl;
- stale response after timeout/cancellation;
- browser close at every non-terminal state;
- service/browser restart before and after persistence;
- Profile reset invalidating the prior session generation;
- malformed or wrong-platform Cookie response;
- failed platform verification preserving prior Cookie;
- crash/kill at every Profile promotion checkpoint restoring the previous
  active Profile or producing deterministic `recovery_required` evidence;
- disk-full, open-handle, antivirus/permission, and same-volume rename failure
  before account activation;
- missing/expired Profile in profile-only mode failing without QR, empty
  Cookie, generic Profile, or default-network fallback;
- browser sync disabled while advanced manual Cookie and profile-only runs remain
  usable and raw argv remains retired;
- structured Cookie duplicate/scope/domain/attribute/version/size rejection;
- locked account with browser/proxy/default-network fallback attempt;
- standard tests with production-like environment variables still blocked from
  real browser and real platform access;
- process inspection proving raw Cookie is absent from managed crawler child
  argv after persistent-Profile preparation.

## 9. Accident Invariants

Must never happen:

- raw Cookie appears in logs/UI/test artifacts outside the explicit transient
  administrator reveal response and clipboard action;
- raw Cookie process-argument exposure is hidden, mislabeled as end-to-end
  isolation, or retained after Packet C acceptance;
- a failed Cookie refresh damages the previously active Profile or replaces
  the previous verified encrypted Cookie;
- a candidate inherits active Profile storage or mutates the active Profile
  before `swapping`;
- database and fixed active Profile disagree without deterministic journal
  recovery, or two operation directories become runtime authorities;
- browser-sync disablement breaks advanced manual Cookie or restores raw Cookie
  argv;
- a Cookie-bridge HTTP/WebSocket route becomes reachable;
- an account uses a first/newest/only browser/Profile by convenience;
- a late response overwrites a newer session or verified Cookie;
- browser-sync failure changes QR behavior or silently opens manual Cookie input;
- a locked Profile falls back to another browser, Profile, proxy, or network;
- restricted third-party code is bundled into the product;
- a local-browser result is reported as server production acceptance.

Must eventually happen:

- every browser-sync session reaches one terminal state;
- every candidate Profile is promoted, rolled back, quarantined for
  `recovery_required`, or deleted; cleanup is attempted by the documented
  deadlines, retains at most one artifact on failure, and emits an operator
  alert instead of accumulating copies;
- browser handles, polling tasks, locks, and acquisition state are
  finalized idempotently;
- service restart reports an interrupted acquisition without changing account
  validity and reconciles any non-terminal promotion journal;
- account/Profile reset invalidates stale session results;
- every promotion commits one verified candidate or restores the predecessor.

## 10. Documentation And Traceability

CR-112 is registered in `CHANGE_REQUESTS.md` as an `Accepted /
Dependency-Gated` new capability and linked to `TASKS.md`, `TRACEABILITY.md`,
and `TEST_PLAN.md`. Same-machine Windows scope, reuse-first/minimal-adaptation
evaluation, CR-112-before-CR-070 sequencing, Profile authority, administrator
Cookie reveal, and the Douyin/Xiaohongshu real-acceptance matrix are confirmed.
Do not call a packet `In Progress` before its start gate or `Verified` before
its packet evidence passes.

Each packet updates `CURRENT_STATE.md`, `TASKS.md`, `TEST_RESULTS.md`, and
`TRACEABILITY.md` only for evidence actually produced. Phase 5.1 historical
ownership remains under CR-047; CR-112 references it as a dependency and does
not reopen or duplicate it.

The five plan files and all CR-112 formal references are one atomic
documentation-delivery unit. They must be staged and committed together; a
partial commit is not a valid synchronized plan state.

## 11. Rollback And Stop Conditions

Rollback is layered:

1. Set `MONITOR_BROWSER_COOKIE_SYNC_ENABLED=false`.
2. Hide/disable C.2 browser auto-sync and stop direct acquisition while
   preserving QR and C.1 advanced manual Cookie.
3. Keep C.3 profile-only execution active after acceptance; rollback must not
   restore raw Cookie argv.
4. Before C.3 acceptance, leave the current baseline inactive/unchanged when
   migration evidence is incomplete rather than partially enabling C.3.
5. Keep additive metadata readable and run promotion recovery before binary
   downgrade; do not delete active Profiles or verified Cookies.
6. Invalidate any in-memory acquisition session during rollback; no separate
   Connector credential or Extension state exists.

Stop the active packet and record evidence when:

- provider paths cannot converge without changing Phase 5.1 scope;
- the direct adapter cannot prove exact context/account/session binding and
  structured acquisition;
- platform verification cannot distinguish the intended account;
- clean-computer bootstrap requires manual browser Profile or Extension setup;
- a test exposes cross-account Cookie material or a real external action from
  a default test path;
- a Cookie-bridge network route is added despite the Packet B replacement;
- Packet C cannot preserve the previous active Profile on failed refresh or
  cannot prove raw Cookie absent from child argv;
- promotion recovery can leave database/Profile disagreement, ambiguous
  dual-active state, or an unbounded candidate/rollback artifact;
- disabling browser sync disables advanced manual Cookie, disables accepted
  profile-only execution, or restores raw Cookie argv;
- server QR or existing manual Cookie behavior regresses.

## 12. Historical Cross-Validation Record

The entries below are dated history for the roadmap artifact. They are not
current execution instructions or acceptance criteria; the current normative
boundaries are in sections 1-11 and the linked Packet B/C/D documents.

- Claude Code round 1, read-only (`Read,Grep,Glob`), verdict `BLOCKED` on the
  original draft.
- Valid findings incorporated here: stale CR number, license/distribution and
  Python runtime gates, Service Worker versus registration proof, local versus
  server scope, loopback security, account/client binding, restart/isolation
  tests, and plan decomposition.
- Phase 5.1P being open is intentionally represented as an execution gate, not
  as a defect in this proposed roadmap.
- Claude Code round 2, read-only (`Read,Grep,Glob`), verdict
  `READY AFTER SMALL REFINEMENTS`, with no blocking findings.
- Round 2 refinements incorporated: in-process Python 3.11 connector ownership,
  standard-install bootstrap proof, reference-protocol divergence handling,
  CR-112 timing, and explicit headless result classification.
- Claude Code final focused re-review, read-only (`Read,Grep,Glob`), verdict
  `READY`: no blocking findings, material refinements, or remaining polish.
- After formal document synchronization, a broader Claude review initially
  returned `READY` but relied on requirements from its prompt rather than file
  evidence. Focused challenge corrected the verdict to `BLOCKED` for missing
  server-side loopback/proxy enforcement, subprocess-Cookie risk
  classification, and atomic delivery wording.
- The three audit gaps are incorporated in the current revision. Final focused
  Claude Code re-review returned `READY` with no blocking or material plan
  issue; no further wording change was requested.
- The 2026-07-19 user decision supersedes the earlier proposed temporary
  local-only argv-risk acceptance option. The target now requires persistent
  Profile preparation and no raw Cookie in managed crawler child argv.
- Supplemented-document deep audit round 1 returned `BLOCKED` for underspecified
  Profile crash consistency, raw-Cookie argv retirement, Bridge-off rollback,
  structured Cookie fidelity, route topology, and restart finalization. The
  resulting C.1/C.2/C.3 contracts were added across specialist and packet docs.
- Deep audit round 2 returned `BLOCKED` and produced valid refinements for the
  exact parent/child interface, version-0 cutover, C.2-only flag ownership,
  cleanup triggering, fresh-candidate isolation, binding rotation, and pinned
  framework evidence. The claim that checkpoint plus directory inspection was
  inherently contradictory was rejected; rename-before-checkpoint ordering,
  operation marker, commit authority, and a directory-shape table now make the
  crash gap explicit.
- Deep audit round 3 incorrectly required future CR-112 implementation and a
  completed Phase 5.1P map before approving the plan. Status wording was made
  unambiguous, and a local pinned-stack probe independently confirmed unmounted
  HTTP 404 and WebSocket pre-accept 403 behavior without a product connector.
- Claude Code deep audit round 4, read-only (`Read,Grep,Glob`), returned
  `READY` with `BLOCKERS=None`, `MATERIAL REFINEMENTS=None`, and confirmed the
  Round 2 technical closures plus the proposed/not-started governance boundary.
- Final complete-diff round 5, read-only (`Read,Grep,Glob`), also returned
  `READY` with no blocker or material refinement after `CURRENT_STATE.md`,
  `TASKS.md`, `TEST_RESULTS.md`, and `TRACEABILITY.md` synchronization.
