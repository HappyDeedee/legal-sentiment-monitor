# Cross-Computer Browser Login And CookieBridge Roadmap

> Planning artifact only. This roadmap does not approve code, schema, runtime,
> extension, or deployment changes. Execute only the packet whose start gate is
> open in the current project documents.

**Goal:** Add an optional local-desktop browser login flow that opens a
project-managed Chrome or Edge Profile, acquires Cookies through a
project-owned CookieBridge-compatible connector, verifies the exact account,
and saves it without manual Cookie copying. Preserve QR login as the primary
server path and manual Cookie input as a collapsed advanced option.

**Baseline:** `main@abb4d66`; local `main` and `origin/main` were `0/0` when
this roadmap was refreshed. `CR-111` is already used. The proposed requirement
identifier is `CR-112`. Phase 5.1P remains the first unblocked execution lane.

**Review lane:** Deep. The roadmap touches browser processes, extension
distribution, authentication material, account identity, durable state,
multi-account isolation, deployment, and shared login/runtime contracts.

## 1. Roadmap Status

This file is a gated master roadmap, not one implementation batch. A roadmap
can be ready for approval while later packets remain blocked by declared
evidence gates. A packet is implementation-ready only when every prerequisite
listed for that packet is verified in current project documents.

The current authoritative order is:

1. Execute Packet A, the existing Phase 5.1P read-only preflight under CR-047.
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
| Phase 5.1P | `docs/TASKS.md` Phase 5.1P is unchecked and explicitly read-only | Active/current | Keep as first lane; execute Packet A | No code, schema, Profile, Cookie, proxy, or runtime mutation | Ready now, read-only |
| Phase 5.1A-D | Gated by Phase 5.1P | Current dependency-gated | Keep under CR-047 | One provider output and requested/effective snapshots | Blocked by Phase 5.1P |
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
  `login_type=cookie`; the roadmap must preserve this V1 execution contract.
- The evaluated CookieBridge extension hardcodes `ws://localhost:8274/ws`,
  generates a `client_id`, and registers without an account/Profile pairing
  claim. Its server accepts clients by `client_id`, keeps connection state in
  memory, and can choose a client when no exact identifier is supplied.
- The evaluated CookieBridge license is non-commercial-learning-only and its
  server declares Python `>=3.12`; the project runtime uses Python 3.11.

## 3. Accepted Planning Decisions

These decisions define the roadmap. Recording CR-112 as accepted still
requires the repository's normal confirmation and documentation process.

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

There is no single authority for both existing login types:

- Account identity authority: `social_account` plus `profile_key`.
- QR mode runtime authority: the server-side persistent Profile.
- Cookie mode runtime authority in V1: the encrypted, platform-verified Cookie
  saved on the account and passed by `runner.py --cookies`.
- The managed Profile supports browser login and preserves browser state for
  Cookie mode, but it does not silently replace the saved Cookie contract.
- The connector is an acquisition/refresh channel only. Its in-memory cache is
  never durable login authority.

Bridge- or manually sourced Cookies must pass the same platform account check
before they are encrypted and activated. The requested account/Profile lock
must still be held when validation and persistence commit. A failed validation
does not overwrite the last verified Cookie.

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

When disabled, the route is not mounted and access returns 404. When enabled,
every remotely reachable reverse proxy denies and does not forward
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
CR-112 preserves the current execution authority but does not classify this as
end-to-end secret isolation.

Packet C remains closed until one path is accepted:

1. a separately governed secure child-secret transport change with explicit
   owner, migration, compatibility, and tests; or
2. a time-bounded local-only risk acceptance naming owner, expiry, environment
   boundary, and excluded production-security claims.

Implementation must not silently change the runner/MediaCrawler contract or
silently accept the existing exposure. If secure transport is selected, child
process inspection must prove raw Cookie is absent from argv.

## 4. Pairing And Multi-Account Contract

The current reference `client_id` is not sufficient account identity. V1 uses
an exact, authenticated pairing flow and never selects the first, newest, or
only connected client implicitly.

### 4.1 First pairing

1. For a new account, the authenticated monitor API first reuses the existing
   `create_draft_social_account` flow so a real account ID and `profile_key`
   exist before browser launch. It then creates a browser-sync login session
   while holding the target account/Profile lock. Existing accounts reuse their
   current identity and Profile.
2. It generates a cryptographically random, single-use pairing token with a
   five-minute maximum lifetime. Durable state stores only its hash and binds
   it to `login_session_id`, `social_account_id`, `profile_key`, platform, and
   the initiating actor.
3. The application generates an ephemeral copy of the project-owned unpacked
   extension. A generated `bridge_config.json` contains the loopback endpoint,
   protocol version, and one-time token. Only the managed browser process for
   that Profile receives this extension path.
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
evidence. The extension must have a stable identity so the connector can
allowlist its `chrome-extension://` origin.

### 4.2 Reconnect and revocation

- Reconnect uses `client_id` plus the Profile-scoped credential, not a new
  arbitrary client selection.
- Connector restart clears live sockets and Cookie cache. The extension
  reconnects and authenticates from Profile storage; durable account/Profile
  and verified Cookie state remain unchanged.
- Account reset, Profile reset, credential rotation, or account deletion
  revokes the binding and invalidates later reconnect attempts.
- One Profile binds to one social account for this workflow. A client already
  bound elsewhere is rejected.

### 4.3 Cookie request

Each Cookie request contains a server-generated request ID, expected binding
ID, platform, and expiry. The connector routes it only to the authenticated
socket for that binding. Responses are accepted only when request ID, binding,
platform, and session are exact and current. Duplicate, late, stale, or
cross-account responses are discarded and audited without Cookie values.

The connector exposes no unauthenticated client-list or Cookie-read endpoint.
Monitor-side calls use an internal authenticated boundary and must name the
exact binding; an empty binding is an error, not a request for any client.

## 5. Browser-Sync State Machine

```text
created
-> browser_starting
-> waiting_extension
-> waiting_user_login
-> requesting_cookie
-> validating
-> persisting
-> succeeded
```

Terminal non-success states:

```text
failed | timed_out | cancelled | browser_closed | bridge_offline
```

Every transition validates the account/Profile lock and session generation.
One centralized, idempotent finalizer cancels polling, rejects late messages,
releases locks, removes ephemeral config, and closes the managed browser after
success or terminal failure. Repeated cancellation/finalization is a no-op.

Persistence is one transaction: verified Cookie ciphertext, Cookie source,
platform identity snapshot, binding metadata, and account status update commit
together. The previous verified Cookie remains intact on failure.

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
- The selected default-off behavior is route-not-mounted with HTTP 404. An
  enabled route still rejects invalid peer or Origin before WebSocket
  acceptance.
- Unit/integration tests use a fake connector and temporary Profiles.
- Real Chrome/Edge and platform login tests require
  `MONITOR_ALLOW_REAL_BROWSER_TESTS=1` and remain separate from standard pytest.
- Empty URL, missing extension artifact, unhealthy connector, or invalid
  executable produces an explicit unavailable state; no default account,
  client, Profile, or Cookie fallback is permitted.

## 7. Packet Gates

### Packet A: Phase 5.1P preflight

Only this packet is ready now. It is read-only and produces the provider
entrypoint map. It makes no CookieBridge implementation decision.

**Exit:** all existing login/crawl/CDP entrypoints and requested/effective
provider fields are mapped without runtime mutation.

### Existing Phase 5.1A-D and acceptance

This existing CR-047 work runs after Packet A and before Packet B. Its current
project tasks remain authoritative.

**Exit:** one BrowserEnvironmentProvider output and runtime snapshot contract
are verified across server-like login and crawl paths.

### Packet B: compatibility, pairing, and protocol spike

Starts after Phase 5.1 acceptance, CR-112 acceptance, and an explicit
sequencing decision relative to CR-070. It may inspect the temporary reference
and run disposable black-box tests. It does not change
product schema, APIs, UI, Profiles, or deployment.

Packet B must also prove server-side loopback peer enforcement,
forwarded-header spoof rejection, exact extension Origin validation,
disabled-route 404, and reverse-proxy exclusion before Packet C can start.

**Exit:** a project-owned protocol and packaging decision exists, and a
prototype proves extension Service Worker, WebSocket authentication,
token-to-client pairing, and one exact Cookie request/response roundtrip.

### Packet C: local browser auto-sync implementation

Starts only after Packet B passes, distribution/runtime decisions are accepted,
the subprocess-Cookie security path is accepted, and a data-model migration
plan is approved.

**Exit:** local Chrome and Edge workflows validate and persist exact-account
Cookies with no manual copy/paste and no cross-account fallback.

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
| Local pilot | Loopback product connector | Managed visible browser | Yes | Operator opt-in | Exact account validation and encrypted persistence |
| Server-like regression | Disabled | Bundled/headless QR browser | Platform as existing plan permits | Existing gates | QR flow and crawl non-regression |
| Production | Disabled for V1 | Server-started browser | Yes | Existing server policy | QR login remains primary acceptance path |

Required negative tests include:

- expired/replayed pairing token;
- unexpected extension origin;
- non-loopback socket peer with a loopback-looking URL or spoofed forwarding
  headers;
- LAN-address and reverse-proxy WebSocket upgrade attempts;
- feature-disabled route returning anything other than 404;
- wrong Profile/client credential;
- simultaneous Account A and B login and crawl;
- stale response after timeout/cancellation;
- browser close at every non-terminal state;
- connector restart before and after persistence;
- project restart with reconnect credential;
- Profile reset and revoked credential;
- malformed or wrong-platform Cookie response;
- failed platform verification preserving prior Cookie;
- locked account with browser/proxy/default-network fallback attempt;
- standard tests with production-like environment variables still blocked from
  real browser, real connector, and real platform access;
- accepted subprocess-Cookie path evidence: raw Cookie absent from child argv,
  or a current local-only risk record with owner/expiry/environment limits.

## 9. Accident Invariants

Must never happen:

- raw Cookie, pairing token, or credential appears in logs/UI/test artifacts;
- raw Cookie process-argument exposure is hidden, mislabeled as end-to-end
  isolation, or carried into Packet C without an accepted decision;
- a non-loopback peer or reverse-proxy request reaches connector protocol state;
- an account uses the first/newest/only Bridge client by convenience;
- a late response overwrites a newer session or verified Cookie;
- Bridge failure changes QR behavior or silently opens manual Cookie input;
- a locked Profile falls back to another browser, Profile, proxy, or network;
- restricted third-party code is bundled into the product;
- a local-browser result is reported as server production acceptance.

Must eventually happen:

- every browser-sync session reaches one terminal state;
- browser, socket waiters, polling tasks, locks, and ephemeral config are
  finalized idempotently;
- connector restart either re-authenticates the exact binding or reports an
  unavailable state without changing account validity;
- account/Profile reset revokes the binding and prevents stale reconnect.

## 10. Documentation And Traceability

CR-112 is registered in `CHANGE_REQUESTS.md` as a new capability with `Needs
Confirmation` and linked to `TASKS.md`, `TRACEABILITY.md`, and `TEST_PLAN.md`.
Do not mark it accepted until the local scope, distribution route, authority
split, pairing protocol, server QR boundary, and sequencing relative to CR-070
are confirmed.

Each packet updates `CURRENT_STATE.md`, `TASKS.md`, `TEST_RESULTS.md`, and
`TRACEABILITY.md` only for evidence actually produced. Phase 5.1 historical
ownership remains under CR-047; CR-112 references it as a dependency and does
not reopen or duplicate it.

The five plan files and all CR-112 formal references are one atomic
documentation-delivery unit. They must be staged and committed together; a
partial commit is not a valid synchronized plan state.

## 11. Rollback And Stop Conditions

Rollback is feature-flag-first:

1. Set `MONITOR_COOKIE_BRIDGE_ENABLED=false`.
2. Hide/disable the browser auto-sync action while preserving QR and advanced
   manual Cookie workflows.
3. Disable the connector route and extension injection.
4. Keep additive metadata readable; do not delete Profiles or verified Cookies.
5. Revoke connector credentials only when an account/Profile is explicitly
   reset or the binding is compromised.

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
- Packet C has no accepted disposition for raw Cookie subprocess arguments;
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
