# CookieBridge Pairing And Compatibility Spike Packet

> Future read-only/disposable spike. It does not modify product code, schema,
> UI, deployment, account records, or durable Profiles.

**Goal:** Determine whether supported Chrome and Edge can automatically load a
project-managed extension and complete an authenticated, exact-client Cookie
roundtrip suitable for a later local browser auto-sync feature.

## Start Gates

- [ ] Phase 5.1P, Phase 5.1A-D, and Phase 5.1 acceptance are verified.
- [x] Proposed CR-112 is registered as `Needs Confirmation`.
      This checked item records documentation intake only and is not
      implementation approval.
- [ ] CR-112 is accepted and an explicit sequencing decision relative to
      CR-070 permits Packet B to start.
- [ ] The temporary third-party source is classified as evaluation-only.
- [ ] Disposable browser/connector tests are explicitly allowed and use test
      Profiles with no real account Cookies.

## Scope

Allowed:

- read-only inspection of the temporary reference extension/server;
- disposable Python 3.12 reference-server process for protocol observation;
- generated test-only compatible extension/connector prototypes under ignored
  temporary paths;
- Chrome and Edge test Profiles with synthetic platform Cookie fixtures.

Excluded:

- copying reference source into the product;
- real account login or real Cookie retrieval;
- product API, database, UI, Docker, or deployment edits;
- remote Bridge or headless production claims.

## Tasks

- [ ] Record protocol observations: WebSocket endpoint, origin behavior,
      registration fields, `client_id` persistence, Cookie request/response,
      cache lifetime, disconnect/reconnect, and implicit client selection.
- [ ] Compare every observed protocol field and trust boundary with the master
      pairing contract. When the reference protocol lacks token pairing,
      authenticated origin, exact binding, or request correlation, record the
      gap as a project-owned implementation requirement rather than weakening
      the master contract.
- [ ] Record license and Python runtime evidence and choose the proposed product
      route: written permission or project-owned compatible implementation.
- [ ] Build a disposable protocol harness that can assert four independent
      milestones: Service Worker present, socket connected, exact client
      authenticated/registered, exact account-scoped Cookie roundtrip complete.
- [ ] Prototype generated `bridge_config.json` injection into an ephemeral
      unpacked extension directory loaded only into a managed test Profile.
- [ ] Prove a stable extension origin can be allowlisted.
- [ ] Prove the WebSocket handler derives locality only from its ASGI socket
      peer, accepts literal `127.0.0.1`/`::1`, and rejects empty,
      unparsable, or non-loopback peers before WebSocket acceptance.
- [ ] Prove spoofed `X-Forwarded-For`, `Forwarded`, and similar headers cannot
      authorize a non-loopback peer, and prove only the exact stable
      `chrome-extension://<extension-id>` Origin is accepted.
- [ ] Prototype the single-use pairing exchange: token hash/TTL, atomic consume,
      replay rejection, binding credential issuance, Profile-local credential
      storage, reconnect, rotation, and revocation.
- [ ] Bind the prototype connector to `127.0.0.1` and reject non-loopback URLs.
- [ ] Prove feature-disabled startup leaves the connector route unmounted with
      404, and prove LAN-address and reverse-proxy WebSocket upgrades fail
      before session/client/pairing or Cookie protocol state.
- [ ] Run synthetic tests for Chrome and Edge on a clean temporary Profile.
- [ ] Test two simultaneous Profiles and prove exact routing with reversed
      registration order; no first/newest/only-client fallback is allowed.
- [ ] Test connector restart, browser restart, malformed frame, stale client,
      wrong platform, wrong origin, expired token, replayed token, late response,
      and cancellation cleanup.
- [ ] Record what a clean Windows computer needs: browser executable, extension
      artifact from the standard monitor installation, writable Profile/runtime
      paths, effective monitor loopback port, and health diagnostics. The V1
      product connector is an in-process Python 3.11 FastAPI module, not a
      separate binary or Python 3.12 runtime.
- [ ] Produce `docs/cookiebridge-compatibility-spike-result.md` with PASS/FAIL
      per milestone and proof limits.

## Exit Criteria

- Chrome and Edge each prove all four milestones, not only extension loading.
- Direct loopback with the exact extension Origin is the only accepted network
  path; LAN, reverse-proxy, spoofed-forwarding-header, and wrong/missing-Origin
  probes fail before protocol state.
- Pairing routes the exact managed Profile to one account session without user
  selection or implicit client choice.
- Reconnect and revocation semantics are demonstrated with synthetic data.
- The product implementation/distribution/runtime route is explicit.
- Any material divergence from the unauthenticated reference protocol is
  mapped to an explicit project-owned implementation and test requirement;
  Packet C never assumes the reference can provide the master pairing contract.
- Clean-computer bootstrap requires no manual extension or Chrome Profile setup.
- A read-only independent review finds no protocol, isolation, or proof gap.

## Stop Conditions

- Extension loading is blocked by supported browser policy.
- Registration cannot be authenticated and correlated automatically.
- Locality or Origin enforcement depends on client URL text, forwarded headers,
  or reverse-proxy implication instead of verified socket/origin evidence.
- Multi-Profile routing depends on timing, nickname, newest client, or operator
  selection.
- The product route still depends on restricted source, the Python 3.12
  reference server, or a second undeclared service lifecycle.
- Any test touches a real platform account or emits Cookie material.

A stopped spike leaves QR and manual Cookie behavior unchanged and keeps
Packet C closed.
