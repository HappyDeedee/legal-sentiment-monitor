# CookieBridge Pairing And Compatibility Spike Packet

> Accepted, dependency-gated read-only/disposable spike. It does not modify
> product code, schema, UI, deployment, account records, or durable Profiles.
> Mark it `In Progress` only after all start gates below pass.

**Goal:** Determine whether supported Chrome and Edge can automatically load a
project-managed extension and complete an authenticated, exact-client Cookie
roundtrip suitable for a later local browser auto-sync feature.

## Start Gates

- [x] Phase 5.1P and Phase 5.1A-D plus their current merged regression fixes
      are verified. The separate Linux/server-like real acceptance remains
      operator-gated and this spike does not claim to close it.
- [x] CR-112 is `Accepted / Dependency-Gated` and executes before CR-070.
- [x] The latest-main scoped Windows provider/preflight gate passed on
      2026-07-21: Compose config, persisted Chrome selection, 12-check isolated
      server-like validation/cleanup, and `234` focused provider/login/crawl
      tests passed. This is local-only evidence and does not close CR-047.
- [ ] The complete 2026-07-21 CR-112 decision, governance, specialist, and
      Packet B/C/D plan set is committed atomically on this branch.
- [x] The temporary third-party source is classified as evaluation-only.
- [x] Disposable browser/connector tests are explicitly allowed and use test
      Profiles with no real account Cookies.

## Scope

Allowed:

- read-only inspection of the temporary reference extension/server;
- disposable Python 3.12 reference-server process for protocol observation;
- direct-reuse black-box evaluation, bounded minimal adapters, and independent
  test-only replacement prototypes under ignored temporary paths;
- Chrome and Edge test Profiles with synthetic platform Cookie fixtures.

Excluded:

- copying reference source into the product;
- real account login or real Cookie retrieval;
- product API, database, UI, Docker, or deployment edits;
- remote Bridge or headless production claims.

## Tasks

- [ ] Record protocol observations: WebSocket endpoint, origin behavior,
      registration fields, `client_id` persistence, Cookie request/response,
      cache lifetime, disconnect/reconnect, implicit client selection, Cookie
      field fidelity, duplicate domain/path names, partitioned-cookie behavior,
      and frame/record limits.
- [ ] Compare every observed protocol field and trust boundary with the master
      pairing contract. When the reference protocol lacks token pairing,
      authenticated origin, exact binding, or request correlation, record the
      gap as an explicit minimal-adaptation or single-component-replacement
      requirement rather than weakening the master contract.
- [ ] Record license, distribution, and Python runtime evidence. For Extension,
      Connector, and protocol separately, classify the result as `direct
      reuse`, `minimal adaptation`, or `single-component replacement`; do not
      decide ownership before measurement.
- [ ] Build a disposable protocol harness that can assert four independent
      milestones: Service Worker present, socket connected, exact client
      authenticated/registered, exact account-scoped Cookie roundtrip complete.
- [ ] Define and test structured Cookie Protocol V1: versioned records,
      required/optional attributes, platform domain allowlist, tuple uniqueness,
      unsupported-attribute behavior, and bounded record/per-record/frame size.
      Do not flatten Bridge output to a Cookie-header string.
- [ ] Prototype generated `bridge_config.json` injection into an ephemeral
      unpacked extension directory loaded only into a managed test Profile.
      Treat this as a candidate bootstrap mechanism, not a committed product
      choice, until cleanup/restart evidence passes.
- [ ] Prove packaged manifest-key material produces one stable extension ID and
      allowlisted Origin across Chrome, Edge, ephemeral copies, project paths
      with spaces, and clean computers. Keep only exact supported-platform and
      loopback host permissions; reject `<all_urls>` or unrelated host access.
      The result document selects the exact product artifact path; the public
      manifest `key` is versioned with that artifact, while any private signing
      material is excluded from the repository and installation logs.
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
- [ ] Prove feature-disabled startup leaves the connector route unmounted:
      normal HTTP probe returns 404 and the pinned packaged runtime rejects an
      unmatched WebSocket upgrade with 403 before acceptance. Prove LAN-address
      and reverse-proxy WebSocket upgrades fail before session/client/pairing or
      Cookie protocol state.
- [ ] Record the tested dependency baseline: FastAPI `0.110.2` and Uvicorn
      `0.29.0` exact pins plus Starlette `0.37.2` from `uv.lock`. Treat exact
      status as a regression assertion; any dependency upgrade must re-audit
      it, while route absence/zero protocol state remains the security rule.
- [ ] Run synthetic tests for Chrome and Edge on a clean temporary Profile.
- [ ] After the exact synthetic Cookie roundtrip, inject the fixture into the
      same managed temporary persistent Profile, restart the browser, and prove
      the Profile retains the fixture and exposes it through the same managed
      browser context.
- [ ] Close the browser, delete the ephemeral session extension/config copy,
      reopen the Profile without Bridge load arguments, and prove the Profile
      remains login-usable with no missing-extension dependency or connector
      reconnect. If this bootstrap design fails, select and prove a different
      browser-bound token delivery mechanism before Packet C.
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
      per milestone, proof limits, and this component matrix:

      | Component | Reference evidence | Contract gaps | License/runtime fit | Decision | Packet C owner |
      | --- | --- | --- | --- | --- | --- |
      | Extension | measured | measured | measured | direct reuse / minimal adaptation / single-component replacement | selected by evidence |
      | Connector | measured | measured | measured | direct reuse / minimal adaptation / single-component replacement | selected by evidence |
      | Protocol | measured | measured | measured | direct reuse / minimal adaptation / single-component replacement | selected by evidence |

## Exit Criteria

- Chrome and Edge each prove all four milestones, not only extension loading.
- The fourth roundtrip milestone includes restart reuse of the managed
  temporary persistent Profile. Managed crawler argv proof remains owned by
  Packet C and Packet D.
- Direct loopback with the exact extension Origin is the only accepted network
  path; LAN, reverse-proxy, spoofed-forwarding-header, and wrong/missing-Origin
  probes fail before protocol state.
- Pairing routes the exact managed Profile to one account session without user
  selection or implicit client choice.
- Reconnect and revocation semantics are demonstrated with synthetic data.
- The implementation/distribution/runtime route and ownership of each
  Extension, Connector, and protocol component are explicit and evidence-based.
- The extension ID is stable, permissions are least-privilege, and the selected
  bootstrap/cleanup mechanism leaves the promoted Profile crawler-usable after
  its session extension/config is gone.
- The result fixes the Chrome/Edge-supported Cookie Protocol V1 fields and
  limits and shows that domain/path/security attributes survive the synthetic
  roundtrip and Profile restart.
- Any material divergence from the unauthenticated reference protocol is
  mapped to an explicit adaptation/replacement implementation and test requirement;
  Packet C never assumes the reference can provide the master pairing contract.
- Clean-computer bootstrap requires no manual extension or Chrome Profile setup.
- A read-only independent review finds no protocol, isolation, component-
  ownership, or proof gap.

## Stop Conditions

- Extension loading is blocked by supported browser policy.
- Extension identity changes across supported browser/installation paths,
  permissions require unrelated hosts, or session-extension cleanup leaves the
  persistent Profile dependent on a deleted path.
- Registration cannot be authenticated and correlated automatically.
- Locality or Origin enforcement depends on client URL text, forwarded headers,
  or reverse-proxy implication instead of verified socket/origin evidence.
- Multi-Profile routing depends on timing, nickname, newest client, or operator
  selection.
- The product route still depends on restricted source, the Python 3.12
  reference server, or a second undeclared service lifecycle.
- Any test touches a real platform account or emits Cookie material.
- Structured Cookie scope/security attributes cannot be preserved, unrelated
  domains cannot be rejected, or supported-browser limits remain undefined.

A stopped spike leaves QR and manual Cookie behavior unchanged and keeps
Packet C closed.
