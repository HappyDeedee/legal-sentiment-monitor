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

## 1. Overview

Roles:

- administrator;
- normal user.

Purpose:

- show operational status;
- provide common entry points;
- surface platform, account, proxy, scheduler, and report issues.

Administrator view:

- total tasks;
- active tasks;
- today's runs;
- collected contents;
- suspected negative leads;
- high-risk leads;
- manual-review leads;
- reports;
- account resource count;
- proxy resource count;
- AI access count;
- recent failures;
- resource warnings.

Normal-user view:

- own active tasks;
- own recent runs;
- own latest reports;
- platform availability in business language;
- shortcuts to create a task and view reports.

Acceptance:

- no project progress, debug, self-test, command, local path, or implementation
  wording is shown;
- normal users do not see resource-management controls.

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

## 3. Run Center

Roles:

- administrator;
- normal user.

Purpose:

- inspect execution status, logs, counts, failures, and stop actions.

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

Acceptance:

- status refresh works while a run is active;
- failure reasons are clear for administrators and business-friendly for normal
  users.

## 4. Report Center

Roles:

- administrator;
- normal user.

Purpose:

- view reports, lead details, and email sending records.

Features:

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

Acceptance:

- selecting different reports changes preview and lead details immediately;
- no-risk reports can still be generated and sent.

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
- account resource warnings;
- proxy warnings;
- recent failures;
- configuration gaps.

Rules:

- diagnostic text must be customer-safe;
- raw paths and secrets are not shown to normal users.
