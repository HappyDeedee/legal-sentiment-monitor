# Local Browser Auto-Sync Login Packet

> Accepted, dependency-gated implementation packet. Start only after Packet B
> passes and selects the component reuse/adaptation/ownership matrix. `Accepted`
> is not `In Progress` or `Verified`.

**Goal:** Add a default-off local browser login flow that automatically
acquires and verifies Cookie material for the exact account while preserving
existing QR and advanced manual Cookie behavior.

## Start Gates

- [x] Phase 5.1P and Phase 5.1A-D plus current merged regression fixes are
      verified. The separate CR-047 Linux/server-like real acceptance remains
      operator-gated and is not claimed by this same-machine Windows packet.
- [ ] Packet B passes Chrome and Edge authenticated roundtrip tests.
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
- [ ] The Packet C migration, compatibility, rollback, and process-inspection
      plan for removing current `runner.py --cookies` use is approved.

## Planned Touch Surface

Expected new focused modules:

- `api/monitoring/cookie_bridge.py`: authenticated connector client boundary;
- `api/monitoring/cookie_material.py`: Bridge/manual canonical Cookie records,
  platform allowlists, validation, and injection boundary;
- `api/monitoring/profile_promotion.py`: fixed-active-path candidate journal,
  swap, rollback, restart recovery, and cleanup;
- a feature-gated FastAPI WebSocket route backed by that module in the existing
  Python 3.11 monitor process;
- `api/monitoring/login_browser_sync.py`: session state machine/finalizer;
- Packet-B-selected extension and connector artifacts/directories;
- focused unit/integration tests for provider, connector, and login sessions.

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

- `cookie_source` (`bridge` or `manual`);
- `profile_runtime_version` and `profile_ready_at` on the account;
- durable `account_profile_promotions` journal state and recovery result;
- connector binding ID and Profile-local `client_id` identifier;
- login-session/promotion IDs, credential hash/version,
  `pending|active|revoked` status, bind/revoke timestamps, and last
  authenticated time;
- last connector health/status without Cookie values;
- browser-sync session identity, actor, trigger source, terminal result, and
  effective browser/Profile/provider summary.

Store raw Cookies only through the existing encrypted account mechanism. Store
only pairing/credential hashes server-side. Standard account APIs expose status
and timestamps, not Cookie, token, credential, raw Profile path, proxy
credential, CDP endpoint, or extension internals. The one exception is a
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

Bridge uses structured Cookie Protocol V1. Advanced manual strings are parsed
into the same canonical internal record model after the UI boundary. Packet B
must fix supported Chrome/Edge fields and limits before this packet starts.

## Tasks

### C.1 - Shared Cookie-To-Profile Service

- [ ] Add backward-compatible schema reads and the accepted account fields,
      promotion journal, session linkage, indexes, and recovery queries.
- [ ] Reuse `create_draft_social_account`; every operation has a real account
      ID and `profile_key` before filesystem or browser work.
- [ ] Implement the fixed-active-path protocol from `ACCOUNT_ENVIRONMENT.md`:
      same-volume candidate/rollback directories, durable checkpoints, closed
      handles, candidate validation, swap, active-path recheck, database commit,
      rollback, restart recovery, bounded cleanup, and `recovery_required`.
- [ ] Initialize every candidate fresh from the locked Phase 5.1 provider
      inputs. Leave the previous active Profile and its extension credential
      storage untouched before `swapping`; never clone either into the
      candidate.
- [ ] Hold the account/Profile lock for the complete operation. At/after
      `swapping`, cancellation becomes a request that finalizes only after safe
      commit or rollback.
- [ ] Implement canonical Cookie records and platform-domain allowlists.
      Bridge structured payloads and advanced manual strings enter the same
      validator/injector after parsing; unsupported security/scope attributes
      fail closed.
- [ ] Reuse the Phase 5.1 provider result for candidate and active-path checks;
      do not add another browser/Profile/proxy resolver.
- [ ] Preserve the previous fixed active Profile, encrypted Cookie, and account
      row on every pre-commit failure. A new-account failure remains draft.
- [ ] Before active-path recheck, remove one-time pairing/config material and
      launch without Bridge injection/session-extension arguments. Reject a
      candidate that depends on a deleted temporary extension path.
- [ ] Recover non-terminal journals before account check, login, reset, export,
      or crawl, and emit only opaque IDs/redacted categories.
- [ ] Keep advanced manual Cookie usable through C.1 without mounting any
      connector route or loading an extension.

### C.2 - Bridge Acquisition

- [ ] Add default-off configuration and leave the connector route unmounted.
      Require HTTP probe 404 and the packaged runtime's unmatched WebSocket
      pre-accept rejection (403 on the pinned Starlette/Uvicorn baseline).
- [ ] Limit `MONITOR_COOKIE_BRIDGE_ENABLED` reads to C.2 router inclusion,
      C.2 UI/capability/readiness, and C.2 extension/pairing launch. C.1
      validator/promotion/recovery/manual modules and every C.3 path must import
      and execute with the flag false.
- [ ] Enforce locality from the ASGI socket peer using a literal loopback IP
      check; reject empty/unparsable/non-loopback peers before WebSocket
      acceptance and ignore forwarded headers for authorization.
- [ ] Require the exact stable `chrome-extension://<extension-id>` Origin and
      reject missing, opaque, or unexpected Origins before protocol state.
- [ ] Keep `/api/monitor/cookie-bridge/` out of every remotely reachable
      reverse proxy and add LAN/proxy negative acceptance probes.
- [ ] Keep connector startup/shutdown/readiness in the monitor FastAPI
      lifecycle; do not introduce Python 3.12 or a second product service.
- [ ] Implement exact authentication, structured Cookie Protocol V1, request
      correlation, timeout, cancellation, reconnect, revocation, and
      no-implicit-client selection.
- [ ] Give a Bridge candidate one exact session/promotion-scoped pending
      binding. Bridge commit activates it and revokes the predecessor; manual
      commit creates no candidate binding and revokes the predecessor;
      rollback revokes the candidate and preserves the predecessor.
- [ ] Use a packaged manifest key to keep the extension ID/Origin stable across
      Chrome, Edge, ephemeral copies, and clean computers. Request only exact
      supported-platform/loopback permissions and exclude `<all_urls>`.
- [ ] Implement the browser-sync state machine and centralized finalizer. Open
      the visible managed candidate automatically and update status without
      manual refresh.
- [ ] Add authenticated start/status/cancel APIs and UI actions in this order:
      QR default, browser auto-sync, collapsed advanced manual Cookie. Bridge
      failure does not auto-open manual input.
- [ ] Add an administrator-only Cookie reveal POST endpoint for one exact
      `social_account`. Keep standard account responses masked; require the
      normal monitor authorization dependency; return 403 to normal users and
      `no-store`/`no-cache` headers on success and error responses.
- [ ] Add the masked Cookie field, eye reveal/hide button, copy button, and copy
      feedback to the administrator account form. Fetch only after explicit
      reveal, keep the value out of browser persistent Storage and URLs, and
      clear transient value/DOM state on close, navigation, account switch, and
      timeout. Normal-user markup has no reveal or copy control.
- [ ] Add customer-safe states for timeout, browser closed, extension
      unavailable, Bridge offline, validation, promotion, rollback, and
      `recovery_required`.

### C.3 - Profile-Only Runner Migration

- [ ] Add one internal profile-only CLI/config contract while keeping
      customer-visible login types `qrcode|cookie`. In CR-112 V1 this internal
      mode replaces managed `login_type=cookie` child execution only; existing
      QR/Profile execution remains regression-protected.
- [ ] In `_build_crawler_cmd`, keep `--lt cookie`, add hidden
      `--monitor_profile_only true`, and omit `--cookies`. In
      `_build_crawler_env`, pass the exact provider-resolved Profile/browser/
      proxy settings plus account ID, `profile_key`, promotion ID, and runtime
      version; pass no Cookie in argv or environment.
- [ ] In `cmd_arg/arg.py`, accept the hidden flag only with `--lt cookie`,
      reject explicit `--cookies`, clear inherited/default `config.COOKIES`, and
      validate required provider/account metadata before crawler creation.
- [ ] Parent preflight requires `profile_runtime_version >= 1`, committed
      promotion state, exact provider Profile, lock ownership, and valid login.
      The child repeats a lightweight login-state check before crawl.
- [ ] On child check failure, return typed `requires_relogin` before invoking
      QR/Cookie/phone login code. Reject CDP standard/generic Profile fallback,
      empty/stale Cookie injection, provider mismatch, and default network.
- [ ] Add internal `ProfileLoginRequired`; map it in `main.py` to reserved exit
      code `42`, and map only that code in `runner.py` to a redacted account/run
      `requires_relogin` result. Other child failures keep their existing error
      classification.
- [ ] Migrate every usable `login_type=cookie` account through C.1. Accounts
      that cannot be validated are marked `requires_relogin`; they never retain
      a hidden argv fallback after C.3 activation.
- [ ] Execute C.3 as a maintenance cutover: pause scheduler/new manual runs,
      reach zero runnable version-0 Cookie accounts, activate the new command
      builder/child guards, and resume. Thereafter version 1 always uses
      profile-only and version 0 is rejected before child spawn.
- [ ] Remove raw Cookie from managed crawler argv and environment and prove the
      effective process command through process inspection.
- [ ] Make Bridge feature-off affect C.2 only. C.1 advanced manual Cookie and
      accepted C.3 profile-only runs remain usable; feature-off never restores
      `runner.py --cookies`.
- [ ] Add audit events with actor, trigger, account ID, Profile key hash,
      promotion/binding IDs, provider summary, effective settings, recovery
      action, and terminal result, excluding secrets and raw paths.

## Tests

Standard tests use fakes and temporary Profiles:

- browser precedence and invalid explicit executable;
- feature disabled means no connector/extension/API/UI activation;
- feature-disabled HTTP probe returns 404 and unmatched WebSocket upgrade gets
  the packaged-runtime pre-accept rejection (403 on the pinned baseline);
- non-loopback peer, spoofed forwarding header, LAN-address, reverse-proxy,
  missing-Origin, and wrong-Origin handshake rejection before protocol state;
- pairing token expiry/replay and wrong origin/client/Profile;
- stable extension ID across Chrome/Edge/ephemeral copy/clean install, least-
  privilege permissions, and no stale extension-path dependency after cleanup;
- pending/active/revoked binding rotation for Bridge commit, manual commit, and
  rollback;
- two concurrent account sessions with reversed response order;
- timeout/cancel/browser close at every state;
- connector and service restart/reconnect;
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
- Bridge-off matrix proving manual Cookie and profile-only runner remain active
  without raw argv, including import/execution tests showing C.1/C.3 never read
  the Bridge flag;
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
- Administrators can explicitly reveal and copy the complete selected-account
  Cookie from a default-masked field; normal users have no entry and receive
  HTTP 403, and secret-leakage checks pass.
- Bridge and manual Cookie acquisition initialize or refresh the same
  account-bound persistent Profile used by later crawler runs.
- Process inspection proves managed crawler child argv contains no raw Cookie.
- Disabling the Bridge flag removes C.2 only; C.1 and accepted C.3 remain
  functional and raw Cookie argv stays retired.
- Promotion recovery has no ambiguous dual-active state and every operation is
  committed, rolled back, failed, or `recovery_required` with bounded cleanup.
- Targeted, full regression, docs, syntax, whitespace, and independent diff
  review checks pass.

## Rollback

Disable the Bridge flag to stop C.2 connector/extension/UI while retaining C.1
advanced manual Cookie, C.3 profile-only execution, additive metadata, the
fixed active Profile, and the last verified Cookie. Normal promotion still
rotates predecessor/candidate bindings according to commit or rollback;
outside that lifecycle, bulk revocation is reserved for explicit reset,
account deletion, or compromise. Schema deletion is not the first rollback,
and accepted rollback never restores raw Cookie argv.

Stop Packet C if loopback/Origin/reverse-proxy enforcement fails, a failed
refresh can damage the previous active Profile, raw Cookie remains in managed
crawler child argv, or implementation silently widens the runner/MediaCrawler
secret boundary. Also stop if journal recovery is ambiguous, internal
profile-only mode can enter login fallback, structured Cookie scope is lossy,
or Bridge-off breaks C.1/C.3.
