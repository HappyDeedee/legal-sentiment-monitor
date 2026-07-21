# Product Requirements

This document describes every active product area in the Legal Sentiment
Monitor web console. It is the product reference for UI, API, and testing work.

## Global Principles

- Administrators manage resources and system capability.
- Normal users submit monitoring needs.
- Normal users should not need to understand accounts, proxies, profiles,
  browser processes, API keys, SMTP passwords, or crawler commands.
- All pages must follow the UI rules in `UI_UX_GUIDELINES.md`.
- Customer-facing UI must avoid implementation-only wording and raw paths.
- Phase 10-18 console work should use the monitoring task loop as the main
  product path: create task, run collection, inspect report, and review email
  delivery.
- Global or vague status language should be replaced with page-specific,
  action-specific language that tells the user what changed and what needs
  attention.
- MediaCrawler is an internal collection engine for the product, not a public
  cockpit. Public product flows should speak in Legal Sentiment Monitor terms
  and should not expose raw crawler/data routes, command-line concepts, local
  files, profile paths, cookies, proxy credentials, or provider debug details
  outside trusted administrator diagnostics.
- Future `/monitor-next` planning under CR-092 is not a change to the current
  `/monitor` product flow. Current Task Center, Run Detail, drawer/modal,
  select/date, report/email, routing, permission, and scroll behavior remain
  the baseline until an explicit replacement gate is accepted and verified.

## 1. Overview

Roles:

- administrator;
- normal user.

Purpose:

- act as the operations home after login;
- show task, run, report, and email delivery health;
- provide common entry points and drilldowns;
- surface account/resource health only as concise business signals.
- help the user judge within about 10 seconds whether today's monitoring is
  normal, where risk or exception exists, and where to click next.

Administrator view:

- task health: total tasks, active tasks, paused tasks, and tasks needing
  attention;
- run activity: today's runs, running runs, failed runs, and recent completion
  trend;
- report activity: generated reports, unsent reports, failed email delivery,
  and manual-review volume;
- suspected negative lead metrics and risk trend;
- account/platform availability summary;
- administrator-only resource health for accounts, proxies, AI access, and
  SMTP/session status;
- recent failures and drilldowns into the affected page.

Normal-user view:

- own task health;
- own recent runs;
- own latest reports and delivery state;
- own suspected negative lead trend where available;
- platform availability in business language when it affects task execution;
- shortcuts to create a task and view reports.
- no account, proxy, AI, SMTP, session, or administrator resource details.

Rules:

- the overview should not behave like a system diagnostics page;
- the accepted dashboard reading path is overall state, recent trend, problems
  to handle, platform or workflow source, and destination for action;
- the current accepted chart modules are KPI strip, monitoring trend, issue
  distribution, platform distribution, delivery/review, and administrator-only
  resource health;
- first implementation should reuse existing tasks, runs, reports, mail state,
  AI lead/review, platform, and administrator resource data. Task funnel,
  platform risk matrix, keyword heat, AI quality, and task rankings are later
  enhancements rather than current required data;
- long scheduler, browser, platform, and deployment status blocks belong in
  administrator System Diagnostics unless summarized as a small health signal;
- text-only status areas should be replaced by compact metrics, charts,
  grouped summaries, and drilldown links;
- do not use the older process-node or `流程总览` diagram as the future
  dashboard target;
- labels such as "configuration incomplete" must identify the affected area or
  be removed;
- global refresh wording should not appear as a second command surface. The
  active page is refreshed through the shared top-bar icon, while pages may
  keep only scoped refresh actions that do different work.

Acceptance:

- no project progress, debug, self-test, command, local path, or implementation
  wording is shown;
- normal users do not see resource-management controls;
- operations home supports desktop, tablet, and mobile layouts without
  overlapping content;
- key numbers, legends, and labels are visible without hover;
- mobile has no horizontal scrolling and no one-character Chinese text columns.

## 2. Monitoring

Roles:

- administrator;
- normal user.

Purpose:

- create and manage monitoring tasks.

Normal-user task wizard:

1. Target
   - law firm name;
   - aliases.
2. Collection Content
   - platforms;
   - platform search terms;
   - crawl range:
     - max items;
     - start page;
     - max pages;
     - time window;
   - comment collection.
3. Schedule
   - frequency;
   - send time.
4. Report
   - recipient emails.

Administrator advanced options:

- account binding;
- proxy binding;
- AI access override;
- email template override;
- browser mode;
- output mode.

Rules:

- law firm name and aliases are evaluation/report context;
- platform search terms are the actual platform search input;
- exclude words are post-collection filters;
- crawl range is a user-facing scope control, not a timeout estimator;
- `max_items` is a content-count cap and may still produce fewer usable results
  after platform limits, deduplication, exclusion words, and time filtering;
- `start_page` applies when the platform crawler honors it;
- `max_pages` is approximate in V1 and may be converted into an item-count cap;
- `time_window` may use platform-native search filters where available, but V1
  must also treat it as monitoring-layer result filtering because platform
  support is not uniform;
- user-facing copy must not promise exact cross-platform page or time-window
  behavior;
- task timeout is controlled by administrator Runtime Strategy and is not
  computed from the user's crawl range;
- AI and email are optional for collection start;
- missing platform resources should block only affected platforms and give a
  clear message.

Crawl range capability matrix:

| Platform | max_items | start_page | max_pages | time_window |
| --- | --- | --- | --- | --- |
| Douyin | content-count cap | platform crawler start page when honored | approximate item-count conversion | platform publish-time filter where possible plus monitoring-layer filter |
| Xiaohongshu | content-count cap | platform crawler start page when honored | approximate item-count conversion | time-descending sort plus monitoring-layer filter |
| Kuaishou | content-count cap | platform crawler start page when honored | approximate item-count conversion | monitoring-layer filter unless native support is implemented later |

If platform behavior changes in MediaCrawler, update this matrix and the
corresponding tests before changing customer-facing copy.

Acceptance:

- normal users can create a task without selecting accounts or proxies;
- administrators can access advanced settings;
- task fields clearly state their actual use.

## 2.1 Global Page Flow And Navigation

Roles:

- administrator;
- normal user.

Purpose:

- make the monitoring task loop clear from login onward;
- reduce nested and popover-only navigation;
- keep administrator-only resource work available without distracting normal
  users.

Navigation rules:

- page order should emphasize Operations Home, Monitoring, and Task Center;
- Task Center replaces the former separate top-level Run Center and Report
  Center entries. It contains task/report grouping as the default first view
  and run records as a secondary troubleshooting view;
- Resource Management and System Configuration should appear as expandable
  navigation groups;
- primary navigation must not rely on hover-only popovers;
- mobile navigation must use a touch-friendly drawer or equivalent grouped
  pattern;
- the authenticated user display and logout action should be grouped at the top
  right on desktop and in a predictable account area on mobile.

Acceptance:

- administrators can reach all existing administrator pages through stable
  navigation;
- normal users see only their allowed pages;
- mobile users can reach nested pages without precision hover or clipped menus.

## 3. Task Center

Roles:

- administrator;
- normal user.

Purpose:

- make the monitoring task-to-public-opinion relationship clear in one place;
- group reports and public-opinion result summaries by monitoring task;
- inspect execution status, logs, counts, failures, and stop actions through
  the run-record subview and Run Detail;
- filter, page, archive, and restore run records without losing history.

Default task-group fields:

- monitoring task / law firm;
- platforms;
- keyword summary;
- latest task/report state;
- latest run or report time where available;
- collected count;
- new count;
- suspected negative count;
- high-risk count;
- manual-review count;
- unevaluated count;
- actions, especially Run Detail.

Run-record subview fields:

- task ID;
- run ID;
- status;
- task name/law firm;
- platform;
- search term summary;
- start time;
- duration;
- collected count;
- new count;
- suspected negative count;
- high-risk count;
- manual-review count;
- failure reason;
- actions.

Rules:

- run ID and task ID must be clearly distinct;
- flat Task Center rows show task ID, run ID, and compact status first;
- grouped Task Center rows hide the duplicated task ID because the group header
  already identifies the monitoring task; group rows show run ID and compact
  status first;
- grouped Task Center headers show aggregate run metrics as compact labeled
  chips instead of one long slash-separated sentence. The chips preserve run
  count, collected count, new count, suspected negative, high risk,
  manual-review, and unevaluated values, with limited-context notes shown only
  when needed;
- completed status cells stay short and do not include long ingestion detail;
  full progress remains available in Run Detail;
- status cells render as compact text-sized badges rather than full-width
  progress-like bars;
- status badges show only normalized short lifecycle labels; backend
  `display_status` or progress text must not become the visible badge label;
- first-level run status badges should be lightweight state-dot labels scoped to
  Task Center tables so task ID and run ID remain visually prioritized;
- deleted task history remains visible as original task deleted;
- running processes can still be stopped even if the task was deleted;
- run-record rows do not duplicate the log button; operators open Run Detail
  and use the `采集日志` section for the same log content;
- logs support refresh through Run Detail and copy/download from the Run Detail
  log section.
- Task Center uses the shared top-bar current-page refresh icon for page-level
  reloads; the first-level Task Center header and filter toolbar should not
  repeat a second generic refresh button.
- the default list should prioritize `visibility = visible` records;
- archived records are hidden from the default list but remain available to
  administrators through filters;
- archive and restore are logical visibility operations, not physical deletion;
- `run_type = test` records can be hidden by default when they are operational
  noise;
- skipped or preflight-blocked records should be grouped, filtered, or visually
  downplayed so they do not bury meaningful runs.
- active runs should surface progress before final completion. During platform
  collection, the UI may show provisional collected/discovered counts derived
  from safe crawler output progress; after platform ingestion finishes, final
  collected, filtered, excluded, and new counts replace provisional values.
- provisional collection progress must be labeled or styled so operators do not
  confuse it with final ingested counts. Missing or partially written crawler
  output should show a waiting/progress state rather than a false zero or a
  false final count.
- while AI evaluation is running, the UI should show evaluation progress and
  batch-updated suspected negative, high-risk, and manual-review counts where
  available.
- active run refresh should continue while visible runs remain running, and it
  should stop only after active runs finish, fail, time out, are cancelled, or
  are marked interrupted.
- timeout runs may have partial provisional or final results. The UI should
  preserve those results and explain that the task reached the system time
  limit instead of implying that collection never started.
- interrupted runs are distinct from completed-with-errors runs. They should
  explain that execution was interrupted or no longer active, preserve any
  collected/evaluated partial results, and offer safe next actions such as
  viewing logs or viewing generated/partial results when available.
- interruption labels must be based on lifecycle evidence, not elapsed time
  alone. The product should prefer step-level causes such as crawler process
  disappeared, browser/session closed, resource lock lost, AI evaluation
  stopped, report generation failed, email delivery skipped/failed, or service
  restart recovery when those causes are known.
- retrying should be visible as part of the active run state when a retry is in
  progress or has been exhausted. The user should be able to distinguish
  "retrying a temporary issue" from "timed out" and "interrupted".
- AI evaluation failure or interruption should degrade unresolved items to
  manual review during active finalization when safe; it should not leave a run
  indefinitely running or block report generation when collected data exists.
- AI progress should show more than a single final count where available:
  total candidates, successful evaluations, failed/fallback evaluations,
  pending-review items, and unresolved items.

Required controls:

- pagination;
- task/law-firm filter;
- status filter;
- platform filter;
- run type filter;
- visibility filter;
- date range filter;
- archive/restore action where permitted.

Filter interaction requirements:

- page-level filter dropdowns must open aligned to their trigger controls in
  the console shell at `1440x900`, `1024x768`, and `390x844`;
- filter dropdowns may use an in-page floating menu to avoid native browser
  dropdown misalignment, but the stored select value and existing filtering
  semantics must remain unchanged;
- page-level date range filters may use an in-page floating date menu to avoid
  native browser date-picker misalignment, but the stored date value and
  existing filtering semantics must remain unchanged;
- date filter menus must stay visually anchored to their trigger while keeping
  the calendar readable. Current date filters behave like ordinary attached
  dropdowns: mount the active menu inside the clicked date control wrapper,
  position it directly below that field, match the clicked trigger width, and
  keep the top anchor marker centered;
- date filter menus must keep all seven weekday/day columns readable; browser
  button padding or automatic minimum widths must not clip day numbers in
  narrow filter menus;
- ordinary edit/configuration form selects and date inputs are not part of the
  Task Center filter dropdown/date-picker behavior unless a later accepted
  requirement changes them.
- CR-071 is the accepted exception for selected drawer/modal `select` fields:
  Monitoring task edit, Platform Account detail, Proxy edit, AI Access edit,
  AI Evaluation Rule edit, Mail Configuration edit, and Mail Template edit
  reuse the same enhanced `.page-filter-region select` mechanism for visual
  consistency. AI Access `模型名称` remains its own combobox.
- CR-072 is the accepted focused exception for Monitoring task edit
  `自定义开始日期` and `自定义结束日期`: these two fields reuse the existing
  `.page-filter-region input[type="date"]` local attached date-picker
  mechanism, while unrelated ordinary business date fields remain native unless
  separately accepted.

Acceptance:

- status refresh works while a run is active;
- provisional collection progress is visible for long active runs before the
  platform subprocess exits;
- AI evaluation progress updates during long evaluation batches;
- interrupted runs are not shown as ordinary running records;
- partial AI/manual-review reports can remain accessible when collected data
  exists;
- failure reasons are clear for administrators and business-friendly for normal
  users;
- long run lists remain usable with pagination;
- archived/noise records do not dominate the default operational view.

### 3.1 Run Detail And AI Evaluation Traceability

Status: Implemented and verified for CR-034 / Phase 20B-E.

Purpose:

- make one run record the primary place to inspect the full execution
  lifecycle;
- avoid forcing operators to switch between separate run and report centers to
  understand AI evaluation progress or per-item evaluation evidence.
- make Task Center / Run Detail the primary operational home for run-scoped
  leads and AI evaluation records, including records that exist before report
  generation.

Implemented rules:

- Task Center provides a per-run detail surface grouped by `run_id`.
- Run detail shows collection, ingestion, AI evaluation, report
  generation, and email delivery in one lifecycle view.
- The AI Evaluation section lists every evaluation candidate/result for
  the run, including items evaluated before a report exists.
- Evaluation detail distinguishes business-safe input/output summaries
  from administrator-only debug fields.
- Exact AI request/response traceability uses trace snapshots for new
  evaluations. Old evaluations without snapshots should be labeled as
  limited-context history.
- Task Center retains final report, report leads, downloads, and email delivery
  history through Run Detail, not through first-level task or run row actions.
- Task Center lead detail is consolidated into Run Detail's `AI 评估` section:
  by default it shows the current run's candidates, and report `查看线索`
  applies a report-scope filter to that same table instead of opening a second
  lead drawer.
- AI Evaluation filters include report, status, risk, platform, keyword, and
  title; the active scope must remain visible so the list does not appear as an
  unlabeled global lead workbench.
- The report filter is only a visible selectable `报告范围` dropdown when the
  current run has multiple reports. If the run has zero reports or exactly one
  report, show a scope note instead of a redundant dropdown.
- Task Center rows expose one action, `详情`. Report preview, lead inspection,
  delivery history, resend, and downloads belong inside Run Detail's `报告` and
  `邮件交付` sections.

Confirmed:

- trace retention must be administrator-configurable, defaulting to 30 days;
- normal users should see only business-safe AI evaluation summaries for their
  own runs, not full prompt snapshots, request payload snapshots, or
  administrator debug metadata;
- normal users must not see raw model responses;
- administrators may see redacted raw model responses for diagnosis;
- unredacted raw model responses must not be stored or exposed to any role.
- trace storage uses a new `ai_evaluation_traces` table with capped/redacted
  JSON fields;
- accepted default size guardrails are: each trace is about 64KB, prompt
  snapshot up to 16KB, request snapshot up to 24KB, response snapshot up to
  24KB, and sampled comments up to 20 comments with per-comment truncation.

### 3.2 AI Evaluation Accuracy And Lead Status

Status: Accepted for CR-045 / Phase 7.2, not implemented yet.

Purpose:

- prevent unevaluated content from being mistaken as safe;
- make target-law-firm relevance stricter before an item is counted as a
  suspected negative lead;
- reduce broad-keyword noise without blocking report generation.

Rules:

- `source_keyword` is recall provenance only. It can explain why a platform
  item was collected, but it must not by itself prove that the item is related
  to the target law firm.
- AI relatedness should require evidence in the collected content itself:
  title, description/body, author, or sampled comments should contain the
  target law firm name, an accepted alias, or a clearly equivalent contextual
  reference.
- Homonyms, geography, generic legal/refund wording, and unrelated law-firm
  names should be treated as not related unless the content also points to the
  target law firm or an accepted alias.
- Comments may support relatedness, negative-signal, and evidence extraction
  only when comments were actually collected and included in the evaluation
  payload.
- Missing AI evaluation rows, AI timeout leftovers, or interrupted evaluation
  candidates must not be displayed or filtered as no-risk content. They should
  become pending manual review during safe finalization, or show an explicit
  unevaluated/limited-context state when mutation is not safe.
- Lead status should distinguish unrelated, evaluated no-risk, suspected
  negative, high-risk, pending manual review, and unevaluated/limited-context
  history.
- Lead status filters should be exact wherever they are shown: `高风险` shows
  only high-risk rows/reports, while `疑似负面` shows only suspected-negative
  rows/reports and must not include high-risk rows just because high risk is
  also negative.
- AI output remains lead screening, not factual determination.

Acceptance:

- broad refund/legal posts collected by a target-bearing keyword are not marked
  as target-related negative leads when the actual content lacks target-law-firm
  evidence;
- target-law-firm or alias mentions in title, description, author, or comments
  can still produce suspected-negative/high-risk leads when negative signals
  are present;
- Task Center and Run Detail views never label missing AI evaluation
  records as no-risk.

## 4. Task-Grouped Reports

Roles:

- administrator;
- normal user.

Purpose:

- define the report grouping behavior now embedded in Task Center;
- view reports, lead details, and email sending records from a task-scoped
  surface;
- group report history by monitoring task and preserve deleted-task context.

Features:

- group reports by monitoring task by default;
- filter the first-level report list by report dimensions such as law firm,
  platform, date, and report range;
- preview HTML report;
- explicitly view lead details for a selected report or group;
- switch lead details when a different report is selected, with visible scope
  and count;
- download Markdown/Excel when available;
- view email send status.

Rules:

- report wording uses suspected negative leads;
- AI output is a lead-screening result, not factual determination;
- cover images use source cover links by default;
- optional cover archiving is disabled by default.
- when `job_id` resolves to an active task, group by that task;
- when `job_id` is null or the task is unavailable, use
  `job_snapshot_json` to group and label the report;
- deleted-task reports should show business context such as law firm name,
  platforms, keywords, frequency, and deleted-task status when available;
- email delivery status should distinguish automatic delivery from manual
  resend.
- lead detail must not silently display all accessible leads or all filtered
  leads without a scope label.
- if a current-filter aggregate lead list is kept, label it as a filtered
  aggregate and keep it visually distinct from selected-report lead detail.
- Task Center report grouping is not the primary surface for every AI evaluation record;
  per-run lifecycle and per-evaluation evidence belong to Run Detail.
- if operators need to inspect lead/evaluation evidence before a report exists
  or after a partial/failed run, the entry point is Task Center / Run Detail.
- Lead-state filtering should live inside the scoped lead drawer, not as a
  first-level Task Center filter. It filters only the currently selected
  report or run lead scope and should not make Task Center read like a
  global lead workbench.

Acceptance:

- selecting different reports changes preview, and choosing "view leads" opens
  scoped lead details immediately;
- users can tell whether visible leads belong to a selected report, selected
  group, originating run, or current filters;
- no-risk reports can still be generated and sent;
- orphan reports remain understandable after their task is deleted or missing.

## 4.1 Email Delivery

Roles:

- administrator;
- normal user for own reports where permissions allow resend.

Purpose:

- send report emails reliably;
- prevent duplicate automatic sends;
- preserve manual resend history.

Rules:

- report generation must not depend on SMTP success;
- automatic email delivery is idempotent per task and schedule window;
- manual resend is allowed and logged separately;
- delivery history should show send type, status, time, recipient summary, and
  error message when failed;
- delivery history should be opened as scoped secondary detail from a selected
  report row/status action and should not dominate the initial Task Center
  task-group layout.
- real email sends must be understandable after the fact: delivery history
  should show whether the send was automatic, manual resend, or an explicit
  validation send, plus the related task/report/run context and effective
  recipients where permitted.
- recipient precedence must be understandable before and after sending: task
  recipients are the delivery targets when present, global default recipients
  are fallback-only, and the SMTP sender is only the from-address.
- routine automated tests and local diagnostics must not silently send real
  external emails. Product operation uses one administrator-controlled Mail
  Configuration switch for real email delivery, defaulting off.
- when the administrator switch is off, mail test, manual resend, and
  automatic delivery do not submit real SMTP; report generation still
  completes and delivery history records a customer-safe skipped or failed
  state where applicable.
- when the administrator switch is on and SMTP configuration is complete, mail
  test, manual resend, and automatic delivery may submit real SMTP.
- the frontend should warn that SMTP acceptance is not recipient inbox proof.
- Mail Configuration should use one page-level primary action group for edit
  configuration, send test mail, refresh/status, delivery-status navigation,
  and the compact real-email state. Inner SMTP/defaults summaries should not
  repeat the same edit/test actions.
- The real-email send switch remains one administrator-only safety control,
  but its normal off/on state should be compact and label-based; enabling real
  SMTP still requires explicit confirmation.
- automatic delivery uses these schedule-window keys:
  - `daily`: `{job_id}_{YYYY-MM-DD}`;
  - `6h`, `12h`, and `cron`: `{job_id}_{YYYY-MM-DD}_{HH}`.

Deferred role-governance direction:

- administrators should eventually be able to control whether normal users can
  send or resend report emails;
- normal-user send/resend quotas may be added later;
- this role/quota work is not part of the immediate CR-036 hidden-email safety
  fix.

Acceptance:

- repeating the same scheduler window does not send multiple automatic emails;
- manual resend can send again and is visible as manual history;
- failed sends are visible without blocking report creation.

## 5. Resource Management

Resource management is administrator-only.

### 5.1 Platform Accounts

Purpose:

- manage platform account resources and login state.

Fields:

- account name;
- platform;
- login type: QR login or Cookie login;
- status;
- bound proxy;
- latest check time;
- latest error summary as read-only operational state;
- recognized platform identity, including display name and avatar when
  available.
- the account list keeps recognized avatar/display name compact, omits the raw
  platform identifier, and shows recognition time in its own column immediately
  before latest check time; account details retain the complete identity.
- existing saved Cookie/Profile recheck before requiring a new login when an
  account is marked for re-login.
- administrator-only complete structured Cookie reveal/copy for explicit
  import through Cookie login on another installation; destination-local
  encryption and Profile creation remain required.
- CR-047 Phase 5.1A-C account-identity summary: safe browser platform,
  identity template, region, environment lock/re-login state, and proxy binding
  state are available now. Phase 5.1D adds one administrator-only compact
  runtime row with provider/mode, last proof time, proxy proof state, fallback
  state, unsupported-field count, and mismatch field names. Raw runtime JSON,
  requested/effective values, probes, Profile/executable paths, proxy endpoints,
  CDP/debug values, fingerprint seeds, and commands remain hidden.
- accepted CR-047 pre-login advanced option: administrators may choose
  only a template family before first login; ordinary account creation uses
  automatic template selection.
- proposed future CR-070 account package actions: administrator-only
  metadata-only export, slim encrypted login-state migration export, import
  preflight, import result, and post-import login verification state.
- proposed future CR-070 package operation status: export/import in progress,
  ready for download, failed, cancelled, expired, deleted, active after import,
  or requires re-login after import.
- accepted CR-112 account login actions (Packet B verified, CR-123 presentation
  refinement): QR remains default; QR, same-machine Windows browser login, and
  Cookie import are peer user-facing choices; browser auto-sync is available
  only when enabled and healthy; an administrator may explicitly reveal/copy
  one selected account's complete Cookie from a default-masked field.
- CR-127 login authority: one account has one current pending login attempt.
  Starting QR, Browser, visible-browser, or Cookie login supersedes older
  pending attempts, and a stale callback cannot replace committed
  Cookie/Profile material or its provenance.
- CR-128 saved-state recovery: a limited account with saved material exposes
  one administrator action that checks the Profile first, then uses the
  encrypted Cookie to build a fresh candidate only for a recoverable failure.
  A `requires_relogin` account only rechecks its saved Profile and still needs
  fresh platform login after a failed check. Candidate and active checks must
  match the already-bound platform account identity.

Rules:

- one platform account maps to one profile;
- profile path is not shown to users;
- CR-047 keeps one platform account mapped to one
  `profile_key` and one stable account identity;
- account name is display-only and not profile identity;
- Xiaohongshu display name/avatar come from the successful signed self-info
  readiness response, while the Profile page identifier/home URL remain the
  stable recognized-account binding metadata;
- login sessions are scoped to the current account;
- no phone-login UI is shown unless a complete supported chain exists;
- verification/captcha/SMS states are returned, not bypassed.
- QR login returns only image bytes that decode as a QR code. Advertisements,
  avatars, banners, and diagnostic screenshots are never presented as QR
  codes; second-factor verification remains a distinct state with explicit
  operator guidance.
- Cookie import accepts a standard Cookie header or Structured Cookie Protocol
  V1 data, validates it in a new destination-local candidate Profile, rechecks
  the platform identity, and swaps the Profile/Cookie material atomically only
  after success. Interruption preserves the prior committed material.
- Saved-Cookie recovery preserves its `browser_sync` or `manual` provenance,
  uses the same promotion journal as Cookie import, and leaves the previous
  account/Profile/Cookie state intact when the Cookie is expired or the
  candidate identity is missing or different.
- platform avatar display must not expose signed external image URLs or query
  parameters to the frontend; use a same-origin server-side cache endpoint and
  fall back to the placeholder when the avatar cannot be fetched safely.
- account-identity summaries must not expose raw profile paths, cookies,
  proxy credentials, local command lines, CDP endpoints, noVNC sessions, or
  fingerprint-debug output. The only Cookie exception is the explicit CR-112
  administrator reveal POST response; standard list/detail payloads stay
  masked.
- CR-112 Cookie reveal is administrator-only, returns HTTP 403 to normal users,
  uses no-store/no-cache headers, and keeps the value only in transient page
  memory. It must not enter URL, browser persistent Storage, logs, audit
  details, diagnostics, screenshots, subprocess argv, or subprocess
  environment.
- normal users must not choose account identity templates or browser
  environment fields; administrators must not edit individual UA, viewport,
  screen, timezone, locale, accept-language, device-scale, mobile, or touch
  fields directly.
- after CR-047 selects a template, the UI/API may show a customer-safe summary
  but must treat the generated fields as system-owned identity values.
- after CR-047 locks an account identity, task-level proxy overrides are
  rejected for that account, and proxy changes require explicit audited
  reset/re-login.
- CR-070 export/import is administrator-only and must be hidden from
  normal users.
- metadata-only account package export contains no login state and imported
  accounts require login before use. If it contains real identity details such
  as fingerprint seed, runtime snapshot summaries, or recognized platform
  account IDs, it is still treated as a sensitive package and should use the
  encrypted package envelope by default.
- slim login-state migration package export contains encrypted login/session
  material, necessary profile state, and platform-account metadata. It must
  require explicit administrator confirmation and must not export raw whole
  browser profile cache or temporary artifacts by default.
- account packages move only the selected platform account environment. They
  do not move monitoring tasks, crawl runs, reports, AI traces, email delivery
  logs, users, runtime settings, or customer business history by default.
- importing a slim login-state package does not guarantee platform acceptance.
  The system must verify login state after import before allowing crawl use.
- imported accounts use a target deployment `profile_key`; the source raw
  profile path is never trusted or shown.
- import must not silently use a missing or mismatched target proxy. The
  administrator must map the imported proxy policy to a target-side proxy or
  re-login under the target deployment's proxy rules.
- the encrypted package may show an administrator the source proxy host/IP and
  port as a mapping hint after decryption, but it must not include or display
  proxy username, password, token, authentication header, or provider secret.
- import creates a new target account/profile by default. Replace, merge, or
  overwrite behavior requires a later explicit conflict policy.
- avatar handling in V1 exports metadata only, not cached avatar image bytes.
- export/import surfaces must not show raw cookies, profile paths, proxy
  credentials, proxy endpoint hints outside the decrypted import preflight,
  package passphrases, CDP endpoints, noVNC tokens, or deployment encryption
  keys.
- export/import operations must show a terminal result to the administrator:
  success/ready, failed, cancelled, expired, active after import, or requires
  re-login. A package operation must not remain silently in progress.

Acceptance:

- adding an account does not show platform-global status tables;
- login succeeds through web UI in a server-like environment;
- adding a second same-platform account does not reuse the first profile;
- recognized account avatars render from a customer-safe same-origin URL and
  do not expose platform signatures, cookies, profile paths, or proxy secrets.
- CR-047 account creation can proceed without manual template selection; if an
  administrator uses the advanced path, only the template family is selectable
  before first login.
- Phase 5.1C login-state checks reuse the same locked account identity unless
  an administrator performs an explicit audited reset/re-login flow. Phase
  5.1D and final Phase 5.1 acceptance still must prove all crawl launch paths
  reuse the same effective environment.
- The verified CR-112 Packet D lane proves designated Douyin and Xiaohongshu accounts each
  exact managed-context acquisition, administrator reveal/copy, fresh candidate
  injection, restart identity verification, `fallback_used=false`, and at
  least one persisted real content item through the normal monitor entry.
  Kuaishou remains Deferred.
- CR-128 recovery tests and live evidence prove an expired saved Cookie reaches
  one terminal failure with rollback, while a fresh browser-sync login survives
  service restart, normal collection, and post-crawl Profile validation.
- after CR-070 is implemented, administrators can move an account environment
  to another deployment through a versioned, encrypted, audited package. Import
  succeeds as usable only after compatibility checks and login-state
  verification pass; otherwise the account is retained as needing re-login.
- normal users never see package export/import actions, package operation
  states, package download links, or package diagnostics.

### 5.2 Proxy Resources

Purpose:

- manage proxy resources and binding candidates.

Fields:

- proxy name;
- provider;
- masked proxy URL;
- status;
- max concurrency;
- notes;
- latest check time;
- latest error.

Rules:

- proxy URLs are encrypted and masked;
- before CR-047 locked account identity is active, task proxy overrides account
  proxy;
- after CR-047 locks an account identity, task proxy overrides are rejected for
  that locked account environment;
- account proxy overrides default network;
- no dynamic proxy rotation is included in V1.

Acceptance:

- administrators can create, edit, disable, and delete proxies;
- proxy concurrency is respected.

### 5.3 AI Access

Purpose:

- manage AI API connection resources.

Fields:

- profile name;
- provider;
- base URL;
- model;
- temperature;
- masked API key;
- active/default flag;
- latest test status.

Rules:

- API keys are encrypted and masked;
- connection test only verifies basic API availability;
- evaluation prompt is managed under AI Evaluation Rules.

Acceptance:

- multiple AI access profiles can exist;
- task collection can run without AI.

## 6. System Configuration

System configuration is administrator-only.

### 6.1 Users And Permissions

Purpose:

- manage users and roles.

V1 roles:

- administrator;
- normal user.

Reserved roles:

- reviewer;
- read-only viewer;
- workspace administrator;
- platform super administrator.

Acceptance:

- normal users cannot access administrator-only pages or APIs.

### 6.2 AI Evaluation Rules

Purpose:

- manage prompt, relevance rules, risk levels, and output schema.

Rules:

- API keys are not configured here;
- test can use the standard law-firm sample;
- AI failure produces manual-review leads.

### 6.3 Mail Configuration

Purpose:

- configure SMTP connection and sender identity.
- control whether the system may submit real emails.

Rules:

- SMTP password is encrypted and masked;
- SMTP test verifies connection/send ability;
- report generation does not depend on SMTP availability.
- the page includes one administrator-only real email send switch backed by
  the persisted `real_email_delivery` runtime setting;
- the switch defaults off and must not be duplicated as a second Email group
  in Runtime Strategy.

### 6.4 Mail Templates

Purpose:

- manage report email templates.

Features:

- subject template;
- governed preset styles for the email body;
- system-controlled report body insertion;
- variable insertion for supported subject and summary fields;
- real-time preview;
- active template marker.

Product direction:

- Long-term mail-template management should not depend on unrestricted
  free-form HTML editing. Administrators should choose from a small set of
  preset styles, and the generated report body should always be inserted by the
  system.
- Template preview must clearly indicate when it uses sample data. Historical
  report/email records should show which template was actually used for a
  delivered email.
- New custom HTML templates must preserve the generated report body through
  `{report_html}` or `{report_body}`. Historical templates remain readable, but
  delivery/preview must not silently drop the generated report body.

Variables:

- law firm name;
- date;
- new content count;
- suspected negative count;
- high-risk count;
- manual-review count;
- platforms;
- report body.

### 6.5 Runtime Strategy

Purpose:

- configure runtime behavior without code changes.

Editable settings:

- global crawl concurrency;
- per-platform concurrency;
- task timeout as a run-level wall-clock deadline;
- lock cleanup buffer;
- retry count;
- retry delay;
- QR timeout;
- login session TTL;
- scheduler tick interval;
- run log retention days;
- report retention days.

Layout:

- administrator-only grouped table layout;
- group settings by Crawling, Login, Scheduler, and Retention;
- show each setting with label, current value, input control, range hint, and
  apply scope;
- each grouped table should include columns for setting, current value, input,
  valid range, apply scope, and lock state;
- display apply scope as:
  - immediate;
  - next run;
  - next session;
  - scheduler reload or restart;
- locked settings are read-only with a lock indicator and a short explanation
  that deployment configuration controls the value.

Task-timeout rules:

- `crawler_timeout_seconds` is copied into each new run as its run-level
  wall-clock timeout;
- V1 does not estimate timeout from `max_items`, `max_pages`, or time window;
- timeout runs may still have partial results and should show a customer-safe
  message that the system stopped the task after reaching the configured time
  limit.

Read-only/locked settings:

- data directory;
- profile root;
- database connection;
- encryption key;
- browser executable;
- service port.

### 6.6 System Diagnostics

Purpose:

- show operational readiness and resource issues.

Content:

- scheduler state;
- browser/runtime state;
- data directory state;
- disk-space state;
- backup-set guidance;
- retention-setting state;
- account resource warnings;
- proxy warnings;
- recent failures;
- configuration gaps.

Rules:

- diagnostic text must be customer-safe;
- raw paths and secrets are not shown to normal users.

### 6.7 Managed Account Request Identity

For a managed platform account, the normal monitor path must use the account's
committed Profile and the effective browser environment resolved by the
provider. The platform request Client and signer must consume one frozen
attempt environment containing the account, platform, `profile_key`, browser
proof, proxy revision, identity revision, resolution ID, attempt ID, and run
ID.

The product must keep these distinctions visible in operational state:

- a saved Profile is the normal crawl authority;
- encrypted Cookie is initialization, refresh, recovery, and migration
  material;
- a content response without platform identity proof is not shown as an
  authenticated account success;
- login-required, second-verification, challenge, rate-limit, proxy, signer,
  environment, and account-identity failures are actionable typed outcomes,
  not anonymous success.

A managed account keeps its account-bound Profile, browser, identity, proxy,
and network. The product does not silently substitute a generic Profile,
another account, or a default network. Same-family browser version updates
retain `profile_key`; browser-family/channel changes use a candidate Profile
and explicit identity validation before promotion.

For managed Douyin requests, `msToken`, `webid`, `verifyFp/fp`, and `ttwid`
come from the verified committed Profile and are frozen with Cookie, UA/UA-CH,
screen/browser values, proxy, signer input, `a_bogus`, and the final URL. A
request with missing, changed, fixed, random, or cross-account material stops
before platform dispatch. Content returned without the bound signed request
proof does not count as authenticated collection.

Every managed platform attempt must finish with one typed terminal result.
Only a bounded `transient_network` result may retry, using the same frozen
resolution and material revisions with a new attempt ID. Login, verification,
rate, proxy, signature, identity, protocol, timeout, cancellation, and crash
results remain terminal and visible through safe customer-facing status.
Managed child output is redacted before log persistence, and process cleanup
must release locks without changing committed Profile/Cookie authority.
