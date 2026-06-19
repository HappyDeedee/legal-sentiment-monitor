# Test Results

This file records verification outcomes. Add new entries at the top.

How to read this file:

- entries are reverse chronological, newest first;
- use the topmost relevant entry for current status;
- older entries are historical snapshots and may mention states that were later
  superseded by newer entries above them;
- use `docs/CURRENT_STATE.md`, `docs/CHANGE_REQUESTS.md`, and
`docs/TRACEABILITY.md` for final current-state decisions.

## 2026-06-19 - CR-081 Atomic Goal Execution Governance Documentation Gate

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added `docs/GOAL_EXECUTION_GUIDELINES.md` as the source for goal packet
  structure, atomicity rules, current execution lanes, test iteration loop,
  acceptance standards, and stop conditions.
- Confirmed CR-075 owns MECE open-todo lane separation while CR-081 owns how
  those lanes become executable atomic goals.
- Synchronized `CHANGE_REQUESTS.md`, `TASKS.md`, `CURRENT_STATE.md`,
  `AGENT_WORKFLOW.md`, `DOCUMENTATION_CHECKS.md`, `TEST_PLAN.md`,
  `TRACEABILITY.md`, and `DECISIONS.md`.
- Confirmed the current execution order remains Phase 21 merge, Phase 5.1P
  read-only preflight, Phase 5.1A-D implementation, Phase 5.1 acceptance, then
  CR-070 / Phase 5.2 after CR-047 provider/effective snapshot verification.
- Added a Phase 5.1 acceptance-gate task block and clarified that Phase 5.1E
  optional CloakBrowser-style provider evaluation is not part of the current
  Phase 5.1A-D implementation path or Phase 5.1 acceptance gate.
- No code, UI, database schema, runtime data, account profile, cookie, proxy,
  crawler, route exposure, deployment configuration, production state, or
  Phase 21 worktree was changed.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `git diff --check`
- Result: PASS whitespace check. Git emitted Windows LF-to-CRLF working-copy
  warnings only.
- Duplicate CR heading/index self-check
- Result: no duplicate CR headings and no missing Quick Index entries.
- Plan-cross-validation read-only subagent review
- Result: READY AFTER SMALL REFINEMENTS, with no blocking findings. The review
  confirmed CR-075 lane separation and CR-081 execution governance are not
  confused; Phase 21 remains `/monitor` frontend visual-only; Phase 5.1P
  remains read-only; Phase 5.1A-D and acceptance are serially gated; CR-070
  waits for CR-047 provider/effective snapshot proof; CR-078/079/080 stay
  future independent; and `Needs Confirmation` items are not treated as ready
  implementation work. The two suggested refinements were applied in this
  entry, in the Phase 5.1 acceptance-gate task block, and in the Phase 5.1E
  task boundary wording.

## 2026-06-19 - CR-078 To CR-080 Future Backlog MECE Documentation Gate

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added CR-078, CR-079, and CR-080 as future independent backlog lanes.
- Created `docs/MONITOR_NEXT_FRONTEND_PLAN.md` for future `/monitor-next`
  frontend migration planning.
- Created `docs/CRAWLER_PROVIDER_ARCHITECTURE.md` for future crawler provider
  architecture planning.
- Synchronized `TASKS.md`, `CURRENT_STATE.md`, `TEST_PLAN.md`, and
  `TRACEABILITY.md` so each new CR has a task block, test gate, and
  traceability row.
- Synchronized specialist docs for frontend architecture, server deployment,
  API authorization, account environment, data model, schema migration, roles
  and permissions, product requirements, and UI/UX guidelines.
- Recorded the CR-079 decision split in `DECISIONS.md`: MediaCrawler internal
  engine boundary is accepted, while exact production route/mount/
  reverse-proxy/404-vs-403-vs-unmounted behavior remains pending route audit.
- No code, UI, database schema, runtime data, account profile, cookie, proxy,
  crawler, deployment configuration, or Phase 21 worktree was changed.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `git diff --check`
- Result: PASS whitespace check. Git emitted Windows LF-to-CRLF working-copy
  warnings only.
- Local full open-todo cross-check
- Result: no blocking findings. CR-078 remains future `/monitor-next`
  planning and does not touch current `/monitor` or Phase 21; CR-079 remains
  public exposure and product-boundary planning without choosing 404/403/
  unmount behavior; CR-080 remains future provider architecture and is not a
  Phase 5.1P prerequisite; CR-070 remains after CR-047 provider/effective
  snapshot verification; no duplicate CR headings were found; both new source
  documents exist.
- Plan-cross-validation read-only subagent review
- Result: READY AFTER SMALL REFINEMENTS, with no blocking findings. The review
  confirmed CR-078/079/080 are present in tasks, CRs, traceability, and test
  plan; CR-078 does not touch Phase 21; CR-079 is not a frontend visual task
  and does not prematurely choose route behavior; CR-080 is separate from
  Phase 5.1P and has no schema/code task; CR-078 and CR-080 remain Needs
  Confirmation; CR-070 remains correctly delayed.

Follow-up:

- After the active Phase 21 worktree is merged, run a small documentation
  cleanup pass for CR numbering, overlapping Phase 21 wording, and any
  Phase21-completed visual or wording items that should be referenced rather
  than repeated in CR-078/079/080.

## 2026-06-19 - CR-075 Open Todo MECE Rebaseline Documentation Gate

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Reorganized the current open roadmap in documentation only.
- Added CR-075 as the owner for the MECE todo rebaseline and Phase 5.1
  preflight gate.
- Kept Phase 21 as the active frontend visual-only lane on the current Task
  Center / Run Detail baseline.
- Added Phase 5.1P as the required documentation/read-only compatibility gate
  before Phase 5.1 schema/code implementation.
- Made container/server-like execution and BrowserEnvironmentProvider
  requested/effective snapshot behavior part of the Phase 5.1
  development/acceptance baseline, not a separate parallel big task.
- Marked CR-070 / Phase 5.2 as dependent on CR-047 provider binding and
  effective runtime snapshot verification.
- Kept CR-037, the unrendered Users And Permissions page, and Phase 7.1D
  historical repair outside the Phase 21 and Phase 5.1 implementation lanes.
- No code, UI, database schema, runtime data, account profile, cookie, proxy,
  crawler, or deployment configuration was changed.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Plan-cross-validation read-only subagent review
- Result: READY AFTER SMALL REFINEMENTS, with no blocking findings. The review
  confirmed the open todos are MECE enough for execution, Phase 5.1 hidden
  coupling is exposed through the preflight/provider/snapshot gate, CR-070 is
  delayed until CR-047 provider/effective snapshot verification, and Phase 21
  preserves the current Task Center / Run Detail visual-only boundary.
- Follow-up refinements from review were applied: Phase 5.1P is explicitly
  read-only mapping only, and local Chrome/Edge auto-detection, local-window
  login, CDP connect-existing, process defaults, and default-network fallback
  are diagnostic fallbacks only for Phase 5.1 acceptance.

## 2026-06-19 - CR-074 Console Refresh Action Deduplication And Icon Loading

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor?codex_verify_overall=1`.

Result:

- Removed redundant first-level page refresh buttons that duplicated the shared
  current-page refresh action.
- Kept one top-bar current-page refresh entry and rendered it as an icon-only
  SVG button with accessible label/tooltip.
- Converted semantically scoped refresh actions for schedule recomputation,
  delivery history, email-template preview, run logs, and Run Detail into the
  same icon-only refresh treatment.
- Added refresh-icon loading behavior with disabled state and a short minimum
  visible spin window so users get clear feedback even when the data request is
  fast.
- Preserved Task Center grouping and filters, resource page primary actions,
  Run Detail, logs, template preview, delivery history, and diagnostics.

Verification:

- `uv run pytest tests/test_monitoring_mvp.py -q -k "cr074 or phase_12b or task_center_single_grouping or monitor_page_uses_tob_information_architecture"`
- Result: PASS, 4 passed.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`:
  - Confirmed six `.refresh-icon-button` controls remain: one top-bar
    current-page refresh plus five scoped refresh actions.
  - Confirmed no visible button text begins with `刷新`.
  - Clicked the top-bar refresh icon and confirmed it enters disabled/loading
    state, keeps empty visible text, then restores to enabled/non-loading.

## 2026-06-19 - CR-070 Plan Cross Validation Re-Review

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Ran a fresh read-only Plan Cross Validation review for CR-070 using the
  current accepted docs set and an external ClaudeCode reviewer.
- The reviewer reported no P0 blockers.
- The reviewer's claimed P1 gaps for missing TEST_PLAN and TRACEABILITY
  coverage did not hold after re-checking the current docs; both already
  contain CR-070-specific coverage.
- Accepted the reviewer's P2 wording note that the plan should avoid stale
  "full migration" / "proposed" phrasing in current normative docs.
- Normalized the CR-070 wording in docs so the active plan consistently refers
  to the slim login-state migration package instead of a raw full-profile
  export.
- No code, database, package artifact, real profile, Cookie, proxy, login
  state, crawler, email, AI provider, or deployment configuration was changed.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `rg` cross-check against current CR-070 wording in docs
- Result: remaining hits are expected historical or exclusion wording, not
  unresolved current-plan contradictions.

## 2026-06-19 - CR-073 Scrollable Drawer Corner Radius Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor?codex_verify_overall=1`.

Result:

- Implemented the focused scrollable drawer corner-radius regression fix.
- Shared `.drawer` shells now keep the rounded chrome and top-right close
  button outside the scroll container, while the content after the header is
  normalized into a shared `.drawer-scroll-body` that owns scrolling.
- The visible scrollbar now belongs to the inner content body and starts below
  the sticky header area instead of painting into the absolute drawer top
  edge.
- The top-right close button remains in the header's top-right position; it
  was not moved inward or toward the center as the workaround.
- CR-038 sticky header/close behavior, CR-071 enhanced drawer/modal selects,
  and CR-072 task edit custom date picker behavior are preserved.

Verification:

- `uv run pytest tests/test_monitoring_mvp.py -q -k "cr073 or cr038 or cr071_drawer_modal_selects_reuse_filter_dropdown_mechanism"`
- Result: PASS, 3 passed.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator path:
  - Reloaded the page and opened the long Monitoring task drawer through
    `新建监控任务`.
  - Confirmed the drawer shell itself is clipped while the inner
    `.drawer-scroll-body` is the scrolling surface.
  - Confirmed the visible scrollbar belongs to the inner body and starts below
    the header area rather than at the outer shell's top edge.
  - Confirmed the top-right corner remains rounded and the close button remains
    visible in the top-right header position.

## 2026-06-19 - CR-070 User Decision Confirmation Documentation Update

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Accepted CR-070 as Phase 5.2 planning after user confirmation.
- Corrected the export design from a raw full-profile migration idea to a slim
  encrypted login-state migration package: export account configuration,
  CR-047 identity metadata, platform-account metadata, login/session state,
  and necessary profile state, while excluding raw browser cache, GPU cache,
  code cache, media cache, crash dumps, downloads, screenshots, temporary
  files, and duplicated or regenerable browser artifacts by default.
- Confirmed V1 package encryption uses a passphrase-based encrypted envelope.
- Confirmed V1 may include source proxy host/IP plus port only as an encrypted
  endpoint hint for target-side mapping, and must not export proxy username,
  password, token, authentication header, or provider secret.
- Confirmed V1 imports create a new target account/profile by default.
- Confirmed V1 exports avatar metadata only, not cached avatar image bytes.
- No code, database, package artifact, real profile, Cookie, proxy, login
  state, crawler, email, AI provider, or deployment configuration was changed.
- Updated the CR-070 design from a raw full-profile migration idea to a slim
  encrypted login-state migration package that carries login/session state and
  necessary profile state while excluding raw whole-profile cache and other
  regenerable browser artifacts by default.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-19 - CR-072 Task Edit Custom Date Picker Consistency

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Implemented the focused task edit custom date consistency follow-up.
- Monitoring task edit `自定义开始日期` and `自定义结束日期` now opt into the
  existing `.page-filter-region input[type="date"]` enhancement and render
  through `.filter-date-enhanced`, `.filter-select-button.filter-date-button`,
  and `.filter-date-menu`.
- The visible date trigger matches Task Center's date-filter button style.
- The original hidden date inputs still store `custom_start` / `custom_end`
  values for the task form and dispatch the same `change` event when changed.
- AI Access `模型名称`, drawer/modal select dropdowns, and unrelated ordinary
  date fields keep their accepted behavior.

Verification:

- `uv run pytest tests/test_monitoring_mvp.py -q -k "cr071_drawer_modal_selects_reuse_filter_dropdown_mechanism or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: PASS.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator path:
  - Opened the visible Monitoring task drawer through `舆情监控 -> 新建任务`.
  - Task edit `自定义开始日期` opened the local attached `.filter-date-menu`
    inside its own `.filter-date-enhanced` wrapper with `position: absolute`,
    `left: 0`, about a 4px top gap, and width matching the trigger within
    about 0.5px.
  - The menu included month navigation, seven weekday labels, a day grid,
    `今天`, and `清空`.
  - Selecting `今天` updated hidden `custom_start` to `2026-06-19` and the
    visible label to `2026/06/19`; clearing reset the hidden value and label.
  - Task edit `自定义结束日期` opened with the same local attachment, weekday
    row, day grid, `今天`, and `清空`; selecting `2026-06-01` updated hidden
    `custom_end` and the visible label.
  - Scope check confirmed the only enhanced date inputs were task edit
    `custom_start`, task edit `custom_end`, and the existing Task Center date
    filters; AI Access `模型名称` remained the existing input/model-list
    combobox.

## 2026-06-19 - CR-070 Plan Cross Validation Documentation Gates

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Continued CR-070 documentation-only planning after the first external
  read-only Plan Cross Validation review.
- Added proposed package schema details, encrypted package envelope rules,
  metadata-only sensitivity boundary, export/import state machines, operation
  locks, cleanup/finalization rules, target proxy mapping rules, profile
  snapshot path/quota safety, package retention behavior, redacted audit
  fields, and CR-070-specific test tripwires.
- Clarified that CR-070 package scope is one selected platform account
  environment, not a full database backup of tasks, runs, reports, AI traces,
  email delivery logs, users, runtime settings, or business history.
- Kept CR-070 status as `Needs Confirmation` for package modes, encryption
  model, proxy credential policy, import conflict behavior, and avatar
  handling.
- No code, database, package artifact, real profile, Cookie, proxy, login
  state, crawler, email, AI provider, or deployment configuration was changed.
- Focused external read-only CR-070 re-review verdict:
  `READY AFTER USER DECISIONS`. The reviewer confirmed the previous P1 gaps
  are closed, found no new P0/P1 blockers, and treated the remaining five
  confirmation items as intentional user/business decisions rather than Codex
  documentation gaps.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before focused re-review.
- Focused external read-only CR-070 re-review through ClaudeCode CLI.
- Result: READY AFTER USER DECISIONS; no new P0/P1 blockers.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency after recording re-review result and adding
  the proposed passphrase-mode envelope shape.

## 2026-06-19 - CR-071 Drawer And Modal Select Dropdown Consistency

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Implemented the focused drawer/modal select consistency follow-up.
- The listed secondary surfaces now opt selected `select` fields into the
  existing `.page-filter-region select` enhancement and reuse the same
  `.filter-select-*` classes and menu behavior as Task Center filters.
- Confirmed the AI Access `模型名称` field remains the existing free-text/model
  list combobox and is not converted.
- Confirmed task edit custom start/end date fields remain native form date
  inputs.
- Confirmed dynamic option refresh paths synchronize visible enhanced labels
  for account, proxy, AI profile, email template, platform login, and disabled
  state changes.

Verification:

- `uv run pytest tests/test_monitoring_mvp.py -q -k "cr071_drawer_modal_selects_reuse_filter_dropdown_mechanism or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 306 deselected, 1 warning.
- `uv run pytest tests/test_monitoring_mvp.py -q`
- Result: 308 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator path:
  - Monitoring task edit, Platform Account detail, Proxy edit, AI Access edit,
    AI Evaluation Rule edit, Mail Configuration edit, and Mail Template edit
    dropdowns opened with `.filter-select-button` triggers and
    `.filter-select-menu` options.
  - Open menus stayed aligned to their triggers and rendered a single
    `.filter-select-option.is-selected` item.
  - AI Access `模型名称` remained the model combobox.
  - Task edit custom date inputs remained native date inputs.

## 2026-06-19 - CR-070 Account Environment Export/Import Documentation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded CR-070 as a proposed new capability for account-environment
  export/import, without implementing code, schema migration, package
  generation, profile access, Cookie access, proxy access, or platform login
  behavior.
- Documented two package modes: metadata-only export and full encrypted
  migration package.
- Documented package manifest, encrypted login/profile material handling,
  platform-account metadata, proxy mapping, import preflight, target
  `profile_key` derivation, post-import login-state verification, and
  `requires_relogin` fallback.
- Documented that package import verifies restoration and login state, but
  does not guarantee that a platform will accept a migrated session across
  different servers, proxies, browser builds, or risk states.
- Marked CR-070 as `Needs Confirmation` for package modes, encryption model,
  proxy credential policy, import conflict behavior, and avatar handling.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-069 Run Detail AI Evaluation Consolidation Verification

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Verified the Task Center / Run Detail information architecture follow-up that
  consolidates report `查看线索` into Run Detail `AI 评估`.
- Confirmed report `查看线索` now acts as a report-scoped shortcut into the same
  AI Evaluation table instead of opening a duplicate lead drawer/table.
- Confirmed Run Detail `AI 评估` keeps report, status, risk, platform, keyword,
  and title filters, while retaining per-evaluation trace detail and
  limited-context old rows.
- Confirmed `报告范围` is a selectable filter only when the selected run has
  multiple reports; runs with zero or one report show a read-only scope note.
- Confirmed Run Detail `AI 评估` status/risk/platform dropdowns use the same
  enhanced page-filter dropdown treatment as first-level Task Center filters.

Verification:

- `uv run pytest tests/test_monitoring_mvp.py -q -k "phase_20c_run_detail_api_scope_filters_and_redacted_trace or phase_20d_run_detail_frontend_hooks or phase_20e_report_leads_backlink_to_run_detail or monitor_page_uses_consistent_buttons_tables_and_modal_actions or task_center_single_grouping_switch_unifies_rows_and_actions or cr048 or cr049 or cr051 or cr052 or cr053 or cr056 or cr057 or phase_18b_report_center_task_grouping_frontend_hooks"`
- Result: 9 passed, 298 deselected, 3 warnings.
- `uv run pytest tests/test_monitoring_mvp.py -q`
- Result: 307 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator Task Center:
  - Opened run detail for `run_id=10693` and switched to `AI 评估`.
  - Verified the AI filter toolbar is a `.page-filter-region`.
  - Verified `状态`, `风险`, and `平台` render as enhanced filter dropdown
    buttons with consistent height and styling.
  - Verified the current run with no generated report shows `报告范围` as a
    hidden stored value plus read-only scope note, not as a dropdown.

## 2026-06-18 - CR-047 Template Selection Policy Documentation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Documented the CR-047 template selection policy as a documentation-only
  refinement, without implementing code, schema, runtime, profile, cookie,
  proxy, or login changes.
- Recorded that account identity template selection is automatic by default.
- Recorded that normal users cannot choose identity templates or field-level
  browser identity values.
- Recorded that administrators may only use an advanced pre-login path to
  choose a template family, while UA, viewport, screen, timezone, locale,
  accept-language, and device flags come from the selected catalog template and
  region bundle.
- Added a deterministic template-selection seed and catalog-order selection
  rule before final fingerprint seed generation.
- Added explicit state-machine rules for template-family changes in `draft`,
  `generated`, `validated`, `login_in_progress`, `locked`, `active`,
  `requires_relogin`, and `resetting`.
- Recorded that changing a locked template requires explicit reset/re-login
  and audit logging.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-068 Date Filter Local Attached Menu Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining Task Center date dropdown visual offset after CR-067.
- The date menu now mounts inside the clicked date control wrapper while open,
  uses wrapper-local absolute positioning, opens directly under the clicked
  field, and matches the clicked trigger width.
- Preserved the original hidden date inputs, stored date values, `change`
  events, clear/reset behavior, weekday/day grid, and ordinary
  form/configuration date inputs.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 307 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for current `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, normal-user Task Center:
  - Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus were
    mounted inside their clicked `.filter-date-enhanced` wrappers, used
    `position: absolute`, had left-edge delta `0px`, top gap about `4px`, and
    width delta about `0.03px`.
  - Tablet effective viewport `980x746`: `结束日期` menu was mounted inside its
    clicked wrapper, used `position: absolute`, had left-edge delta `0px`, top
    gap about `4px`, width delta `0px`, and no horizontal page overflow.
  - Mobile effective viewport `364x819`: after scrolling the date field into
    view, `结束日期` menu was mounted inside its clicked wrapper, used
    `position: absolute`, had left-edge delta `0px`, top gap about `4px`,
    width delta about `0.23px`, and no horizontal page overflow.

## 2026-06-18 - CR-067 Date Filter Trigger-Width Visual Attachment Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining Task Center date dropdown visual offset after CR-066.
- The date menu now matches the clicked trigger width when the trigger is
  usable, aligns its left edge to the trigger left edge, keeps the top anchor
  marker tied to the trigger center, and only uses a small minimum readable
  width for unusually narrow triggers before viewport clamping.
- Preserved the original hidden date inputs, stored date values, `change`
  events, clear/reset behavior, weekday/day grid, and ordinary
  form/configuration date inputs.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: PASS after implementation.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for current `api/monitor_web/index.html`
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, normal-user Task Center:
  - Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus
    matched the clicked trigger width within about `0.04px`, aligned left
    edges within about `0.4px`, kept the top anchor marker aligned to the
    trigger center within about `0.12px`, stayed inside the visual viewport,
    and had zero overflowing date cells.

## 2026-06-18 - Phase 19-20 And Task Center Final Regression Verification

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`, validation database
`.codex_tmp/phase20_browser/monitor.sqlite`.

Result:

- Re-verified Phase 19B-D, Phase 20B-E, CR-048/CR-049 preservation, and the
  Task Center information-architecture consolidation after the latest Task
  Center/date-filter refinements.
- Confirmed the formal console exposes one top-level `任务中心` instead of a
  separate Report Center, the Task Center list uses one filter surface, the
  `按舆情任务分组` control is a display switch, grouped rows are keyed by the
  monitoring task context, and row actions are limited to `详情`.
- Confirmed Run Detail is the shared run-scoped surface for Overview,
  Collection Logs, Collected Contents, AI Evaluation, Report, and Email
  Delivery; AI evaluation rows open detail from the same surface, and Report
  contains preview, report-scoped leads, delivery history, resend, and
  HTML/Excel/Markdown downloads.
- Confirmed normal users see only allowed navigation (`总览`, `舆情监控`,
  `任务中心`) and can open Task Center `详情` without seeing administrator
  resource/configuration navigation.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or phase_19c or phase_19d or phase_20b or phase_20c or phase_20d or phase_20e or cr051 or task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions or cr048 or cr049"`
- Result: 16 passed, 291 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 307 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator path:
  - Desktop effective viewport `1383x874`: Task Center had no Report Center
    entry, no page horizontal overflow, grouped mode was enabled, grouped rows
    showed only `详情` actions, and Run Detail opened with six tabs.
  - Run `#1` Run Detail showed AI Evaluation counts and row-level `查看`, the
    Report tab showed `预览`, `查看线索`, `交付历史`, `重发邮件`, and
    `下载 HTML/Excel/Markdown`, the Email Delivery tab showed scoped delivery
    status, and visible Run Detail text did not expose raw API keys,
    authorization headers, cookies, SMTP passwords, proxy credentials, profile
    paths, or server-local paths.
- Browser verification on local `/monitor`, normal-user path
  (`user@example.com` / `UserPass123!`):
  - Desktop effective viewport `1383x874`: visible navigation was limited to
    `总览`, `舆情监控`, and `任务中心`; no Report Center entry was visible; Task
    Center grouped rows showed only `详情`; no page horizontal overflow.
  - Tablet effective viewport `980x746`: Task Center remained reachable,
    visible row `详情` buttons opened Run Detail, Run Detail stayed within the
    viewport with the six expected tabs, and no page horizontal overflow was
    observed.
  - Mobile effective viewport `364x819`: after scrolling the Task Center table
    into view, row `详情` buttons remained reachable, Run Detail opened as a
    readable near-fullscreen drawer with the six expected tabs, and no page
    horizontal overflow was observed.

## 2026-06-18 - CR-066 Date Filter Trigger-Attached Dropdown Alignment Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining Task Center date dropdown visual offset after CR-065.
- The date menu now opens from the clicked trigger's left edge like a normal
  attached filter dropdown, shrinks before clamping near the right edge, keeps
  the visual-viewport safety checks, and preserves the top anchor marker
  connection to the clicked trigger center.
- Preserved the original hidden date inputs, stored date values, `change`
  events, clear/reset behavior, weekday/day grid, and ordinary
  form/configuration date inputs.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for current `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, Task Center, administrator path:
  - Desktop effective viewport `1383x874`: `开始日期` and `结束日期` menus opened
    from the clicked trigger's left edge. `开始日期` left-edge delta was about
    `0.36px`; `结束日期` left-edge delta was about `0.39px` after shrinking to
    about `221px`. Both stayed inside the visual viewport, had zero overflowing
    date cells, and created no page horizontal overflow.

## 2026-06-18 - CR-065 Date Filter Center-Anchored Visual Alignment Regression Fix

Result:

- Historical verified snapshot superseded by CR-066. It proved the
  center-anchored readable popover had correct mathematical center alignment,
  but later browser review found it still looked visually detached from the
  date field at desktop review width.

## 2026-06-18 - CR-064 Date Filter Trigger-Attached Edge Shrink Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining Task Center date dropdown visual offset after CR-063.
- The date menu now uses the visual viewport for fixed-position edge checks,
  prefers left-edge attachment to the clicked date filter, and slightly shrinks
  near the right edge before falling back to right alignment or viewport
  clamping.
- Preserved the original hidden date inputs, stored date values, `change`
  events, clear/reset behavior, weekday/day grid, and ordinary
  form/configuration date inputs.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for current `api/monitor_web/index.html`
- Result: PASS, 2 inline scripts parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 307 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, Task Center:
  - Desktop effective viewport `1383x874`: `开始日期` left edge aligned to the
    trigger within about `0.4px`; `结束日期` left edge aligned within about
    `0.4px` after shrinking to about `221px`; both had zero overflowing date
    cells and no visual-viewport overflow.
  - Tablet effective viewport `980x746`: `开始日期` left edge aligned within
    about `0.3px`; `结束日期` left edge aligned within about `0.3px` after
    shrinking to about `198px`; both had zero overflowing date cells and no
    visual-viewport overflow.
  - Mobile effective viewport `364x819`: both date menus used the mobile
    trigger width, stayed attached to the field, had zero overflowing date
    cells, and created no page horizontal overflow.

## 2026-06-18 - CR-047 Task-Level Proxy Override Policy Decision

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded the confirmed CR-047 V1 policy: after an account identity is
  locked, task-level proxy overrides are rejected for that locked account
  environment.
- Recorded that proxy changes require explicit account identity reset/re-login.
- Recorded that existing logged-in accounts should remain readable but not
  receive guessed identity backfill; they should be re-logged in under CR-047
  identity rules when the feature is implemented.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-063 Date Filter Readable Anchored Popover Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining Task Center date dropdown visual misalignment report
  after CR-062.
- Browser inspection showed the CR-062 menu was coordinate-correct, but the
  trigger-width calendar was still visually cramped. The current menu uses a
  compact readable calendar width and a top anchor marker aligned to the
  clicked trigger.
- Preserved the original hidden date inputs, stored date values, `change`
  events, clear/reset behavior, weekday/day grid, and ordinary
  form/configuration date inputs.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, `.codex_tmp/inline_datepicker_cr063.js` parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 307 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, normal-user Task Center:
  - Desktop effective viewport `1383x874`: `开始日期` opened at about `236px`
    wide with its left edge aligned to the trigger, `结束日期` opened at about
    `236px` wide with its right edge aligned to the trigger, both with zero
    overflowing day cells.
  - Tablet effective viewport `980x746`: `结束日期` stayed inside the viewport,
    kept about a `4px` top gap, and had zero overflowing day cells.
  - Mobile effective viewport `364x819`: `结束日期` used the mobile trigger
    width, stayed inside the viewport, had zero overflowing day cells, and
    created no page horizontal overflow.

## 2026-06-18 - CR-062 Date Filter Grid Compression Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Fixed the remaining date-filter visual misalignment report after CR-061.
- Browser inspection showed the date-picker shell was already aligned to the
  trigger, but the internal calendar cells could still be compressed because
  date buttons inherited browser default padding and automatic minimum width.
- Updated the date grid CSS so weekday/day columns share the available
  trigger-width surface and two-digit day numbers no longer overflow or clip.
- Preserved CR-061 trigger-width left-edge anchoring, original hidden date
  inputs, date values, `change` events, clear/reset behavior, and ordinary
  form/configuration date inputs.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser verification on local `/monitor`, administrator Task Center at the
  desktop review viewport:
  - `开始日期` and `结束日期` menu widths still matched the trigger within about
    `0.03px`;
  - left/right edge deltas stayed within about `0.42px`;
  - both menus showed all seven weekday/day columns;
  - date cell overflow checks returned no overflowing day numbers.

## 2026-06-18 - Phase 19/20 And Task Center Final Verification Refresh

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Re-ran the Phase 19B-D, Phase 20B-E, CR-048/CR-049 preservation, and Task
  Center consolidation regression set after the latest Task Center date-filter
  refinement.
- Re-checked the formal Task Center in the in-app browser for administrator
  and normal-user paths at desktop, tablet, and mobile review viewports.
- Confirmed the top-level navigation exposes `任务中心` and no separate
  `报告中心`; normal users see only `总览`, `舆情监控`, and `任务中心`.
- Confirmed grouped Task Center rows keep row action text to `详情`; Run Detail
  opens with `概览`, `采集日志`, `采集内容`, `AI 评估`, `报告`, and `邮件交付`.
- Confirmed Task Center date filters use the CR-065 center-anchored readable
  popover, remain inside the viewport, keep seven date columns readable, and do
  not create page-level horizontal overflow at the tested viewports.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or phase_19c or phase_19d or phase_20b or phase_20c or phase_20d or phase_20e or cr048 or cr049 or cr051 or cr052 or cr053 or cr054 or cr055 or cr056 or cr057 or cr058 or cr059 or cr060 or cr061 or task_center_single_grouping_switch or monitor_page_uses_consistent_buttons_tables_and_modal_actions or run_summary_and_log_api_redact_sensitive_values or sensitive_text_is_redacted"`
- Result: 18 passed, 289 deselected, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Administrator browser verification:
  - 1440x900 effective viewport `1383x874`: no page horizontal overflow, no
    `报告中心` nav, row actions only `详情`, grouped headers start with
    `运行 ID` and compact status, Run Detail opened with all six tabs, and no
    sensitive-key/path pattern was visible in the Run Detail drawer.
  - 1024x768 effective viewport `980x746`: no page horizontal overflow, no
    `报告中心` nav, row actions only `详情`, and date menus stayed inside the
    viewport.
  - 390x844 effective viewport `364x819`: no page horizontal overflow, no
    `报告中心` nav, row actions only `详情`, date filter controls remained
    visible and usable, and date menus stayed inside the viewport.
- Normal-user browser verification:
  - 1440x900 effective viewport `1383x874`: nav only `总览`, `舆情监控`,
    `任务中心`; no page horizontal overflow; row actions only `详情`; Run
    Detail opened with all six tabs and no sensitive-key/path pattern.
  - 1024x768 effective viewport `980x746`: nav only allowed pages, no page
    horizontal overflow, row actions only `详情`, and date menus stayed inside
    the viewport.
  - 390x844 effective viewport `364x819`: nav only allowed pages, no page
    horizontal overflow, row actions only `详情`, date filter controls remained
    visible and usable, and date menus stayed inside the viewport.

## 2026-06-18 - CR-047 Account Identity Fidelity Documentation Refinement

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Refined CR-047 from Account Browser Environment Consistency into Account
  Identity Fidelity without implementing code, schema, or runtime changes.
- Documented the account identity lifecycle target: profile traces, browser
  environment, proxy region/policy, runtime binding, lock state, and audit
  state.
- Split profile-folder responsibilities from database-stored identity launch
  rules.
- Added planned Account Identity Generator and Account Identity Validator
  expectations, including stable generation, self-consistency validation, China
  mainland region/timezone/locale/accept-language defaults, and fail-closed
  behavior for missing or contradictory identity fields.
- Kept CR-047 accepted but not implemented, and kept the fixed-environment
  proxy override policy as a required confirmation before code implementation.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-047 V1 Provider Boundary Documentation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded the confirmed CR-047 boundary that V1 does not introduce
  CloakBrowser or CloakBrowser-Manager.
- Recorded that V1 stays on the existing Playwright/CDP provider path and uses
  a provider boundary for future expansion.
- Recorded why Canvas, WebGL, font inventory, plugins, extensions, and long
  browsing history are future/provider-dependent rather than V1 commitments:
  they depend on browser build, OS/fonts, graphics stack, installed extensions,
  profile history, provider behavior, and runtime JavaScript probes instead of
  static launch options alone.
- Added a planning estimate for future high-fidelity browser-persona work:
  1-2 days for provider/license/deployment review, 3-5 days for a one-platform
  prototype, 1-2 weeks for optional provider integration, and 3-6+ weeks for a
  production-grade browser-pool/profile-history capability.

## 2026-06-18 - CR-047 Generation And Lifecycle Spec Update

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added the first-pass deterministic identity-generation specification:
  canonical input tuple, HMAC-SHA256 seed derivation, template catalog, and
  versioned catalog note for future browser upgrades.
- Added the identity lifecycle state machine, fail-closed launch order, runtime
  snapshot shape, audit events, and test-safety tripwires to the CR-047
  account-environment docs.
- Synchronized CR-047 requirements across TASKS, CURRENT_STATE, DECISIONS,
  CHANGE_REQUESTS, DATA_MODEL, SCHEMA_MIGRATION, TRACEABILITY, TEST_PLAN, and
  PRODUCT_REQUIREMENTS without changing runtime code.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-061 Date Filter Trigger-Width Anchoring Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the page-level filter date menu after browser review found the
  CR-060 centered compact calendar still looked offset beside the date button.
- The custom date menu now matches the clicked date trigger width and aligns
  to the trigger's left edge, so it reads as an attached dropdown instead of a
  wider floating calendar.
- The calendar internals were compacted to keep month navigation, day grid,
  and quick actions readable inside the trigger-width menu.
- Existing hidden date inputs, values, `change` events, clear/reset behavior,
  and ordinary form/configuration date inputs remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- Browser coordinate inspection on local `/monitor` after logging in as the
  administrator and opening Task Center at the desktop review viewport.
- Result: PASS; `开始日期` opened with menu width matching the trigger within
  about `0.03px`, left/right edge deltas within about `0.40px`, inside the
  viewport, and about a `4px` top gap.
- Result: PASS; `结束日期` opened with menu width matching the trigger within
  about `0.03px`, left/right edge deltas within about `0.43px`, inside the
  viewport, and about a `4px` top gap.

## 2026-06-18 - CR-060 Date Filter Compact Center Alignment Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the page-level filter date menu after browser review found the
  CR-059 edge-aligned calendar still looked offset beside narrow date buttons.
- The custom date menu now uses a compact calendar width of about `232px`
  instead of forcing a 280px minimum for the Task Center date filters.
- `开始日期` and `结束日期` now align the menu center line to the trigger center
  line when space allows, then clamp only as a final viewport-safety fallback.
- Existing hidden date inputs, values, `change` events, clear/reset behavior,
  and ordinary form/configuration date inputs remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser coordinate inspection on local `/monitor` after reloading the page
  and opening Task Center at the desktop review viewport.
- Result: PASS; `开始日期` opened with the menu center aligned to the trigger
  center within about `0.13px`, stayed inside the viewport, and kept about a
  `4px` top gap.
- Result: PASS; `结束日期` opened with the menu center aligned to the trigger
  center within about `0.10px`, stayed inside the viewport, and kept about a
  `4px` top gap.

## 2026-06-18 - CR-059 Date Filter Edge Anchoring Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the page-level filter date menu positioning so wider date menus
  attach to the clicked trigger edge instead of centering and visually drifting
  from the trigger.
- `开始日期` aligns the menu left edge to the trigger left edge when there is
  room.
- `结束日期` near the right viewport edge aligns the menu right edge to the
  trigger right edge when needed to avoid overflow.
- Existing hidden date inputs, values, `change` events, clear/reset behavior,
  and ordinary form/configuration date inputs remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before final status update.
- Browser coordinate inspection on local `/monitor` after reloading the page
  and opening Task Center at the desktop review viewport.
- Result: PASS; `开始日期` opened with the menu left edge aligned to the trigger
  left edge within about `0.36px`.
- Result: PASS; `结束日期` opened with the menu right edge aligned to the
  trigger right edge within about `0.42px`.
- Result: PASS; both menus stayed inside the viewport with about a `4px` top
  gap.
- Browser interaction check selected `2026-06-18` and then cleared it on
  `结束日期`; the original input changed to `2026-06-18`, the visible label
  changed to `2026/06/18`, and clearing reset both value and label.

## 2026-06-18 - Phase 20C Run Detail Path Redaction Hardening

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Hardened the shared sensitive-text redaction so Run Detail collection logs
  and AI trace text redact Windows paths with spaces, Unix absolute paths,
  residual Chrome path fragments, and implementation-only path field names
  such as `profile_path`.
- The Run Detail log API keeps returning customer-safe log content, but no
  longer leaks path tails such as `Program Files\Google\Chrome\Application`.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "sensitive_text_is_redacted or run_summary_and_log_api_redact_sensitive_values or phase_20c_run_detail_api_scope_filters_and_redacted_trace or phase_20b_ai_trace_persistence_redaction_truncation_and_retention"`
- Result: 4 passed, 303 deselected, 3 warnings.
- Manual sample check through `api.monitoring.security.redact_sensitive` and
  `customer_safe_text`.
- Result: PASS; sample strings containing `C:\Program Files\Google\Chrome`,
  `Files\Google\Chrome`, `profile_path=C:\Users\...`, and
  `/home/app/monitor_data/...` were redacted to `[PATH_REDACTED]`,
  `[REDACTED]`, or customer-safe `运行日志` wording.

## 2026-06-18 - CR-058 Date Filter Center Clamp Follow-up

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the Task Center date filter menu to center on the clicked trigger
  control by default, then clamp only when the wider menu approaches the
  viewport edge.
- Fixed the date select/clear path so it stores the active input before
  closing the menu; this prevents the date menu click handler from clearing
  its own state before dispatching the existing `change` event.
- The original date inputs, visible date labels, clear/reset behavior, and
  existing filter semantics remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- Browser coordinate inspection with the in-app browser after applying the
  `1440x900` browser target, effective viewport `1398x874`.
- Result: PASS; both `开始日期` and `结束日期` date menus used
  `position: fixed`, opened with about a 4px top gap, and stayed inside the
  viewport.
- `开始日期`: menu center matched the trigger center within about `0.13px`.
- `结束日期`: menu center was shifted left by about `12.10px` because the
  280px menu reached the right viewport clamp; the menu still stayed inside
  the viewport with the intended right margin.

## 2026-06-18 - CR-058 Date Filter Edge Alignment Follow-up

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the Task Center date filter floating menu from center anchoring to
  trigger-edge alignment with viewport clamping. This keeps the wider picker
  visually attached to the clicked date control instead of floating beside it.
- The original date inputs, visible date labels, clear/reset behavior, and
  existing filter `change` semantics remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or phase_19c or phase_19d or phase_20b or phase_20c or phase_20d or phase_20e or cr048 or cr049 or cr051 or cr052 or cr053 or cr054 or cr055 or cr056 or cr057 or cr058 or task_center_single_grouping_switch or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 16 passed, 291 deselected, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser coordinate inspection with the in-app browser after applying the
  `1440x900` browser target, effective viewport `1398x874`.
- Result: PASS; `开始日期` and `结束日期` date menus used `position: fixed`,
  opened with about a 4px top gap, and stayed inside the viewport.
- `开始日期`: menu left edge aligned with the trigger left edge within about
  `0.36px`.
- `结束日期`: menu right edge aligned with the trigger right edge within about
  `0.42px`.

## 2026-06-18 - CR-058 Date Filter Center-Anchoring Follow-up

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Adjusted the Task Center date filter floating menu from side-specific
  alignment to center anchoring on the trigger control, with viewport clamping
  only when needed.
- The original date inputs, visible date labels, clear/reset behavior, and
  existing filter `change` semantics remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 2 passed, 305 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser coordinate inspection with the in-app browser after applying the
  `1440x900` browser target, effective viewport `1398x874`.
- Result: PASS; `开始日期` and `结束日期` date menus used `position: fixed`,
  opened with about a 4px top gap, stayed inside the viewport, and their menu
  center lines matched the trigger center lines within 1px. Measured center
  delta was about `-0.13px` for `开始日期` and `-0.10px` for `结束日期`.

## 2026-06-18 - Task Center Report Action Menu Removal Follow-up

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Removed the legacy report-list grouping and report-row action menu model from
  the formal console after Task Center consolidation.
- Task Center grouped and flat rows now keep the list-layer action model to
  `详情`; report preview, lead inspection, delivery history, resend, and
  downloads remain available inside Run Detail.
- The email delivery history drawer now points users to Run Detail's email
  delivery area instead of the old report list status/more-menu entry.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr051 or cr052 or cr053 or cr054 or cr055 or cr056 or cr057 or cr058 or phase_17b_report_center_delivery_history_frontend_hooks or phase_18b_report_center_task_grouping_frontend_hooks or phase_20d_run_detail_frontend_hooks or phase_20e_report_leads_backlink_to_run_detail or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 6 passed, 301 deselected, 1 warning.
- Static search confirmed the production frontend no longer contains
  `report-action-menu`, `data-report-menu-button`, `renderReportsTable`,
  `currentReports`, `reportEmailStatusCell`, or old report action-menu
  functions.

## 2026-06-18 - CR-058 Filter Date Picker Alignment Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Follow-up fix: Task Center date filters now anchor the wider date menu to
  the trigger's center line and clamp only when needed to avoid viewport
  overflow, preventing date pickers from looking detached after viewport
  clamping.
- Task Center page-level date filters now keep their original
  `<input type="date">` values and filtering semantics while rendering the
  visible picker through a fixed-position in-page date menu.
- The enhancement is scoped to `.page-filter-region input[type="date"]`;
  ordinary form and configuration date inputs remain native.
- Date selection and clear/reset paths synchronize the visible date button
  label with the underlying date input value.
- CR-057 grouped Task Center metric chips are also verified: the grouped header
  shows compact labeled aggregate chips instead of the previous long
  slash-separated summary sentence.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch_unifies_rows_and_actions or cr051_task_center_consolidates_report_grouping_without_separate_report_center or phase_19d_run_center_frontend_progress_polling_hooks or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 4 passed, 303 deselected, 1 warning.
- Browser coordinate inspection with the in-app browser on local `/monitor` at
  effective viewport `1398x874` after applying the `1440x900` browser target.
- Result: PASS; Task Center `run_date_from` date menu used `position: fixed`,
  opened with a 4px top gap, stayed within the viewport, and did not create
  horizontal overflow.
- Browser interaction inspection on the same date filter.
- Result: PASS; selecting `2026-06-01` updated the original input to
  `2026-06-01` and visible label to `2026/06/01`; clearing reset the input to
  empty and visible label to `开始日期`.
- Browser coordinate inspection for the right-side `run_date_to` filter after
  the follow-up fix.
- Result: PASS; at effective viewport `1398x874`, the `结束日期` trigger was
  about 173px wide and the date menu about 280px wide; the menu used
  `position: fixed`, stayed inside the viewport, opened with a 4px top gap,
  and remained visually anchored to the trigger.

## 2026-06-18 - CR-056 Filter Dropdown Alignment Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`, local `/monitor`
served at `http://127.0.0.1:19220/monitor`.

Result:

- Filter-region selects now keep their original select elements and filter
  values while rendering the visible dropdown through a fixed-position in-page
  menu.
- The enhancement is scoped to `.page-filter-region`; ordinary form and
  configuration selects remain native.
- Programmatic filter resets and role-mode updates synchronize the visible
  filter button label with the underlying select value.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "task_center_single_grouping_switch or phase_19d_run_center_frontend_progress_polling_hooks or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 3 passed, 304 deselected, 1 warning.
- Browser coordinate inspection with Chrome at `1440x900` on Task Center
  `run_status_filter`.
- Result: PASS; dropdown left aligned with trigger within 1px, stayed inside
  viewport, and selecting `已完成` updated the original select value.
- Browser coordinate inspection with Chrome at `1440x900` on Platform Accounts
  `account_status_filter`.
- Result: PASS; dropdown aligned with trigger and stayed inside viewport.

## 2026-06-18 - CR-055 Task Center Status Column Visual Refinement

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Task Center table rendering now gives `状态` headers and cells a stable
  `col-status` class.
- First-level run status badges no longer reuse the global `.status` pill class.
- Status badges render as compact state-dot labels with constrained status-column
  width, while active progress remains a short helper line below the badge.
- Grouped and flat Task Center field order, single `详情` action, and Run Detail
  behavior remain unchanged.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19d_run_center_frontend_progress_polling_hooks or task_center_single_grouping_switch or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 3 passed, 304 deselected, 1 warning.
- Browser inspection of local `/monitor` at desktop, tablet, and mobile widths.
- Result: PASS for compact status column and visible `详情` action.

## 2026-06-18 - CR-054 Task Center Status Badge Compactness Regression Fix

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Task Center status badges now use normalized short lifecycle labels instead
  of raw long `display_status` text.
- Completed rows render as `已完成` even if backend progress metadata includes
  ingestion completion detail.
- Active rows still may show one short progress cue below the badge.
- Task Center CSS constrains status badges to compact text-sized width, so the
  status cell no longer reads as a full-width bar.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19d_run_center_frontend_progress_polling_hooks or task_center_single_grouping_switch or cr051 or monitor_page_uses_consistent_buttons_tables_and_modal_actions"`
- Result: 4 passed, 303 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-053 Task Center Field Priority And Global Select Alignment

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Flat Task Center run rows now begin with `任务 ID`, `运行 ID`, and compact
  `状态`.
- Grouped Task Center rows hide duplicated `任务 ID` because the group header
  already identifies the monitoring task; group rows begin with `运行 ID` and
  compact `状态`.
- Terminal status cells stay short, and completed rows no longer append long
  ingestion/progress text in the table.
- Task Center status badges render as compact text-sized badges instead of
  full-width bars.
- Task Center keeps a single page-level refresh action; the filter toolbar
  keeps `筛选` and `清空`.
- The main content container no longer clips vertical overflow, reducing
  native select/dropdown misalignment across console pages.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr051 or task_center_single_grouping_switch or monitor_page_uses_consistent_buttons_tables_and_modal_actions or phase_15b_run_center_frontend_filters_pagination_archive_controls or phase_19d_run_center_frontend_progress_polling_hooks"`
- Result: 5 passed, 302 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-18 - CR-051 Task Center And Report Grouping Consolidation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Consolidated the formal console's separate Run Center / Report Center
  top-level IA into one `任务中心` entry.
- Task Center now opens on the existing report-by-monitoring-task grouping so
  each law-firm monitoring task shows its report rows, risk counts, preview,
  Run Detail, and secondary row actions in one surface.
- The old run-record table is preserved as the `运行记录` subview for run ID,
  task ID, type, visibility, duration, full failure reason, stop/log/archive/
  restore, and Run Detail operations.
- Removed the separate top-level `reports` section and `report_center` menu
  key. Legacy `reports` shortcut calls normalize to Task Center's task-group
  view.
- Kept report preview, report-scoped lead inspection, delivery history,
  resend, HTML/Excel/Markdown downloads, and Run Detail reachable while
  preserving CR-048/CR-049 scoped drawers as secondary detail.

Verification:

- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr051 or phase_18b_report_center_task_grouping_frontend_hooks or phase_17b_report_center_delivery_history_frontend_hooks or cr048 or cr049 or phase_20d_run_detail_frontend_hooks or phase_20e_report_leads_backlink_to_run_detail or phase_19d_run_center_frontend_progress_polling_hooks or phase_12b_page_entry_and_role_flow_shortcuts or phase_13b_operations_home_desktop_visual_metrics or monitor_page_uses_tob_information_architecture"`
- Result: 11 passed, 295 deselected, 1 warning.

## 2026-06-18 - Phase 20D Run Detail Frontend And Phase 20E Backlink

Environment: local worktree `E:\myproject\MediaCrawler`, plus an isolated
local FastAPI service on `http://127.0.0.1:19220/monitor` using
`.codex_tmp\phase20_browser` as temporary validation data.

Result:

- Added Run Center `详情` as the run-scoped entry into Run Detail.
- Run Detail now groups Overview, Collection Logs, Collected Contents, AI
  Evaluation, Report, and Email Delivery for the selected `run_id`.
- AI Evaluation lists every candidate/result returned by the run-detail API
  and opens a per-evaluation detail view with business input, structured
  output, limited-context or redacted trace information, and role-safe debug
  visibility.
- Completed the remaining Phase 20E backlink: report lead rows with `run_id`
  expose `运行详情`, old/no-run rows show `上下文有限`, and the report lead
  drawer stays above Run Detail when opened from Run Detail's Report tab.
- Preserved CR-048/CR-049: Report Center still has no first-level global lead
  table, lead-state filtering remains drawer-local, and delivery history stays
  a scoped secondary drawer.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or phase_19c or phase_19d or phase_20b or phase_20c or phase_20d or phase_20e or cr048 or cr049"`
- Result: 13 passed, 292 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_20e_report_leads_backlink_to_run_detail"`
- Result: 1 passed, 304 deselected, 1 warning.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed in the final check.
- `uv run python scripts/check_docs.py`
- Result before final documentation update: PASS docs consistency.
- Browser acceptance on the isolated local service:
  - administrator and normal user at 1440x900, 1024x768, and 390x844 could
    log in, open Run Center, open run `#1` details, see final collection count
    `已采集 2`, see AI progress `2 / 2`, switch through the six Run Detail
    sections, and open per-evaluation detail.
  - normal-user detail stayed business-safe and did not show administrator
    debug trace text; neither role saw API keys, authorization headers,
    cookies, SMTP passwords, proxy credentials, profile paths, server-local
    paths, or raw unredacted model responses.
  - Run Detail's Report tab opened report `#1` leads; the lead drawer showed
    report scope and a clickable `运行详情` backlink; clicking it closed the
    lead drawer and returned to originating run `#1`.
  - The final overlay check confirmed `#report_leads_drawer.drawer.active`
    has a higher z-index than `#run_detail_drawer`, so the backlink is
    actually clickable when opened from inside Run Detail.
  - Report Center still did not render `leads_table` as first-level page
    content and the checked viewports had no page-level horizontal overflow.

## 2026-06-18 - Phase 20C Run Detail And AI Evaluation API

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added scoped run-detail API output for lifecycle overview, crawler logs,
  collected content, paginated/filterable AI evaluations, reports, and email
  delivery links by `run_id`.
- Added per-evaluation detail API output with role-safe trace fields: normal
  users receive business-safe input/output summaries for their own runs only,
  while administrators receive redacted debug snapshots.
- AI evaluation list filters now cover status, risk, platform, source keyword,
  and title with pagination metadata.
- API output removes or redacts raw responses, API keys, authorization headers,
  cookies, SMTP passwords, proxy credentials, profile paths, server-local
  paths, and sensitive diagnostic labels. Historical evaluations without trace
  rows remain explicit limited-context.

Verification:

- `python -m py_compile api/monitoring/database.py api/routers/monitor.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_20c or phase_20b"`
- Result: 4 passed, 298 deselected, 3 warnings.

## 2026-06-18 - Phase 20B AI Evaluation Trace Persistence

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added the `ai_evaluation_traces` schema and migration path with indexes for
  run/content, evaluation, and status/created-time lookup.
- New successful, failed, and fallback AI evaluations persist redacted/capped
  trace snapshots with business input, prompt/request, provider/model,
  structured output, redacted response, fallback/error detail, duration, and
  timestamps.
- `ai_trace_retention_days` is now an administrator runtime setting with a
  30-day default, monitor YAML mapping, doctor retention visibility, and a
  trace-only cleanup helper.
- Old evaluations without trace snapshots return explicit limited-context
  state. Trace write failures and retention cleanup do not block
  `ai_evaluations`, report generation, terminal run finalization, or email
  delivery semantics.
- Trace storage redacts API keys, authorization headers, cookies, proxy
  credentials, profile/server-local paths, and oversized prompt/request/
  response/comment snapshots include truncation metadata.

Verification:

- `python -m py_compile api/monitoring/ai.py api/monitoring/database.py api/monitoring/doctor.py api/monitoring/runner.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_20b or phase_2_runtime_settings_storage_validation_and_environment_locks or phase_2_runtime_settings_api_is_admin_only or phase_7_1_ai_invalid_json_exception_and_timeout_fallback_to_pending_review or phase_19c or phase_19b"`
- Result: 8 passed, 293 deselected, 3 warnings.

## 2026-06-18 - Phase 19D Run Center Frontend Progress Display And Polling

Environment: local worktree `E:\myproject\MediaCrawler`, plus an isolated
local FastAPI service on `http://127.0.0.1:19219/monitor` using
`.codex_tmp\phase19d_browser` as temporary validation data.

Result:

- Implemented Run Center silent polling for visible active runs, with polling
  stopped when visible rows no longer contain `running` status or when the
  user leaves Run Center.
- The Run Center row now displays provisional collection progress and active
  AI evaluation progress from `collection_progress` / `ai_progress` without
  replacing final `raw_contents`, `new_contents`, suspected-negative,
  high-risk, manual-review, or unevaluated summary semantics.
- Status rendering now covers running collection, AI evaluation, report
  generation, email sending, timeout, cancelled, interrupted, skipped,
  partial-failed, failed, and completed states. User-facing run status labels
  now match the accepted Run Center terms: `已完成`, `运行超时`, `已取消`, and
  `执行中断`.
- Stop, log, lead, archive, and restore actions remain reachable while
  progress values refresh. Normal users keep own-run scope and do not see
  administrator archive/restore controls.

Verification:

- `python -m py_compile api/monitoring/database.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19d or phase_15b or phase_19b or phase_19c"`
- Result: 5 passed, 293 deselected, 1 warning.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- Browser acceptance on the isolated local service:
  - administrator at 1440x900, 1024x768, and 390x844: Run Center displayed
    active provisional collection progress, AI `evaluated/total` progress,
    terminal states, and `查看日志` / `查看线索` / `归档` actions with no page
    horizontal overflow, no tiny collapsed buttons, and table overflow kept
    inside the table scroller.
  - normal user at 1440x900, 1024x768, and 390x844: navigation exposed only
    `总览`, `舆情监控`, `运行中心`, and `报告中心`; Run Center showed only the
    normal user's scoped runs; `归档`/`恢复` administrator controls were hidden;
    `查看日志` and `查看线索` stayed reachable with no page horizontal overflow.

## 2026-06-18 - Phase 19C AI Evaluation Progress Updates

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Implemented AI evaluation progress snapshots in `crawl_runs.summary` without
  adding a separate progress model.
- Active AI evaluation now updates `ai_progress` with total candidates,
  evaluated items, successful evaluations, failed/fallback evaluations,
  manual-review count, suspected-negative count, high-risk count, unresolved
  items, and a final marker.
- AI provider exceptions still fall back to `pending_review` / manual review,
  and report generation remains possible from the fallback state.
- Final AI progress is protected from stale or repeated running-progress
  writes, and terminal runs ignore later progress writes.
- Timeout/partial-failure AI finalization summaries now use the same visible
  progress fields for final manual-review fallback state.

Verification:

- `python -m py_compile api/monitoring/runner.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19c or phase_7_1_ai_invalid_json_exception_and_timeout_fallback_to_pending_review or phase_7_2_timeout_finalization_creates_pending_review_fallback_rows"`
- Result: 3 passed, 293 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or phase_19c or run_platform_retries_transient_crawler_failure or phase_2_run_platform_uses_settings_for_retry_and_deadline or run_platform_attaches_bound_proxy_summary or run_platform_does_not_retry_login_required_error"`
- Result: 6 passed, 290 deselected, 1 warning.

## 2026-06-18 - Phase 19B Run Center Progress Data Layer

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Implemented provisional collection progress in `crawl_runs.summary` using
  the existing Phase 7.1 lifecycle/progress fields instead of adding a new
  progress table or conflicting model.
- Running crawler attempts now update safe collection snapshots from crawler
  output files while preserving the existing subprocess, timeout, stop, retry,
  log-redaction, and resource-lock flow.
- Missing output, empty files, partially written JSON, malformed JSON, and
  partially valid JSONL are tolerated; readable records can contribute to
  provisional progress while malformed fragments are counted as malformed
  progress evidence.
- Final ingestion counts remain the existing `raw_contents`,
  `filtered_contents`, `excluded_contents`, and `new_contents` values and are
  not replaced by provisional output counts.
- Run-list reads now expose customer-safe `collection_progress`,
  `progress_message`, `progress_updated_at`, and `ai_progress` fields for the
  later Phase 19D frontend display.

Verification:

- `python -m py_compile api/monitoring/runner.py api/monitoring/database.py api/routers/monitor.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_19b or run_platform_retries_transient_crawler_failure or phase_2_run_platform_uses_settings_for_retry_and_deadline or run_platform_attaches_bound_proxy_summary or run_platform_does_not_retry_login_required_error"`
- Result: 5 passed, 290 deselected, 1 warning.

## 2026-06-18 - Phase 17.1C And Phase 17.2B-C Email Explanation And Guardrails

Environment: local worktree `E:\myproject\MediaCrawler`, browser acceptance
against the running `/monitor` console at `http://127.0.0.1:8765/monitor`.

Result:

- Completed the Phase 17.1C operator-facing recipient explanation surfaces:
  task report settings, Mail Configuration, preflight output, and delivery
  history now explain that task recipients win, global default recipients are
  fallback-only, and the SMTP sender is not a recipient.
- Completed Phase 17.2B template-body guardrails: new custom HTML templates
  cannot be saved unless they contain `{report_html}` or `{report_body}`, and
  preview metadata reports whether the required generated-report placeholder is
  present.
- Completed Phase 17.2C preset-style direction: the mail-template drawer offers
  administrator style presets (`standard`, `compact`, `formal`, and
  `custom/history`) that preserve the system-generated report body while
  keeping historical free-form templates readable.
- Preserved legacy-template compatibility: old templates that lack the body
  placeholder remain readable, and report-email rendering appends the generated
  report body during preview/send so a historical custom wrapper cannot
  silently drop the report content.
- Delivery history now exposes send-time template provenance, including whether
  the delivery used a task-bound template, the active template at send time, the
  system default body, or historical limited-context metadata.
- Rechecked the CR-048 Report Center information architecture after the user's
  risk-filter placement feedback: the first-level Report Center toolbar shows
  only `律所`, `平台`, `开始日期`, `结束日期`, and `报告范围`; `线索状态` / risk
  filtering is inside the scoped lead drawer and filters only the selected
  report or selected run lead scope.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17_1c_17_2bc or phase_17_2_email_template_body_guardrails or job_preflight_uses_bound_ai_profile_and_email_template or email_template_preview or active_email_template or report_email_preview_reuses_active_email_template or job_bound_email_template or phase_17b_report_center_delivery_history_frontend_hooks or cr049"`
- Result: 11 passed, 283 deselected, 1 warning.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- `uv run python -m py_compile api\monitoring\database.py api\monitoring\mailer.py api\monitoring\preflight.py tests\test_monitoring_mvp.py`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 2 inline/module script blocks parsed in the final check.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr048 or cr049 or phase_15b or phase_17b_report_center_delivery_history_frontend_hooks or phase_18b_report_center_task_grouping_frontend_hooks or monitor_page_uses_tob_information_architecture"`
- Result: 6 passed, 288 deselected, 1 warning after restoring the report-step
  helper text that says email misconfiguration does not block collection and
  report generation.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency after the final documentation update.
- Browser acceptance:
  - Report Center first-level filters were `律所`, `平台`, `开始日期`, `结束日期`,
    and `报告范围`; there was no first-level `风险` / `线索状态` filter and no
    first-level lead-detail or delivery-history panel.
  - The `report_leads_drawer` existed and contained the drawer-local
    `线索状态` filter with `高风险`, `疑似负面`, `待人工复核`, `不相关`,
    `已评估无风险`, and `未评估/上下文有限` options.
  - Mail Configuration and task report settings showed recipient-precedence
    wording; Mail Templates showed the sample-data preview note and
    body-placeholder guardrail.
  - The new-template drawer defaulted to the standard preset, retained
    `{report_html}` in the generated HTML, and exposed the preset options
    `标准日报`, `紧凑摘要`, `正式简报`, and `自定义 / 历史模板`.
  - Report delivery-history drawer opened from the report email-status action;
    the current browser data set had no delivery attempts for the selected
    report, so send-time template row rendering was covered by automated static
    and unit tests rather than a live row in that browser check.

Limitations:

- No real SMTP send was performed. The verification stayed within mocked or
  local non-sending paths.
- Full CR-034 / Phase 20 run detail, AI trace persistence, and per-evaluation
  debug evidence remain outside this goal.

## 2026-06-18 - Phase 17.1D Orphan Email Evidence Dry-Run

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added `scripts/review_orphan_email_evidence.py` as a read-only dry-run
  helper for historical email delivery evidence. It supports `--database`,
  `--delivery-log-id`, `--job-id`, `--report-id`, `--artifact-root`, and
  `--json`.
- The helper reports delivery-log id, `job_id`, `report_id`, send type/status,
  sent/created time, job/report/run existence, artifact existence,
  classification, `mode=dry_run`, `mutations_attempted=0`, and the required
  backup/approval/rollback gates before any future mutation.
- Documented the observed CR-036 historical evidence for delivery-log rows `60`
  and `81`: `job_id=9686` / `run_id=8380` / `report_id=3959` and
  `job_id=9759` / `run_id=8447` / `report_id=3998`, including exported `.eml`
  references, attachment names, missing job/run/report rows, and the default
  preserve policy.
- Updated the deployment docs/runbook so orphan evidence review remains
  read-only and any later delete, annotation, repair, or migration requires a
  database backup, artifact/email backup, explicit operator approval, and a
  rollback plan.

Verification:

- `uv run python scripts\review_orphan_email_evidence.py --job-id 9686`
- Result: PASS dry-run. It found `delivery_log_id=60`, `job_id=9686`,
  `report_id=3959`, `classification=orphan_delivery_log`,
  `secondary=detached_report_artifacts, limited_context`,
  `artifacts_existing=3/3`, and `mutations_attempted=0`.
- `uv run python scripts\review_orphan_email_evidence.py --job-id 9759`
- Result: PASS dry-run. It found `delivery_log_id=81`, `job_id=9759`,
  `report_id=3998`, `classification=orphan_delivery_log`,
  `secondary=detached_report_artifacts, limited_context`,
  `artifacts_existing=3/3`, and `mutations_attempted=0`.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17_1d or phase_17b_email_delivery_history_api_scope_and_safe_fields or phase_17b_report_center_delivery_history_frontend_hooks or phase_18b_report_center_task_grouping_frontend_hooks"`
- Result: 4 passed, 288 deselected, 3 warnings.
- `uv run python -m py_compile scripts\review_orphan_email_evidence.py tests\test_monitoring_mvp.py`
- Result: PASS.
- `uv run python scripts\check_docs.py`
- Result: PASS docs consistency.

Limitations:

- No historical database row or artifact mutation was performed. Any future
  cleanup/annotation remains a separate operator-approved repair task.
- Phase 17.1C operator-facing recipient-source explanation and Phase 17.2B-C
  template guardrails remain open for the next email/template batch.

## 2026-06-17 - CR-048/CR-049 Report And Mail Information Architecture

Environment: local worktree `E:\myproject\MediaCrawler`, browser acceptance
against the running `/monitor` console at `http://127.0.0.1:8765/monitor`.

Follow-up acceptance tuning:

- User review found the first-level Report Center `风险/线索状态` style filter
  still made the page read like a lead workbench after lead detail moved into a
  drawer.
- Adjusted the information architecture so the first-level Report Center
  toolbar contains only report dimensions: `律所`, `平台`, date range, and
  `报告范围`.
- Moved `线索状态` into the lead drawer as drawer-local filtering. It now
  filters only the selected report or selected run lead scope and no longer
  appears as a first-level Report Center filter.
- Browser acceptance after reload and visible navigation through the Operations
  Home `查看报告` shortcut showed Report Center active with labels `律所`,
  `平台`, `开始日期`, `结束日期`, `报告范围`; no first-level `report_risk`,
  `lead_status_filter`, `leads_table`, or `email_delivery_history`; 3 report
  row `查看线索` buttons; and the lead drawer for report `#3772` containing
  drawer-local `线索状态` plus `筛选线索` with a selected-report scope hint.
- Browser console error log remained empty after the follow-up checks.
- Follow-up checks passed:
  `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr048 or cr049 or phase_15b or phase_17b_report_center_delivery_history_frontend_hooks or phase_18b_report_center_task_grouping_frontend_hooks or monitor_page_uses_tob_information_architecture"`
  returned 6 passed, 285 deselected, 1 warning; `node --check
  api/webui/monitor/monitor.js` passed; inline monitor page script parse passed
  with 1 script block.

Result:

- Implemented the focused CR-048/CR-049 frontend information-architecture
  batch without changing backend APIs, database schema, SMTP delivery logic,
  permissions, crawler behavior, or AI trace storage.
- Report Center is now report-first: the first-level lead detail panel and
  `leads_table` are removed, the process-draft preview hint card is removed,
  and report rows expose an explicit `查看线索` action separate from preview.
- Report lead details open in a drawer with selected-report title, scope,
  count, applied filter summary, and empty states. The drawer says the content
  is limited to the selected report and is not a global lead workbench.
- Run Center rows now expose `查看线索`; clicking a run row opens the same
  drawer with run-scoped title/scope/hint so run-generated leads have a Run
  Center entry before any future full Run Detail implementation.
- Report Center first-level filter wording now stays on report dimensions. The
  limit field is `报告范围`; the former `全部报告和线索` wording is removed because
  lead details are no longer first-level page content, and lead status
  filtering is drawer-local.
- Report Center delivery history is no longer a first-level panel. Clicking a
  report email-status button or `更多 > 查看交付历史` opens a scoped drawer with
  report scope, record count, refresh action, latest status, and SMTP
  acceptance wording.
- Mail Configuration no longer shows the large first-level
  `SMTP 与发送默认值` or full-width real-email status panels. Edit, test,
  refresh/status, delivery-status navigation, and the single real-email switch
  are in the page-level action bar, with compact summary metrics underneath.
- Preserved report preview, downloads, resend, report grouping, delivery
  history, CR-043 real-email confirmation behavior, and CR-044 SMTP
  acceptance wording.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "leads_api_can_scope_items_to_selected_run or leads_api_can_scope_items_to_selected_report or cr048 or cr049 or phase_15b or phase_17b_report_center_delivery_history_frontend_hooks or monitor_page_uses_tob_information_architecture"`
- Result: 7 passed, 284 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "leads_api_can_scope_items_to_selected_run or leads_api_can_scope_items_to_selected_report or cr048 or cr049 or phase_15b or phase_17b_report_center_delivery_history_frontend_hooks or monitor_page_uses_tob_information_architecture or phase_18b"`
- Result: 8 passed, 283 deselected, 1 warning.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS, 1 inline script block parsed.
- Browser acceptance:
  - refreshed `/monitor` and confirmed Report Center first-level filters
    contain `报告范围` and do not contain a first-level `线索状态`/`风险` filter,
    `leads_table`, `email_delivery_history`, `data-report-delivery-panel`, or
    `report-hint`;
  - after loading reports, Report Center showed 3 `查看线索` buttons and 3
    email-status buttons;
  - clicking report `查看线索` opened `报告线索明细 #3772`; the drawer scope was
    `报告 #3772 的线索明细` and the hint said the list is limited to the current
    report;
  - clicking report email status opened `邮件交付历史 #3772`; the drawer scope
    was `报告 ID 3772 的邮件交付历史` and the page did not render delivery
    history in the first-level Report Center section;
  - Run Center showed 100 visible `查看线索` row actions in the current view;
    clicking the first opened `运行 #9047 线索明细` with a run-scoped hint;
  - mobile navigation at `390x844` opened Report Center and Mail
    Configuration; both had no horizontal overflow, no first-level lead or
    delivery-history panel, and no old SMTP/defaults or real-email status
    panel;
  - browser console error log was empty after the checks.

Limitations:

- Full Phase 20 Run Detail, AI trace persistence, per-evaluation debug detail,
  and run-detail deep links remain future CR-034 / Phase 20 work.
- Full Phase 21 page-level visual refinement remains open outside this focused
  CR-048/CR-049 batch.

## 2026-06-17 - CR-045/Phase 7.2C-D AI Relevance Hardening

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Implemented the Phase 7.2C-D relevance hardening without adding database
  schema fields or role-visible debug fields.
- Updated the default AI prompt so `source_keyword` is explicitly recall
  provenance only and cannot by itself prove target-law-firm relatedness.
- Added post-provider AI normalization that forces model output back to
  unrelated/irrelevant when title, description, author, and actually collected
  comments do not contain the target law firm or accepted aliases.
- Preserved comment evidence support only when comments are collected and
  passed into the AI payload.
- Added calibration coverage for noisy-positive keyword-only output, broad
  refund/legal noise, homonym/geography-only `海安` mentions, title-based
  target evidence, and comment-only target evidence.
- Verified the report/lead filtering path: keyword-only and geography-only
  fixtures stay out of suspected-negative/high-risk buckets, while true title
  and collected-comment target evidence remains eligible for suspected-negative
  or high-risk classification.

Verification:

- `uv run python -m py_compile api/monitoring/ai.py tests/test_monitoring_mvp.py`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7_2 or cr050 or ai_evaluation_payload_includes_content_and_comment_context"`
- Result: 9 passed, 279 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7 or cr050 or ai_config or ai_rule or evaluate_content or report_center_risk_filters"`
- Result: 19 passed, 269 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-17 - Open TODO Test Gate Hardening

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Hardened planned verification gates for the current open TODO queue without
  implementing product code.
- Added negative-test expectations for CR-045/Phase 7.2C-D so
  `source_keyword`-only evidence cannot become a target-related negative lead
  even when a mocked model emits a noisy positive.
- Added CR-047/Phase 5.1 account-environment tripwires for confirmed proxy
  override policy, hidden process-default fallback, and fail-closed incomplete
  browser-environment values.
- Added Phase 17.1D dry-run/no-op evidence requirements so orphan email review
  cannot mutate delivery logs, report artifacts, or historical rows without
  backup and explicit operator approval.
- Added Phase 19 lifecycle-progress tests for disappeared crawler subprocesses,
  repeated finalization, and late progress writes after terminal state.
- Added Phase 20 traceability tests proving trace write failure and retention
  cleanup cannot block finalization or mutate `ai_evaluations`, reports, or
  delivery logs.
- Added CR-048/CR-049 frontend tripwires for unlabeled Report Center lead
  tables and duplicated Mail Configuration edit/test controls.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-17 - CR-048 Report Center Lead Detail IA Documentation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded CR-048 as an accepted Report Center information-architecture
  optimization.
- Clarified that Report Center remains report-first: lead detail must be
  explicitly scoped to selected report, selected report group, originating run,
  or visibly labeled current-filter aggregate.
- Clarified placement: Run Center / Run Detail is the primary operational home
  for run-scoped leads and AI evaluation records, while Report Center keeps
  report-scoped "view leads" shortcuts.
- Added task, product, UI, formal-console plan, test-plan, decision, and
  traceability coverage for explicit "view leads", scope/count/filter labels,
  filtered-aggregate labeling, and empty-state clarity.
- Kept global lead workbench and per-AI-evaluation trace/debug detail outside
  CR-048; those remain separate future capability or CR-034 / Phase 20 scope.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency after the additional Run Center versus Report
  Center placement clarification.

## 2026-06-17 - CR-049 Mail Configuration And Delivery History IA Documentation

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded CR-049 as an accepted frontend information-architecture
  optimization for Mail Configuration and Report Center delivery history.
- Clarified that Mail Configuration should use one page-level action bar for
  edit configuration, send test mail, refresh/status, delivery-status
  navigation, and compact real-email state.
- Clarified that SMTP/defaults summaries should not repeat edit/test buttons,
  and that the CR-043 real-email switch remains a single compact
  administrator safety control with explicit confirmation before enabling.
- Clarified that Report Center delivery history is scoped secondary detail
  opened from a report row/status action and should not dominate the initial
  report archive layout.
- Preserved CR-043/CR-044 safety behavior, SMTP acceptance wording, delivery
  history, resend, and no-real-SMTP automated verification boundaries.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-17 - CR-050 Report Center Lead Status Filter Precision

Environment: local worktree
`E:\myproject\MediaCrawler-worktrees\cr045-phase-7-2-ab`.

Result:

- Fixed the Report Center/leads API risk filter semantics so `高风险` and
  `疑似负面` are exact filters instead of overlapping negative buckets.
- Added exact `suspected_negative_count` as a derived summary field for report
  filtering while preserving the existing `negative_count` total-negative
  summary for report/template compatibility.
- Preserved pending-review, unrelated, evaluated no-risk, and
  unevaluated/limited-context filter separation.
- Did not change crawler behavior, AI relevance calibration, SMTP delivery,
  permissions, or historical runtime data.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr050 or phase_7_2_lead_filters"`
- Result: 2 passed, 282 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7_2 or cr050 or ai or leads or report"`
- Result: 110 passed, 174 deselected, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `uv run python -m py_compile api/monitoring/database.py api/monitoring/reporting.py api/routers/monitor.py tests/test_monitoring_mvp.py`
- Result: PASS.

## 2026-06-17 - CR-045/Phase 7.2A-B Unevaluated Lead Safety

Environment: local worktree
`E:\myproject\MediaCrawler-worktrees\cr045-phase-7-2-ab`.

Result:

- Implemented explicit lead states for missing AI evaluation rows so they are
  exposed as unevaluated or limited-context instead of no-risk.
- Updated report/run summary counts, report filters, leads API filters, report
  generation, Report Center status rendering, and Run Center count display so
  pending review, unrelated, evaluated no-risk, suspected negative, high-risk,
  and unevaluated/limited-context states are not collapsed together.
- Kept `pending_review` as a separate bucket even when fallback or historical
  rows carry related/negative flags, so pending-review rows do not inflate
  suspected-negative or high-risk counts.
- Updated active timeout and partial-failure finalization to create
  `pending_review` fallback rows for known unresolved AI candidate IDs before
  report generation when safe.
- Preserved idempotent fallback behavior and did not add any historical repair
  workflow or mutate historical run `8317`.
- Added customer-safe `ai_finalization_fallback` summary evidence for known
  unresolved candidates, fallback rows created, remaining unresolved items, and
  limited-context rows left unchanged.
- Added a small platform-status robustness fallback for uninitialized monitor
  database reads in filesystem-only tests; initialized runtime behavior still
  uses active social-account profiles.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7_2 or ai or leads or report"`
- Result: 109 passed, 173 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 282 passed, 3 warnings.
- Rebase refresh on latest `origin/main` after CR-038:
  `uv run python scripts/check_docs.py` passed,
  `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7_2 or ai or leads or report"`
  passed with 109 passed, 174 deselected, 3 warnings, and
  `uv run python -m pytest tests/test_monitoring_mvp.py` passed with 283
  passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check for `api/monitor_web/index.html`
- Result: PASS.
- `python -m py_compile api/monitoring/database.py api/monitoring/reporting.py api/monitoring/runner.py api/monitoring/platform_status.py api/routers/monitor.py tests/test_monitoring_mvp.py`
- Result: PASS.

Remaining:

- Phase 7.2C-D relevance hardening and calibration fixtures remain open.
- Phase 20 AI traceability remains accepted but not implemented.

## 2026-06-17 - CR-038 Sticky Drawer Close Accessibility

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr038-sticky-drawer-close`, branch
`codex/cr038-sticky-drawer-close`.

Result:

- Implemented CR-038 as a frontend-only accessibility follow-up before Phase
  21, without changing backend APIs, database schema, permissions, crawler,
  AI, SMTP, scheduler, deployment behavior, navigation, page density, or
  workflows.
- Shared drawer/modal headers are sticky inside scrollable drawers, with solid
  white background, border/shadow separation, and stable close-button sizing so
  content does not bleed through while scrolling.
- After manual acceptance review found that scrolled content could still peek
  through the drawer's top padding above the sticky header, the drawer top
  padding was moved into the header itself so the sticky header fully covers the
  top edge while content scrolls underneath.
- Existing backdrop click-to-close, Escape close through the shared overlay
  handler, and bottom save/close action bars are preserved.
- Added targeted frontend hook coverage for the required drawer surfaces and
  sticky-header/sticky-footer layering rules.

Verification:

- `uv run python scripts/check_docs.py`: PASS.
- `node --check api/webui/monitor/monitor.js`: PASS.
- Inline script parse check for `api/monitor_web/index.html`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr038 or phase_11c or phase_11d"`:
  3 passed, 277 deselected, 1 warning.
- Browser sweep on the local CR-038 service checked task edit, account, proxy,
  AI profile, mail config, mail template, run log, and report preview drawers
  at 1440x900, 1024x768, and 390x844. For each viewport, sticky close controls
  stayed visible/clickable after scrolling, visible footer controls remained
  reachable, backdrop close and Escape close still worked, page horizontal
  overflow stayed at 0, and app-side console error logs were empty.
- Follow-up geometry check for task edit and account drawers at 1440x900,
  1024x768, and 390x844 confirmed the sticky header reaches the drawer top
  edge after scrolling, the top probe hits the header rather than scrolled
  content, close controls remain visible, and horizontal page overflow remains
  0.

## 2026-06-17 - Current TODO Cross-Validation And Queue Refinement

Environment: `E:\myproject\MediaCrawler`, branch `main`.

Result:

- Reviewed the current open TODO queue with the `plan-cross-validation` flow
  and a read-only Claude review over project documents.
- Confirmed no global roadmap blocker was found, but adjusted documentation so
  CR-045/Phase 7.2 is clearly the first ordinary implementation priority
  before broad-keyword AI labels are relied on in pilot use.
- Repositioned CR-035/Phase 7.1D as a conditional operator-approved historical
  remediation path rather than a normal feature batch.
- Added CR-038 sticky drawer close accessibility to the active follow-up queue.
- Added a Phase 5.1 prerequisite to confirm the fixed-environment proxy
  override policy before account browser-environment code implementation.
- Clarified that Phase 21 layout collapse is a hard verification risk, not a
  confirmed current production breakage claim.

Verification:

- Read-only Claude review reported no global blocking findings.
- Follow-up read-only Claude review after queue refinements reported no
  blocking findings and no material findings.
- `uv run python scripts/check_docs.py`
- Result: PASS.

## 2026-06-17 - CR-047 Account Browser Environment Consistency Documentation

Environment: `E:\myproject\MediaCrawler`, branch `main`.

Result:

- Restored the locally drafted account browser-environment consistency
  requirement into current mainline documents under the new CR-047 number.
- Kept historical CR-042 as the rejected real-email validation-window design
  superseded by CR-043.
- Added Phase 5.1 tasks, traceability, test-plan coverage, data-model and
  migration notes, account-environment rules, product requirements, and
  decision records for the accepted-but-not-implemented CR-047 scope.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS.

## 2026-06-17 - CR-046 Platform Account Avatar Safe Cache Display

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Added server-side account-avatar cache helper and administrator-only avatar
  endpoint.
- The social-account API now returns same-origin avatar URLs instead of signed
  external platform image URLs.
- Signed avatar query parameters remain out of frontend API responses.
- Normal users cannot access platform-account avatar images.
- Traversal attempts against cached-avatar paths are rejected.
- Existing profile path and cookie hiding behavior remains covered.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "avatar or social_account_pool_redacts_signed_avatar_urls or social_account_api_view_hides_profile_paths"`
- Result: 4 passed, 275 deselected, 3 warnings.
- `python -m py_compile api/monitoring/avatar_cache.py api/monitoring/database.py api/routers/monitor.py tests/test_monitoring_mvp.py`
- Result: PASS.
- Browser verification on `http://localhost:8080/monitor`: the Platform
  Accounts avatar loaded from
  `/api/monitor/social-accounts/1/avatar` with `naturalWidth=100` and
  `naturalHeight=100`.
- Full monitoring regression suite:
  `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 279 passed, 3 warnings.

## 2026-06-17 - CR-044 Mail Test Recipient Coverage And SMTP Acceptance Clarity

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Investigated the operator report that Mail Configuration test mail showed
  SMTP submission success but recipient-side mail was not found.
- Confirmed the previous test-mail path used only the first configured global
  default recipient when no explicit test target was supplied.
- Updated test-mail recipient resolution so one test message is addressed to
  all configured global default recipients.
- Updated the API response and frontend test console to show submitted
  recipient count/source while preserving the warning that SMTP acceptance is
  not recipient inbox proof.
- Kept automated verification on mocked SMTP only; no real external email was
  sent by the test run.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr044 or
  cr043_mail_test_submits_all_default_recipients or
  cr043_admin_frontend_real_email_toggle_controls_mail_test or
  phase_17_1_smtp_refused_recipients_fail_delivery or
  phase_17_1_manual_resend_and_mail_test_are_blocked_without_opt_in"`: 4
  passed, 273 deselected, 3 warnings.

## 2026-06-17 - CR-043 Runtime Restart And Superseded Lock Regression Check

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`, local service
`http://127.0.0.1:8080/monitor`.

Result:

- Investigated an operator-visible error where clicking the Mail Configuration
  real-email switch returned
  `real_email_delivery is locked by deployment configuration`.
- Confirmed the running 8080 service was still serving the superseded CR-042
  deployment-gated validation-window code even though the current worktree code
  already implemented CR-043.
- Restarted the local 8080 service from the current worktree while preserving
  the active server-like data/profile directories:
  `data_server_like` and `browser_data_server_like`.
- Verified the live API now reports `real_email_delivery` as source
  `database`, `is_locked=false`, `apply_scope=immediate`, and no YAML path or
  deployment lock reason.
- Verified administrator API updates can turn the switch off and back on
  successfully. No mail-test, manual resend, automatic delivery, platform
  crawl, or AI provider call was triggered during this verification.
- Added a regression test proving superseded CR-042 environment variables and
  stale `system_settings.is_locked=1/source=environment` rows do not lock the
  CR-043 `real_email_delivery` switch.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k
  "cr043_real_email_toggle_ignores_superseded_deployment_locks or
  cr043_real_email_runtime_setting_is_admin_editable"`: 2 passed, 274
  deselected, 3 warnings.
- Live 8080 API check after restart: administrator login succeeded;
  `/api/monitor/runtime-settings` returned `real_email_delivery.is_locked=false`;
  `PUT /api/monitor/runtime-settings` succeeded for both `false` and `true`;
  `/api/monitor/email-validation-window` mapped to the same one-switch state
  and showed two configured fallback recipients.
- Browser refresh on `/monitor` showed the Mail Configuration switch as
  enabled and editable, with no locked-state response.

## 2026-06-17 - CR-043 Administrator Frontend Real Email Send Toggle

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Replaced the rejected CR-042 validation-window product direction with the
  user-confirmed CR-043 one-switch model.
- Mail Configuration exposes one administrator real email send switch backed
  by the persisted `real_email_delivery` runtime setting.
- Removed the user-facing deployment frontend gate, scheduler-exclusion gate,
  expiry, and single-use validation-window workflow from the accepted daily
  operation model.
- Kept compatibility responses for older internal names, but they now report
  the same single switch state.
- Runtime Strategy omits the Email group so the same real-email control is not
  presented in two places.
- Real SMTP remains default-off. Mail test, manual resend, and automatic
  report delivery follow the same switch, and automated verification must use
  mocked SMTP/tripwire protection rather than sending real external mail.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr043 or
  phase_17_1 or email_test_results or runtime_settings"`: 14 passed, 261
  deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 275 passed, 3
  warnings.
- `uv run python scripts/check_docs.py`: PASS.
- `python -m py_compile api\monitoring\settings.py api\monitoring\mailer.py
  api\routers\monitor.py tests\test_monitoring_mvp.py`: PASS.
- `node --check api\webui\monitor\monitor.js`: PASS.
- Inline script parse check for `api\monitor_web\index.html`: PASS.
- `git diff --check`: no whitespace errors; Git reported expected
  LF-to-CRLF working-copy warnings on Windows.

## 2026-06-17 - CR-041 Minimum Usable Pilot Gate Closure

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Closed CR-041 Pilot Gate C for the current first-usable-pilot standard.
- Verified the real Douyin server-like workflow evidence for `run_id=3` /
  `report_id=3`: server-side account/profile path, 14 raw/new contents,
  report generation, and 14 AI fallback `pending_review` items.
- Verified controlled real SMTP submission through a frontend-enabled
  administrator real-email path with `delivery_log_id=6`, `report_id=3`,
  `send_type=manual_resend`, `trigger_source=manual_resend`, `status=sent`,
  and two effective recipients from `global_default_fallback`.
- The operator confirmed both approved recipients received the report email.
  This is recorded only as a redacted receipt reference; mailbox addresses,
  message content, SMTP secrets, and runtime paths are not stored in docs.
- The ignored local operator evidence file
  `data_server_like\pilot_gate_c_evidence.pending.json` was finalized to
  `schema_version=pilot_gate_c_v2`, `status=passed`, and
  `recipient_receipt_confirmed=true`.

Verification:

- `uv run python scripts/pilot_gate_c_evidence.py --check
  data_server_like\pilot_gate_c_evidence.pending.json`: PASS.
- `uv run python scripts/check_docs.py`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 275 passed, 3
  warnings.
- Read-only Claude Code documentation-focused review inspected
  `docs/CURRENT_STATE.md`, `docs/TASKS.md`, `docs/TRACEABILITY.md`,
  `docs/CHANGE_REQUESTS.md`, and `docs/TEST_RESULTS.md` only. It reported no
  Blocking findings and no CR-041 Material findings, and confirmed the current
  documents consistently support CR-041 being Verified when the operator
  receipt-confirmation fact is accepted.

Remaining:

- CR-041 no longer blocks first usable pilot readiness. Phase 21, CR-038,
  Phase 19B-D, Phase 20, CR-037, Phase 7.1D historical run `8317`
  remediation, and Phase 17.1D orphan evidence operations remain separate
  follow-up work under their existing gates.

## 2026-06-17 - CR-042 Frontend Real Email Validation Window

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Implemented the user-confirmed frontend-operable real-email validation
  window as a Pilot Gate C usability bridge, not as a permanent ordinary
  toggle.
- Added read-only runtime visibility for `frontend_real_email_validation` /
  `MONITOR_ALLOW_FRONTEND_REAL_EMAIL_VALIDATION`.
- Added administrator-only API state/open/close endpoints for a time-limited
  single-use validation window.
- Opening the window now requires both deployment gates
  (`MONITOR_ALLOW_REAL_EMAIL_SEND=true` and
  `MONITOR_ALLOW_FRONTEND_REAL_EMAIL_VALIDATION=true`) and scheduler
  exclusion (`scheduler_disabled=true` / `MONITOR_DISABLE_SCHEDULER=true`).
- Mail-test and administrator manual-resend API paths require an open
  validation window before real SMTP is allowed. Normal-user resend remains
  non-sending through the default safety gate.
- A successful validation send marks the window used and closes it
  automatically; the frontend shows deployment-gate state, effective recipient
  source/count, expiry/single-use state, and the warning that SMTP acceptance
  is not recipient receipt.
- Delivery history now displays effective recipients and effective-recipient
  source, so global default-recipient fallback is visible to operators.

Verification:

- `python -m py_compile api\monitoring\settings.py api\monitoring\database.py api\monitoring\mailer.py api\monitoring\reporting.py api\routers\monitor.py`:
  PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr042"`:
  5 passed, 270 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "cr042 or phase_17_1 or phase_17b_report_center_delivery_history_frontend_hooks or monitor_page_uses_resource_modals_and_page_sections"`:
  10 passed, 265 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 275 passed, 3
  warnings.
- `uv run python scripts/check_docs.py`: PASS.
- `git diff --check`: no whitespace errors; Git reported expected LF-to-CRLF
  working-copy warnings on Windows.
- `uv run python scripts/pilot_gate_c_evidence.py --check
  data_server_like\pilot_gate_c_evidence.pending.json`: expected FAIL for the
  ignored local pending evidence draft, with only `status` not yet `passed` and
  `smtp_validation.recipient_receipt_confirmed` not yet true. This confirms the
  draft is ready for finalization after recipient-side receipt is confirmed,
  but cannot close CR-041 prematurely.
- Read-only Claude Code review found one real CR-042 safety issue: the open
  endpoint depended on frontend state for scheduler exclusion and did not
  independently reject direct API calls while scheduler delivery was active.
  The endpoint now checks the same deployment gate state as the frontend, and
  tests cover missing real-email gate, missing frontend gate, scheduler-active
  rejection, administrator-only access, normal-user non-sending resend, and
  single-use auto-disable.
- A second read-only Claude Code review after the fix reported no Blocking
  issues and no CR-041/CR-042-relevant Material issues. It confirmed direct API
  open now rejects missing real-email gate, missing frontend gate, or active
  scheduler; validation-window APIs are administrator-only; normal-user resend
  remains non-sending; administrator mail-test/manual-resend require an open
  window; successful validation use auto-disables the window; and CR-041
  remains incomplete until recipient receipt proof and passing evidence JSON.

Remaining:

- CR-041 Pilot Gate C still cannot close until at least one approved recipient
  confirms inbox/spam/quarantine receipt for the latest real SMTP validation
  attempt and the redacted `pilot_gate_c_v2` evidence JSON passes. The latest
  controlled validation-window attempt recorded `delivery_log_id=6`,
  `report_id=3`, `send_type=manual_resend`, `status=sent`, and two effective
  recipients from `global_default_fallback`; this proves SMTP submission was
  accepted, not recipient inbox delivery.

## 2026-06-17 - CR-041 SMTP Receipt Gate Tightening

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Real SMTP was enabled only for the validation window and disabled again
  afterward through deployment environment state.
- Manual resend for `report_id=3` produced delivery-log rows `id=3` and
  `id=4` with `send_type=manual_resend`, `trigger_source=manual_resend`,
  `effective_recipient_source=global_default_fallback`, two effective
  recipients, and `status=sent`.
- The operator reported that the email was not actually received. Therefore,
  the `sent` rows are treated as SMTP server acceptance evidence only and do
  not satisfy Pilot Gate C recipient-side receipt proof.
- Tightened Pilot Gate C evidence schema to `pilot_gate_c_v2` by requiring
  `smtp_validation.recipient_receipt_confirmed=true` and a redacted
  `recipient_receipt_reference`.
- Updated report-center frontend wording so `sent` displays as SMTP accepted
  and manual resend toast asks the operator to confirm inbox or spam receipt,
  instead of implying final delivery.
- Hardened SMTP result handling so `smtplib.send_message()` recipient-refusal
  results are treated as failed delivery instead of being recorded as `sent`.
  This distinguishes SMTP acceptance from explicit SMTP refusal, while still
  requiring separate recipient-side receipt confirmation for Pilot Gate C.
- Recorded CR-042 as `Needs Confirmation` for a future frontend-controlled,
  deployment-gated, administrator-only, time-limited real-email validation
  window. No CR-042 implementation was started.

Verification:

- `python -m py_compile scripts\pilot_gate_c_evidence.py tests\test_monitoring_mvp.py`:
  PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "pilot_gate_c_evidence or phase_17b_report_center_delivery_history_frontend_hooks"`:
  18 passed, 251 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17_1_smtp_refused_recipients_fail_delivery or phase_17_1_explicit_real_email_opt_in_reaches_mocked_smtp or phase_17_1_manual_resend_and_mail_test_are_blocked_without_opt_in"`:
  3 passed, 267 deselected, 1 warning.
- `uv run python scripts/pilot_gate_c_evidence.py --check docs/pilot_gate_c_evidence.example.json`:
  expected FAIL because the committed example is intentionally incomplete; it
  now also rejects missing recipient receipt confirmation.
- `uv run python scripts/check_docs.py`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 270 passed, 3
  warnings.
- Runtime state after validation was rechecked through the API:
  `real_email_delivery=false`, `scheduler_disabled=true`, both locked by
  environment configuration.
- Read-only Claude Code external review was run with a read-only prompt and no
  edit/write/database/email/crawler/AI/service permissions. It reported no
  Blocking findings and no CR-041-relevant Material findings. It confirmed
  CR-041 cannot close yet because recipient-side receipt confirmation and a
  passing `pilot_gate_c_v2` operator evidence JSON are still required.

Remaining:

- CR-041 Pilot Gate C still cannot close until an approved recipient confirms
  actual receipt and the redacted operator evidence JSON passes the checker.

## 2026-06-17 - CR-041 Pilot Gate C Evidence Checker

Environment: isolated worktree
`E:\myproject\MediaCrawler-worktrees\cr041-pilot-evidence`, branch
`codex/cr041-pilot-evidence`.

Result:

- Added `scripts/pilot_gate_c_evidence.py`, a default-safe checker for
  operator-filled Pilot Gate C real-workflow evidence.
- Added `docs/pilot_gate_c_evidence.example.json` as an incomplete redacted
  evidence template. The template is expected to fail validation until a real
  operator validation run fills it with redacted references.
- The checker only reads or writes the requested JSON file. It does not start
  services, crawl platforms, call AI providers, mutate databases, inspect or
  repair historical run `8317`, touch orphan email evidence, or send email.
- The checker rejects missing real-platform/SMTP/AI-fallback evidence,
  unchecked redaction surfaces, placeholders, secret-looking values, raw local
  paths, provider endpoints, proxy credentials, cookies, and sensitive evidence
  keys.
- Pilot Gate D boundary was rechecked from current docs: Phase 21, CR-038,
  Phase 19B-D, Phase 20, and CR-037 remain outside the first-pilot blocker set
  unless a later accepted P0 regression changes the boundary; historical run
  remediation and orphan evidence cleanup remain dry-run, backup, rollback,
  and explicit-operator-approval gated.
- CR-041 remains incomplete until real external platform login/crawl,
  explicit-opt-in real SMTP validation, real-run redaction evidence, and a
  passing operator-filled evidence JSON are available.

Verification:

- `python -m py_compile scripts\pilot_gate_c_evidence.py tests\test_monitoring_mvp.py`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "pilot_gate_c_evidence"`:
  17 passed, 249 deselected, 1 warning.
- `uv run python scripts\pilot_gate_c_evidence.py --write-template docs\pilot_gate_c_evidence.example.json`: PASS.
- `uv run python scripts\pilot_gate_c_evidence.py --check docs\pilot_gate_c_evidence.example.json`: expected FAIL because the committed template is intentionally incomplete.
- `uv run python scripts/check_docs.py`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 266 passed, 3
  warnings.
- `uv run python scripts/server_like_validation.py`: PASS. All 11 automated
  server-like checks returned `ok: true`.

External validation:

- Read-only Claude Code review was run with Read/Grep/Glob-only tool access
  and no edit/write/Bash/database/email/crawler/AI/service permissions.
- Initial review found no Blocking issues and one Material test-coverage
  finding for schema-version, placeholder, redaction-surface, and additional
  secret-pattern branches.
- Added the missing automated tests. Focused read-only recheck reported the
  Material finding resolved and no remaining Blocking, Material, or Polish
  findings for CR-041 evidence-checker coverage.

## 2026-06-17 - CR-041 Pre-Commit Verification Refresh

Environment: local worktree `E:\myproject\MediaCrawler`, branch
`codex/cr041-pilot-gate`.

Result:

- Refreshed the CR-041 automated evidence before committing the safety and
  lifecycle gate work.
- No real SMTP delivery, real platform crawl, real AI-provider call, runtime
  database mutation outside isolated tests, or historical run/evidence repair
  was performed.
- CR-041 remains incomplete only because the real external pilot checks still
  require operator credentials/session and explicit opt-in.

Verification:

- `python -m py_compile api\monitoring\settings.py api\monitoring\database.py api\monitoring\mailer.py api\monitoring\reporting.py api\monitoring\runner.py api\routers\monitor.py tests\conftest.py tests\test_monitoring_mvp.py`: PASS.
- `uv run python scripts/check_docs.py`: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 249 passed, 3
  warnings.
- `uv run python scripts/server_like_validation.py`: PASS. All 11 automated
  server-like checks returned `ok: true`.

## 2026-06-16 - CR-041 Pilot Gate C Automated Server-Like Validation

Environment: local worktree `E:\myproject\MediaCrawler`, branch
`codex/cr041-pilot-gate`.

Result:

- Ran the automated server-like validation script with isolated temporary data,
  production local-login fallback disabled, scheduler disabled, AI skipped, and
  server-side profile roots.
- The script verified service web UI reachability, administrator HTTP login,
  server QR/status login capability as the primary flow, local-window login
  blocked in production mode, same-platform accounts using separate
  `profile_key` paths, profile metadata survival across service restart,
  account/profile/proxy lock enforcement, no local Chrome dependency, and
  headless Chromium availability.
- This satisfies the automated/non-external portion of Pilot Gate C. It does
  not prove real platform QR scanning, real platform crawling, real AI-provider
  behavior, or real SMTP delivery with operator credentials.

Verification:

- `uv run python scripts/server_like_validation.py`: PASS. All 11 checks
  returned `ok: true`.

Remaining:

- CR-041 still cannot be marked complete until an operator provides or confirms
  a usable real platform account/session for at least one platform crawl and an
  explicit real SMTP validation window with `MONITOR_ALLOW_REAL_EMAIL_SEND=true`.
- Real external validation must record redaction evidence and must not expose
  API keys, SMTP passwords, cookies, proxy credentials, raw profile paths,
  provider endpoints, local paths, or command lines.

## 2026-06-16 - CR-035/Phase 7.1A-C Run Lifecycle And AI Fallback Implementation

Environment: local worktree `E:\myproject\MediaCrawler`, branch
`codex/cr041-pilot-gate`.

Result:

- Implemented Phase 7.1A compatibility for run identity: new runs persist
  `crawl_runs.job_id`, running-run lookup can resolve legacy rows through
  `summary.job_id`, and a dry-run-capable backfill helper lists resolvable
  rows while skipping unresolved historical rows.
- Implemented Phase 7.1B idempotent terminal finalization: repeated terminal
  writes cannot reopen or corrupt a terminal run, repeated resource-lock
  release is harmless, lifecycle summaries persist phase, heartbeat, retry
  state, last safe result, and redacted last error, and Phase 7.1-marked stale
  running rows can recover as `interrupted` only after evidence checks.
- Implemented Phase 7.1C AI fallback: per-item timeout, exception, invalid
  result, and non-task-cancelling interruption fall back to `pending_review`;
  AI progress counts track total, successful, fallback, pending-review, and
  unresolved items; partial/manual-review state can still produce a report.
- Historical run `8317` was not modified. Phase 7.1D remains the required
  dry-run, backup, rollback, and explicit-operator-approval gate for any
  historical remediation.

Verification:

- `python -m py_compile api\monitoring\settings.py api\monitoring\database.py api\monitoring\runner.py tests\test_monitoring_mvp.py`
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7_1 or phase_5_recovery_marks_expired_running_run_before_releasing_locks or phase_2_run_job_marks_run_timeout_with_partial_results or ingest_dedupes_and_report_keeps_pending_review"`:
  8 passed.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 249 passed, 3
  warnings.
- `uv run python scripts/check_docs.py`: PASS.

Remaining:

- CR-041 is not complete yet. Pilot Gate C server-like real workflow validation
  still remains.
- Phase 7.1D historical run remediation remains open and must not run without
  explicit operator approval.

External validation:

- Read-only Claude Code review was run with Read/Grep/Glob-only tool access
  and no edit/write/Bash/database/email/crawler/AI/service permissions.
- The reviewer reported no Blocking findings and no Material findings that
  affect CR-041 pilot readiness for Phase 7.1A-C.
- The reviewer classified historical run `8317` remediation as correctly
  remaining in Phase 7.1D and Pilot Gate C real workflow validation as the
  remaining external gate.
- Minor polish notes did not require code changes before continuing.

## 2026-06-16 - CR-036/Phase 17.1A-B Email Safety Implementation

Environment: local worktree `E:\myproject\MediaCrawler`, branch
`codex/cr041-pilot-gate`.

Result:

- Implemented the Phase 17.1A shared real SMTP safety gate. Automatic report
  delivery, manual resend, and mail-test paths default to non-sending behavior
  unless `MONITOR_ALLOW_REAL_EMAIL_SEND` is explicitly enabled.
- Added read-only/deployment-locked runtime visibility for
  `real_email_delivery` / `MONITOR_ALLOW_REAL_EMAIL_SEND`; browser runtime
  settings cannot enable it.
- Blocked default report delivery records a customer-safe `skipped` delivery
  state while preserving report generation and delivery-log evidence.
- Added a suite-level SMTP tripwire that fails automated tests if
  `smtplib.SMTP` or `smtplib.SMTP_SSL` is reached without explicit opt-in.
- Implemented Phase 17.1C backend effective-recipient traceability:
  `recipients_json` remains the task/request snapshot, while
  `effective_recipients_json`, `effective_recipient_source`, and
  `trigger_source` record the final delivery target and send trigger.
- Implemented the Phase 17.2A backend portion that overlaps with CR-036:
  report snapshots and delivery logs now persist customer-safe effective
  template provenance without storing raw template HTML or SMTP secrets.
- No real SMTP email was sent. The explicit real-mail path was validated only
  through mocked SMTP under `MONITOR_ALLOW_REAL_EMAIL_SEND=true`.

Verification:

- `python -m py_compile api\monitoring\settings.py api\monitoring\database.py api\monitoring\mailer.py api\monitoring\reporting.py api\routers\monitor.py tests\conftest.py tests\test_monitoring_mvp.py`
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "login_window_open or phase_17_1 or phase_17a or phase_16_email_delivery or report_resend_email_updates_status or ai_and_email_test_paths"`:
  8 passed.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17_1 or phase_17a or phase_16_email_delivery or phase_18a_report_job_snapshots"`:
  7 passed.
- `uv run python -m pytest tests/test_monitoring_mvp.py`: 244 passed, 3
  warnings.
- `uv run python scripts/check_docs.py`: PASS.

Remaining:

- CR-041 is not complete yet. Phase 7.1A-C run lifecycle/AI fallback/partial
  report work, read-only external validation, and the minimum server-like real
  workflow gate still remain.
- Phase 17.1C operator-facing preflight/UI recipient-source explanation,
  Phase 17.1D orphan-evidence operations notes, and Phase 17.2B-C template
  guardrails/preset governance remain open follow-up tasks.

External validation:

- Read-only Claude Code review was run with Read/Grep/Glob-only tool access
  and no edit/write/Bash/database/email/crawler/AI permissions.
- The reviewer reported no Blocking findings for Phase 17.1A-B.
- Material findings were classified as follow-up or later-gate work: real SMTP
  delivery with operator credentials still belongs to Pilot Gate C; recipient
  source UI/preflight explanation remains Phase 17.1C follow-up; orphan
  evidence operations notes remain Phase 17.1D; template body guardrails and
  preset governance remain Phase 17.2B-C.
- The reviewer noted a possible mail-test coverage gap, but the current local
  suite already asserts default `send_test_email` blocking in
  `test_phase_17_1_manual_resend_and_mail_test_are_blocked_without_opt_in`.

## 2026-06-16 - CR-034 Decision Confirmation Closed

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- User confirmed the CR-034 visibility boundary: normal users see only
  business-safe AI evaluation summaries for their own runs; administrators may
  see redacted prompt/request/response debug snapshots; unredacted raw model
  responses must not be stored or exposed to any role.
- User confirmed AI trace retention must be administrator-configurable, with a
  30-day default.
- User accepted the default trace size guardrails: about 64KB per trace, 16KB
  prompt snapshot, 24KB request snapshot, 24KB response snapshot, and up to 20
  sampled comments with per-comment truncation.
- User accepted `ai_evaluation_traces` as the storage shape for trace snapshots,
  linked to `run_id`, `raw_content_id`, and `ai_evaluations.id`.
- CR-034 was moved from Needs Confirmation / Partially Confirmed to Accepted in
  the planning documents. Phase 20 remains not implemented.

Verification:

- Documentation-only decision update.
- No code, database schema, runtime settings implementation, crawler behavior,
  AI-provider call, or frontend behavior was changed.

## 2026-06-16 - CR-041 Minimum Usable Pilot Acceptance Gate Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added CR-041 as an Accepted documentation-governance gate for deciding when
  the system can be used first in a small pilot.
- Tightened first-pilot acceptance around three hard gates: CR-036/Phase
  17.1A-B hidden-real-email safety, CR-035/Phase 7.1A-C run lifecycle and
  partial-result safety, and a minimum server-like real workflow.
- Explicitly kept Phase 21 UI refinement, CR-038 sticky drawer close, Phase
  19 realtime progress, Phase 20 AI traceability, and CR-037 role/quota
  governance outside the first usable pilot blocker set unless a later accepted
  P0 safety, security, or core-flow regression changes the boundary.
- Linked CR-041 to `TASKS.md`, `TEST_PLAN.md`, `TRACEABILITY.md`,
  `CURRENT_STATE.md`, and `DECISIONS.md`.
- No code, database, SMTP, crawler, AI-provider, runtime data, or historical
  evidence was changed.

Verification:

- Documentation-only planning update. Implementation remains pending.

## 2026-06-16 - Phase 21 Formal Console UI Refinement Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` as the page-level
  frontend UI/UX refinement execution plan for the formal `/monitor` console.
- Recorded CR-040 as an Accepted existing-feature optimization and Phase 21 as
  the corresponding implementation phase.
- Linked CR-040 to `TASKS.md`, `TEST_PLAN.md`, `TRACEABILITY.md`, and
  `CURRENT_STATE.md`.
- The plan defines what to do, where to do it, how to test it, how to verify
  it, target experience, and acceptance criteria for every formal console
  page and major secondary surface.
- The plan also records the design confirmation model: the user confirms
  design-system direction and workflow boundaries, not every individual color,
  spacing, or layout value.
- Added Phase 21 layout-resilience rules after prototype review exposed a
  card/grid failure mode where Chinese labels can collapse into one-character
  vertical columns. Future Phase 21 implementation must fail verification if
  dashboard cards, closed-loop/status tracks, dense resource cards, run/report
  cards, or secondary overlays show text collapse, overlaps, hidden actions, or
  horizontal overflow at `1440x900`, `1024x768`, or `390x844`.
- Cross-validation review found one execution ambiguity around the currently
  unrendered `Users And Permissions` page. The plan was refined so Phase 21
  explicitly excludes that page and requires a separate new-capability CR if it
  is implemented later.
- Added implementation sequencing guidance: workstreams A-O should be handled
  as small frontend batches with local smoke checks before Phase 21P full
  cross-page verification.
- Added concrete layout stress pass/fail examples for long law-firm names and
  closed-loop cards.
- Phase 21A-21P implementation tasks remain unchecked; no UI code has been
  implemented in this planning update.

Verification:

- Documentation-only planning update.
- No production frontend code, backend API, database, permission model,
  crawler, AI-provider, SMTP, scheduler, deployment, or runtime data was
  changed.

## 2026-06-16 - CR-035/CR-036 Decision Confirmation Closed

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- User confirmed CR-035 recovery/retry/timeout decisions:
  evidence-based stale recovery, 10-minute heartbeat grace period, crawler
  retry reuse for platform/browser/network failures, AI item retry budget, and
  `ai_item_timeout_seconds=120`.
- User confirmed CR-036 real-mail safety decisions:
  `MONITOR_ALLOW_REAL_EMAIL_SEND` environment gate, read-only runtime
  visibility, non-sending local/test behavior unless explicitly allowed,
  manual resend safety behavior, `trigger_source`, and
  `effective_recipients_json`.
- CR-035 and CR-036 were moved from Needs Confirmation to Accepted in the
  planning documents. CR-037 remains Deferred.

Verification:

- Documentation-only decision update.
- No code, database, delivery-log, email, or runtime mutation was performed.

## 2026-06-16 - CR-035/CR-036 Partial Decision Confirmation Update

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Recorded user-confirmed CR-035 decisions: `interrupted` is a first-class
  terminal run status; active finalization may convert known unresolved AI
  candidates to `pending_review`; AI evaluation progress counts should include
  success, failure, fallback, pending-review, and unresolved totals; preventing
  future `crawl_runs.job_id` gaps is primary and historical backfill is
  fallback-only.
- Kept CR-035 blocked for remaining decisions on stale-recovery evidence,
  retry policy, and AI item timeout.
- Recorded user-confirmed CR-036 decision that historical unexpected-email
  evidence should be preserved by default and not mutated without backup and
  explicit operator approval.
- Kept CR-036 blocked for remaining decisions on explicit real-mail validation,
  runtime/deployment setting surface, and local/manual resend behavior.
- Recorded CR-037 as a deferred future capability for administrator-managed
  normal-user email send/resend policy and quotas.

Verification:

- Documentation-only decision update.
- No code, database, delivery-log, email, or runtime mutation was performed.

## 2026-06-16 - CR-036 Test And Local Email Delivery Safety Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Read-only inspection traced two unexpected real `日报 海安律所` emails to
  temporary test/local report runs rather than to a visible active operator
  task.
- Confirmed the two `.eml` files are distinct messages with distinct
  attachments and send times:
  - `job_9686_run_8380_20260616_152702.*`
  - `job_9759_run_8447_20260616_165528.*`
- Confirmed matching automatic delivery-log rows exist for `job_id=9686` /
  `report_id=3959` and `job_id=9759` / `report_id=3998`.
- Confirmed the current `monitor_jobs`, `crawl_runs`, and `reports` rows for
  those IDs no longer exist, which explains why the console no longer shows a
  matching active task.
- Identified the strongest local trigger evidence as
  `tests/test_monitoring_mvp.py::test_run_job_blocks_platform_when_login_window_is_open`,
  which reaches `run_monitor_job` without mocking the report email delivery
  path.
- Recorded CR-036 and Phase 17.1 follow-up tasks for real SMTP safety, test
  isolation, effective-recipient traceability, and historical orphan evidence
  handling.

Verification:

- Read-only inspection only.
- No code, database, or delivery-log mutation was performed.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-16 - CR-035 Run Lifecycle Stuck Recovery Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Reworked `docs/RUN_AI_STUCK_BUG_TODO.md` so the live run `8317` stuck-running
  issue is separated into CR-035/Phase 7.1 regression-fix scope and
  CR-031/Phase 19 progress-visibility enhancement scope.
- Recorded the completed-phase follow-up rule: historical completed phases
  remain verification snapshots, while newly found defects get their own
  regression-fix CR, task block, traceability row, and tests.
- Added proposed Phase 7.1 tasks for run identity compatibility, idempotent
  finalization, stale recovery before deadline, AI fallback, partial report
  generation, and current-run remediation gating.
- Added a comprehensive read-only review prompt to
  `docs/RUN_AI_STUCK_BUG_TODO.md` for future agent review.

Verification:

- Documentation-only planning update; implementation remains blocked pending
  CR-035 confirmation.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-16 - CR-033 Secondary Overlay Loading Feedback Verified

Environment: local worktree `E:\myproject\MediaCrawler`; formal console
served at `http://127.0.0.1:8080/monitor`.

Result:

- Added stable button-level loading feedback for secondary drawers and modals,
  including task save, account save, account QR login start, local login
  window open, Cookie save/clear, login continuation confirmation, proxy save,
  AI access save, AI model-list fetch, AI connection test, AI rule test/save,
  mail config save, mail test, email template save, and email template preview.
- Added local loading text inside the platform account login result area,
  Cookie result area, login-session history area, AI model status, AI rule test
  console, and email-template preview subject area.
- Kept the existing QR login, Cookie login, local login fallback, login
  records, resource forms, test modals, and business flows unchanged. No
  backend API, database, permission, crawler, AI provider, or SMTP logic was
  changed.

Verification:

- Inline monitor page script parse check.
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "monitor_page_uses or phase_11c or phase_11d or phase_12b or phase_17b or phase_18b"`
- Result: 8 passed, 233 deselected, 3 warnings.
- `uv run python scripts\check_docs.py`
- Result: PASS docs consistency.
- Browser check on `http://127.0.0.1:8080/monitor` confirmed the Platform
  Accounts modal opens, the added overlay action buttons are present with
  dedicated feedback bindings, and browser console errors remain empty.

Limitations:

- Real platform QR scanning, real AI-provider calls, and real SMTP delivery
  were not triggered in this verification to avoid creating live external
  side effects.

## 2026-06-16 - CR-034 Run Detail And AI Evaluation Traceability Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Reviewed the current AI evaluation path and confirmed that
  `build_evaluation_payload(job, content, comments)` can provide the business
  input payload at evaluation time.
- Confirmed current `ai_evaluations` stores final structured fields and a
  redacted `raw_response`, but does not persist exact prompt/request/input
  snapshots, provider/model metadata, duration, or per-attempt trace detail.
- Added CR-034 as a Needs Confirmation requirement for Run Detail and AI
  Evaluation Traceability.
- Added proposed Phase 20 tasks for confirmation, data model, trace
  persistence, run-detail API, frontend run detail, and explicit Report Center
  lead entry.
- Added proposed data-model and migration notes for `ai_evaluation_traces`
  without marking them accepted or implemented.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-16 - CR-033 Formal Console Full-Coverage Positive UI Optimization Verified

Environment: local worktree `E:\myproject\MediaCrawler`; formal console
served at `http://127.0.0.1:8080/monitor`.

Result:

- Applied a cleaner, lower-noise enterprise visual layer to the formal monitor
  console without introducing a framework, build step, backend API, database,
  crawler, AI, SMTP, or permission change.
- Reprioritized the dashboard so operations metrics and closed-loop
  task -> run -> report -> email status appear before the 01-05 shortcut flow.
- Added page-shaped skeleton/loading states for dashboard, accounts, proxies,
  AI access, AI rules, mail configuration, mail templates, runtime strategy,
  run center, report center, and system diagnostics.
- Kept formal navigation, filters, batch actions, account QR/Cookie/login
  history flows, task drawer fields, resource forms, AI rule modal, mail
  template iframe preview, run logs, report preview, delivery history, resend,
  and download actions available.
- Kept account, task, AI rule, and report row more menus as fixed floating
  menus that are not clipped by table scroll containers.
- Compressed the mobile dashboard metrics and closed-loop rail at 390px while
  keeping the 01-05 shortcut flow available below the operational data.

Verification:

- Inline monitor page script parse check.
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- `uv run pytest tests/test_monitoring_mvp.py::test_monitor_page_uses_tob_information_architecture_without_customer_facing_engine_traces tests/test_monitoring_mvp.py::test_monitor_page_uses_consistent_buttons_tables_and_modal_actions tests/test_monitoring_mvp.py::test_phase_11a_monitor_static_boundary_and_tokens_are_available tests/test_monitoring_mvp.py::test_phase_11b_base_layout_styles_live_in_monitor_css tests/test_monitoring_mvp.py::test_phase_11c_interaction_helpers_and_floating_menus tests/test_monitoring_mvp.py::test_phase_11d_responsive_foundation_and_mobile_navigation tests/test_monitoring_mvp.py::test_phase_12a_navigation_groups_and_login_landing tests/test_monitoring_mvp.py::test_phase_12b_page_entry_and_role_flow_shortcuts tests/test_monitoring_mvp.py::test_phase_13b_operations_home_desktop_visual_metrics tests/test_monitoring_mvp.py::test_phase_13c_operations_home_responsive_role_views tests/test_monitoring_mvp.py::test_phase_15b_run_center_frontend_filters_pagination_archive_controls tests/test_monitoring_mvp.py::test_phase_17b_report_center_delivery_history_frontend_hooks tests/test_monitoring_mvp.py::test_phase_18b_report_center_task_grouping_frontend_hooks`
- Result: 13 passed, 1 warning.
- Browser desktop 1440px sweep:
  dashboard, jobs, accounts, proxies, ai, ai_rules, email, email_templates,
  runtime, runs, reports, and doctor all opened with zero app console errors
  and no horizontal page overflow.
- Browser secondary-surface checks:
  account dialog, job drawer, proxy drawer, AI profile drawer, AI connection
  test modal, AI rule modal, mail config modal, mail test modal, email template
  drawer, run log drawer, report preview drawer, and report action menu opened
  and retained their expected controls.
- Browser responsive checks:
  tablet 1024px page sweep passed with mobile navigation open/select/close;
  mobile 390px full page sweep passed with no horizontal page overflow; account
  dialog, run log drawer, and report preview drawer stayed within safe margins
  and remained closable.

Limitations:

- This pass did not implement CR-031 realtime run-progress backend/product
  behavior.
- Real platform QR scanning, real AI provider calls, and real SMTP delivery
  remain pilot-deployment validation items, not part of this frontend-only
  visual optimization.

## 2026-06-16 - Phase 19A Requirement Intake Classification And CR-031 Planning

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added CR-031 for Run Center realtime progress visibility as an accepted
  existing feature optimization. The product code remains not implemented.
- Added CR-032 for requirement classification and optimization documentation
  rules.
- Added Phase 19A-19D task structure covering requirement documentation rules,
  run-center progress data, AI evaluation progress, and frontend progress
  polling/display.
- Updated product, UI, frontend architecture, traceability, and test-plan
  documents so future implementation has explicit boundaries and acceptance
  tests.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

## 2026-06-16 - CR-030 Row Action Menu Clipping Regression Fix Verified

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Moved Platform Account, Monitoring Task, and AI Evaluation Rule row "more"
  menu content out of table rows and into page-level fixed floating containers.
- Kept table rows to trigger buttons only, so table scroll containers and
  sticky action columns cannot clip or cover the menu content.
- Preserved existing report-center floating menu behavior.
- Menus still close on outside click, escape, page change, and successful
  action.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11c_interaction_helpers_and_floating_menus"`
- Result: 1 passed, 240 deselected, 1 warning.
- Inline monitor page script parse check.
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- Browser checks for Platform Accounts, Monitoring Tasks, and AI Evaluation
  Rules row "more" menus on `http://127.0.0.1:8080/monitor`.
- Result: PASS. Each menu rendered as a fixed `BODY` child, stayed inside the
  viewport, and was not inside a `.table-wrap` scroll container.

## 2026-06-16 - CR-029 Login Session Success Reconciliation Verified

Environment: local worktree `E:\myproject\MediaCrawler`.

Result:

- Added same-account login-state reconciliation for server-side QR login
  sessions. When QR polling reports QR failure, timeout, platform error, or a
  disappeared browser session, the monitor API now checks the same
  account/Profile through MediaCrawler account validation before returning
  failure.
- If the account/Profile validates successfully, the login session is updated
  to `success` with the message `登录成功，账号已通过验活。`.
- If validation fails, the original QR/session failure state remains; captcha,
  slider, SMS, and manual-verification states are not bypassed.
- Updated the login modal so an active matching account status renders as
  login success instead of `当前没有拿到二维码`.
- Added a Xiaohongshu-specific customer-safe hint when a legacy profile-path
  directory exists but the current profile-key runtime path does not, without
  migrating or exposing the raw path.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "login_session or qrcode or account_check or mediacrawler_login_capability or platform_status_uses_active_account_profile or phase_6"`
- Result: 41 passed, 200 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 241 passed, 3 warnings.
- `python -m py_compile api\routers\monitor.py api\monitoring\account_check.py tests\test_monitoring_mvp.py`
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- Inline monitor page script parse check.
- Result: PASS.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Browser smoke check for `http://127.0.0.1:8080/monitor`.
- Result: PASS, monitor shell loaded with no browser console errors.

Limitations:

- Verification used mocked platform-login outcomes and local static/API tests.
  Real platform QR scanning and crawling remain production pilot validation
  items.

## 2026-06-16 - Phase 18B Report Center Task Grouping Frontend Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Updated the report-center frontend list rendering path to group reports by
  active monitoring task when `job_id` resolves.
- Grouped deleted-task and missing-task reports from the Phase 18A
  `job_snapshot` customer-safe fields.
- Added deleted-task, historical snapshot, and limited-context labels while
  avoiding raw `job_snapshot_json` exposure.
- Preserved selected-report preview, report-specific lead switching, download
  links, latest email delivery status, delivery history, manual resend menu
  entry, and row actions.
- Added grouped report-center styles for desktop, tablet, and mobile.
- Did not change schema, migrations, API authorization, owner/workspace scope,
  or V1 product boundaries.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_18b or phase_18a or phase_17b or report_resend_email_updates_status or report_history_keeps_law_firm_snapshot_after_job_deleted or leads_api_can_scope_items_to_selected_report"`
- Result: 8 passed, 228 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 236 passed, 3 warnings.
- `python -m py_compile tests\test_monitoring_mvp.py`
- Result: PASS.
- Inline monitor page script parse check with `node --check` against the
  extracted inline script.
- Result: PASS.
- Browser validation on isolated service `127.0.0.1:19218` with temporary
  monitor data:
  - `/monitor`, `/static/monitor/monitor.css`, and
    `/static/monitor/monitor.js` returned HTTP 200;
  - administrator login opened Report Center with four validated group types:
    active task, deleted task, missing-task snapshot, and limited-context
    historical report;
  - group headers showed task/snapshot labels plus platform, keyword, and
    frequency context without raw snapshot JSON;
  - report ID 1 preview opened the drawer, scoped lead detail to report ID 1,
    kept download menu links under report ID 1, and displayed the automatic
    delivery-history row;
  - 1440px, 1024px, and 390px checks found four grouped sections, no
    page-level horizontal overflow, and no authenticated console/page errors;
  - normal-user login kept Report Center visible and administrator resource or
    diagnostics entries hidden.

Limitations:

- Browser validation used isolated temporary sample data, not production data.
- Real platform crawling, real SMTP delivery, real AI provider behavior, and
  production credentials remain production pilot risks inherited from earlier
  phases.
- The Codex in-app browser returned `net::ERR_BLOCKED_BY_CLIENT` for the local
  validation URL, so equivalent local Playwright validation was used against
  the same isolated FastAPI service.

## 2026-06-16 - Phase 18A Report Job Snapshot Data Model Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added `reports.job_snapshot_json` to new SQLite database creation and
  compatible existing-database migration.
- Added shared report job snapshot builders for task ID, law firm, platforms,
  search keywords, frequency, and deleted-task context.
- Persisted snapshots for newly generated reports.
- Backfilled snapshots for existing reports whose `job_id` still resolves to a
  monitoring task.
- Updated task deletion to mark report snapshots with deleted-task context
  before the task row is removed.
- Kept unrecoverable old reports readable as limited-context historical
  reports.
- Preserved `job_id` for active and historical task relations.
- Preserved owner/workspace filtering by resolving reports through current
  report/job/creator scope; snapshot content is never used to grant access.
- Exposed customer-safe `job_snapshot`, `job_deleted`,
  `legacy_without_job_snapshot`, and `limited_context` fields for Phase 18B
  consumption.
- Did not implement Phase 18B frontend report grouping, grouped layouts, or
  responsive grouped-report UI.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_18a`
- Result: 2 passed, 233 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_18a or phase_17b or phase_17a or phase_16 or report_resend_email_updates_status or report_history_keeps_law_firm_snapshot_after_job_deleted or list_reports_limit_zero"`
- Result: 10 passed, 225 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 235 passed, 3 warnings.
- `python -m py_compile api\monitoring\database.py api\monitoring\reporting.py api\routers\monitor.py tests\test_monitoring_mvp.py`
- Result: PASS.

Limitations:

- Phase 18A is data-model preparation only. Phase 18B must still implement
  report-center grouping, deleted-task/limited-context labels, and desktop,
  tablet, and mobile grouped-report verification.
- Browser validation was not rerun because Phase 18A has no visual UI change.
  Existing Phase 17B browser validation remains the latest report-center
  frontend proof until Phase 18B.
- Real platform crawling, real SMTP delivery, real AI provider behavior, and
  production credentials remain production pilot risks inherited from earlier
  phases.

## 2026-06-16 - Phase 17B Email Delivery History Frontend Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added report delivery-history API access for
  `/api/monitor/reports/{report_id}/email-delivery-logs`, scoped through the
  current actor and report visibility.
- Returned report latest-state fields and customer-safe delivery-log rows
  without exposing SMTP passwords, tokens, cookies, proxy secrets, or internal
  redaction labels.
- Updated the report center with latest delivery status cells, a
  delivery-history panel, refresh control, and report action-menu entry for
  viewing history.
- Displayed send type, status, time, recipient summary, send-window key, and
  customer-safe error messages.
- Required confirmation before manual resend and refreshed both the report list
  and selected delivery history after resend.
- Preserved report preview, lead detail switching, report downloads, run
  center, task list, task-create entry, logout, and role-visible navigation.
- Did not add Phase 18 report snapshots/grouping, schema changes, or frontend
  dependencies.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_17b`
- Result: 2 passed, 231 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17b or phase_17a or phase_16 or report_resend_email_updates_status or phase_1_http_routes_enforce_sessions_roles_and_owner_scope or monitor_page_uses"`
- Result: 9 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 233 passed, 3 warnings.
- `python -m py_compile api\routers\monitor.py api\monitoring\database.py api\monitoring\reporting.py tests\test_monitoring_mvp.py`
- Result: PASS.
- `node --check api\webui\monitor\monitor.js`
- Result: PASS.
- Inline monitor page script parse check
- Result: PASS.
- Isolated browser service on `127.0.0.1:19217`:
  - `/monitor`, `/static/monitor/monitor.css`, and
    `/static/monitor/monitor.js` returned HTTP 200;
  - administrator login opened the console and Report Center;
  - delivery history rendered automatic and manual-resend rows with
    recipients, window key, status, time, and customer-safe error text;
  - 1440px, 1024px, and 390px report-center checks kept the delivery-history
    surface usable without page-level horizontal overflow;
  - report preview drawer, report row menu, run center, task list,
    task-create entry, logout, and normal-user role-visible navigation were
    checked with no console errors.

Limitations:

- Browser validation used isolated temporary data and did not prove real SMTP
  delivery, real platform crawling, or production credential behavior.
- Phase 18 report snapshots and grouped report-center UI remain planned and
  unimplemented.

## 2026-06-16 - Phase 17A Email Idempotency And Delivery Logic Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Connected automatic report email delivery to `email_delivery_logs`.
- Used the accepted `send_window_key` helper for `daily`, `6h`, `12h`, and
  `cron` schedule windows.
- Added automatic-send idempotency for
  `workspace_id + job_id + send_window_key + send_type=auto`; repeated
  automatic delivery in the same window is recorded as `skipped` and does not
  call the mailer again.
- Recorded automatic pending/sent/failed/skipped delivery rows with recipient
  summaries and customer-safe error messages.
- Recorded explicit manual resend as a separate `manual_resend` delivery row
  with `sent_by` while leaving automatic idempotency independent.
- Preserved report generation when SMTP fails and kept
  `reports.email_status` / `reports.email_error` as latest-state
  compatibility fields until Phase 17B delivery-history UI is implemented.
- Carried run-source labels through CLI and scheduler paths so automatic and
  manual run summaries remain distinguishable.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_17a`
- Result: 2 passed, 229 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17a or phase_16 or phase_15b or phase_15a or phase_14 or report_resend_email_updates_status or phase_7_run_job_generates_report_without_ai_or_email or cli_run_due or scheduler"`
- Result: 20 passed, 211 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 231 passed, 3 warnings.
- `python -m py_compile api\monitoring\database.py api\monitoring\reporting.py api\monitoring\runner.py api\monitoring\scheduler.py api\monitoring\cli.py api\routers\monitor.py tests\test_monitoring_mvp.py`
- Result: PASS.

Limitations:

- Phase 17A is backend delivery-governance work only. It does not add the
  Phase 17B report-center delivery-history frontend and does not implement
  Phase 18 report grouping or report snapshots.
- Real SMTP delivery, real platform crawling, and production credential
  behavior remain production pilot risks inherited from earlier phases.

## 2026-06-16 - Phase 16 Email Delivery Data Model Preparation Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added `email_delivery_logs` to new SQLite database creation and compatible
  existing-database migration.
- Stored `workspace_id`, `job_id`, `report_id`, `send_window_key`,
  `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
  `recipients_json`, and `created_at`.
- Added `email_send_window_key` for the accepted `daily`, `6h`, `12h`, and
  `cron` rules.
- Added delivery-log insert/list helpers that preserve customer-safe error
  text and recipient summaries without storing SMTP passwords, proxy
  credentials, or tokens.
- Added recommended indexes:
  `idx_email_delivery_job_window`, `idx_email_delivery_report`, and
  `idx_email_delivery_status`.
- Added partial unique index `idx_email_delivery_auto_window_unique` for one
  pending/sending/sent automatic row per workspace, task, schedule window, and
  `send_type=auto`.
- Preserved existing `reports.email_status` and `reports.email_error`
  latest-state compatibility fields.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_16`
- Result: 1 passed, 228 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_16 or phase_15b or phase_15a or phase_14 or report_resend_email_updates_status"`
- Result: 5 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 229 passed, 3 warnings.
- `python -m py_compile api/monitoring/database.py tests/test_monitoring_mvp.py`
- Result: PASS.

Limitations:

- Phase 16 is data-model preparation only. It does not connect scheduler or
  mailer delivery behavior to the log table, does not prevent duplicate sends
  end to end, and does not add report-center delivery-history UI. Those remain
  Phase 17A and Phase 17B work.
- Real SMTP delivery remains a production pilot risk inherited from earlier
  phases.

## 2026-06-16 - Phase 15B Run Center Frontend Refinement Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added run-center pagination UI with summary and previous/next controls.
- Added task/law-firm, status, platform, run type, visibility, date, and page
  size filters.
- Default run-center view now requests `run_type=operational`, which separates
  scheduled/manual operational records from test/diagnostic noise.
- Added administrator archive and restore row actions with confirmation while
  keeping normal users scoped to visible records.
- Preserved run-log drawer refresh, copy, and download controls.
- Added frontend/CSS regression coverage for the Phase 15B controls and kept
  Phase 16/18 terms out of this frontend batch.
- Added the `operational` run-type API alias needed by the default frontend
  view while preserving `scheduled`, `manual`, and `test` filters.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15b or phase_15a"`
- Result: 2 passed, 226 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15b or phase_15a or phase_14 or run_logs or list_runs"`
- Result: 4 passed, 224 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 228 passed, 3 warnings.
- `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Inline monitor page script parse check
- Result: PASS.
- Isolated browser service on `127.0.0.1:19180`:
  - `/monitor`, `/static/monitor/monitor.css`, and
    `/static/monitor/monitor.js` returned HTTP 200;
  - administrator login opened the operations home and Run Center;
  - Run Center showed pagination, filters, default visible/operational
    summary, row status, log, and archive actions;
  - test/diagnostic records were hidden from the default operational view and
    visible through the run-type filter;
  - the run-log drawer opened with real `crawler.log` content and displayed
    refresh, copy, and download controls;
  - administrator archive/restore API behavior was verified against the
    running service;
  - normal-user API scope returned `403` for archived visibility and archive
    action;
  - desktop 1440px, tablet 1024px, and mobile 390px run-center layouts kept
    filters, status, actions, summary, pagination, and list content reachable
    without horizontal page overflow.

Limitations:

- Browser validation used isolated temporary data and did not prove real
  platform crawling, SMTP delivery, or AI-provider behavior.
- Phase 16 email delivery logs and Phase 18 report snapshots remain planned
  and unimplemented.

## 2026-06-16 - Phase 15A Run Center API And Data Governance Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added run API/query pagination while preserving the existing `runs` and
  `running_job_ids` response fields.
- Added `pagination` and `filters` response metadata for the run list API.
- Added filters for task ID, law firm, status, platform, run type, visibility,
  and date range.
- Added administrator-only archive and restore APIs that update
  `crawl_runs.visibility`, `archived_at`, and `archived_by` without physically
  deleting run records.
- Default run-list API behavior hides archived records. Administrators can
  request archived or all records explicitly; normal users receive `403` for
  archived/all visibility requests.
- Preserved owner/workspace scope for paginated and filtered run results.
- Preserved existing status values, report links, and run-log access for
  visible records. Archived run logs and stop actions are hidden from normal
  users.
- Added
  `tests/test_monitoring_mvp.py::test_phase_15a_run_center_api_pagination_filters_archive_and_scope`.
- Did not implement Phase 15B frontend pagination, filter controls, or row
  archive/restore actions.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation and after verification.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_15a`
- Result: 1 passed, 226 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15a or run_logs or list_runs"`
- Result: 2 passed, 225 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 227 passed, 3 warnings.

Limitations:

- Phase 15A is API/data governance only. Run-center frontend pagination,
  filter controls, archive/restore confirmations, and responsive run-center
  layout remain Phase 15B work.
- Phase 16 email delivery logs and Phase 18 report snapshots remain planned
  and unimplemented.

## 2026-06-16 - Phase 14 Run Center Data Model Preparation Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added compatible `crawl_runs` schema fields for run-center governance:
  `visibility`, `run_type`, `archived_at`, and `archived_by`.
- New database creation now includes `visibility = visible` and
  `run_type = scheduled` defaults.
- Existing database migration adds the same fields, backfills empty values to
  `visible` and `scheduled`, and preserves `archived_at` and `archived_by` as
  nullable fields.
- Added recommended Phase 14 indexes:
  `idx_crawl_runs_visibility` on `(workspace_id, visibility, started_at)` and
  `idx_crawl_runs_type_status` on `(workspace_id, run_type, status)`.
- Added
  `tests/test_monitoring_mvp.py::test_phase_14_run_center_visibility_fields_migrate_and_backfill`.
- Verified existing run reads, run list reads, report links, and status values
  remain readable after the migration.
- Did not implement Phase 15 pagination, filters, archive/restore APIs,
  default archived hiding, frontend run-center controls, email delivery logs,
  or report grouping.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation and after verification.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_14`
- Result: 1 passed, 225 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_14 or phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 13 passed, 213 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 226 passed, 3 warnings.

Limitations:

- Phase 14 is data-model preparation only. Run-center pagination, filtering,
  default visible-only behavior, archive/restore APIs, and responsive frontend
  controls remain Phase 15A/15B work.
- Phase 16 email delivery logs and Phase 18 report snapshots remain planned
  and unimplemented.

## 2026-06-16 - Phase 13C Operations Home Responsive And Role Views Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Adapted the operations home for 1024px tablet and 390px mobile layouts with
  explicit wrapping rules for metric cards, drilldown entries, resource
  signals, and the administrator health summary.
- Replaced the home-page detailed diagnostics block with a compact
  administrator-only health summary and moved detailed readiness, scheduler,
  system-checklist, and platform-status sections to System Diagnostics.
- Kept normal users scoped to their own task/run/report metrics and
  business-safe resource wording `资源由管理员维护`; normal users do not see
  administrator resource drilldowns or System Diagnostics shortcuts.
- Preserved administrator resource health as concise signals with drilldowns to
  resource pages and System Diagnostics.
- Added
  `tests/test_monitoring_mvp.py::test_phase_13c_operations_home_responsive_role_views`.
- No schema migration, API contract change, email delivery logs, run archive
  fields, report snapshots, chart dependency, or new frontend framework was
  added.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation and after verification.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 12 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` plus
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200 and contained `运营首页`;
  - `/static/monitor/monitor.css`: HTTP 200 and contained
    `.operations-admin-health`;
  - `/static/monitor/monitor.js`: HTTP 200 and contained `MonitorUI`.
- Browser validation:
  - administrator login reached Operations Home;
  - administrator 1440px, 1024px, and 390px checks found five operations metric
    cards, the compact administrator health summary, visible primary actions,
    and no horizontal overflow;
  - administrator System Diagnostics drilldown reached readiness, scheduler,
    and platform status details;
  - normal-user login used a fresh browser context;
  - normal-user navigation exposed only `总览`, `舆情监控`, `运行中心`, and
    `报告中心`;
  - normal users saw business-safe resource wording `资源由管理员维护`;
  - normal users did not see administrator account/resource drilldowns,
    administrator health summary, or System Diagnostics shortcuts;
  - normal-user 1024px and 390px checks found no horizontal overflow;
  - normal-user task drawer, Run Center, Report Center, and logout path
    remained reachable;
  - authenticated console/page errors were empty. The unauthenticated
    session-check 401 before login remains existing login behavior and was not
    treated as an authenticated console regression.

Limitations:

- Phase 13C closes the operations-home responsive and role-view batch. Phase 14
  is still required before run-center archive/noise filtering and must add its
  accepted data-model fields and migration/backfill tests first.
- Real platform QR scanning, real platform crawling, real AI provider, and real
  SMTP delivery remain production pilot risks inherited from earlier phases.

## 2026-06-16 - Phase 13B Operations Home Desktop Visual Metrics Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Replaced the default text-heavy Overview dashboard with an operations-home
  visual metric layout in `api/monitor_web/index.html`.
- Rendered task health, run activity, report/review status, email delivery
  latest state, suspected negative leads, and concise resource health from the
  Phase 13A operations-home API contract, with a legacy summary fallback for
  compatibility.
- Added drilldowns into Monitoring, Run Center, Report Center, report email
  delivery status, and administrator platform-account resources where
  permitted.
- Moved long readiness, scheduler, and platform diagnostics into a collapsed
  administrator-only diagnostics section so they no longer dominate the default
  home page.
- Added operations-home layout and metric styles to
  `api/webui/monitor/monitor.css`.
- Added
  `tests/test_monitoring_mvp.py::test_phase_13b_operations_home_desktop_visual_metrics`.
- Chose native HTML/CSS rather than a chart dependency, so no new dependency or
  `DECISIONS.md` entry was required.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before and after code verification.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 11 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` plus
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200 and contained `运营首页`;
  - `/static/monitor/monitor.css`: HTTP 200 and contained
    `.operations-metric-grid`;
  - `/static/monitor/monitor.js`: HTTP 200 and contained `MonitorUI`.
- Browser validation:
  - administrator login reached Operations Home;
  - administrator saw five operations metric cards;
  - administrator drilldowns reached Monitoring, Run Center, Report Center,
    report email delivery status, and Platform Accounts;
  - administrator diagnostics were collapsed by default;
  - administrator 1440px, 1024px, and 390px checks found no horizontal
    overflow;
  - normal-user login used a fresh browser context;
  - normal-user navigation exposed only `总览`, `舆情监控`, `运行中心`, and
    `报告中心`;
  - normal users saw business-safe resource wording `资源由管理员维护`;
  - normal users did not see the administrator resource drilldown or system
    diagnostics;
  - normal-user task drawer, Report Center, and logout path remained
    reachable;
  - authenticated console/page errors were empty. The unauthenticated
    session-check 401 before login remains existing login behavior and was not
    treated as an authenticated console regression.

Limitations:

- Phase 13B implements the desktop visual metric surface and role-safe
  drilldowns. Phase 13C still needs the dedicated responsive and role-view
  close-out required by the roadmap.
- No schema migration, run archive/noise filtering, email delivery log,
  delivery-history UI, report grouping, or report snapshot behavior was added
  in this batch.

## 2026-06-15 - Phase 13A Operations Home Data Layer Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`.

Result:

- Added an operations-home data contract under the existing
  `/api/monitor/dashboard` API surface.
- Extended the existing dashboard summary with `summary.operations_home` while
  preserving all existing flat dashboard fields for compatibility.
- Returned the same object as top-level `operations_home` so Phase 13B can
  migrate the frontend without breaking old summary consumers.
- Aggregated task health, run activity, report activity, email delivery latest
  state, suspected lead metrics, and concise resource health from existing
  persisted tables.
- Represented missing delivery history as unavailable instead of fabricating
  Phase 16/17 delivery-log metrics.
- Preserved administrator workspace-wide visibility and normal-user
  owner/workspace scope. Normal users receive business-safe resource health and
  no platform account, proxy, AI profile, or login-session counts.
- Added
  `tests/test_monitoring_mvp.py::test_phase_13a_operations_home_data_layer_scopes_real_aggregates`.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_13a`
- Result: 1 passed, 222 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 10 passed, 213 deselected, 3 warnings.

Limitations:

- Phase 13A only adds the API/data layer. It does not implement the Phase 13B
  desktop visual metrics or Phase 13C responsive/role-specific frontend view.
- No schema migration, email delivery log, run archive, or report grouping
  behavior was added in this batch.

## 2026-06-15 - Phase 12B Page Entry And Role Flow Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Added consistent page entry headers for Operations Home, Monitoring, Run
  Center, Report Center, account resources, proxy resources, AI access, AI
  rules, mail configuration, mail templates, runtime settings, and system
  diagnostics.
- Added role-aware task-loop shortcuts for creating a monitoring task, viewing
  runs, viewing reports, checking report email delivery status, and resolving
  administrator resource issues.
- Added a report-center email delivery entry that keeps latest report email
  status and manual resend discovery in the task loop without implementing the
  later delivery-log data model.
- Changed the shell refresh action to refresh the current page instead of a
  global-status-only action.
- Added
  `tests/test_monitoring_mvp.py::test_phase_12b_page_entry_and_role_flow_shortcuts`.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation and after documentation
  close-out.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses"`
- Result after documentation close-out: 8 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Browser validation:
  - administrator login landed on `dashboard`;
  - 12 page entries existed in the DOM;
  - administrator Operations Home showed 5 shortcuts including the resource
    support shortcut;
  - create-task shortcut opened the task drawer;
  - task -> runs -> reports shortcuts navigated successfully;
  - report-center email delivery entry was visible;
  - normal-user navigation contained only `总览`, `舆情监控`, `运行中心`, and
    `报告中心`;
  - normal-user Operations Home showed 4 task-loop shortcuts and no visible
    administrator resource shortcuts;
  - normal-user email delivery shortcut navigated to Report Center and the
    email delivery entry;
  - 1440px, 1024px, and 390px checks found no business-area horizontal
    overflow for page entries, shortcut blocks, or the email delivery entry;
  - 390px mobile navigation opened, selected Monitoring, and closed;
  - page console errors were empty.

Limitations:

- Phase 12B only standardizes page entry structure and role-safe task-loop
  navigation. Phase 13A must still define the real operations-home data
  contract and aggregates.
- No backend API contract, database schema, permission model, email-delivery
  log, run archive, or report grouping changes were made in this batch.

## 2026-06-15 - Phase 12A Navigation Structure And Login Landing Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Replaced detached hover popovers for Resource Management and System
  Configuration with expandable navigation groups.
- Routed successful form login and session restore to Operations Home
  (`dashboard`) when no explicit allowed destination is present.
- Grouped authenticated user identity and logout in the desktop top-right
  account area and added a predictable mobile account area in the navigation
  drawer.
- Preserved administrator and normal-user menu visibility rules.
- Added
  `tests/test_monitoring_mvp.py::test_phase_12a_navigation_groups_and_login_landing`.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation and after documentation
  close-out.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses"`
- Result after documentation close-out: 7 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Playwright authenticated browser validation:
  - form login landed on `dashboard`;
  - session restore landed on `dashboard`;
  - administrator Resource Management and System Configuration groups were
    visible and expandable/collapsible;
  - mobile nested `email_templates` page switching worked and closed the
    drawer;
  - normal-user navigation contained only `总览`, `舆情监控`, `运行中心`, and
    `报告中心`;
  - authenticated console/page errors were empty.

Limitations:

- Phase 12A only changes navigation structure, login/session landing, and
  account/logout grouping. Phase 12B still needs to standardize page entry
  headers, descriptions, primary actions, toolbar areas, and role-specific
  task-loop shortcuts.
- No API contract, data model, schema migration, or permission model changes
  were made in this batch.

## 2026-06-15 - Phase 11D Responsive Foundation Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Implemented accepted responsive breakpoints in
  `api/webui/monitor/monitor.css`: desktop `>= 1280px`, tablet
  `768px - 1279px`, and mobile `< 768px`.
- Added touch-safe mobile navigation in `api/monitor_web/index.html` using a
  top-left hamburger button, left-side drawer, and backdrop.
- Added mobile navigation behavior for toggle open, backdrop close, Escape
  close, page-switch close, and desktop-resize reset.
- Made shell, header actions, page heads, toolbars, grids, modals/drawers,
  action rows, toasts, and dense tables usable or scroll-safe on tablet and
  mobile.
- Added a normal-user frontend permission guard so mail-template preview
  polling does not call administrator-only endpoints.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses"`
- Result before documentation close-out: 6 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Playwright authenticated browser validation:
  - administrator dashboard loaded at 1440px with 12 navigation entries;
  - normal user loaded with only `总览`, `舆情监控`, `运行中心`, and `报告中心`;
  - tablet 1024px mobile navigation opened, closed by backdrop, and closed by
    Escape;
  - mobile 390px navigation opened, page switch closed the drawer, and the
    task-create drawer remained reachable;
  - desktop task drawer, run log drawer, report preview drawer, and report
    action menu opened successfully;
  - authenticated administrator and normal-user paths reported no console or
    page errors.

Limitations:

- Phase 11D keeps dense tables scroll-safe on mobile. Full page-specific card
  conversions remain for later page phases.
- Phase 11D does not restructure Resource Management or System Configuration
  popover navigation; that is the next allowed Phase 12A work.

## 2026-06-15 - Phase 11C Interaction Components And Floating Menu Fix Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Added shared toast, loading, empty-state, modal, drawer, and action-menu
  styles to `api/webui/monitor/monitor.css`.
- Added the `window.MonitorUI` helper boundary in
  `api/webui/monitor/monitor.js` for toast, loading, empty-state,
  close-menu, portal-root, and fixed floating-menu positioning helpers.
- Reworked account, monitoring-task, AI-rule, and report row menus to use
  fixed viewport placement and viewport-edge adjustment.
- Kept the no-build Vanilla JavaScript/CSS path and did not introduce a
  floating-position dependency, so no new `DECISIONS.md` entry was required.
- Verified that proxy, AI access, and mail-template surfaces currently use
  direct edit/test/preview actions rather than row menus, so no clipped row-menu
  surface exists there in Phase 11C.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or phase_11c or monitor_page_uses"`
- Result: 5 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Playwright authenticated interaction check:
  - account, monitoring-task, AI-rule, and report row menus used
    `position: fixed`;
  - active menus stayed inside the viewport;
  - outside click and Escape closed menus;
  - page changes and action execution close menus through the shared
    close-menu path;
  - 1024px and 390px smoke checks for monitoring tasks, run center, and report
    center completed without console or page errors.

Limitations:

- Phase 11C does not implement the Phase 11D responsive foundation or mobile
  navigation. Responsive breakpoint and touch-navigation work remains the next
  allowed execution goal.

## 2026-06-15 - Phase 11B Base Layout And Navigation Visual Foundation Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Moved the base desktop shell, side navigation, brand, header, button,
  metric-card, toolbar, page-toolbar, toolbar-actions, and page-actions styling
  into `api/webui/monitor/monitor.css`.
- Kept table, modal, form, report-preview, task-wizard, AI-rule,
  mail-template, and resource-specific styles in the existing inline style
  block for later Phase 11C/11D and page-specific batches.
- Preserved page IDs, navigation data attributes, inline JavaScript behavior,
  business data flow, and administrator/normal-user menu visibility.
- Applied the first low-noise Apple-style desktop foundation through a quieter
  shell width, translucent header, refined navigation spacing, and shared
  button/card/toolbar styling.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or monitor_page_uses"`
- Result: 4 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Playwright desktop 1440px authenticated smoke check:
  login, logout, dashboard, monitoring task list, run center, report center,
  task-create entry, Resource Management popover, and System Configuration
  popover remained reachable; no console errors or page errors were reported.

Limitations:

- Phase 11B does not implement shared interaction helpers, fixed/portal row
  menu positioning, or mobile responsive navigation. Those remain for Phase
  11C and Phase 11D.

## 2026-06-15 - Phase 11A Frontend Module Boundary Verified

Environment: worktree
`E:\myproject\MediaCrawler-worktrees\console-optimization-10-18`, branch
`codex/console-optimization-10-18`, isolated local FastAPI service with
temporary monitor data.

Result:

- Created `api/webui/monitor/monitor.css` with namespaced design-token custom
  properties for color, typography, spacing, radius, shadows, z-index, status
  colors, motion, and breakpoints.
- Created `api/webui/monitor/monitor.js` as a quiet Phase 11A module boundary
  with no console logging, global variables/functions, event listeners, or UI
  behavior.
- Referenced `/static/monitor/monitor.css` before the existing inline
  `<style>` block and `/static/monitor/monitor.js` after the existing inline
  `<script>` block.
- Kept the existing inline CSS/JS in place and did not introduce an intentional
  visual redesign in this batch.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or monitor_page_uses"`
- Result: 3 passed, 214 deselected, 4 warnings.
- Runtime HTTP check on isolated service:
  - `/monitor`: HTTP 200;
  - `/static/monitor/monitor.css`: HTTP 200;
  - `/static/monitor/monitor.js`: HTTP 200.
- Playwright authenticated smoke check at 1440px, 1024px, and 390px:
  dashboard, monitoring task list, run center, report center, and task-create
  entry remained reachable; no console errors or page errors were reported.

Limitations:

- Phase 11A only creates the static module boundary and token layer. Base
  layout migration, visible Apple-style visual foundation, shared interaction
  helpers, floating-menu fixes, and responsive navigation remain for Phase
  11B-11D.

## 2026-06-15 - Phase 10-18 Systematic Global Review Reconfirmed

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the systematic global Phase 10-18 audit covering roadmap linkage,
  task landability, granularity, functional completeness, testing,
  acceptance standards, documentation write-back, and execution-goal readiness.
- Accepted the review conclusion that Phase 10-18 has no P0/P1 blockers after
  the previous Phase 13, Phase 17, and Phase 18 granularity refinements.
- Reconfirmed that Phase 11A remains the next allowed execution goal.
- Recorded the remaining findings as P2 implementation refinements:
  - Phase 13A may define more concrete operations-home data sources during
    implementation;
  - Phase 11B may add more quantified Apple-style visual references during
    token/layout implementation;
  - Phase 11C may define exact `MonitorUI` API signatures with JSDoc during
    implementation;
  - later Phase 12-18 batches may extend phase-specific regression checklists
    as implementation evidence accumulates.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only review confirmation. No Phase 11A code
  implementation was performed.

## 2026-06-15 - Phase 10.5 Global Review Verified

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the follow-up Phase 10-18 global plan复审.
- Accepted the conclusion that the revised roadmap has no remaining P0/P1
  blockers.
- Confirmed remaining review notes are P2 refinements that can be handled
  during implementation.
- Marked Phase 10.5 review tasks complete in `TASKS.md`.
- Updated `CURRENT_STATE.md` so Phase 11A is the next allowed execution goal.
- Updated `TRACEABILITY.md` so CR-028 is verified.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only gate verification. No Phase 11A code
  implementation was performed.

## 2026-06-15 - Phase 10-18 Global Plan Review Follow-Up

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the global Phase 10-18 landability audit.
- Accepted the core finding that Phase 13, Phase 17, and Phase 18 were still
  too coarse as single implementation goals.
- Split Phase 13 into:
  - Phase 13A Operations Home Data Layer;
  - Phase 13B Operations Home Desktop Visual Metrics;
  - Phase 13C Operations Home Responsive And Role Views.
- Split Phase 17 into:
  - Phase 17A Email Idempotency And Delivery Logic;
  - Phase 17B Email Delivery History Frontend.
- Split Phase 18 into:
  - Phase 18A Report Job Snapshot Data Model;
  - Phase 18B Report Center Task Grouping Frontend.
- Strengthened Phase 11B/11C/11D, Phase 12A/12B, Phase 13, Phase 17, and
  Phase 18 implementation boundaries in `FRONTEND_ARCHITECTURE.md`.
- Added explicit Phase 14 index and Phase 15 run-list response compatibility
  tasks.
- Added matching Phase 13A-C, Phase 17A-B, and Phase 18A-B verification
  coverage to `TEST_PLAN.md`.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only plan refinement. It does not complete Phase 10.5
  and does not implement Phase 11-18 code.

## 2026-06-15 - Global Phase 10-18 Plan Review Gate Added

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Accepted the user's correction that Phase 10-18 review must be global and
  cross-phase, not a Phase 11A-only readiness review.
- Added CR-028 for the global Phase 10-18 plan review gate.
- Added Phase 10.5 to `TASKS.md` as a documentation-only review gate before
  Phase 11 implementation.
- Updated `AGENTS.md` and `AGENT_WORKFLOW.md` so agents must review the whole
  roadmap before generating a phase-specific execution goal.
- Updated `FRONTEND_ARCHITECTURE.md` with cross-phase impact review points
  covering Phase 11 through Phase 18.
- Updated `TEST_PLAN.md`, `TRACEABILITY.md`, and `CURRENT_STATE.md` so the
  global review gate is tracked, testable, and reflected as the current next
  step.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only governance update. It does not complete the
  Phase 10.5 global plan review and does not implement Phase 11A code.

## 2026-06-15 - Phase 11A Goal Boundary Tightening

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the Phase 11A execution readiness audit and accepted its conclusion
  that Phase 11A can be prepared as a bounded goal.
- Tightened Phase 11A documentation before implementation:
  - `monitor.css` must use new namespaced tokens such as `--color-*`,
    `--space-*`, and `--font-*`;
  - Phase 11A must not define legacy aliases such as `--bg`, `--surface`,
    `--primary`, or `--radius`;
  - legacy aliases are deferred to Phase 11B when inline styles are migrated;
  - `monitor.js` must not define global variables/functions, log to console, or
    execute UI behavior in Phase 11A;
  - 1440px desktop, 1024px tablet, and 390px mobile layouts must remain
    unchanged.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only follow-up. No Phase 11A code implementation was
  performed.

## 2026-06-15 - Phase 11A Execution Readiness Review Follow-Up

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the implementation-granularity audit that marked Phase 11A safe to
  execute as a bounded goal.
- Accepted the audit conclusion that Phase 11A is small enough for one goal:
  create `monitor.css`, create `monitor.js`, reference both from
  `api/monitor_web/index.html`, define tokens, and keep visible UI unchanged.
- Added more precise Phase 11A execution rules:
  - `monitor.css` should load before the existing inline `<style>` block;
  - `monitor.js` should load after the existing inline `<script>` block;
  - `monitor.js` should remain quiet and avoid console logging or UI behavior
    in Phase 11A;
  - rollback is limited to removing the two static references and the two new
    files.
- Accepted the P2 note that Phase 11C may need a lightweight floating-position
  library, but kept that as a Phase 11C decision that must be recorded in
  `DECISIONS.md` before adding any dependency.
- Accepted the P2 note that Phase 11D mobile navigation needs a concrete
  direction and documented top-left hamburger plus left-side drawer as the
  default direction.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a documentation-only follow-up. No Phase 11A code implementation was
  performed.

## 2026-06-15 - Phase 11/12/15 Granularity Planning Refinement

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Reviewed the implementation-readiness audit and accepted the finding that
  Phase 11 was too large for one safe goal.
- Split Phase 11 into:
  - Phase 11A module boundary and CSS token layer;
  - Phase 11B base layout and navigation visual foundation;
  - Phase 11C interaction components and floating menu fix;
  - Phase 11D responsive foundation.
- Split Phase 12 into:
  - Phase 12A navigation structure and login landing;
  - Phase 12B page entry and role flow.
- Split Phase 15 into:
  - Phase 15A run center API and data governance;
  - Phase 15B run center frontend refinement.
- Added regression-protection guidance to `FRONTEND_ARCHITECTURE.md` so Phase
  11 batches protect login/logout, navigation, task list, run center, report
  preview, account login entry, resource pages, modals, toasts, and role-based
  menu visibility.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- This is a planning refinement only. No Phase 11 code implementation was
  performed.

## 2026-06-15 - Phase 10 Frontend Architecture Decision Complete

Environment: local repository documentation and source-structure audit in
`E:\myproject\MediaCrawler`.

Result:

- Completed the Phase 10 architecture decision without implementing UI code.
- Verified `AGENTS.md`, `AGENT_WORKFLOW.md`, and `scripts/check_docs.py`
  include `FRONTEND_ARCHITECTURE.md`.
- Audited the current monitor frontend structure:
  - `/monitor` serves `api/monitor_web/index.html`;
  - the monitor console is a single inline HTML/CSS/JavaScript file over 4,000
    lines long;
  - current responsive behavior relies mainly on coarse `1100px` and `720px`
    breakpoints;
  - `/static` is already available for local static assets through FastAPI.
- Recorded the Phase 11 implementation direction: keep the `/monitor` entry
  and no-build deployment path, but introduce local CSS/JS module boundaries
  for the design-system layer before broad UI rewrite.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- No frontend visual, interaction, or responsive implementation was changed.
- Phase 11-18 remain planned and unimplemented.

## 2026-06-15 - Phase 10-18 Console Optimization Planning

Environment: local repository documentation update in `E:\myproject\MediaCrawler`.

Result:

- Added Phase 10-18 documentation planning for console-wide optimization.
- Accepted CR-019 to CR-027 covering navigation, design system, operations
  home, run center governance, report grouping, email delivery governance,
  email delivery tracking data model, run visibility data model, and frontend
  technology stack.
- Added `FRONTEND_ARCHITECTURE.md` with the accepted Vanilla JavaScript plus CSS
  custom properties direction, responsive breakpoints, navigation strategy,
  table/modal/floating-menu patterns, and operations-home architecture.
- Updated product, UI/UX, data model, schema migration, tasks, current state,
  traceability, and test planning documents for Phase 10-18.
- Synchronized `AGENTS.md`, `AGENT_WORKFLOW.md`, and `scripts/check_docs.py`
  so the new frontend architecture document is discoverable by agents and
  documentation checks.

Verification:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Limitations:

- No Phase 10-18 application code or database migration was implemented.
- The current web console remains the pre-redesign implementation until the
  planned phases are executed.

## 2026-06-14 - Phase 9 Security And Operations Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and automated readiness/doctor
diagnostic checks.

Result:

- Added minimal administrator-operation audit logging for resource and
  security-sensitive operations, including platform login configuration,
  platform accounts, login sessions, proxy resources, AI profiles/rules, mail
  configuration/templates, runtime settings, and administrator-triggered report
  resend.
- Kept audit details intentionally small and non-secret; tests verify API keys,
  SMTP passwords, proxy credentials, and cookies are not written to audit
  logs.
- Hardened sensitive text redaction for encrypted-field names, proxy URLs, and
  Chinese secret labels such as password, key, token, cookie, and proxy address.
- Added account invalidation and proxy-error alert paths to readiness checks.
- Added disk-space, retention-setting, backup-set, and resource-alert checks to
  doctor diagnostics.
- Updated deployment guidance so database, account profiles, reports,
  encryption key, and deployment configuration are explicit backup targets.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_9 or doctor_reports_deployment_diagnostics or readiness_status_reports_checks or sensitive_text_is_redacted"`
- Result: 6 passed, 210 deselected, 1 warning.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 216 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed.

Limitations:

- Phase 9 does not add automated retention cleanup jobs; retention settings and
  diagnostics are visible, while cleanup execution remains future operations
  work.
- Real account invalidation, proxy-provider behavior, SMTP delivery, AI
  provider behavior, and platform crawling still require live pilot validation.

## 2026-06-14 - Phase 8 Server-Like Validation Verified

Environment: isolated server-like service process in local worktree
`E:\myproject\MediaCrawler-worktrees\v1-roadmap` using `uv run`, a temporary
persistent data directory, real FastAPI/uvicorn HTTP service startup,
production login flags, and headless Playwright Chromium.

Result:

- Added `scripts/server_like_validation.py` to start the real FastAPI app with
  isolated persistent data/profile roots and production-oriented environment
  flags.
- Verified `/monitor` is reachable over HTTP and a bootstrap administrator can
  log in through the API.
- Verified web QR/status login capability is advertised as the primary
  `server_qrcode` flow while local-window login is hidden and blocked with
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.
- Verified two same-platform accounts receive separate `profile_key` values
  and runtime profile paths under the persistent account-profile root.
- Verified profile metadata survives service restart.
- Verified account/profile locks and proxy concurrency limits through the
  runtime lock APIs, with proxy locks backed by `resource_locks`.
- Verified the automated validation path does not require the operator's local
  Chrome and that Playwright Chromium can launch headless.

Verification:

- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed.

Limitations:

- Docker/container validation could not be performed on this machine, so Phase
  8 used an isolated real service process as the server-like path.
- The automated run verifies the web QR/status path and production local-login
  gating, but it does not complete a real platform QR scan or real platform
  crawl with a live account.
- Real AI provider, SMTP, platform login, and platform crawling behavior remain
  deployment/pilot validation risks.

## 2026-06-14 - Phase 7 Runs Reports And AI Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Verified that a monitoring run can finish and generate a report when AI is
  disabled and email sending is unavailable.
- Verified AI-disabled or AI-failure content is stored as `pending_review`
  manual-review material instead of blocking report generation.
- Verified report wording keeps "疑似负面线索" and "AI 仅作线索筛查，不代表事实认定"
  semantics.
- Verified selected report previews load leads scoped by `report_id`.
- Verified run-log UI keeps refresh, copy, and download controls and log API
  output remains customer-safe.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 213 passed, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_7 or pending_review or report_scope or monitor_page_uses_tob"`
- Result: 4 passed, 209 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 7 verification uses local and mocked execution paths where external
  platform, AI provider, or SMTP behavior would otherwise be required.
- Real provider/SMTP reliability and end-to-end server deployment remain pilot
  and Phase 8 validation risks.

## 2026-06-14 - Phase 6 Server Login Flow Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Made server-side QR login the primary administrator account-login flow.
- Added structured login-session states: `preparing`, `waiting_qrcode`,
  `waiting_scan`, `waiting_confirm`, `success`, `needs_verification`,
  `qrcode_failed`, `timeout`, and `platform_error`.
- Normalized legacy login states for compatibility while returning structured
  states to the API and frontend.
- Kept login sessions tied to Phase 5 `profile_key` runtime paths, closed the
  server browser after successful login, and re-checked existing profiles
  before marking accounts active.
- Hid local-window login controls and blocked the local-window login endpoint
  when `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`.
- Updated deployment and account-environment documentation for the production
  login boundary.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 212 passed, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "login_session or qrcode or phase_6 or local_login"`
- Result: 34 passed, 178 deselected, 1 warning.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m py_compile api/monitoring/database.py api/monitoring/login_qrcode.py api/monitoring/login_status.py api/routers/monitor.py`
- Result: Python compile check passed.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 6 verification is local and mocked where platform login would require
  real QR scanning. It does not replace Phase 8 server-like acceptance.
- Service/container restart validation, no-local-Chrome production acceptance,
  and real profile reuse across restart remain Phase 8 tasks.

## 2026-06-14 - Phase 5 Account Environment Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Added a `profile_key` runtime path resolver for
  `{workspace_id}/{platform}/acc_{account_id}` account profiles.
- Changed new account environments so arbitrary submitted profile paths are not
  the account identity; account names remain display-only.
- Kept real profile paths internal to crawler/login/check code paths while
  customer-facing account, run, and login-session responses use profile-key or
  configured-state wording instead of raw server paths.
- Added account/profile lock acquisition and release through
  `social_accounts.locked_by_run_id`, `locked_at`, and `lock_expires_at`.
- Added proxy concurrency control through `resource_locks` with
  `proxy_profiles.max_concurrency`.
- Added startup and scheduler recovery for timed-out running runs and persisted
  locks, releasing locks only after the owning run is terminal or recovered.
- Ensured account-bound proxy information is passed into both login command
  preparation and crawler execution.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 211 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 5 does not implement the full Phase 6 structured server-login state
  machine or production-mode local-login hiding.
- Phase 5 does not complete server-like acceptance validation; profile reuse
  across service/container restart remains Phase 8 acceptance work.

## 2026-06-14 - Phase 4 Normal User Task Wizard Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Replaced the normal-user task creation experience with a four-step wizard:
  target, collection content, schedule, and report.
- Included law firm, aliases, platform search terms, selected platforms, crawl
  range, comment collection, frequency/send time, enabled state, and recipient
  emails in the normal-user path.
- Added crawl range copy explaining that max items is a content-count cap,
  start page and max pages depend on platform behavior, and task timeout is
  controlled by administrator Runtime Strategy.
- Hid account binding, proxy binding, AI access override, email template
  override, output mode, target type, and browser mode from normal users.
- Added API-side normal-user payload cleanup so advanced task fields are
  ignored even if a normal user submits them directly.
- Kept administrator advanced task settings available and verified that
  administrator submissions still persist advanced bindings.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 207 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 4 does not implement Phase 5 account/profile/proxy runtime locking or
  `profile_key` path resolution.
- Phase 4 does not make server-side QR login the primary production login
  flow; that remains Phase 6 after the account environment is complete.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Phase 3 Administrator Resource Center Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Refined the administrator resource center UI for platform accounts, proxy
  resources, AI access, mail configuration, and mail templates.
- Kept platform accounts in the existing account-detail dialog with account
  resource metrics, filters, login maintenance, Cookie maintenance, proxy
  binding, bulk actions, and customer-safe login state text.
- Added proxy resource summary cards, search/status filters, and consistent
  modal action footer for create/edit.
- Added AI access summary cards, search/protocol/test-status filters,
  consistent modal action footer for create/edit, and retained the dedicated
  connection-test dialog without exposing raw API keys.
- Changed mail configuration to use edit/test dialogs, summary cards, masked
  password behavior, and a test console that records success or failure without
  blocking report generation.
- Added mail-template summary cards, search/status filters, live preview, and
  consistent modal actions.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 206 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 3 is a resource-center UI and interaction refinement. It does not
  implement Phase 4 simplified normal-user task wizard, Phase 5
  profile-key/lock runtime behavior, Phase 6 primary server-side login flow, or
  Phase 8 server-like acceptance validation.
- Proxy connection testing remains outside Phase 3 because the current product
  and API surface only define create/edit/disable/delete for proxy resources;
  no new proxy test requirement was accepted in this phase.

## 2026-06-14 - Phase 2 System Settings Center Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Added database-backed runtime settings with defaults, `monitor.yaml` loading,
  database overrides, validation ranges, apply scopes, environment locks, and
  audit logging.
- Added administrator-only `/api/monitor/runtime-settings` read/update APIs and
  a grouped Runtime Strategy page for Crawling, Login, Scheduler, and
  Retention settings.
- Kept Runtime Strategy inaccessible to normal users through both API role
  checks and menu permissions.
- Moved scheduler tick/disable, global crawl concurrency, per-platform
  concurrency, crawler timeout, crawler retry count/delay, QR timeout, login
  session TTL, lock cleanup buffer, and retention settings into the runtime
  settings layer.
- Changed newly started crawl runs to store `timeout_seconds` and
  `deadline_at`, allocate remaining run time to platform crawler attempts, and
  mark deadline-exceeded runs as `timeout` while preserving partial platform
  summaries.
- Updated safe environment examples with the deployment-lock variables for
  Phase 2 runtime settings.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 206 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 2 does not implement Phase 3 administrator resource-page refinements,
  Phase 4 simplified normal-user task wizard, Phase 5 persisted
  account/profile/proxy lock acquisition, or Phase 6 primary server-login flow.
- Retention settings are configurable and visible, but automated cleanup jobs
  remain for later operations work.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Phase 1 Users And Permissions Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run`, the monitoring SQLite database, and Node script parsing for the
single-file frontend.

Result:

- Implemented environment-bootstrap administrator creation and bcrypt password
  hashing.
- Added session-based authentication with HTTP-only `monitor_session` cookie
  and hashed session tokens in `user_sessions`.
- Added `/api/auth/login`, `/api/auth/logout`, `/api/auth/session`, and
  administrator-only `/api/users` management endpoints.
- Added shared FastAPI authentication and role dependencies.
- Protected `/api/monitor/*` routes with session authentication.
- Restricted platform accounts, proxies, AI, mail, login sessions, system
  diagnostics, smoke/system checks, and resource operations to administrators.
- Scoped normal-user jobs, runs, reports, and leads to the owning user in the
  default workspace.
- Added frontend login screen, session check, current-user badge, logout, and
  role-based navigation/menu visibility.
- Implemented `scripts/check_docs.py`.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 200 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- Node syntax check for the `api/monitor_web/index.html` script block
- Result: monitor web script parses.

Limitations:

- Phase 1 does not implement runtime settings, simplified normal-user task
  wizard, profile-key runtime resolver, server-side QR login primary flow, or
  server-like acceptance validation. These remain for Phase 2 and later phases.
- Local development cookie settings still use `secure=false`; production HTTPS
  cookie behavior remains part of server-like validation and deployment work.

## 2026-06-14 - Phase 0.5 Schema Foundation Verified

Environment: local worktree `E:\myproject\MediaCrawler-worktrees\v1-roadmap`
using `uv run` and the monitoring SQLite database.

Result:

- Implemented Phase 0.5 foundation schema in `api/monitoring/database.py`.
- Created `workspaces`, `users`, `user_sessions`, `system_settings`,
  `audit_logs`, and `resource_locks`.
- Added `workspace_id`, `created_by`, and `updated_by` to priority business
  tables.
- Added `profile_key` to `social_accounts` and `login_sessions`, including
  default key backfill and inheritance for new account login sessions.
- Added run timeout fields to `crawl_runs`: `timeout_seconds`, `deadline_at`,
  and `timeout_reason`.
- Added account/profile lock fields to `social_accounts`:
  `locked_by_run_id`, `locked_at`, and `lock_expires_at`.
- Verified default workspace backfill with `workspace_id = 1`.
- Verified existing MVP tasks, social accounts, login sessions, runs, and
  reports still load after migration.

Verification:

- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 198 passed, 3 warnings.

Limitations:

- Phase 0.5 adds schema and minimal profile-key persistence only. Full
  authentication, RBAC, runtime settings UI, runtime lock acquisition,
  timeout enforcement, and server-like login validation remain for later
  phases.
- No server-like acceptance validation was performed in this phase.

## 2026-06-14 - Documentation Review Follow-Up For Timeout And Range

Environment: local repository documentation update.

Result:

- Added a concrete run-level timeout example showing remaining-time allocation
  across platform crawler attempts.
- Clarified that current MVP timeout is subprocess-level and Phase 2 should
  migrate it to a run-level wall-clock deadline.
- Added startup and scheduler recovery implementation guidance for stale
  running runs and persisted locks.
- Added crawl range platform capability matrix for Douyin, Xiaohongshu, and
  Kuaishou.
- Added Phase 0.5 monitoring API response-shape regression checks.
- Added YAML-to-database runtime settings mapping.

Limitations:

- No code or runtime validation was performed.
- The review item claiming CR-012A/B/C were missing from `TRACEABILITY.md` was
  not applied because the current matrix already contains separate accepted
  CR-012A, CR-012B, and CR-012C rows.

## 2026-06-14 - CR-012 Timeout Lock And Crawl Range Documentation

Environment: local repository documentation update.

Result:

- Accepted CR-012A profile key format:
  `{workspace_id}/{platform}/acc_{account_id}`.
- Accepted CR-012B as run-level wall-clock timeout plus lock cleanup buffer.
- Accepted CR-012C as inline account/profile locks plus `resource_locks` for
  proxy concurrency.
- Accepted CR-017 Runtime Strategy administrator-only grouped table layout.
- Added CR-018 for crawl range capability boundaries.
- Updated data model, schema migration, system settings, product requirements,
  UI guidelines, traceability, tasks, and tests.

Limitations:

- No code or runtime validation was performed.
- Phase 0.5 schema foundation is still not implemented.

## 2026-06-14 - Review Follow-Up Minor Documentation Gaps

Environment: local repository documentation update.

Result:

- Clarified documentation check script timing as Phase 1 close-out.
- Added bootstrap administrator login checks to the test plan.
- Added recommended container base image guidance.
- Added `.gitignore` validation for `monitor.yaml`.
- Added Quick Index maintenance and superseded-decision rules to agent
  workflow.
- Added CR-017 for Runtime Strategy page layout confirmation.

Limitations:

- No code or runtime validation was performed.
- CR-017 remains pending user confirmation before Phase 2 UI implementation.

## 2026-06-14 - Attached Review Follow-Up

Environment: local repository documentation update.

Result:

- Strengthened Phase 0.5 wording as a blocking prerequisite before Phase 1-9.
- Added explicit current-code gaps for missing auth/workspace/settings/profile
  schema and hard-coded scheduler/concurrency settings.
- Added migration regression checks for existing monitoring APIs, scheduler,
  runs, and reports.
- Added server QR login headless/container validation checks.
- Added code-document consistency checks to `DOCUMENTATION_CHECKS.md`.
- Added container build requirements and current frontend technology-stack
  guidance.
- Added CR quick index and CR-016 to preserve the review follow-up in the
  documentation loop.

Limitations:

- No code or runtime validation was performed.
- Phase 0.5 schema foundation is still not implemented.
- Phase 5/6 still need CR-012A, CR-012B, and CR-012C confirmation.

## 2026-06-14 - Review Follow-Up Documentation Hardening

Environment: local repository documentation update.

Result:

- Clarified implementation status: Phase 0.5 is not started and is required
  before Phase 1.
- Split CR-012 into CR-012A, CR-012B, and CR-012C for profile key format, lock
  timeout, and lock storage confirmation.
- Added Phase 0.5 schema foundation tests and standard permission test data.
- Added `DOCUMENTATION_CHECKS.md` as the future documentation consistency
  script specification.
- Added parallel-document merge protocol, authentication/error UI states,
  runtime settings page layout, and encryption key management guidance.

Limitations:

- No code or runtime validation was performed.
- Phase 5/6 remain blocked until CR-012A, CR-012B, and CR-012C are confirmed.

## 2026-06-14 - Phase 0.5 Documentation Alignment

Environment: local repository documentation update.

Result:

- Added Phase 0.5 schema foundation to the implementation task list.
- Updated current-state wording so Phase 1 is no longer shown as blocked by
  accepted permission decisions.
- Split accepted account/profile migration direction from still-unconfirmed
  account/profile/proxy lock details.
- Aligned runtime settings documentation with `monitor.example.yaml`, including
  `scheduler.disabled`.
- Clarified that MVP includes minimal audit logs and session-based
  authentication fields.
- Added `API_AUTHENTICATION.md` and `SERVER_DEPLOYMENT.md` for Phase 1 and
  Phase 8 implementation guidance.

Limitations:

- No application runtime validation was performed.
- Phase 5/6 still need confirmation for final `profile_key` format, lock
  timeout behavior, and lock table vs lock fields.

## 2026-06-14 - Permission Confirmation Accepted

Environment: local repository documentation update.

Result:

- Marked permission confirmation items C-001 to C-007 as accepted.
- Confirmed single-workspace V1, session auth, environment bootstrap admin,
  normal-user task deletion, normal-user report resend, disabled-user task
  behavior, and minimal MVP audit log.
- Confirmed flexible key-value system settings table.

Limitations:

- Profile key format and lock timeout details still need confirmation before
  coding the account/profile locking layer.
- No code or runtime validation was performed.

## 2026-06-14 - Profile Migration Decision Updated

Environment: local repository documentation update.

Result:

- Updated account environment and schema migration documents to reflect the
  confirmed direct-new-profile migration direction.
- Added workspace explanation to the permission confirmation document.

Limitations:

- At the time of this entry, workspace strategy was not yet confirmed; it was
  later accepted as single-workspace V1.
- No code or runtime validation was performed.

## 2026-06-14 - Review Follow-Up P0 Additions

Environment: local repository documentation update.

Result:

- Added permission confirmation pack.
- Added compatible schema migration plan.
- Added `monitor.example.yaml`.
- Updated document routing, traceability, current state, decisions, and tasks.

Limitations:

- Confirmation items remain unresolved.
- No code or runtime validation was performed.

## 2026-06-14 - P0 Specialist Documents Added

Environment: local repository documentation update.

Result:

- Added roles and permissions specification.
- Added account environment specification.
- Added runtime settings specification.
- Added target data model planning document.
- Updated document routing and traceability.

Limitations:

- Several high-impact assumptions remain marked as needing user confirmation.
- No application runtime validation was performed.

## 2026-06-14 - Confirmation Gate Added

Environment: local repository documentation update.

Result:

- Added confirmation-gate rule to agent workflow.
- Updated agent entry instructions.
- Added CR-004 and traceability entry.

Limitations:

- No application runtime validation was performed.

## 2026-06-14 - Documentation Loop Expansion

Environment: local repository documentation update.

Result:

- Added menu-level product requirements.
- Added change request intake document.
- Added traceability matrix.
- Added detailed agent workflow document.
- Updated agent entry rules and current state.

Limitations:

- No application runtime validation was performed.
- No server-like acceptance validation has been completed yet.

## 2026-06-14 - Documentation Bootstrap

Environment: local repository inspection only.

Result:

- Added initial governance documents.
- No application runtime validation was performed in this step.
- No server-like acceptance validation has been completed yet.

Next required verification:

- confirm documents are committed to Git;
- run existing tests after the next implementation change;
- create or use a server-like environment for login/profile validation before
  production acceptance.
