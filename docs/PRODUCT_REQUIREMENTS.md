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
- failure reasons are clear for administrators and business-friendly for normal
  users;
- long run lists remain usable with pagination;
- archived/noise records do not dominate the default operational view.

## 4. Report Center

Roles:

- administrator;
- normal user.

Purpose:

- view reports, lead details, and email sending records.
- group report history by monitoring task and preserve deleted-task context.

Features:

- group reports by monitoring task by default;
- filter by law firm, platform, risk level, and date;
- preview HTML report;
- switch lead details when a different report is selected;
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

Acceptance:

- selecting different reports changes preview and lead details immediately;
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
- automatic delivery uses these schedule-window keys:
  - `daily`: `{job_id}_{YYYY-MM-DD}`;
  - `6h`, `12h`, and `cron`: `{job_id}_{YYYY-MM-DD}_{HH}`.

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

Rules:

- one platform account maps to one profile;
- profile path is not shown to users;
- account name is display-only and not profile identity;
- login sessions are scoped to the current account;
- no phone-login UI is shown unless a complete supported chain exists;
- verification/captcha/SMS states are returned, not bypassed.

Acceptance:

- adding an account does not show platform-global status tables;
- login succeeds through web UI in a server-like environment;
- adding a second same-platform account does not reuse the first profile.

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

Rules:

- SMTP password is encrypted and masked;
- SMTP test verifies connection/send ability;
- report generation does not depend on SMTP availability.

### 6.4 Mail Templates

Purpose:

- manage report email templates.

Features:

- subject template;
- HTML body;
- variable insertion;
- real-time preview;
- active template marker.

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
