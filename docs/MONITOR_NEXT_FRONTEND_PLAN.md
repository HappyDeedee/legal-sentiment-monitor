# Monitor Next Frontend Plan

This document is the planning source for CR-078. It records a future
`/monitor-next` evaluation lane and does not change the current `/monitor`
console.

## Status

Status: Needs Confirmation.

CR-078 is not Phase 21. Phase 21 remains the active frontend visual refinement
lane for the current `/monitor` console, using the existing Vanilla
JavaScript and no-build baseline. This document must not be used to introduce a
framework, build step, dependency, route, API change, or page migration until a
later accepted implementation CR confirms the decision.

## Goal

Evaluate and plan a gradual future frontend rebuild that can coexist with the
current console and eventually replace it only after equivalence, permissions,
responsive behavior, tests, and rollback are proven.

Default future direction:

```text
/monitor      -> current production console
/monitor-next -> future independently mounted frontend candidate
```

## Hard Boundaries

- Do not replace `/monitor` during CR-078 planning.
- Do not create a frontend project or Node build pipeline during CR-078
  planning.
- Do not select Vue, React, a component library, Tailwind, or a build process
  as final until a later accepted decision.
- Do not change existing `/api/auth/...` or `/api/monitor/...` contracts.
- Do not call `/api/crawler/...`, `/api/data/...`, old websocket endpoints, or
  raw MediaCrawler control surfaces from the new frontend.
- Do not restore separate top-level Run Center or Report Center pages.
- Do not change Task Center, Run Detail, drawers, modals, enhanced selects,
  local date menus, close behavior, scroll ownership, routing, owner scope, or
  report scope for visual neatness.
- If a page migration needs backend API changes, record a separate API CR.

## Technology Evaluation

Before implementation, compare at minimum:

- Vue 3 + TypeScript + Vite;
- React + TypeScript + Vite;
- Naive UI, Arco Design, Element Plus, Ant Design, Radix, or an equivalent
  headless component approach.

The selection note must explain fit for:

- Chinese ToB management console workflows;
- tables, forms, drawers, modals, dates, dropdowns, menus, and permission
  navigation;
- responsive behavior at `1440x900`, `1024x768`, and `390x844`;
- type checking and test coverage;
- packaging and deployment complexity;
- dependency weight and long-term maintainability.

## Architecture Requirements

Future implementation must define these layers before page migration starts:

- app entry, routing, permission guards, and layout shell;
- page routes that assemble feature modules without large inline business
  logic;
- feature modules for auth, operations home, monitoring tasks, Task Center,
  Run Detail, resource pages, mail, runtime strategy, and diagnostics;
- common components for status labels, metrics, empty/error/loading states,
  dialogs, drawers, and action controls;
- a unified API client for `/api/auth/...` and `/api/monitor/...`;
- role, permission, API response, and view-model types;
- local state versus shared session/permission state boundaries;
- design tokens for color, typography, spacing, radius, shadow, z-index,
  status colors, and breakpoints;
- tests for API client, routing/permissions, components, pages, and browser
  smoke/E2E paths.

## Replacement Gate

The future frontend may propose replacing `/monitor` only after all conditions
below are satisfied:

- all currently rendered formal console pages are covered;
- all user-visible actions have equivalent behavior or a separate accepted CR;
- administrator and normal-user permission behavior is equivalent;
- Task Center remains the single top-level task/result entry;
- Run Detail keeps the six sections and scoped report/email/AI behavior;
- enhanced dropdowns, date pickers, drawers, modals, floating menus, closing
  behavior, and scroll ownership have equivalent behavior;
- desktop, tablet, and mobile acceptance passes;
- build/type/test/browser checks pass;
- current monitor API compatibility is preserved;
- a rollback path to the current `/monitor` or a deploy rollback is recorded.

## Old Frontend Removal Gate

Deleting the old `/monitor` implementation is a later task and is allowed only
after:

- `/monitor-next` has already replaced `/monitor`;
- at least one complete business loop is verified:
  login -> create or view task -> run or inspect run -> Run Detail -> report
  -> email delivery;
- administrator and normal-user paths both pass;
- no P0/P1 frontend regression remains;
- the rollback window is ended or explicitly waived by the user;
- documentation marks the old frontend as historical;
- deletion does not affect backend APIs, task runs, report downloads, account
  login, or static deployment.

## Documentation Outputs

Before implementation starts, the frontend migration lane must produce:

- technology selection note;
- directory and layering plan;
- route and permission matrix;
- API client boundary;
- component and state boundary plan;
- design-token plan;
- responsive strategy;
- replacement gate;
- rollback plan;
- test plan.
