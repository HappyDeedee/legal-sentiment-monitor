# Local Browser Auto-Sync Login Packet

> Future implementation packet. Start only after the compatibility spike and
> its distribution, runtime, pairing, and clean-computer decisions pass.

**Goal:** Add a default-off local browser login flow that automatically
acquires and verifies Cookie material for the exact account while preserving
existing QR and advanced manual Cookie behavior.

## Start Gates

- [ ] Phase 5.1 acceptance is verified.
- [ ] Packet B passes Chrome and Edge authenticated roundtrip tests.
- [ ] CR-112 scope and project-owned connector/distribution route are accepted.
- [ ] CR-112 sequencing relative to CR-070 is accepted.
- [ ] Additive schema/migration, retention, and rollback rules are approved.
- [ ] Exact API/UI state machine and permission checks are documented.
- [ ] The raw Cookie subprocess-argument risk has an accepted disposition:
      secure child-secret transport under an explicit owner, or a time-bounded
      local-only risk acceptance with expiry and no production-security claim.

## Planned Touch Surface

Expected new focused modules:

- `api/monitoring/cookie_bridge.py`: authenticated connector client boundary;
- a feature-gated FastAPI WebSocket route backed by that module in the existing
  Python 3.11 monitor process;
- `api/monitoring/login_browser_sync.py`: session state machine/finalizer;
- project-owned extension and connector directories selected in Packet B;
- focused unit/integration tests for provider, connector, and login sessions.

Expected existing files:

- browser provider/runtime consumers established by Phase 5.1;
- `api/monitoring/database.py` and approved migrations;
- `api/routers/monitor.py`;
- account login HTML/CSS/JavaScript only;
- configuration examples and specialist documentation.

Do not change Task Center, Run Detail, reports, email, AI, roles, crawler
provider architecture, dynamic account rotation, or dynamic proxy scheduling.

## Data Contract

Persist additive metadata only after migration approval:

- `cookie_source` (`bridge` or `manual`);
- connector binding ID and Profile-local `client_id` identifier;
- credential hash/version, bind/revoke timestamps, and last authenticated time;
- last connector health/status without Cookie values;
- browser-sync session identity, actor, trigger source, terminal result, and
  effective browser/Profile/provider summary.

Store raw Cookies only through the existing encrypted account mechanism. Store
only pairing/credential hashes server-side. Customer APIs expose status and
timestamps, not Cookie, token, credential, raw Profile path, proxy credential,
CDP endpoint, or extension internals.

## Tasks

- [ ] Add default-off configuration; leave the connector route unmounted with
      404 when disabled.
- [ ] Enforce locality from the ASGI socket peer using a literal loopback IP
      check; reject empty/unparsable/non-loopback peers before WebSocket
      acceptance and ignore forwarded headers for authorization.
- [ ] Require the exact stable `chrome-extension://<extension-id>` Origin and
      reject missing, opaque, or unexpected Origins before protocol state.
- [ ] Keep `/api/monitor/cookie-bridge/` out of every remotely reachable
      reverse proxy and add LAN/proxy negative acceptance probes.
- [ ] Keep connector startup, shutdown, and readiness inside the monitor
      FastAPI lifecycle; do not introduce a Python 3.12 product runtime or a
      second service lifecycle.
- [ ] Add migrations with backward-compatible reads and rollback evidence.
- [ ] Implement exact connector authentication, request correlation, timeout,
      cancellation, reconnect, revocation, and no-implicit-client selection.
- [ ] Implement the browser-sync state machine and centralized idempotent
      finalizer from the master roadmap.
- [ ] Hold the account/Profile lock through browser launch, pairing, Cookie
      request, platform verification, and transactional persistence.
- [ ] Reuse `create_draft_social_account` for a new account so pairing always
      starts with a persisted account ID and assigned `profile_key`; do not add
      a parallel temporary-account identity model.
- [ ] Use the Phase 5.1 provider result; do not add another executable/Profile/
      proxy resolver.
- [ ] Validate Bridge Cookie through the existing platform account check and
      confirm platform identity before replacing the saved Cookie.
- [ ] Preserve the prior verified Cookie on any failure.
- [ ] Preserve Cookie-mode encrypted-material authority and record provenance
      without switching to Profile-only execution. Keep current
      `runner.py --cookies` behavior only until the accepted subprocess-secret
      decision assigns any invocation change to an explicit owner.
- [ ] Apply the accepted subprocess-Cookie decision. Secure transport must
      prove raw Cookie absent from child argv; temporary local-only acceptance
      must expose owner/expiry/environment limits to trusted diagnostics and
      must not be described as production secret isolation.
- [ ] Add authenticated start/status/cancel APIs. Status responses are
      customer-safe and session/account scoped.
- [ ] Add UI actions in this order: QR default, browser auto-sync, collapsed
      advanced manual Cookie. Do not auto-open manual input on Bridge failure.
- [ ] Open the managed browser automatically, update status without manual
      refresh, close it through finalization, and show distinct timeout,
      browser-closed, extension-unavailable, Bridge-offline, verification, and
      persistence states.
- [ ] Reuse the same validation/persistence service for Bridge and manual
      Cookie sources so they cannot drift.
- [ ] Add audit events with actor, trigger, account ID, Profile key hash,
      browser family/source, connector state, effective settings, and terminal
      result, excluding all secrets.

## Tests

Standard tests use fakes and temporary Profiles:

- browser precedence and invalid explicit executable;
- feature disabled means no connector/extension/API/UI activation;
- feature disabled returns 404 for the unmounted route;
- non-loopback peer, spoofed forwarding header, LAN-address, reverse-proxy,
  missing-Origin, and wrong-Origin handshake rejection before protocol state;
- pairing token expiry/replay and wrong origin/client/Profile;
- two concurrent account sessions with reversed response order;
- timeout/cancel/browser close at every state;
- connector and service restart/reconnect;
- late response after finalization;
- platform validation failure and prior Cookie preservation;
- transaction rollback between validation and persistence;
- repeated finalization and lock release;
- manual Cookie path parity and QR non-regression;
- tripwire proving standard tests never reach a real browser, connector, or
  platform even with production-like environment variables.

Opt-in real-browser tests prove Chrome and Edge extension registration and
synthetic roundtrip. Real platform login belongs only to an explicit local
pilot and must not expose evidence secrets.

## Exit Criteria

- A local user can choose browser auto-sync, log into the visible managed
  browser, and see the exact account verified/saved without copying Cookie.
- Two accounts remain isolated under concurrency, restart, and reversed order.
- QR and advanced manual Cookie paths retain their existing behavior.
- The accepted subprocess-Cookie security path has current evidence and no
  ambiguous or hidden risk ownership remains.
- Disabling the flag removes the new runtime path without deleting data.
- Targeted, full regression, docs, syntax, whitespace, and independent diff
  review checks pass.

## Rollback

Disable the flag, stop connector/extension launch, and retain readable additive
metadata, Profiles, and last verified Cookies. Revoke binding credentials only
for explicit reset or compromise. Schema deletion is not the first rollback.

Stop Packet C if loopback/Origin/reverse-proxy enforcement fails, raw Cookie
argv disposition is absent or expired, or implementation would silently widen
the runner/MediaCrawler secret boundary.
