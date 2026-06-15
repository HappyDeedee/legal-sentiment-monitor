# Frontend Architecture

This document is the technical reference for the Phase 10-18 console
optimization roadmap. It defines the accepted frontend stack, layout strategy,
responsive behavior, and component boundaries before UI implementation begins.

## Status

Planning accepted on 2026-06-15. Phase 10 architecture review is complete.
Phase 11A module boundary, Phase 11B base layout, Phase 11C interaction
helper/floating-menu, and Phase 11D responsive foundation batches are complete
and verified. Phase 12A navigation structure and login landing is the next
frontend batch.

Agents must use this document together with:

- `UI_UX_GUIDELINES.md`;
- `PRODUCT_REQUIREMENTS.md`;
- `CHANGE_REQUESTS.md`;
- `TASKS.md`;
- `TEST_PLAN.md`.

If frontend documents conflict, follow this priority:

1. `DECISIONS.md`;
2. this document;
3. `UI_UX_GUIDELINES.md`;
4. `PRODUCT_REQUIREMENTS.md`;
5. `TASKS.md`.

## Product Flow

The console should be rebuilt around the monitoring task loop:

```text
Operations Home -> Create / manage task -> Run Center -> Report Center -> Email delivery
```

Administrator resource management supports the loop, but it should not dominate
the normal-user entry path. The login landing page should route users to the
operations home, not a diagnostic-heavy system page.

## Accepted Technology Stack

Confirmed direction:

- keep vanilla JavaScript for this redesign round;
- use CSS custom properties as the design-token layer;
- keep the app usable without React, Vue, Angular, Tailwind, Alpine.js, or
  Petite-Vue;
- keep the no-build deployment path unless a later change request accepts a
  build step;
- optional lightweight libraries may be considered only for focused needs:
  charts, date handling, or floating menu positioning.

Optional library rules:

- a chart library may be used for the operations home only if native HTML/CSS
  would make the view fragile or hard to maintain;
- a floating-position library may be used to prevent action menus from being
  clipped by scroll containers;
- any new dependency must be recorded in `DECISIONS.md` before implementation;
- do not introduce a framework or utility CSS system for a single page.

## File And Module Strategy

Phase 10 file-structure audit:

- the current monitor console is served from `api/monitor_web/index.html`;
- `/monitor` returns that file directly;
- the file currently contains inline CSS and JavaScript and is over 4,000
  lines long;
- existing responsive behavior is concentrated around coarse `1100px` and
  `720px` media queries;
- the FastAPI app already mounts `/static` from `api/webui`, so local static
  CSS/JS assets can be served without a new build pipeline.

Decision for Phase 11:

Keep the `/monitor` entry and no-build deployment path, but do not continue
adding the redesign as one larger inline file. Phase 11 should introduce a
small local static module boundary for the design-system layer before broad UI
rewrites.

Recommended first split:

```text
api/monitor_web/index.html
api/webui/monitor/monitor.css
api/webui/monitor/monitor.js
```

The exact file names can change during implementation, but the direction is:

- CSS variables, base layout, responsive rules, and reusable component classes
  move into a local CSS file;
- JavaScript helpers for navigation, menus, modals, refresh behavior, and page
  rendering move into one or more local JS files;
- the HTML entry keeps the root shell and script/style references;
- no bundler is required.

Allowed directions:

- keep `api/monitor_web/index.html` but organize CSS variables, component
  helpers, page renderers, and route handlers clearly;
- split local CSS and JavaScript files under the existing monitor web static
  surface if that reduces risk;
- preserve the existing server route and deployment model.

Not allowed in this roadmap without a new accepted CR:

- migrating to React, Vue, Angular, Svelte, or another SPA framework;
- requiring a new Node build pipeline for the console;
- replacing the whole product shell with a marketing-style landing page.

## Phase 11 Implementation Batches

Phase 11 must not be implemented as one broad goal. Use these batches.

## Cross-Phase Impact Review

Before approving any Phase 11-18 execution goal, review Phase 10-18 as one
roadmap. The review should verify both the local batch boundary and the effect
on later phases.

Required cross-phase checks:

- Phase 11A-D create the frontend foundation for Phase 12 navigation, Phase 13
  operations home, Phase 15 run center, Phase 17 email delivery surfaces, and
  Phase 18 report grouping. A Phase 11 change must not make those later pages
  harder to implement through hidden inline coupling or inconsistent
  responsive rules.
- Phase 12 navigation and login landing must preserve Phase 11 responsive and
  floating-menu decisions, and must not break administrator/normal-user menu
  visibility.
- Phase 13 operations home depends on the task-loop product model and should
  not reintroduce diagnostic-heavy blocks that Phase 12 is moving away from.
- Phase 14 must land compatible run-field migration and backfill before Phase
  15 frontend filters, archive/restore actions, or noise filtering depend on
  `visibility` and `run_type`.
- Phase 15 API/data governance must preserve run logs, report links,
  owner/workspace scope, and existing status values before Phase 15 frontend
  refinement changes list behavior.
- Phase 16 must land email delivery logs and idempotency keys before Phase 17
  displays delivery history or changes resend behavior.
- Phase 17 must keep report generation tolerant of SMTP failure and must not
  block Phase 18 report grouping or preview switching.
- Phase 18 report grouping must preserve selected-report preview, lead detail
  switching, owner/workspace scope, and deleted-task history through
  `job_snapshot_json`.

A plan review is not complete if it only says the next phase is safe. It must
also state whether the overall phase order, granularity, verification plan,
and rollback boundaries are strong enough to reach the final console goal.

### Phase 11A - Module Boundary And CSS Tokens

Goal:

- create a safe local static boundary without changing visible UI.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js`.

Rules:

- add CSS/JS references to the HTML entry;
- load `monitor.css` before the existing inline `<style>` block so Phase 11A
  cannot override the current inline visual variables;
- load `monitor.js` after the existing inline `<script>` block;
- keep existing inline CSS and JavaScript in place;
- define tokens only: colors, typography, spacing, radius, shadows, z-index,
  status colors, and breakpoint values;
- do not migrate behavior or restyle pages in this batch.
- keep `monitor.js` as a quiet module boundary; it should not log to the
  console or execute UI behavior in Phase 11A.

Required token groups:

- neutral colors;
- primary colors;
- status colors: success, warning, danger, and info;
- navigation colors;
- font families, font sizes, font weights, and line heights;
- spacing scale using the accepted 8px base grid plus semantic aliases;
- radius scale;
- shadow scale;
- z-index scale;
- motion duration/easing tokens;
- breakpoint values for mobile and tablet;
- no legacy compatibility aliases in Phase 11A.

Token naming rules:

- use new namespaced variables such as `--color-*`, `--space-*`,
  `--font-*`, `--radius-*`, `--shadow-*`, `--z-*`, and `--transition-*`;
- do not define existing inline variable aliases such as `--bg`, `--surface`,
  `--line`, `--text`, `--muted`, `--primary`, or `--radius` in Phase 11A;
- legacy aliases can be added in Phase 11B only when the related inline style
  section is migrated and visual parity is being verified.

Rollback:

- remove the two static-file references from `api/monitor_web/index.html`;
- remove `api/webui/monitor/monitor.css` and `api/webui/monitor/monitor.js`;
- do not touch existing inline CSS/JS during rollback because Phase 11A must
  not remove or migrate it.

### Phase 11B - Base Layout And Navigation Visual Foundation

Goal:

- move base shell styling into `monitor.css` and improve desktop visual
  foundation.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js` only if a very small helper is required.

Rules:

- focus on shell, header, navigation, buttons, cards, and toolbars;
- migrate or override only these base selectors in this batch:
  `.shell`, `.shell > aside`, `.brand`, `nav`, `.nav-group`, `.nav-label`,
  `nav button`, `header`, `.user-info`, `.btn`, `.primary`, `.secondary`,
  `.ghost`, `.danger`, `.card`, `.metric-card`, `.toolbar`, and
  `.toolbar-actions`;
- do not migrate table, modal, form, report-preview, task-wizard, AI-rule,
  mail-template, or resource-specific styles in this batch unless needed to
  preserve visual parity after moving a shared selector;
- prefer moving style rules from the inline `<style>` block into
  `monitor.css`; do not duplicate divergent definitions in both places once a
  selector is migrated;
- preserve current page IDs, role visibility, and data-loading behavior;
- preserve HTML structure except for class hooks that are required to attach
  the migrated base styles;
- do not restructure navigation hierarchy yet; that belongs to Phase 12;
- verify desktop first before widening to responsive behavior.

### Phase 11C - Interaction Components And Floating Menus

Goal:

- standardize shared interaction helpers and fix clipped menus.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js`.

Rules:

- introduce a small `MonitorUI` helper boundary or equivalent plain-object API;
- centralize toast, loading, empty-state, menu-close, and floating-menu helpers
  with explicit APIs such as `showToast(message, type)`,
  `showLoading(target)`, `renderEmptyState(target, options)`,
  `closeFloatingMenus()`, and `positionFloatingMenu(triggerEl, menuEl)`;
- decide whether a shared DOM root such as `<div id="monitor_portal_root">`
  is needed before implementation; if added, it belongs at the end of
  `api/monitor_web/index.html` and must be used only for overlays/menus;
- row menus should use fixed or portal-style positioning;
- menu positioning should account for viewport edges;
- menus close on outside click, escape, page change, and successful action.
- first attempt a small local positioning helper; if a lightweight floating
  library is needed, record the dependency decision in `DECISIONS.md` before
  adding it.
- affected menu surfaces include account, proxy, AI access, AI rules, report,
  mail-template, and modal-contained row actions.

### Phase 11D - Responsive Foundation

Goal:

- make the console usable across the accepted desktop/tablet/mobile breakpoints.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js`.

Rules:

- implement mobile navigation with a touch-safe drawer or equivalent pattern;
- default mobile navigation direction is a top-left hamburger button that opens
  a left-side drawer and switches to a close state while open;
- add only the DOM hooks needed for mobile navigation, such as a hamburger
  button, drawer active state, and optional backdrop; keep page section IDs and
  data loading intact;
- tablet behavior should allow page headers and toolbars to wrap into two rows
  while keeping primary actions visible;
- make toolbars, form grids, metric grids, modals, and dense tables usable;
- mobile tables may remain scroll-safe in Phase 11D;
- page-specific card conversions should happen in Phase 12, Phase 13, Phase
  15, or later page phases when the page flow is being rewritten.

### Phase 12A - Navigation Structure And Login Landing Boundary

Goal:

- replace popover-based primary navigation with task-loop navigation groups and
  route authenticated users to the operations home.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js`.

Rules:

- replace Resource Management and System Configuration popovers with expanded
  or accordion-style navigation groups; use native `<details>/<summary>` or a
  small custom accordion only after choosing the simpler maintainable option;
- preserve `data-tab` page IDs unless a specific page rename is documented and
  all callers are updated in the same batch;
- route successful login and normal session restore to Operations Home when no
  explicit allowed destination is present;
- group authenticated user identity and logout in the desktop top-right area;
- place the mobile account area in the navigation drawer or another predictable
  touch-safe area;
- preserve administrator and normal-user menu visibility rules.

### Phase 12B - Page Entry And Role Flow Boundary

Goal:

- standardize page entry structure around the monitoring task loop.

Files:

- `api/monitor_web/index.html`;
- `api/webui/monitor/monitor.css`;
- `api/webui/monitor/monitor.js`.

Rules:

- apply a common page header pattern to Operations Home, Monitoring, Run
  Center, Report Center, account resources, proxy resources, AI access, AI
  rules, mail configuration, mail templates, runtime settings, and system
  diagnostics;
- each page header should define title, description, primary action, and
  toolbar/filter region where applicable;
- task-loop shortcuts should live on Operations Home or the relevant page
  header/toolbar, not as hidden hover-only navigation;
- do not change API contracts in this batch unless the page entry needs a
  documented field that already exists server-side;
- verify administrator and normal-user entry paths separately.

## Phase 13 Operations Home Boundaries

Phase 13 is split so data, desktop presentation, and responsive/role behavior
can be verified separately.

Phase 13A data boundary:

- use `api/routers/monitor.py` for the API route unless a small
  `api/monitoring/operations_home.py` helper is introduced to keep aggregation
  testable;
- aggregate from existing task, run, report, lead, email, and resource data;
- do not add schema only for a visual metric unless the metric is accepted as a
  data-model requirement;
- keep `/api/monitor/dashboard` compatible during migration or explicitly
  document a response version.

Phase 13B visual boundary:

- update the `dashboard`/overview section in `api/monitor_web/index.html`;
- use `monitor.css` for reusable metric and operations-home layout classes;
- avoid a chart dependency unless CSS/HTML makes the metric fragile; record any
  accepted chart dependency in `DECISIONS.md`.

Phase 13C responsive and role boundary:

- verify administrator and normal-user metric visibility separately;
- keep detailed diagnostics under System Diagnostics and show only concise
  resource health on the operations home;
- verify desktop, tablet, and mobile layouts.

## Phase 17 Email Delivery Boundaries

Phase 17A logic boundary:

- implement idempotent send-window logic in `api/monitoring/mailer.py`,
  `api/monitoring/reporting.py`, scheduler/report generation call sites, or a
  small email-delivery helper module;
- write delivery attempts to `email_delivery_logs`;
- keep latest report email fields readable until the report center consumes
  delivery history;
- do not block report generation when SMTP fails.

Phase 17B frontend boundary:

- update report-center UI in `api/monitor_web/index.html`;
- expose latest delivery state and history through monitor API routes;
- preserve report preview, lead switching, downloads, and owner/workspace
  filtering.

## Phase 18 Report Grouping Boundaries

Phase 18A data boundary:

- add and backfill `reports.job_snapshot_json` in the database layer;
- update report generation in `api/monitoring/reporting.py` to persist
  snapshots for new reports;
- follow the JSON shape in `DATA_MODEL.md` and the migration rules in
  `SCHEMA_MIGRATION.md`.

Phase 18B frontend boundary:

- update the report list/rendering path in `api/monitor_web/index.html`;
- group by active task when `job_id` resolves and by snapshot when it does
  not;
- handle empty snapshots with a limited-context historical fallback;
- preserve selected report preview and lead detail switching.

## Regression Protection

Phase 11 batches must protect these core flows:

- login and logout;
- session restore;
- page navigation and tab switching;
- monitoring task list loading;
- normal-user task wizard entry;
- run center list and log modal;
- report list, preview, lead switching, and downloads;
- account resource list and QR login entry;
- proxy, AI, mail configuration, and mail-template pages;
- modal open/close behavior;
- toast feedback;
- role-based menu visibility.

Phase 11 may improve but must not break:

- floating row menus;
- table scrolling;
- report preview modal;
- runtime settings grouped tables;
- server-side QR login status dialog.

Phase 11D can defer full mobile card conversion for:

- AI rule editor;
- mail-template editor and preview;
- system diagnostics detail views;
- other dense administrator-only configuration surfaces.

Each batch should run:

- documentation consistency check;
- core login/navigation smoke path;
- desktop 1440px visual check;
- any batch-specific interaction or responsive checks from `TEST_PLAN.md`.

## Layout System

Breakpoints:

```text
mobile: < 768px
tablet: 768px - 1279px
desktop: >= 1280px
```

Desktop:

- persistent left navigation;
- top bar with global context and user controls;
- user identity and logout grouped at the top right;
- page content uses stable max-width and dense enterprise spacing;
- resource management and system configuration appear as expanded navigation
  groups, not hover-only popovers.

Tablet:

- collapsible side navigation;
- page header and toolbar may wrap into two rows;
- tables hide secondary columns or move details into row expansion;
- modals use wider safe margins and sticky action footers.

Mobile:

- top navigation with hamburger menu and drawer;
- no hover-only navigation;
- no nested popover menus for primary page entry;
- tables convert to structured cards or summary rows with detail panels;
- long forms use step sections and sticky bottom actions;
- report preview and run logs can use near-fullscreen dialogs.

## Navigation

Primary navigation must make the task loop obvious:

1. Operations Home;
2. Monitoring Tasks;
3. Run Center;
4. Report Center;
5. Resource Management;
6. System Configuration.

Resource Management and System Configuration should be expandable groups in the
navigation tree. They should not rely on detached popover menus because those
are hard to use on touch devices and are prone to clipping.

## Component Patterns

Buttons:

- primary action per page;
- secondary actions in toolbar or row action menu;
- destructive actions require confirmation;
- action labels should use business language.

Toolbars:

- search, filters, refresh, and batch actions stay in the same visual row on
  desktop;
- tablet and mobile may wrap filters into a compact filter panel.

Tables:

- desktop uses full data tables where comparison matters;
- tablet hides low-priority columns and keeps row actions accessible;
- mobile uses cards or list rows with stable information hierarchy;
- horizontal scrolling is allowed only for genuinely dense operational tables
  and should not hide row actions.

Floating menus:

- row "more" menus must render above scroll containers;
- positioning should use fixed or portal-style placement;
- menus must close on outside click, escape, route change, and successful
  action;
- menus must not be clipped by table, card, modal, or page containers.

Modals:

- use modal dialogs for create, edit, test, confirm, login, report preview, and
  run logs;
- mobile modals may become near-fullscreen;
- action footers should remain reachable on long content.

## Operations Home

The operations home should be visual and task-oriented:

- task health and recent collection activity;
- report generation and email delivery status;
- suspected negative lead trends;
- account availability summary;
- drilldown links into Monitoring, Run Center, Report Center, and Resource
  Management.

Avoid long diagnostic blocks on the home page. System diagnostics belong under
administrator system configuration unless summarized as a small health signal.

## State Refresh

The old global refresh concept should be replaced with explicit refresh
behavior:

- page-level refresh updates the current page data;
- active run rows may auto-poll while running;
- operations-home metrics should show last updated time;
- refresh labels should say what is being refreshed.

## Responsive Verification

Frontend implementation must be checked at minimum in these viewport classes:

- desktop: 1440px wide or wider;
- tablet: around 1024px wide;
- mobile: around 390px wide.

Acceptance should cover:

- no overlapping text or controls;
- no clipped row menus;
- navigation usable without hover;
- modals usable on mobile;
- report preview and run logs readable;
- task creation, run inspection, report grouping, and email delivery status
  paths remain reachable.
