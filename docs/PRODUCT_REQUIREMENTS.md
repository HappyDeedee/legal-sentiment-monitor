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

## 1. Overview

Roles:

- administrator;
- normal user.

Purpose:

- act as the operations home after login;
- show task, run, report, and email delivery health;
- provide common entry points and drilldowns;
- surface account/resource health only as concise business signals.

Administrator view:

- task health: total tasks, active tasks, paused tasks, and tasks needing
  attention;
- run activity: today's runs, running runs, failed runs, and recent completion
  trend;
- report activity: generated reports, unsent reports, failed email delivery,
  and manual-review volume;
- suspected negative lead metrics and risk trend;
- account/platform availability summary;
- recent failures and drilldowns into the affected page.

Normal-user view:

- own task health;
- own recent runs;
- own latest reports and delivery state;
- own suspected negative lead trend where available;
- platform availability in business language when it affects task execution;
- shortcuts to create a task and view reports.

Rules:

- the overview should not behave like a system diagnostics page;
- long scheduler, browser, platform, and deployment status blocks belong in
  administrator System Diagnostics unless summarized as a small health signal;
- text-only status areas should be replaced by compact metrics, charts,
  grouped summaries, and drilldown links;
- labels such as "configuration incomplete" must identify the affected area or
  be removed;
- "refresh global status" should be replaced by page-specific refresh controls
  with a last-updated time.

Acceptance:

- no project progress, debug, self-test, command, local path, or implementation
  wording is shown;
- normal users do not see resource-management controls;
- operations home supports desktop, tablet, and mobile layouts without
  overlapping content.

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

- page order should emphasize Operations Home, Monitoring, Run Center, and
  Report Center;
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

## 3. Run Center

Roles:

- administrator;
- normal user.

Purpose:

- inspect execution status, logs, counts, failures, and stop actions.
- filter, page, archive, and restore run records without losing history.

Table columns:

- run ID;
- task ID;
- task name/law firm;
- platform;
- search term summary;
- status;
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
- deleted task history remains visible as original task deleted;
- running processes can still be stopped even if the task was deleted;
- logs open in a large modal, auto-positioned at the latest content;
- logs support refresh, copy, and download.
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

Status: Accepted for CR-034 / Phase 20, not implemented yet.

Purpose:

- make one run record the primary place to inspect the full execution
  lifecycle;
- avoid forcing operators to switch from Run Center to Report Center to
  understand AI evaluation progress or per-item evaluation evidence.
- make Run Center / Run Detail the primary operational home for run-scoped
  leads and AI evaluation records, including records that exist before report
  generation.

Proposed rules:

- Run Center should provide a per-run detail surface grouped by `run_id`.
- Run detail should show collection, ingestion, AI evaluation, report
  generation, and email delivery in one lifecycle view.
- The AI Evaluation section should list every evaluation candidate/result for
  the run, including items evaluated before a report exists.
- Evaluation detail should distinguish business-safe input/output summaries
  from administrator-only debug fields.
- Exact AI request/response traceability requires new trace snapshots for new
  evaluations. Old evaluations without snapshots should be labeled as
  limited-context history.
- Report Center should retain final report, report leads, downloads, and email
  delivery history, but should expose explicit "view leads" actions and link
  back to run detail where possible.
- Report Center lead detail must show whether the visible list is scoped to a
  selected report, selected report group, originating run, or current filters;
  it must not appear as an unlabeled global lead workbench.
- Report Center "view leads" is a report-scoped shortcut, not the primary
  lead/evaluation workbench.

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
- Report Center and future Run Detail views never label missing AI evaluation
  records as no-risk.

## 4. Report Center

Roles:

- administrator;
- normal user.

Purpose:

- view reports, lead details, and email sending records.
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
- Report Center is not the primary surface for every AI evaluation record;
  per-run lifecycle and per-evaluation evidence belong to Run Detail.
- if operators need to inspect lead/evaluation evidence before a report exists
  or after a partial/failed run, the entry point is Run Center / Run Detail.
- Lead-state filtering should live inside the scoped lead drawer, not as a
  first-level Report Center filter. It filters only the currently selected
  report or run lead scope and should not make the Report Center read like a
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
  report row/status action and should not dominate the initial Report Center
  archive layout.
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
- notes;
- latest check time;
- latest error.
- recognized platform identity, including display name and avatar when
  available.
- accepted future CR-047 browser-environment summary: browser platform,
  timezone/locale, screen size, environment lock state, and proxy binding state
  after Phase 5.1 is implemented.

Rules:

- one platform account maps to one profile;
- profile path is not shown to users;
- future CR-047 implementation must keep one platform account mapped to one
  `profile_key` and one fixed browser environment;
- account name is display-only and not profile identity;
- login sessions are scoped to the current account;
- no phone-login UI is shown unless a complete supported chain exists;
- verification/captcha/SMS states are returned, not bypassed.
- platform avatar display must not expose signed external image URLs or query
  parameters to the frontend; use a same-origin server-side cache endpoint and
  fall back to the placeholder when the avatar cannot be fetched safely.
- browser-environment summaries must not expose raw profile paths, cookies,
  proxy credentials, local command lines, CDP endpoints, noVNC sessions, or
  fingerprint-debug output.

Acceptance:

- adding an account does not show platform-global status tables;
- login succeeds through web UI in a server-like environment;
- adding a second same-platform account does not reuse the first profile;
- recognized account avatars render from a customer-safe same-origin URL and
  do not expose platform signatures, cookies, profile paths, or proxy secrets.
- after CR-047 is implemented, repeated login-state checks and crawl runs for
  the same platform account reuse the same locked browser environment unless
  an administrator performs an explicit audited reset/re-login flow.

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
- task proxy overrides account proxy;
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
