# Formal Console UI Refinement Execution Plan

Status: Accepted Phase 21 execution plan. Phase 21 implementation code has not
started yet. Use this document as the required implementation reference before
editing the formal console frontend.

## Purpose

This document turns the latest formal-console UI/UX review into the Phase 21
fine-grained execution plan. The target is the current formal `/monitor`
frontend, not the static prototype at `design-prototypes/console-review/`.

The work is a positive refinement pass: improve visual quality, commercial
polish, information hierarchy, interaction efficiency, responsive behavior,
and state feedback while preserving every existing business flow.

## Baseline

Formal frontend baseline:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`
- `api/webui/monitor/monitor.js`

Reference prototype:

- `design-prototypes/console-review/`

The prototype may be used only as visual reference. It is not a functional
baseline because it does not preserve all formal-console pages, buttons,
menus, drawers, filters, and administrator workflows.

## Hard Boundaries

Allowed:

- frontend-only UI and interaction refinements in the formal monitor console;
- CSS token, spacing, density, state-label, table, drawer, modal, and
  responsive refinements;
- copy refinements that make existing actions clearer without changing
  product meaning;
- page-level loading, empty, error, success, and disabled-state polish using
  existing data and APIs.

Not allowed:

- no backend API changes;
- no database schema changes;
- no permission or role-model changes;
- no crawler, AI-provider, SMTP, scheduler, or deployment behavior changes;
- no new frontend framework, build step, Tailwind, React, Vue, Alpine, or
  Petite-Vue;
- no merging Resource Management or System Configuration pages;
- no replacing floating menus with side business drawers;
- no deleting buttons, filters, batch actions, row actions, drawers, modals,
  download actions, or confirmation flows;
- no new dashboard metrics that require new backend fields.
- no implementing the currently unrendered `Users And Permissions` page in
  this phase. That surface is named in role documentation as a V1 permission
  area, but it is not part of the current formal-console rendered page set; if
  the user wants it implemented, record a separate new-capability CR.

## Target Experience

The console should feel like a quiet, professional law-firm public-opinion
operations cockpit:

- data and exceptions first;
- low visual noise;
- strong but restrained hierarchy;
- clear first action on every page;
- compact tables where comparison matters;
- stable modal/drawer behavior;
- business-safe status language;
- mobile access to status, navigation, reports, logs, and urgent actions.

The UI must not feel like:

- a generic admin template;
- a marketing landing page;
- a simplified demo;
- a static prototype that hides real workflows;
- a dashboard made of decorative cards and fake charts.

## Design Confirmation Model

The user does not need to approve every individual color value, spacing value,
or layout adjustment before implementation. Confirmation should happen at the
design-system and workflow level, then the implementation batch should apply
that direction consistently and verify it with screenshots and interaction
checks.

Confirm before implementation:

- the overall visual direction, such as clean neutral enterprise console,
  restrained primary accent, and low-noise status colors;
- the color-token family, including neutral base, primary accent, and semantic
  status colors;
- page density direction, such as compact operational tables and reduced
  decorative card surfaces;
- navigation hierarchy rules for first-level and second-level pages;
- Operations Home priority order and whether the `01-05` shortcut block should
  be visually reduced;
- whether any page, workflow, drawer, modal, field group, or action would be
  moved, renamed, hidden, or removed;
- whether a visual idea requires backend data, a new API field, a new
  permission rule, or a product decision.

No per-item confirmation is required for:

- individual border, shadow, hover, focus, disabled, or skeleton values that
  follow the confirmed token system;
- minor spacing, row height, table density, card padding, and toolbar wrapping
  refinements;
- copy edits that clarify an existing action without changing product meaning;
- responsive adjustments that keep the same fields and actions reachable;
- internal CSS class organization that does not change user-visible behavior.

Always require a separate user confirmation or CR before:

- removing or merging pages;
- deleting buttons, filters, batch actions, row menus, drawers, modals, or
  fields;
- changing role visibility;
- changing account login behavior, QR/Cookie flow, delivery behavior,
  report-download behavior, run lifecycle behavior, or runtime setting meaning;
- adding metrics, charts, or visualizations that need new backend data;
- changing customer-facing product terminology in a way that affects legal,
  permission, deployment, account, security, email, or report semantics.

## Implementation Sequencing

Implement Phase 21 as small frontend batches, not as one broad visual rewrite:

- Workstreams A-O may be implemented and smoke-checked independently.
- Each workstream must preserve its listed fields, buttons, overlays, menus,
  role boundaries, and visible states before moving to the next workstream.
- Phase 21P is the final cross-page verification gate after A-O are complete.
- If Phase 21P finds a regression, rework the smallest affected workstream
  rather than rewriting unrelated pages.
- Do not mark any Phase 21 task complete until the corresponding code change,
  browser check, and documentation update agree.

## Global Refinement Rules

### Visual System

- Recalibrate colors to a clean neutral base plus one restrained primary
  accent and semantic status colors.
- Reduce default blue tint and repeated white-card surfaces.
- Keep radii consistent and modest.
- Use shadows only where elevation communicates an overlay or active surface.
- Keep contrast high enough for labels, buttons, status tags, filters, and
  disabled states.
- Make status labels consistent across pages:
  running, success, failed, timeout, interrupted, archived, pending review,
  manual review, email failed, resource limited.

### Density And Layout

- Use cards for summaries and repeated items only when they help scanning.
- Prefer compact tables, grouped lists, divider bands, and stable toolbars for
  operational pages.
- Do not turn dense administrator pages into large decorative cards.
- Keep page actions predictable:
  primary action in page header; filters in toolbar; row actions in row or
  floating menu; destructive actions confirmed.
- Keep button labels from wrapping at desktop, tablet, and mobile widths.
- Every card, grid, and status module must keep readable text widths. Text must
  not collapse into one-character vertical columns, especially in dashboard
  loop/status cards, metric cards, resource cards, run cards, and report cards.
- Cards or modules with four or more inner columns must define minimum column
  widths and a fallback layout. At `1440x900`, `1024x768`, and `390x844`, they
  must wrap to fewer columns, stack, or collapse into compact rows before text
  becomes unreadable.
- Long law-firm names, platform names, account labels, failure reasons, and
  status text must use sane wrapping rules such as stable `minmax` tracks,
  minimum inline sizes, `overflow-wrap` for long tokens, and line clamp or
  tooltip treatment where a compact card cannot safely show the full text.

### Interaction Feedback

- Every save, test, run, stop, archive, restore, resend, refresh, and login
  action must show immediate local feedback.
- Use button-level loading for action buttons and page-shaped skeletons for
  list/table refresh.
- Loading must preserve layout size where possible.
- Empty states must name the page-specific next action.
- Error states must say what failed and where to recover.
- Disabled states must explain business-relevant reasons.

### Overlay Rules

- Existing drawers, modals, and floating menus stay in the same workflow
  category.
- Long drawers must keep close controls reachable, following CR-038 where
  applicable.
- Standard close behavior:
  visible close button, backdrop close where already supported, Escape close,
  and automatic close on page switch.
- More menus must remain floating or portal-style and must not be clipped by
  table, card, drawer, or page containers.

### Responsive Rules

Verify at:

- desktop: `1440x900`;
- tablet: `1024x768`;
- mobile: `390x844`.

Mobile must preserve:

- navigation open, close, and page selection;
- current status overview;
- task creation entry;
- run status and log entry;
- report preview and delivery status;
- account login maintenance visibility for administrators;
- reachable modal close and bottom action controls.

Layout resilience must be checked at every accepted viewport:

- no page or card may show text as one Chinese character per line because a
  column became too narrow;
- dashboard closed-loop, trajectory, shortcut, metric, and resource-health
  sections must degrade before they squeeze content;
- dense Run Center and Report Center cards/tables must keep status, primary
  action, and secondary action readable and reachable;
- loading, empty, and error states must preserve the same safe width behavior
  as loaded content.

Concrete pass/fail examples:

- Pass: on mobile `390x844`, a long law-firm name such as
  `北京市海淀区恒泰律师事务所` wraps across readable multi-character lines inside
  an Operations Home card, while the card's primary action remains reachable.
- Pass: a desktop closed-loop track with task, run, report, and email steps
  wraps or switches to compact rows before labels become narrow columns.
- Fail: any card renders Chinese labels as a vertical sequence like
  `任 / 务 / 配 / 置`, overlaps adjacent metrics, clips a required button, or
  requires horizontal page scrolling at `1440x900`, `1024x768`, or `390x844`.

## Implementation Workstreams

### A. Global Shell And Design Tokens

Files:

- `api/webui/monitor/monitor.css`
- `api/monitor_web/index.html` only if class hooks are required
- `api/webui/monitor/monitor.js` only if shared helper behavior is required

Do:

- refine neutral, primary, status, border, background, and text tokens;
- audit button, input, select, badge, toast, empty-state, error, skeleton, and
  modal base styles;
- make top header, current user area, global refresh, and logout visually
  calmer;
- strengthen active, hover, focus, and disabled states;
- keep icon and text alignment stable in navigation and toolbar buttons.

Do not:

- rename page IDs or `data-tab` values;
- change role visibility rules;
- change API calls or page loading order.

Acceptance:

- all 12 logged-in formal pages plus login remain reachable;
- no button text becomes unreadable;
- no browser console errors;
- no horizontal overflow at 1440, 1024, or 390 widths.

### B. Navigation Hierarchy

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`
- `api/webui/monitor/monitor.js`

Do:

- visually distinguish top-level pages from `Resource Management` and
  `System Configuration` subpages;
- keep `dashboard`, `jobs`, `runs`, and `reports` as the main task loop;
- keep `accounts`, `proxies`, and `ai` under resources;
- keep `ai_rules`, `email`, `email_templates`, `runtime`, and `doctor` under
  system configuration;
- improve expanded/collapsed group affordances and active subpage cues;
- verify mobile navigation opens by tap, closes by backdrop/Escape/page
  selection, and keeps active state clear.

Do not:

- merge navigation groups;
- hide administrator pages from administrators;
- expose administrator pages to normal users.

Acceptance:

- administrators can reach every existing administrator page;
- normal users see only allowed pages;
- first-level and second-level navigation are visually distinguishable without
  relying only on indentation.

### C. Operations Home

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Do:

- remove the remaining onboarding feeling from the `01-05` quick-entry block;
- preserve all five shortcuts but reduce their first-screen footprint;
- place operational data before guidance:
  task health, run activity, report output, email delivery, resource impact;
- make the primary next action match the most urgent state shown on the page;
- use the task loop as the main structure:
  task -> run -> report -> email -> issue handling;
- keep administrator resource-health drilldowns concise and route detailed
  diagnosis to System Diagnostics.

Do not:

- introduce fake charts or metrics not backed by existing dashboard data;
- put long diagnostics back on the home page;
- remove normal-user business-safe resource wording.

Acceptance:

- desktop first screen shows data and urgent actions before shortcuts;
- mobile first screen shows key status and one clear next action without a
  long visual chart dominating the page;
- closed-loop, shortcut, metric, and resource-health cards remain readable at
  `1440x900`, `1024x768`, and `390x844`; no label may collapse into
  one-character vertical wrapping;
- administrator and normal-user views remain role-safe.

### D. Monitoring Tasks And Task Drawer

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- `New Task`, schedule refresh, Run Center shortcut, search, platform filter,
  status filter, clear filters;
- row `Run`, `Stop`, and `More`;
- row menu: edit task, pause/resume, delete task;
- task drawer fields for target, aliases, platform search terms, platforms,
  max items, start page, max pages, first/second-level comments, exclude words,
  administrator account/proxy binding, target type, output mode, login mode,
  crawl range, frequency, send time, custom dates, custom cron, enabled flag,
  AI access, evaluation-rule hint, recipients, and email template;
- drawer actions: save task, fill sample, clear, close.

Do:

- improve drawer section hierarchy and scan order;
- make administrator-only advanced settings visually separate but available;
- improve long-form spacing, helper text, and sticky action behavior;
- make mobile drawer sections easier to scan without hiding fields.

Do not:

- simplify the task drawer into the static prototype's reduced task form;
- remove sample-fill, clear, or administrator advanced fields.

Acceptance:

- existing task creation and editing flows still expose every current field;
- normal-user advanced fields remain hidden;
- administrators can still bind accounts, proxies, AI, and templates.

### E. Platform Accounts

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`
- `api/webui/monitor/monitor.js` if shared login feedback needs refinement

Must preserve:

- top actions: add account, refresh account, return to tasks;
- filters: search, platform, availability, login type, attention-only,
  clear filters;
- batch actions: check, disable, enable, delete;
- row actions: detail, more;
- row menu: check login status, relogin, enable/disable, delete;
- account dialog:
  basic profile, platform, status, bound proxy, login source, notes, exception
  summary, advanced exception record;
- login maintenance:
  login-method options, QR login area, local-window fallback where allowed,
  Cookie login area, capability hints, status badges, login result area;
- login history;
- actions: save account and delete account.

Do:

- make the account dialog read as a high-trust operational maintenance surface,
  not a generic resource form;
- strengthen the four-part flow:
  basic profile, login maintenance, login records, final account settings;
- make QR login progress and Cookie save feedback easy to understand;
- preserve external account identity and avatar-related display when available;
- make batch actions visually secondary until rows are selected.

Do not:

- replace account dialog with generic config modal;
- remove QR login, Cookie login, local fallback controls, login records,
  filters, batch actions, row menu, or external identity fields.

Acceptance:

- administrator can open add/edit account, start QR login, use Cookie save,
  view login records, run row-menu actions, and perform batch actions;
- every login status has a visible and understandable state;
- mobile account dialog remains closable and action buttons remain reachable.

### F. Proxy Resources

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- add proxy, refresh proxy, view accounts, search, status filter, clear
  filters, refresh;
- row edit/delete;
- drawer fields: name, provider, status, proxy URL, max concurrency, notes,
  error message;
- actions: clear, save proxy, close.

Do:

- improve list density and masked-secret readability;
- make proxy health and latest error easier to scan;
- keep destructive delete clearly separated.

Acceptance:

- proxy create/edit/delete still works through the existing UI;
- masked proxy values remain masked;
- status and error fields are readable on mobile.

### G. AI Access

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- add AI access, refresh, view evaluation rules, search, protocol filter,
  test-status filter, clear filters, refresh;
- row edit, connection test, set default, delete;
- connection-test modal with profile card, model, protocol, test message,
  console, start test, close;
- AI profile drawer fields:
  name, protocol, model name, model selector, Base URL, API Key, get model
  list, advanced temperature, set default, clear, save, close.

Do:

- clarify the difference between connection testing and evaluation rules;
- make model-list loading and test result feedback more precise;
- tighten the resource table and reduce generic card feel.

Acceptance:

- connection test still opens independently;
- model list fetch still has button-level loading and fallback text;
- default switching and delete remain confirmed or clearly feedback-driven.

### H. AI Evaluation Rules

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- add rule, refresh rules, view AI access;
- row detail and more;
- row menu: test rule, set default, delete;
- rule modal:
  basic information, rule configuration sections, prompt preview, fixed output
  fields, test sample, test result;
- actions: test evaluation rule, restore default, save rule, close.

Do:

- make the large rule editor more modular and easier to scan;
- keep prompt preview readable without overwhelming the form;
- make sample test result and loading state clearer.

Do not:

- merge AI rules into AI access;
- hide or remove rule sections.

Acceptance:

- a reviewer can understand role positioning, relevance, suspected negative,
  risk level, evidence extraction, and suggested action sections separately;
- row more menu remains unclipped.

### I. Mail Configuration

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- edit mail config, send test mail, refresh config, view delivery status;
- edit/test functionality, while CR-049 may move duplicate inner entries into
  the page-level action bar;
- mail config modal fields:
  SMTP host, port, encryption, sender, username, password, default recipients,
  subject template;
- actions: cancel, save, close;
- mail test modal with console, start test, close.

Do:

- apply CR-049 by consolidating edit configuration, send test mail,
  refresh/status, delivery-status navigation, and the real-email state into
  one page-level action bar;
- remove or demote duplicated edit/test controls from the SMTP/defaults
  summary when the same actions are already present in the page header;
- render the real-email state as a compact labeled toolbar control with
  concise helper text rather than a full-width normal-state panel;
- make sender versus recipients clearer;
- explain default recipients as fallback only without changing delivery logic;
- make password mask and test status easier to read;
- align with CR-036 safety wording when that work is implemented later.

Acceptance:

- SMTP password remains masked;
- testing and saving have visible loading/success/failure states;
- SMTP/defaults summary does not duplicate page-header edit/test actions;
- the real-email switch state is visible, compact, and intentional;
- email delivery shortcut still routes to reports.

### J. Mail Templates

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- add template, refresh template, view mail config, search, status filter,
  clear filters, refresh;
- row edit, set current where available, delete;
- template drawer:
  name, subject template, HTML template, variable hints, set current, iframe
  preview, save template, refresh preview, clear, close.

Do:

- make variable hints easier to use;
- keep iframe preview visually stable;
- clarify that template-editor preview uses sample data;
- prepare visual room for future CR-039 preset styles without implementing
  template provenance in this UI-only pass.

Do not:

- remove HTML editor or iframe preview until CR-039 implementation explicitly
  changes the product model.

Acceptance:

- templates remain editable and previewable;
- active/current state remains visible;
- preview refresh has local feedback.

### K. Runtime Strategy

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- refresh strategy, save strategy, view system diagnostics;
- grouped table structure;
- current value, input, valid range, apply scope, lock state.

Do:

- improve grouped-table scanning;
- make locked settings and apply scope visually consistent;
- make `Save Strategy` look like a high-risk configuration action.

Do not:

- convert the runtime strategy page into unrelated cards;
- hide range, scope, or lock information.

Acceptance:

- administrators can still inspect and edit settings in grouped tables;
- locked values are visibly read-only and explain why.

### L. Run Center

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`
- `api/webui/monitor/monitor.js` only if polling or shared feedback UI changes
  are needed without API changes

Must preserve:

- new task, refresh runs, view reports;
- filters:
  task/law firm, status, platform, run type, visibility, start date, end date,
  page size, filter, clear, refresh;
- pagination;
- row actions: view logs, stop, archive, restore;
- run log drawer with title, metadata, refresh, copy, download, close.

Do:

- make filters easier to scan and collapse/wrap cleanly;
- make status, failure reason, and action columns easier to compare;
- keep stop/log actions stable during refresh;
- keep Run Center / Run Detail as the primary operational entry for
  run-scoped leads and AI evaluation records when Phase 20 is implemented;
- align visual language with Phase 19 future progress states without adding
  new progress data in this pass.

Do not:

- add real-time progress fields that require Phase 19 backend work;
- remove pagination or archive/restore governance controls.

Acceptance:

- all filters still work;
- pagination remains reachable;
- log drawer opens, refreshes, copies, downloads, and closes at all viewport
  sizes.

### M. Report Center

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- new task, refresh report, view run center;
- refresh report email status and refresh history;
- filters:
  law firm, platform, risk, start date, end date, display range, filter;
- grouped report list;
- row preview and more;
- report more menu:
  view delivery history, resend email, download HTML, download Excel, download
  Markdown;
- delivery history area;
- lead detail area;
- explicit report/group "view leads" entry when CR-048 is implemented;
- report preview drawer with source link/cover hint, mail-title notice, iframe,
  and standard close behavior.

Do:

- make the page read as report archive plus delivery history;
- make selected report, lead detail, and delivery history relationship clear;
- show lead-detail scope, count, and filters so the area cannot be mistaken for
  an unlabeled global lead list;
- present "view leads" as a report-scoped shortcut, not as the main
  run/evaluation workbench;
- keep delivery history as scoped secondary detail opened from a report
  row/status action instead of a dominant default panel;
- make download actions visible but not dominant;
- make resend feel like an external-impact action with confirmation and clear
  result.

Do not:

- hide downloads inside inaccessible UI;
- make preview the only way to inspect leads;
- present Report Center as a global lead workbench unless a separate future CR
  explicitly adds that capability;
- remove delivery history.

Acceptance:

- selecting a report or choosing "view leads" updates preview context or lead
  detail with an explicit scope label;
- delivery status button loads and scrolls or reveals history;
- resend confirmation and result feedback remain clear.

### N. System Diagnostics

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- rerun diagnosis, run system diagnosis, handle account resources;
- diagnostic summary;
- system diagnosis result;
- next steps;
- system runtime state;
- scheduler state;
- platform state;
- generated readiness/action cards.

Do:

- reduce long explanation blocks into summary, impact, and next action;
- keep administrator-safe technical detail when needed;
- make issue severity and routing clearer.

Do not:

- turn diagnostics into a static description page;
- remove action cards or diagnosis-trigger feedback.

Acceptance:

- diagnosis actions still produce loading and result feedback;
- account/proxy/platform issues route to the right resource page;
- customer-facing wording avoids raw secrets and local paths.

### O. Login Page

Files:

- `api/monitor_web/index.html`
- `api/webui/monitor/monitor.css`

Must preserve:

- email field;
- password field;
- login button;
- login error feedback;
- existing session logic.

Do:

- improve trust, focus, loading, and error readability;
- keep the page restrained and product-focused.

Do not:

- add public registration;
- add marketing hero content;
- change authentication behavior.

Acceptance:

- failed login shows customer-safe error;
- login button shows loading while submitting;
- successful login lands on the operations home.

## Explicit Non-Adoption From Static Prototype

Do not adopt the following prototype simplifications:

- reduced task form;
- generic resource configuration modal;
- missing AI Evaluation Rules page;
- missing Mail Templates page;
- missing report download actions;
- missing account QR/Cookie/login-history flow;
- missing account batch management;
- missing run pagination and full filter set;
- inline-only row actions replacing formal floating menus;
- demo-only buttons such as `simulate error state` in production UI;
- visible words such as `prototype`, `mock`, or `static data`.

## Verification Plan

### Static Checks

- `node --check api/webui/monitor/monitor.js`
- inline script parse check for `api/monitor_web/index.html`
- `uv run python scripts/check_docs.py`
- targeted frontend tests in `tests/test_monitoring_mvp.py` for formal console
  pages and CR-033 regression coverage

### Browser Checks

Use the running formal `/monitor` page in a server-like local service.

Desktop `1440x900`:

- login, logout, session restore;
- all administrator pages;
- all normal-user pages;
- navigation group expand/collapse;
- every row more menu;
- task drawer;
- account dialog with QR/Cookie/login history;
- AI test modal;
- AI rule modal;
- mail config/test modal;
- mail-template drawer;
- run log drawer;
- report preview drawer;
- report more menu;
- no console errors;
- no horizontal page overflow.

Tablet `1024x768`:

- mobile/tablet navigation open, select nested page, close;
- toolbars wrap without hidden primary actions;
- drawers and modals fit within safe margins;
- floating menus not clipped.

Mobile `390x844`:

- first screen of Operations Home shows status and urgent action;
- navigation can reach Monitoring, Run Center, Report Center, and allowed
  administrator pages;
- task drawer can scroll and close;
- account login dialog can show QR/Cookie state and close;
- run log and report preview are readable and closable;
- no horizontal overflow or overlapping text.

### Role Checks

Administrator:

- sees resource management and system configuration;
- can reach all preserved administrator pages and secondary surfaces.

Normal user:

- sees only operations home, monitoring tasks, run center, and report center;
- does not see account/proxy/AI/mail/runtime/diagnostics administrator
  controls;
- task creation stays simplified and does not expose administrator advanced
  options.

### Regression Checklist

The implementation is not acceptable if any of these regress:

- fewer pages are reachable;
- any existing button disappears without an accepted CR;
- any existing drawer/modal/menu disappears or changes workflow category;
- QR login, Cookie login, or login history is removed;
- task drawer loses fields;
- report downloads disappear;
- run logs lose refresh/copy/download;
- row more menus become clipped;
- mobile navigation requires hover;
- console has browser errors;
- page has horizontal overflow at accepted viewports.
- any card, closed-loop track, metric group, report/run summary, or resource
  summary squeezes text into one-character vertical columns, overlaps adjacent
  content, or hides a primary action.

## Acceptance Standard

The work is accepted only when:

- every preserved formal-console page and action still exists;
- visual hierarchy is clearer than CR-033 baseline;
- Operations Home feels like a daily operations cockpit, not onboarding;
- Platform Accounts remains a complete account-maintenance workflow;
- Run Center and Report Center are easier to scan under real operational
  density;
- secondary drawers and menus remain usable at desktop, tablet, and mobile
  sizes;
- screenshots at `1440x900`, `1024x768`, and `390x844` prove that dashboard
  cards, dense operational lists, and secondary surfaces keep readable line
  lengths without text collapse, overlap, unreachable buttons, or horizontal
  overflow;
- all verification checks are recorded in `TEST_RESULTS.md`;
- `TASKS.md`, `CURRENT_STATE.md`, `TRACEABILITY.md`, and `TEST_PLAN.md` agree
  with the completed implementation state.
