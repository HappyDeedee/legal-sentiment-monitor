# CR-129 Account Profile And Platform Request Identity Consistency

## Metadata

- CR: CR-129
- Type: Phase 5.1 follow-up regression fix; account-environment hardening;
  platform-request identity consistency
- Status: Accepted / In Progress (Packets A-D verified; Packet E next)
- Baseline: `main@6cffdbaf0c0ffca8863192c962918a37349f10a4`
- Branch: `codex/cr-129-request-identity-consistency`
- Owner: project implementation lane
- Review route: deep plan-cross-validation with Claude Code read-only tools

## Baseline And Problem

CR-112 and its verified follow-ups established an account-scoped Profile,
Cookie promotion, BrowserEnvironmentProvider, and saved-account checks. The
current runner now freezes a BrowserEnvironmentPlan for a run, but the actual
platform HTTP clients and signers still derive request inputs independently.
That leaves a second, implicit request-environment authority.

Observed and code-confirmed contradictions:

| Area | Current evidence | Risk | Required action |
| --- | --- | --- | --- |
| Browser/Profile | Provider returns a safe effective result, while clients receive mutable page/context values | Request identity can drift after resolution | Project one immutable request contract from effective proof |
| XHS | `core.py`, `client.py`, and `playwright_sign.py` independently read Cookie, UA, proxy, URL, and body | Signature input can differ from sent request | Freeze and validate all signer/client inputs |
| Douyin | Client reads page LocalStorage and generates request values while proxy and headers may refresh | `msToken`, `verifyFp`, UA, and `a_bogus` can belong to different states | Bind token, browser, proxy, signer, and final request to one attempt |
| Proxy | Proxy mixin can refresh an expired proxy during a request | Managed account silently changes network identity | Reject/classify drift; allow refresh only as a new verified revision |
| Retry | Client and runner have separate retry paths | A retry can select a different environment or repeat a terminal platform action | Bound retries to a frozen environment and typed errors |
| Persistence | Run summaries contain outcomes but not a safe request proof | Successful content lacks auditable identity evidence | Persist only safe revisions/digests and proof metadata |

## Goal

For every managed account crawl, establish one immutable, versioned request
environment derived from the effective browser provider proof. The XHS and
Douyin core/client/signer/request paths consume that environment and reject
missing, conflicting, stale, or cross-account values. A successful item is
accepted as authenticated only when platform-specific identity evidence also
passes.

## In Scope

- A versioned `PlatformRequestEnvironment` or the reviewed equivalent.
- Binding account, platform, `profile_key`, browser family/channel/version,
  proxy revision, identity revision, request resolution, attempt, run,
  locale, timezone, UA, Accept-Language, and Cookie-material revision.
- XHS signer/client/request consistency and identity checks.
- Douyin signer/client/request consistency and identity checks.
- Managed proxy drift, retry, cancellation, timeout, process exit, and
  service-restart terminal semantics.
- Safe cross-process handle validation and secret tripwires.
- Focused regression tests, affected-suite regression, documentation, and
  designated real acceptance.

## Out Of Scope

- Reimplementation of CookieBridge Extension, Connector, or WebSocket path.
- CR-070 account/Profile export package.
- CAPTCHA, SMS, human-verification, or platform challenge bypass.
- Anonymous collection, account rotation, dynamic proxy scheduling, or a new
  crawler framework.
- Direct transfer of a whole browser Profile between browser families or
  hosts.
- Use of protected accounts 9197 and 9198 for collection validation.

## Hard Boundaries

1. The committed Profile resolved by `social_account.profile_key` is the
   crawl and browser-login authority.
2. Encrypted Cookie is initialization, refresh, recovery, and migration
   material; it is not a second crawl authority.
3. BrowserEnvironmentProvider is the sole source for browser, Profile, UA,
   locale, timezone, window, and proxy environment resolution.
4. Platform clients and signers consume the frozen request environment and do
   not derive a second account environment from config, globals, defaults, or
   a different page.
5. A managed account never silently changes to anonymous mode, a generic
   Profile, another account, a default proxy, or a default network.
6. CR-070 remains after CR-112 and after this follow-up's verified boundary.
7. CR-112's same-machine Windows and reuse-first component decisions remain
   protected. This CR does not reopen Packet B component selection.

## Invariants

### Must Never Happen

- One crawl attempt sends a signature computed from a different Cookie, UA,
  URL, query, body, proxy, Profile, or token revision.
- One Profile is bound to two `social_account` records.
- A stale login callback or late child-process result overwrites a newer
  attempt or committed authority.
- Raw Cookie, Token, proxy credentials, or signature material appears in
  argv, environment variables, URLs, logs, audit details, or persisted safe
  snapshots.
- A terminal login, identity, challenge, rate-limit, signature, or proxy
  error is blindly retried as a generic network failure.
- Content without platform identity proof is reported as authenticated.

### Must Eventually Finalize

- Every attempt reaches a terminal result: success, failed, timeout,
  cancelled, interrupted, or a typed platform-action state.
- Every retry records a new attempt ID while inheriting the same verified
  environment revision unless a new resolution is explicitly performed.
- Every environment mismatch has a stable typed error and safe evidence.
- Failed, cancelled, timed-out, interrupted, and browser-closed operations
  retain the prior committed Profile and Cookie authority.
- A successful managed crawl records safe request-environment proof and
  platform identity proof.

## Dependencies And Gates

- Phase 5.1A-D, CR-114 through CR-128, and CR-112 Packet B/C/D are verified on
  the baseline main branch.
- CR-047 Linux/server-like proof remains operator-gated and is not replaced by
  local Windows evidence.
- CR-070 remains sequenced after CR-112 and this request-identity follow-up.
- Designated real acceptance IDs are Douyin `8972` and Xiaohongshu `9196`.
  Douyin `9197` and `9198` are protected and excluded from collection.
- The plan cannot enter implementation until deep review reports
  `Overall verdict=READY`, `Blocking findings=None`, and
  `Material refinements=None`.

## Authority And Data Contract

| Field group | Authority | Safe persisted representation |
| --- | --- | --- |
| account/platform/Profile | `social_accounts` plus provider plan | IDs, `profile_key`, platform |
| browser | effective provider proof | family, source, channel, version digest |
| proxy | account binding and provider result | proxy ID/policy/revision digest |
| identity | account identity revision and provider proof | revision and redacted summary |
| request | one frozen attempt environment | contract version, resolution/attempt/run IDs |
| Cookie/token | controlled memory or encrypted material reference | material revision, source, hash |
| signature | signer output for the frozen request | safe algorithm/version/result digest |

Raw secrets and Profile paths stay in the existing controlled runtime objects.
The external contract carries references, revisions, hashes, and redacted
proof only.

## Expected Touch Surface

Expected files, subject to review of the exact lifecycle:

- `tools/platform_request_environment.py` or an existing contract module;
- `api/monitoring/browser_environment_provider.py`;
- `tools/browser_environment.py`;
- `api/monitoring/runner.py`;
- `media_platform/xhs/core.py`, `media_platform/xhs/client.py`,
  `media_platform/xhs/playwright_sign.py`;
- `media_platform/douyin/core.py`, `media_platform/douyin/client.py`,
  `media_platform/douyin/help.py`;
- `proxy/proxy_mixin.py` and the relevant proxy helpers;
- additive persistence/serialization code only if safe proof storage needs it;
- focused and regression tests;
- CR-129 formal documents and packet records.

## Hard Implementation Gates

These gates define what each packet must establish; they do not claim that the
baseline already implements the new contract.

Before Packet A code:

- define and test the immutable request-contract shape, required fields,
  lifecycle, expiry, binding checks, safe handle format, and proof projection
  from `BrowserEnvironmentResult`;
- define the safe distinction between a Profile key, proxy revision, browser
  proof digest, Cookie-material revision, and raw in-memory value;
- define how a managed attempt rejects a missing provider result instead of
  falling back to a generic browser, Profile, proxy, or network.

Before Packet B/C code:

- Packet B must cover `xhs/client.py:_pre_headers()`,
  `xhs/playwright_sign.py:sign_with_xhshow()` and `_build_sign_string()`, the XHS
  `request()` transport, and
  `xhs/core.py` preparation as one frozen input contract;
- Packet C must cover `douyin/client.py:_pre_headers()`,
  `douyin/help.py:get_a_bogus()`, `douyin/help.py:get_web_id()`, the Douyin
  request transport, and `douyin/core.py` page evidence as one frozen input
  contract;
- deterministic RED/GREEN tests must prove old Cookie, UA, token, URL/query,
  body, or proxy paired with a new request is rejected before dispatch.

Before Packet D child-process work:

- deterministic tripwires must prove synthetic child argv/environment/result
  files contain no Cookie value, token, proxy password, Profile path, CDP
  endpoint, or raw signature material;
- the safe handle must carry only versioned IDs, revisions, hashes, and
  Profile-only launch metadata needed by the child.

Before Packet E real acceptance:

- temporary-Profile tests must pass service restart, manual/scheduled trigger,
  proxy revision stability, retry attempt binding, terminal-state, and
  fallback-proof checks;
- only then may designated Douyin `8972` and Xiaohongshu `9196` be touched.

Secret-leak stop condition: if a test, log, audit record, snapshot, or child
inspection exposes a Cookie value, token, proxy password, Profile path, CDP
endpoint, or raw signature material, stop the packet, quarantine the evidence,
remove it from tracked artifacts, and redesign the safe handle before resuming.

## Atomic Packets

### Packet A - PlatformRequestEnvironment

Project a request contract only from a verified `BrowserEnvironmentResult`.
Make it immutable, versioned, attempt-bound, expiration-bound, and safe to
serialize. Validate every required binding before a Client is constructed.
Add RED tests for absent fields, conflicting revisions, cross-account Profile,
expired contracts, and secret leakage.

Packet A makes safe request proof mandatory for every post-CR-129 platform
attempt. At minimum the proof records contract version, workspace/account/
platform/Profile identifiers, browser family/source/channel/version digest,
proxy ID/policy/revision, identity revision, Cookie-material revision,
resolution/attempt/run IDs, locale/timezone/UA/language, creation/expiry,
`fallback_used`, and redacted signer/request digests. Raw paths, URLs with
credentials, Cookie/token values, proxy credentials, and complete headers are
excluded. Historical pre-CR-129 runs may remain limited-context and must not be
retrofit with guessed proof.

Packet A implementation receipt (2026-07-22): `Verified`. The immutable
contract, safe parent binding, child proof write/read path, attempt ordering
guard, managed proxy freeze, XHS signed-header snapshot, and Douyin managed
Profile token gate are implemented in code. Focused Packet A coverage passes
`19`; the affected governed selection passes `228`; the complete monitoring
regression passes `715` with three existing warnings. Python compile, docs
consistency, documentation regression, and `git diff --check` pass. The final
focused Claude read-only review reported no P0/P1 findings; its two P2 notes
were documentation-only and were corrected. Full child argv/environment/log
tripwires and typed terminal error taxonomy remain explicit Packet D gates.

Exit gate: contract tests pass; no platform call occurs for invalid contracts;
existing pre-CR-129 account setup remains compatible.

### Packet B - Xiaohongshu Request Identity

Route Cookie, `a1`, `web_session`, UA, UA-CH, Accept-Language, URL, query,
body, signer input/output, HTTP headers, Profile, and proxy through the frozen
contract. Prove the Cookie and signer inputs match the actual request. Classify
identity failure and preserve the committed Profile.

Exit gate: focused XHS RED/GREEN tests, identity proof tests, retry/lock tests,
and affected monitoring regression pass.

Packet B implementation receipt (2026-07-22): `Verified`. Managed XHS Core
builds one frozen request identity from Provider-effective account/Profile,
Cookie, required `a1`/`web_session`, UA/UA-CH, Accept-Language, and proxy
values. `_pre_headers()`, `sign_with_xhshow()` / `_build_sign_string()`, and
the final httpx URL/body use byte-identical copied inputs; target, body, Cookie,
UA, proxy, revision, or expiry drift stops before dispatch. Safe signed request
proof is atomic, monotonic, and bounded to request 1 plus the latest 31; Runner
requires a bound signed 2xx proof before XHS ingest. Focused coverage passes
`33`, the affected monitoring selection passes `12`, and full monitoring
passes `696` with three existing warnings. The complete suite passes `747`
with one documented pre-existing XHS Store assertion outside this packet.
Python compile and `git diff --check` pass. Claude focused re-review returned
`PASS` with no blocker or material refinement. No real platform traffic was
used; Packet C is next.

### Packet C - Douyin Request Identity

Route Cookie, User-Agent, UA-CH, `webid`, `verifyFp`, `msToken`, `ttwid`,
`a_bogus`, page/local-storage evidence, URL/query/body, Profile, and proxy
through one frozen attempt. Remove unbound fixed or cross-account values and
reject drift before platform dispatch.

Exit gate: focused Douyin identity/signature tests, account isolation, retry,
and affected monitoring regression pass.

Packet C implementation receipt (2026-07-22): `Verified`. The request contract
is v2 with provider-effective window/device fields. Managed Douyin Core captures
`xmst`, the Profile web ID, `s_v_web_id`, and `ttwid` once from the verified
Profile and freezes them as `msToken`, `webid`, `verifyFp/fp`, and `ttwid`.
Cookie, UA/UA-CH, screen, browser version/channel, proxy, signer input,
`a_bogus`, and final URL are one immutable request. Fixed/random/cross-account
values, per-request Page reads, and in-flight Cookie/proxy refresh fail before
HTTP. Runner requires a bound signed 2xx Douyin proof. Focused tests pass `48`,
full monitoring passes `696`, and the complete suite passes `767` with the same
pre-existing XHS Store assertion. The designated `8972` Profile-construction
diagnostic confirms all required material exists and safe projection excludes
raw values; it performs no content collection. Independent focused review is
`PASS`. The current Client has no POST call sites, so managed POST remains
fail-closed until body-aware signer proof exists. Packet D is next.

### Packet D - Error, Retry, And Process Boundary

Use typed categories for login required, second verification, challenge,
rate-limit, proxy block, signature mismatch, invalid Cookie, environment or
account identity mismatch, transient network, protocol change, timeout,
cancel, and process crash. Only bounded transient-network retries are
automatic. Child processes receive a versioned safe handle or Profile-only
launch information, with tripwire tests for argv/environment/logs/snapshots.

Proxy expiry, proxy revision drift, proxy region mismatch, and proxy block are
terminal managed-environment errors (`proxy_expired`, `proxy_revision_mismatch`,
`proxy_region_mismatch`, `proxy_blocked`) and require a new explicit
resolution. They do not refresh the proxy inside an in-flight attempt.
Explicit transport reset/refusal may retry within the configured count and
deadline; timeout remains terminal. Each retry gets a new `attempt_id`, inherits the same
`resolution_id` and verified environment revision, records its retry ordinal,
and stops at the budget or any terminal platform error.

Exit gate: terminal-state, stale-callback, cancellation, restart, crash,
retry, and leakage tests pass.

Packet D implementation receipt (2026-07-22): `Verified`. The child terminal
contract covers all 14 categories, binds exact account/Profile/run/revision
state, and is consumed once by the parent. Only `transient_network` retries;
each retry has a new attempt ID and unchanged resolution/identity/Cookie/proxy
revisions. The parent rejects missing, stale, cross-attempt, or conflicting
terminal evidence. Windows cleanup terminates the complete child process tree.
Managed stdout is redacted before disk write, with final sanitizer and
argv/environment/result tripwires as defense in depth. Dedicated tests pass
`84`; complete monitoring passes `704`; the repository-wide run reports `817`
passed with only six local-Redis dependency failures and the documented
pre-existing XHS Excel factory assertion. The initial review findings were
fixed or resolved with call-chain evidence; focused re-review returned `PASS`,
no remaining P0/P1/P2, and atomic readiness `YES`. Packet E is next.

### Packet E - Compatibility And Real Acceptance

Preserve QR, browser auto-sync, manual Cookie, saved Profile checks, Profile
restart, manual runs, scheduled Runner, server-like paths, and normal monitor
collection. A same-family browser version update keeps `profile_key` and does
not itself require login; a family/channel change uses a candidate Profile,
Cookie validation, identity check, then promotion. Execute the designated
Douyin and XHS real lanes serially.

Exit gate: each platform proves identity and persists at least one real item,
`fallback_used=false`, no secret leakage, restart check passes, and protected
accounts remain unused.

## Test Matrix

| Area | Synthetic proof | Real proof |
| --- | --- | --- |
| contract binding | account/Profile/browser/proxy/revision mismatch RED tests | designated snapshot evidence |
| XHS signer/request | frozen Cookie/UA/URL/query/body/proxy equality | ID `9196`, identity endpoint and saved item |
| Douyin signer/request | frozen token/UA/query/body/proxy equality | ID `8972`, identity endpoint and saved item |
| account isolation | two-account concurrent fixtures | serial designated lanes |
| locks/retry | same-account lock and transient-only retry | bounded normal monitor run |
| lifecycle | cancel, timeout, crash, restart, stale callback | service restart and recheck |
| leakage | argv/env/log/audit/snapshot tripwires | child-process inspection |
| compatibility | QR/browser/Cookie/Profile fixtures | normal monitor entry |

Automatic tests use temporary Profiles, synthetic Cookie, synthetic proxy,
fake browser/provider, and a real-platform blocking tripwire. Real acceptance
uses explicit designated IDs only; no account discovery, random pool choice,
anonymous route, default Profile, or default network.

## Real Acceptance Matrix

1. Validate the designated account's committed Profile and Cookie material.
2. Establish one frozen request environment and prove exact platform identity.
3. Run the normal monitor collection path, not a diagnostic or anonymous path.
4. Persist at least one non-empty Douyin item for `8972` and one non-empty
   Xiaohongshu item for `9196`.
5. Record `fallback_used=false` and safe environment/identity proof.
6. Inspect child-process arguments and environment for secret absence.
7. Restart the service; recheck both Profiles and run a bounded minimum crawl.
8. Confirm no data or request crossed into accounts `9197` or `9198`.

## Rollback And Recovery

- Each packet is one atomic commit and can be reverted independently.
- Invalid candidate environments are discarded before committed Profile/Cookie
  promotion.
- Existing committed Profile, encrypted Cookie, source, identity, and locks
  remain the recovery authority after failed or interrupted operations.
- Additive schema changes require a reversible migration and a tested old-code
  read path; no destructive field removal is part of this CR.
- If two root-cause attempts expose another independent authority, stop the
  packet, update this plan, and run focused re-review before continuing.

## Stop Conditions

- Any protected account is selected or touched by a real collection.
- A test reaches a real platform without an explicit designated gate.
- A request environment field is missing, contradictory, expired, or derived
  from a second authority.
- A terminal platform-action error is retried as transient network.
- Secret tripwire, identity proof, or fallback proof fails.
- The same symptom survives two root-cause fixes without new evidence.
- Claude review has a blocker or material refinement that is not incorporated.

## Documentation Sync

After registration and after every packet, synchronize:

- `docs/CHANGE_REQUESTS.md`
- `docs/TASKS.md`
- `docs/CURRENT_STATE.md`
- `docs/DECISIONS.md`
- `docs/ACCOUNT_ENVIRONMENT.md`
- `docs/DATA_MODEL.md`
- `docs/SCHEMA_MIGRATION.md`
- `docs/PRODUCT_REQUIREMENTS.md`
- `docs/SERVER_DEPLOYMENT.md`
- `docs/TEST_PLAN.md`
- `docs/TEST_RESULTS.md`
- `docs/TRACEABILITY.md`
- this packet plan

Use `Proposed`, `Queued`, `Accepted`, `In Progress`, and `Verified` precisely;
do not mark a packet Verified before its code and evidence exist.

## PR And Merge Conditions

- Focused tests, affected/full regression, compile, JavaScript checks, docs
  consistency, documentation tests, and `git diff --check` pass.
- Independent read-only full-diff review passes with no unresolved P0/P1/P2.
- Designated real acceptance evidence is documented without secrets.
- PR is created from the CR-129 branch, merged, and verified after merge.
- Local `main` equals `origin/main`, primary worktree is clean, and only
  already-merged safe worktrees are removed.

## TODO Baseline Classification

| Item | Classification | Action in CR-129 |
| --- | --- | --- |
| CR-112 | already completed / historical within V1 boundary | protect decision and reuse evidence |
| CR-119..CR-128 | already completed / historical Verified | do not reopen; add regression links only |
| CR-047 server-like identity fidelity | operator-gated | retain as separate gate |
| CR-070 | future-valid | keep after CR-112 and CR-129 |
| CR-092..CR-094 | future-valid or Needs Confirmation | leave outside this implementation |
| request identity split | active/current follow-up | execute CR-129 packets A-E |

## Review Ledger

The deep review ledger is maintained during plan validation. Each round records
round number, finding, severity, evidence, action, status, affected files, new
tests, and documentation update. Temporary raw review output stays under
`.codex_tmp`; only durable decisions and results enter formal project docs.

### Round 1 - Claude deep review

- B1/B2: the plan named the authority split but did not state the exact
  contract gate or mutable signer entry points. Action: added Hard
  Implementation Gates and explicit XHS/Douyin entry points. Status: fixed in
  plan; implementation remains Packet A-C work.
- B3: proxy refresh classification was implicit. Action: added terminal proxy
  revision/expiry/region categories and new-resolution rule. Status: fixed.
- B4: retry inheritance was underspecified. Action: added new-attempt/same-
  resolution/revision/ordinal rule. Status: fixed.
- B5: safe proof persistence was optional in the first draft. Action: made
  post-CR-129 safe proof mandatory and historical rows limited-context. Status:
  fixed.
- B6: safe handle exclusions were not explicit enough. Action: added child
  tripwires and excluded Profile paths/CDP endpoints/proxy credentials/raw
  signatures. Status: fixed.
- Review verdict: BLOCKED because the first draft omitted these material
  execution gates. Focused Round 2 must verify only these revisions and any
  directly affected baseline/table inconsistency.

### Round 2 - Claude focused re-review

- Verdict: `READY`.
- Blocking findings: `None`.
- Material refinements: `None`.
- B1/B2: exact immutable-contract gate and XHS/Douyin signer/Core/transport
  entry points confirmed.
- B3: terminal proxy expiry/revision/region/block categories and explicit new
  resolution confirmed.
- B4: new attempt ID with inherited resolution/environment revision and retry
  ordinal confirmed.
- B5: mandatory post-CR-129 safe proof and limited-context historical rows
  confirmed.
- B6: child argv/environment/result/log/audit/snapshot tripwires and secret
  stop condition confirmed.
- TODO baseline, formal documents, protected CR-112 boundary, CR-070 order,
  designated IDs, and implementation readiness were all found consistent.

### Round 3 - Packet A implementation review

- The first implementation review returned `PASS AFTER MATERIAL
  REFINEMENTS`, identifying proxy refresh drift, stale proof ordering, missing
  safe-channel tripwires, and minimal XHS/Douyin input guards.
- Packet A addressed the in-scope findings with managed proxy-refresh
  rejection, monotonic attempt-proof merging, safe binding/proof tripwires,
  immutable XHS signed headers, managed Douyin `msToken` presence validation,
  and concurrent account projection coverage.
- Packet D child-process argv/environment/log tripwires, Packet B/C complete
  signer/request equality, and typed retry taxonomy remain intentionally
  deferred to their named packets under the hard implementation gates.
- Focused Round 2 returned `PASS AFTER SMALL FIXES`, with no P0/P1 findings and
  two documentation-only P2 notes. The notes were corrected in the Douyin CDP
  docstring and XHS signer docstring. Packet A is permitted to commit.
