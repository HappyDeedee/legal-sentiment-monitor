# Current State

Last updated: 2026-06-16

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
Data Layer is complete and verified. Phase 13B - Operations Home Desktop
Visual Metrics is complete and verified. Phase 13C - Operations Home
Responsive And Role Views is complete and verified. Phase 14 - Run Center
Data Model Preparation is complete and verified. Phase 15A - Run Center API
And Data Governance is complete and verified. Phase 15B - Run Center Frontend
Refinement is complete and verified. Phase 16 - Email Delivery Data Model
Preparation is the next allowed execution goal.
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
  landing, grouped account/logout controls, Phase 12B standardized page
  entries with task-loop shortcuts for administrator and normal-user paths,
  Phase 13A dashboard API operations-home aggregates for task health, run
  activity, report activity, email delivery latest state, suspected lead
  metrics, and role-safe resource health, Phase 13B desktop operations
  home visual metrics with drilldowns, and Phase 13C responsive operations
  home role views with detailed diagnostics moved to System Diagnostics, and
  Phase 14 run-center data-model fields for run visibility, run type,
  archived time, and archived user with visible/scheduled backfill and
  recommended indexes, plus Phase 15A run-center API/query pagination,
  filters, default visible-only listing, administrator-only archived access,
  archive/restore APIs, and response metadata for pagination, filters,
  visibility, and run type, plus Phase 15B run-center frontend pagination,
  filters, default operational-record view, administrator archive/restore row
  controls with confirmation, and responsive run-center verification.

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
- Phase 13 - Overview Operations Home Redesign: complete and verified
  through Phase 13A-13C.
- Phase 14 - Run Center Data Model Preparation: complete and verified.
- Phase 15 - Run Center Governance And Frontend: complete and verified through
  Phase 15A-15B.
- Phase 16 - Email Delivery Data Model Preparation: planned, not implemented.
- Phase 17 - Email Delivery Governance: planned as Phase 17A-17B, not
  implemented.
- Phase 18 - Report Center Task Grouping: planned as Phase 18A-18B, not
  implemented.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; Phase 5 account environment runtime and
  Phase 6 login-flow runtime are complete.

The documented V1 product roadmap is implemented through Phase 9 in this
worktree, and the console optimization roadmap is verified through Phase 15B.
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

- Phase 16 execution preparation. No Phase 16 email delivery data-model
  implementation work is in progress yet.

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
- Phase 16-18 plans depend on future implementation and verification. The
  current frontend has the complete Phase 11-12 foundation and Phase 13A data
  contract: local static module
  boundary, base desktop shell/navigation/button/card/toolbar styling, shared
  interaction helper/fixed floating-menu behavior, responsive
  desktop/tablet/mobile navigation/layout rules, expandable navigation groups,
  operations-home landing, and standardized page entries with role-safe
  task-loop shortcuts, plus role-scoped operations-home aggregates on
  `/api/monitor/dashboard`, a Phase 13B desktop operations-home view with
  visual metric cards and task-loop drilldowns, and Phase 13C tablet/mobile
  role views with concise administrator health and normal-user business-safe
  resource wording. The current schema also has Phase 14 run visibility and
  run type fields, and Phase 15A exposes the corresponding run-center
  governance API layer. Phase 15B now wires that API into the run-center
  frontend with pagination, filters, archive/restore actions, and operational
  versus test/noise separation.
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
- Phase 13A added an operations-home API data contract under the existing
  dashboard endpoint, preserving old summary fields while exposing task
  health, run activity, report activity, email delivery latest state,
  suspected lead metrics, and concise resource health for Phase 13B/13C.
- Phase 13B replaced the default text-heavy overview with desktop visual
  operations metrics, role-safe drilldowns, concise resource health, and a
  collapsed administrator diagnostics section while keeping the Phase 13A API
  contract and old dashboard compatibility.
- Phase 13C adapted the operations home for 1024px tablet and 390px mobile,
  kept normal-user metrics business-safe, moved detailed readiness/scheduler/
  platform diagnostics to System Diagnostics, and retained only a compact
  administrator health summary on the home page.
- Email idempotency and report task grouping are accepted data-model directions
  but are not active schema features yet. Run visibility/noise-filtering data
  fields are active schema features after Phase 14, and archive/restore APIs,
  pagination, and filters are active after Phase 15A. Frontend run-center
  controls are active after Phase 15B. Email delivery logs remain Phase 16
  work.
- The first global Phase 10-18 review found that Phase 13, Phase 17, and Phase
  18 were too coarse as single goals. The plan now splits them into data/API
  and frontend/responsive batches.
- Phase 10.5 follow-up global review found no remaining P0/P1 blockers.
  Remaining review notes are P2 implementation refinements and do not block
  Phase 15B.

## Next Step

Next allowed implementation step:

1. start Phase 16 only;
2. add the `email_delivery_logs` data model according to `DATA_MODEL.md` and
   `SCHEMA_MIGRATION.md`;
3. verify migration, fields, indexes or uniqueness rules, backfill
   compatibility, and rollback risk before Phase 17A;
4. preserve existing report generation, resend, preview, download, and
   run-center behavior while adding the delivery-log foundation.

## Latest Verification

Phase 15B run center frontend refinement verification on 2026-06-16:

- Added run-center pagination controls and page metadata rendering.
- Added task/law-firm, status, platform, run type, visibility, date, and page
  size filters wired to the Phase 15A run-list API.
- Added the default `run_type=operational` view so scheduled/manual
  operational records are separated from `test` noise records unless the user
  explicitly filters for test/diagnostic records.
- Added administrator-only archive and restore row actions with confirmation.
  Normal users keep visible-record scope and cannot request archived/all
  records.
- Preserved run-log drawer behavior, including refresh, copy, download, and
  customer-safe log text.
- Verified `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200 in the isolated browser
  service.
- Verified desktop 1440px, tablet 1024px, and mobile 390px run-center
  layouts keep filters, status, actions, summary, pagination, and table
  content reachable without horizontal page overflow.
- Verified administrator archive/restore API behavior through the running
  browser service: run ID 1 moved from visible to archived and restored back
  to visible. Verified normal-user API scope returns `403` for archived
  visibility and archive action.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15b or phase_15a"`
- Result: 2 passed, 226 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15b or phase_15a or phase_14 or run_logs or list_runs"`
- Result: 4 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 228 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check
- Result: PASS.

Phase 15A run center API and data governance verification on 2026-06-16:

- Added run API/query pagination with `pagination` response metadata while
  preserving existing `runs` and `running_job_ids` response fields.
- Added filters for task ID, law firm, status, platform, run type, visibility,
  and date range.
- Added administrator-only archive and restore APIs that update run visibility
  without physically deleting records.
- Default run-list API behavior now hides archived records; administrators can
  request archived or all records explicitly, while normal users cannot.
- Preserved owner/workspace scope, existing status values, report links, and
  run-log access for visible runs.
- Did not add Phase 15B frontend pagination, filter controls, or row
  archive/restore controls.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15a or run_logs or list_runs"`
- Result: 2 passed, 225 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 227 passed, 3 warnings.

Phase 14 run center data model preparation verification on 2026-06-16:

- Added `crawl_runs.visibility`, `crawl_runs.run_type`,
  `crawl_runs.archived_at`, and `crawl_runs.archived_by` to new database
  creation and compatible existing-database migration.
- Backfilled empty existing run rows to `visibility = visible` and
  `run_type = scheduled`.
- Added `idx_crawl_runs_visibility` on
  `(workspace_id, visibility, started_at)` and `idx_crawl_runs_type_status` on
  `(workspace_id, run_type, status)` for Phase 15 filters.
- Verified existing run reads, run list reads, report links, and status values
  remain readable after the migration.
- Did not add Phase 15 pagination, filters, archive/restore APIs, frontend
  controls, email delivery logs, or report grouping.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_14 or phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 13 passed, 213 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 226 passed, 3 warnings.

Phase 13C operations home responsive and role views verification on
2026-06-16:

- Adapted the operations home for tablet and mobile so metric cards, drilldown
  entries, resource signals, and administrator health summary wrap without
  horizontal overflow.
- Replaced the home-page detailed diagnostics block with a compact
  administrator-only system health summary and moved detailed readiness,
  scheduler, platform status, and checklist sections to System Diagnostics.
- Preserved normal-user business-safe resource wording and kept administrator
  resource-health drilldowns and System Diagnostics hidden from normal users.
- Preserved the Phase 13A dashboard API contract and did not add schema,
  email-delivery-log, run-archive, or report-grouping fields.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 12 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` and
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator 1440px, 1024px, and 390px checks found five metric cards
  and no horizontal overflow; administrator System Diagnostics drilldown showed
  readiness, scheduler, and platform status details; normal-user 1024px and
  390px checks found business-safe resource wording, no administrator health
  summary, no account/system-diagnostics shortcuts, no horizontal overflow, and
  task drawer, Run Center, Report Center, and logout paths remained reachable.

Phase 13B operations home desktop visual metrics verification on
2026-06-16:

- Replaced the default text-heavy Overview content with an operations-home
  metric surface rendered from the Phase 13A `operations_home` contract, while
  preserving a legacy dashboard summary fallback during migration.
- Added five desktop visual metric cards for task health, run activity, report
  and review status, email delivery latest state, and suspected negative
  leads.
- Added task-loop drilldowns into Monitoring, Run Center, Report Center,
  report email delivery status, and administrator platform-account resources
  where permitted.
- Kept system readiness, scheduler, and platform diagnostics under a collapsed
  administrator-only diagnostics section instead of the default first-screen
  home content.
- Used native HTML/CSS with existing CSS tokens and did not add a chart
  library or other frontend dependency, so no new `DECISIONS.md` entry was
  required.
- Preserved normal-user role safety: normal users receive business-safe
  resource wording and do not see administrator resource drilldowns or system
  diagnostics.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 11 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` and
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator and normal-user authenticated console paths had no page
  or console errors; administrator 1440px, 1024px, and 390px checks found five
  metric cards and no horizontal overflow; administrator drilldowns reached
  jobs, runs, reports, email delivery status, and accounts; diagnostics were
  collapsed by default; normal-user navigation exposed only `总览`, `舆情监控`,
  `运行中心`, and `报告中心`; normal users saw `资源由管理员维护`, no resource
  drilldown, and no system diagnostics.

Phase 13A operations home data layer verification on
2026-06-15:

- Added `summary.operations_home` to the existing dashboard summary contract
  and returned the same object as top-level `operations_home` from
  `/api/monitor/dashboard` for the Phase 13B frontend migration.
- Preserved existing flat dashboard fields such as `jobs_total`,
  `runs_total`, `reports_total`, `contents_total`,
  `failed_runs_recent`, `skipped_runs_recent`, and administrator resource
  totals.
- Aggregated task health, run activity, report activity, email delivery latest
  state from `reports.email_status`, suspected lead metrics from
  `ai_evaluations`, and concise resource health from existing persisted data.
- Preserved administrator workspace-wide visibility and normal-user
  owner/workspace scoping; normal users receive business-safe resource health
  without platform account, proxy, AI profile, or login-session counts.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_13a`
- Result: 1 passed, 222 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 10 passed, 213 deselected, 3 warnings.

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
