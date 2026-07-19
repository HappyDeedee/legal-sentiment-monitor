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

## Proposed CR-112 Local Browser Auto-Sync Boundary

Status: `Needs Confirmation`. This is a proposed local Windows capability and
does not change the accepted production/server deployment boundary.

Proposed V1 topology:

```text
monitor FastAPI service + project-owned connector route + managed browser
on the same Windows computer
```

- The connector is a feature-gated WebSocket module in the existing Python
  3.11 FastAPI process, not a separate Python 3.12 product service.
- The extension connects through `127.0.0.1` and the effective monitor port.
  Non-loopback and cross-host endpoints remain disabled.
- The WebSocket handler authorizes locality from the ASGI socket peer
  (`websocket.client.host` / `scope["client"]`) using a literal IP loopback
  check. It rejects an empty, unparsable, or non-loopback peer before accepting
  the socket, even when FastAPI listens on `0.0.0.0`.
- `X-Forwarded-For`, `Forwarded`, and similar proxy headers are ignored for the
  loopback authorization decision. A future trusted-proxy/remote topology
  requires a separate accepted CR rather than broadening this route.
- The handshake requires the exact allowlisted
  `chrome-extension://<stable-extension-id>` Origin. Missing, opaque, or
  unexpected Origins and invalid peers are rejected before protocol state or
  Cookie access.
- The standard monitor installation contains the project-owned extension and
  creates its per-session managed copy automatically. The operator does not
  install an extension manually, create a personal Chrome Profile, use a Google
  account, place a connector binary, or install Python 3.12.
- Browser resolution is valid explicit executable, Chrome, Edge, then supported
  Chromium. Chrome is preferred when Chrome and Edge both exist.
- The feature is disabled by default. Disabled or unhealthy state must not
  mount a usable connector path, load the extension, generate pairing tokens,
  choose another account/client, or alter QR/manual Cookie behavior.
- Disabled startup does not mount `/api/monitor/cookie-bridge/ws`, so direct
  HTTP/WebSocket access receives 404. When enabled, invalid peer or Origin is
  rejected before WebSocket acceptance and must not create session, client,
  pairing, audit-success, or Cookie-read state.

Production remains server-first:

- production continues to use the server-started QR browser and persisted
  server Profile;
- local Chrome/Edge auto-sync evidence is not production acceptance;
- remote Bridge, browser-on-operator/monitor-on-server topology, cross-host
  Cookie transport, and headless Bridge remain outside the proposed V1 scope;
- a headless compatibility result may be recorded as supported or unsupported
  without changing the server QR production baseline.

CR-112 compatibility, implementation, and deployment packets remain gated by
confirmation, Phase 5.1 acceptance, the existing CR-070 sequence or a later
accepted sequencing decision, project-owned protocol proof, data-model and
migration approval, and clean-computer acceptance.

## Required Persistent Data

Persist and back up:

```text
database
account profile root
reports
run logs
secret/encryption key
monitor.yaml if used
```

Never commit runtime data or real secrets to Git.

## Environment Variables

Required or expected deployment variables:

```text
MONITOR_DATA_DIR
MONITOR_DATABASE_URL
MONITOR_SECRET_KEY_PATH
MONITOR_BROWSER_EXECUTABLE
MONITOR_ADMIN_EMAIL
MONITOR_ADMIN_PASSWORD
MONITOR_PORT
MONITOR_CORS_ORIGINS
MONITOR_LOGIN_QR_HEADLESS
MONITOR_ALLOW_LOCAL_LOGIN_WINDOW
```

Deployment variables that lock settings should be visible as read-only in the
administrator settings UI.

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
- deny and do not forward `/api/monitor/cookie-bridge/` in every production or
  remotely reachable reverse-proxy configuration, including WebSocket upgrade
  handling. The local extension connects directly to the loopback monitor
  endpoint and never through the public proxy.

CR-112 acceptance includes negative probes through the machine LAN address and
configured reverse proxy, plus spoofed `X-Forwarded-For`/`Forwarded` headers.
All must fail before connector protocol state. Only a direct loopback peer with
the exact extension Origin may proceed to pairing authentication.

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
