# CookieBridge Deployment And Acceptance Packet

> Accepted, dependency-gated acceptance packet. It validates the same-machine
> Windows feature on clean computers and with designated real accounts while
> protecting the server-first QR baseline. It does not promote local browser
> evidence into production proof.

**Goal:** Prove repeatable installation, browser selection, failure isolation,
rollback, and QR non-regression across supported environments.

## Start Gates

- [ ] Packet C implementation and fake/integration tests pass.
- [ ] Distribution artifacts and runtime ownership are fixed and documented.
- [ ] No real secret, Profile, Cookie, local database, or deployment-only
      configuration is included in artifacts.
- [ ] `DESIGNATED_DY_ACCOUNT_ID` and `DESIGNATED_XHS_ACCOUNT_ID` name two
      explicit administrator-approved project-managed accounts in the
      acceptance deployment. Missing, wrong-platform, shared, or ambiguous IDs
      stop real acceptance before Cookie acquisition.

## Clean-Computer Contract

The supported Windows installer/startup path must:

- detect a valid explicit browser, then Chrome, then Edge, then Chromium;
- report the selected executable/family/source without raw sensitive paths in
  customer-facing UI;
- include the Packet-B-selected extension in the standard monitor installation and
  generate its ephemeral session copy automatically;
- preserve one packaged manifest-key-derived extension ID/Origin across Chrome,
  Edge, ephemeral copies, and clean computers, with no `<all_urls>` or unrelated
  host permission;
- create writable application-managed Profile and ephemeral runtime paths;
- mount the connector route in the existing monitor service, connect through
  the loopback URL, diagnose port conflicts, and enforce locality from the
  server-side socket peer even when the service binds on `0.0.0.0`;
- authorize connections from the server-side socket peer only, ignore
  forwarded headers for locality, and require the exact stable extension
  Origin before WebSocket acceptance;
- mount/health-check the in-process connector route only when the feature flag
  is enabled;
- require no Google account, Chrome personal Profile, extension-store action,
  developer mode toggle, or manual Cookie copy/paste;
- preserve QR and advanced manual Cookie use when the feature is disabled.
- leave the connector route unmounted when disabled: normal HTTP probe returns
  404 and the pinned packaged runtime rejects unmatched WebSocket upgrade with
  403 before acceptance; deny `/api/monitor/cookie-bridge/` in remotely
  reachable reverse proxies.

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
- [ ] Service kill, disk full, open Profile handle, antivirus/permission error,
      and restart at every candidate/swap/recheck/commit/rollback checkpoint;
      each case restores the previous active Profile or enters deterministic
      `recovery_required` without deleting the only usable copy.
- [ ] Checkpoint-lag/operation-marker directory matrix and due cleanup on
      startup, periodic timer, first successful run, and pre-refresh; idle
      accounts reach the 24-hour cleanup attempt without scheduler activity.
- [ ] Two and more managed account Profiles, concurrent login attempts, and
      restart with no cross-account Cookie response.
- [ ] First Cookie login creates an account-bound persistent Profile; a later
      browser/service restart and crawler launch reuse it without raw Cookie in
      child argv.
- [ ] Session extension/config cleanup leaves the promoted Profile usable when
      reopened without Bridge load arguments and produces no reconnect from a
      deleted extension path.
- [ ] Failed Cookie refresh leaves the previous active Profile and verified
      encrypted Cookie usable.
- [ ] Bridge/manual commit and rollback produce the exact pending/active/revoked
      binding state and never let the rollback Profile reconnect with the
      promoted binding.
- [ ] Feature disabled/unhealthy: no extension load and no implicit fallback.
- [ ] C.1/C.2/C.3 rollback matrix: Bridge disabled unmounts only C.2;
      advanced manual Cookie remains usable through C.1; accepted profile-only
      execution remains active; raw Cookie argv is not restored.
- [ ] C.3 maintenance cutover pauses new runs, reaches zero runnable version-0
      Cookie accounts, proves hidden CLI/provider-env/exit-code wiring, resumes,
      and rejects any later version-0 account before child spawn.
- [ ] Direct loopback plus exact extension Origin succeeds; LAN-address,
      spoofed forwarded-header, reverse-proxy WebSocket upgrade, and
      missing/wrong-Origin probes fail before connector protocol state.
- [ ] Upgrade from a version without connector metadata. Binary downgrade is
      allowed only after every promotion journal is terminal and the target
      binary can preserve C.1/C.3 semantics; Bridge rollback otherwise disables
      C.2 only, with QR/manual Cookie still usable and no argv restoration.
- [ ] Standard pytest remains fake-only; real-browser tests require explicit
      opt-in and synthetic Cookies.
- [ ] Packaged dependency assertion records FastAPI `0.110.2`, Uvicorn
      `0.29.0`, and locked Starlette `0.37.2`; HTTP 404/WebSocket 403 are
      regression checks while route absence/zero protocol state are invariant.
- [ ] Local pilot verifies one real platform account at a time with redacted
      evidence and explicit operator approval.
- [ ] Real Douyin acceptance uses only `DESIGNATED_DY_ACCOUNT_ID`: acquire the
      current Cookie from its project-managed logged-in Profile through the
      Extension, prove the exact platform/account identity, reveal and copy it
      through the administrator UI, inject only that Cookie into a fresh
      candidate Profile, restart and verify identity, then use the normal
      monitor collection entry to persist at least one real content item.
- [ ] Real Xiaohongshu acceptance repeats the same serial workflow using only
      `DESIGNATED_XHS_ACCOUNT_ID` and persists at least one real content item.
- [ ] Fresh candidates copy no predecessor LocalStorage, cache, Service Worker,
      extension credential storage, or other Profile files. Only the Cookie
      acquired for the exact designated account is injected before validation.
- [ ] Both real crawls prove the designated account/Profile/provider/proxy
      authority, `fallback_used=false`, and no anonymous, generic Profile,
      other-account, task-proxy, process-default, or default-network fallback.
- [ ] Transient process inspection proves no plaintext Cookie in crawler child
      argv or environment. Committed evidence records only booleans, digests,
      timestamps, and internal IDs, never the Cookie or raw command line.
- [ ] After both platform checks, remove Extension session/config/cache
      material, restart the monitor service, revalidate each committed Profile,
      and complete one bounded minimal crawl per required platform without the
      Extension being present or connected.
- [ ] Kuaishou is `Deferred`; its absence or failed unexecuted matrix row does
      not fail this Packet D. It must not be reported as tested.
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
- The designated Douyin and Xiaohongshu accounts each complete Extension
  acquisition, exact-account validation, administrator reveal/copy, fresh
  candidate injection, Profile restart verification, and persistence of at
  least one real content item through the normal monitor entry.
- Both required platform runs show `fallback_used=false`; Kuaishou remains
  explicitly `Deferred` and is not counted as a failure.
- Cookie acquisition persists the exact account Profile across restart, and
  process inspection finds no raw Cookie in managed crawler child argv.
- Failure, restart, concurrency, upgrade, and rollback matrices pass.
- Promotion journal recovery leaves no ambiguous active Profile, unbounded
  candidate, or database/Profile disagreement.
- Loopback peer, Origin, disabled HTTP 404/WebSocket 403 baseline, and reverse-
  proxy exclusion tests pass without trusting client-supplied forwarding
  headers.
- Server QR and existing manual Cookie behavior show no regression.
- Feature-off state has no connector/extension side effects.
- Documentation, installer/deployment examples, tests, and evidence agree.
- Independent read-only review finds no blocking or material acceptance gap.

## Real Acceptance Evidence Boundary

Real acceptance runs serially: Douyin first, then Xiaohongshu. Before each run,
resolve the designated environment variable to one exact account row and prove
the platform matches. The normal monitor account lock covers acquisition,
candidate injection, validation, promotion, restart check, and bounded crawl.
No account discovery, first-account selection, or fallback is accepted.

The administrator reveal/copy check is observed in the frontend but evidence
contains only `reveal_succeeded`, `copy_succeeded`, account ID, actor ID,
timestamp, and response-header booleans. Screenshots, console output, HAR files,
traces, logs, and audit details must not contain the Cookie. The intentional OS
clipboard copy is cleared by the acceptance operator after observation and is
not persisted by the product.

## Stop And Rollback

Stop rollout on cross-account leakage, secret exposure, implicit fallback,
unreliable automatic extension loading, non-idempotent cleanup, or QR/crawler
regression. Disable the feature flag and connector route while retaining
Profiles and last verified Cookies for existing paths. Feature-off rollback
affects C.2 only after Packet C acceptance; it preserves C.1 manual
Cookie-to-Profile and C.3 profile-only runner behavior.

Also stop rollout when a LAN/proxy request reaches connector protocol state, a
failed refresh damages the previous active Profile, or process inspection finds
raw Cookie in managed crawler child argv.
