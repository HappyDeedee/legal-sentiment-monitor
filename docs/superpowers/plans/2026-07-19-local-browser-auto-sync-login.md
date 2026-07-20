# Local Browser Auto-Sync Login Packet

> Packet B and C.1-C.3 are verified within their recorded proof boundaries.
> Packet D remains dependency-gated pending atomic C.3 delivery and designated
> real-account evidence.

**Goal:** Add a default-off local browser login flow that automatically
acquires and verifies Cookie material for the exact account while preserving
existing QR and advanced manual Cookie behavior.

## Start Gates

- [x] Phase 5.1P and Phase 5.1A-D plus current merged regression fixes are
      verified. The separate CR-047 Linux/server-like real acceptance remains
      operator-gated and is not claimed by this same-machine Windows packet.
- [x] Packet B result document and synchronized component matrix are committed
      as `Verified` in `1d7465c`.
- [x] CR-112 same-machine Windows scope is accepted. Packet B, rather than an
      upfront ownership assumption, selects direct reuse, minimal adaptation,
      or one focused replacement for each component.
- [x] CR-112-before-CR-070 sequencing is accepted.
- [x] Additive schema/migration, retention, and rollback rules are approved by
      the accepted CR-112 specialist documents, subject to Packet B limits.
- [x] Exact API/UI state machine and permission checks, including the narrow
      administrator Cookie reveal boundary, are documented.
- [x] The target raw-Cookie disposition is confirmed: prepare and validate the
      persistent Profile before crawler launch and pass no raw Cookie in child
      argv.
- [x] The Packet C migration, compatibility, rollback, and process-inspection
      plan for removing current `runner.py --cookies` use is approved.

## Planned Touch Surface

Expected new focused modules:

- `api/monitoring/browser_cookie_acquisition.py`: exact managed browser-context
  Cookie capture boundary;
- `api/monitoring/cookie_material.py`: auto-sync/manual canonical Cookie records,
  platform allowlists, validation, and injection boundary;
- `api/monitoring/profile_promotion.py`: fixed-active-path candidate journal,
  swap, rollback, restart recovery, and cleanup;
- `api/monitoring/login_browser_sync.py`: session state machine/finalizer;
- focused unit/integration tests for provider, managed browser acquisition,
  and login sessions.

Expected existing files:

- browser provider/runtime consumers established by Phase 5.1;
- `api/monitoring/database.py` and approved migrations;
- `api/monitoring/account_check.py` and `api/monitoring/runner.py`;
- `api/routers/monitor.py`;
- `cmd_arg/arg.py`, `config/base_config.py`, `main.py`, and platform
  launch/login callers needed for one internal profile-only mode and reserved
  relogin exit mapping;
- account login HTML/CSS/JavaScript only;
- administrator-only Cookie reveal response handling in transient page memory;
- configuration examples and specialist documentation.

Do not change Task Center, Run Detail, reports, email, AI, roles, crawler
provider architecture, dynamic account rotation, or dynamic proxy scheduling.

## Data Contract

Persist additive metadata only after migration approval:

- `cookie_source` (`browser_sync` or `manual`);
- `profile_runtime_version` and `profile_ready_at` on the account;
- durable `account_profile_promotions` journal state and recovery result;
- login-session/promotion IDs, session generation, and last acquisition status;
- browser-sync session identity, actor, trigger source, terminal result, and
  effective browser/Profile/provider summary.

Store raw Cookies only through the existing encrypted account mechanism.
Standard account APIs expose status and timestamps, not Cookie, raw Profile
path, proxy credential, CDP endpoint, or browser-context internals. The one exception is a
dedicated administrator-only POST reveal response for the selected account;
normal users receive HTTP 403.

The reveal response carries the complete decrypted Cookie only in the response
body, uses `Cache-Control: no-store, private`, `Pragma: no-cache`, no validator,
and is never embedded in URL/query text. The frontend keeps it only in
transient page memory, masks it by default, uses an eye control for display,
copies only on an explicit click with feedback, and clears it on account
change, drawer close, navigation, and timeout. Cookie material must not enter
localStorage, sessionStorage, IndexedDB, logs, audit details, diagnostics,
screenshots, subprocess arguments, or subprocess environment. Redacted access
audit may record actor/account/action/result without any Cookie body, fragment,
scope, or hash.

The persistent Profile resolved from `profile_key` is the normal browser
session and crawl environment for both QR and accepted Cookie login. Encrypted
Cookie material remains available for bootstrap, refresh, recovery, and
migration. It is not passed to managed crawler children through argv.

The fixed active path remains `resolve_account_profile_path(profile_key)`.
Candidate and rollback directories are internal same-volume operation
artifacts; no provider/crawler resolves them. The exact journal states,
swap/recheck/commit ordering, restart recovery, and bounded cleanup follow
`ACCOUNT_ENVIRONMENT.md`. Schema ownership follows `DATA_MODEL.md` and
`SCHEMA_MIGRATION.md`.

Browser acquisition and advanced manual strings use the same canonical
structured Cookie Protocol V1 after the UI boundary. Packet B fixed the
Chrome/Edge fields and limits before this packet starts.

## Tasks

### C.1 - Shared Cookie-To-Profile Service

- [x] Add backward-compatible schema reads and the accepted account fields,
      promotion journal, session linkage, indexes, and recovery queries.
- [x] Reuse `create_draft_social_account`; every operation has a real account
      ID and `profile_key` before filesystem or browser work.
- [x] Implement the fixed-active-path protocol from `ACCOUNT_ENVIRONMENT.md`:
      same-volume candidate/rollback directories, durable checkpoints, closed
      handles, candidate validation, swap, active-path recheck, database commit,
      rollback, restart recovery, bounded cleanup, and `recovery_required`.
- [x] Enforce the shared account-run/Profile-promotion exclusion contract,
      require a `256 MiB` storage reserve before candidate creation, and enqueue
      retained rollback cleanup after a successful managed run.
- [x] Initialize every candidate fresh from the locked Phase 5.1 provider
      inputs. Leave the previous active Profile and browser storage untouched
      before `swapping`; never clone either into the candidate.
- [x] Hold the account/Profile lock for the complete operation. At/after
      `swapping`, cancellation becomes a request that finalizes only after safe
      commit or rollback.
- [x] Implement canonical Cookie records and platform-domain allowlists.
      Browser-acquired structured payloads and advanced manual strings enter the same
      validator/injector after parsing; unsupported security/scope attributes
      fail closed.
- [x] Reuse the Phase 5.1 provider result for candidate and active-path checks;
      do not add another browser/Profile/proxy resolver.
- [x] Preserve the previous fixed active Profile, encrypted Cookie, and account
      row on every pre-commit failure. A new-account failure remains draft.
- [x] Before active-path recheck, close all acquisition handles and launch the
      fixed path without capture hooks or Cookie injection.
- [x] Recover non-terminal journals before account check, login, reset, export,
      or crawl, and emit only opaque IDs/redacted categories.
- [x] Keep advanced manual Cookie usable through C.1 without starting any
      managed browser acquisition.

C.1 verification is complete within the synthetic/local proof boundary: the additive migration,
canonical protocol, candidate/rollback journal, atomic account-run/Profile
exclusion, `256 MiB` storage reserve, marker-based restart recovery, cleanup
after a successful managed run, manual Cookie promotion, profile-authority
dispatch, and QR/manual regression checks pass. C.2 verification is complete
within its local proof boundary; C.3 is verified within its automated/local
proof boundary and Packet D remains governed by `TASKS.md`.

### C.2 - Managed Browser Acquisition

- [x] Add default-off `MONITOR_BROWSER_COOKIE_SYNC_ENABLED` configuration.
      Leave the rejected Cookie-bridge route absent in both feature states and
      retain HTTP 404/unmatched-WebSocket 403 regression probes.
- [x] Limit the feature-flag reads to C.2 router inclusion, C.2
      UI/capability/readiness, and C.2 managed-browser launch. C.1
      validator/promotion/recovery/manual modules and every C.3 path must import
      and execute with the flag false.
- [x] Create the acquisition session before browser launch and bind its exact
      account ID, `profile_key`, login session, promotion, provider resolution,
      attempt ID, actor, platform, and generation under the account/Profile
      lock.
- [x] Pass the live Playwright/CDP browser-context handle directly from the
      parent operation to the acquisition service. Reject caller-supplied raw
      Profile paths, default contexts, missing handles, closed handles, and any
      account/session/generation mismatch.
- [x] Capture structured Cookie records directly from that exact context,
      enforce Packet B limits and platform allowlists, reject late/stale results,
      and pass only the canonical payload to C.1.
- [x] Implement the browser-sync state machine and centralized finalizer. Open
      the visible managed candidate automatically and update status without
      manual refresh.
- [x] Add authenticated start/status/cancel APIs and UI actions in this order:
      QR default, browser auto-sync, collapsed advanced manual Cookie. Browser
      sync failure does not auto-open manual input.
- [x] Add an administrator-only Cookie reveal POST endpoint for one exact
      `social_account`. Keep standard account responses masked; require the
      normal monitor authorization dependency; return 403 to normal users and
      `no-store`/`no-cache` headers on success and error responses.
- [x] Add the masked Cookie field, eye reveal/hide button, copy button, and copy
      feedback to the administrator account form. Fetch only after explicit
      reveal, keep the value out of browser persistent Storage and URLs, and
      clear transient value/DOM state on close, navigation, account switch, and
      timeout. Normal-user markup has no reveal or copy control.
- [x] Add customer-safe states for timeout, browser closed, browser
      unavailable, stale session, validation, promotion, rollback, and
      `recovery_required`.

C.2 verification covers focused unit/API/permission/state/process tests,
adjacent Phase 5.1/login/crawl regressions, the complete monitor suite,
desktop/phone UI checks, and a controlled account-bound start/cancel run. The
controlled run preserved the previous active account/Profile, removed the
candidate, and left no Chromium process owned by the cancelled session.

### C.3 - Profile-Only Runner Migration

- [x] Add one internal profile-only CLI/config contract while keeping
      customer-visible login types `qrcode|cookie`. In CR-112 V1 this internal
      mode replaces managed `login_type=cookie` child execution only; existing
      QR/Profile execution remains regression-protected.
- [x] In `_build_crawler_cmd`, keep `--lt cookie`, add hidden
      `--monitor_profile_only true`, and omit `--cookies`. In
      `_build_crawler_env`, pass the exact provider-resolved Profile/browser/
      proxy settings plus account ID, `profile_key`, promotion ID, and runtime
      version; pass no Cookie in argv or environment.
- [x] In `cmd_arg/arg.py`, accept the hidden flag only with `--lt cookie`,
      reject explicit `--cookies`, clear inherited/default `config.COOKIES`, and
      validate required provider/account metadata before crawler creation.
- [x] Parent preflight requires `profile_runtime_version >= 1`, committed
      promotion state, exact provider Profile, lock ownership, and valid login.
      The child repeats a lightweight login-state check before crawl.
- [x] On child check failure, return typed `requires_relogin` before invoking
      QR/Cookie/phone login code. Reject CDP standard/generic Profile fallback,
      empty/stale Cookie injection, provider mismatch, and default network.
- [x] Add internal `ProfileLoginRequired`; map it in `main.py` to reserved exit
      code `42`, and map only that code in `runner.py` to a redacted account/run
      `requires_relogin` result. Other child failures keep their existing error
      classification.
- [x] Preserve committed version-1 `login_type=cookie` accounts. Accounts
      that cannot be validated are marked `requires_relogin`; they never retain
      a hidden argv fallback after C.3 activation.
- [x] Execute C.3 as a startup maintenance cutover before scheduler/manual runs,
      reach zero runnable version-0 Cookie accounts, activate the new command
      builder/child guards, and resume. Thereafter version 1 always uses
      profile-only and version 0 is rejected before child spawn.
- [x] Remove raw Cookie from managed crawler argv and environment and prove the
      effective process command/environment through fake-process inspection.
      Packet D retains real OS process inspection.
- [x] Make browser-sync feature-off affect C.2 only. C.1 advanced manual Cookie and
      accepted C.3 profile-only runs remain usable; feature-off never restores
      `runner.py --cookies`.
- [x] Add audit events with actor, trigger, account ID, Profile key hash,
      promotion/session IDs, provider summary, effective settings, recovery
      action, and terminal result, excluding secrets and raw paths.

## Tests

Standard tests use fakes and temporary Profiles:

- browser precedence and invalid explicit executable;
- feature disabled means no acquisition browser/API/UI activation;
- rejected Cookie-bridge HTTP probe returns 404 and unmatched WebSocket upgrade gets
  the packaged-runtime pre-accept rejection (403 on the pinned baseline);
- stale/replayed request, wrong account/Profile/session/generation, and missing
  or closed exact context handle;
- explicit tripwire proving no Cookie-bridge HTTP/WebSocket route is mounted;
- two concurrent account sessions with reversed response order;
- timeout/cancel/browser close at every state;
- browser and service restart/interruption;
- late response after finalization;
- platform validation failure and prior Cookie preservation;
- administrator Cookie reveal success, missing account handling, normal-user
  HTTP 403, `no-store`/`no-cache` headers, standard-response masking, explicit
  reveal/copy feedback, transient clearing, and absence from browser Storage,
  URL, logs, audit details, diagnostics, argv, and environment;
- failed refresh preserving the prior active Profile and restart-usable login;
- first Cookie login creating a persistent Profile that remains valid after
  service/browser restart;
- crash/kill at every journal checkpoint, including after each directory move
  and before/after the account/journal database transaction;
- disk full, open handles, antivirus/permission errors, same-volume checks,
  cleanup failure, contradictory directory evidence, and bounded quarantine;
- checkpoint-lag directory-shape recovery, operation-marker mismatch, periodic
  24-hour cleanup with no managed run, and pre-refresh cleanup retry;
- structured Cookie protocol version, domain/path tuple, domain allowlist,
  required attribute, duplicate, malformed, and bounded-size failures;
- profile-only missing/expired/invalid Profile and CDP fallback rejection;
- hidden profile-only CLI/env contract, explicit/default Cookie clearing,
  reserved exit-code mapping, version-1 routing, version-0 pre-spawn rejection,
  and maintenance-cutover interruption/resume;
- browser-sync-off matrix proving manual Cookie and profile-only runner remain active
  without raw argv, including import/execution tests showing C.1/C.3 never read
  the browser-sync flag;
- repeated finalization and lock release;
- manual Cookie path parity and QR non-regression;
- tripwire proving standard tests never reach a real browser or
  platform even with production-like environment variables.

Opt-in real-browser tests prove Chrome and Edge exact-context structured
acquisition, restart, and isolation. Real platform login belongs only to an
explicit local pilot and must not expose evidence secrets.

## Exit Criteria

- A local user can choose browser auto-sync, log into the visible managed
  browser, and see the exact account verified/saved without copying Cookie.
- Two accounts remain isolated under concurrency, restart, and reversed order.
- QR and advanced manual Cookie paths retain their existing behavior.
- Administrators can explicitly reveal and copy the complete selected-account
  Cookie from a default-masked field; normal users have no entry and receive
  HTTP 403, and secret-leakage checks pass.
- Browser-sync and manual Cookie acquisition initialize or refresh the same
  account-bound persistent Profile used by later crawler runs.
- Process inspection proves managed crawler child argv contains no raw Cookie.
- Disabling the browser-sync flag removes C.2 only; C.1 and accepted C.3 remain
  functional and raw Cookie argv stays retired.
- Promotion recovery has no ambiguous dual-active state and every operation is
  committed, rolled back, failed, or `recovery_required` with bounded cleanup.
- Targeted, full regression, docs, syntax, whitespace, and independent diff
  review checks pass.

## Rollback

Disable the browser-sync flag to stop C.2 acquisition/UI while retaining C.1
advanced manual Cookie, C.3 profile-only execution, additive metadata, the
fixed active Profile, and the last verified Cookie. Normal promotion still
commits one verified candidate or restores the predecessor. Schema deletion is
not the first rollback, and accepted rollback never restores raw Cookie argv.

Stop Packet C if exact browser-context/account/session binding fails, a failed
refresh can damage the previous active Profile, raw Cookie remains in managed
crawler child argv, or implementation silently widens the runner/MediaCrawler
secret boundary. Also stop if journal recovery is ambiguous, internal
profile-only mode can enter login fallback, structured Cookie scope is lossy,
or browser-sync-off breaks C.1/C.3.
