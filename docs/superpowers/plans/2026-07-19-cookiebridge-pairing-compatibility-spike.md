# CookieBridge Compatibility And Acquisition Spike Packet

> Verified on 2026-07-21. Product code, schema, UI, deployment, real account
> records, and durable Profiles remain unchanged by this disposable packet.

**Goal:** Measure the reference CookieBridge Extension, Connector, and protocol
against the accepted CR-112 contract, then select an evidence-backed
acquisition path that works with supported Chrome and Edge.

## Start Gates

- [x] Phase 5.1P, Phase 5.1A-D, and the current merged regression fixes are
      verified within their documented proof boundaries.
- [x] CR-112 Packet B is `Accepted / Verified`, executes before CR-070, and the
      latest-main scoped Windows provider gate passed.
- [x] The synchronized CR-112 plan was committed atomically as `44baf78`.
- [x] The third-party source is evaluation-only, and all tests use temporary
      Profiles plus synthetic Cookie records.

## Allowed Work

- read-only reference source inspection and disposable black-box execution;
- installed Chrome and Edge with isolated temporary Profiles;
- independent test-only adapters under ignored temporary paths;
- structured Cookie fidelity, restart, isolation, bounded-size, and cleanup
  tests;
- feature-disabled route probes on the pinned packaged runtime.

Excluded work remains product code/schema/UI/deployment changes, real account
login, real Cookie retrieval, durable Profile mutation, and remote or
production claims.

## Completed Measurements

- [x] Recorded reference endpoint, Origin handling, registration fields,
      client selection, cache/lifecycle, Cookie response shape, duplicate
      scope behavior, license, distribution, and Python runtime.
- [x] Tested reference Extension loading on current branded Chrome and Edge,
      including an Edge copy under a path containing spaces and Chinese
      characters.
- [x] Proved an Edge reference roundtrip reaches one correlated response while
      also proving that it has no pairing token/Profile claim and flattens
      scoped Cookie records.
- [x] Proved current Chrome does not load the unpacked reference Extension
      through the command-line switch, so Extension direct reuse cannot meet
      the supported-browser contract.
- [x] Proved the reference manifest has no stable key and its unpacked
      Extension ID changes with installation path.
- [x] Proved direct Playwright/CDP acquisition from an exact managed persistent
      context on Chrome and Edge preserves domain/path/host-only/HttpOnly/
      Secure/SameSite attributes and distinct same-name path tuples.
- [x] Proved two concurrent temporary Profiles remain isolated and each
      survives browser/Profile restart without any Extension Service Worker.
- [x] Fixed structured Cookie Protocol V1 at `256` records, `8192` serialized
      bytes per record, and `1048576` serialized bytes per acquisition. Six
      fail-closed negative cases pass; unsupported `partition_key` is rejected.
- [x] Confirmed the feature-disabled pinned runtime returns HTTP `404` and
      unmatched WebSocket upgrade `403`. The selected V1 path adds no product
      WebSocket route.
- [x] Removed generated test Profiles after browser close and verified no test
      used a real account, Cookie, platform request, or product Profile.
- [x] Produced `docs/cookiebridge-compatibility-spike-result.md` with exact
      evidence, limits, proof boundaries, and the component matrix.

## Component Selection

| Component | Decision | Packet C implementation owner |
| --- | --- | --- |
| Extension | `single-component replacement` | Existing managed Playwright/CDP browser context |
| Connector | `single-component replacement` | In-process account-bound acquisition service with no WebSocket route |
| Protocol | `minimal adaptation` | Internal structured Cookie Protocol V1 from Playwright Cookie records |

The direct path binds to the browser context that the parent operation created
for one locked `social_account_id`, `profile_key`, and `login_session_id`. It
does not discover or select clients and therefore removes the reference
pairing, Origin, loopback, extension-ID, and reconnect trust boundaries.

## Packet C Contract Change

- C.2 owns direct managed-browser Cookie acquisition, start/status/cancel APIs,
  and the browser auto-sync UI. It does not package an Extension or mount a
  Cookie-bridge WebSocket route.
- C.1 remains the shared canonical validator, fresh candidate injector,
  identity checker, encrypted store, promotion/recovery service, and advanced
  manual Cookie path.
- C.3 remains the profile-only child migration and raw-Cookie argv/environment
  retirement.
- Exact account/session/Profile binding, failure preservation, administrator
  reveal/copy security, QR/manual/server regressions, and Packet D real
  acceptance remain unchanged.
- The Packet B evidence and synchronized implementation boundary are complete.
  Packet C may start after the Packet B result is committed atomically.

## Exit Criteria

- The reference behavior and its distribution/runtime/security/fidelity gaps
  are recorded without copying third-party source into product paths.
- Chrome and Edge both pass the selected direct acquisition, structured
  fidelity, restart, two-Profile isolation, and cleanup tests.
- The component matrix assigns one explicit evidence-backed decision and one
  Packet C owner to Extension, Connector, and protocol.
- Packet C/D and formal CR-112 documents describe the selected direct path and
  contain no active requirement to package the rejected reference Extension or
  Connector.
- Documentation, whitespace, and independent acceptance gates pass.

## Stop Conditions

- direct acquisition cannot be bound to the exact application-created browser
  context and account/session lock;
- Chrome or Edge loses required Cookie scope/security attributes, restart
  persistence, or Profile isolation;
- product behavior retains an implicit/default browser, Profile, client,
  account, Cookie, or network fallback;
- any test touches real account material or leaves a generated temporary
  Profile behind;
- the implementation would require restricted reference source, manual
  Extension installation, a separate Connector, or Python 3.12.
