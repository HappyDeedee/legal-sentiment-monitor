# Current State

Last updated: 2026-06-17

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
Preparation is complete and verified. Phase 17A - Email Idempotency And
Delivery Logic is complete and verified. Phase 17B - Email Delivery History
Frontend is complete and verified. Phase 18A - Report Job Snapshot Data Model
is complete and verified. Phase 18B - Report Center Task Grouping Frontend is
complete and verified. Phase 10-18 console optimization is complete through
the accepted roadmap. Phase 19A - Requirement Intake Classification Rules is
complete and verified as a documentation-governance update. CR-031 Run Center
Realtime Progress Visibility is accepted as the next run-center optimization
requirement, but its product code is not implemented yet. CR-033 Formal
Console Full-Coverage Positive UI Optimization is complete and verified as a
frontend-only pass on the latest formal `/monitor` console; it does not change
backend APIs, database schema, permissions, crawler behavior, AI provider
logic, SMTP delivery, or Phase 19B-19D product scope. The CR-033 pass now also
includes stable secondary drawer/modal button-level loading feedback for
account login, resource saves, AI/mail tests, and template preview actions.
CR-034 Run Detail And AI Evaluation Traceability is accepted as Phase 20, but
implementation has not started. Trace retention must be an
administrator-configurable runtime setting with a 30-day default, not a
hard-coded value. Permission visibility is also confirmed: normal users see
only business-safe summaries for their own runs, administrators may see
redacted prompt/request/response debug snapshots, and unredacted raw responses
must not be exposed. Trace storage uses a new `ai_evaluation_traces` table
with capped/redacted JSON fields and accepted default size guardrails. CR-035
Run Lifecycle Finalization And AI Stuck
Recovery Regression Fix is accepted as a follow-up for the completed Phase 7
responsibility area; Phase 7 remains a historical verified snapshot, while
Phase 7.1 is the accepted regression-fix task block for the newly observed
stuck-run class. Phase 7.1A-C is now implemented and verified locally: new
runs persist `crawl_runs.job_id`, compatible legacy summary-based reads and
dry-run backfill are available, run finalization is idempotent, terminal
statuses are protected from stale writers, Phase 7.1 lifecycle heartbeats are
persisted in `crawl_runs.summary`, stale Phase 7.1 rows can recover as
`interrupted` without auto-repairing older historical rows, AI item
timeout/exception/invalid-result paths fall back to `pending_review`, and
partial/manual-review reports can still be generated. CR-036 Test And Local Email Delivery Safety Regression Fix is
accepted as a follow-up for the completed
Phase 17 email-delivery responsibility area after two unexpected real
`日报 海安律所` emails were traced to temporary test/local run records and
unmocked SMTP delivery. Phase 17 remains a historical verified snapshot, while
Phase 17.1 is the accepted regression-fix task block for preventing tests and
local diagnostics from sending hidden real external mail while preserving an
explicit production/pilot real-mail validation path. Phase 17.1A-B is now
implemented and verified locally with an environment-controlled real SMTP
safety gate, read-only deployment runtime visibility, default non-sending
automated/local/report-delivery behavior, explicit opt-in SMTP validation
tests, and a suite-level SMTP tripwire. Phase 17.1C and Phase 17.2A backend
metadata for effective recipients, trigger source, and effective template
provenance is also implemented and verified for report snapshots and delivery
logs; remaining operator-facing copy/preflight explanation and historical
email/template explanation work stays open. Historical unexpected email
evidence is confirmed to be preserved by default. CR-037 Role-Based
Email Delivery Governance And Quotas is deferred as a future capability for
administrator-managed normal-user send/resend policy and quotas. CR-040 Formal
Console Page-Level UI/UX Refinement is accepted as Phase 21, a frontend-only
implementation phase with `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` as the
execution-plan reference; Phase 21 code work has not started yet and no
production frontend code has been changed for CR-040 in the planning update.
The Phase 21 plan now explicitly treats prototype-observed layout collapse as
a hard production risk: dashboard cards, closed-loop tracks, dense status
cards, resource cards, run/report cards, and secondary overlays must not
squeeze text into one-character vertical columns, overlap content, hide
primary actions, or create horizontal overflow at `1440x900`, `1024x768`, or
`390x844`. Phase 21 also explicitly excludes the currently unrendered
`Users And Permissions` page; implementing that page would require a separate
new-capability CR. CR-041 Minimum Usable Pilot Acceptance Gate is accepted as
the current "system can be used first" readiness standard: first pilot use is
blocked by the remaining real-external portion of the minimum server-like
workflow; hidden-real-email safety and stuck-run lifecycle safety have both
been implemented, locally verified, and externally reviewed. Automated
server-like validation also passes, and a default-safe Pilot Gate C evidence
template/checker is available for operator-filled real-workflow proof. The
evidence checker is not a substitute for live credentials: pilot validation
with a real platform account/session, one real crawl, explicit-opt-in real SMTP
credentials, and real-run redaction evidence is still required before the
whole gate can be closed. CR-041 is not blocked by Phase 21 visual refinement,
CR-038 drawer accessibility, Phase 19 realtime progress, Phase 20 AI
traceability, or CR-037 role/quota governance unless a later accepted P0
regression changes that boundary.
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
  home role views with detailed diagnostics moved to System Diagnostics,
  CR-033 dashboard data-first visual polish, unclipped floating menus,
  page-shaped loading states, secondary overlay loading feedback, and mobile
  dashboard density reduction, and
  Phase 14 run-center data-model fields for run visibility, run type,
  archived time, and archived user with visible/scheduled backfill and
  recommended indexes, plus Phase 15A run-center API/query pagination,
  filters, default visible-only listing, administrator-only archived access,
  archive/restore APIs, and response metadata for pagination, filters,
  visibility, and run type, plus Phase 15B run-center frontend pagination,
  filters, default operational-record view, administrator archive/restore row
  controls with confirmation, and responsive run-center verification, plus
  Phase 16 email delivery log schema, send-window key helper, delivery-log
  insert/list helpers, customer-safe delivery-log text handling, partial
  unique automatic-send window protection, and Phase 17A scheduler/report
  delivery logic that records automatic attempts, skips duplicate automatic
  sends by schedule window, logs failures without blocking report generation,
  records manual resend separately, keeps report latest-state fields readable,
  and Phase 17B report-center delivery-history UI/API surfaces latest delivery
  state, automatic/manual delivery history, recipient summaries, and
  customer-safe delivery errors without exposing SMTP secrets, plus Phase
  17.1A-B real SMTP safety gating blocks automated/local hidden external sends
  by default, records blocked deliveries as customer-safe skipped states,
  keeps explicit opt-in pilot validation available, and installs an automated
  SMTP tripwire, plus Phase 17.1C/17.2A backend delivery metadata records
  effective recipients, recipient source, trigger source, and effective email
  template provenance for new report snapshots and delivery logs, plus Phase 18A
  report snapshots store task context for new and backfilled reports while
  keeping unrecoverable historical reports readable with limited context, and
  Phase 18B groups report-center rows by active task or stored snapshot while
  preserving preview, lead switching, downloads, delivery history, and row
  actions.

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
- Phase 7.1 - Runs, Reports, And AI Stuck Recovery Follow-up: partially
  complete and verified locally. Phase 7.1A-C is implemented: new runs persist
  `crawl_runs.job_id`, legacy `summary.job_id` rows are read compatibly and
  dry-run backfillable when resolvable, terminal finalization is idempotent,
  Phase 7.1 lifecycle summaries include phase/heartbeat/retry/error/progress
  evidence, stale Phase 7.1 rows can recover as `interrupted` after the
  confirmed evidence checks, AI item timeout/exception/invalid-result paths
  fall back to `pending_review`, and partial/manual-review reports can be
  generated. Phase 7.1D historical run `8317` remediation remains open and
  still requires backup, rollback, dry-run preview, and explicit operator
  approval.
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
- Phase 16 - Email Delivery Data Model Preparation: complete and verified.
- Phase 17 - Email Delivery Governance: complete and verified through Phase
  17A-17B.
- Phase 17.1 - Email Delivery Safety Follow-up: partially complete and
  verified locally. Phase 17.1A-B real SMTP safety gate and automated-test
  tripwire are implemented. Phase 17.1C backend effective-recipient
  traceability is implemented for report delivery and delivery logs. Remaining
  Phase 17.1C operator-facing preflight/UI copy and Phase 17.1D historical
  orphan evidence operations notes are still open.
- Phase 17.2 - Report Email Template Governance: partially complete and
  verified locally. Phase 17.2A backend effective-template provenance is
  implemented for new report snapshots and email delivery logs. Phase 17.2B-C
  report-body guardrails, preview semantics, and preset-style governance remain
  accepted follow-up work.
- Phase 18 - Report Center Task Grouping: complete and verified through Phase
  18A-18B.
- Phase 19 - Run Center Realtime Progress And Requirement Intake Governance:
  Phase 19A documentation-governance rules are complete and verified; Phase
  19B-19D run-center realtime progress implementation is accepted but not
  started.
- Phase 20 - Run Detail And AI Evaluation Traceability: accepted but not
  implemented. Confirmed scope includes configurable `ai_trace_retention_days`
  with a 30-day default, normal-user business-safe summaries only,
  administrator redacted prompt/request/response debug snapshots, no
  unredacted raw responses for any role, new `ai_evaluation_traces` storage,
  and default trace size guardrails.
- Phase 21 - Formal Console Page-Level UI/UX Refinement: accepted but not
  implemented. This is a frontend-only formal console refinement phase covering
  global shell/design tokens, navigation hierarchy, Operations Home,
  Monitoring, Platform Accounts, Proxies, AI Access, AI Rules, Mail
  Configuration, Mail Templates, Runtime Strategy, Run Center, Report Center,
  System Diagnostics, Login, and cross-page verification.
- Minimum Usable Pilot Acceptance Gate: accepted but not satisfied. CR-036 /
  Phase 17.1A-B email side-effect safety and CR-035/Phase 7.1A-C run
  lifecycle/AI fallback/partial-report safety are implemented, locally
  verified, and read-only externally reviewed. Automated server-like validation
  passes without relying on the operator's local Chrome. A no-side-effect
  Pilot Gate C evidence checker now provides a structured way to validate
  redacted operator proof for the remaining real workflow. The gate still
  requires a real platform login/crawl path with a persistent server-side
  account profile, explicit-opt-in real SMTP validation with operator
  credentials, real-run redaction proof, and a passing operator evidence JSON
  check before the system is described as ready for first pilot use.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; Phase 5 account environment runtime and
  Phase 6 login-flow runtime are complete.

The documented V1 product roadmap is implemented through Phase 9 in this
worktree, and the console optimization roadmap is verified through Phase 18B.
Production pilot handoff still requires live platform, SMTP, and AI-provider
validation with real deployment credentials. CR-041 now defines the narrower
first usable pilot gate before that handoff can be described as ready.

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
  after the browser session closes, QR-session failures are reconciled against
  same-account MediaCrawler account/Profile validation before showing failure,
  and `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false` hides and blocks local-window
  login fallback for production mode.
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
- Phase 19 requirement-documentation rules have been added:
  future CRs must classify whether they are a new capability, existing feature
  optimization, regression fix, or documentation-governance change, and must
  include background, purpose, boundaries, related tasks, and acceptance
  criteria.
- CR-031 Run Center Realtime Progress Visibility has been accepted:
  active runs should show provisional collection progress before platform
  subprocess completion, AI progress should update during long evaluation
  batches, and frontend polling should continue while visible runs remain
  active. This is documented but not implemented.
- CR-035 Run Lifecycle Finalization And AI Stuck Recovery Regression Fix has
  been recorded as a follow-up regression fix after live task `9297` / run
  `8317` showed collection and partial AI evaluation had progressed while the
  persisted run remained `running`. The fix is documented as Phase 7.1 and
  should precede or be explicitly separated from Phase 19B-19D progress-display
  work. User confirmation on 2026-06-16 accepted `interrupted` as a distinct
  terminal state, active pending-review fallback for unresolved AI candidates,
  AI evaluation progress counts, and prevention-first `job_id` persistence.
  A later confirmation accepted evidence-based stale recovery, a 10-minute
  heartbeat grace period, retry-before-timeout behavior, and
  `ai_item_timeout_seconds=120`.
- CR-036 Test And Local Email Delivery Safety Regression Fix has been recorded
  as a follow-up regression fix after two real emails were traced to temporary
  `海安律所` test/local jobs: `job_id=9686/run_id=8380` and
  `job_id=9759/run_id=8447`. The corresponding automatic delivery logs show
  `status=sent`, while the current `monitor_jobs`, `crawl_runs`, and `reports`
  rows no longer exist for those IDs. The strongest local trigger evidence is
  `test_run_job_blocks_platform_when_login_window_is_open`, which calls
  `run_monitor_job` without mocking report email delivery. The fix is
  documented as Phase 17.1 and should be handled separately from Phase 19 run
  progress and Phase 20 AI traceability. User confirmation on 2026-06-16
  accepted preserving the historical unexpected-email evidence by default, then
  accepted environment-controlled real-email gating, read-only runtime
  visibility, non-sending local/test behavior by default, explicit real-mail
  validation support, and trigger-source/effective-recipient traceability.
- CR-037 Role-Based Email Delivery Governance And Quotas has been recorded as
  a deferred future capability after the user clarified that administrator
  authority, normal-user email send/resend restrictions, and possible daily
  quotas may be needed later. It is not part of the immediate CR-036 safety
  fix.
- CR-040 Formal Console Page-Level UI/UX Refinement has been accepted as Phase
  21. The standalone execution plan defines per-page preservation rules,
  allowed visual changes, testing, verification, and acceptance criteria. The
  planning update does not change code and does not reopen CR-033; Phase 21
  implementation work remains not started.
- CR-034 Run Detail And AI Evaluation Traceability has been accepted as a
  run-center optimization with data-model implications. The current
  code can construct AI input payloads and stores final evaluation results, but
  it does not persist exact prompt/request/input snapshots for historical
  evaluations. Phase 20 implementation has not started.

## In Progress

- No active code implementation batch is currently in progress. Phase 10-18
  console optimization is complete and verified through Phase 18B. Phase 19A
  documentation governance is complete. Phase 19B-19D run-center realtime
  progress code work is not started. Phase 7.1 and Phase 17.1 are accepted but
  not implemented. Phase 20 is accepted but not implemented. Phase 21 is
  accepted but not implemented. CR-037 is deferred.

## Known Risks

- Phase 5 still stores `profile_path` as a transition-only internal runtime
  field for existing login/crawler code paths, but new identity and path
  resolution are `profile_key` based and customer-facing responses mask real
  paths.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR/login capability and profile persistence now have automated
  server-like validation, but real platform QR scanning, real platform
  crawling, and explicit-opt-in real SMTP delivery still require a live
  server/account pilot with operator-controlled credentials.
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
- CR-041 tightens the first usable pilot boundary: Phase 17.1A-B, Phase
  7.1A-C, and a minimum server-like real workflow are required before first
  pilot use. Phase 21, CR-038, Phase 19B-D, Phase 20, and CR-037 are not first
  pilot blockers unless a later accepted P0 safety, security, or core-flow
  regression changes the boundary.
- CR-041 Pilot Gate C now has a default-safe evidence template/checker:
  `scripts/pilot_gate_c_evidence.py` can write
  `docs/pilot_gate_c_evidence.example.json` and validate a separate
  operator-filled evidence file. The checker only reads JSON evidence and
  rejects missing real-workflow proof, placeholders, unchecked redaction
  surfaces, secret-looking values, raw local paths, provider endpoints, proxy
  credentials, cookies, and sensitive evidence keys. It does not start
  services, crawl platforms, call AI, mutate data, or send email.
- CR-031 is accepted but not implemented: active Run Center rows still depend
  on the current `crawl_runs.summary` update timing until Phase 19B-19D code
  work is completed. Operators may still need manual refresh or logs to
  understand long-running crawl progress in the current runtime.
- CR-035 Phase 7.1A-C is implemented and locally verified. Historical run
  `8317` still must not be repaired automatically; Phase 7.1D requires safe
  operational steps, backup, rollback, dry-run preview, and explicit operator
  approval before changing historical AI rows, reports, or terminal status.
- CR-036 Phase 17.1A-B and backend Phase 17.1C/17.2A are implemented and
  locally verified. The product direction is not "never send real mail"; real
  mail must be intentional, visible, attributable validation or production
  delivery through `MONITOR_ALLOW_REAL_EMAIL_SEND=true`. Operator-facing
  recipient-source UI/preflight explanation, orphan evidence operations notes,
  and template guardrails remain follow-up work.
- CR-037 is deferred: normal-user email send/resend quotas and administrator
  policy controls are not yet designed. Existing V1 role permissions remain in
  force until a future confirmed phase changes them.
- CR-034 is accepted but not implemented: storing and exposing AI
  prompt/request/response details will add new trace persistence and role-safe
  APIs. Historical AI evaluations cannot be treated as having exact input
  snapshots because those snapshots were not persisted at evaluation time.
- Phase 18B report-center task grouping is implemented and verified. The
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
  versus test/noise separation. Phase 16 adds the email delivery log table,
  window-key helper, safe delivery-log helpers, and auto-window uniqueness
  foundation. Phase 17A connects scheduler/report send logic to that foundation
  so duplicate automatic sends in the same window are skipped, automatic
  failures are logged with customer-safe text, and manual resend is recorded
  separately. Phase 17B now surfaces this history in the report center with
  customer-safe delivery errors, confirmation for manual resend, and
  desktop/tablet/mobile report-center validation. Phase 18A now adds
  `reports.job_snapshot_json`, new-report snapshot persistence, compatible
  backfill for reports whose `job_id` resolves, deleted-task snapshot context,
  limited-context flags for unrecoverable old reports, and owner/workspace
  filtering that does not trust snapshot content. Phase 18B now consumes those
  fields in the report center to group active reports by task, group deleted or
  missing-task reports by stored snapshot, label deleted and limited-context
  history, and keep preview, lead detail switching, downloads, delivery
  history, and row actions tied to the selected report.
- Phase 11 was completed as four verified batches: Phase 11A module boundary
  and tokens, Phase 11B base layout/navigation visual foundation, Phase 11C
  interaction components and floating menus, and Phase 11D responsive
  foundation. A follow-up Phase 11C regression fix now renders Platform
  Account, Monitoring Task, and AI Evaluation Rule row "more" menus from
  page-level floating containers so table scroll areas and sticky action
  columns cannot cover the popup content.
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
- Email delivery-history UI and report task grouping are accepted directions.
  Run visibility/noise-filtering data fields are active schema features after
  Phase 14, archive/restore APIs, pagination, and filters are active after
  Phase 15A, frontend run-center controls are active after Phase 15B, and
  email delivery logs are active schema features after Phase 16. Automatic-send
  idempotency in the scheduler/report delivery workflow is active after Phase
  17A; report-center delivery-history UI is active after Phase 17B; report
  snapshots are active after Phase 18A; report task grouping is active after
  Phase 18B.
- The first global Phase 10-18 review found that Phase 13, Phase 17, and Phase
  18 were too coarse as single goals. The plan now splits them into data/API
  and frontend/responsive batches.
- Phase 10.5 follow-up global review found no remaining P0/P1 blockers.
  Remaining review notes were P2 implementation refinements and did not block
  Phase 11-18 execution. Phase 18B preserved Phase 18A snapshot/permission
  behavior and did not use snapshot content to grant access.

## Next Step

Next allowed implementation order:

1. satisfy the remaining real-external portion of CR-041 Pilot Gate C with a
   server-like workflow: server-side login/profile path, one real platform
   crawl when credentials/session are available, AI fallback, explicit-opt-in
   SMTP validation, redaction checks, and a passing
   `scripts/pilot_gate_c_evidence.py --check <operator-evidence.json>` result;
2. handle CR-035/Phase 7.1D historical run remediation only through the
   dry-run, backup, rollback, and explicit-operator-approval gate;
3. implement Phase 17.1C/17.2A remaining operator-facing recipient/template
   explanations and Phase 17.2B-C template guardrails as follow-up if they
   become the next accepted batch;
4. implement Phase 21 formal console page-level UI/UX refinement as
   frontend-only workstreams with the Phase 21P cross-page layout-resilience
   gate;
5. implement CR-031/Phase 19B-19D realtime run-progress work after Phase 7.1
   lifecycle fields are available, unless a deliberately small compatible
   provisional-progress batch is documented first;
6. schedule CR-034/Phase 20 implementation after higher-priority safety and
   lifecycle work if run-detail traceability becomes the next execution batch;
7. prepare production pilot handoff and deployment-specific validation after
   the safety and lifecycle regression fixes are verified;
8. verify real platform QR scanning, real platform crawling, SMTP delivery,
   and AI-provider behavior with production credentials;

## Latest Verification

Phase 18B report-center task grouping frontend verification on 2026-06-16:

- Updated the report-center list rendering path to group reports by active
  monitoring task when `job_id` resolves.
- Grouped deleted or missing-task reports using the customer-safe
  `job_snapshot` fields exposed by Phase 18A.
- Added deleted-task, historical snapshot, and limited-context labels without
  exposing raw `job_snapshot_json`.
- Preserved per-report preview, lead detail switching, download links, email
  delivery latest state/history, manual resend menu entry, and row actions.
- Added responsive grouped-report styles for desktop, tablet, and mobile.
- Verified administrator and normal-user role paths without changing API,
  schema, permission, or data-scope behavior.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_18b or phase_18a or phase_17b or report_resend_email_updates_status or report_history_keeps_law_firm_snapshot_after_job_deleted or leads_api_can_scope_items_to_selected_report"`
- Result: 8 passed, 228 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 236 passed, 3 warnings.
- Inline monitor page script parse check and `python -m py_compile
  tests\test_monitoring_mvp.py`
- Result: PASS.
- Browser validation on isolated service `127.0.0.1:19218` with temporary
  data:
  - `/monitor`, `/static/monitor/monitor.css`, and
    `/static/monitor/monitor.js` returned HTTP 200;
  - administrator login opened Report Center with active-task, deleted-task,
    missing-task snapshot, and limited-context historical groups;
  - grouped report labels, platform/keyword/frequency chips, preview drawer,
    report-specific lead switching, report download menu links, latest email
    status, and delivery-history rows stayed tied to report ID 1;
  - 1440px, 1024px, and 390px report-center checks found four groups, no
    page-level horizontal overflow, and no authenticated console/page errors;
  - normal-user login kept Report Center visible and administrator resource or
    diagnostics entries hidden.

Phase 18A report job snapshot data model verification on 2026-06-16:

- Added `reports.job_snapshot_json` to new database creation and compatible
  existing-database migration.
- Added shared report job snapshot builders for law firm, platforms, search
  keywords, frequency, task ID, and deleted-task context.
- Persisted snapshots for newly generated reports.
- Backfilled snapshots for existing reports whose `job_id` still resolves to
  `monitor_jobs`.
- Preserved `job_id` as the active or historical task relation while marking
  deleted-task reports from the stored snapshot context.
- Kept unrecoverable old reports readable as limited-context historical
  reports.
- Preserved owner/workspace filtering by resolving reports through the current
  report/job/creator scope and never using snapshot content to grant access.
- Exposed customer-safe `job_snapshot`, `job_deleted`,
  `legacy_without_job_snapshot`, and `limited_context` fields through existing
  report views for Phase 18B consumption.
- Did not implement Phase 18B frontend report grouping or grouped report
  layouts.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_18a`
- Result: 2 passed, 233 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_18a or phase_17b or phase_17a or phase_16 or report_resend_email_updates_status or report_history_keeps_law_firm_snapshot_after_job_deleted or list_reports_limit_zero"`
- Result: 10 passed, 225 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 235 passed, 3 warnings.
- `python -m py_compile api\monitoring\database.py api\monitoring\reporting.py api\routers\monitor.py tests\test_monitoring_mvp.py`
- Result: PASS.

Phase 17B email delivery history frontend verification on 2026-06-16:

- Added a report delivery-history API endpoint scoped by the current
  administrator/normal-user actor and backed by `email_delivery_logs`.
- Kept report visibility and owner/workspace filtering by resolving the report
  through `get_report(..., actor=actor)` before returning delivery logs.
- Returned customer-safe delivery-log fields only and scrubbed sensitive labels
  such as SMTP passwords, tokens, cookies, and proxy secrets from visible
  delivery errors.
- Updated the report center to show latest delivery status, clickable delivery
  status cells, a delivery-history panel, send type, status, time, recipients,
  send-window key, and customer-safe error messages.
- Added a report action for viewing delivery history and required confirmation
  before manual resend; after resend the report list and selected history
  refresh.
- Preserved report preview, lead detail switching, downloads, run-center
  navigation, task-list and task-create entry behavior, logout, and
  administrator/normal-user role visibility.
- Did not add Phase 18 report snapshots, report grouping, schema changes, or
  new frontend dependencies.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_17b`
- Result: 2 passed, 231 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17b or phase_17a or phase_16 or report_resend_email_updates_status or phase_1_http_routes_enforce_sessions_roles_and_owner_scope or monitor_page_uses"`
- Result: 9 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 233 passed, 3 warnings.
- `python -m py_compile api\routers\monitor.py api\monitoring\database.py api\monitoring\reporting.py tests\test_monitoring_mvp.py`
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- Inline monitor page script parse check
- Result: PASS.
- Runtime browser validation on isolated service `127.0.0.1:19217`:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200; administrator login opened
  the console; report center loaded sample reports; delivery history displayed
  automatic and manual-resend rows with recipients, window key, status, time,
  and no secret-label leakage; 1440px, 1024px, and 390px report-center checks
  kept the delivery-history surface usable without page-level horizontal
  overflow; report preview drawer, report row menu, run center, task list,
  task-create entry, logout, and normal-user role-visible navigation were
  checked with no console errors.

Phase 17A email idempotency and delivery logic verification on 2026-06-16:

- Connected report automatic email delivery to the Phase 16
  `email_delivery_logs` foundation.
- Used `send_window_key` generation for `daily`, `6h`, `12h`, and `cron`
  through the accepted data-model helper.
- Added automatic-send idempotency by `workspace_id + job_id +
  send_window_key + send_type=auto`; repeated automatic sends in the same
  window record a skipped delivery log and do not call the mailer again.
- Recorded automatic delivery attempts, successes, failures, recipient
  summaries, and customer-safe errors in `email_delivery_logs`.
- Recorded explicit manual resend as a separate `send_type=manual_resend`
  delivery log with the acting user ID while keeping automatic idempotency
  independent.
- Preserved report generation when SMTP is unavailable and kept
  `reports.email_status` / `reports.email_error` readable until Phase 17B
  migrates the report center to delivery history.
- Passed Phase 17A focused and related regression tests, plus the full
  monitoring MVP test suite.
- Did not implement Phase 17B report-center delivery-history frontend or
  Phase 18 report grouping/snapshot behavior.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_17a`
- Result: 2 passed, 229 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17a or phase_16 or phase_15b or phase_15a or phase_14 or report_resend_email_updates_status or phase_7_run_job_generates_report_without_ai_or_email or cli_run_due or scheduler"`
- Result: 20 passed, 211 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 231 passed, 3 warnings.
- `python -m py_compile api\monitoring\database.py api\monitoring\reporting.py api\monitoring\runner.py api\monitoring\scheduler.py api\monitoring\cli.py api\routers\monitor.py tests\test_monitoring_mvp.py`
- Result: PASS.

Phase 16 email delivery data model preparation verification on 2026-06-16:

- Added `email_delivery_logs` to new database creation and compatible existing
  database migration.
- Stored `workspace_id`, `job_id`, `report_id`, `send_window_key`,
  `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
  `recipients_json`, and `created_at`.
- Added allowed send types `auto` and `manual_resend`, allowed statuses
  `pending`, `sending`, `sent`, `failed`, and `skipped`, and send-window key
  generation for `daily`, `6h`, `12h`, and `cron`.
- Added Phase 16 indexes:
  `idx_email_delivery_job_window`, `idx_email_delivery_report`, and
  `idx_email_delivery_status`.
- Added partial unique index `idx_email_delivery_auto_window_unique` so one
  pending, sending, or sent automatic delivery can exist for the same
  workspace, task, window, and `send_type=auto`, while failed/skipped retries
  and manual resend rows can be recorded separately.
- Preserved existing `reports.email_status` and `reports.email_error`
  compatibility fields.
- Ensured delivery-log helper output and stored errors use customer-safe
  sensitive text handling and do not store SMTP passwords, proxy credentials,
  or tokens.
- Did not implement Phase 17A scheduler/mailer send-flow idempotency or Phase
  17B delivery-history frontend.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_16`
- Result: 1 passed, 228 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_16 or phase_15b or phase_15a or phase_14 or report_resend_email_updates_status"`
- Result: 5 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 229 passed, 3 warnings.
- `python -m py_compile api/monitoring/database.py tests/test_monitoring_mvp.py`
- Result: PASS.

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
