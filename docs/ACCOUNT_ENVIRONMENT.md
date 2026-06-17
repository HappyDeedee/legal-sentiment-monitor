# Account Environment

This document defines the relationship between platform accounts, profiles,
proxies, browser sessions, login sessions, and crawl runs.

## Core Model

```text
Task -> Platform Account -> Profile -> Proxy -> Server Browser Session
```

Rules:

- one platform account maps to one profile;
- one profile cannot be used by two browser sessions at the same time;
- one platform account cannot be used by two crawl runs at the same time;
- proxy priority is task proxy, account proxy, then default network;
- login and crawling should use the same proxy when a proxy is bound.

Accepted CR-047 target rule:

```text
one platform account = one profile_key = one fixed browser environment
```

The fixed browser environment means that server-side login, login-state
checks, and crawling for the same platform account should reuse the same
persisted profile, user agent, browser platform fingerprint family, timezone,
locale, screen size, fingerprint seed, and proxy policy.

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
- browser_platform;
- fingerprint_seed;
- user_agent;
- timezone;
- locale;
- screen_width;
- screen_height;
- browser_environment_locked_at;
- browser_environment_lock_reason;
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

The CR-047 browser-environment fields are accepted for future implementation,
not yet implemented in the current runtime. They should be assigned before the
first QR login or accepted Cookie login validation and locked after the account
environment becomes usable. Silent edits after successful login are not
allowed; changing a locked environment requires an explicit reset/re-login flow
with audit logging.

Reference note:

- CloakBrowser-Manager is a useful reference for stable profile settings such
  as browser platform, fingerprint seed, user agent, timezone, locale, screen
  size, proxy, CDP, and noVNC.
- This project should absorb that account-environment model, but should not
  copy CloakBrowser-Manager's standalone account center, database, frontend,
  authentication model, or deployment layout without a separate provider
  decision.

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
3. system creates a draft account environment internally;
4. server browser starts a login session with the draft profile;
5. UI displays QR/status;
6. after login success, administrator confirms save;
7. account becomes active.

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
   browser-environment configuration;
4. before CR-047 implementation, use existing proxy priority: task proxy,
   account proxy, then default network;
5. after CR-047 implementation, apply the persisted user agent, browser
   platform/fingerprint inputs, timezone, locale, screen size, and effective
   proxy policy;
6. use the same resolved environment for QR login, login-state checks, and
   crawling.

If no usable account exists for a platform, skip or fail only that platform and
record a clear reason.

The existing proxy-priority rule must be reconciled before CR-047 code work: an
account-bound proxy is the stable default for the account environment. A
task-level proxy override must either be a visible explicit exception or be
blocked for fixed-environment accounts according to the final implementation
decision.

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
