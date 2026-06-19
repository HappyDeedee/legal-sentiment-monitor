# Account Environment

This document defines the relationship between platform accounts, profiles,
proxies, browser sessions, login sessions, and crawl runs.

## Core Model

```text
Task -> Platform Account -> Account Identity -> Profile + Proxy -> Server Browser Session
```

Rules:

- one platform account maps to one profile;
- one platform account maps to one persisted account identity after CR-047;
- one profile cannot be used by two browser sessions at the same time;
- one platform account cannot be used by two crawl runs at the same time;
- before CR-047 locked account identity is active, proxy priority is task
  proxy, account proxy, then default network;
- after CR-047 locks an account identity, task-level proxy overrides are
  rejected for that locked account environment, and proxy changes require
  explicit reset/re-login;
- login and crawling should use the same proxy when a proxy is bound.

Accepted CR-047 target rule:

```text
one platform account = one profile_key = one stable account identity
```

The stable account identity means that server-side QR login, accepted Cookie
validation, login-state checks, and crawling for the same platform account
should reuse the same persisted profile traces, browser environment, proxy
region/policy, runtime binding, lock state, and audit trail.

The profile folder stores browser traces, including cookies, local storage,
IndexedDB, cache, history, preferences, service workers, and session state.
The database stores the account identity rules needed to launch the same
browser environment again: user agent, browser platform, timezone, locale,
accept-language, viewport/screen/device flags, fingerprint seed, proxy policy,
region, generator metadata, validation state, lock state, and re-login state.

## Profile Identity

Confirmed target design:

```text
profile_key = {workspace_id}/{platform}/acc_{account_id}
runtime_path = {ACCOUNT_PROFILE_ROOT}/{profile_key}
```

Examples:

```text
default/dy/acc_1429
default/xhs/acc_1430
default/ks/acc_1431
```

Rules:

- account name is display-only;
- account name changes must not change profile identity;
- real profile paths are never shown in normal-user UI;
- administrator UI may show "account environment created" rather than raw path;
- raw profile paths may appear only in server diagnostics for trusted admins,
  pending a separate administrator diagnostics decision.

## Social Account Fields

Target fields:

- id;
- workspace_id;
- platform;
- account_name;
- login_type;
- status;
- profile_key;
- proxy_id;
- environment_region;
- browser_platform;
- identity_template;
- fingerprint_seed;
- user_agent;
- timezone;
- locale;
- accept_language;
- screen_width;
- screen_height;
- viewport_width;
- viewport_height;
- device_scale_factor;
- is_mobile;
- has_touch;
- identity_generator_name;
- identity_generator_version;
- identity_environment_version;
- proxy_region_snapshot;
- browser_environment_locked_at;
- browser_environment_lock_reason;
- requires_relogin;
- identity_state;
- identity_runtime_snapshot_json;
- notes;
- last_login_at;
- last_checked_at;
- last_error;
- is_active;
- created_by;
- updated_by.

Existing `profile_path` is a transition-only legacy field. New account
environments must use `profile_key`, and old low-volume accounts can be
re-created or re-logged in instead of receiving long-term compatibility logic.

The CR-047 account identity fields are accepted for future implementation, not
yet implemented in the current runtime. They should be generated or assigned
before the first QR login or accepted Cookie login validation and locked after
the account environment becomes usable. Silent edits after successful login are
not allowed; changing a locked identity requires an explicit reset/re-login
flow with audit logging. If a proxy region or identity template change would
make the current locked identity inconsistent, mark the account
`requires_relogin` instead of silently changing future launches.

Reference note:

- CloakBrowser-Manager is a useful reference for stable profile settings such
  as browser platform, fingerprint seed, user agent, timezone, locale, screen
  size, proxy, CDP, and noVNC.
- This project should absorb that account-environment model, but should not
  copy CloakBrowser-Manager's standalone account center, database, frontend,
  authentication model, or deployment layout without a separate provider
  decision.

## Account Identity Responsibilities

Profile folder responsibility:

- preserve login traces such as cookies, local storage, IndexedDB, cache,
  browser history, preferences, service workers, sessions, and extension state
  if extensions are later enabled;
- stay under the server-side account profile root resolved from `profile_key`;
- never be exposed as a raw filesystem path in normal-user UI or APIs.

Database identity responsibility:

- persist launch inputs that should remain stable across login and crawl:
  browser platform, user agent, timezone, locale, accept-language,
  viewport/screen/device flags, fingerprint seed, and provider metadata;
- persist proxy policy and customer-safe region snapshot for consistency
  checks;
- persist lock, reset, re-login, and audit state;
- provide a role-safe summary for administrators without exposing cookies,
  proxy credentials, CDP endpoints, noVNC sessions, or fingerprint-debug
  internals.

## Account Identity Generation And Validation

CR-047 should add an Account Identity Generator:

- input: workspace, platform, account ID, proxy/region policy, identity
  template or template-family selection policy, and seed salt;
- output: environment region, browser platform, user agent, timezone, locale,
  accept-language, screen, viewport, device scale factor, mobile/touch flags,
  fingerprint seed, and generator metadata;
- stability rule: the same input produces the same identity;
- differentiation rule: different accounts normally receive different seeds
  and fingerprints unless an administrator explicitly clones a safe template
  before first login;
- explainability rule: each generated identity can be traced to a
  customer-safe template and generator version.

Initial template examples:

- `CN_WIN_CHROME_1920`;
- `CN_WIN_CHROME_1536`;
- `CN_MAC_CHROME_1440`;
- `CN_ANDROID_CHROME`;
- `HK_DESKTOP_CHROME`;
- `SG_DESKTOP_CHROME`.

Template selection policy:

- default behavior is system automatic selection before first QR login or
  accepted Cookie validation;
- normal users cannot choose identity templates or browser-environment fields;
- administrators do not need to choose a template for ordinary account
  creation;
- administrators may use an advanced pre-login override to choose only a
  template family, such as Windows Chrome desktop, Mac Chrome desktop, or
  Android Chrome, not individual fields such as UA, viewport, screen,
  timezone, locale, accept-language, or device flags;
- the generator expands the final selected catalog template into exact fields;
- after successful login locks the account identity, template changes require
  the explicit reset/re-login workflow and audit logging.

China mainland proxy rule:

- `environment_region = CN_MAINLAND`;
- `timezone = Asia/Shanghai`;
- `locale = zh-CN`;
- `accept_language = zh-CN,zh;q=0.9`;
- use a coherent desktop or mobile device template;
- avoid province-level browser overfitting. Prefer stable proxy region/ISP,
  device family, browser family, and language/timezone consistency.

CR-047 should also add an Account Identity Validator that fails closed before
login or crawl launch when:

- proxy region and timezone/locale/accept-language conflict;
- browser platform, user agent, viewport/screen, mobile flag, and touch flag do
  not describe the same device class;
- required locked identity fields are missing;
- a locked account would fall back to process defaults;
- a task-level proxy override conflicts with the final confirmed proxy policy.

## Identity Lifecycle State Machine

The identity state is persisted in `identity_state` and is distinct from the
existing login status.

| State | Meaning | Editable fields |
| --- | --- | --- |
| `draft` | account exists but identity fields are not assigned yet | proxy region and optional admin template-family choice |
| `generated` | identity fields are assigned but not yet validated | same as `draft`; no field-level identity edits |
| `validated` | generator output passed the validator and is ready for login | same as `generated` until login starts |
| `login_in_progress` | QR or Cookie login is currently running | none except transient login-session metadata |
| `locked` | successful login or validation froze the browser environment | no direct identity fields; only admin reset can change state |
| `active` | locked identity is usable for crawl runs | no direct identity fields |
| `requires_relogin` | locked identity became inconsistent and must be rebuilt | none except reset/re-login workflow |
| `resetting` | admin reset is clearing the old identity before regeneration | reset workflow fields only |

Allowed transitions:

- `draft -> generated` when the generator writes a template and seed.
- `generated -> validated` when the validator passes all required checks.
- `validated -> login_in_progress` when server login starts.
- `login_in_progress -> locked` when QR login or Cookie validation succeeds.
- `locked -> active` when the account becomes reusable for later runs.
- `locked -> requires_relogin` when template, proxy region, or other locked
  input changes would make the current identity inconsistent.
- `requires_relogin -> resetting -> draft` when an administrator performs an
  explicit audited reset/re-login flow.
- Any validation failure returns the account to `draft` or leaves it in
  `generated` with an error record; it must not silently continue to login.

Template-family change rules:

- in `draft`, an administrator's advanced template-family choice is allowed
  and the next generator run uses that family;
- in `generated`, changing the template family invalidates generated identity
  fields and returns the account to `draft` before regeneration;
- in `validated`, changing the template family invalidates the validated
  identity and returns the account to `draft` before regeneration and
  revalidation;
- in `login_in_progress`, template-family changes are rejected because the
  active login session owns the validated identity;
- in `locked` or `active`, template-family changes move through
  `requires_relogin` and the explicit reset/re-login workflow; they must not
  silently regenerate future launch fields;
- in `requires_relogin` or `resetting`, template-family changes are part of the
  audited reset workflow only.

## Identity Generation Specification

Phase 5.1 generator v1 is deterministic and template-driven:

- template-selection input tuple:
  `workspace_id`, `platform`, `account_id`, `proxy_region_snapshot`,
  `template_family_or_auto`, and `seed_salt`;
- template-selection serialization:
  `workspace_id|platform|account_id|proxy_region_snapshot|template_family_or_auto`;
- template-selection seed:
  `template_selection_seed =
  hex(HMAC-SHA256(seed_salt, template_selection_serialization))[0:32]`;
- candidate template selection:
  filter the versioned template catalog by `proxy_region_snapshot` and the
  optional administrator-selected template family, keep the candidate list in
  documented catalog order, and select
  `index = int(template_selection_seed[0:8], 16) % candidate_count`;
- if the filtered candidate list is empty, validation fails closed with a
  named error instead of falling back to a random or process default template;
- canonical identity input tuple:
  `workspace_id`, `platform`, `account_id`, `proxy_region_snapshot`,
  `identity_template`, and `seed_salt`;
- canonical identity input serialization:
  `workspace_id|platform|account_id|proxy_region_snapshot|identity_template`;
- seed derivation:
  `fingerprint_seed =
  hex(HMAC-SHA256(seed_salt, canonical_identity_input))[0:32]`;
- template lookup:
  the selected `identity_template` selects a fixed row from the catalog below;
- no random fallback:
  the same input tuple must always produce the same output row.

Template catalog v1:

The values below are the Phase 5.1 v1 catalog. If the bundled browser version
is upgraded later, a new `identity_environment_version` and generator version
must be recorded instead of mutating locked identities in place.

| Template | browser_platform | user_agent | screen | viewport | scale | mobile | touch | timezone | locale | accept_language |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CN_WIN_CHROME_1920` | `windows` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36` | `1920x1080` | `1920x963` | `1` | `false` | `false` | `Asia/Shanghai` | `zh-CN` | `zh-CN,zh;q=0.9` |
| `CN_WIN_CHROME_1536` | `windows` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36` | `1536x864` | `1536x768` | `1` | `false` | `false` | `Asia/Shanghai` | `zh-CN` | `zh-CN,zh;q=0.9` |
| `CN_MAC_CHROME_1440` | `macos` | `Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36` | `1440x900` | `1440x789` | `2` | `false` | `false` | `Asia/Shanghai` | `zh-CN` | `zh-CN,zh;q=0.9` |
| `CN_ANDROID_CHROME` | `android` | `Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Mobile Safari/537.36` | `1080x2400` | `412x915` | `2.625` | `true` | `true` | `Asia/Shanghai` | `zh-CN` | `zh-CN,zh;q=0.9` |
| `HK_DESKTOP_CHROME` | `windows` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36` | `1920x1080` | `1920x963` | `1` | `false` | `false` | `Asia/Hong_Kong` | `zh-HK` | `zh-HK,zh;q=0.9,en;q=0.8` |
| `SG_DESKTOP_CHROME` | `windows` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.183 Safari/537.36` | `1440x900` | `1440x789` | `1` | `false` | `false` | `Asia/Singapore` | `en-SG` | `en-SG,en;q=0.9,zh;q=0.7` |

Template rules:

- `identity_template` is the final catalog row selected by the generator before
  the first login; it may be influenced only by an administrator's pre-login
  template-family override.
- The generator must not improvise a different template silently.
- If no administrator template-family override is provided, automatic template
  selection is used.
- `screen` is the physical display envelope used for the template; `viewport`
  is the browser content area.
- `is_mobile` and `has_touch` must agree with the template family.
- `browser_platform` describes the family of the template, not a runtime
  stealth guess.
- UI/API paths must not expose field-level editing for UA, viewport, screen,
  timezone, locale, accept-language, device scale factor, mobile flag, or touch
  flag. Those fields come from the selected template and the region bundle.
- `proxy_region_snapshot` is a customer-safe region bucket only, such as
  `CN_MAINLAND`, `HK`, `SG`, `TW`, `JP`, `US`, or `EU`; it is not an IP,
  city, province, or proxy credential.

## Fail-Closed Enforcement

The pre-launch identity resolver must run before any browser session is opened
or attached.

Order:

1. resolve the bound account, template, and proxy policy;
2. normalize empty strings to missing values;
3. verify the identity state is compatible with the requested action;
4. validate required fields and contradictions;
5. build the Playwright/CDP launch options only from the validated identity;
6. if any required field cannot be honored, abort the launch.

Rules:

- empty string counts as missing for every required identity field;
- a locked identity may not silently fall back to process defaults;
- a locked identity may not accept a task-level proxy override;
- `CDP attach` is allowed only when the stored snapshot already matches the
  current profile and the effective values can be verified;
- `Playwright` launch must be rejected if the provider cannot honor a required
  field such as `user_agent`, `timezone`, `locale`, `accept_language`,
  `viewport`, `screen`, `device_scale_factor`, `is_mobile`, `has_touch`, or
  the bound proxy policy;
- unsupported optional metadata, such as provider-specific fingerprint
  internals, must be recorded as `not_managed` rather than silently invented;
- a validation failure must return a named error reason and must not continue
  to login or crawl.

Suggested error reasons:

- `account_identity_missing`;
- `account_identity_contradiction`;
- `account_identity_locked_proxy_override`;
- `account_identity_provider_unsupported`;
- `account_identity_snapshot_mismatch`;
- `account_identity_requires_relogin`.

## Runtime Snapshot

Add `identity_runtime_snapshot_json` to store requested and effective values.
The snapshot is customer-safe and redacted.

Snapshot shape:

```json
{
  "requested": {
    "identity_template": "CN_WIN_CHROME_1920",
    "browser_platform": "windows",
    "user_agent": "...",
    "timezone": "Asia/Shanghai",
    "locale": "zh-CN",
    "accept_language": "zh-CN,zh;q=0.9",
    "screen_width": 1920,
    "screen_height": 1080,
    "viewport_width": 1920,
    "viewport_height": 963,
    "device_scale_factor": 1,
    "is_mobile": false,
    "has_touch": false,
    "proxy_region_snapshot": "CN_MAINLAND"
  },
  "effective": {
    "user_agent": "...",
    "timezone": "...",
    "locale": "...",
    "accept_language": "...",
    "screen_width": 1920,
    "screen_height": 1080,
    "viewport_width": 1920,
    "viewport_height": 963,
    "device_scale_factor": 1,
    "is_mobile": false,
    "has_touch": false,
    "proxy_region_snapshot": "CN_MAINLAND"
  },
  "provider": {
    "name": "playwright",
    "mode": "launch",
    "version": "v1"
  },
  "probes": {
    "navigator.userAgent": "...",
    "navigator.language": "...",
    "navigator.languages": ["..."],
    "Intl.DateTimeFormat().resolvedOptions().timeZone": "...",
    "window.screen": {"width": 1920, "height": 1080},
    "window.innerSize": {"width": 1920, "height": 963},
    "window.devicePixelRatio": 1,
    "navigator.maxTouchPoints": 0,
    "navigator.webdriver": true
  },
  "unsupported_fields": [],
  "fallback_used": false,
  "validated_at": "2026-06-18T00:00:00Z"
}
```

Rules:

- write the snapshot after successful login validation and after successful
  crawl launch if the effective values are available;
- if requested and effective values differ for a required field, the launch is
  invalid and must fail closed;
- if a supported field is unavailable from the provider, fail closed instead of
  fabricating an effective value;
- `unsupported_fields` is allowed only for future/provider-dependent or
  metadata-only fields that are explicitly documented as not managed in V1;
- the snapshot must not include cookies, proxy credentials, raw profile paths,
  CDP endpoints, or noVNC session tokens.

## Audit And Diagnostics

Identity audit events:

- `identity_generated`;
- `identity_validated`;
- `identity_locked`;
- `identity_requires_relogin`;
- `identity_reset_requested`;
- `identity_reset_completed`;
- `identity_launch_failed`.

Each audit event should record:

- actor user ID or system actor;
- trigger source such as admin save, QR success, cookie success, scheduler,
  manual run, or restart recovery;
- account ID, workspace ID, platform, and template;
- old and new `identity_state`;
- old and new `proxy_region_snapshot` when relevant;
- validation or launch failure reason;
- snapshot reference or diff summary.

Admin diagnostics should surface the last runtime snapshot, the validation
reason for the last failure, and the effective-vs-requested diff without
showing secrets or raw paths.

## Account Environment Export And Import

CR-070 defines an administrator-only account migration package. It extends the
CR-047 identity model from "stable inside one deployment" to "movable between
deployments when security and compatibility checks pass".

The export/import feature is not a replacement for database backup/restore. It
is scoped to a single platform account environment:

```text
platform account + profile_key traces + account identity + login material +
platform-account metadata
```

Package modes:

- metadata-only package: exports account identity and platform-account metadata
  but excludes cookies and browser profile traces. Import must mark the
  account as needing login before crawl use. Because identity fields such as
  `fingerprint_seed` and runtime snapshots still describe a real account
  environment, the recommended V1 default is to put metadata-only exports in
  the same encrypted package envelope. A later explicitly redacted diagnostic
  export may be plaintext only if it excludes sensitive identity fields.
- slim login-state migration package: exports account identity, encrypted login
  material, platform-account metadata, proxy endpoint hint, and only the
  necessary profile state needed to attempt login-state reuse after import.
  It is not a raw copy of the whole browser profile directory.

Confirmed V1 package policy:

- V1 supports metadata-only export and a slim encrypted login-state migration
  package.
- V1 uses passphrase-based package encryption. Target-deployment public-key
  encryption remains future scope.
- V1 may include the source proxy endpoint hint such as host/IP and port inside
  the encrypted package payload, but it must not export proxy username,
  password, token, or provider secret. Audit logs, manifest summaries, and API
  responses must not expose the endpoint hint.
- V1 imports create a new target account/profile by default. Replace, merge,
  or overwrite remains future scope.
- V1 exports avatar metadata only. Cached avatar image bytes are future scope.
- V1 migration mode is a slim login-state package, not full raw profile export:
  include required login/session state and profile configuration; exclude
  cache, GPU cache, code cache, crash dumps, temporary files, large media
  cache, service-worker caches that can be regenerated, and other browser
  artifacts not needed for login-state reuse.

Package scope boundary:

- included: the selected platform account row, CR-047 identity fields,
  customer-safe platform identity metadata, encrypted proxy endpoint hint
  without credentials, target-side proxy mapping hints, optional encrypted
  login material, and optional slim profile state;
- excluded by default: monitoring tasks, crawl runs, reports, AI evaluation
  traces, email delivery logs, user records, runtime settings, full database
  backup content, customer business history, raw full browser cache, browser
  binaries, downloaded files, screenshots, and large temporary profile
  artifacts.

Manifest fields:

- package format and package version;
- package mode: `metadata_only` or `slim_login_state`;
- created time and exporting actor;
- source deployment product/schema identity version;
- source workspace, platform, account ID, account display name, login type,
  and source `profile_key`;
- target compatibility hints such as identity environment version, provider
  name, provider mode, browser family, platform, and profile format version;
- CR-047 identity summary: environment region, browser platform, template,
  timezone, locale, accept-language, viewport/screen/device class, generator
  metadata, lock state, re-login state, and redacted runtime snapshot summary;
- platform account metadata captured by the project, such as recognized
  platform account ID/name/display name, avatar metadata, last login/check
  timestamps, status, and last customer-safe error;
- proxy policy reference and `proxy_region_snapshot`, without plaintext proxy
  credentials;
- content checksums for package sections and a redacted package checksum that
  can be recorded in audit logs.

### Package Schema V1

The package format below is the accepted CR-070 V1 contract for Phase 5.2
implementation planning.

Package naming:

```text
account-environment-package-v1.maepkg
```

Logical package structure after decrypting a slim login-state migration
package:

```text
manifest.json
account/account.json
account/identity_runtime_snapshot_redacted.json
profile/slim_profile.zip
checksums/sha256.json
```

Metadata-only packages use the same manifest and account files but omit
`profile/slim_profile.zip` and any login material.

Required `manifest.json` fields:

```json
{
  "package_format": "account_environment_package",
  "package_version": "1.0",
  "package_mode": "metadata_only",
  "created_at": "2026-06-19T00:00:00Z",
  "source": {
    "product": "legal-sentiment-monitor",
    "schema_version": "current",
    "workspace_id": 1,
    "platform": "dy",
    "account_id": 123,
    "profile_key": "1/dy/acc_123"
  },
  "compatibility": {
    "identity_environment_version": "v1",
    "provider_name": "playwright",
    "provider_mode": "launch",
    "slim_profile_format": "zip-v1"
  },
  "checksums": {
    "algorithm": "sha256",
    "manifest_payload_hash": "redacted-or-full-hash-inside-package",
    "slim_profile_hash": "sha256-or-empty"
  }
}
```

Required `account/account.json` groups:

- platform account fields: platform, account display name, login type, status,
  last login/check timestamps, recognized platform account ID/name/display
  name when available, customer-safe last error, and avatar metadata;
- CR-047 identity fields: environment region, browser platform, template,
  fingerprint seed, UA, timezone, locale, accept-language, screen/viewport
  and device flags, generator metadata, identity state, lock/re-login state,
  proxy region snapshot, and redacted runtime snapshot reference;
- proxy mapping hint: source proxy ID or source proxy label only as a
  non-secret reference, source proxy region snapshot, encrypted source proxy
  endpoint hint when present, and whether target proxy mapping is required;
- import policy hint: whether metadata-only import must require login, and
  whether slim login-state import must run login verification before
  activation.

Sensitive metadata rule:

- `fingerprint_seed`, detailed runtime snapshots, recognized platform account
  IDs, and profile-derived metadata are inside the encrypted payload by
  default;
- redacted manifest summaries may include only customer-safe labels, version
  fields, package mode, platform, source/target account references, and
  checksum evidence;
- if the operator later confirms a plaintext redacted metadata export, it must
  omit `fingerprint_seed`, detailed runtime snapshots, cookies, login tokens,
  profile traces, proxy credentials, and raw profile keys.

Slim profile state rules:

- include login/session files and provider-owned storage needed to attempt
  account reuse, such as cookies, local storage, IndexedDB, storage-state
  files, preferences, login-relevant service-worker registrations, and
  session-state records where the active provider stores them;
- include CR-047 identity and launch metadata from the database rather than
  trying to infer it from browser files;
- exclude browser cache, GPU cache, code cache, media cache, crash reports,
  downloads, screenshots, temporary files, and other content that is duplicated
  across profiles or can be regenerated;
- if a provider stores login tokens inside a broader profile database, export
  the smallest provider-supported safe subset. If the subset cannot be
  separated safely, include the containing file only after redaction review and
  checksum it explicitly;
- if login-state files cannot be identified safely for a provider, fail closed
  or fall back to metadata-only export rather than exporting the whole profile
  silently.

Validation rules:

- unknown `package_format`, `package_version`, or `package_mode` fails
  preflight;
- package version compatibility is exact for V1: a V1 importer accepts only
  `package_version = "1.0"` unless a later compatibility matrix is documented;
- checksums use SHA-256 over canonical UTF-8 JSON for JSON sections and over
  raw bytes for binary sections;
- JSON fields are required unless explicitly marked optional in the
  implementation schema. Empty string counts as missing for required fields;
- raw cookies, local filesystem paths, proxy credentials, package passphrases,
  CDP endpoints, noVNC tokens, and deployment encryption keys are forbidden in
  manifest and account metadata.

Slim login-state migration package content:

- manifest;
- sanitized database export for the selected platform account only;
- encrypted Cookie/login material stored by the project, if present;
- slim profile state rooted at the account's resolved `profile_key`, including
  provider-owned cookies, localStorage, IndexedDB, preferences,
  login-relevant service-worker/session records, and session state where
  available;
- encrypted source proxy endpoint hint when present, limited to host/IP and
  port, never proxy username, password, token, or provider secret;
- avatar metadata without external signed URLs or cached image bytes.

Forbidden package content:

- plaintext cookies or platform tokens;
- plaintext proxy credentials unless a later explicit security decision allows
  it;
- proxy username, password, token, provider secret, or authentication header;
- deployment encryption keys;
- package passphrases;
- raw source or target profile paths;
- traversal paths or absolute filesystem paths;
- CDP endpoints, noVNC tokens, local command lines, or browser debug ports;
- full raw browser profile copies, browser cache, GPU cache, code cache, media
  cache, crash dumps, downloads, screenshots, and temporary profile artifacts
  unless a future provider-specific review explicitly requires one of them;
- cached avatar image bytes in V1;
- unrelated monitoring tasks, crawl runs, reports, AI traces, email delivery
  logs, or customer business data.

Encryption rules:

- slim login-state migration packages must be encrypted before leaving the
  source deployment;
- V1 package encryption uses a package-specific passphrase;
- the source deployment's stored-secret encryption key must not be exported as
  a shortcut for target import;
- metadata-only packages may still be integrity-protected and should be
  redacted, but they must not contain login material.

### Package Encryption Specification

V1 uses passphrase-based encryption. Target public-key encryption remains
future/provider-dependent.

Passphrase mode:

- use a vetted cryptography library, not custom encryption code;
- derive a 256-bit content-encryption key with Argon2id when available;
- minimum Argon2id parameters: random 16-byte salt, memory cost at least
  64 MiB, iterations at least 3, parallelism 1 or more;
- if Argon2id is unavailable, implementation must document and test a
  replacement KDF before use rather than silently weakening the package;
- encrypt the canonical package payload with AES-256-GCM using a random
  96-bit nonce;
- authenticate the clear outer header as additional authenticated data;
- never store the passphrase in the package, database, audit logs, browser
  local storage, or server logs.

Outer clear header:

- package format and version;
- encryption mode and algorithm;
- KDF name and non-secret KDF parameters;
- random salt and nonce;
- redacted package checksum or package ID for audit correlation;
- no account display name, raw profile key, cookie, proxy credential, local
  path, or platform token.

V1 passphrase-mode envelope shape:

```json
{
  "outer_header": {
    "package_format": "account_environment_package",
    "package_version": "1.0",
    "encryption_mode": "passphrase",
    "content_cipher": "AES-256-GCM",
    "kdf": "Argon2id",
    "kdf_params": {
      "memory_kib": 65536,
      "iterations": 3,
      "parallelism": 1
    },
    "salt_b64": "base64-random-salt",
    "nonce_b64": "base64-random-nonce",
    "package_id": "redacted-package-id"
  },
  "ciphertext_b64": "base64-ciphertext-with-auth-tag"
}
```

Envelope rules:

- `outer_header` is authenticated as AES-GCM additional authenticated data;
- `ciphertext_b64` contains the encrypted canonical payload and authentication
  tag as produced by the selected library;
- checksum and manifest validation happen after successful decryption;
- `outer_header` must stay account-anonymous and must not include display
  names, raw profile keys, raw profile paths, cookies, proxy credentials,
  package passphrases, CDP endpoints, noVNC tokens, or platform tokens.

Public-key mode, future scope:

- use a standard age-compatible X25519 recipient encryption flow or another
  reviewed library-based envelope encryption design;
- store only target public keys or key IDs in configuration;
- never export target private keys or the source deployment encryption key;
- document key registration, rotation, and lost-key recovery before enabling
  the mode.

Export rules:

- only administrators can export;
- export must fail or ask for retry if the account is locked by a running crawl,
  login session, or reset workflow;
- export reads only the selected account environment, not unrelated business
  data;
- export audit logs record actor, account, platform, package mode, package
  version, identity environment version, and redacted checksum evidence.

Export lock and concurrency rules:

- export fails immediately when the account has an active crawl, login session,
  reset workflow, or package import/export operation;
- export must take a short account package operation lock before reading the
  slim profile state so new login, crawl, reset, import, or export work cannot
  start for the same account mid-snapshot;
- the operation lock is released on success, failure, cancellation, timeout, or
  process interruption recovery;
- if the account state changes after preflight but before snapshot completion,
  the export fails with `account_package_state_changed` instead of producing an
  inconsistent package;
- package operation audit logs include trigger source, lock state at preflight,
  operation start/end time, terminal status, and redacted failure reason;
- V1 package operations should use a bounded internal timeout, recommended 15
  minutes, and timeout must finalize to a terminal failed or cancelled state.

### Export State Machine

Package export is a long-running operation when slim profile state is included.
It has its own operation state so cancellation, timeout, or process interruption
cannot leave an account package lock stuck.

| State | Meaning | Terminal |
| --- | --- | --- |
| `preflight` | permissions, account state, package mode, provider compatibility, and disk quota are being checked | no |
| `locked` | the account package operation lock is held | no |
| `reading_metadata` | account identity and platform-account metadata are being read | no |
| `snapshotting_profile` | slim profile state is being copied into a staging area for migration packages | no |
| `building_payload` | manifest, account metadata, checksums, and optional slim profile state are assembled | no |
| `encrypting` | the package payload is being encrypted or integrity-protected | no |
| `ready_for_download` | encrypted package artifact is ready for administrator download | yes |
| `failed` | export failed and produced no usable package | yes |
| `cancelled` | administrator or timeout cancelled the export | yes |
| `expired` | package artifact expired before download or retention cleanup | yes |
| `deleted` | package artifact was deleted after download or cleanup | yes |

Export finalization rules:

- every non-terminal state must release the package operation lock on
  success, failure, cancellation, timeout, or recovery;
- if `snapshotting_profile`, `building_payload`, or `encrypting` is
  interrupted, staged files are deleted unless the operation reaches
  `ready_for_download`;
- an export that reaches `ready_for_download` records a redacted checksum and
  expiry time, not raw package bytes in the database;
- repeated finalization for the same export operation is idempotent and must
  not recreate package bytes, reopen the account lock, or change a failed
  export into a successful one.

Import rules:

- only administrators can import;
- import begins with a preflight that validates integrity, manifest schema,
  package version, provider compatibility, identity environment version,
  source platform, slim profile state layout, and path safety;
- import creates a new target account/profile by default. The target
  `profile_key` is derived from the target workspace/platform/account ID, not
  copied as a raw source path;
- target-side proxy mapping is required when the package references a bound
  proxy policy. Import must fail closed or mark `requires_relogin` if the
  target deployment lacks a compatible proxy mapping;
- CR-047 locked identity fields may be preserved only if provider and runtime
  compatibility checks pass. Otherwise the account is imported in a
  `requires_relogin` state;
- import writes all slim profile-state files under the configured account profile
  root and rejects traversal or absolute-path entries;
- import audit logs record source package metadata, target account ID, package
  mode, compatibility result, login verification result, and redacted failure
  reason.

Import lock and concurrency rules:

- import preflight takes a package-operation lock keyed by package checksum or
  upload ID so the same package cannot be imported concurrently by two
  requests in the same workspace;
- after the target account row is created, import also locks that account and
  target `profile_key` until the import reaches a terminal state;
- import must not start a login verification while another run, login, reset,
  export, or import owns the same target account/profile;
- every terminal import state releases both package and account/profile locks;
- if the service restarts while an import is non-terminal, recovery either
  resumes from a safe checkpoint or finalizes as `failed`/`rolled_back` with a
  redacted reason.

### Target Proxy Mapping

The package never trusts a source proxy credential on the target deployment.
When the package contains a bound proxy policy, import requires an explicit
target-side mapping before the imported account can become active.

Mapping input:

```json
{
  "source_proxy_ref": "source-proxy-id-or-label",
  "source_proxy_endpoint_hint": "encrypted-host-or-ip-and-port",
  "source_proxy_region_snapshot": "CN_MAINLAND",
  "target_proxy_id": 456,
  "target_proxy_region_snapshot": "CN_MAINLAND"
}
```

Validation rules:

- if the source package says a proxy was bound, missing `target_proxy_id`
  fails preflight for activation and may only import the account as
  `requires_relogin`;
- target proxy region must match the source `proxy_region_snapshot` or another
  explicitly compatible region bundle documented by CR-047;
- target proxy must exist, belong to the target workspace, be active, and pass
  existing secret-redaction rules;
- import must not silently fall back to direct network, default network, or a
  different proxy;
- `source_proxy_endpoint_hint` may be used only inside the decrypted package
  preflight UI to help an administrator choose the matching target proxy. It
  must not be logged, audited, exposed in list APIs, or treated as usable
  proxy configuration because it lacks credentials by design;
- if the source account had no proxy policy, the import may proceed without
  target proxy mapping, but login verification still decides whether the
  account can become active.

### Import State Machine

Package import has its own operation state. It is separate from CR-047
`identity_state`, though a successful or failed import may update the account's
identity state.

| State | Meaning | Terminal |
| --- | --- | --- |
| `preflight` | manifest, integrity, permissions, and target compatibility are being checked | no |
| `preflight_failed` | package cannot be imported safely | yes |
| `decrypting` | encrypted payload is being decrypted into a temporary workspace | no |
| `extracting_profile` | slim profile state is being validated and staged | no |
| `writing_database` | target account row and redacted metadata are being written | no |
| `verifying_login` | platform login-state check is running | no |
| `active` | import and login verification succeeded | yes |
| `requires_relogin` | import preserved safe metadata/profile evidence but login or compatibility failed | yes |
| `failed` | import could not preserve a usable or diagnosable account record | yes |
| `rolled_back` | staged files and database writes were reverted after failure | yes |

Transition rules:

- `preflight -> preflight_failed` for schema, checksum, version, permission,
  package mode, proxy mapping, or path-safety failures;
- `preflight -> decrypting -> extracting_profile -> writing_database` only
  after integrity and compatibility checks pass;
- `writing_database -> verifying_login` for slim login-state migration
  packages;
- `writing_database -> requires_relogin` for metadata-only packages;
- `verifying_login -> active` only when the platform account check succeeds;
- `verifying_login -> requires_relogin` on platform rejection, verification
  timeout, verification interruption, provider mismatch, or proxy mismatch;
- any non-terminal state can move to `failed` or `rolled_back` if cleanup
  cannot preserve a safe diagnostic record.

Rollback and idempotency rules:

- profile extraction happens in a temporary staging directory first;
- staged profile files are moved under the target profile root only after path,
  quota, checksum, and account conflict checks pass;
- if database write fails before profile activation, staged files are deleted;
- if login verification fails after a safe account/profile has been written,
  keep the account for diagnosis but mark `requires_relogin`;
- importing the same package twice creates a new target account by default;
  replacing or merging an existing account is forbidden until a later conflict
  policy is confirmed;
- repeated cleanup or finalization for the same import attempt must be
  idempotent and must not reopen an `active`, `requires_relogin`, `failed`, or
  `rolled_back` terminal result.

Conflict policy:

- V1 default is create-new-account import only;
- source account IDs, display names, recognized platform account IDs, and
  source `profile_key` values are used for matching diagnostics, not for
  overwriting target rows;
- if a possible duplicate target account is detected, import may show an
  administrator warning, but it must still create a new account or stop before
  writing. Replace, merge, and in-place profile overwrite remain future scope
  until explicitly confirmed.

### Profile Snapshot Safety

Slim profile state validation must happen before extraction writes to the
target profile root.

Required checks:

- reject absolute paths, drive-letter paths, UNC paths, parent-directory
  traversal, empty path components, Windows alternate data streams, and unsafe
  reserved device names;
- reject symlinks, junctions, hardlinks, or any archive entry that would point
  outside the target profile directory;
- normalize all archive paths with `/` separators before validation;
- reject corrupt archives, unsupported compression, duplicate paths with
  conflicting checksums, and unknown slim profile state format versions;
- enforce a V1 default maximum encrypted package size of 512 MiB unless a
  later deployment setting changes it;
- enforce a V1 default maximum profile file count of 20,000 files;
- check available disk space before extraction and require at least twice the
  declared uncompressed profile size plus 256 MiB free;
- fail closed if declared size, actual size, or checksum evidence does not
  match.

Post-import verification:

- importing a file is not enough to mark an account usable;
- slim login-state migration imports must run the same platform login-state
  check used by server login reconciliation before the account can crawl;
- if verification succeeds, the account may become active under the target
  deployment's locks and identity state;
- if verification fails, the account is retained for diagnosis but marked
  `requires_relogin` and must not be silently used by the scheduler or manual
  runs;
- metadata-only imports always require login before crawl use.

Compatibility limits:

- a migrated login state can fail because platforms may bind sessions to IP,
  browser version, device trust, server time, risk score, or recent activity;
- import therefore guarantees package integrity and controlled restoration, not
  platform acceptance;
- if the target deployment uses a different provider, browser build, OS,
  profile format, proxy region, or identity environment version, import must
  report the mismatch instead of pretending the account is active.

Version compatibility rule:

- V1 import accepts only the same `package_version`, provider family, and
  `identity_environment_version` unless a later compatibility matrix is
  documented;
- if source and target identity versions differ, import may preserve metadata
  but must mark the account `requires_relogin`;
- automatic profile or identity migration across provider versions is future
  scope.

Package retention:

- generated packages are operator-download artifacts, not long-term application
  storage;
- temporary package files should be deleted after successful download or after
  a short expiry window, recommended 24 hours for temporary files;
- if `account_environment_packages` metadata is persisted, set `expires_at`
  with a recommended default of 7 days and provide cleanup diagnostics;
- package bytes must never be committed to Git or included in ordinary
  documentation artifacts.

Safe audit example:

```json
{
  "action_type": "account_package_import_completed",
  "resource_type": "social_account",
  "resource_id": 789,
  "details_json": {
    "package_mode": "slim_login_state",
    "package_version": "1.0",
    "source_platform": "dy",
    "source_account_id": "redacted-source-id",
    "target_account_id": 789,
    "identity_environment_version": "v1",
    "provider_name": "playwright",
    "compatibility_result": "matched",
    "login_verification_result": "requires_relogin",
    "redacted_checksum": "sha256:12ab...89ef",
    "failure_reason": "platform_session_rejected"
  }
}
```

Unsafe audit fields are forbidden: raw cookies, profile paths, proxy
credentials, package passphrases, CDP endpoints, noVNC tokens, local command
lines, or deployment encryption keys.

## Test Safety

Tests and local diagnostics default to no real identity side effects.

- real profile access is disabled unless `TEST_ALLOW_REAL_ACCOUNT_IDENTITY=true`;
- real proxy connection is disabled unless `TEST_ALLOW_REAL_PROXY=true`;
- real platform login is disabled unless `TEST_ALLOW_REAL_PLATFORM_LOGIN=true`;
- real account package export is disabled unless
  `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_EXPORT=true`;
- real account package import into a non-disposable workspace is disabled unless
  `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_IMPORT=true`;
- disposable profile roots and mock identity resolvers are the default for
  unit and integration tests;
- tripwires must fail the test if a real profile root, cookie store, proxy URL
  with credentials, or live login session is touched without explicit opt-in;
- package tests must use fake cookies, fake proxy references, disposable slim
  profile-state archives, and fixture package files by default;
- package tripwires must fail if fixture artifacts contain real cookie names,
  known proxy credential patterns, real profile-root prefixes, package
  passphrases, or live platform account identifiers;
- any test that validates the generator or snapshot should use a test-only
  workspace/account tuple, not a production account.

## V1 Provider Scope

V1 stays on the current Playwright/CDP provider path and does not introduce
CloakBrowser.

- V1 commits to the identity fields the current provider path can launch and
  verify consistently: browser platform, user agent, timezone, locale,
  accept-language, viewport, screen, device flags, proxy policy, and
  lock/audit state.
- V1 does not promise full spoofing for Canvas, WebGL, font inventory,
  `navigator.plugins`, extension state, or long browsing history. Those
  surfaces are future/provider-dependent because they require provider-,
  browser-build-, or profile-state-specific behavior that is outside the first
  identity-fidelity batch.
- The reason is practical, not conceptual: these signals are not just static
  launch options. They may depend on graphics drivers, browser build, OS font
  inventory, extension installation, persistent browsing history, and runtime
  JavaScript behavior. Claiming them in V1 without a dedicated provider and
  effective-value probes would create a false acceptance standard.
- Any later high-fidelity browser-persona provider must be treated as a
  separate decision with its own security, deployment, verification, and
  maintenance review.

CR-080 records a future crawler-provider architecture planning lane in
`CRAWLER_PROVIDER_ARCHITECTURE.md`. It is not the same as Phase 5.1P:
Phase 5.1P maps the current MediaCrawler/CDP/BrowserEnvironmentProvider paths
for CR-047 account identity fidelity, while CR-080 is future extensibility
planning. CR-080 must not add provider bindings, provider tables, profile
material, account fields, runtime behavior, or crawler changes without a later
accepted implementation CR and, where needed, a separate data model/migration
CR.

Provider-specific profile material such as local profile directories, remote
profile ids, cookie stores, CDP context ids, or provider-owned references must
remain behind controlled bindings. The upper-layer account identity remains
`profile_key`, and future providers must not bypass the monitor system's
account/profile/proxy locks, reset/re-login rules, redaction rules, or
server-like acceptance boundary.

Estimated future cost if high-fidelity browser-persona work is later accepted:

- read-only provider evaluation and license/deployment review: about 1-2 days;
- local prototype against one platform account and one proxy region: about
  3-5 days;
- optional provider integration with account/profile/proxy locks, redaction,
  administrator access control, and runtime snapshots: about 1-2 weeks;
- production-grade high-fidelity browser pool with extensions, long-term
  profile history policy, monitoring, rollback, and cross-platform validation:
  about 3-6+ weeks, depending on provider maturity and server constraints.

## Login Types

V1 customer-visible login types:

- QR login;
- Cookie login.

Not included in V1:

- phone login;
- SMS automation;
- captcha bypass;
- slider bypass.

Verification states must be returned to the UI rather than bypassed.

## Login State Machine

| State | Meaning |
| --- | --- |
| not_logged_in | account has no usable login material |
| preparing | server browser is opening login page |
| waiting_qrcode | QR code is available or being prepared |
| waiting_scan | waiting for operator to scan |
| waiting_confirm | scanned and waiting for mobile confirmation |
| success | login succeeded and profile is persisted |
| needs_verification | platform requires slider, captcha, SMS, or manual action |
| qrcode_failed | QR code could not be generated or the QR browser session disappeared |
| timeout | login session expired or was replaced by a newer session |
| platform_error | login verification or platform state check failed |
| invalid | existing login state is no longer usable |

Legacy login-session values are normalized for compatibility:
`waiting_manual_browser` maps to `qrcode_failed`, `waiting_verification` maps
to `needs_verification`, `scanned` maps to `waiting_confirm`, `expired` maps to
`timeout`, and `failed` maps to `platform_error`.

## New Account Flow

Preferred product flow:

1. administrator opens add-account modal;
2. administrator enters account name, platform, login type, and optional proxy;
3. if needed, administrator may choose an advanced template family before first
   login; ordinary creation leaves template selection automatic;
4. system creates a draft account environment internally;
5. system selects and validates the account identity before opening the login
   browser;
6. server browser starts a login session with the generated profile and
   identity;
7. UI displays QR/status;
8. after login success, administrator confirms save;
9. account identity is locked and the account becomes active.

If Cookie login is selected:

1. administrator enters account metadata;
2. administrator pastes Cookie;
3. system encrypts Cookie;
4. account becomes active or needs check.

## Runtime Binding

At crawl time:

1. if task has bound account, use that account;
2. otherwise select an active same-platform account in the workspace;
3. resolve its `profile_key` and, after CR-047 implementation, its locked
   account identity configuration;
4. before CR-047 implementation, use existing proxy priority: task proxy,
   account proxy, then default network;
5. after CR-047 implementation, apply the persisted user agent, browser
   platform/fingerprint inputs, timezone, locale, accept-language,
   viewport/screen/device flags, and effective proxy policy;
6. reject task-level proxy overrides for locked account environments; changing
   the proxy requires explicit reset/re-login;
7. use the same resolved environment for QR login, login-state checks, and
   crawling.

If no usable account exists for a platform, skip or fail only that platform and
record a clear reason.

The existing proxy-priority rule is reconciled for CR-047 code work: an
account-bound proxy is the stable default for a locked account environment.
Task-level proxy overrides are blocked for locked account environments. To use
another proxy, an administrator must reset the account identity and re-login
under the new proxy policy.

## Locks

Minimum V1 locks:

- account lock;
- profile lock;
- proxy concurrency lock.

Confirmed lock behavior:

- account/profile locks use inline fields on `social_accounts`;
- the account row lock also protects the account's `profile_key`;
- proxy concurrency uses `resource_locks` and enforces `max_concurrency`;
- task timeout is a run-level wall-clock deadline controlled by administrator
  Runtime Strategy;
- lock expiry follows the run deadline plus `lock_cleanup_buffer_seconds`;
- expired locks are recovery signals only and must not be reused until recovery
  verifies the owning run state.

Account/profile lock fields:

- `locked_by_run_id`;
- `locked_at`;
- `lock_expires_at`.

Proxy lock records:

- `resource_type = "proxy"`;
- `resource_id = proxy_profiles.id`;
- `run_id`;
- `locked_at`;
- `expires_at`.

Expired lock recovery rules:

1. Find expired account/profile or proxy locks.
2. Check the owning run.
3. If the run is `success`, `partial_failed`, `failed`, `timeout`,
   `cancelled`, or `interrupted`, release the lock.
4. If the run is still `running`, verify whether the owning process or job task
   is still alive.
5. If the process is no longer alive, mark the run as `interrupted` or
   `timeout`, then release the lock.
6. If the process is alive but the run deadline has passed, stop the process,
   mark the run as `timeout`, then release the lock.
7. Do not let a new run acquire an expired lock directly before recovery has
   reconciled the owning run.

Startup recovery must scan `running` runs and persisted locks after service
restart because in-memory process tracking is lost across restarts.

Implementation guidance:

- put shared recovery logic in `api/monitoring/recovery.py`, or another single
  recovery module imported by the scheduler and application startup path;
- call startup recovery before `start_scheduler()` begins launching due jobs;
- call stale-lock recovery from each scheduler tick before checking due jobs;
- recovery should query `crawl_runs.status = "running"`, compare `deadline_at`
  with current time, reconcile live process/job tracking when available, then
  release locks only after the owning run state is corrected;
- current MVP process tracking is in-memory and job-based, so Phase 5/6
  implementation must not assume run-level process tracking exists until it is
  added.

## Migration From profile_path

Confirmed direction:

- Do not keep long-term legacy compatibility for `profile_path`.
- The current account count is low and the project is still in agile
  development.
- New account environments should use `profile_key`.
- Existing accounts can be re-created or re-logged in under the new profile
  model instead of physically moving old profile directories.

Migration strategy:

1. add `profile_key`;
2. stop accepting arbitrary profile paths from the customer-facing UI;
3. create new account profiles under the new profile root;
4. mark old profile-path-based accounts as needing re-login or manual reset;
5. remove legacy profile-path dependence after validation.

## Server Acceptance

Server-like acceptance must verify:

- QR login works without local Chrome;
- profile persists after browser close;
- profile persists after service/container restart;
- two same-platform accounts have different profiles;
- same account/profile cannot run concurrently;
- proxy binding is respected during login and crawl.
