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
- page refresh controls should be page-specific and show what was refreshed;
- page headers should keep title, summary, primary action, and user controls in
  predictable positions.

## Menu Structure

Administrator:

- Overview
- Monitoring
- Run Center
- Report Center
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
- Run Center
- Report Center

Phase 10-18 menu behavior:

- Overview should be renamed or treated as Operations Home in user-facing
  structure;
- Resource Management and System Configuration use expanded navigation groups,
  not detached hover-only popovers;
- mobile navigation must work by tap, not hover;
- nested pages should remain reachable with clear active states and without
  clipped submenus.

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

Interaction rules:

- every save, test, run, stop, archive, restore, resend, and refresh action
  needs loading, success, and error feedback;
- destructive or history-changing actions require confirmation;
- disabled controls must explain why when the reason is business-relevant;
- more menus close on outside click, escape, successful action, and navigation
  change;
- row action menus must not be clipped by table or scroll containers.

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

Run Center:

- desktop: table with pagination and filters;
- tablet: hide secondary columns and keep status/actions visible;
- mobile: cards or summary rows with status, task, platform, time, and actions.

Report Center:

- desktop: grouped task/report table and preview area;
- tablet: grouped list with report detail panel;
- mobile: task groups as expandable sections, report preview in a modal or
  separate detail view.

Action menus:

- render above scroll containers with fixed or portal-style positioning;
- keep a minimum touch target;
- never depend on the table row height changing after menu open.

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
