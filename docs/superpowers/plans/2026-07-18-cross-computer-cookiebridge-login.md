# Cross-Computer Browser Login And CookieBridge Roadmap

> Planning artifact only. This roadmap does not approve code, schema, runtime,
> extension, or deployment changes. Execute only the packet whose start gate is
> open in the current project documents.

**Goal:** Add an optional local-desktop browser login flow that opens a
project-managed Chrome or Edge Profile, acquires Cookies through a
project-owned CookieBridge-compatible connector, verifies the exact account,
and saves it without manual Cookie copying. Preserve QR login as the primary
server path and manual Cookie input as a collapsed advanced option.

**Baseline:** originally reviewed against `main@abb4d66`; Phase 5.1P was later
verified against `main@459237f` on 2026-07-19. `CR-111` is already used. The
proposed requirement identifier is `CR-112`. Phase 5.1A is implemented and
independently verified; Phase 5.1B is now the next CR-047 unit.

**Review lane:** Deep. The roadmap touches browser processes, extension
distribution, authentication material, account identity, durable state,
multi-account isolation, deployment, and shared login/runtime contracts.

## 1. Roadmap Status

This file is a gated master roadmap, not one implementation batch. A roadmap
can be ready for approval while later packets remain blocked by declared
evidence gates. A packet is implementation-ready only when every prerequisite
listed for that packet is verified in current project documents.

The current authoritative order is:

1. Keep Packet A, the verified Phase 5.1P read-only preflight under CR-047, as
   the provider compatibility boundary.
2. Complete the existing Phase 5.1A-D implementation and Phase 5.1 acceptance
   gate under CR-047. This roadmap does not duplicate or reorder that work.
3. Preserve CR-070 / Phase 5.2 as the currently accepted lane after CR-047.
4. CR-112 is registered as `Needs Confirmation`; a later accepted decision
   must place Packet B relative to CR-070 before Packet B starts.
5. Execute Packet B, the connector compatibility, pairing, and protocol spike,
   only after its confirmation and sequencing gates pass.
6. Accept the distribution/runtime decisions and then execute Packet C,
   the local browser auto-sync feature.
7. Execute Packet D, the clean-computer and deployment acceptance matrix.

Packet documents:

- `docs/superpowers/plans/2026-07-19-phase-5.1p-browser-provider-preflight.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-pairing-compatibility-spike.md`
- `docs/superpowers/plans/2026-07-19-local-browser-auto-sync-login.md`
- `docs/superpowers/plans/2026-07-19-cookiebridge-deployment-acceptance.md`

## 2. Current Baseline Diff

| Label | Current evidence | Classification | Documentation action | Protected behavior | Readiness |
|---|---|---|---|---|---|
| Phase 5.1P | `docs/TASKS.md` and `docs/phase-5.1p-browser-entrypoint-map.md` record verified completion | Completed read-only preflight | Keep as Packet A evidence and provider boundary | No code, schema, Profile, Cookie, proxy, or runtime mutation | Complete |
| Phase 5.1A-D | Phase 5.1P and Phase 5.1A-C verified and merged; Phase 5.1D is active | Current, serially dependency-gated | Keep under CR-047 | One provider output and requested/effective snapshots | Complete Phase 5.1D |
| Phase 5.1 acceptance | Gated by Phase 5.1A-D | Current dependency-gated | Keep under CR-047 | Server-like proof; no diagnostic fallback presented as identity proof | Blocked |
| Proposed CR-112 | Registered in formal governance with status `Needs Confirmation` | Needs Confirmation | Keep linked plans proposed until scope and sequencing are accepted | Current QR and manual Cookie flows | Not implementation-ready |
| CookieBridge source | Temporary source under `.codex_tmp`; extension loads a Service Worker but did not register in the observed black-box run | Needs Baseline | Evaluate in Packet B only | No product dependency on unproved connector behavior | Future-valid |
| CR-070 / Phase 5.2 | Starts after CR-047 provider/snapshot verification | Deferred dependency | Do not absorb into CR-112 | Existing import/export ownership | Future-only |
| CR-092 to CR-094 | Independent future architecture lanes | Future-only | Keep separate | No hidden prerequisite or parallel account/provider system | Future-only |

Browser and login evidence on the current baseline:

- `tools/browser_launcher.py` detects Chrome before Edge and Chromium.
- `login_browser.py`, `login_qrcode.py`, and `account_check.py` still resolve or
  consume browser paths independently.
- `MONITOR_BROWSER_EXECUTABLE` is documented but is not yet one uniformly
  consumed login/runtime authority.
- `runner.py` passes decrypted saved Cookie material through `--cookies` for
  `login_type=cookie`. Phase 5.1P mapped that current baseline without
  changing it; Packet C owns the later confirmed migration to persistent
  Profile preparation and no raw Cookie in managed crawler child argv.
- The evaluated CookieBridge extension hardcodes `ws://localhost:8274/ws`,
  generates a `client_id`, and registers without an account/Profile pairing
  claim. Its server accepts clients by `client_id`, keeps connection state in
  memory, and can choose a client when no exact identifier is supplied.
- The evaluated CookieBridge license is non-commercial-learning-only and its
  server declares Python `>=3.12`; the project runtime uses Python 3.11.

## 3. Accepted Planning Decisions

These decisions define the roadmap. The persistent-Profile/login-material
sub-decision was confirmed on 2026-07-19. Recording the remaining CR-112 scope
as accepted still requires the repository's normal confirmation and
documentation process.

### 3.1 Login model and UI order

Keep the backend login types:

```text
qrcode
cookie
```

For `login_type=cookie`, add provenance rather than a third login type:

```text
cookie_source=bridge
cookie_source=manual
```

User-facing order:

1. QR login is the default.
2. Browser login and automatic synchronization is the normal Cookie workflow
   when the local feature is enabled and healthy.
3. Manual Cookie input remains visible inside a collapsed advanced section.

Bridge health failure is a state of the browser auto-sync workflow. It does
not automatically open or promote manual Cookie input, and it never switches
the selected account.

### 3.2 Identity and login-material authority

- Account identity authority: `social_account` plus `profile_key`.
- QR and accepted Cookie login both converge on the application-managed
  persistent Profile resolved from `profile_key`. That Profile is the normal
  browser session and crawl environment for both modes.
- A Bridge- or manually supplied Cookie is bootstrap, refresh, recovery, and
  migration material. It is injected into an account-bound persistent Profile
  and validated there before activation, and the verified value is also
  retained through the encrypted account store.
- An existing active Profile uses the fixed-active-path, same-volume
  candidate/rollback journal from `ACCOUNT_ENVIRONMENT.md`; a failed candidate
  restores the previous Profile/Cookie or blocks as `recovery_required`
  without guessing.
- The connector is an acquisition/refresh channel only. Its in-memory cache is
  never durable login authority.

Bridge- or manually sourced Cookies must pass the same platform account check
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

V1 browser auto-sync is local-desktop and same-host only:

```text
monitor service + managed browser + connector service
on the same Windows computer
```

The product connector is a WebSocket module in the existing monitor FastAPI
service. It binds through the monitor service and the extension connects only
to `127.0.0.1`; the default URL is
`ws://127.0.0.1:8080/api/monitor/cookie-bridge/ws`. Deployments using a
different effective `MONITOR_PORT` must set the matching loopback URL and pass
startup health validation. Non-loopback endpoints are rejected while
`MONITOR_COOKIE_BRIDGE_REMOTE_ENABLED=false`.

Locality is enforced on the server-side socket peer, not inferred from the URL
or proxy headers. The handler accepts only a parseable literal loopback peer
(`127.0.0.1` or `::1`), ignores `X-Forwarded-For`, `Forwarded`, and similar
headers for authorization, and requires the exact allowlisted
`chrome-extension://<stable-extension-id>` Origin before accepting the
WebSocket. Invalid peer or Origin is rejected before session/client/pairing or
Cookie protocol state.

When disabled, the route is not mounted: normal HTTP probe returns 404 and the
pinned Starlette/Uvicorn baseline rejects unmatched WebSocket upgrade with 403
before acceptance. When enabled, every remotely reachable reverse proxy denies
and does not forward
`/api/monitor/cookie-bridge/`, including WebSocket upgrades. Direct LAN-address,
spoofed forwarding-header, missing/wrong-Origin, and reverse-proxy probes must
fail before protocol state.

Remote Bridge topology, browser-on-operator/monitor-on-server topology, and
cross-host Cookie transport are outside V1. They require a separate decision
covering TLS, endpoint authentication, origin policy, network access control,
secret rotation, and deployment ownership.

Server production acceptance remains the existing server-started QR workflow.
Local Chrome/Edge auto-sync is not production proof. Headless extension support
may be evaluated in Packet D but does not gate the V1 local feature and does
not replace the QR production baseline.

### 3.5 Distribution and runtime

The source under `.codex_tmp` is evaluation evidence only. Product integration
must use one accepted route:

1. written permission granting the intended use and distribution; or
2. a project-owned compatible extension and connector implementation based on
   the observed protocol requirements, without copying restricted source.

The plan defaults to route 2. No third-party extension/server source is copied,
bundled, modified, or shipped before the decision is recorded. Packet B may
run read-only inspection and disposable black-box tests against the temporary
artifact.

The Python 3.12 reference server is a disposable Packet B dependency only. The
V1 product connector runs inside the existing Python 3.11 FastAPI service; it
has the same startup/shutdown lifecycle, exposes a feature-gated loopback
WebSocket route, and reports readiness through monitor diagnostics. There is no
separate connector process or Python 3.12 requirement on a product computer. A
project-wide Python upgrade and a separately managed connector service are
outside CR-112.

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

## 4. Pairing And Multi-Account Contract

The current reference `client_id` is not sufficient account identity. V1 uses
an exact, authenticated pairing flow and never selects the first, newest, or
only connected client implicitly.

### 4.1 First pairing

1. For a new account, the authenticated monitor API first reuses the existing
   `create_draft_social_account` flow so a real account ID and `profile_key`
   exist before browser launch. It then creates a browser-sync login session
   while holding the target account/Profile lock. Existing accounts reuse their
   locked identity/provider inputs, but leave the current active Profile
   untouched and initialize a fresh candidate; active Profile and extension
   storage are never cloned into the candidate.
2. It generates a cryptographically random, single-use pairing token with a
   five-minute maximum lifetime. Durable state stores only its hash and binds
   it to `login_session_id`, `social_account_id`, `profile_key`, platform, and
   the initiating actor.
3. Packet B selects and proves the browser-bound bootstrap mechanism. The
   current candidate is an ephemeral copy of the project-owned unpacked
   extension whose generated `bridge_config.json` contains the loopback
   endpoint, protocol version, and one-time token. Only the managed candidate
   browser receives this extension path, and Packet B must prove that removing
   it leaves the promoted Profile crawler-usable without a stale path or
   reconnect side effect.
4. The extension reads its packaged config, connects from the expected stable
   extension origin, and registers with `protocol_version`, its Profile-local
   `client_id`, and the pairing token.
5. The connector atomically consumes the token, rejects expiry/replay, derives
   the account/Profile binding from server-side token state, and returns a
   rotatable Profile-scoped credential.
6. The extension stores `client_id` and the credential in that managed
   Profile's `chrome.storage.local`. The service stores only the credential
   hash and binding metadata. The ephemeral extension directory remains
   readable by that browser until the session is terminal and the browser has
   closed, then the centralized finalizer removes it.

The ephemeral directory uses restricted local permissions and is excluded from
backups and repository tracking. The consumed token remains invalid even if its
file is read before terminal cleanup. Token and credential values are redacted
from API responses, logs, diagnostics, test snapshots, and documentation
evidence. The extension identity is fixed by packaged manifest-key material and
must produce the same allowlisted `chrome-extension://` origin across Chrome,
Edge, ephemeral copies, and clean installations. Its manifest requests only
`cookies`, storage, and exact supported-platform/loopback permissions required
by the accepted protocol; `<all_urls>` and unrelated host access are excluded.

### 4.2 Reconnect and revocation

- Reconnect uses `client_id` plus the Profile-scoped credential, not a new
  arbitrary client selection.
- A candidate credential remains `pending` and serves only the exact promotion
  session. Bridge commit activates it and revokes the predecessor; manual
  Cookie commit creates no candidate binding and revokes the predecessor;
  rollback revokes the candidate and preserves the predecessor.
- Connector restart clears live sockets and Cookie cache. The extension
  reconnects and authenticates from Profile storage; durable account/Profile
  and verified Cookie state remain unchanged.
- Account reset, Profile reset, credential rotation, or account deletion
  revokes the binding and invalidates later reconnect attempts.
- One Profile binds to one social account for this workflow. A client already
  bound elsewhere is rejected.

### 4.3 Cookie request

Each Cookie request contains a server-generated request ID, expected binding
ID, platform, protocol version, and expiry. The connector routes it only to the
authenticated socket for that binding. Responses are accepted only when
request ID, binding, platform, protocol version, and session are exact and
current. Duplicate, late, stale, or cross-account responses are discarded and
audited without Cookie values.

Bridge responses use the structured Cookie Protocol V1 defined in
`ACCOUNT_ENVIRONMENT.md`. They preserve domain/path/security attributes and
distinct Cookie tuples; they are not flattened to a Cookie-header string.
Packet B fixes Chrome/Edge supported attributes and bounded record/frame limits
before Packet C. Unrelated domains, malformed scope, exact duplicate tuples,
unsupported required attributes, and unsupported protocol versions fail closed.
Advanced manual strings are canonicalized by C.1 into the same internal record
model before Profile injection.

The connector exposes no unauthenticated client-list or Cookie-read endpoint.
Monitor-side calls use an internal authenticated boundary and must name the
exact binding; an empty binding is an error, not a request for any client.

## 5. Browser-Sync And Profile-Promotion State Machines

Browser-sync states:

```text
created
-> preparing_profile
-> browser_starting
-> waiting_extension
-> waiting_user_login
-> requesting_cookie
-> validating_candidate
-> candidate_ready
-> promoting_profile
-> validating_active
-> committing
-> succeeded
```

Terminal non-success session states:

```text
failed | timed_out | cancelled | browser_closed | bridge_offline |
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
swap/recovery/binding matrix lives in `ACCOUNT_ENVIRONMENT.md` and is a required
Packet C contract.

Each same-volume rename completes before its following checkpoint write. The
checkpoint may therefore lag one rename; it is not competing authority. The
single account/Cookie/binding plus `committed` database transaction decides old
versus new authority, while recovery uses the operation marker and exact
directory-shape table in `ACCOUNT_ENVIRONMENT.md` to perform that decision.

Every transition validates the account/Profile lock, session generation, and
promotion ID. Each non-terminal state has a deadline and restart rule.
Cancellation before `swapping` removes the closed candidate; cancellation at
or after `swapping` waits for safe commit or rollback before the session becomes
terminal. A service restart reconciles non-terminal promotion journals before
the affected account can be checked, reset, exported, logged in, or crawled.

One centralized, idempotent finalizer cancels polling, rejects late messages,
closes browser/Profile handles, releases locks, removes ephemeral extension
config, and invokes journal recovery/cleanup. It never deletes the fixed active
Profile or the only rollback copy. Repeated finalization is a no-op.
Committed rollback cleanup is triggered by the first successful managed run,
by startup/periodic `cleanup_after` scanning, and before a new promotion. A
failed cleanup retains one artifact, blocks refresh, and alerts for operator
remediation rather than accumulating copies.

The database commit is atomic only for verified Cookie ciphertext, source,
identity snapshot, binding/profile-ready metadata, account status, audit
linkage, and journal state. Filesystem promotion occurs before that transaction
and is made recoverable by the journal; documentation and code must not describe
the database and Profile directory as one atomic transaction.

Before `active_recheck`, one-time pairing/config material is removed. The fixed
active path is reopened without Bridge injection arguments or a session
extension copy so the check proves crawler-equivalent reuse and catches any
dependency on a deleted temporary extension path.

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
MONITOR_COOKIE_BRIDGE_ENABLED=false
MONITOR_COOKIE_BRIDGE_URL=ws://127.0.0.1:8080/api/monitor/cookie-bridge/ws
MONITOR_COOKIE_BRIDGE_REMOTE_ENABLED=false
MONITOR_ALLOW_REAL_BROWSER_TESTS=0
```

- Default-off means the connector route is not mounted, and no
  extension load argument, pairing token, schema-dependent API, or UI auto-sync
  action is activated.
- `MONITOR_COOKIE_BRIDGE_ENABLED` controls only Packet C.2 connector,
  extension, APIs, and UI. It does not disable C.1 advanced-manual
  Cookie-to-Profile service or C.3 profile-only runner behavior after those
  sub-packets are accepted.
- Only C.2 router inclusion, UI/capability/readiness, and extension/pairing
  launch may read that flag. C.1 validation/promotion/recovery/manual Cookie
  and C.3 command/child/platform guards import and execute independently when
  it is false.
- The selected default-off behavior is route-not-mounted: a normal HTTP probe
  returns 404, while the pinned Starlette/Uvicorn baseline rejects an unmatched
  WebSocket upgrade with 403 before acceptance. Packet B locks these packaged-
  runtime expectations. An enabled route still rejects invalid peer or Origin
  before WebSocket acceptance.
- Baseline evidence is FastAPI `0.110.2` and Uvicorn `0.29.0` from exact
  `pyproject.toml` pins plus Starlette `0.37.2` from `uv.lock`. Status codes are
  regression evidence, not the authorization boundary; route absence and zero
  connector protocol state are mandatory across reviewed dependency upgrades.
- Unit/integration tests use a fake connector and temporary Profiles.
- Real Chrome/Edge and platform login tests require
  `MONITOR_ALLOW_REAL_BROWSER_TESTS=1` and remain separate from standard pytest.
- Empty URL, missing extension artifact, unhealthy connector, or invalid
  executable produces an explicit unavailable state; no default account,
  client, Profile, or Cookie fallback is permitted.

## 7. Packet Gates

### Packet A: Phase 5.1P preflight

This packet is complete. It is read-only, produced
`docs/phase-5.1p-browser-entrypoint-map.md`, and made no CookieBridge
implementation decision.

**Exit:** all existing login/crawl/CDP entrypoints and requested/effective
provider fields are mapped without runtime mutation.

### Existing Phase 5.1A-D and acceptance

This existing CR-047 work now runs from Phase 5.1A through Phase 5.1D and
acceptance before Packet B. Its current project tasks remain authoritative.

**Exit:** one BrowserEnvironmentProvider output and runtime snapshot contract
are verified across server-like login and crawl paths.

### Packet B: compatibility, pairing, and protocol spike

Starts after Phase 5.1 acceptance, CR-112 acceptance, and an explicit
sequencing decision relative to CR-070. It may inspect the temporary reference
and run disposable black-box tests. It does not change
product schema, APIs, UI, Profiles, or deployment.

Packet B must also prove server-side loopback peer enforcement,
forwarded-header spoof rejection, exact extension Origin validation, disabled
HTTP 404/WebSocket 403 behavior on the pinned runtime, and reverse-proxy
exclusion before Packet C can start.

**Exit:** a project-owned protocol and packaging decision exists, and a
prototype proves extension Service Worker, WebSocket authentication,
token-to-client pairing, and one exact Cookie request/response roundtrip.

### Packet C: local browser auto-sync implementation

Starts only after Packet B passes, distribution/runtime decisions are accepted,
the persistent-Profile/no-raw-argv migration plan is approved, and a data-model
migration plan is approved.

Packet C is serial:

1. **C.1 Profile service:** shared Bridge/manual canonicalization, candidate
   validation, promotion journal, fixed-path swap, restart recovery, cleanup,
   and account migration. No Bridge route/UI is enabled.
2. **C.2 Bridge acquisition:** connector, extension, pairing, APIs, and UI,
   controlled only by `MONITOR_COOKIE_BRIDGE_ENABLED`.
3. **C.3 Profile-only runner:** migrate/mark every `login_type=cookie` account,
   add the
   explicit internal profile-only child contract, prohibit generic/QR/default
   fallback, prove no raw Cookie argv/env, and retire managed `--cookies` use.

**Exit:** C.1-C.3 pass in order; local Chrome and Edge workflows validate and
persist exact-account Cookies with no manual copy/paste or cross-account
fallback; advanced manual Cookie still works when Bridge is disabled; and
managed crawler children use the fixed verified Profile with no raw Cookie.

### Packet D: deployment and acceptance

Starts after Packet C targeted and integration tests pass.

**Exit:** clean Windows computer setup, browser matrix, failure/restart matrix,
rollback, and server QR non-regression are verified. Headless Bridge remains a
separate result and does not weaken the server-first boundary.

## 8. Verification Matrix

| Environment | Connector | Browser | Real platform | Allowed by default | Required proof |
|---|---|---|---|---|---|
| Standard pytest | Fake | Fake/temp Profile | No | Yes | State machine, pairing, replay, isolation, cleanup |
| Local diagnostics | Fake or disposable loopback | Installed browser | No | Yes | Provider resolution and extension registration |
| Opt-in browser smoke | Disposable loopback | Chrome and Edge | No | Explicit opt-in | Service Worker + authenticated registration + roundtrip |
| Local pilot | Loopback product connector | Managed visible browser | Yes | Operator opt-in | Exact account validation, encrypted Cookie persistence, Profile restart reuse, and no raw Cookie argv |
| Server-like regression | Disabled | Bundled/headless QR browser | Platform as existing plan permits | Existing gates | QR flow and crawl non-regression |
| Production | Disabled for V1 | Server-started browser | Yes | Existing server policy | QR login remains primary acceptance path |

Required negative tests include:

- expired/replayed pairing token;
- unexpected extension origin;
- non-loopback socket peer with a loopback-looking URL or spoofed forwarding
  headers;
- LAN-address and reverse-proxy WebSocket upgrade attempts;
- feature-disabled normal HTTP probe not returning 404, or unmatched WebSocket
  upgrade not returning the packaged-runtime pre-accept rejection (403 on the
  pinned Starlette/Uvicorn baseline);
- wrong Profile/client credential;
- unstable extension ID across Chrome/Edge/ephemeral copies/clean installs,
  overbroad extension host permissions, or a promoted Profile depending on a
  deleted session extension path;
- candidate binding active before commit, predecessor binding usable after
  commit, candidate binding usable after rollback, or manual promotion leaving
  the rollback Profile's binding active;
- simultaneous Account A and B login and crawl;
- stale response after timeout/cancellation;
- browser close at every non-terminal state;
- connector restart before and after persistence;
- project restart with reconnect credential;
- Profile reset and revoked credential;
- malformed or wrong-platform Cookie response;
- failed platform verification preserving prior Cookie;
- crash/kill at every Profile promotion checkpoint restoring the previous
  active Profile or producing deterministic `recovery_required` evidence;
- disk-full, open-handle, antivirus/permission, and same-volume rename failure
  before account activation;
- missing/expired Profile in profile-only mode failing without QR, empty
  Cookie, generic Profile, or default-network fallback;
- Bridge disabled while advanced manual Cookie and profile-only runs remain
  usable and raw argv remains retired;
- structured Cookie duplicate/scope/domain/attribute/version/size rejection;
- locked account with browser/proxy/default-network fallback attempt;
- standard tests with production-like environment variables still blocked from
  real browser, real connector, and real platform access;
- process inspection proving raw Cookie is absent from managed crawler child
  argv after persistent-Profile preparation.

## 9. Accident Invariants

Must never happen:

- raw Cookie, pairing token, or credential appears in logs/UI/test artifacts;
- raw Cookie process-argument exposure is hidden, mislabeled as end-to-end
  isolation, or retained after Packet C acceptance;
- a failed Cookie refresh damages the previously active Profile or replaces
  the previous verified encrypted Cookie;
- a candidate inherits the active Profile's connector credential or mutates
  the active Profile before `swapping`;
- database and fixed active Profile disagree without deterministic journal
  recovery, or two operation directories become runtime authorities;
- Bridge disablement breaks advanced manual Cookie or restores raw Cookie argv;
- a non-loopback peer or reverse-proxy request reaches connector protocol state;
- an account uses the first/newest/only Bridge client by convenience;
- a late response overwrites a newer session or verified Cookie;
- Bridge failure changes QR behavior or silently opens manual Cookie input;
- a locked Profile falls back to another browser, Profile, proxy, or network;
- restricted third-party code is bundled into the product;
- a local-browser result is reported as server production acceptance.

Must eventually happen:

- every browser-sync session reaches one terminal state;
- every candidate Profile is promoted, rolled back, quarantined for
  `recovery_required`, or deleted; cleanup is attempted by the documented
  deadlines, retains at most one artifact on failure, and emits an operator
  alert instead of accumulating copies;
- browser, socket waiters, polling tasks, locks, and ephemeral config are
  finalized idempotently;
- connector restart either re-authenticates the exact binding or reports an
  unavailable state without changing account validity;
- account/Profile reset revokes the binding and prevents stale reconnect;
- normal promotion reaches a terminal binding state: Bridge commit activates
  only the candidate and revokes the predecessor, manual commit leaves the new
  Profile unpaired and revokes the predecessor, and rollback preserves only the
  predecessor.

## 10. Documentation And Traceability

CR-112 is registered in `CHANGE_REQUESTS.md` as a new capability with `Needs
Confirmation` and linked to `TASKS.md`, `TRACEABILITY.md`, and `TEST_PLAN.md`.
The persistent-Profile authority and no-raw-Cookie-argv target are confirmed.
Do not mark the full CR accepted until the local scope, distribution route,
pairing protocol, server QR boundary, and sequencing relative to CR-070 are
confirmed.

Each packet updates `CURRENT_STATE.md`, `TASKS.md`, `TEST_RESULTS.md`, and
`TRACEABILITY.md` only for evidence actually produced. Phase 5.1 historical
ownership remains under CR-047; CR-112 references it as a dependency and does
not reopen or duplicate it.

The five plan files and all CR-112 formal references are one atomic
documentation-delivery unit. They must be staged and committed together; a
partial commit is not a valid synchronized plan state.

## 11. Rollback And Stop Conditions

Rollback is layered:

1. Set `MONITOR_COOKIE_BRIDGE_ENABLED=false`.
2. Hide/disable C.2 browser auto-sync, unmount the connector route, and stop
   extension injection while preserving QR and C.1 advanced manual Cookie.
3. Keep C.3 profile-only execution active after acceptance; rollback must not
   restore raw Cookie argv.
4. Before C.3 acceptance, leave the current baseline inactive/unchanged when
   migration evidence is incomplete rather than partially enabling C.3.
5. Keep additive metadata readable and run promotion recovery before binary
   downgrade; do not delete active Profiles or verified Cookies.
6. Apply normal promotion binding rotation as part of commit/rollback. Outside
   that lifecycle, bulk-revoke credentials only for explicit account/Profile
   reset, account deletion, or confirmed compromise.

Stop the active packet and record evidence when:

- provider paths cannot converge without changing Phase 5.1 scope;
- the prototype cannot prove authenticated registration and exact roundtrip;
- extension policy prevents reliable managed loading on supported browsers;
- platform verification cannot distinguish the intended account;
- clean-computer bootstrap requires manual browser Profile or extension setup;
- a test exposes cross-account Cookie material or a real external action from
  a default test path;
- loopback enforcement depends on URL text, forwarded headers, or reverse-proxy
  implication rather than the socket peer and exact extension Origin;
- Packet C cannot preserve the previous active Profile on failed refresh or
  cannot prove raw Cookie absent from child argv;
- promotion recovery can leave database/Profile disagreement, ambiguous
  dual-active state, or an unbounded candidate/rollback artifact;
- disabling Bridge disables advanced manual Cookie, disables accepted
  profile-only execution, or restores raw Cookie argv;
- server QR or existing manual Cookie behavior regresses.

## 12. Cross-Validation Record

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
