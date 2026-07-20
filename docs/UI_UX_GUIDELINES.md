# UI/UX Guidelines

## Product Style

The interface must feel like a professional ToB operations system, not a
temporary crawler demo.

Design goals:

- clear hierarchy;
- low learning cost;
- restrained enterprise visual style;
- consistent interaction patterns;
- role-appropriate complexity.

Phase 10-18 visual direction:

- Apple-style clean enterprise interface;
- calm, low-noise surfaces;
- strong but restrained hierarchy;
- polished spacing, readable density, and precise interaction feedback;
- no marketing-style landing page after login.

## Frontend Technology Stack

Current implementation:

- vanilla JavaScript;
- inline or local CSS;
- no external UI component framework in V1 unless a later decision changes the
  frontend stack;
- custom modal and table interactions should follow the rules in this document.

Accepted Phase 10-18 direction:

- keep Vanilla JavaScript plus CSS custom properties;
- do not introduce Tailwind, Alpine.js, Petite-Vue, React, Vue, or a required
  frontend build pipeline in this redesign round;
- optional lightweight libraries may be considered only for focused charting or
  floating menu positioning, and must be recorded before implementation;
- use `FRONTEND_ARCHITECTURE.md` as the frontend architecture reference.

Do not introduce a new UI framework or component library only for a single page
without a change request and decision.

CR-092 future `/monitor-next` planning may evaluate Vite, TypeScript, Vue,
React, and component-library options, but it does not change the current
`/monitor` UI stack or the closed Phase 21 visual baseline. The current formal
console interaction baseline remains Task Center, Run Detail, drawers, modals,
enhanced select/date controls, close behavior, scroll ownership, and routing
until a later replacement gate proves equivalence.

## Global Layout

Use a consistent admin layout:

- left navigation;
- top status/user area;
- page title area;
- status summary area;
- toolbar;
- main content area;
- modal area.

Phase 10-18 layout requirements:

- login success opens the operations home;
- user identity and logout are grouped at the top right on desktop;
- vague global banners such as generic scheduler/configuration status should be
  removed or rewritten into specific actionable state;
- page-level refresh should use one shared top-bar current-page refresh icon;
  first-level pages should not repeat another refresh button when it reloads
  the same data;
- page headers should keep title, summary, primary action, and user controls in
  predictable positions.

## Menu Structure

Administrator:

- Overview
- Monitoring
- Task Center
- Resource Management
  - Platform Accounts
  - Proxy Resources
  - AI Access
- System Configuration
  - Users And Permissions
  - AI Evaluation Rules
  - Mail Configuration
  - Mail Templates
  - Runtime Strategy
  - System Diagnostics

Normal user:

- Overview
- Monitoring
- Task Center

Phase 10-18 menu behavior:

- Overview should be renamed or treated as Operations Home in user-facing
  structure;
- Task Center is the single top-level entry for the former run/report surfaces.
  It opens on task/report grouping and offers a `运行记录` subview for
  operational troubleshooting;
- Resource Management and System Configuration use expanded navigation groups,
  not detached hover-only popovers;
- mobile navigation must work by tap, not hover;
- nested pages should remain reachable with clear active states and without
  clipped submenus.
- tablet and narrow-desktop navigation uses the persistent collapsed icon rail
  without a bottom horizontal scrollbar; the sidebar collapse control remains
  available where the shell exposes it, and true mobile retains the drawer
  trigger.

## Page Structure

Every page should follow this structure:

1. Page title, short description, and primary action.
2. Status summary or key metrics.
3. Toolbar with search, filters, refresh, and batch actions when needed.
4. Main table/list/preview/log area.
5. Modal dialogs for add, edit, test, confirm, and login actions.

Avoid:

- one-off page layouts;
- large inline creation forms on first-level pages;
- repeated menus and tabs for the same function;
- showing administrator resource details to normal users.

Operations pages should prioritize:

- one clear primary action;
- compact key metrics;
- filters before large lists;
- direct drilldown to the next likely operational page;
- visible last-updated time for refreshable data.

Do not let diagnostic or platform status blocks dominate the home page.

## Design System

Use CSS custom properties for:

- color tokens;
- surface and border colors;
- spacing scale;
- radius scale;
- shadows;
- status colors;
- typography scale.

Visual rules:

- use restrained neutral surfaces with clear content contrast;
- avoid one-note color palettes;
- reserve bright colors for state, risk, and primary action;
- keep cards and controls at modest radii unless a later design decision
  changes the system;
- use consistent status tags for running, success, warning, failed, archived,
  manual-review, and pending states;
- use compact headings inside dashboards, tables, sidebars, and modals.
- the Operations Home should prioritize charts, bars, and numbers over prose
  or tables, and desktop/tablet dashboard content should not extend below the
  left navigation/shell height.
- Operations Home charts should expose visible legends or direct labels when
  color meaning is not obvious, keep KPI/alert icons on one compact scale, and
  reserve category palettes for composition views such as platform breakdowns.
- When Operations Home data is sparse, prefer content-sized cards and denser
  chart substrates over viewport-filling empty panels or filler copy.
- CR-105 Operations Home uses a calm ToB operations color ledger: `#F6F8FA`
  page background, `#FFFFFF` cards, `#0F766E` normal/completed/business-total,
  `#2563EB` running/realtime/platform comparison, `#D97706` pending review or
  pending action, `#DC2626` failure/exception, `#991B1B` high-risk public
  opinion, and neutral grays `#64748B` / `#CBD5E1`.
- Platform category colors may appear only inside the platform distribution
  module. They must not override the page-wide semantic meaning of teal, blue,
  amber, red, and dark red.
- The CR-105 Operations Home target is six chart modules: KPI strip,
  `监控走势`, `问题分布`, `平台分布`, `交付 / 复核`, and administrator-only
  `资源健康`. Do not use the older process-node or `流程总览` diagram as the
  future dashboard target.
- CR-105 core dashboard charts should use locally vendored ECharts instances
  instead of handcrafted SVG paths or custom DOM chart geometry. The current
  CR-104 `.operations-trend-svg` and path helper functions are the baseline to
  replace. SVG icons and ECharts internal SVG/canvas output remain allowed.
- CR-105 module alignment is a hard visual rule. KPI cards, trend/issues row,
  and lower modules must share consistent gutters and row edges; card title
  regions should have the same height; headline numbers, legends, direct
  labels, and chart plot origins should sit on stable left edges; lower cards
  should use equal visual height on desktop. KPI cards should align internal
  label, value, and micro-chart positions across all cards. When `资源健康` is
  hidden, the remaining modules should reflow on the same grid instead of
  leaving a blank slot or uneven spacing. Loading, empty, stale, and chart-local
  error states must keep container dimensions stable.
- CR-106A Operations Home refinement should make the top status and
  `问题分布` action-first: high-risk leads and pending review should not be
  visually buried behind lower-severity counts. The `平台分布` module should
  distinguish platform volume from failure signals when current run summaries
  provide that data. The `邮件` module should be labeled as report-level
  delivery state until CR-106B is explicitly accepted. On mobile, KPI cards
  should stay compact enough that `监控走势` and `问题分布` appear early in the
  reading path.

Interaction rules:

- every save, test, run, stop, archive, restore, resend, and refresh action
  needs loading, success, and error feedback;
- destructive or history-changing actions require confirmation;
- disabled controls must explain why when the reason is business-relevant;
- Platform Accounts shows a compact safe account-environment summary. Safe
  proxy/region/template-family controls are editable before login, read-only
  after lock, and unlocked after an explicit `更改环境` action only for the
  `重置并重新登录` workflow.
- The Platform Accounts labelled recent-error card and basic-form warning stay
  on one visible line with ellipses and complete-text titles. The advanced
  error textarea remains the editable full-value surface.
- Account-bound local visible login shows an in-progress state while the user
  completes platform verification, then automatically saves the validated
  Profile result. Closing the account drawer does not cancel reconciliation;
  generic unbound local login remains status-only.
- `requires_relogin` and `resetting` disable QR, visible-browser, Cookie-save,
  and single/bulk account-check actions with customer-safe guidance. The reset
  action remains reachable and must state that Profile, Cookie, and platform
  identity are preserved while login verification is required again.
- more menus close on outside click, escape, successful action, and navigation
  change;
- row action menus must not be clipped by table or scroll containers.
- first-level page filter dropdowns should render through a fixed or portal
  style in-page menu when native browser dropdowns misalign in the console
  shell; keep the underlying select value and filter semantics unchanged.
- first-level page filter date pickers may use the same fixed or portal style
  in-page menu when native browser date pickers misalign; keep the underlying
  date input value and change semantics unchanged.
- when a date picker menu would otherwise look detached from its trigger, make
  it behave like the other page filter dropdowns: match the clicked trigger
  width when usable, align the menu's left edge to the trigger, keep the top
  anchor marker aligned to the trigger center, and use a small minimum readable
  width only for unusually narrow triggers before viewport clamping.
- date menus must render the internal calendar as a stable seven-column grid;
  day cells should not inherit browser-default padding or automatic minimum
  widths that clip two-digit dates.
- do not replace ordinary form/configuration selects or date inputs with custom
  controls unless a focused requirement accepts that form interaction change.
- CR-071 accepts a focused exception for selected secondary drawer/modal
  `select` fields: they should reuse the existing `.page-filter-region select`
  enhancement so dropdowns match Task Center filters. Keep opt-in regions
  visually neutral, keep underlying select values/change behavior unchanged,
  and do not convert AI Access `模型名称`.
- CR-072 accepts a focused date exception for Monitoring task edit
  `自定义开始日期` and `自定义结束日期`: they should reuse the existing
  `.page-filter-region input[type="date"]` enhancement, render the same
  select-style date trigger, and open the local attached `.filter-date-menu`
  directly below the clicked button while preserving the original input value
  and `change` semantics.
- CR-074 standardizes refresh affordances: the first-level current-page refresh
  lives in the top bar as an icon-only SVG button with an accessible label,
  while scoped refresh actions such as schedule recomputation, log refresh,
  preview refresh, delivery-history refresh, and Run Detail refresh may remain
  only when they refresh a different local scope. All refresh icons should show
  a loading/spinning state while their associated work is pending.
- Mail template tables should stay dense: remove redundant row helper sentences
  when the template name already communicates the state, and keep update-time
  cells in the same compact wrap-safe treatment used by the AI rule table so
  timestamps do not widen the table.
- Explanatory helper copy in dense formal-console headers, labels, table cells,
  and overlay action areas should be removed when it repeats the surrounding
  control meaning or crowds the layout. Do not replace that removed copy with
  `?` helper icons or another hidden tooltip layer unless a later accepted CR
  asks for it. Keep operational state, errors, warnings, empty states, loading
  feedback, counts, login prompts, safety guardrails, and actual data visible
  when they are needed for action or recovery.

## Responsive Layout

Breakpoints:

- mobile: `< 768px`;
- tablet: `768px - 1279px`;
- desktop: `>= 1280px`.

Desktop:

- persistent left navigation;
- top-right user/logout group;
- full data tables where comparison matters;
- toolbars with search, filters, refresh, and batch actions in one row when
  space allows.

Tablet:

- collapsible side navigation;
- page headers and toolbars may wrap;
- secondary table columns may hide or move into row details;
- modals use safe margins and sticky action footers.

Mobile:

- top hamburger navigation or equivalent touch drawer;
- no hover-only page entry;
- tables convert to cards or summary rows with detail panels;
- long forms use step sections and reachable bottom actions;
- report preview and run logs may use near-fullscreen dialogs.

Responsive acceptance:

- no overlapping controls or text;
- no clipped popover menus;
- all primary flows remain reachable;
- button text fits its container;
- modal actions remain accessible on mobile.

## Table And List Rules

Desktop tables may show dense operational information, but mobile should not
inherit every column.

Task Center:

- desktop: task-grouped report/result rows first, with a secondary run-record
  table for pagination and filters;
- tablet: grouped task/report lists wrap before action buttons hide; the run
  record subview may hide secondary operational columns but must keep
  status/actions visible;
- mobile: task groups become expandable sections; run records become summary
  rows with status, task, platform, time, and actions.
- flat run rows should front-load task ID, run ID, and compact status;
- grouped run rows should hide the duplicated task ID column because the
  group header already carries task identity, then show run ID and compact
  status first;
- grouped run headers should show aggregate values as compact metric chips
  rather than one long slash-separated sentence; use labels such as `运行`,
  `采集`, `新增`, `疑似负面`, `高风险`, `待复核`, and `未评估`.
- non-zero risk/review/unevaluated group metrics may use restrained warning or
  danger emphasis, while zero values stay visually quiet.
- limited-context, deleted-task, or historical-context explanations should be a
  short note under the group metrics, not part of the metric chip text.
- the default task-group view should prioritize monitoring-task identity and
  result summary: task/law firm, platforms, keyword summary, latest status,
  collected/new counts, suspected negative, high risk, manual review,
  unevaluated, and Run Detail.
- run ID, task ID, run type, visibility, duration, and full failure reason
  belong in the `运行记录` subview and Run Detail instead of crowding the
  default task-group list.
- active runs should show compact progress states such as collecting,
  ingesting, AI evaluating, report generating, email sending, timed out, or
  complete without forcing operators to open logs.
- Task Center table status should render as a compact text-sized badge, not as
  a full-width pill or progress bar.
- Task Center status badges should show normalized short lifecycle labels only;
  long backend display/progress text belongs in Run Detail or a short helper
  line, not in the badge itself.
- Task Center first-level run status badges should use a lightweight
  state-dot label style scoped to the run table, not the global heavy status
  pill style used in other console surfaces.
- interrupted runs should use a distinct terminal state label and business-safe
  helper text. Do not display them as ordinary running rows.
- provisional counts must be visually distinguishable from final counts using
  a label, status tag, helper text, or equivalent non-color-only cue.
- recommended active polling is every 5 seconds while visible rows contain an
  active status. Polling should stop when visible rows are all terminal:
  success, failed, partial failed, timeout, cancelled, or interrupted.
- AI progress should be shown as evaluated over total while active, such as
  `250 / 271`, and as a final evaluated count when complete.
- progress refresh must not resize table rows or cards in a way that causes
  controls to jump, overlap, or become hidden on desktop, tablet, or mobile.
- stop and log actions remain reachable while progress values refresh.
- status labels should use the following Chinese terms unless a later product
  copy decision changes them: `interrupted` = "执行中断",
  `partial_failed` = "部分失败", `timeout` = "运行超时",
  `cancelled` = "已取消", `success` = "已完成".
- a recommended provisional-progress pattern is "采集中 250（临时）" or an
  equivalent spinner/tag treatment. Final counts should drop the temporary
  indicator, for example "已采集 271".
- proposed Phase 20 run detail should use a drawer or page-level detail surface
  rather than adding a large nested table directly inside the run list.
- Run Detail should be the primary place for run-scoped leads and AI
  evaluation records; a Task Center row can open the detail as a drawer or page.
- Run Detail should also be the primary place for run-scoped logs and
  run-scoped report preview. Do not add first-level row buttons that duplicate
  Run Detail's `采集日志` or `报告` sections.
- AI evaluation detail should use a compact list plus a separate detail panel
  for input/output snapshots so long prompt, request, response, and evidence
  text do not overwhelm the run list.
- Run Detail AI Evaluation filter selects should use the same enhanced
  page-filter dropdown treatment as first-level Task Center filters. Show
  `报告范围` as a dropdown only when the current run has multiple reports; use a
  read-only scope note for zero-report and single-report runs.
- debug-only fields must be visually separated from business-safe evaluation
  fields and must not appear for roles that are not allowed to inspect them.

Task-Grouped Reports:

- desktop: grouped task/report table embedded in Task Center, with report
  preview reached from Run Detail's report section;
- tablet: grouped list with report detail panel;
- mobile: task groups as expandable sections, report preview in a modal or
  separate detail view.
- task-group report and run rows should prioritize a single `详情` action;
  report preview, lead details, delivery history, resend, and downloads belong
  inside Run Detail.
- report lead details should be reached from Run Detail's `报告` and
  `AI 评估` areas, not from a first-level report-row button.
- the lead drawer should not present itself as a main lead/evaluation center;
  it is a scoped secondary surface opened from Run Detail.
- lead detail needs a visible scope label and count, such as selected report,
  selected report group, originating run, or drawer-local filters.
- lead-status filtering belongs inside the scoped lead drawer, not in the
  first-level Task Center toolbar; the first-level report toolbar should stay
  on report dimensions such as law firm, platform, date, and report range.
- do not present an unlabeled flat lead table in Task Center; if filtered
  aggregate leads are shown, label them as filtered aggregate rather than
  selected-report detail.
- empty states should say whether no report is selected, the selected report
  has no leads, or the drawer-local filters have no matches.
- email delivery history should open as scoped secondary detail from Run
  Detail and should not visually dominate the task center list, preview, or
  lead-detail hierarchy.

Mail Configuration:

- put edit configuration, send test mail, refresh/status, delivery-status
  navigation, and the real-email state in one page-level action bar.
- do not repeat edit/test buttons inside the SMTP/defaults summary when those
  actions already exist in the page header.
- show the real-email send state as one compact labeled toolbar toggle/button;
  use confirmation for enabling and concise helper text or tooltip for the
  SMTP acceptance warning.
- the SMTP/defaults section should read as a status and configuration summary,
  not as a second command center.
- explain recipient precedence near task report settings, Mail Configuration,
  and preflight output: task recipients override global defaults, global
  defaults are fallback-only, and the SMTP sender is not a recipient.

Mail Templates:

- steer new report-email templates through governed preset styles that wrap the
  system-generated report body.
- custom HTML editing must show a body-placeholder guardrail and should not
  save a new template that omits `{report_html}` or `{report_body}`.
- preview surfaces should clearly say when they use sample data rather than a
  selected report/run's generated HTML.
- delivery history should identify the send-time template/source so operators
  do not compare a historical email against a later active template by mistake.

Action menus:

- render above scroll containers with fixed or portal-style positioning;
- keep a minimum touch target;
- never depend on the table row height changing after menu open.

Filter dropdowns:

- page filter dropdown menus should stay aligned to the clicked control at
  desktop, tablet, and mobile widths;
- filter menus must not be clipped by table wrappers, drawer bodies, or the
  main content container;
- selecting a filter option must trigger the same filtering behavior as the
  original select control;
- clear/reset paths must update both the stored filter value and the visible
  filter label.
- page filter date menus follow the same alignment, clipping, selection, and
  reset rules while preserving the original date input value.
- page filter date menus should read as attached to the trigger through
  visible anchoring, but their day grid must remain readable; the seven day
  columns must not clip weekday labels or two-digit dates at desktop, tablet,
  or mobile widths. The current first-level filter pattern is a local attached
  menu: mount the active date menu inside the clicked date control wrapper,
  position it directly below that field, and match the clicked trigger width.

Scrollable drawers and modals:

- long drawer headers should remain sticky within the drawer so the close
  button stays reachable while content scrolls;
- sticky headers need a solid background and border or shadow separation so
  form content does not show through;
- scrollable drawer scrollbars should read as content scrollbars, not as
  full-height outer-frame rails: keep the outer drawer shell clipped to its
  rounded chrome, keep header controls outside the scroll container, and place
  content scrolling inside `.drawer-scroll-body` below the header;
- preserving the top-right rounded corner must not be solved by moving the
  close button toward the center; the close button stays in the top-right
  header position;
- z-index layering inside a drawer should keep the sticky header above normal
  form content but below in-drawer floating menus or dropdown overlays;
- bottom action bars should remain reachable and must not overlap the sticky
  header, form controls, or scrollbars.

## Runtime Strategy Page

Runtime Strategy is administrator-only.

Use grouped table sections:

- Crawling;
- Login;
- Scheduler;
- Retention.

Each group should use a compact operations-table layout with these columns:

- setting;
- current value;
- input control;
- valid range;
- apply scope;
- lock state.

Apply scope should be shown as short operational labels:

- immediate;
- next run;
- next session;
- scheduler reload or restart;
- cleanup job.

Locked deployment settings are read-only and show a lock indicator with a short
tooltip explaining that deployment configuration controls the value.

Do not show raw environment variable names, file paths, profile paths, command
lines, or internal lock identifiers in normal customer-facing text. Trusted
administrator diagnostics may expose limited technical detail only when needed
for operations.

## Modal Rules

Use modal dialogs consistently for:

- create;
- edit;
- test;
- login QR/status;
- delete confirmation;
- stop confirmation;
- resend confirmation.

Use large modal dialogs for:

- report preview;
- run logs;
- account login session details.

Do not mix drawer, inline form, and modal for the same operation category in
the first version.

## Normal User Task Wizard

Normal users create tasks through a simplified wizard:

1. Target
   - law firm name;
   - aliases.
2. Collection Content
   - platforms;
   - platform search terms;
   - crawl range;
   - comment collection.
3. Schedule
   - frequency;
   - send time when applicable.
4. Report
   - recipient emails.

Do not show these to normal users:

- account selection;
- proxy selection;
- AI profile selection;
- email template selection;
- browser mode;
- profile path;
- crawler command;
- debug status.

Administrators may access advanced options where needed.

## Administrator Resource Pages

Resource pages use:

- primary action button at top right;
- search and filters in the toolbar;
- table as the main content;
- create/edit in modal dialogs;
- status tags for resource state;
- clear error messages and latest check time.

Resource pages include:

- platform accounts;
- proxy resources;
- AI access;
- mail templates;
- users.

## Status Language

Normal-user language:

- Platform resource is available.
- Platform resource needs administrator attention.
- Task submitted.
- Report is generating.
- Report has been sent.

Administrator language:

- Account login state expired.
- Proxy connection failed.
- Account profile is currently in use.
- QR login timed out.
- Verification is required.

For platform-account login sessions, show the current action and next operator
step before technical detail. Repeated backend polling records, page URLs,
page titles, raw browser/profile errors, and platform navigation noise belong
in collapsed administrator diagnostics, not the default customer-facing modal
view. If explicit SMS verification is available, present send, input, submit,
inline validation, and continue-confirm as one compact operation panel. Never
present captcha, SMS, slider, or platform risk checks as bypassed or automated.

## Customer-Facing Forbidden Text

Do not show these in customer-facing UI:

- internal project names;
- command lines;
- local paths;
- profile paths;
- environment variable names;
- debug wording;
- demo wording;
- self-test wording;
- raw API keys, cookies, proxy passwords, or SMTP passwords.

## Interaction Feedback

Every action must provide feedback:

- loading state immediately after click;
- disabled button while executing;
- success toast;
- understandable error message;
- local refresh after success;
- confirmation for destructive actions.

Actions requiring feedback include:

- save task;
- run task;
- stop run;
- delete task;
- view logs;
- preview report;
- resend email;
- add account;
- start login;
- save proxy;
- test AI;
- test SMTP;
- save template;
- save runtime settings.

## Authentication And Error Pages

Login page:

- use a centered card layout with restrained product branding;
- include email and password fields;
- include a clear login button and loading state;
- show failed-login errors without revealing whether the email exists;
- do not include public self-registration in V1.

Permission denied page:

- show the message `当前角色无权访问此功能`;
- provide a return-to-overview action;
- do not reveal hidden administrator resource details.

Empty states:

- use a simple icon, short message, and one primary action when available;
- example for monitoring: `暂无监控任务`;
- example for reports: `暂无报告`;
- avoid technical explanations in normal-user empty states.

Loading states:

- use skeleton rows for initial table loading;
- use inline spinners for refresh actions;
- disable the action button while save/test/run actions are in progress;
- keep layout dimensions stable while loading.
