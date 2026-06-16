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
