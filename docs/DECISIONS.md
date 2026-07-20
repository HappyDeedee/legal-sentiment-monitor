# Decisions

This file is append-only. Add new dated decisions instead of rewriting history.
If a later decision supersedes an earlier one, keep the old decision and add a
short `Superseded by` note rather than deleting history.

## 2026-06-14

- The system is positioned as a server-deployed ToB law-firm public-opinion
  monitoring system.
- The first version targets single-server, low-concurrency internal or
  customer-pilot use.
- The first version does not include complex account rotation, captcha bypass,
  SMS automation, high-concurrency worker clusters, public SaaS onboarding, or
  billing.
- System administrators maintain account pools, proxy IPs, AI access, email
  settings, templates, runtime settings, and users.
- Normal users only create monitoring tasks by choosing platforms, entering
  platform search terms, setting frequency, and entering report recipient
  emails.
- Normal users must not need to manage platform accounts, proxies, browser
  profiles, API keys, SMTP passwords, or local paths.
- Server-like validation is mandatory. A task that only works through a local
  Chrome window is not production-ready.
- Each platform account must have an independent profile.
- Account names are display labels. Profile identity must use a stable key such
  as workspace, platform, and account ID.
- Same account and same profile are single-concurrency resources.
- Proxy priority is task-bound proxy, then account-bound proxy, then default
  network.
- Login and crawling should use the same account proxy when configured.
- Customer-facing UI must not expose real server paths, profile paths, raw
  secrets, command lines, debug wording, or implementation-only details.
- Create/edit/test interactions should be visually consistent. First-version
  UI should prefer modal dialogs for secondary operations to avoid mixed drawer
  and inline form behavior.
- Every active menu item must be covered by product requirements, not only the
  features explicitly discussed in chat.
- Meaningful new user requirements must be recorded in `CHANGE_REQUESTS.md`
  and connected to tasks and tests before being treated as complete.
- Agent work must update project documents as part of the completion criteria.
- Parallel agent/worktree development is allowed only with clear module/file
  ownership and document updates in each branch.
- Ambiguous high-impact requirements must be confirmed with the user before
  they are marked accepted or implemented in stable product documents.
- P0 specialist documents may contain proposed implementation details, but
  sections marked as open confirmation items must be confirmed before coding
  the affected phase.
- Profile migration does not need long-term legacy compatibility. Because the
  current account count is low and the project is still in agile development,
  existing profile-path-based accounts can be reset or re-logged in under the
  new `profile_key` model.
- Do not design long-term fallback behavior around legacy `profile_path`.
  New account environments should use `profile_key`; old low-volume accounts
  should be re-created or re-logged in instead of physically migrated.
- V1 uses one default workspace, with `workspace_id` reserved in data models
  but no visible multi-workspace management UI.
- V1 uses session-based authentication with secure HTTP-only cookie.
- Initial administrator creation uses environment bootstrap variables.
- Normal users can delete their own non-running tasks and resend their own
  reports.
- Disabled users cannot log in, while their existing enabled tasks continue
  under workspace ownership until an administrator changes them.
- MVP includes minimal audit logging for security-sensitive administrator
  actions.
- Runtime settings use a flexible key-value `system_settings` table in V1.
- Account profile keys use `{workspace_id}/{platform}/acc_{account_id}`.
- Normal-user crawl range settings are capability-bounded controls, not exact
  cross-platform guarantees. `max_items` is a content-count cap, `start_page`
  applies where the platform crawler honors it, `max_pages` is approximate, and
  time windows may be implemented by platform-native filters, monitoring-layer
  filtering, or both.
- Administrator task timeout is a run-level wall-clock deadline. V1 does not
  auto-compute timeout from crawl range because platform behavior, keyword
  volume, account state, network conditions, and anti-abuse checks vary too
  much for reliable estimation.
- Account/profile lock expiry follows the run deadline plus a cleanup buffer.
  Expired locks are recovery signals only; they must not be reused until the
  owning run is verified as finished, timed out, failed, cancelled, interrupted,
  or no longer alive.
- Account/profile locks use inline fields on `social_accounts`. Proxy
  concurrency uses a `resource_locks` table because one proxy can allow multiple
  concurrent runs up to its configured limit.
- Runtime Strategy is administrator-only and uses grouped table sections for
  Crawling, Login, Scheduler, and Retention settings.
- Phase 6 makes server-side QR login the primary administrator login flow.
  Local-window login is a development-only fallback controlled by
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW`; production deployments should set it to
  false and use the web QR/status flow for acceptance.
- Phase 8 server-like validation may use an isolated real FastAPI service
  process with persistent data/profile directories when Docker or a remote
  Linux server is unavailable on the validation machine. This validates the
  server-controlled HTTP UI/API path, production login flags, profile
  persistence across service restart, runtime locks, and headless browser
  availability, but it does not replace live pilot validation for real platform
  QR scanning, real platform crawling, real AI provider, or real SMTP delivery.
- Phase 9 completes V1 security and operations with minimal administrator
  audit logs, secret redaction, resource-alert diagnostics, backup guidance,
  disk-space diagnostics, and retention-setting diagnostics. Automated
  retention cleanup jobs are not added in V1; operators should use the
  diagnostics and backup guidance during pilot operations until a later cleanup
  job is explicitly planned.
- Completed phases are historical verification snapshots. When a new defect is
  found in a completed phase's responsibility area, agents should create a
  follow-up regression-fix CR and task block linked back to the original phase
  instead of rewriting the old phase as incomplete or mixing the defect into an
  unrelated later enhancement phase.
- Confirmed for CR-108: documentation is the first gate before code migration.
  The older server-login/SMS/Docker worktree is a source of historical evidence
  and implementation material, not a branch to merge directly. Conflicting old
  CR-107/CR-108 document entries must be remapped into current mainline CR-108.
  Server/container mode keeps the server QR/status flow primary and local
  login windows disabled; Windows local mode may use a service-owned visible
  login window only as an explicit manual-verification fallback. Captcha, SMS,
  slider, and platform risk checks are never bypassed.

## 2026-06-15

- Phase 10-18 will be a documentation-first console optimization roadmap before
  implementation starts. The accepted product direction is a full console
  redesign, not a small visual patch.
- The console should be rebuilt around the monitoring task loop: operations
  home, monitoring task creation/management, run center, report center, and
  email delivery. Administrator resource management supports this loop.
- Login should route users to an operations home. The operations home should
  use visual metrics, drilldowns, task health, report status, email delivery
  status, and concise resource health instead of long diagnostic text blocks.
- Resource Management and System Configuration should be expandable navigation
  groups, not detached hover-only popover menus. Mobile navigation must work
  without hover.
- The authenticated user identity and logout action should be grouped together
  at the top right.
- CR-020 is one unified Frontend Design System requirement. Visual language,
  interaction patterns, and responsive behavior are strongly coupled and should
  not be split into separate CRs for this roadmap.
- The visual direction is Apple-style: clean, high-end, low-noise,
  enterprise-ready, and still efficient for repeated operational work.
- Frontend breakpoints for Phase 10-18 are mobile below 768px, tablet from
  768px to 1279px, and desktop at 1280px and above.
- The frontend technology stack for this redesign remains Vanilla JavaScript
  plus CSS custom properties. Do not introduce Tailwind, Alpine.js,
  Petite-Vue, React, Vue, or a new required build pipeline in this round.
  Optional lightweight libraries may be considered only for focused charting or
  floating menu placement needs and must be recorded before implementation.
- Run records should use logical archive/hide behavior instead of hard delete.
  The accepted data-model direction is `crawl_runs.visibility` with `visible`
  and `archived`, `crawl_runs.run_type` with `scheduled`, `manual`, and
  `test`, plus `archived_at` and `archived_by`.
- Report center should group reports by monitoring task by default. Historical
  reports whose task cannot be resolved should use `reports.job_snapshot_json`
  to preserve law firm, platform, keyword, frequency, and deleted-task context.
- Email automatic delivery idempotency should use a new
  `email_delivery_logs` table. Automatic sends are deduped by task and
  schedule window, while manual resend is allowed and logged separately.
- `send_window_key` generation for the current scheduler frequencies is:
  `daily` uses `{job_id}_{YYYY-MM-DD}`; `6h`, `12h`, and `cron` use
  `{job_id}_{YYYY-MM-DD}_{HH}`. Weekly and monthly frequencies are not part of
  the current confirmed scheduler behavior.
- Phase 10-18 plan reviews must be global before they become phase-specific.
  Agents must first audit the full roadmap for final-goal fit, cross-phase
  dependencies, implementation granularity, rollback boundaries, verification
  coverage, and cross-phase impact risks. A Phase 11A-only readiness review is
  not enough to approve execution of the roadmap or generate an execution
  goal.

## 2026-06-16

- Confirmed for CR-035: run interruption must use a first-class terminal
  `interrupted` status rather than overloading `partial_failed`.
- Confirmed for CR-035: stale recovery should use evidence first, not elapsed
  time alone. The recovery check should inspect live task evidence, resource
  locks, last heartbeat, last completed step, and redacted last error before
  deciding that a run is interrupted.
- Confirmed for CR-035: the default stale-heartbeat grace period is 10
  minutes.
- Confirmed for CR-035: retry policy should reuse existing crawler retry
  controls for platform/browser/network failures and apply a separate AI item
  retry budget; all retries must finish before the run deadline.
- Confirmed for CR-035: `ai_item_timeout_seconds` should default to 120 seconds
  and be capped by the remaining run deadline.
- Confirmed for CR-035: active finalization may convert known unresolved AI
  evaluation candidates to `pending_review` so report generation can continue.
  Historical interrupted runs must not have AI rows rewritten unless an
  operator explicitly approves a repair workflow.
- Confirmed for CR-035: the run summary and frontend-visible progress should
  include AI evaluation totals, including candidate count, successful
  evaluations, failed/fallback evaluations, pending-review count, and
  unresolved count where available.
- Confirmed for CR-035: preventing new `crawl_runs.job_id` gaps is the primary
  fix. Historical `job_id` backfill is only a compatibility fallback and must
  remain dry-run first.
- Confirmed for CR-036: historical unexpected email evidence should be
  preserved by default. Existing `.eml` files, report artifacts, delivery-log
  rows, and related evidence must not be deleted or mutated without database
  backup and explicit operator approval.
- Confirmed for CR-036: real email delivery must remain intentional and
  attributable. Routine automated tests and local diagnostics must not create
  hidden real SMTP side effects.
- Confirmed for CR-036: the deployment gate should be environment-controlled
  and surfaced read-only in runtime settings so operators can see whether real
  mail is allowed.
- Confirmed for CR-036: local manual resend may only send real mail when the
  explicit real-mail validation policy allows it; otherwise it should remain a
  non-sending validation path.
- Deferred beyond CR-036: role-based email sending permissions, normal-user
  send quotas, and administrator-managed resend limits are a later governance
  requirement. They should not block the immediate test/local email safety
  regression fix.
- Confirmed for CR-039: report email templates should move away from
  unrestricted free-form HTML editing. Future template management should use a
  small set of administrator-selectable preset styles, while the generated
  report body is inserted by the system and each delivered email records the
  effective template used.
- Confirmed for CR-034: AI evaluation trace retention must be an
  administrator-configurable runtime setting, defaulting to 30 days, rather
  than a hard-coded retention window.
- Confirmed for CR-034: prompt/request/response/comment size limits are
  storage and API guardrails for trace snapshots, not user-facing business
  rules. The accepted default guardrails are about 64KB per trace, 16KB for the
  prompt snapshot, 24KB for the request snapshot, 24KB for the response
  snapshot, and up to 20 sampled comments with per-comment truncation.
  Oversized trace fields should be truncated with an explicit marker and must
  not block AI evaluation, report generation, or run finalization.
- Confirmed for CR-034: normal users must not see raw AI model responses.
  Administrators may see redacted raw model responses for diagnosis, but
  unredacted raw model responses must not be stored or exposed to any role.
- Confirmed for CR-041: "the system can be used first" is judged by a minimum
  usable pilot gate, not by completion of every optimization roadmap item. The
  hard first-pilot blockers are hidden-real-email safety, stuck-run lifecycle
  safety, and a minimum server-like real workflow.
- Confirmed for CR-041: Phase 21 UI refinement, CR-038 drawer accessibility,
  Phase 19 realtime progress, Phase 20 AI traceability, and CR-037
  role/quota governance do not block the first usable pilot unless a later
  accepted P0 safety, security, or core-flow regression changes that boundary.
- Confirmed for CR-041: historical run remediation and orphan email evidence
  handling remain dry-run, backup, rollback, and explicit-operator-approval
  gated; first-pilot readiness must not silently mutate historical evidence.
- Confirmed for CR-034: normal users may see only business-safe AI evaluation
  summaries for their own runs. Full prompt snapshots, request payload
  snapshots, and administrator debug metadata are administrator-only.
- Confirmed for CR-034: AI trace snapshots should be stored in a new
  `ai_evaluation_traces` table linked to `run_id`, `raw_content_id`, and
  `ai_evaluations.id`, rather than being added to `ai_evaluations` or stored
  as run/report artifact files.
- Confirmed for CR-043: real email delivery should use one administrator
  frontend switch on Mail Configuration, backed by the default-off persisted
  `real_email_delivery` runtime setting. The rejected CR-042 multi-layer
  validation-window design must not be reintroduced for daily operation:
  no deployment frontend gate, scheduler-exclusion gate, expiry window, or
  single-use validation window is required for the administrator switch.
- Confirmed for CR-045: platform `source_keyword` is recall provenance only
  and must not by itself prove that a collected item is related to the target
  law firm. Relatedness and negative-risk classification should be grounded in
  title, description/body, author, or sampled comments that identify the
  target law firm, accepted aliases, or a clearly equivalent reference.
  Missing AI evaluation records, timeout leftovers, and interrupted evaluation
  candidates must not be displayed as no-risk content.

## 2026-06-17

- Confirmed for CR-047: Account Browser Environment Consistency is accepted as
  a Phase 5.1 existing-feature optimization. The initial local draft used
  CR-042, but CR-042 is already the historical rejected real-email validation
  window, so the account browser-environment requirement is recorded as
  CR-047.
- Confirmed for CR-047: the target rule is one platform account equals one
  `profile_key` and one fixed browser environment. Server-side QR login,
  accepted Cookie validation, login-state checks, and crawling should reuse the
  same persisted profile, user agent, browser platform/fingerprint family,
  timezone, locale, screen size, and effective proxy policy.
- Confirmed for CR-047: CloakBrowser-Manager is a reference for stable
  profile settings, CDP, and noVNC concepts only. It is not a required
  dependency, must not replace the current Platform Accounts center, and any
  optional provider evaluation requires a separate security, deployment,
  license, authentication, noVNC access-control, storage, and redaction review.
- Confirmed for CR-047: locked browser-environment fields must not be silently
  edited after successful login validation. Changing a locked environment
  requires an explicit administrator reset/re-login flow with audit logging and
  clear consequences.
- Confirmed for CR-048: Report Center remains a report-first artifact surface.
  Lead detail may appear there only as an explicit scoped secondary view tied
  to a selected report, selected report group, originating run, or visibly
  labeled current-filter aggregate.
- Confirmed for CR-048: an unlabeled flat lead list in Report Center is not an
  acceptable long-term information architecture because it makes users wonder
  whether they are seeing all leads, filtered leads, or one report's leads.
- Confirmed for CR-048: a standalone global lead workbench is out of scope for
  this optimization and would require a separate capability CR. Per-run
  lifecycle, every AI evaluation record, and trace/debug evidence remain
  CR-034 / Phase 20 Run Detail responsibilities.
- Confirmed for CR-048: if the UI needs a primary home for "lead center"
  behavior, it belongs under Run Center / Run Detail because leads are produced
  by a run and may exist before a report is generated. Report Center should
  provide report-scoped "view leads" shortcuts only.
- Confirmed for CR-049: Mail Configuration should use one page-level action
  bar for edit configuration, test mail, refresh/status, delivery-status
  navigation, and the compact real-email send state. Inner SMTP/defaults
  panels should not repeat the same primary edit/test actions.
- Confirmed for CR-049: the CR-043 real-email send switch remains the single
  administrator safety control, but its normal/off presentation should be a
  compact labeled toolbar control with concise state text rather than a large
  full-width block. Turning it on still requires explicit confirmation.
- Confirmed for CR-049: Report Center delivery history is scoped secondary
  detail opened from a report row/status action; it should not dominate the
  initial report archive layout.

## 2026-06-18

- Confirmed refinement for CR-047: the accepted Phase 5.1 direction is now
  Account Identity Fidelity rather than only Account Browser Environment
  Consistency. The target is account identity lifecycle management: profile
  traces plus browser environment plus proxy region plus runtime binding plus
  lock/audit consistency.
- Confirmed refinement for CR-047: the profile folder stores browser traces
  such as cookies, local storage, IndexedDB, cache, history, preferences,
  service workers, and session state, while the database stores account
  identity launch rules such as user agent, browser platform, timezone,
  locale, accept-language, screen/viewport/device flags, fingerprint seed,
  proxy policy, region, generator metadata, lock state, and re-login state.
- Confirmed refinement for CR-047: Phase 5.1 should include an Account
  Identity Generator and Account Identity Validator. The generator must be
  stable, differentiated, self-consistent, and explainable. The validator must
  fail closed for missing fields, region/timezone/locale mismatches, UA/device
  contradictions, proxy-policy conflicts, and hidden Playwright/process-default
  fallback.
- Confirmed refinement for CR-047: for China mainland proxy identities, use a
  coherent default region bundle such as `environment_region = CN_MAINLAND`,
  `timezone = Asia/Shanghai`, `locale = zh-CN`, and `accept_language =
  zh-CN,zh;q=0.9`, while avoiding province-level browser overfitting.
- Confirmed for CR-047: adopt the strict proxy policy for V1 account identity
  fidelity. After an account identity is locked, task-level proxy overrides are
  rejected for that locked account environment. To change proxy policy, an
  administrator must reset the account identity and re-login under the new
  proxy.
- Confirmed for CR-047: existing logged-in accounts do not need compatibility
  preservation or guessed identity backfill. They should remain readable and be
  re-logged in under the CR-047 identity rules when the feature is implemented.
- Confirmed for CR-047: V1 does not introduce CloakBrowser or
  CloakBrowser-Manager. The first implementation should use the existing
  Playwright/CDP provider path, with a provider boundary for future expansion.
- Confirmed for CR-047: V1 does not promise full management of Canvas, WebGL,
  font inventory, `navigator.plugins`, browser extensions, or long-term
  browsing history. These are future/provider-dependent because they depend on
  browser build, OS/fonts, graphics stack, installed extensions, profile
  history, and runtime JavaScript probes rather than simple launch options.
- Confirmed for CR-047: if later accepted, high-fidelity browser-persona work
  should be estimated as a separate provider project: about 1-2 days for
  provider/license/deployment review, 3-5 days for a local one-platform
  prototype, 1-2 weeks for optional provider integration, and 3-6+ weeks for a
  production-grade browser-pool/profile-history capability.
- Confirmed for CR-047: the CR-047 identity lifecycle uses persisted
  `identity_state` plus `identity_runtime_snapshot_json` so generation,
  validation, login, lock, relogin, and reset states are explicit rather than
  implicit.
- Confirmed for CR-047: the deterministic generator uses a canonical input
  tuple with HMAC-SHA256 seed derivation and template-specific field rows; it
  must not improvise random values or process-default fallback for locked
  identities.
- Confirmed for CR-047: tests and local diagnostics default to real-profile,
  real-proxy, and real-platform-login tripwires off. Real account identity
  access requires explicit opt-in environment flags.
- Confirmed for CR-047: account identity template selection is automatic by
  default. Normal users cannot choose templates or field-level browser
  identity values. Administrators may only use an advanced pre-login override
  to select a template family, and any change to a locked identity requires
  explicit reset/re-login.
- Confirmed for CR-051: the former top-level Run Center and Report Center
  execution/report surfaces are consolidated into one top-level `任务中心`.
  The first-level view uses the existing report-by-monitoring-task grouping so
  operators can see which law-firm monitoring task each report and public
  opinion result belongs to.
- Confirmed for CR-051: the former run-record table fields such as run ID,
  task ID, type, visibility, duration, and failure reason remain available in
  the `运行记录` subview and Run Detail, but the task-group first view should
  prioritize business identification and result summaries: task/law firm,
  platforms, keyword summary, latest/report status, collection/new counts,
  suspected negative, high risk, manual review, unevaluated, and the `运行详情`
  drilldown.
- Confirmed for CR-051: the separate top-level Report Center navigation entry
  and page section are removed. Report preview, report-scoped lead inspection,
  delivery history, resend, and downloads remain reachable from the
  task-group surface, mostly as secondary row actions or the `更多` menu.
- Confirmed for CR-052: after Task Center consolidation, row-level actions
  should not duplicate capabilities already available in Run Detail. The
  run-record row no longer exposes `查看日志`; operators use Run Detail's
  `采集日志` section for the same log content plus copy/download. The
  task-group report row no longer exposes `预览`; operators preview a report
  from Run Detail's `报告` section, while `更多` continues to hold
  report-scoped leads, delivery history, resend, and downloads.
- Confirmed for CR-053: Task Center run tables should prioritize identifiers
  before state. Flat mode begins with `任务 ID`, `运行 ID`, and compact `状态`.
  Grouped mode hides the duplicated `任务 ID` column because the group header
  already identifies the monitoring task; group rows begin with `运行 ID` and
  compact `状态`.
- Confirmed for CR-053: first-level status cells stay compact. Completed rows
  show terminal state only, while active rows may show one short progress cue;
  full progress, logs, report, AI evaluation, and delivery evidence remain in
  Run Detail.
- Confirmed for CR-053: Task Center has one page-level refresh entry. The
  filter toolbar keeps `筛选` and `清空`; it does not repeat a second refresh
  button.
- Confirmed for CR-053: native select/dropdown controls must not be clipped or
  shifted by the main content container. Console-wide layout should leave
  vertical overflow visible while table-local horizontal scrolling remains
  inside table wrappers.
- Confirmed for CR-057: grouped Task Center run summaries should read as
  compact labeled metrics, not as a long slash-separated sentence and not as
  large nested cards. The task identity remains in the group title; aggregate
  run, collection, new-content, risk, review, and unevaluated counts appear as
  small chips, while limited-context or deleted-task context stays as a short
  note.
- Confirmed for CR-058: page-level filter date inputs may use the same
  fixed-position in-page floating menu pattern as filter selects when native
  browser date pickers misalign. The original date input must remain in place,
  keep its value and `change` semantics, and ordinary form/configuration date
  inputs must remain native unless a later focused requirement changes them.
- Confirmed for CR-059: when a page-level filter date menu is wider than its
  trigger, edge anchoring is preferred over center anchoring. The menu should
  align its left edge with the trigger when space allows, align its right edge
  with the trigger near the right viewport edge, and use viewport clamping only
  as an overflow fallback.
- Confirmed for CR-060: the CR-059 edge-anchoring attempt is retained as
  historical verification, but the current accepted visual rule for page-level
  filter date menus is compact trigger-center alignment. If the calendar menu
  would otherwise be much wider than the date trigger, reduce the calendar
  width first, align its center line to the trigger center line, and clamp only
  as the final viewport-safety fallback.
- Confirmed for CR-061: CR-060 is retained as historical verification, but the
  current accepted visual rule for page-level filter date menus is
  trigger-width anchoring. The visible date menu should match the clicked
  trigger's width and align to its left edge when viewport space allows,
  because that reads more like a normal filter dropdown than a wider centered
  calendar surface. Viewport clamping remains only the final safety fallback.
- Confirmed for CR-062: trigger-width date menus must also protect the internal
  calendar grid. Date cells should reset browser-default button padding and
  automatic minimum width so all seven weekday/day columns remain readable
  inside the anchored menu.
- Confirmed for CR-063: CR-061/CR-062 remain historical verification, but the
  current accepted visual rule for page-level filter date menus is a readable
  compact calendar popover. Narrow desktop date triggers should not force a
  cramped trigger-width calendar; instead the menu uses a compact readable
  width, a top anchor marker aligned to the clicked trigger center, right-edge
  alignment near the viewport edge, and viewport clamping as the final safety
  fallback.
- Confirmed for CR-064: CR-063's readable popover remains the baseline, but
  the current accepted right-edge rule is trigger-attached shrink before
  right-align. Page-level date menus should use the visual viewport for
  fixed-position edge checks, prefer left-edge attachment to the clicked
  trigger, slightly reduce the readable width near the right edge when that
  keeps the menu attached and the seven-day grid readable, and fall back to
  right alignment or clamping only when the attached width would be too narrow.
- Confirmed for CR-065: CR-064 remains historical verification, but the current
  accepted visual rule for page-level filter date menus is trigger-center
  anchoring. A readable compact calendar may be wider than the date trigger,
  but its center line and top anchor marker should align to the clicked
  trigger center whenever the visual viewport can accommodate it; viewport
  clamping is the final safety fallback.
- Confirmed for CR-066: CR-065 remains historical verification, but the current
  accepted visual rule for page-level filter date menus is trigger-attached
  dropdown alignment. A readable compact calendar should open from the clicked
  trigger's left edge when space allows, shrink before clamping if the readable
  width would overflow the visual viewport, and keep the top anchor marker
  tied to the clicked trigger center.
- Confirmed for CR-067: CR-066 remains historical verification, but the current
  accepted visual rule for page-level filter date menus is trigger-width visual
  attachment. The visible date menu should match the clicked trigger width when
  the trigger is usable, align its left edge to the trigger, keep the top
  anchor marker tied to the trigger center, and use a small minimum readable
  width only for unusually narrow triggers before viewport clamping.
- Confirmed for CR-068: CR-067 remains historical verification, but the current
  accepted visual rule for page-level filter date menus is local attached menu
  positioning. The active date menu should be mounted inside the clicked
  `.filter-date-enhanced` wrapper and positioned with local absolute
  coordinates so it opens directly under that field, while preserving the
  original date input value and `change` semantics.
- Confirmed for CR-070: Account Environment Export And Import Package is
  accepted as a Phase 5.2 new capability for moving one selected platform
  account environment between deployments. It is not a full database
  backup/restore feature and does not include monitoring tasks, crawl runs,
  reports, AI traces, email logs, users, runtime settings, or customer
  business history by default.
- Confirmed for CR-070: V1 supports metadata-only export and a slim encrypted
  login-state migration package. The migration package should include account
  configuration, CR-047 identity metadata, platform-account metadata, login/
  session state, and necessary profile state, not a raw whole browser profile
  copy. Cache, GPU cache, code cache, media cache, crash dumps, downloads,
  screenshots, temporary files, and other duplicated or regenerable browser
  artifacts are excluded by default.
- Confirmed for CR-070: V1 package encryption uses a passphrase-based
  encrypted package envelope. Target-deployment public-key encryption is future
  scope.
- Confirmed for CR-070: V1 may include source proxy host/IP plus port as an
  encrypted endpoint hint to help target-side proxy mapping, but must not
  export proxy username, password, token, authentication header, or provider
  secret. Audit logs, manifest summaries, and ordinary API responses must not
  expose the endpoint hint.
- Confirmed for CR-070: imports create a new target account/profile by
  default. Replace, merge, and overwrite behavior is future scope.
- Confirmed for CR-070: V1 exports avatar metadata only. Cached avatar image
  bytes are future scope.
- Confirmed for CR-072: the Monitoring task edit drawer's
  `自定义开始日期` and `自定义结束日期` are a focused exception to the ordinary
  form-date-native rule. They should reuse the existing CR-068 local attached
  date-picker mechanism, while unrelated edit/configuration date inputs remain
  native unless separately accepted.

## 2026-06-19

- Confirmed for CR-040 / Phase 21: Phase 21 is rebaselined on the current
  formal `/monitor` console after Task Center and Run Detail consolidation,
  not on the older separate Run Center / Report Center structure.
- Confirmed for CR-040 / Phase 21: the current `任务中心` information
  architecture is frozen for the Phase 21 visual pass. Phase 21 may refine
  colors, contrast, density, spacing, typography, status styling, loading,
  empty, error, focus, shadow, and responsive wrapping, but it must not restore
  separate top-level Run Center or Report Center pages.
- Confirmed for CR-040 / Phase 21: Task Center grouping, the `运行记录`
  subview, one first-level `详情` route, Run Detail's six sections, report
  scope filtering, enhanced select/date controls, `.drawer-scroll-body`,
  top-bar refresh, drawer/modal/menu categories, close/backdrop/Escape
  behavior, and overlay scroll/routing logic must not be changed for visual
  neatness without a separate accepted CR.
- Confirmed for CR-093: MediaCrawler is an internal collection engine for the
  Legal Sentiment Monitor product, not the public product cockpit. The exact
  production route, mount, reverse-proxy, and 404-vs-403-vs-unmounted strategy
  remains pending until a read-only route audit confirms current dependencies
  and the user accepts the implementation strategy.
- Confirmed for CR-095: future non-trivial work should start from an atomic
  goal packet before implementation. The packet must name the owner CR/phase,
  baseline, scope, out-of-scope, hard boundaries, start gate, touch surface,
  test loop, acceptance criteria, rollback or recovery, documentation updates,
  and stop conditions. The accepted execution rhythm is now Phase 21 merged and
  closed on `main`, Phase 5.1P read-only preflight, Phase 5.1A-D
  implementation, Phase 5.1 acceptance, then CR-070 / Phase 5.2 after CR-047
  provider/effective snapshot verification.

## 2026-06-20

- Confirmed for documentation governance: completed Phase 21 CR identifiers
  remain historical records and are not rewritten. The non-Phase-21 governance
  and future backlog items previously drafted with conflicting labels were
  renumbered to CR-091 Open Todo MECE Rebaseline, CR-092 Frontend Stack
  Migration Evaluation, CR-093 MediaCrawler Internalization/Public Exposure,
  CR-094 Crawler Engine Provider Architecture, and CR-095 Atomic Goal
  Execution Governance. Future agents must keep CR identifiers unique for
  separate current entries.
- Confirmed for todo governance: before a new execution lane or non-trivial
  goal starts, agents must run a read-only todo baseline review and classify
  active or next items as current, already completed, stale, duplicate,
  future-only, deferred, `Needs Confirmation`, operator-gated, or
  historical/archive-only.
- Confirmed for CR-105: the next Operations Home dashboard optimization uses
  Apache ECharts for core dashboard charts in the current no-build `/monitor`
  console, and the library must be vendored locally under the existing static
  asset path rather than loaded from a CDN. The current handcrafted
  `.operations-trend-svg` / path-helper chart geometry is the CR-104 baseline
  to replace, not the CR-105 implementation pattern.
- Confirmed for CR-105: CR-097 through CR-103 are historical/archive-only for
  future dashboard implementation. Their `流程总览`, `operations-stage-*`,
  heatmap-block, and no-chart-library details must not block the accepted
  chart-dashboard rebuild. CR-104 remains the current implemented baseline
  until CR-105 code is implemented and verified.
  Current-state note (2026-07-12): that condition is satisfied. CR-105 is the
  implemented and verified current ECharts baseline; CR-104 is now a verified
  historical predecessor.
- Confirmed for CR-105: the future Operations Home target is a six-module
  chart dashboard, not a process-node diagram. The page should let users judge
  within about 10 seconds whether today's monitoring is normal, where risk or
  exception exists, and where to click next. The first implementation should
  reuse current dashboard/runs/reports data and administrator resource health;
  task funnels, platform risk matrices, keyword heat, AI-quality analytics,
  and task rankings are later enhancements rather than current requirements.
- Confirmed for CR-105: the expected local ECharts vendor file is
  `api/webui/monitor/vendor/echarts.min.js`, served at
  `/static/monitor/vendor/echarts.min.js`. Missing trend buckets should remain
  a frontend read-only aggregation from existing `/runs` and `/reports` in the
  first implementation; backend trend buckets require a later accepted CR.
  When normal-user views hide administrator resource health, the remaining
  lower dashboard modules must reflow without a blank resource slot.

## 2026-07-19

- Confirmed for CR-047 / Phase 5.1B: account identity generation uses
  `MONITOR_ACCOUNT_IDENTITY_SEED_SALT` as UTF-8 bytes when explicitly set.
  Otherwise it derives a purpose-separated 32-byte salt from the decoded
  deployment Fernet key with
  `hmac.new(deployment_key_bytes,
  b"MediaCrawler/account-identity/seed/v1",
  hashlib.sha256).digest()`. The salt/key is not stored in account rows or
  returned through APIs.
- Confirmed for CR-047 / Phase 5.1B: backup/restore must preserve either the
  explicit identity seed-salt setting or the deployment secret key. Changing
  this authority is an identity migration that requires the later explicit
  reset/re-login lifecycle; it must not silently regenerate locked identities.
- Confirmed for CR-047 / Phase 5.1B: deterministic identity is generated only
  for a new social-account INSERT after the stable account ID and `profile_key`
  exist. Ordinary UPDATEs, including legacy draft-account updates, never
  regenerate or guess identity. Phase 5.1C owns explicit regeneration and
  state transitions.
- Confirmed for CR-047 / Phase 5.1C: SQLite lifecycle functions are the only
  authority for `identity_state`, `requires_relogin`, browser-environment lock
  metadata, and identity audit writes. Routes and account checks request
  transitions; they do not write parallel lifecycle state.
- Confirmed for CR-047 / Phase 5.1C: QR status success does not lock an account
  by itself. The account-level Profile check must pass first. Accepted QR,
  Cookie, and Profile checks lock and activate the same persisted identity with
  distinct safe reason codes.
- Confirmed for CR-047 / Phase 5.1C: an unlocked terminal login failure returns
  to `validated`; failed maintenance of a previously locked account restores
  `active` and preserves the prior lock. Pending verification keeps
  `login_in_progress`, and a second QR/visible-browser start conflicts until
  the owning operation is completed or explicitly cancelled.
- Confirmed for CR-047 / Phase 5.1C: locked proxy/region/template-family change
  requests preserve current locked inputs and mark `requires_relogin`.
  Administrator reset has no force bypass, rejects login/run ownership,
  preserves account/Profile/Cookie/platform identity material, rebuilds only
  generated environment fields, and ends `validated`/`standby` before a later
  login or check can reactivate the account.
- Confirmed for CR-047 sequencing: Phase 5.1D still owns provider launch
  options, requested/effective probes, runtime snapshots, proxy transport
  proof, Runner/CDP/default-fallback removal, and final server-like acceptance.
  Phase 5.1C completion does not claim those surfaces.
- Confirmed for CR-112: QR login and accepted Cookie login converge on the
  same application-managed persistent Profile resolved from
  `social_account.profile_key`. The persistent Profile is the normal browser
  session and crawl environment for both login modes.
- Confirmed for CR-112: a Bridge- or manually supplied Cookie is bootstrap,
  refresh, recovery, and migration material. The monitor injects the candidate
  Cookie into an account-bound persistent Profile, validates the exact platform
  identity in that Profile, and activates the result only after validation.
  The verified Cookie is also retained through the encrypted account store;
  connector cache is never durable login authority.
- Confirmed for CR-112: an existing active Profile must not be damaged by a
  failed Cookie refresh. Packet C must use a staged or equivalently reversible
  Profile update and preserve the previously active Profile and verified
  encrypted Cookie when validation or persistence fails.
- Confirmed for CR-112: the target managed-account crawl path does not pass raw
  Cookie material in child-process arguments. The monitor prepares and
  validates the persistent Profile before crawler launch, and acceptance must
  prove through process inspection that raw Cookie is absent from child argv.
  Current `runner.py --cookies` behavior remains baseline evidence until the
  approved migration is implemented; it is not the CR-112 target contract.
- This confirmation resolves only CR-112 Profile persistence, login-material
  authority, and raw-Cookie argv disposition. CR-112 remains `Needs
  Confirmation` for same-host V1 scope, project-owned extension/connector
  delivery, and sequencing relative to CR-070.
- Confirmed for CR-047 / Phase 5.1D: the pre-lock proxy priority remains task
  proxy, account proxy, then default network. After an account identity is
  locked, a null `proxy_id` is an explicit direct-network policy rather than a
  task-proxy or default-network fallback; a non-null `proxy_id` is an
  account-bound policy whose browser-routed region must be proven. This does
  not authorize task-level proxy overrides or change CR-112/CR-070 ownership.

## 2026-07-20

- Confirmed for CR-117: a clean Windows local deployment selects one browser in
  this order: valid explicit executable, Chrome, Edge, supported Chromium,
  installed Playwright Chromium, then automatic Playwright Chromium install.
  The versioned selection manifest is deployment-local and authoritative for
  every independent account Profile on later starts. Cross-process locking
  covers the complete read/select/write transaction. A missing saved browser
  fails closed; a newly installed higher-priority browser does not replace it.
- Confirmed for CR-117: existing Profile data without a selection manifest
  preserves the pre-CR-117 authority: valid explicit executable when supplied,
  otherwise Playwright Chromium. Browser-channel migration is an explicit
  reset/re-login operation, not an automatic fallback.
- Confirmed for CR-117: actual browser version remains required and is recorded
  in the runtime snapshot, but version change by itself is non-blocking. Other
  managed identity, Profile, proxy, malformed-version, and proof failures stay
  fail closed. This changes runtime compatibility, not the generated account
  identity catalog.
- Confirmed for CR-117: both Windows local launchers run the shared preflight.
  Automatic installation uses the active interpreter and only the `chromium`
  target. Docker and service-only automatic installation remain unchanged.

- Confirmed for CR-116: Playwright persistent contexts do not expose an owning
  `Browser` object. Effective Chromium version proof uses the exact page's
  temporary CDP `Browser.getVersion` response and immediately detaches. The
  requested plan version is not an evidence fallback; absent or malformed CDP
  evidence still fails closed.
- Confirmed for CR-116: the current account identity catalog is generator
  `1.1`, environment `v2`. It keeps the six template names, deterministic
  selection order, seed derivation domain, Profile ownership, and proxy policy,
  while aligning UA version with pinned Playwright 1.45 Chromium
  `127.0.6533.17` and aligning `accept_language` with the provider-effective
  locale (`zh-CN`, `zh-HK`, or `en-SG`).
- Confirmed for CR-116: v1 account identity rows are not rewritten in place.
  They fail closed as `account_identity_requires_relogin` and require the
  existing explicit audited reset/re-login flow before reuse.
