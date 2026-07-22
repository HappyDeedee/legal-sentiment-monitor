# CR-131 Managed Account End-to-End Transport Identity Consistency

Date: 2026-07-22

Owner: CR-131

Classification: Existing Feature Optimization

Status: Accepted / Ready for Implementation

Baseline: `main@a0a85834479ff6d7503b0a21f0a354a71d3c4d0b`

Planning branch: `codex/cr-131-managed-transport-identity-plan`

Review lane: deep architecture and external-side-effect review

## 1. Goal And Success Condition

Extend the verified CR-129 application-layer account binding through the
Python HTTP transport layer without using the native Chrome network stack for
batch collection.

The observable success condition is:

- login, Profile checks, Cookie refresh, account liveness checks, manual and
  scheduled collection, Runner retry/recovery, and service restart all consume
  one account authority resolved by `BrowserEnvironmentProvider`;
- every managed XHS or Douyin attempt owns one account-bound transport Session,
  Cookie Jar, connection pool, proxy revision, and versioned NetworkPersona;
- browser and managed-transport proofs independently match machine-readable
  allowed ranges and are semantically compatible;
- missing, stale, conflicting, or unsupported identity material stops before
  platform dispatch;
- no generic Profile, other account, ambient proxy, direct network, rolling
  fingerprint alias, or anonymous fallback is used;
- the committed Profile remains browser-login authority and failed candidate
  Cookie/Profile reconciliation preserves the previous committed authority.

This plan improves controllable consistency and auditability. It does not claim
that a platform cannot associate accounts by IP reputation, ASN, device/account
history, phone number, behavior, or other server-side signals.

## 2. Confirmed Product Boundaries

In scope:

- XHS and Douyin managed account paths introduced by CR-129;
- browser login, second verification, Profile validation, and credential
  refresh as the browser channel;
- Python API liveness checks and collection as the managed transport channel;
- TLS, JA3N, JA4, ALPN, HTTP/2, connection reuse, proxy/DNS, headers, Cookie,
  token, signature, retry, cancellation, crash, and restart consistency;
- synthetic validation, server-like validation, and explicitly gated designated
  account acceptance.

Out of scope:

- BrowserPageTransport for batch collection;
- Kuaishou and other platform-client transport migrations;
- account rotation, captcha/SMS bypass, dynamic proxy scheduling, or a
  high-concurrency crawler cluster;
- changing the committed-Profile or encrypted-Cookie authority defined by
  CR-112, CR-127, CR-128, and CR-129;
- promising absolute resistance to platform association;
- copying code from private or license-restricted reference repositories.

## 3. TODO Baseline Diff

| Label | Current-baseline evidence | Classification | Documentation action | Protected behavior | Readiness |
| --- | --- | --- | --- | --- | --- |
| CR-112 | Committed Profile and encrypted-Cookie promotion/recovery contracts | verified historical | keep historical | Profile is browser authority; encrypted Cookie is material | complete |
| CR-117 | browser selection and explicit channel migration rules | verified historical | keep historical | no silent browser-family migration | complete |
| CR-118 through CR-128 | login monotonicity, runtime proof, promotion, and recovery receipts | verified historical | keep historical | prior login and recovery guarantees remain intact | complete |
| CR-129 | frozen account/Profile/Cookie/UA/token/proxy/signature request environment and typed attempt result | verified historical predecessor | add follow-up CR-131 | do not reopen or weaken CR-129 | complete |
| Current HTTP clients | XHS and Douyin construct a fresh HTTPX client for request dispatch; account-check clients are not managed | current gap | own under CR-131 | signer/final-request byte identity remains | ready for CR-131 |
| CR-130 | Cookie form promotion regression fix | verified historical, unrelated | keep historical | UI promotion path remains unchanged | complete |
| CR-047 | Linux/server-like account identity acceptance | operator-gated | keep separate gate | local evidence does not replace server-like proof | operator-only |
| CR-070 | account environment export/import | future-valid | sequence after CR-131 | export only committed authority, never live Session state | future-only |
| Kuaishou and other HTTPX clients | no CR-129 managed-request contract | deferred | leave out of CR-131 | no implied transport guarantee | deferred |

Execution order is CR-129 Verified -> CR-131 -> fresh CR-070 baseline review.
CR-047 remains a separate operator-gated server-like acceptance lane and is not
silently closed by CR-131 synthetic or Windows evidence.

## 4. Architecture Decision

Adopt a hybrid architecture:

```text
BrowserEnvironmentProvider
  -> account/Profile/browser/proxy/persona resolution
  -> browser login, second verification, Profile check, credential refresh
  -> frozen PlatformRequestEnvironment + NetworkPersona
  -> attempt-bound ManagedImpersonationTransport
       -> pinned curl_cffi.AsyncSession
       -> account-only Cookie Jar and connection pool
       -> explicit proxy, DNS, TLS/H2 and header policy
  -> account liveness check and XHS/Douyin API collection
  -> isolated Set-Cookie candidate
  -> browser reconciliation and atomic authority promotion
```

`ManagedImpersonationTransport` is project-owned. `curl_cffi.AsyncSession` is
the selected protocol engine, not a new identity authority. It receives only a
validated, frozen `NetworkPersona` and request snapshot. It must be created with
an exact impersonation target and `trust_env=False`; rolling aliases such as
`chrome` or `edge` are forbidden in managed mode.

HTTPX remains available for unrelated control-plane traffic and unmanaged
platforms. Managed XHS/Douyin platform requests and their account liveness
checks move through the new transport. Browser traffic remains limited to
login, verification, Profile checks, and credential refresh.

### 4.1 Option Comparison

| Option | TLS/H2 and connection identity | Cookie/session isolation | Deployment and maintenance | Decision |
| --- | --- | --- | --- | --- |
| HTTPX plus headers/SSL | headers can align, but current HTTPX is HTTP/1.1 and exposes the Python/OpenSSL TLS family | possible with a persistent client, but does not solve the transport-persona gap | smallest code change | rejected as managed platform transport |
| `curl_cffi.AsyncSession` | explicit browser preset, custom JA3/Akamai/extra fields, H2, and connection reuse | one Session/Jar per attempt is practical | in-process MIT dependency with Windows/Linux wheels; version catalog required | selected engine |
| local TLS/H2 sidecar | can centralize a different fingerprint engine | adds another credential-bearing process and another pool/isolation boundary | highest operational, IPC, proxy, failure, and secret-handling cost | deferred contingency only |
| BrowserPageTransport | closest to the actual browser network and JavaScript environment | naturally tied to browser context | violates the confirmed batch-network boundary and expands runtime cost/refactor scope | comparison baseline only |
| browser login plus managed HTTP | keeps visible authentication in browser and efficient API collection in Python | safe only with one provider authority, one persona contract, and staged Cookie reconciliation | bounded change that fits the existing Runner | selected architecture |

The public `tls.sub2api.org` endpoint returned HTTP 502 during Packet A and did
not expose a sidecar API contract. The Sub2API repository is useful only as an
in-process TLS-profile and account/pool-isolation design reference; it is not
adopted as a service dependency.

## 5. Packet A Feasibility Receipt

Packet A used temporary dependencies, loopback HTTP servers, public synthetic
fingerprint collectors, local browser executables, and existing tests. It did
not change `pyproject.toml`, a lock file, product code, database state, real
Profiles, or real platform accounts.

### 5.1 Environment And Dependency Evidence

- baseline host: Windows 11 x86-64, Python 3.12.10, `uv 0.11.7`;
- project baseline: `httpx 0.28.1`; no project `curl_cffi` dependency;
- tested candidate: stable `curl_cffi 0.15.0`, installed in an isolated
  `uv run --no-project --with curl-cffi==0.15.0` environment;
- PyPI publishes CPython 3.10+ ABI3 wheels for Windows x86-64/ARM64,
  manylinux x86-64/AArch64 and other architectures, and musllinux
  x86-64/AArch64;
- actual target-server import and native-library startup remain Packet G
  deployment evidence, not an inference from wheel filenames.

`curl_cffi 0.15.0` and the current `0.16.0b1` source expose Chrome targets
through `chrome146` and Edge targets only for `edge99` and `edge101`. The Packet
A host has Chrome `150.0.7871.129` and Edge `150.0.4078.83`. Therefore neither
local browser channel has an exact published preset. Managed mode must stop at
preflight until a tested compatibility entry exists; Edge must never inherit a
generic Chrome target.

### 5.2 Synthetic Runtime Evidence

The temporary harness proved:

- one `AsyncSession` imports response `Set-Cookie` values and reuses a
  loopback connection;
- separate concurrent Sessions keep Cookie values and connection sets
  disjoint;
- cancellation completes and the library remains closable;
- an explicit invalid proxy fails instead of reaching a valid loopback origin
  directly;
- a new Session starts with an empty Jar;
- `response.headers.get_list("set-cookie")` preserves separate Set-Cookie
  header lines;
- the built-in Jar retains name/value/domain/path/Secure/expiry/HttpOnly data,
  but the observed Jar projection does not retain SameSite. Packet F must
  therefore use the separate header lines and a validated structured candidate
  model; the library Jar is not the durable authority format.

The focused CR-129 request-identity baseline passed `97` tests. It proves XHS
signer/final-request freezing and Douyin managed GET/token/signature boundaries.
The current managed Douyin client deliberately stops POST before network
because body-aware `a_bogus` proof is absent; Packet E owns that extension.

### 5.3 Measured Fingerprint Evidence

The public synthetic collector `https://tls.peet.ws/api/all` was used after
`https://tls.sub2api.org/` returned HTTP 502. No IP, ClientHello random,
session ID, or other runtime-random value is recorded here.

| Channel | Measured result |
| --- | --- |
| current HTTPX with a Chrome UA | HTTP/1.1; JA4 identifies an H1 Python/OpenSSL-style channel; no Akamai H2 proof |
| `curl_cffi chrome136` across three new Sessions | H2 and one stable JA4/Akamai profile; raw JA3 hashes varied as Chrome extension order varied |
| native Chrome 150 and Edge 150 | H2; the same measured Akamai H2 digest; browser-channel JA4 remained in its own allowed family |
| native Chrome 150 versus `curl_cffi chrome146` | normalized JA3N digest and Akamai H2 digest matched in this sample, while JA4 differed |

The measured native Chrome 150 ClientHello advertised three additional
signature schemes that the `chrome146` preset did not advertise. This explains
why matching JA3N and H2 alone is insufficient. Packet B must validate separate
browser and transport allowed proofs plus an explicit compatibility relation;
it must not require byte-identical random handshakes or accept one matching
hash as a complete proof.

Measured hashes are dated diagnostic evidence only. They are not copied into a
production allowlist until Packet B adds a versioned evidence schema, repeat
sampling, source attribution, and review.

### 5.4 Reference And License Matrix

| Source | Boundary | License/readability | Use |
| --- | --- | --- | --- |
| `lexiforest/curl_cffi` | in-process browser TLS/H2 impersonation and async Session | MIT; public and retrieved | direct pinned dependency candidate |
| `apify/crawlee-python` | browser/HTTP client, SessionPool, retry lifecycle | Apache-2.0; public | lifecycle design reference only |
| `Wei-Shaw/sub2api` and `tls.sub2api.org` | account/pool TLS-profile reference and public collector | repository public; collector returned 502 | design reference only; no sidecar adoption |
| `MediaCrawlerPro-Python` | HTTPX/Playwright multi-account crawler | private source retrieved; custom non-commercial license | design reference only; no code copy |
| `MediaCrawlerPro-CookieBridge` | extension/server Cookie transfer keyed by client ID | private source retrieved; custom non-commercial license; optional-any-account and stale-cache behavior conflict with this CR | design reference only; no code copy |
| `MediaCrawlerPro-SignSrv` | separate Node signing service | private source retrieved; custom non-commercial license | design reference only; current project signer retained |
| `Cloxl/xhshow` | XHS request signatures | MIT; public | retain existing project integration; no transport authority |
| `ReaJason/xhs` | XHS HTTP Session patterns | MIT; public | reference only |
| `Johnserf-Seed/f2` | Douyin token/signature utilities | Apache-2.0; public; older release | reference only; no authority replacement |

### 5.5 Evidence-Gap Ledger

| Gap | Packet A disposition | Follow-up |
| --- | --- | --- |
| Windows/Linux wheel availability | fixed for published artifacts | Packet G proves install/import on actual server image |
| AsyncSession construction and close | fixed by isolated Windows prototype | Packet C adds stress and fault tests |
| JA3/JA4/H2 measurement | fixed for route selection | Packet B creates reviewed allowed ranges |
| Chrome/Edge target coverage | accepted limitation | fail closed; add a persona only after exact evidence review |
| same-account connection reuse | fixed by loopback proof | Packet C proves bounded pool behavior |
| cross-account isolation | fixed at library prototype level | Packet C/G prove integrated two-account isolation |
| XHS/Douyin current signature validity | fixed for current CR-129 synthetic GET boundary | Packet D/E re-run after transport integration |
| Douyin body-aware POST | deferred | Packet E; no current managed POST dispatch |
| private reference readability | fixed | license-restricted sources remain reference-only |
| `tls.sub2api.org` availability | accepted external outage | use a replaceable collector adapter and record source/time |
| actual server native dependency | deferred | Packet G server-like preflight |

No evidence gap requires a product, permission, data, or deployment choice from
the user. Unsupported runtime combinations have a deterministic stop rule.

## 6. Identity Consistency Contract

| Signal category | Authority | Required consistency | Validation | Drift handling |
| --- | --- | --- | --- | --- |
| account, workspace, platform, `profile_key` | account record and provider result | exact | equality and safe IDs | stop before Session creation |
| identity, Cookie-material, proxy, resolution, attempt, run, persona revisions | frozen provider/request binding | exact and monotonic | versioned binding plus CAS | close Session; new resolution/attempt as defined |
| Cookie and token values | committed Profile plus encrypted material selected for the attempt | exact within attempt | secret-free digests and required-name checks | isolate candidate; never mutate in-flight authority |
| URL, method, body, signer input/output | platform request snapshot | byte-identical where signer semantics require it | existing CR-129 digest proof | stop before dispatch |
| UA, UA-CH, browser family/channel/version range, OS/platform | NetworkPersona | semantically compatible | structured parsing and allowed-range rule | unsupported persona preflight failure |
| language, locale, timezone, screen, viewport, device/touch | provider-effective browser proof | semantically compatible | normalized values and policy matrix | new provider resolution or failure |
| TLS versions/ciphers/extensions/signature schemes, JA3N, JA4, ALPN | channel-specific expected proof in NetworkPersona | within the channel's versioned allowed range | normalized collector proof and digest | quarantine persona revision; stop dispatch |
| H2 SETTINGS/order, window update, priority, pseudo-header order | transport fingerprint profile | exact or allowed set for that profile | structured H2 proof | stop dispatch |
| proxy ID/URL, public egress, DNS mode, region/ASN policy | provider and runtime proxy proof | exact revision; compatible observed network persona | safe proxy digest and bounded external proof | no direct fallback; terminal proxy/persona error |
| GREASE value, ClientHello random, ephemeral key share, PSK binder, ticket bytes, stream IDs | protocol runtime | expected to vary | negative tests reject persistence/fixed-value requirements | do not store or compare byte-for-byte |
| interval, concurrency, pagination, retry, connection reuse | account/runtime policy | stable behavior policy | bounded counters and attempt proof | terminal policy error or new attempt |

Exact values and semantic ranges are different contracts. A browser proof and
a transport proof do not need the same raw JA3 hash, random bytes, key share,
or ticket. They must independently match their channel-specific allowlist and
then pass the compatibility relation for browser family, version range, OS,
headers, locale, and proxy egress.

## 7. NetworkPersona And Fingerprint Model

Use preset-first profiles. Raw TLS/H2 fields support diagnostics, evidence
comparison, and a reviewed custom profile; they are not the primary account
configuration surface.

`NetworkPersona` contains safe, versioned references:

- `persona_id`, `persona_revision`, schema version, evidence source, capture
  time, last verification time, explicit `valid_until`, and compatibility
  digest. A persona is quarantined at `valid_until`, and is also invalidated
  immediately by a browser/engine/channel/catalog change; the initial validity
  policy is evidence-driven and is not an unmeasured fixed-day promise;
- browser channel/family, browser implementation and allowed version range,
  OS/platform, UA/UA-CH policy, locale/language/timezone/screen/device policy;
- `browser_expected_proof` with allowed JA3N/JA4/ALPN/H2 and runtime-network
  proof rules;
- `transport_fingerprint_profile_id` and
  `transport_fingerprint_profile_revision`;
- `transport_expected_proof` with pinned engine/version, exact impersonation
  target, allowed JA3N/JA4/ALPN/H2 proof, header-order policy, and proxy/DNS
  policy;
- a machine-readable browser-to-transport compatibility rule.

`TransportFingerprintProfile` contains:

- pinned `curl_cffi` version and exact target;
- supported browser channels and browser-version range;
- expected TLS version/cipher/group/signature/extension policies;
- GREASE and extension-permutation policy;
- ALPN, certificate compression, ALPS and ticket policy;
- JA3N/JA4 expected values or reviewed ranges;
- Akamai/H2 SETTINGS order and values, WINDOW_UPDATE, priority, pseudo-header
  and ordinary-header order;
- source, schema, evidence time, last verified time, explicit `valid_until`,
  and a safe digest.

GREASE values, ClientHello random, ephemeral keys, PSK binders, ticket content,
connection objects, and pool state are never stored in a reusable profile.

CR-131 does not require a database migration or a new user-editable system
setting. The initial persona catalog is version-controlled deployment/code
data with strict schema, size, field, and digest validation. Durable account
persona selection uses the provider's existing effective runtime authority.
If implementation proves that a queryable durable binding is required, stop
that packet and register an additive, nullable, reversible schema packet before
writing any historical row.

## 8. Session Ownership And Lifecycle

The Session ownership key is:

```text
workspace_id + account_id + platform + profile_key + resolution_id
+ attempt_id + run_id + identity_revision + cookie_material_revision
+ proxy_revision + persona_id + persona_revision
+ transport_fingerprint_profile_id + transport_fingerprint_profile_revision
+ profile_runtime_revision
```

Rules:

1. One key owns one `ManagedImpersonationTransport`, `AsyncSession`, Cookie Jar,
   and connection pool.
2. The account liveness check and all managed API calls in that attempt reuse
   this Session; no platform Client creates an inner HTTPX client.
3. Session construction validates the provider proof, exact target, engine
   version, explicit proxy, `trust_env=False`, DNS policy, Cookie candidate
   state, and persona compatibility before any platform request.
4. A Session is never shared across accounts, platforms, resolutions,
   attempts, runs, proxies, persona revisions, or credential revisions.
5. A transient Runner retry first cancels and closes the old Session and pool,
   records terminal cleanup, then creates a new attempt ID and new Session from
   the same frozen identity/Cookie/proxy/persona revisions. Attempts do not
   overlap.
6. Login, second verification, challenge, rate limit, identity mismatch,
   signer/protocol mismatch, timeout, cancellation, crash, and proxy/persona
   mismatch do not retry as transient network failures.
7. Service restart recreates Sessions from committed revisions. It does not
   serialize sockets, connection pools, TLS tickets, ephemeral keys, or a live
   Cookie Jar.
8. Cancellation and timeout close the Session in centralized finalization,
   discard uncommitted candidates, release locks, and preserve committed
   authority. Startup recovery makes the same cleanup idempotent after a crash.

For SOCKS proxies, managed hostname resolution must use the provider-approved
remote-DNS form. The persona records an explicit `dns_resolution_mode` enum:
`proxy_remote`, `proxy_connect`, or `provider_explicit_direct`; there is no
`system_default` mode. HTTP proxy/CONNECT and explicitly provider-selected
direct policies are tested separately. Ambient `HTTP_PROXY`, `HTTPS_PROXY`,
`ALL_PROXY`, and `NO_PROXY` values never become managed authority.

## 9. Cookie And Profile Authority State Machine

```text
committed Profile + committed encrypted Cookie revision
  -> provider resolution and frozen material snapshot
  -> attempt-bound transport Session/Jar
  -> isolated Set-Cookie candidate revision
  -> same account/persona/proxy API identity check
  -> encrypted candidate staging with expected base revisions
  -> candidate Profile clone and browser identity validation
  -> journaled compare-and-swap promotion of Profile generation + Cookie revision
  -> old generation retirement after commit
```

There is no unrestricted two-way synchronization.

- The committed Profile remains browser-login authority.
- Encrypted Cookie remains initialization, refresh, recovery, and migration
  material.
- A response Jar is attempt-local and is not automatically authoritative.
- `Set-Cookie` is captured from separate header lines and parsed with a
  structured parser. Comma splitting is forbidden.
- Candidate keys are `(name, domain, path)`; host-only, Domain, Path, Secure,
  HttpOnly, SameSite, Expires, Max-Age, creation order, and deletion semantics
  are preserved.
- Domain scope must match the request host and the platform allowlist. Invalid
  public-suffix/cross-platform domains, control characters, malformed dates,
  oversized fields, excessive counts, or unknown critical attributes stop
  candidate processing.
- `Max-Age <= 0` or an expired Expires value records a candidate deletion for
  the exact key. Same-name Cookies at different domains/paths remain distinct.
- Repeated exact keys follow response header order and are covered by tests;
  ambiguous conflicting material never becomes a flat name/value map.
- Candidate secrets stay in controlled memory or the existing encrypted
  staging mechanism. Logs and proofs contain only IDs, revisions, counts,
  reason codes, and safe digests.

Promotion uses the existing account-start lock, promotion journal, candidate
Profile, and compare-and-swap revisions. The candidate Cookie is encrypted but
not committed authority until browser identity validation passes. Filesystem
generation switch and database revision update use a journaled protocol so a
crash can deterministically finish or roll back. Failure, timeout,
cancellation, proxy drift, second verification, concurrent update, or crash
keeps the old Profile and Cookie revision authoritative.

## 10. Environment And Side-Effect Matrix

| Environment | Allowed by default | Explicit gate | Forbidden |
| --- | --- | --- | --- |
| unit/contract tests | loopback servers, synthetic Cookie/Profile, fake proxy and fingerprint proofs | none | real platform, real account, ambient proxy, production DB/Profile |
| local diagnostics | read-only version/wheel checks and explicitly named public fingerprint collector | operator runs the diagnostic command | platform login/collection and durable promotion |
| server-like automated validation | isolated service, temporary Profile, synthetic endpoint/proxy tripwire | explicit server-like test command | designated or protected real account traffic |
| designated pilot | serial XHS `9196` and Douyin `8972` only | operator opt-in plus account IDs and preflight proof | accounts `9197`/`9198`, Kuaishou, automatic account selection |
| production | managed task/account binding through the provider | accepted deployment configuration and persona catalog | anonymous/generic/other-account/default-proxy/direct fallback |

Every test process installs a network tripwire before importing platform
clients. Only loopback and explicitly mocked hosts are allowed. A test fails if
an environment variable, default account selector, scheduler, retry, account
check, or diagnostic path can reach a real platform.

## 11. Atomic Development Packets

Packet A below is the completed documentation/feasibility gate. Packets B-G are
product implementation packets and remain unchecked in `TASKS.md`.

### Packet A - Feasibility And Route Selection (complete)

Owned surface: architecture comparison, dependency/license review, wheel and
channel coverage, temporary Session/cookie/proxy/TLS/H2 prototypes, current
signer boundary, evidence ledger, and focused architecture review.

Acceptance: this document contains measured evidence, no unresolved product
decision, and a fail-closed route for unsupported Chrome/Edge combinations.

Rollback: remove temporary environments and synthetic artifacts; no product
state or dependency file changed.

### Packet B - Persona And Proof Contracts

Primary risk: accepting a semantically contradictory or guessed persona.

Expected touch surface:

- new transport/persona contract module under `tools/`;
- BrowserEnvironmentProvider and PlatformRequestEnvironment safe projections;
- safe proof serialization and tests;
- first establish RED contract tests with a fake/optional engine metadata
  adapter, including the missing-dependency and unsupported-target failures;
  then pin `curl_cffi` as the production dependency and run GREEN tests against
  the real isolated engine. Packet A's temporary install remains outside the
  project dependency and lock files.

Steps and RED/GREEN loop:

1. RED: reject missing engine version, rolling target, unsupported channel,
   Edge-to-Chrome substitution, stale proof, mismatched OS/UA-CH, and a proof
   where only JA3N matches.
2. Implement strict schemas for `NetworkPersona`, browser expected proof,
   transport fingerprint profile, transport expected proof, and compatibility
   result.
3. Add a versioned, size-limited, field-allowlisted persona catalog and exact
   dependency/target resolver.
4. Add safe digest/projection helpers and explicit reason codes; omit raw
   randoms, paths, proxies, Cookies, and tokens.
5. GREEN: repeat-sampled synthetic proofs hit separate allowed ranges and the
   cross-channel compatibility rule; unsupported local Chrome/Edge stop before
   Session construction.

Acceptance: compatibility is machine-decidable; no measured value is guessed;
the exact `curl_cffi` version/target is pinned; `check_docs`, focused tests, and
read-only review pass.

Rollback: remove the additive catalog/contracts and dependency pin; CR-129
HTTPX behavior remains available behind the unstarted CR-131 gate. Stop if a
supported target requires changing the confirmed browser-channel boundary or
persisting a new account field.

### Packet C - Attempt-Bound Managed Transport

Primary risk: cross-account connection/Cookie/proxy reuse or non-finalized
Sessions.

Expected touch surface: managed transport wrapper, Runner attempt ownership,
account-check path, XHS/Douyin Client construction, process finalization, and
synthetic network tripwires.

Steps and RED/GREEN loop:

1. RED: prove current fresh-HTTPX and unmanaged account-check paths do not
   satisfy Session ownership/reuse.
2. Implement the exact ownership key, `AsyncSession` lifecycle,
   `trust_env=False`, explicit proxy/DNS policy, bounded pool, timeout, and
   centralized async close.
3. Route managed account liveness checks and one attempt's platform calls
   through the same transport authority; account-check code must not construct
   a separate HTTPX client or bypass the frozen binding.
4. Make retry close the old pool before starting a non-overlapping new attempt;
   restart reconstructs from committed revisions only.
5. GREEN: same-attempt reuse, two-account concurrency isolation, proxy failure
   without direct fallback, cancellation/timeout/crash finalization, and
   secret-free proofs pass.

Acceptance: no managed XHS/Douyin call or managed account-check call creates an
inner HTTPX client; one attempt has one Session revision; all terminal paths
close it exactly once.

Rollback: disable the CR-131 managed-transport route before deployment and
restore the CR-129 client factory; never fall back after a managed attempt has
started. Stop if cancellation leaves live requests/pools or account-check
cannot consume the frozen binding.

### Packet D - XHS Transport Integration

Primary risk: changing bytes after XHS signing or flattening Cookie path/domain
semantics.

Expected touch surface: XHS Core/Client/request identity, signer adapter,
managed transport request/response adapter, and XHS tests.

Steps and RED/GREEN loop:

1. RED: current signer snapshot passed to a different transport Session,
   Cookie candidate, proxy, header order, URL/query, or body is rejected.
2. Adapt XHS managed GET/POST dispatch to the attempt transport without
   changing the existing sign-string/final-request contract.
3. Bind `a1`, `web_session`, Cookie selection, UA/UA-CH, Accept-Language,
   signature headers, proxy, persona, and response candidate revision.
4. Preserve typed failure and bounded request-proof behavior.
5. GREEN: byte identity, Cookie duplicate/path cases, two accounts, retry,
   cancellation, Set-Cookie isolation, and no-real-network tripwire pass.

Acceptance: XHS account check and collection use the same account transport;
only bound signed 2xx proof permits ingest; candidate Cookie does not mutate the
in-flight or committed authority.

Rollback: remove XHS adapter wiring and dependency use for XHS before rollout;
preserve CR-129 request identity. Stop on any signer/final-request byte drift.

### Packet E - Douyin Transport Integration

Primary risk: token/persona drift and body-unaware POST signing.

Expected touch surface: Douyin Core/Client/request identity, `a_bogus` adapter,
managed transport request/response adapter, and Douyin tests.

Steps and RED/GREEN loop:

1. RED: mismatched `ttwid`, `verifyFp`, `msToken`, `webid`, Cookie, UA-CH,
   proxy, persona, query, body, or signer output stops before dispatch.
2. Route existing managed GET and explicitly unsigned general-search policy
   through the attempt transport without rereading Page/global values.
3. Define body canonicalization as the exact UTF-8 bytes presented to the
   transport, prove signer output includes a digest of those bytes, and prove
   the final HTTP body matches that digest byte-for-byte before enabling any
   managed POST endpoint; retain the current pre-network stop otherwise.
4. Bind response candidates without changing current frozen token authority.
5. GREEN: GET/signature policy, body-aware POST RED/GREEN cases, two accounts,
   retry/cancel, and no-real-network tripwire pass.

Acceptance: current GET behavior remains signed/unsigned exactly as the
endpoint policy requires; a POST is enabled only with byte-identical body-aware
proof; ingest requires bound 2xx evidence.

Rollback: remove Douyin adapter wiring; preserve the CR-129 managed POST stop.
Stop if signer support cannot prove the exact final body.

### Packet F - Candidate Cookie And Profile Reconciliation

Primary risk: response Cookie material silently becoming login authority or a
crash splitting Profile/Cookie revisions.

Expected touch surface: structured Cookie candidate, encrypted staging,
promotion journal/Profile clone integration, account locks, startup recovery,
and tests.

Steps and RED/GREEN loop:

1. RED: SameSite loss, cross-domain Cookie, same-name different-path Cookie,
   deletion, concurrent candidate, proxy drift, second verification, timeout,
   cancellation, and crash cannot change committed authority.
2. Parse separate Set-Cookie lines into a bounded structured candidate and
   retain exact scope/deletion semantics.
3. Perform same-account/persona/proxy API identity check, encrypted staging,
   candidate Profile injection, and browser identity validation.
4. Promote Profile generation and encrypted Cookie revision with the existing
   journal/lock plus compare-and-swap base revisions; make recovery idempotent.
5. GREEN: every success/failure/interruption terminal state converges, old
   authority survives failure, and concurrent promotions serialize.

Acceptance: only a fully verified candidate becomes committed; no raw secret
appears in logs/argv/environment/audit/proofs; restart deterministically
finishes or rolls back a journal.

Rollback: stop candidate intake, discard uncommitted stages, and retain the
last committed Profile/Cookie pair. Stop if filesystem and database recovery
cannot identify one authoritative generation.

### Packet G - Deployment, Regression, And Designated Acceptance

Primary risk: a development-only fingerprint or dependency being treated as
server/production proof.

Expected touch surface: deployment preflight, one-click diagnostics,
server-like validation, full tests, operational docs, and designated manual
acceptance artifacts.

Steps and RED/GREEN loop:

1. RED: missing native dependency, wrong engine version/target, unsupported
   Chrome/Edge, ambient proxy, direct fallback, stale persona, or wrong DNS
   mode blocks startup/pre-dispatch with a safe diagnostic.
2. Validate Windows and target Linux/server-like install/import, TLS/H2 proof,
   proxy egress, service restart, and three restart cycles without persisting
   live Session state.
3. Run full synthetic regression with global platform-network tripwire and
   two-account concurrency/fault tests.
4. With explicit operator opt-in, run serial acceptance only for Douyin `8972`
   and XHS `9196`; keep `9197`/`9198` protected and Kuaishou Deferred.
5. Require one persisted real item per designated platform, bound proof,
   `fallback_used=false`, zero secret leakage, and post-restart repeat proof.

Acceptance: Windows and Linux/server-like preflight pass; all automatic tests
remain synthetic; designated acceptance meets the explicit account and
evidence gate; CR-047 remains separately classified until its own evidence is
recorded.

Rollback: remove the deployment enablement and keep the system at the last
verified CR-129 behavior. Never auto-select a different account or direct
network during rollback. Stop on any protected-account touch, missing proof,
secret match, or unsupported persona.

## 12. Test And Acceptance Matrix

| Layer | Required proof | Does not prove |
| --- | --- | --- |
| documentation | CR/task/current/decision/trace/test alignment and executable packet boundaries | runtime protocol behavior |
| unit/contract | schema, ownership key, compatibility, Cookie semantics, reason codes, secret-safe projections | native dependency or real connection behavior |
| loopback integration | Session reuse/isolation, proxy failure, timeout/cancel, candidate state, no inner HTTPX | public TLS fingerprint or platform acceptance |
| public synthetic collector | observed TLS/JA3N/JA4/ALPN/H2 and browser/transport ranges | platform account trust or long-term stability |
| server-like | dependency, browser channel, proxy/DNS, restart, process cleanup, no-real-network gates | designated real account behavior |
| designated pilot | actual XHS/Douyin account check, collection, persisted content, restart, and no fallback | universal resistance to platform association |

Mandatory negative tests include:

- exact-target missing, rolling alias, and Edge-to-Chrome substitution;
- matching JA3N with incompatible JA4 or headers;
- ambient proxy variables and invalid explicit proxy;
- same Cookie name at multiple domains/paths, SameSite, Secure, expiry, and
  deletion;
- account/profile/resolution/attempt/revision/persona mismatch;
- persona or transport fingerprint `valid_until` expiry, browser/engine/catalog
  change invalidation, and an unrefreshed proof;
- an invalid or implicit `dns_resolution_mode`, including a SOCKS request that
  resolves locally when `proxy_remote` is required;
- old Session still alive when retry begins;
- account-check path bypassing managed transport;
- cancellation/crash between staging, candidate Profile validation, and
  promotion commit;
- test/scheduler/default-account paths attempting real platform traffic;
- secret material in argv, environment, logs, audit, safe proof, or exceptions.
- ephemeral TLS state (GREASE, ClientHello random, session ticket, ephemeral
  keys, PSK binder, or connection identifier) stored in a NetworkPersona or
  TransportFingerprintProfile.

## 13. Documentation And Compatibility Updates

Each implementation packet updates, when affected:

- `docs/TASKS.md`;
- `docs/CURRENT_STATE.md`;
- `docs/TEST_RESULTS.md`;
- `docs/TRACEABILITY.md`;
- `docs/ACCOUNT_ENVIRONMENT.md` and `docs/SERVER_DEPLOYMENT.md`;
- `docs/TEST_PLAN.md` when a contract or acceptance lane changes;
- `docs/DECISIONS.md` when the selected engine, authority, persistence, or
  rollback boundary changes.

There is no CR-131 schema migration or user-editable setting in the accepted
planning baseline. `DATA_MODEL.md`, `SCHEMA_MIGRATION.md`, and
`SYSTEM_SETTINGS.md` change only if a later packet first registers and reviews
an actual durable/configuration boundary.

## 14. Residual Association Risks

Even after all packets pass, platforms can still correlate or challenge
accounts through:

- proxy quality, public IP history, ASN, geolocation, DNS behavior, or shared
  upstream infrastructure;
- phone number, recovery identity, payment/contact data, account relationships,
  prior device and login history;
- request timing, navigation, pagination, concurrency, content interests, and
  other behavioral patterns;
- browser JavaScript/device APIs that an HTTP transport does not execute;
- platform-side protocol changes, challenges, rate rules, or hidden scoring;
- gaps between the latest installed browser and available fingerprint targets.

These are accepted residual risks, not evidence that identity isolation failed.
Operational diagnostics must distinguish a contract mismatch from a platform
challenge or reputation signal.

## 15. Review Gate And Issue Ledger

Maximum review rounds: 10. Round 1 is a full deep architecture/instruction
review. Later rounds are focused on previously reported blockers or material
refinements. Each finding is classified as fixed, accepted, deferred, rejected,
or needs user decision.

Final focused re-review gate (Round 2):

```text
Architecture verdict = SOUND
Architecture blockers = None
Architecture material refinements = None
Instruction verdict = READY
Instruction blockers = None
Instruction material refinements = None
Unresolved user decisions = None
```

Round 1 issue ledger (from the independent read-only review, before focused
re-review):

| Finding | Disposition |
| --- | --- |
| A-BLOCK-01 ownership-key revision ambiguity | fixed: split transport fingerprint revision and Profile runtime revision |
| I-MAT-01 account-check transport bypass wording | fixed: account-check is an explicit managed transport caller and acceptance invariant |
| I-MAT-02 dependency pin ordering | fixed: RED uses optional/fake engine metadata, then production pin and GREEN |
| I-MAT-03 stale persona policy | fixed: explicit `valid_until` and event invalidation; no guessed fixed-day threshold |
| I-MAT-04 Douyin body-aware proof | fixed: exact final UTF-8 body digest is part of signer proof |
| I-MAT-05 DNS mode omission | fixed: explicit `proxy_remote`/`proxy_connect`/`provider_explicit_direct` enum; no system default |
| W-MIN-01 current Chrome/Edge target gap | accepted: fail-closed operational prerequisite, no silent mapping |
| W-MIN-02 ephemeral-state negative test | fixed: added to mandatory test matrix |

Round 2 focused re-review found no new blocker or material refinement. The
Chrome/Edge 150 target gap remains an explicitly accepted fail-closed
operational prerequisite; it is not a silent compatibility claim. CR-131 is
now `Accepted / Ready for Implementation`. Packet B is the first product-code
packet; Packets B-G remain unstarted until their individual gates open. A final
status-only read-only review returned PASS with no blocking or material
finding.
