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
```

Deployment variables that lock settings should be visible as read-only in the
administrator settings UI.

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

## Container Checklist

Minimum container build requirements:

- base image provides Python 3.11 or newer;
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
9. logs do not expose secrets, cookies, proxy credentials, or raw profile paths.

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
- a report can be opened from restored data.

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

Acceptance cannot be marked complete until:

- local desktop Chrome is not used;
- the web UI controls login;
- server-side profile persistence is verified across restart;
- concurrency limits are verified for account/profile/proxy resources.
