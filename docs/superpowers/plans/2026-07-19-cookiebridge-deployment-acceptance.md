# CookieBridge Deployment And Acceptance Packet

> Future acceptance packet. It validates the local feature on clean computers
> and protects the server-first QR baseline. It does not promote local browser
> evidence into production proof.

**Goal:** Prove repeatable installation, browser selection, failure isolation,
rollback, and QR non-regression across supported environments.

## Start Gates

- [ ] Packet C implementation and fake/integration tests pass.
- [ ] Distribution artifacts and runtime ownership are fixed and documented.
- [ ] No real secret, Profile, Cookie, local database, or deployment-only
      configuration is included in artifacts.

## Clean-Computer Contract

The supported Windows installer/startup path must:

- detect a valid explicit browser, then Chrome, then Edge, then Chromium;
- report the selected executable/family/source without raw sensitive paths in
  customer-facing UI;
- include the project-owned extension in the standard monitor installation and
  generate its ephemeral session copy automatically;
- create writable application-managed Profile and ephemeral runtime paths;
- bind the connector to `127.0.0.1` and diagnose port conflicts;
- authorize connections from the server-side socket peer only, ignore
  forwarded headers for locality, and require the exact stable extension
  Origin before WebSocket acceptance;
- mount/health-check the in-process connector route only when the feature flag
  is enabled;
- require no Google account, Chrome personal Profile, extension-store action,
  developer mode toggle, or manual Cookie copy/paste;
- preserve QR and advanced manual Cookie use when the feature is disabled.
- leave the connector route unmounted with 404 when disabled and deny
  `/api/monitor/cookie-bridge/` in remotely reachable reverse proxies.

Acceptance must start from a clean Windows computer with the documented Python
3.11 monitor runtime and Chrome or Edge. Beyond the standard monitor
installation, the operator performs no extension/connector file placement and
installs no Python 3.12 runtime or separate connector service.

## Acceptance Matrix

- [ ] Windows with Chrome and Edge: explicit path first; otherwise Chrome.
- [ ] Windows with Edge only: Edge selected and full synthetic roundtrip passes.
- [ ] Windows with supported Chromium only: declared compatibility result,
      without silently claiming Chrome/Edge equivalence.
- [ ] Browser path, project path, and Profile path containing spaces and Chinese
      characters.
- [ ] Existing Profile lock, browser crash, connector crash, service restart,
      port conflict, stale credential, revoked Profile, and read-only install
      root with writable configured data directory.
- [ ] Two and more managed account Profiles, concurrent login attempts, and
      restart with no cross-account Cookie response.
- [ ] Feature disabled/unhealthy: no extension load and no implicit fallback.
- [ ] Direct loopback plus exact extension Origin succeeds; LAN-address,
      spoofed forwarded-header, reverse-proxy WebSocket upgrade, and
      missing/wrong-Origin probes fail before connector protocol state.
- [ ] Upgrade from a version without connector metadata and rollback to the
      previous version with QR/manual Cookie still usable.
- [ ] Standard pytest remains fake-only; real-browser tests require explicit
      opt-in and synthetic Cookies.
- [ ] Local pilot verifies one real platform account at a time with redacted
      evidence and explicit operator approval.
- [ ] Server-like QR login, SMS verification handling, Profile persistence,
      account checks, manual/scheduler runs, and crawler execution regressions.

## Headless And Production Decision

V1 production remains QR-first with the server-started browser and persisted
server Profile. The local browser auto-sync feature is disabled in production
configuration by default.

Headless extension evaluation reports independent milestones:

1. extension/service worker loaded;
2. authenticated connector registration;
3. exact synthetic Cookie roundtrip;
4. restart/reconnect and multi-Profile isolation.

A failure at any milestone records headless Bridge as unsupported for that
environment. It does not fail the local-desktop feature and does not change the
server QR acceptance path. Cross-host/remote Bridge remains outside this packet.
Headless Bridge failure therefore does not block V1 local-desktop acceptance or
existing server production use; it is reported as `unsupported` for the tested
environment.

## Observability And Proof Strength

Health output includes feature enabled state, in-process connector route state,
loopback endpoint, protocol version, browser family/source, extension version,
connected exact binding count, and last error category. It excludes Cookie,
token, credential, raw Profile path, proxy secret, and platform page content.

Proof labels:

- docs checks prove governance consistency only;
- fake tests prove state, isolation, and negative guarantees under controlled
  adapters;
- real-browser synthetic tests prove loading, registration, and protocol on
  that browser/host;
- local pilot proves one real login/account flow on that machine;
- server-like QR tests prove the protected production baseline;
- no local result by itself proves a different production host or future
  remote Bridge topology.

## Exit Criteria

- Clean Windows setup succeeds with Chrome-first and Edge fallback without
  manual Profile/extension setup.
- Failure, restart, concurrency, upgrade, and rollback matrices pass.
- Loopback peer, Origin, disabled-route 404, and reverse-proxy exclusion tests
  pass without trusting client-supplied forwarding headers.
- Server QR and existing manual Cookie behavior show no regression.
- Feature-off state has no connector/extension side effects.
- Documentation, installer/deployment examples, tests, and evidence agree.
- Independent read-only review finds no blocking or material acceptance gap.

## Stop And Rollback

Stop rollout on cross-account leakage, secret exposure, implicit fallback,
unreliable automatic extension loading, non-idempotent cleanup, or QR/crawler
regression. Disable the feature flag and connector route while retaining
Profiles and last verified Cookies for existing paths.

Also stop rollout when a LAN/proxy request reaches connector protocol state or
the accepted subprocess-Cookie risk decision is absent, expired, or contradicted
by process-inspection evidence.
