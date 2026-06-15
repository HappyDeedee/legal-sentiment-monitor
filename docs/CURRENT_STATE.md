# Current State

Last updated: 2026-06-15

## Current Phase

Phase 0 documentation is complete. Phase 0.5 - Schema Foundation is complete
and verified. Phase 1 - Users And Permissions is complete and verified. Phase
2 - System Settings Center is complete and verified. Phase 3 - Administrator
Resource Center is complete and verified. Phase 4 - Normal User Task Wizard is
complete and verified. Phase 5 - Account Environment is complete and verified.
Phase 6 - Server Login Flow is complete and verified locally. Phase 7 - Runs,
Reports, And AI is complete and verified locally. Phase 8 - Server-Like
Validation is complete and verified through an isolated server-like service
process. Phase 9 - Security And Operations is complete and verified locally.
Phase 10-18 console optimization planning has been accepted as the next
roadmap. Phase 10 - Frontend Architecture And Technology Decision is complete
as a documentation and architecture decision phase. Phase 10.5 - Phase 10-18
Global Plan Review Gate is complete and found no P0/P1 blockers after the
granularity refinements. Phase 11 - Frontend Design System is complete and
verified through Phase 11A, Phase 11B, Phase 11C, and Phase 11D. Phase 12A -
Navigation Structure And Login Landing is complete and verified. Phase 12B -
Page Entry And Role Flow is complete and verified. Phase 13A - Operations Home
Data Layer is the next allowed execution goal.
The active SQLite schema now provides the foundation tables and columns
required before later implementation work, and the web/API layer now has
session login, administrator/normal-user roles, menu visibility,
owner-scoped business data access, administrator-managed runtime strategy
settings, administrator resource pages with consistent summary, toolbar, modal,
and test interactions, a normal-user task wizard with administrator-only
advanced options, and profile-key based account environments with persisted
account/profile/proxy locks, stale-run recovery, server-side QR login as the
primary administrator flow, structured login states, profile persistence/reuse
checks, deployment gating for local-window login fallback, AI/manual-review
fallback, email-failure-tolerant report generation, report-specific lead
preview switching, run log refresh/copy/download controls, and an automated
server-like validation script that starts the real FastAPI service with
production login flags, persistent profile roots, service restart checks, and
headless browser verification, administrator-operation audit logs, sensitive
value redaction, resource-alert diagnostics, backup guidance, disk-space
  diagnostics, retention-setting diagnostics, Phase 11 local static frontend
  assets, base shell/navigation visual styles, fixed floating-menu behavior,
  responsive desktop/tablet/mobile navigation and layout foundations, Phase
  12A expandable primary navigation groups, operations-home login/session
  landing, grouped account/logout controls, and Phase 12B standardized page
  entries with task-loop shortcuts for administrator and normal-user paths.

## Implementation Status

- Phase 0 - Documentation: complete.
- Phase 0.5 - Schema Foundation: complete and verified.
- Phase 1 - Users And Permissions: complete and verified.
- Phase 2 - System Settings: complete and verified.
- Phase 3 - Administrator Resource Center: complete and verified.
- Phase 4 - Normal User Task Wizard: complete and verified.
- Phase 5 - Account Environment: complete and verified.
- Phase 6 - Server Login Flow: complete and verified locally.
- Phase 7 - Runs, Reports, And AI: complete and verified locally.
- Phase 8 - Server-Like Validation: complete and verified through automated
  server-like validation.
- Phase 9 - Security And Operations: complete and verified locally.
- Phase 10 - Frontend Architecture And Technology Decision: complete as a
  documentation and architecture decision phase.
- Phase 10.5 - Phase 10-18 Global Plan Review Gate: complete as a
  documentation-only review gate.
- Phase 11 - Frontend Design System: complete and verified through Phase
  11A-11D.
- Phase 12 - Navigation And Page Entry Redesign: complete and verified through
  Phase 12A-12B.
- Phase 13 - Overview Operations Home Redesign: planned as Phase 13A-13C;
  Phase 13A is the next allowed execution goal and is not implemented.
- Phase 14 - Run Center Data Model Preparation: planned, not implemented.
- Phase 15 - Run Center Governance And Frontend: planned, not implemented.
- Phase 16 - Email Delivery Data Model Preparation: planned, not implemented.
- Phase 17 - Email Delivery Governance: planned as Phase 17A-17B, not
  implemented.
- Phase 18 - Report Center Task Grouping: planned as Phase 18A-18B, not
  implemented.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; Phase 5 account environment runtime and
  Phase 6 login-flow runtime are complete.

The documented V1 product roadmap is implemented through Phase 9 in this
worktree, and the console optimization roadmap is verified through Phase 12B.
Production pilot handoff still requires live platform, SMTP, and AI-provider
validation with real deployment credentials.

## Completed

- Project direction has been clarified as a server-deployed ToB law-firm
  public-opinion monitoring system.
- The first-version boundary has been clarified as single-server,
  low-concurrency, administrator-managed resources, and normal-user task
  creation.
- The role split has been clarified:
  - system administrator maintains account pool, proxies, AI, email, templates,
    runtime strategy, and users;
  - normal user configures platforms, content, frequency, and recipient emails.
- The account-environment model has been clarified:
  task -> platform account -> profile -> proxy -> server browser.
- Server-like validation has been made mandatory for production acceptance.
- Initial governance documents have been added.
- Menu-level product requirements have been documented.
- Change request intake, traceability, and agent workflow documents have been
  added.
- A confirmation gate has been added: ambiguous high-impact requirements must
  be confirmed by the user before becoming accepted product or architecture
  decisions.
- P0 implementation specifications for roles, account environment, runtime
  settings, and data model have been added as planning documents.
- A permission confirmation pack, compatible schema migration plan, and runtime
  configuration example have been added.
- API authentication/authorization and server deployment guides have been
  added.
- Documentation consistency check specification and Phase 0.5 test coverage
  have been added.
- Permission, workspace, authentication, initial administrator, disabled-user
  behavior, audit-log timing, and runtime settings storage decisions have been
  accepted using the V1 recommended options.
- Phase 0.5 schema foundation has been implemented in
  `api/monitoring/database.py`: default workspace, user/session/settings/audit
  tables, ownership columns, profile keys, run timeout fields, account lock
  fields, and proxy `resource_locks`.
- Existing monitoring MVP task/account/login/run/report records still load
  after the schema foundation migration.
- Phase 1 user and permission foundation has been implemented:
  environment-bootstrap administrator creation, bcrypt password hashes,
  session-token cookies backed by `user_sessions`, user management APIs,
  shared FastAPI auth/role dependencies, administrator-only resource APIs,
  normal-user owner scope for jobs/runs/reports/leads, and frontend login/menu
  visibility.
- `scripts/check_docs.py` has been implemented and currently passes.
- Phase 2 runtime strategy has been implemented:
  `api/monitoring/settings.py` defines runtime defaults, YAML mapping,
  validation ranges, apply scopes, and environment locks; `system_settings`
  stores database overrides with audit logging; administrators can edit grouped
  Runtime Strategy tables; normal users cannot access runtime settings APIs;
  scheduler tick/disable, crawl concurrency, crawler retry, run-level timeout,
  QR timeout, login session TTL, lock cleanup buffer, and retention settings
  now read through the runtime settings layer.
- Newly started crawl runs copy `crawler_timeout_seconds` into
  `crawl_runs.timeout_seconds`, compute `deadline_at`, allocate remaining run
  time to platform crawler attempts, and mark deadline-exceeded runs as
  `timeout` while preserving partial platform results.
- Phase 3 administrator resource center has been refined:
  platform accounts keep the single account-detail dialog, proxy resources have
  summary cards plus search/status filters, AI access has summary cards plus
  protocol/test-status filters and a connection-test dialog, mail configuration
  uses edit/test dialogs with masked password behavior, and mail templates have
  summary cards plus search/status filters and live preview.
- Phase 4 normal-user task creation has been simplified:
  normal users see a four-step task wizard for target, collection content,
  schedule, and report recipients; crawl range copy explains the actual V1
  boundaries; account/proxy/AI/template/browser fields are hidden from normal
  users; the API also clears those advanced fields for normal-user create/edit
  requests; administrators still keep advanced task binding controls.
- Phase 5 account environment runtime has been implemented:
  account profile runtime paths are derived from stable `profile_key` values,
  new account environments ignore arbitrary customer-provided profile paths,
  account names are display labels only, account/profile summaries no longer
  expose real server paths, account/profile locks use inline
  `social_accounts` fields, proxy concurrency uses `resource_locks`, run
  cleanup releases locks, and startup/scheduler recovery reconciles timed-out
  running runs before releasing persisted locks.
- Phase 6 server login flow has been implemented:
  administrator account login now starts from server-side QR sessions by
  default, login APIs and the frontend use structured states (`preparing`,
  `waiting_qrcode`, `waiting_scan`, `waiting_confirm`, `success`,
  `needs_verification`, `qrcode_failed`, `timeout`, and `platform_error`),
  legacy login states are normalized for compatibility, successful login is
  re-checked before the account is marked active, profile-key paths are reused
  after the browser session closes, and `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`
  hides and blocks local-window login fallback for production mode.
- Phase 7 runs, reports, and AI behavior has been verified:
  jobs can complete with AI disabled and email unavailable, new contents enter
  `pending_review` instead of blocking report generation, report wording keeps
  "suspected negative leads" semantics and avoids factual conclusions, report
  preview requests load leads scoped to the selected report ID, and run logs
  expose refresh, copy, and download controls with customer-safe text.
- Phase 8 server-like validation has been implemented and verified:
  `scripts/server_like_validation.py` starts the real FastAPI app as an HTTP
  service with isolated persistent data directories, production login flags
  (`MONITOR_LOGIN_QR_HEADLESS=true` and
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`), bootstrap administrator login,
  web QR/status capability checks, local-window login blocking,
  same-platform account profile separation, profile metadata persistence across
  service restart, account/profile/proxy runtime lock enforcement, and
  headless Playwright Chromium availability.
- Phase 9 security and operations has been implemented and verified:
  administrator resource changes write minimal `audit_logs` records without
  plaintext secrets, sensitive text redaction covers API keys, passwords,
  cookies, proxy credentials, encrypted-field labels, and Chinese secret
  labels, readiness now surfaces account invalidation and proxy-error alert
  paths, doctor diagnostics include disk-space, retention-setting, backup-set,
  and resource-alert checks, and deployment docs describe database, profile,
  report, encryption-key, and configuration backups.
- Phase 10-18 console optimization requirements have been accepted in
  documentation:
  - navigation and page entries will be rebuilt around the monitoring task
    loop;
  - the frontend design system will combine Apple-style visual language,
    interaction patterns, and responsive behavior;
  - the operations home will replace the text-heavy overview;
  - run center governance will use logical archive and noise filtering;
  - email automatic sending will use delivery logs and schedule-window
    idempotency;
  - report center grouping will use monitoring task grouping and
    `job_snapshot_json` for orphan report history;
  - the frontend technology stack remains Vanilla JavaScript plus CSS custom
    properties for this redesign round.

## In Progress

- Phase 13A execution preparation. No Phase 13A-18 implementation work is in
  progress.

## Known Risks

- Phase 5 still stores `profile_path` as a transition-only internal runtime
  field for existing login/crawler code paths, but new identity and path
  resolution are `profile_key` based and customer-facing responses mask real
  paths.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR/login capability and profile persistence now have automated
  server-like validation, but real platform QR scanning and real platform
  crawling still require a live server/account pilot.
- The newly added product documents are initial versions and should be refined
  during implementation.
- Profile migration strategy has been clarified: existing low-volume
  `profile_path` accounts do not need long-term compatibility and can be reset
  or re-logged in under the new `profile_key` model.
- Phase 2/9 retention settings are configurable and visible in diagnostics,
  but automated retention cleanup jobs remain for later operations work.
- Docker/container validation could not be run on this machine. Phase 8 used
  an isolated real FastAPI service process with persistent temp data instead.
- Phase 7 and Phase 8 automated checks do not prove real AI provider, SMTP,
  real platform QR scanning, or real platform crawling behavior; those remain
  deployment and pilot risks.
- Phase 13A-18 plans depend on future implementation and verification. The
  current frontend has the complete Phase 11-12 foundation: local static module
  boundary, base desktop shell/navigation/button/card/toolbar styling, shared
  interaction helper/fixed floating-menu behavior, responsive
  desktop/tablet/mobile navigation/layout rules, expandable navigation groups,
  operations-home landing, and standardized page entries with role-safe
  task-loop shortcuts.
- Phase 11 was completed as four verified batches: Phase 11A module boundary
  and tokens, Phase 11B base layout/navigation visual foundation, Phase 11C
  interaction components and floating menus, and Phase 11D responsive
  foundation.
- Phase 12A replaced detached Resource Management and System Configuration
  popover navigation with expandable groups, routed login/session restore to
  Operations Home, and grouped user identity/logout controls for desktop and
  mobile.
- Phase 12B standardized page entry headers and task-loop shortcuts across
  Operations Home, Monitoring, Run Center, Report Center, resource pages, mail
  configuration, runtime settings, and system diagnostics while preserving
  normal-user role boundaries.
- Email idempotency, run archive/noise filtering, and report task grouping are
  accepted data-model directions but are not active schema features yet.
- The first global Phase 10-18 review found that Phase 13, Phase 17, and Phase
  18 were too coarse as single goals. The plan now splits them into data/API
  and frontend/responsive batches.
- Phase 10.5 follow-up global review found no remaining P0/P1 blockers.
  Remaining review notes are P2 implementation refinements and do not block
  Phase 13A.

## Next Step

Next allowed implementation step:

1. start Phase 13A only;
2. define the operations-home data contract under the existing monitor API
   surface;
3. aggregate task health, run activity, report activity, email delivery status,
   suspected lead metrics, and concise resource health from real persisted data
   or documented empty states;
4. preserve administrator and normal-user owner/workspace scope before moving
   to Phase 13B.

## Latest Verification

Phase 12B page entry and role flow verification on
2026-06-15:

- Standardized page entry headers across Operations Home, Monitoring, Run
  Center, Report Center, account resources, proxy resources, AI access, AI
  rules, mail configuration, mail templates, runtime settings, and system
  diagnostics.
- Added task-loop shortcuts for creating a monitoring task, viewing runs,
  viewing reports, checking report email delivery status, and resolving
  administrator resource issues where permitted.
- Replaced the header refresh affordance with current-page refresh behavior
  and kept Operations Home using the existing `dashboard` route ID.
- Preserved Phase 12A expandable navigation, login/session landing,
  account/logout grouping, and role visibility behavior.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator path exposed 12 page entries and 5 Operations Home
  shortcuts; task-loop shortcuts opened the task drawer and navigated jobs ->
  runs -> reports; the report email delivery entry was visible; normal-user
  navigation only exposed `总览`, `舆情监控`, `运行中心`, and `报告中心`; normal-user
  Operations Home exposed 4 task-loop shortcuts and no administrator resource
  shortcuts; 1440px, 1024px, and 390px checks found no business-area horizontal
  overflow; mobile navigation opened, switched to Monitoring, and closed; page
  console errors were empty.

Phase 12A navigation structure and login landing verification on
2026-06-15:

- Replaced detached hover popovers for Resource Management and System
  Configuration with expandable navigation groups in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`.
- Routed successful login and session restore to Operations Home when no
  explicit allowed destination is present.
- Grouped authenticated user identity and logout in the desktop top-right
  account area and added a predictable mobile account area in the navigation
  drawer.
- Preserved administrator and normal-user menu visibility rules.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; form login and session restore landed on `dashboard`; administrator
  groups expanded/collapsed; mobile nested navigation reached
  `email_templates` and closed the drawer; normal-user navigation only exposed
  `总览`, `舆情监控`, `运行中心`, and `报告中心`; authenticated console/page errors
  were empty.

Phase 11D responsive foundation verification on
2026-06-15:

- Implemented the accepted desktop `>= 1280px`, tablet `768px - 1279px`, and
  mobile `< 768px` breakpoint foundation in `api/webui/monitor/monitor.css`.
- Added touch-safe mobile navigation hooks in `api/monitor_web/index.html`:
  hamburger toggle, primary sidebar/navigation IDs, and a navigation backdrop.
- Added mobile navigation behavior for open, backdrop close, Escape close,
  page-switch close, and desktop-resize reset.
- Kept dense tables scroll-safe on mobile while leaving page-specific card
  conversions to later page phases.
- Added a normal-user frontend permission guard so mail-template preview
  polling does not call administrator-only endpoints.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator and normal-user authenticated paths loaded with no
  console/page errors; 1440px, 1024px, and 390px checks covered navigation,
  task-create entry, run log drawer, report preview drawer, and report action
  menu.

Phase 11C interaction components and floating menu verification on
2026-06-15:

- Added shared toast, loading, empty-state, modal, drawer, and action-menu
  styles to `api/webui/monitor/monitor.css`.
- Added the `window.MonitorUI` helper boundary in
  `api/webui/monitor/monitor.js` with toast, loading, empty-state,
  close-menu, portal-root, and fixed floating-menu positioning helpers.
- Reworked account, monitoring-task, AI-rule, and report row menus to use
  fixed viewport placement through local helpers instead of a new dependency.
- Verified row menus close on outside click, Escape, page change, and action
  execution. Proxy, AI access, and mail-template surfaces currently use direct
  edit/test/preview actions and have no row-menu clipping surface in this
  batch.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or phase_11c or monitor_page_uses"`
- Result: 5 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright authenticated interaction check:
  account, monitoring-task, AI-rule, and report menus used `position: fixed`,
  stayed inside the viewport, and closed on outside click and Escape; run
  center and report center smoke checks passed at 1024px and 390px.

Phase 11B base layout and navigation visual foundation verification on
2026-06-15:

- Moved base shell, side navigation, header, button, card, metric-card,
  toolbar, page-toolbar, toolbar-action, and page-action styling into
  `api/webui/monitor/monitor.css`.
- Kept page IDs, navigation data attributes, inline JavaScript behavior,
  business data flow, and role/menu visibility unchanged.
- Preserved table, modal, form, report-preview, task-wizard, AI-rule,
  mail-template, and resource-specific styling for later batches.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or monitor_page_uses"`
- Result: 4 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright desktop 1440px authenticated smoke check:
  login, logout, dashboard, monitoring task list, run center, report center,
  task-create entry, Resource Management popover, and System Configuration
  popover remained reachable with no console or page errors.

Phase 11A frontend module boundary verification on 2026-06-15:

- Added `api/webui/monitor/monitor.css` and
  `api/webui/monitor/monitor.js`.
- Referenced `/static/monitor/monitor.css` before the existing inline
  `<style>` block and `/static/monitor/monitor.js` after the existing inline
  `<script>` block.
- Kept existing inline CSS/JS behavior in place; no visible UI redesign was
  introduced.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or monitor_page_uses"`
- Result: 3 passed, 214 deselected, 4 warnings.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright authenticated smoke check at 1440px, 1024px, and 390px:
  dashboard, monitoring task list, run center, report center, and task-create
  entry remained reachable with no console or page errors.

Phase 10-18 documentation planning verification on 2026-06-15:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Phase 10.5 global roadmap review verification on 2026-06-15:

- Phase 10-18 global复审 result: PASS; no P0/P1 blockers.
- Phase 13, Phase 17, and Phase 18 have been split into smaller execution
  batches.
- Phase 11A is allowed as the next execution goal.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Phase 10 frontend architecture verification on 2026-06-15:

- Frontend structure audit found the monitor console is served from
  `api/monitor_web/index.html`, over 4,000 lines long, with inline CSS and
  JavaScript and coarse `1100px`/`720px` breakpoints.
- The FastAPI app keeps `/monitor` as the direct console entry and already
  exposes `/static` for local static assets.
- Decision: keep `/monitor` and the no-build path, but Phase 11 should split
  the design-system layer into local CSS/JS modules instead of expanding the
  inline file.
- Follow-up planning refinement: Phase 11 is split into 11A-11D, Phase 12 is
  split into 12A-12B, and Phase 15 is split into 15A-15B so each batch can be
  executed and verified with a bounded goal.

Phase 9 security and operations verification passed on 2026-06-14:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_9 or doctor_reports_deployment_diagnostics or readiness_status_reports_checks or sensitive_text_is_redacted"`
- Result: 6 passed, 210 deselected, 1 warning.
- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed: service web UI reachable, administrator
  login over HTTP, web QR/status login flow primary, local-window login
  disabled, same-platform profiles separated, profile-key runtime paths under
  the persistent profile root, account/profile lock limit enforced through
  runtime API, proxy lock enforced through `resource_locks`, profile metadata
  survives restart, no local Chrome dependency, and headless Playwright
  Chromium available.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 216 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Earlier Phase 7 and Phase 8 verification remains recorded in
`docs/TEST_RESULTS.md`.
