# CR-132 Windows Login Bootstrap And Bounded Browser Startup

## Metadata

- CR: CR-132
- Type: regression fix
- Status: Implementation Verified / Operator Acceptance Pending
- Baseline: `main@a0a8583`
- Branch: `codex/cr-132-windows-login-bootstrap`
- Owner: project implementation lane
- Primary risk: account-bound browser startup and cleanup on a clean Windows
  computer

## Baseline

The affected computer selects and persists Chrome successfully, starts the
FastAPI service, and serves `/monitor`. QR creation then times out for Douyin
and Xiaohongshu, browser auto-sync is not enabled by the Windows launchers, the
visible-browser fallback rejects an unsaved account, and timeout cleanup can
leave the initiating request in a loading state.

## Goal

Make a fresh Windows local checkout reach QR or Browser login through the
selected project browser with bounded startup, actionable stage reporting, and
the existing account/Profile authority.

## In Scope

- Windows local launcher defaults and spawned-process health ownership.
- New named account persistence before either Browser implementation.
- Managed QR and browser-sync startup stages, timeouts, and cleanup bounds.
- Driver-owned failed-start process reaping and cleanup-before-rollback order.
- Local visible-login stage reporting and frontend request bounds.
- Focused, adjacent, full, browser, documentation, and review gates.

## Out Of Scope

- Schema, crawler request identity, proxy scheduling, account rotation,
  Profile export/import, or production/server browser topology.
- CAPTCHA, slider, SMS, or platform verification bypass.
- Real account/Profile/Cookie mutation during automated tests.

## Hard Boundaries

1. The committed account Profile remains browser and crawl authority.
2. Browser-sync and manual Cookie promotion keep their existing journal,
   identity, rollback, and secret-redaction rules.
3. One account retains one current login attempt across QR, Browser, visible
   fallback, and Cookie entry.
4. Explicit environment values override Windows local defaults.
5. Docker and service-only production defaults remain server-first.
6. Logs and responses contain stage names and safe IDs only, never Cookie,
   Profile paths, proxy credentials, URLs with secrets, or debug endpoints.
7. Profile directories are mutated only after validation cleanup completes; an
   unconfirmed cleanup is retained as `recovery_required` for explicit repair.

## Start Gate And Dependencies

- CR-117, CR-120, CR-122, and CR-127 are verified historical dependencies.
- The operator confirmed local browser auto-sync by default and direct Browser
  entry for a named unsaved account.
- The branch is clean at `a0a8583`; CR-131 remains a separate unmerged lane.

## Expected Touch Surface

- `start_monitor_oneclick.bat`, `start_webui.bat`
- `api/main.py`, `api/monitoring/startup_launcher.py`
- `api/monitoring/login_qrcode.py`
- `api/monitoring/login_browser_sync.py`
- `api/monitoring/login_browser.py`
- `api/monitoring/account_check.py`
- `api/monitoring/profile_promotion.py`
- `tools/browser_environment.py`
- `api/monitor_web/index.html`
- `tests/test_monitoring_mvp.py`
- CR-132 formal documents

## Execution Steps

1. Add deterministic RED coverage for the observed launcher, frontend, timeout,
   and cleanup gaps.
2. Apply local defaults and bind one-click health to its spawned process.
3. Persist a new named account before visible Browser fallback.
4. Add safe startup stages and bounded QR/browser cleanup.
5. Run targeted tests, fix failures, then run adjacent and complete regression.
6. Verify the rendered login modal and local service, synchronize documents,
   and complete independent read-only review.

## Acceptance

- A clean Windows launcher exposes Browser auto-sync without a manual flag.
- QR startup and browser startup terminate with a specific stage on failure.
- A named unsaved account enters either Browser path after one draft save.
- No stale service satisfies one-click startup health.
- Account/Profile/Cookie authority and production defaults remain unchanged.

## Rollback And Recovery

Revert the CR-132 code and local launcher defaults as one unit. Existing
database rows, account Profiles, browser selection manifests, and encrypted
Cookie material require no migration or rollback. A failed login attempt keeps
the prior committed authority and closes or terminalizes only its own session.

## Documentation Updates

Update `CHANGE_REQUESTS.md`, `TASKS.md`, `CURRENT_STATE.md`, `DECISIONS.md`,
`ACCOUNT_ENVIRONMENT.md`, `SERVER_DEPLOYMENT.md`, `PRODUCT_REQUIREMENTS.md`,
`UI_UX_GUIDELINES.md`, `TEST_PLAN.md`, `TEST_RESULTS.md`, and
`TRACEABILITY.md` when verification closes.

## Stop Conditions

- A change would weaken account-attempt arbitration or Profile promotion.
- A cleanup path cannot prove bounded termination without touching unrelated
  browser processes.
- A test or log exposes Cookie, Profile path, proxy credentials, or platform
  secrets.
- The fix requires a second browser-selection authority or production topology
  change.
