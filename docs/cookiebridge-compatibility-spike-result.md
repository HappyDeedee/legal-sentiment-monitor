# CR-112 Packet B Compatibility Spike Result

Status: `Verified` on 2026-07-21. The Packet B evidence and synchronized
implementation boundary are complete within the synthetic local proof scope.

## Scope And Baseline

- Baseline: `main@2ea2c1e96675297e302368b1226ec7aac05f2bb1` plus the
  accepted CR-112 plan commit `44baf78`.
- Environment: same-machine Windows, Chrome `150.0.7871.125`, Edge
  `150.0.4078.83`, Playwright `1.45.0`, FastAPI `0.110.2`, Starlette
  `0.37.2`, and Uvicorn `0.29.0`.
- Inputs: ignored reference source, temporary browser Profiles, and synthetic
  Cookie records only.
- Excluded: product code/schema/UI changes, real account Cookies, real login,
  real platform requests, durable account Profiles, and production claims.

## Reference Findings

The evaluated reference is not a complete CR-112 product boundary:

- its Extension hardcodes `ws://localhost:8274/ws` and has no packaged
  manifest key;
- its registration contains a generated `client_id`, but no pairing token,
  account/Profile claim, or authenticated credential;
- its Connector accepts every Origin, keeps client/cache state only in memory,
  and can choose an available client when no exact `client_id` is supplied;
- its Cookie response is a flattened `name=value` string. A synthetic pair
  with the same name and different paths returned only one value, with no
  domain, path, `HttpOnly`, `Secure`, or `SameSite` attributes;
- its server requires Python `>=3.12`, while the product runtime is Python
  `3.11`;
- its license is the repository's non-commercial learning license and is not
  selected as a product distribution dependency.

Browser loading results:

| Browser/path | Reference Extension | Exact result |
| --- | --- | --- |
| Chrome `150.0.7871.125` | FAIL | The target Service Worker did not load from `--load-extension`; no target Extension ID was present. |
| Edge `150.0.4078.83` | PARTIAL | The target Service Worker loaded and registered a `client_id`, but the reference protocol failed exact binding and structured-Cookie requirements. |
| Edge copied extension path with spaces and Chinese characters | FAIL identity stability | The unpacked Extension loaded under a different ID because the manifest has no stable key. |

Current branded Chrome intentionally restricts command-line loading of
unpacked extensions. This is consistent with the official
[Chrome extension update](https://developer.chrome.com/blog/extension-news-june-2025?hl=en)
and the corresponding
[Chromium change](https://chromium.googlesource.com/chromium/src/+/04f6233ce5be7e5e420418b5286f3b0f87ffc28f%5E%21/).
Managed policy/store installation would add deployment and distribution
dependencies and still would not repair the reference pairing or Cookie
fidelity gaps.

## Selected Acquisition Proof

The independent replacement prototype reads Cookies from the exact
application-managed persistent browser context through Playwright/CDP. No
Extension, WebSocket Connector, client discovery, or Cookie string flattening
is involved.

| Requirement | Chrome | Edge |
| --- | --- | --- |
| Fresh temporary persistent Profiles | PASS | PASS |
| Two same-name Cookies with different paths remain distinct | PASS | PASS |
| Domain/path/host-only/HttpOnly/Secure/SameSite preserved | PASS | PASS |
| Browser/Profile restart preserves records | PASS | PASS |
| Two simultaneous Profiles remain isolated | PASS | PASS |
| No Extension Service Worker required | PASS | PASS |
| Temporary test Profiles removed after close | PASS | PASS |

Each browser test used three synthetic records per Profile. The structured
validator accepted distinct scope tuples and rejected six negative cases:
exact duplicate tuple, unrelated domain, unsupported partition key, oversized
record, excessive record count, and oversized frame.

Protocol V1 limits fixed by this spike:

- maximum `256` Cookie records per acquisition;
- maximum `8192` serialized bytes per record;
- maximum `1048576` serialized bytes per acquisition payload;
- required fields: `name`, `value`, `domain`, and `path`;
- supported optional fields: `expires`, `http_only`, `secure`, `same_site`,
  and derived `host_only`;
- `partition_key` is rejected until the selected provider proves roundtrip
  support rather than silently dropping it;
- tuple identity is `(name, domain, path, partition_key)`;
- platform domain allowlists and exact duplicate rejection are fail closed.

The feature-disabled baseline remains HTTP `404` and unmatched WebSocket
upgrade `403` on the pinned FastAPI/Starlette/Uvicorn runtime. The selected V1
product path adds no Cookie-bridge WebSocket route, so no Origin, loopback,
pairing-token, or connected-client trust boundary exists in Packet C.

## Component Decision Matrix

| Component | Reference evidence | Contract gaps | License/runtime fit | Decision | Packet C owner |
| --- | --- | --- | --- | --- | --- |
| Extension | Edge loads; Chrome does not; unpacked ID changes with path | Chrome deployment, stable identity, authenticated account binding, cleanup dependency | Reference distribution is not selected | `single-component replacement` | Existing managed Playwright/CDP browser context |
| Connector | In-memory WebSocket registry and cache work for a basic Edge roundtrip | permissive Origin, optional/implicit client selection, no credential binding, separate lifecycle | Python `>=3.12`; product is Python `3.11` | `single-component replacement` | In-process account-bound browser acquisition service; no WebSocket route |
| Protocol | Request ID is echoed in the basic roundtrip | flattened string loses duplicate scope and security attributes | Wire format is tied to rejected reference path | `minimal adaptation` | Internal structured Cookie Protocol V1 from Playwright Cookie records |

## Packet C Handoff

- C.2 opens or attaches only to the exact browser context created for the
  locked `social_account_id`, `profile_key`, and `login_session_id`.
- The server retains the context handle; acquisition never discovers a
  browser/Profile/client by nickname, timing, first/newest/only ordering, or
  default Profile.
- The direct result enters the same canonical validator, candidate injection,
  account identity check, encrypted persistence, and promotion journal used by
  advanced manual Cookie input.
- The selected feature flag controls only C.2 start/status/cancel/UI behavior.
  Feature-off means no browser acquisition starts. QR, C.1 manual
  Cookie-to-Profile, and C.3 profile-only crawling remain independent.
- Product installation needs only the already selected Chrome or Edge and the
  existing Playwright/CDP runtime. It does not install an Extension, run a
  Connector service, expose a loopback Cookie route, or require Python 3.12.

## Proof Boundary

This result proves the component choice with synthetic local evidence. It does
not implement Packet C, prove a real platform account, close CR-047
Linux/server-like acceptance, or prove a second physical computer. Packet D
still requires designated Douyin and Xiaohongshu accounts, administrator
reveal/copy, fresh candidate injection, restart verification, no fallback, no
plaintext child argv/environment, and at least one persisted real item per
platform. Kuaishou remains `Deferred`.
