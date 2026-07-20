# Server Deployment

This document defines the V1 server deployment and server-like validation
expectations. Production acceptance must prove that users can operate the
system through the web UI without relying on the operator's local browser.

## Deployment Boundary

V1 target:

- single server;
- low concurrency;
- web UI accessed through HTTP/HTTPS;
- server-side browser automation;
- persistent database, reports, logs, and account profiles;
- administrator-managed accounts, proxies, AI, mail, and settings.

The system is not production-ready if QR login, crawling, or profile reuse only
works through a local desktop Chrome window.

## Supported Deployment Modes

Recommended first target:

- container or container-like Linux environment with mounted persistent data.

Allowed secondary target:

- systemd service on a Linux server with an installed headless browser.

Both modes must use the same server-side browser/profile behavior.

## Windows Local Startup

For Windows development or local operator use, the repository provides a
one-click launcher that can start the service and open the browser on the same
machine. The launcher should treat the service bind host and browser URL as
separate values:

- service bind host: where the FastAPI server listens;
- browser URL: what the operator's browser opens.

When the service binds to `0.0.0.0`, the browser should still open a concrete
reachable address such as `http://127.0.0.1:8080/monitor` on the local
machine. For remote or forwarded access, operators may override the browser
URL explicitly without changing the bind host.

The Windows helper scripts in the repository should follow the same rule:
`MONITOR_HOST` controls the bind address, `MONITOR_PORT` controls the port,
and `MONITOR_BROWSER_URL` overrides only the browser destination.

`start_monitor_oneclick.bat` and `start_webui.bat` require `uv` and run the
shared local browser preflight before service startup:

1. An existing deployment selection is reused. A matching explicit
   `MONITOR_BROWSER_EXECUTABLE` may confirm it; a conflicting explicit path or
   missing saved system/explicit browser stops startup.
2. A clean deployment without Profile data selects a valid explicit browser,
   then Chrome, Edge, supported Chromium, or installed Playwright Chromium.
3. Existing Profile data without a manifest preserves a valid explicit browser
   when configured; otherwise it binds to Playwright Chromium.
4. When the selected Playwright Chromium is absent, the launcher runs
   `python -m playwright install chromium` through the active project
   interpreter. Installation output remains visible and the executable is
   checked again before service startup.
5. Installer failure or failed post-install verification stops startup and
   returns `uv run playwright install chromium`.

The selection manifest stores only a contract version, browser source/channel,
and local executable path under `MONITOR_DATA_DIR`; it is not customer-facing.
Its sibling lock file is a transient cross-process synchronization artifact,
not selection data. The complete read/select/write transaction is locked so
concurrent local/service starts return the same browser.
All account Profiles remain separate by `profile_key` but share this stable
deployment browser. Browser version updates are recorded after launch and do
not change the selection. The service-only script retains operator-managed
prerequisites, and Docker retains its pinned Playwright base image.

To intentionally change browser channel, stop the service, reset/re-login the
affected account Profiles, remove `MONITOR_DATA_DIR/browser_selection.json`,
set the desired explicit executable if needed, and run a local preflight again.
Deleting only the manifest while retaining system-browser Profile data is not
a supported migration path.

## Accepted CR-112 Local Browser Auto-Sync Boundary

Status: `Accepted / Verified (Packet B)`. This is an accepted same-machine
Windows capability and does not change the production/server deployment
boundary. Packet B selected direct managed-context acquisition; Packet C/D
schema, runtime, UI, and real acceptance remain gated.

Accepted V1 topology:

```text
monitor FastAPI service + project-managed browser
on the same Windows computer
```

- Packet B selected the existing Playwright/CDP context as the replacement for
  Extension and Connector. The parent account operation retains one exact live
  context handle; no browser/client discovery or network Cookie transport is
  used.
- The standard monitor installation therefore contains no CR-112 Extension or
  Connector service. The operator does not install an Extension, create a
  personal Chrome Profile, use a Google account, place a Connector binary, or
  install Python 3.12.
- Browser resolution is valid explicit executable, Chrome, Edge, then supported
  Chromium. Chrome is preferred when Chrome and Edge both exist.
- The 2026-07-19 confirmed login-material sub-decision applies inside this
  accepted capability: QR and accepted Cookie login converge on the
  account-bound persistent Profile resolved from `profile_key`. Encrypted
  Cookie remains bootstrap/refresh/recovery/migration material.
- An existing active Profile uses the fixed-path promotion journal from
  `ACCOUNT_ENVIRONMENT.md`: same-volume candidate/rollback artifacts,
  active-path recheck, database commit, and startup recovery. Failed or
  ambiguous promotion preserves prior data or blocks only that account as
  `recovery_required`.
- The candidate is fresh from the locked Phase 5.1 provider inputs rather than
  a clone of active Profile storage. Before active-path recheck, every
  acquisition handle closes and the Profile opens through the normal provider
  without capture hooks or Cookie injection.
- After successful Profile preparation, managed crawler children receive no
  raw Cookie through argv. Clean-computer acceptance includes process
  inspection for this guarantee.
- The administrator-only full-Cookie reveal is a dedicated POST response, not
  a standard account field or deployment diagnostic. It uses no-store/no-cache
  headers and must not enter reverse-proxy access logs with a body, browser
  persistent Storage, URL, audit details, diagnostics, argv, or environment.
  Normal users receive HTTP 403 and have no frontend entry.
- The feature is disabled by default. Disabled or unhealthy state must not
  launch acquisition, choose another account/browser/Profile, or alter QR/
  manual Cookie behavior.
- Packet C is layered: C.1 is the shared advanced-manual/browser-sync
  Cookie-to-Profile promotion service, C.2 is direct acquisition/API/UI, and
  C.3 is the internal profile-only runner. The browser-sync flag controls C.2
  only. After C.3 acceptance, disabling it preserves C.1/C.3 and never restores
  raw Cookie argv.
- Only C.2 route/UI/readiness/managed-browser code reads
  `MONITOR_BROWSER_COOKIE_SYNC_ENABLED`. C.1
  startup recovery/manual Cookie and C.3 command/child/platform guards remain
  active independently. C.3 deployment pauses new runs, migrates or blocks
  every version-0 Cookie account, and resumes only after no such account is
  runnable; later version-0 runs fail before child spawn.
- Both feature states leave `/api/monitor/cookie-bridge/ws` unmounted. A normal
  HTTP probe receives 404; with the pinned Starlette/Uvicorn baseline, an
  unmatched WebSocket upgrade receives 403 before acceptance.
- The reviewed baseline is FastAPI `0.110.2` and Uvicorn `0.29.0` from exact
  project pins plus Starlette `0.37.2` from `uv.lock`. HTTP/WebSocket status is
  regression evidence; route absence and zero WebSocket protocol state remain
  mandatory if dependencies change.

Production remains server-first:

- production continues to use the server-started QR browser and persisted
  server Profile;
- local Chrome/Edge auto-sync evidence is not production acceptance;
- remote browser sync, browser-on-operator/monitor-on-server topology,
  cross-host Cookie transport, and headless direct acquisition remain outside
  the accepted V1 scope;
- a headless compatibility result may be recorded as supported or unsupported
  without changing the server QR production baseline.

CR-112 compatibility, implementation, and deployment packets remain gated by
their packet-specific provider, protocol, security, migration, test, and real-
acceptance evidence. CR-112 executes before CR-070. The separate CR-047 Linux/
server-like real acceptance remains operator-gated and CR-112 local proof does
not close it.

Before serving account checks, login, reset, export, or crawl after startup,
the monitor must reconcile non-terminal Profile-promotion journals. An
ambiguous operation blocks only the affected account as `recovery_required`;
it never guesses which directory is active or deletes the remaining copies.
The same startup lifecycle runs due committed-rollback cleanup, and a periodic
worker plus pre-refresh check enforces the 24-hour/at-most-one rule even for an
idle account.

## Required Persistent Data

Persist and back up:

```text
database
account profile root
reports
run logs
secret/encryption key
explicit account-identity seed salt when configured
monitor.yaml if used
```

CR-112 candidate/rollback operation directories are excluded from ordinary
backups and CR-070 exports. The fixed committed active
Profile is backed up only after no promotion is non-terminal and operation
cleanup has removed any retained rollback/active marker. A restore that
contains a non-terminal promotion journal runs the same recovery gate before
account use.

Never commit runtime data or real secrets to Git.

## Environment Variables

Required or expected deployment variables:

```text
MONITOR_DATA_DIR
MONITOR_DATABASE_URL
MONITOR_SECRET_KEY_PATH
MONITOR_ACCOUNT_IDENTITY_SEED_SALT
MONITOR_BROWSER_EXECUTABLE
MONITOR_BROWSER_PROXY_PROBE_URL
MONITOR_BROWSER_PROXY_PROBE_TIMEOUT_MS
MONITOR_ADMIN_EMAIL
MONITOR_ADMIN_PASSWORD
MONITOR_PORT
MONITOR_CORS_ORIGINS
MONITOR_LOGIN_QR_HEADLESS
MONITOR_ALLOW_LOCAL_LOGIN_WINDOW
```

Deployment variables that lock settings should be visible as read-only in the
administrator settings UI.

`MONITOR_ACCOUNT_IDENTITY_SEED_SALT` is optional. When omitted, Phase 5.1B
derives the identity-generator salt from the existing deployment encryption
key with a fixed purpose label. When explicitly set, back up the deployment
secret configuration containing this value together with the database and
Profiles. Losing or changing the effective salt changes future deterministic
generation and must be handled through the explicit reset/re-login lifecycle,
not silent regeneration.

`MONITOR_BROWSER_EXECUTABLE` is optional. A non-empty value is the exact
authoritative Chromium executable for managed login/check/crawl paths; an
invalid file fails closed. When empty, the server uses the Chromium executable
from the pinned Playwright installation and records source
`playwright_bundled`. Managed production paths do not select a local browser
by Chrome/Edge discovery order.

`MONITOR_BROWSER_PROXY_PROBE_URL` has no default and is required before an
account-bound proxy can be used. The provider opens it through the bound
browser proxy before returning the context. It must return a JSON object whose
`region` exactly matches the account's safe `proxy_region_snapshot`. The URL,
response, external IP, and proxy secret are not logged or persisted.
`MONITOR_BROWSER_PROXY_PROBE_TIMEOUT_MS` controls only this proof and defaults
to `30000`. Explicit-direct accounts do not call the probe and record
`effect_proof=not_applicable`.

`MONITOR_BROWSER_ENVIRONMENT_PLAN` and
`MONITOR_BROWSER_ENVIRONMENT_RESULT_PATH` are bounded Runner-to-child internal
handoff variables. Operators must not set them in `.env`, container, systemd,
or secret-manager configuration. Each attempt receives a new binding; the
child consumes/removes the plan before browser launch and atomically writes a
safe result that the parent validates before ingesting crawler output.

Production deployments should set:

```text
MONITOR_LOGIN_QR_HEADLESS=true
MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false
```

`MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=true` is only a development fallback for
operators working on a desktop machine. It is not an acceptance path for V1.

## Browser Requirements

The server environment must provide a browser that can run headless and persist
profiles.

Acceptance requirements:

- QR login is initiated by the server;
- QR code or structured status is shown in the web UI;
- account profile is written under the configured profile root;
- closing the browser does not delete login state;
- restarting the service/container preserves login state;
- separate platform accounts use separate profile directories.
- managed QR/Profile/Cookie/crawl paths use the same account-derived provider
  plan and exact `profile_key` directory;
- an account-bound proxy passes the configured browser-routed region proof, or
  the login/crawl attempt stops before platform work;
- managed CDP connect-existing, local browser auto-detection, generic Profile,
  process proxy, and CDP-to-standard fallback do not satisfy acceptance.

If the platform requires manual verification, the server should return a
structured `needs_verification` state instead of attempting bypass behavior.
If QR generation fails, the server should return `qrcode_failed` and a
customer-safe message. In production mode, local-window login endpoints should
return a permission error and direct administrators back to the web QR flow.

## Container Checklist

Minimum container build requirements:

- base image provides Python 3.11 or newer;
- recommended base image: official Playwright Python image for the pinned
  Playwright version, such as `mcr.microsoft.com/playwright/python:*`;
- acceptable fallback: `python:3.11-slim` with explicit Playwright browser and
  system dependency installation;
- install application dependencies;
- install Playwright Chromium and required system dependencies;
- copy application code into the image;
- expose `MONITOR_PORT`;
- mount persistent storage for `MONITOR_DATA_DIR`;
- provide deployment environment variables through an env file or secret
  manager;
- start the FastAPI service through the same command used by production.

The first container/server-like environment should verify:

1. service starts with no desktop browser on the operator machine;
2. web UI is reachable by URL;
3. initial administrator can log in;
4. database and profile root are mounted to persistent storage;
5. server browser can start in headless mode;
6. QR login can be completed through the web UI;
7. profile survives service/container restart;
8. scheduled task can run using the server-side profile;
9. local-window login fallback is disabled;
10. logs do not expose secrets, cookies, proxy credentials, or raw profile
    paths.

## systemd Checklist

For direct server deployment:

1. run the service as a dedicated non-root user where possible;
2. set environment variables through a deployment env file;
3. point data and profile roots to persistent server paths;
4. install the browser and required system libraries;
5. enable service restart on failure;
6. configure reverse proxy and HTTPS before production exposure;
7. ensure backups include database, profiles, reports, and encryption key.

## Reverse Proxy And HTTPS

Production exposure should use a reverse proxy such as Nginx or Caddy.

Required behavior:

- preserve secure cookies;
- forward client IP headers where audit logs need them;
- restrict CORS to trusted origins;
- avoid exposing internal diagnostic routes publicly.
- do not add or forward `/api/monitor/cookie-bridge/` in any production or
  remotely reachable reverse-proxy configuration, including WebSocket upgrade
  handling. The selected local product path has no Cookie-bridge endpoint.

CR-112 acceptance proves direct and proxied HTTP/WebSocket probes cannot reach
Cookie acquisition state because the route is absent.

## Public Exposure Boundary

CR-093 accepts the product boundary that MediaCrawler is an internal collection
engine, not the public product cockpit. The exact route, mount, reverse-proxy,
and 404-vs-403 strategy still needs confirmation after a read-only route audit.

Default production exposure should be designed around:

- `/monitor`;
- `/api/auth/...`;
- `/api/monitor/...`;
- monitor-specific static assets;
- necessary authenticated report/download/avatar cache resources.

Old MediaCrawler WebUI surfaces, raw crawler/data APIs, websocket diagnostics,
direct crawler-control paths, raw file browsing/preview/download paths, generic
old static/logo paths, local command lines, profile paths, cookies, and proxy
credentials must not be publicly exposed as product surfaces. If the current
formal monitor workflow still depends on an old route, that dependency must be
recorded with a replacement path before the route is denied, unmounted, or
hidden behind administrator-only diagnostics.

CR-094 provider architecture is a future planning lane. Production crawler
providers must still satisfy the server-like/container admission rule here:
they cannot require the operator's local desktop browser as the production
runtime.

## Backup And Restore

Minimum backup set:

- database;
- account profile root;
- reports;
- encryption key;
- deployment configuration.

Restore validation must include:

- service starts after restore;
- administrator login works;
- account profiles can be reused;
- a report can be opened from restored data;
- System Diagnostics shows acceptable database, disk-space, backup-set,
  retention-setting, account-alert, and proxy-alert checks before pilot use.

## Account Environment Migration Packages

CR-070 defines an account-level migration path that is narrower than full
backup/restore. Backup/restore moves an entire deployment. An account
environment package moves one selected platform account environment to another
deployment.

Package scope:

- account identity metadata;
- platform account metadata captured by the project;
- optional encrypted login material;
- optional encrypted slim profile state rooted at `profile_key`;
- proxy mapping requirement and redacted region snapshot.
- optional encrypted source proxy host/IP plus port hint for target-side
  mapping, without proxy username, password, token, authentication header, or
  provider secret.

Deployment operators should treat slim login-state migration packages as
sensitive runtime artifacts:

- store them outside Git;
- encrypt them with a package passphrase before transfer;
- transfer them only through an operator-approved channel;
- delete or archive them according to a short retention policy after import;
- never paste package passphrases, raw cookies, proxy endpoint hints, proxy
  credentials, or local profile paths into issue trackers, chat logs,
  screenshots, or project documents.

Slim package boundary:

- export login/session state and provider profile configuration needed to
  attempt account reuse;
- exclude raw browser cache, GPU cache, code cache, media cache, crash dumps,
  downloads, screenshots, temporary files, and duplicated or regenerable
  browser artifacts by default;
- export avatar metadata only, not cached avatar image bytes.

Target deployment import requirements:

1. verify package integrity and manifest version;
2. verify browser/provider and identity-environment compatibility;
3. map any source proxy policy to a target-side proxy or mark the account as
   needing re-login;
4. write slim profile-state files only under the configured account profile root;
5. run login-state verification before allowing crawl use;
6. audit the import result without raw secrets or paths.

Import success means the target deployment restored the package safely and the
platform login-state check passed. If the platform rejects the migrated
session, the account should remain imported for diagnosis but marked
`requires_relogin`.

## Email Delivery Evidence Management

Unexpected report emails, orphan delivery logs, and detached report artifacts
must be treated as evidence first, not as cleanup candidates.

Read-only review steps:

1. identify the delivery-log row and note `job_id`, `report_id`, recipient
   snapshot, send time, and delivery status;
2. locate the matching report artifact files and any exported `.eml` message;
3. check whether the original job, run, or report rows still exist;
4. classify the case as orphaned only when the delivery record no longer has a
   live job/report owner in the database;
5. preserve the database row, report file, and message file together until an
   operator explicitly approves any mutation.

Dry-run helper:

```bash
uv run python scripts/review_orphan_email_evidence.py --job-id 9686 --json
uv run python scripts/review_orphan_email_evidence.py --job-id 9759 --json
```

The helper opens the SQLite database read-only, inspects delivery-log rows,
checks whether related job/report/run records and report artifacts exist, and
prints `mutations_attempted: 0`. It does not delete, annotate, repair, or
rewrite database rows or artifact files. Use `--delivery-log-id`, `--job-id`,
or `--report-id` to narrow the review; use `--database` and `--artifact-root`
when inspecting a copied backup outside the default data directory.

Recorded CR-036 evidence:

- delivery-log row `60`, `job_id=9686`, `run_id=8380`, `report_id=3959`,
  sent automatic email at `2026-06-16T07:27:11Z`, attachments
  job_9686_run_8380_20260616_152702.xlsx and
  job_9686_run_8380_20260616_152702.md, exported message
  `C:/Users/Administrator/Desktop/日报 海安律所.eml`;
- delivery-log row `81`, `job_id=9759`, `run_id=8447`, `report_id=3998`,
  sent automatic email at `2026-06-16T08:55:33Z`, attachments
  job_9759_run_8447_20260616_165528.xlsx and
  job_9759_run_8447_20260616_165528.md, exported message
  `C:/Users/Administrator/Desktop/日报 海安律所.2eml.eml`;
- the corresponding `monitor_jobs`, `crawl_runs`, and `reports` rows were no
  longer present during read-only inspection, so these rows are preserved as
  historical orphan email evidence by default.

Default policy:

- do not delete, annotate, or rewrite historical delivery evidence during
  investigation;
- back up the database and the relevant report/email artifacts before any
  approved mutation;
- record the approval reason, operator, backup location, and rollback plan
  before taking action;
- keep restored or archived reports readable for normal support review.

If cleanup is ever approved, handle it as a separate operator-gated repair
task. Evidence review itself should remain read-only.

## Encryption Key Management

V1 behavior:

- use one encryption key for stored secrets;
- create or load the key from `MONITOR_SECRET_KEY_PATH` or the configured data
  directory;
- do not include automatic key rotation in V1.

If the key is compromised:

1. stop the service;
2. back up the database and deployment data;
3. replace the compromised key;
4. restart the service;
5. re-enter encrypted secrets such as proxy URLs, API keys, SMTP passwords,
   cookies, and account login material;
6. record the event in the audit log once audit logging exists.

Automated key rotation is deferred until after V1.

## Server-Like Acceptance

Before production handoff, run the server-like tests in `TEST_PLAN.md` and
record results in `TEST_RESULTS.md`.

Automated server-like validation can be run from the deployment worktree with:

```bash
uv run python scripts/server_like_validation.py
```

The script starts a real FastAPI HTTP service with isolated persistent data
directories, `MONITOR_LOGIN_QR_HEADLESS=true`,
`MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`, scheduler disabled, AI skipped, and
server-side profile roots. It validates web reachability, administrator login,
web QR/status login capability, local-window login blocking, separate
same-platform profiles, profile metadata across service restart, runtime
account/profile/proxy locks, and headless Chromium availability.

Acceptance cannot be marked complete until:

- local desktop Chrome is not used;
- the web UI controls login;
- server-side profile persistence is verified across restart;
- concurrency limits are verified for account/profile/proxy resources.
