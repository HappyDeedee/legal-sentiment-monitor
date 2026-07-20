# Browser Cookie Sync Deployment And Acceptance Packet

> Accepted, dependency-gated acceptance packet. It validates the same-machine
> Windows feature on clean computers and with designated real accounts while
> protecting the server-first QR baseline. Local browser evidence is not
> production proof.

**Goal:** Prove repeatable installation, browser selection, exact managed-
context Cookie acquisition, failure isolation, rollback, real collection, and
QR non-regression across supported environments.

## Start Gates

- [x] Packet C implementation and fake/integration tests pass.
- [x] Distribution artifacts and runtime ownership are fixed and documented.
- [x] No real secret, Profile, Cookie, local database, or deployment-only
      configuration is included in artifacts.
- [ ] `DESIGNATED_DY_ACCOUNT_ID` and `DESIGNATED_XHS_ACCOUNT_ID` name two
      explicit administrator-approved project-managed accounts in the
      acceptance deployment. Missing, wrong-platform, shared, or ambiguous IDs
      stop real acceptance before Cookie acquisition.

## 2026-07-21 Live Gate Status

Packet D is `In Progress / External-Gated`, not verified.

- `DESIGNATED_DY_ACCOUNT_ID=5809` resolves one exact project-managed Douyin
  account whose existing Profile passed identity/login checks before and after
  the bounded attempt.
- The direct managed-browser process used a managed user-data directory and no
  Cookie argument. The session timed out because platform login was not
  completed in the visible browser; its failed candidate was cleaned and the
  previous active Profile remained authoritative.
- The deployment contains no Xiaohongshu account, so
  `DESIGNATED_XHS_ACCOUNT_ID` cannot resolve and the mandatory second-platform
  workflow has not started.
- No real Cookie capture, reveal/copy, promotion, `fallback_used=false` crawl,
  or persisted real content item is claimed by this attempt.

Resume after an approved project-managed Xiaohongshu account exists and the
operator can complete the designated Douyin login in the visible browser.

## Clean-Computer Contract

The supported Windows installer/startup path must:

- detect a valid explicit browser, then Chrome, then Edge, then supported
  Chromium, then the declared Playwright Chromium repair path;
- report selected browser family/source without exposing sensitive raw paths in
  customer-facing UI;
- create writable application-managed Profile and operation paths;
- use the existing project Playwright/CDP runtime to retain the exact browser
  context created for one locked account/session;
- require no Google account, Chrome personal Profile, Extension installation,
  browser developer-mode action, Connector service, Python 3.12 runtime, or
  manual Cookie copy/paste;
- leave `/api/monitor/cookie-bridge/` unmounted in both feature states; normal
  HTTP returns 404 and unmatched WebSocket upgrade returns the pinned-runtime
  pre-accept rejection 403;
- preserve QR and advanced manual Cookie use when browser sync is disabled.

Acceptance starts from a clean Windows computer with the documented Python
3.11 monitor runtime and Chrome or Edge. The operator performs no Extension or
Connector placement beyond the standard monitor installation.

## Acceptance Matrix

- [ ] Windows with Chrome and Edge: explicit path first; otherwise Chrome.
- [ ] Windows with Edge only: Edge selected and full synthetic direct
      acquisition passes.
- [ ] Windows with supported Chromium only: declared compatibility result,
      without silently claiming Chrome/Edge equivalence.
- [ ] Browser, project, Profile, and data paths containing spaces and Chinese
      characters.
- [ ] Existing Profile lock, browser crash, service restart, stale session
      generation, closed context, and read-only install root with writable
      configured data directory.
- [ ] Service kill, disk full, open Profile handle, antivirus/permission error,
      and restart at every candidate/swap/recheck/commit/rollback checkpoint;
      each case restores the previous active Profile or enters deterministic
      `recovery_required` without deleting the only usable copy.
- [ ] Checkpoint-lag/operation-marker directory matrix and due cleanup on
      startup, periodic timer, first successful run, and pre-refresh; idle
      accounts reach the 24-hour cleanup attempt without scheduler activity.
- [ ] Two and more managed account Profiles, concurrent login attempts,
      reversed completion order, and restart with no cross-account Cookie
      result.
- [ ] First Cookie login creates an account-bound persistent Profile; a later
      browser/service restart and crawler launch reuse it without raw Cookie in
      child argv or environment.
- [ ] Failed Cookie refresh leaves the previous active Profile and verified
      encrypted Cookie usable.
- [ ] Browser-sync/manual commit and rollback commit one verified candidate or
      restore the predecessor without ambiguous dual-active state.
- [ ] Feature disabled/unhealthy: no acquisition browser launch and no implicit
      browser/Profile/account/Cookie/network fallback.
- [ ] C.1/C.2/C.3 rollback matrix: browser sync disabled removes only C.2;
      advanced manual Cookie remains usable through C.1; accepted profile-only
      execution remains active; raw Cookie argv is not restored.
- [ ] C.3 maintenance cutover pauses new runs, reaches zero runnable version-0
      Cookie accounts, proves hidden CLI/provider-env/exit-code wiring, resumes,
      and rejects any later version-0 account before child spawn.
- [ ] Upgrade from a version without acquisition/promotion metadata. Binary
      downgrade is allowed only after every promotion journal is terminal and
      the target binary preserves accepted C.1/C.3 semantics.
- [ ] Standard pytest remains fake-only; real-browser tests require explicit
      opt-in and synthetic Cookies.
- [ ] Packaged dependency assertion records FastAPI `0.110.2`, Uvicorn
      `0.29.0`, and locked Starlette `0.37.2`; HTTP 404/WebSocket 403 are
      regression checks while route absence/zero protocol state are invariant.
- [ ] Local pilot verifies one real platform account at a time with redacted
      evidence and explicit designated account IDs.
- [ ] Real Douyin acceptance uses only `DESIGNATED_DY_ACCOUNT_ID`: acquire the
      current structured Cookie from its project-managed logged-in Profile
      through the selected exact-context service, prove platform/account
      identity, reveal and copy it through the administrator UI, inject only
      that Cookie into a fresh candidate, restart and verify identity, then use
      the normal monitor collection entry to persist at least one real item.
- [ ] Real Xiaohongshu acceptance repeats the same serial workflow using only
      `DESIGNATED_XHS_ACCOUNT_ID` and persists at least one real item.
- [ ] Fresh candidates copy no predecessor LocalStorage, cache, Service Worker,
      IndexedDB, or other Profile files. Only the structured Cookie acquired
      for the exact designated account is injected before validation.
- [ ] Both real crawls prove designated account/Profile/provider/proxy
      authority, `fallback_used=false`, and no anonymous, generic Profile,
      other-account, task-proxy, process-default, or default-network fallback.
- [ ] Transient process inspection proves no plaintext Cookie in crawler child
      argv or environment. Committed evidence records only booleans, digests,
      timestamps, and internal IDs, never Cookie or raw command lines.
- [ ] After both platform checks, close and clear temporary acquisition
      handles/state, restart the monitor service, revalidate each committed
      Profile, and complete one bounded minimal crawl per required platform
      without running browser auto-sync again.
- [x] Kuaishou is `Deferred`; its absence or unexecuted matrix row does not fail
      Packet D and must not be reported as tested.
- [ ] Server-like QR login, SMS verification handling, Profile persistence,
      account checks, manual/scheduler runs, and crawler execution regressions.

## Headless And Production Decision

V1 production remains QR-first with the server-started browser and persisted
server Profile. Local browser auto-sync is disabled in production by default.

Headless direct-acquisition observation uses independent milestones:

1. exact provider-selected context created;
2. exact account/Profile/session generation retained;
3. structured synthetic Cookie acquisition complete;
4. restart and multi-Profile isolation complete.

A failure at any milestone records headless direct acquisition as unsupported
for that environment. It does not fail the local-desktop feature or change the
server QR acceptance path. Cross-host Cookie transport remains outside V1.

## Observability And Proof Strength

Health output includes feature enabled state, provider readiness, protocol
version, browser family/source, active acquisition-session count, and last safe
error category. It excludes Cookie, raw Profile path, proxy secret, browser
endpoint, and platform page content.

Proof labels:

- docs checks prove governance consistency only;
- fake tests prove state, isolation, and negative guarantees under controlled
  adapters;
- real-browser synthetic tests prove exact-context acquisition and Cookie
  fidelity on that browser/host;
- local pilot proves the designated real account workflow on that machine;
- server-like QR tests prove the protected production baseline;
- no local result by itself proves a different production host or future
  cross-host topology.

## Exit Criteria

- Clean Windows setup succeeds with Chrome-first and Edge fallback without
  manual Profile or Extension setup.
- Designated Douyin and Xiaohongshu accounts each complete direct acquisition,
  exact-account validation, administrator reveal/copy, fresh candidate
  injection, Profile restart verification, and at least one persisted real
  content item through the normal monitor entry.
- Both required platform runs show `fallback_used=false`; Kuaishou remains
  `Deferred` and is not counted as a failure.
- Process inspection finds no raw Cookie in managed crawler child argv or
  environment.
- Failure, restart, concurrency, upgrade, rollback, and cleanup matrices pass.
- Promotion recovery leaves no ambiguous active Profile, unbounded candidate,
  or database/Profile disagreement.
- The rejected Cookie-bridge HTTP/WebSocket route remains absent.
- Server QR and existing manual Cookie behavior show no regression.
- Feature-off has no C.2 browser-acquisition side effect and does not disable
  C.1/C.3.
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
wrong context/session binding, non-idempotent cleanup, failed-refresh damage,
raw Cookie child argv/environment, or QR/crawler regression. Disable
`MONITOR_BROWSER_COOKIE_SYNC_ENABLED` while retaining committed Profiles and
last verified Cookies. Feature-off rollback affects C.2 only after Packet C
acceptance; it preserves C.1 manual Cookie-to-Profile and C.3 profile-only
runner behavior.
