# Current State

Last updated: 2026-06-20

## Current Phase

Phase 0 documentation is complete. Phase 0.5 - Schema Foundation is complete
and verified. Phase 1 - Users And Permissions is complete and verified. Phase
2 - System Settings Center is complete and verified. Phase 3 - Administrator
Resource Center is complete and verified. Phase 4 - Normal User Task Wizard is
complete and verified. Phase 5 - Account Environment is complete and verified.
Phase 6 - Server Login Flow is complete and verified locally. Phase 7 - Runs,
Reports, And AI is complete and verified locally. Phase 8 - Server-Like
Validation is complete and verified through an isolated server-like service
process. Phase 9 - Security And Operations is complete and verified locally.
Phase 10-18 console optimization planning has been accepted as the next
roadmap. Phase 10 - Frontend Architecture And Technology Decision is complete
as a documentation and architecture decision phase. Phase 10.5 - Phase 10-18
Global Plan Review Gate is complete and found no P0/P1 blockers after the
granularity refinements. Phase 11 - Frontend Design System is complete and
verified through Phase 11A, Phase 11B, Phase 11C, and Phase 11D. Phase 12A -
Navigation Structure And Login Landing is complete and verified. Phase 12B -
Page Entry And Role Flow is complete and verified. Phase 13A - Operations Home
Data Layer is complete and verified. Phase 13B - Operations Home Desktop
Visual Metrics is complete and verified. Phase 13C - Operations Home
Responsive And Role Views is complete and verified. Phase 14 - Run Center
Data Model Preparation is complete and verified. Phase 15A - Run Center API
And Data Governance is complete and verified. Phase 15B - Run Center Frontend
Refinement is complete and verified. Phase 16 - Email Delivery Data Model
Preparation is complete and verified. Phase 17A - Email Idempotency And
Delivery Logic is complete and verified. Phase 17B - Email Delivery History
Frontend is complete and verified. Phase 18A - Report Job Snapshot Data Model
is complete and verified. Phase 18B - Report Center Task Grouping Frontend is
complete and verified. Phase 10-18 console optimization is complete through
the accepted roadmap. Phase 19A - Requirement Intake Classification Rules is
complete and verified as a documentation-governance update. CR-031 Run Center
Realtime Progress Visibility is implemented and verified through Phase 19B-19D:
running crawler progress is stored in the existing `crawl_runs.summary`
lifecycle/progress shape, AI progress is updated during long batches, and the
Run Center frontend now keeps visible active-run polling alive, labels
provisional collection counts, shows AI evaluated/total progress plus
report/email/timeout/cancel/interrupted states, and preserves administrator and
normal-user scoped visibility. CR-033 Formal
Console Full-Coverage Positive UI Optimization is complete and verified as a
frontend-only pass on the latest formal `/monitor` console; it does not change
backend APIs, database schema, permissions, crawler behavior, AI provider
logic, SMTP delivery, or Phase 19B-19D product scope. The CR-033 pass now also
includes stable secondary drawer/modal button-level loading feedback for
account login, resource saves, AI/mail tests, and template preview actions.
CR-034 Run Detail And AI Evaluation Traceability is implemented and verified
through Phase 20B-D plus the remaining Phase 20E report-to-run backlink: new
evaluations now persist redacted and capped
`ai_evaluation_traces` rows with business input, prompt/request,
provider/model, structured output, response snapshot, fallback/error detail,
duration, and timestamps; `ai_trace_retention_days` is an administrator
runtime setting with a 30-day default and cleanup helper; old evaluations
without trace snapshots return an explicit limited-context state. Phase 20C
adds scoped run-detail APIs for lifecycle overview, crawler logs, collected
contents, paginated/filterable AI evaluations, report links, email-delivery
links, and per-evaluation trace detail. Normal users may see only business-safe
summaries for their own runs, administrators may see redacted debug snapshots,
and no API role may see unredacted raw responses, API keys, authorization
headers, cookies, SMTP passwords, proxy credentials, profile paths, or server
local paths; collection logs and trace text now also redact Windows paths with
spaces, Unix absolute paths, residual path fragments, and implementation-only
path field names. Phase 20D adds the Run Center `详情` entry and a run-scoped
detail drawer with Overview, Collection Logs, Collected Contents, AI
Evaluation, Report, and Email Delivery sections; every AI evaluation row can
open role-safe input/output trace detail in the same run detail surface.
Phase 20E now links report-scoped leads with `run_id` back to the originating
run detail while keeping old/no-run rows as limited-context and preserving the
CR-048/CR-049 Report Center and delivery-history information architecture.
CR-051 Task Center And Report Grouping Consolidation is implemented and
verified as a frontend information-architecture follow-up: the formal console
now exposes one top-level `任务中心` entry instead of separate Run Center and
Report Center entries, opens by default on the existing report-by-monitoring-
task grouping, and keeps the old run-record table as a `运行记录` subview for
run ID, task ID, type, visibility, duration, full failure reason, stop/log/
archive/restore, and Run Detail operations. The first-level task-group view
prioritizes monitoring-task identity and public-opinion result summaries
rather than copying every run-record field. Report preview, report-scoped
lead inspection, delivery history, resend, downloads, and Run Detail remain
reachable from the task-group surface while CR-048/CR-049 scoped drawers
remain secondary detail.
CR-053 Task Center Field Priority And Global Select Alignment is implemented
and verified as a frontend density/interaction follow-up: flat Task Center run
tables now begin with `任务 ID`, `运行 ID`, and compact `状态`; grouped mode
hides the duplicated `任务 ID` column because the group header carries task
identity, and group rows begin with `运行 ID` followed by compact `状态`;
completed rows no longer carry long ingestion detail in the status cell; the
filter toolbar keeps only the page-level Task Center refresh entry; and the
main content container no longer clips native select/dropdown overflow,
fixing the global dropdown misalignment reported in the browser.
CR-054 Task Center Status Badge Compactness Regression Fix is implemented and
verified as a focused follow-up to CR-053: Task Center status badges now use
normalized short lifecycle labels instead of raw long `display_status`
strings, so completed rows render as `已完成` even when backend progress
metadata includes ingestion detail; active rows may still show one short
progress cue below the badge, while full progress remains in Run Detail.
CR-055 Task Center Status Column Visual Refinement is implemented and verified
as a small frontend follow-up to CR-054: Task Center run tables now mark status
columns with a stable `col-status` class and render first-level run statuses as
Task Center-specific narrow state-dot badges rather than the global heavy
`.status` pill, keeping task/run identifiers visually prioritized.
CR-056 Filter Dropdown Alignment Regression Fix is implemented and verified as
a follow-up to CR-053 after browser review found filter dropdowns could still
misalign at `1440x900`: filter toolbar selects now keep their original select
values and filtering semantics, but render the visible dropdown as a
fixed-position in-page menu scoped to `.page-filter-region`; ordinary form
configuration selects remain native. CR-057 Task Center Group Summary Metric
Chips is implemented and verified as a frontend-only density refinement:
grouped Task Center headers now render the former long slash-separated
aggregate sentence as compact labeled metric chips while preserving the same
counts, grouped table, filters, Run Detail entry, and dropdown behavior.
CR-058 Filter Date Picker Alignment Regression Fix is implemented and verified
as a follow-up to CR-056; CR-059 through CR-067 are retained as verified
historical positioning attempts for the same date-filter surface. CR-068 Filter
Date Picker Local Attached Menu Regression Fix is the current visual rule:
page-level filter date inputs inside `.page-filter-region` keep their original
date values and `change` semantics, but render the active date menu inside the
clicked `.filter-date-enhanced` wrapper with local absolute positioning. The
menu opens directly under the clicked field, matches the trigger width, keeps
the top anchor marker centered, and preserves the seven-column day grid without
clipped day numbers. Ordinary form/configuration date inputs remain native. The
CR-069 verification pass now also confirms the Run Detail `AI 评估` filters use
the same page-filter dropdown treatment, and `报告范围` is shown as a selectable
filter only when the current run has multiple reports; zero-report or
single-report runs use a read-only scope note. CR-071 Drawer And Modal Select
Dropdown Consistency is implemented and verified as a focused frontend-only
follow-up: selected secondary drawer/modal `select` fields now explicitly
reuse the existing `.page-filter-region select` enhancement and `.filter-select-*`
menu classes, including Monitoring task edit, Platform Account detail, Proxy
edit, AI Access edit, AI Evaluation Rule edit, Mail Configuration edit, and
Mail Template edit. AI Access `模型名称` remains the existing combobox, and
dynamic option/disabled-state updates synchronize the visible enhanced labels.
CR-072 Task Edit Custom Date Picker Consistency now layers the Monitoring task
edit drawer's `自定义开始日期` and `自定义结束日期` onto the existing
`.page-filter-region input[type="date"]` enhancement so they use the same
local attached date menu as Task Center filters, while unrelated ordinary date
fields remain native unless separately accepted.
CR-073 Scrollable Drawer Corner Radius Regression Fix is implemented and
verified as a focused frontend-only visual follow-up: shared drawer shells now
keep the rounded outer chrome and top-right close button outside the scroll
container, while content after the header scrolls inside a normalized
`.drawer-scroll-body`; the visible scrollbar therefore begins below the header
instead of at the absolute drawer top edge, and CR-038 sticky close,
CR-071 enhanced selects, and CR-072 task edit date picker behavior are
preserved.
CR-074 Console Refresh Action Deduplication And Icon Loading is implemented
and verified as a focused frontend-only interaction-density follow-up: the
formal console now uses one top-bar current-page refresh icon for page-level
reloads, removes duplicate page-header/filter-toolbar refresh buttons that
loaded the same data, keeps semantically scoped refresh actions as icon-only
controls for schedule recomputation, delivery history, template preview, run
logs, and Run Detail, and shows disabled/loading spin feedback while refresh
work is pending.
The first focused CR-040 / Phase 21 navigation visual pass is also implemented
and locally verified: the formal console sidebar now uses the current light
enterprise shell, compact icon-supported first/second-level entries, a desktop
collapse-to-icon rail, and a compact top-right account menu. Navigation hover
and active states are explicitly separated so first-level, second-level, and
collapsed sidebar hover use a pure neutral light-gray surface while selected
entries keep the restrained Phase 21 teal active state; the combined
active/hover selector that made second-level hover look selected has been
removed. CR-075 responsive navigation consistency is also verified: desktop
keeps the full/collapsible sidebar, tablet/narrow desktop uses the persistent
collapsed icon side rail without the top-left mobile trigger, and mobile keeps
the drawer trigger with working backdrop/Escape/page-selection close behavior.
CR-076 is verified as a focused mobile-header regression fix after browser
review found a narrow state where the title could be squeezed into
one-character vertical wrapping: the mobile header now gives navigation,
title, status, refresh, and account controls explicit grid areas, with the
title and status chips on their own readable rows. This pass preserved
administrator/normal-user menu
visibility, the single top-level `任务中心`, Task Center grouping and
`运行记录`, Run Detail six sections, enhanced select/date behavior,
`.drawer-scroll-body`, and top-bar refresh.
CR-077 is also verified as the follow-up cascade-resilience fix for the same
mobile header surface: because the formal page has inline style blocks after
`monitor.css`, the accepted mobile header grid is now mirrored in the final
inline style layer and regression tests inspect all inline style blocks. In-app
browser verification at mobile, tablet, and desktop widths confirmed the title
stays horizontal, mobile drawer behavior remains intact, tablet/narrow desktop
keeps the icon rail without the top-left mobile trigger, and representative
resource-page content has no right-side horizontal overflow.
CR-078 is verified as an additional Phase 21B responsive-shell regression fix:
the final mobile cascade now locks the header title to horizontal writing, keeps
the closed mobile drawer off-canvas without visible width reservation, constrains
representative resource pages such as `代理资源` to the phone viewport while
leaving dense tables scrollable only inside `.table-wrap`, and separates the
tablet collapsed side-rail navigation row from the bottom collapse button so
`系统诊断` remains directly clickable at `1024x768`.
CR-079 is verified as the follow-up mobile-header compact-rail fix after phone
browser review still found a resource-page state that could squeeze the product
title into a one-character column: the mobile header now uses a stable 40px
icon navigation trigger, keeps `舆情监控运营后台` in the first-row title column,
and lets status chips wrap on their own row. Browser checks on `代理资源`
confirmed the document width stays inside the effective phone viewport and no
narrow Chinese text columns are detected. Task Center, Run Detail, enhanced
select/date controls, `.drawer-scroll-body`, mobile drawer close behavior,
owner/report scope, and top-bar refresh semantics remain unchanged.
CR-080 is verified as a focused Phase 21B side-rail cleanup after browser
review of a `1169px` tablet/narrow-desktop viewport: the persistent collapsed
icon rail no longer exposes a bottom horizontal scrollbar, while the existing
sidebar collapse button remains available, the side-rail navigation remains
vertically scrollable, and the final administrator entry still hit-tests to its
navigation button. Desktop `>=1280px` keeps the expanded/collapsible sidebar,
and true mobile `<768px` keeps the drawer trigger and close behavior. Task
Center, Run Detail, enhanced select/date controls, `.drawer-scroll-body`,
owner/report scope, role visibility, and top-bar refresh semantics remain
unchanged.
CR-086 is verified as a focused Phase 21 visual-density optimization: targeted
explanatory helper copy in formal console page headers, labels, resource
headers, account cells, Task Center, Monitoring, and representative overlays
now uses a consistent neutral `?` tooltip with hover, keyboard focus, and click
access. The original helper copy remains available in tooltip content while
operational state, errors, warnings, counts, empty/loading feedback, buttons,
filters, row actions, downloads, refresh, save/test, and confirmation flows
remain visible or reachable. Task Center, Run Detail six sections, enhanced
select/date controls, `.drawer-scroll-body`, close behavior, owner/report
scope, role visibility, and top-bar refresh semantics remain unchanged.
CR-087 is verified as the current follow-up rule after user acceptance
review: the CR-086 `?` helper-tooltip affordance has been removed, the removed
explanatory small helper copy is not restored, and operational state plus
required actions remain visible. Task Center, Run Detail six sections,
enhanced select/date controls, `.drawer-scroll-body`, close behavior,
owner/report scope, role visibility, and top-bar refresh semantics remain
unchanged.
CR-088 is verified as the immediate AI rule modal follow-up: the `AI 状态`
line, the legacy-prompt notice, and the default empty result hint were removed
from the `AI 评估规则` modal, while the rule sections, sample inputs, test
action, save action, and rendered test output remain intact.
The CR-088 browser and docs checks are also reflected in `TEST_RESULTS.md`,
`TRACEABILITY.md`, `TASKS.md`, and `TEST_PLAN.md`, so the current verified
state now treats the AI rule modal as a compact edit-and-test surface rather
than a small-helper-text surface.
CR-089 is verified as the current mail-template follow-up: the mail template
list no longer shows the `正文占位符已保留` row helper sentence, and the
`更新时间` cell now uses the compact AI-rule-style timestamp treatment so the
table stays dense without changing template actions or placeholder guardrails.
The CR-089 browser and docs checks are reflected in `TEST_RESULTS.md`,
`TRACEABILITY.md`, `TASKS.md`, and `TEST_PLAN.md`.
Phase 21A and Phase 21B are now locally verified as the completed opening
workstreams of the formal console refinement: the global shell/design-token
layer remains a no-build Vanilla JavaScript plus CSS custom-property stack, the
login surface and logged-in pages render without console errors or document
horizontal overflow in the focused checks, administrator and normal-user menu
visibility is preserved, and the navigation hierarchy visually separates the
first-level task-loop pages from the Resource Management/System Configuration
subpages. Browser verification covered administrator and normal-user paths at
desktop, tablet/narrow-desktop, and phone widths, plus an administrator
page-open sweep for `dashboard`, `jobs`, `runs`, `accounts`, `proxies`, `ai`,
`ai_rules`, `email`, `email_templates`, `runtime`, and `doctor`. The verified
CR-080 boundary is explicit: remove the side navigation rail's bottom
horizontal scrollbar, not the sidebar collapse button. Phase 21C Operations
Home refinement is the next unclosed Phase 21 workstream.
Phase 21C Operations Home refinement is also implemented and locally verified:
the dashboard now puts operational metrics, attention state, resource health,
and system-health signals ahead of compact shortcuts; the administrator
shortcut set preserves all five entries (`新建任务`, `任务中心`, `运行记录`,
`资源处理`, and `系统诊断`), while normal users still see only their three
permitted entries. Redundant explanatory dashboard copy was removed from the
attention queue and system-health summary without changing the dashboard API,
metrics, permissions, page routes, Task Center, Run Detail, enhanced
select/date controls, `.drawer-scroll-body`, owner/report scope, or top-bar
refresh behavior. Browser checks covered administrator and normal-user
Operations Home views at desktop, tablet/narrow-desktop, and phone widths with
no console errors, document horizontal overflow, hidden primary shortcuts, or
one-character text columns. Phase 21D Monitoring Tasks and Task Drawer is now
the next unclosed Phase 21 workstream.
Phase 21D Monitoring Tasks and Task Drawer is now implemented and locally
verified: the Monitoring page keeps new task, schedule refresh, Task Center
shortcut, search, platform/status filters, clear filter, task table, run, stop,
and row more-menu edit/pause-resume/delete actions, while the task drawer keeps
all current normal-user and administrator fields. The visual pass only refines
task toolbar chrome, drawer section hierarchy, administrator advanced grouping,
and action-area polish. Normal users still receive the simplified task wizard
with administrator-only fields hidden; administrators still see account/proxy,
technical collection, AI, and template controls. Browser checks covered
administrator and normal-user task page/drawer paths at desktop,
tablet/narrow-desktop, and phone widths, with `.drawer-scroll-body`, close
button behavior, enhanced select/date controls, Task Center, Run Detail,
owner/report scope, and top-bar refresh semantics preserved. Phase 21E Platform
Accounts is now implemented and locally verified: the Platform Accounts page
keeps add account, return-to-tasks, filters, attention-only quick filter, batch
check/disable/enable/delete controls, account list, row detail/action hooks, and
the account-maintenance dialog with basic profile, login maintenance, login
records, final account actions, QR login, local-window fallback, Cookie login,
save, delete, and close controls. The visual pass only refines account-list
chrome, batch-toolbar hierarchy, account filter density, account dialog
sections, login-card hierarchy, and account-drawer overflow containment. Normal
users still do not see Platform Accounts navigation or administrator shortcuts.
Browser checks covered administrator account page/dialog paths at desktop,
tablet/narrow-desktop, and phone widths plus normal-user role visibility; no
console errors, document horizontal overflow, one-character text columns, or
`.drawer-scroll-body` ownership regressions were found. Task Center, Run Detail,
enhanced select/date controls, owner/report scope, and top-bar refresh semantics
remain preserved. Phase 21F Proxy Resources is now implemented and locally
verified: the Proxy Resources page keeps add proxy, view accounts, search,
status filter, clear filters, row edit/delete, drawer clear/save/close, delete
confirmation, and the CR-074 top-bar current-page refresh without reintroducing
a page-local `刷新代理` button. The visual pass tightens proxy-list density,
makes masked proxy values easier to read without exposing credentials, separates
latest error text for scanning, and constrains the proxy drawer at desktop,
tablet/narrow-desktop, and phone widths while preserving `.drawer-scroll-body`
as the scroll owner. Browser checks covered administrator proxy list,
create/edit/delete cleanup, proxy drawer, tablet side rail with the collapse
button preserved and no bottom horizontal scrollbar, and phone table scrolling
inside `.table-wrap`; no document horizontal overflow or one-character Chinese
text columns were found.
Phase 21G AI Access is now implemented and locally verified: the AI Access list
and drawer keep model names as compact non-wrapping chips, the Base URL/API
key/test-state columns are easier to scan, the model-list fetch action sits in
the existing model combobox instead of a separate selection button, and the
connection-test modal keeps its existing test/close flow. CR-081 is verified as
a Phase 21G regression fix for scrollable drawers/modals: footer action bars
are extracted from `.drawer-scroll-body` into direct `.drawer-fixed-footer`
chrome so scrollbars stop between the fixed header and fixed footer. Static
syntax, targeted CR-038/CR-073/Phase 21F/Phase 21G regression tests, docs
consistency, and browser checks at `1440x900`, `1024x768`, and `390x844` pass
for the CR-081 overlay boundary fix. Browser checks opened representative
scrollable drawers/modals and confirmed zero header/body/footer gaps, no footer
action buttons inside `.drawer-scroll-body`, no document horizontal overflow,
and no one-character Chinese text columns.
Phase 21H AI Evaluation Rules is now implemented and locally verified: the AI
rule list uses denser rule-name, status, and test-state cells with stable action
column width; the rule editor keeps the existing basic information, six rule
sections, prompt preview, fixed output fields, sample input, and result area
while making the editor/test areas easier to scan; and the test result panel now
has idle/loading/success/error visual states. Browser checks at `1440x900`,
`1024x768`, and `390x844` confirmed AI Evaluation Rules opens, add/view AI
access actions remain visible, the row more menu stays within the viewport,
the rule drawer opens with all fields/actions present, `.drawer-scroll-body`
and fixed footer boundaries remain intact, and no document horizontal overflow
or one-character Chinese text columns were found. CR-082 is also verified as a
focused follow-up to CR-081 after user browser review of scrollable overlay
chrome: Mail Configuration, Monitoring task drawer, and Mail Template drawer
were rechecked at desktop and phone widths, and the measured geometry confirmed
that the visible scrollbar belongs only to the middle `.drawer-scroll-body`
between the fixed header and fixed footer. Footer actions remain direct
  `.drawer-fixed-footer` children, required buttons remain visible, and no
  document horizontal overflow was introduced.
CR-090 is now also verified as the current narrow Phase 21H follow-up: the AI
rule list keeps the denser desktop table widths, and the rule modal now uses a
more compact left editor / right sample-and-result proportion while preserving
the same sections, test/save/restore controls, close behavior, enhanced-select
boundary, `.drawer-scroll-body`, and the single-column responsive fallback at
tablet and phone widths.
Phase 21I Mail Configuration is now implemented and locally verified: the mail
configuration page keeps one page-level action group for editing configuration,
sending a test mail, opening Task Center, and toggling real-email delivery,
while the SMTP/defaults summary remains a compact status surface instead of
duplicating edit/test actions. The visual pass refines summary cards, fallback
recipient wording, masked password readability, SMTP/defaults form density, and
mail-test console scanability without changing SMTP APIs, real-email switch
confirmation, delivery behavior, or CR-049 action hierarchy. Browser checks at
`1440x900`, `1024x768`, and `390x844` confirmed Mail Configuration opens, all
required actions remain visible, there are no console errors, no document
horizontal overflow, no one-character Chinese text columns, and the mail
configuration/test drawer scrollbars stay between their fixed header and fixed
footer. Phase 21J Mail Templates followed as the next unclosed Phase 21
workstream.

CR-083 AI Access Model Helper Copy Removal Regression Fix is now verified as a
small follow-up to the Phase 21G AI Access drawer work: the persistent helper
sentence under the model combobox has been removed to reduce drawer height,
while the model-name input, `获取模型列表` action, manual entry, selection list,
fixed footer, close behavior, and connection-test flow are preserved. Browser
checks at `1440x900`, `1024x768`, and `390x844` confirmed the opened AI Access
drawer no longer renders the removed helper copy, has no console errors,
document horizontal overflow, or one-character Chinese text columns, and keeps
the scrollbar between the fixed header and fixed footer.
CR-084 is now verified as a focused Phase 21B follow-up for the
tablet/narrow-desktop shell: at `1024x768`, the persistent `sidebar-collapsed`
rail now contracts to the intended narrow icon-rail width in the final cascade
instead of visually reading as the expanded fixed sidebar. The collapse button,
vertical rail scrolling, role visibility, and true mobile drawer behavior are
preserved.
CR-085 is also verified as a narrower Phase 21B final-cascade follow-up after
in-app browser review at an observed `innerWidth` around `809px`: the final
inline style layer now mirrors the accepted `768px - 1279px` tablet side-rail
contract, so `body.sidebar-collapsed .shell` uses a `68px` icon rail plus the
content column, the mobile navigation trigger is not painted, the collapse
button remains painted, and true mobile `<768px` still uses the drawer trigger.
This preserved Task Center, Run Detail, enhanced select/date controls,
`.drawer-scroll-body`, owner/report scope, top-bar refresh, and backend
behavior.

Phase 21J Mail Templates is now implemented and locally verified: the mail
template list uses denser template-name, subject, active-state, and action
treatment; the template drawer keeps the HTML editor, subject field, set-current
checkbox, variable buttons, local preview refresh icon, iframe preview, save,
clear, and close controls while shortening layout-heavy helper copy. The page
keeps add template, view mail config, search/status filters, clear filters, row
edit/delete, CR-039 body-placeholder guardrails, and CR-074 top-bar-only page
refresh without adding a duplicate page-local refresh button. Browser checks at
`1440x900`, `1024x768`, and `390x844` confirmed the Mail Templates page and
drawer open with no console errors, no document horizontal overflow, no
one-character Chinese text columns, and the template drawer scrollbar remains
between the fixed header and fixed footer. Variable copy, preview refresh,
status filtering, clear filters, and close interactions were exercised.

Phase 21K Runtime Strategy is now implemented and locally verified: grouped
runtime setting tables keep the accepted Crawling/Login/Scheduler/Retention
structure while improving group headers, current-value/source readability,
valid-range scanning, apply-scope chips, lock-state presentation, and the
save-strategy risk cue. The page preserves save strategy, view diagnostics,
top-bar-only page refresh, grouped tables, current values, inputs, ranges,
apply scopes, and lock states without exposing raw deployment environment
variable names in the runtime page copy. Static syntax, inline script parse,
targeted Phase 21K/J/I plus CR-074 frontend tests, and browser checks at
`1440x900`, `1024x768`, and `390x844` passed with no console errors, no
document horizontal overflow, and no one-character Chinese text columns.

Phase 21L Task Center Conservative Visual Pass is now implemented and locally
verified: the current Task Center keeps one top-level `任务中心`, default
task/report grouping, the `运行记录` subview, run filters, pagination, top-bar
page refresh, compact statuses, grouped metric chips, and the single
first-level `详情` route into Run Detail. The visual pass only refines panel
density, filter-toolbar chrome, grouped metric chips, table separators, status
contrast, hover/focus states, empty/loading surfaces, and responsive wrapping.
It does not restore separate top-level Run Center or Report Center pages, does
not add duplicate first-level log/preview/lead/delivery/download actions, and
does not move lead-state filters into the first-level toolbar. Targeted
Task Center/CR-051/CR-069/CR-071/CR-072/CR-073/CR-074 regression tests and
browser checks at `1440x900`, `1024x768`, and `390x844` passed with no console
errors, no document horizontal overflow, and no one-character Chinese text
columns.

Phase 21M Overlay And Run Detail Freeze Gate is now implemented and locally
verified: overlay chrome, focus/hover states, scrollbar styling, header/footer
separation, Run Detail tab chrome, and loading/empty/error visual treatment were
refined without changing overlay workflows. The Run Detail drawer still exposes
the six sections `概览`, `采集日志`, `采集内容`, `AI 评估`, `报告`, and
`邮件交付` in the same order; `采集日志` keeps copy/download actions; the AI
Evaluation filters keep enhanced select behavior; and task-edit custom date
pickers keep the local attached date menu. Representative fixed-footer drawers
at desktop, tablet, and phone widths keep direct header, `.drawer-scroll-body`,
and footer regions with zero header/body and body/footer gaps, footer actions
outside `.drawer-scroll-body`, no console errors, no document horizontal
overflow, and no one-character Chinese text columns. Task Center, Run Detail,
enhanced select/date, drawer scroll ownership, close/backdrop/Escape behavior,
owner scope, report scope, and top-bar refresh semantics remain unchanged.

Phase 21N System Diagnostics is now implemented and locally verified: the
diagnostics page keeps rerun diagnosis, run system diagnosis, process account
resources, readiness/action cards, runtime state, scheduler state, platform
state, generated diagnosis artifacts, and customer-safe wording. The visual pass
adds clearer section headers, status summary cards, impact/next-action
hierarchy, compact recommendation cards, and a scheduler status card without
changing `/doctor`, `/readiness`, `/scheduler-status`, `/smoke`, platform
status APIs, permission checks, account-resource routing, or Task Center/Run
Detail behavior. Phase 21O Login Page and Phase 21P Cross-Page Verification are
now complete as well, with the remaining Phase 21 verification evidence
recorded in `docs/TEST_RESULTS.md`.

The final Phase 21 cross-page regression pass confirmed the current formal
console baseline: one top-level `任务中心`, default task/report grouping,
`运行记录` subview, Run Detail six sections, enhanced drawer/modal selects and
task edit date picker, `.drawer-scroll-body`, and shared top-bar refresh. The
Phase 21 plan remains visual-only and must not restore separate top-level Run
Center / Report Center pages or change Task Center, Run Detail, overlay,
select/date, close, scroll, routing, owner-scope, or report-scope behavior
without a separate accepted CR.

A final local regression pass on 2026-06-20 verified the full Phase 19B-D,
Phase 20B-E, CR-048/CR-049 preservation, and Task Center consolidation scope:
the focused Phase 19/20/Task Center/CR-048/049 pytest selection passed, the
full `tests/test_monitoring_mvp.py` suite passed with 307 tests, `node --check
api/webui/monitor/monitor.js`, the inline `api/monitor_web/index.html` script
parse, and `scripts/check_docs.py` passed, and browser checks covered
administrator plus normal-user Task Center/Run Detail paths at desktop,
tablet, and mobile viewports.
CR-035
Run Lifecycle Finalization And AI Stuck
Recovery Regression Fix is accepted as a follow-up for the completed Phase 7
responsibility area; Phase 7 remains a historical verified snapshot, while
Phase 7.1 is the accepted regression-fix task block for the newly observed
stuck-run class. Phase 7.1A-C is now implemented and verified locally: new
runs persist `crawl_runs.job_id`, compatible legacy summary-based reads and
dry-run backfill are available, run finalization is idempotent, terminal
statuses are protected from stale writers, Phase 7.1 lifecycle heartbeats are
persisted in `crawl_runs.summary`, stale Phase 7.1 rows can recover as
`interrupted` without auto-repairing older historical rows, AI item
timeout/exception/invalid-result paths fall back to `pending_review`, and
partial/manual-review reports can still be generated. CR-036 Test And Local Email Delivery Safety Regression Fix is
accepted as a follow-up for the completed
Phase 17 email-delivery responsibility area after two unexpected real
`日报 海安律所` emails were traced to temporary test/local run records and
unmocked SMTP delivery. Phase 17 remains a historical verified snapshot, while
Phase 17.1 is the accepted regression-fix task block for preventing tests and
local diagnostics from sending hidden real external mail while preserving an
explicit production/pilot real-mail validation path. Phase 17.1A-B is now
implemented and verified locally with an environment-controlled real SMTP
safety gate, read-only deployment runtime visibility, default non-sending
automated/local/report-delivery behavior, explicit opt-in SMTP validation
tests, and a suite-level SMTP tripwire. Phase 17.1C is now complete: effective
recipient metadata is persisted in delivery logs, and task configuration, mail
configuration, preflight, and delivery-history surfaces explain that task
recipients win, global default recipients are fallback-only, and SMTP sender
is not a delivery target. Phase 17.1D is also implemented and verified with a
read-only orphan email evidence review helper, no-op proof, and
backup/approval/rollback runbook notes for the historical `job_id=9686` and
`job_id=9759` evidence. Phase 17.2A-C is now complete: report snapshots and
delivery logs persist effective template provenance, delivery history shows
the send-time template/source, custom HTML templates are blocked unless they
contain `{report_html}` or `{report_body}`, legacy templates stay readable and
append the generated report body if needed, template preview clearly states it
uses sample data, and new templates are steered through administrator style
presets that wrap the system-generated report body. Historical unexpected
email evidence is confirmed to be preserved by default. CR-037 Role-Based
Email Delivery Governance And Quotas is deferred as a future capability for
administrator-managed normal-user send/resend policy and quotas. CR-040 Formal
Console Page-Level UI/UX Refinement is accepted as Phase 21, a frontend-only
implementation phase with `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` as the
execution-plan reference. The Phase 21 plan was rebaselined on 2026-06-19
against the current formal `/monitor` console after CR-051, CR-053, CR-069,
CR-071, CR-072, CR-073, and CR-074. Broad CR-040 page-level visual refinement
remains open, but the current Task Center / Run Detail behavior is now the
baseline: one top-level `任务中心`, default task/report grouping, `运行记录`
as the run-record subview, Run Detail's six sections, enhanced select/date
menus, `.drawer-scroll-body`, and the shared top-bar refresh icon must not be
undone by Phase 21. Phase 21 may refine colors, contrast, spacing, density,
status styling, loading/empty/error/focus states, and responsive wrapping, but
must not restore separate top-level Run Center / Report Center pages or change
Task Center, Run Detail, drawer, modal, row-menu, select/date, close, scroll,
or routing logic without a separate accepted CR. The Phase 21 plan now
explicitly treats prototype-observed layout collapse as a hard production
verification risk rather than confirmed current production breakage: dashboard
cards, closed-loop tracks, dense status cards, resource cards, Task Center /
Run Detail surfaces, and secondary overlays must not squeeze text into one-
character vertical columns, overlap content, hide primary actions, or create
horizontal overflow at `1440x900`, `1024x768`, or `390x844`. Phase 21 also
explicitly excludes the currently unrendered `Users And Permissions` page;
implementing that page would require a separate new-capability CR. CR-041
Minimum Usable Pilot Acceptance Gate is now satisfied
for the current "system can be used first" readiness standard:
hidden-real-email safety and stuck-run lifecycle safety have both been
implemented, locally verified, and externally reviewed; automated server-like
validation passes; the real Douyin pilot run verified server-side login/profile
reuse, crawl, AI fallback, report generation, and redaction; and the
frontend-enabled real SMTP validation recorded `delivery_log_id=6` for
`report_id=3`. The operator confirmed both approved recipients received the
report email, and the redacted `pilot_gate_c_v2` operator evidence JSON passed
the checker. CR-042's earlier multi-layer validation-window design is now
rejected and superseded by CR-043: one administrator Mail Configuration switch
backed by the default-off `real_email_delivery` runtime setting. A `sent`
delivery-log status still means SMTP submission acceptance only; recipient
receipt remains a separate evidence item. CR-041 is not blocked by Phase 21
visual refinement, Phase 19 realtime progress, Phase 20 AI traceability, or
CR-037 role/quota governance unless a later accepted P0 regression changes that
boundary. CR-038 Sticky Drawer Close accessibility is now implemented and
verified as a small frontend-only follow-up before Phase 21: shared
drawer/modal headers remain sticky inside scrollable drawers, close buttons stay
reachable, sticky headers have solid visual separation, existing backdrop and
Escape close paths are preserved, and bottom action bars remain reachable.
CR-044 Mail Test Recipient Coverage And SMTP Acceptance Clarity is implemented
and verified: the Mail Configuration test-mail path submits one message to all
configured global default recipients when no explicit target is supplied,
returns recipient count/source metadata, and shows that count/source in the
frontend while preserving the warning that SMTP acceptance is not recipient
inbox proof.
CR-045 AI Evaluation Accuracy And Unevaluated Lead Status Clarity is accepted
as a new Phase 7.2 follow-up regression fix after live pilot inspection found
that timeout-leftover content without `ai_evaluations` rows could be displayed
as "no risk" and broad target-bearing keywords could recall many unrelated
refund/legal posts. Phase 7 and Phase 7.1 remain historical snapshots. Phase
7.2A-B is now implemented and verified locally: missing AI evaluation rows are
returned as unevaluated or limited-context instead of no-risk; Report Center,
Run Center, leads API, report generation, and filters split unrelated,
evaluated no-risk, suspected negative, high-risk, pending manual review, and
unevaluated/limited-context states; active timeout/partial finalization creates
`pending_review` fallback rows for known unresolved candidate IDs when safe and
records customer-safe fallback evidence. Phase 7.2C-D is now implemented and
verified locally: the AI prompt and post-provider normalization enforce that
`source_keyword` is recall provenance only; title, description, author, or
actually collected comments must contain the target law firm or accepted alias
before model output can mark a row as target-related or negative; homonym or
geography-only mentions such as "海安" remain unrelated unless the target law
firm/alias appears; calibration fixtures cover noisy-positive keyword-only
output, broad refund/legal noise, true title evidence, and comment-only target
evidence. CR-050 is implemented and verified as a focused CR-045 follow-up:
Report Center and leads API risk filters keep `高风险` and `疑似负面` exact, so
the `疑似负面` filter no longer includes high-risk rows.
CR-047 Account Identity Fidelity is accepted as Phase 5.1, a future
account-environment optimization that extends the existing `profile_key` model
with lifecycle-level identity consistency: profile traces, browser
environment, proxy region/policy, runtime binding, lock state, and audit
state. The documentation now distinguishes profile-folder traces from
database-stored launch/environment rules and adds the planned Account Identity
Generator and Validator requirements. Template selection is now documented as
automatic by default, with only an advanced pre-login administrator
template-family override and no field-level identity editing for normal users
or ordinary account creation. CloakBrowser-Manager remains a reference only for
stable profile settings, CDP, and noVNC, and does not become a required
dependency or replace the current Platform Accounts center. V1 now explicitly
stays on the existing Playwright/CDP provider path and does not introduce
CloakBrowser. Canvas, WebGL, font inventory, plugins, extensions, and long
browsing history are future/provider-dependent rather than V1 managed surfaces
because they depend on provider/browser/OS/profile/runtime behavior that cannot
be guaranteed by static launch settings alone. The fixed-environment proxy
override policy is confirmed for Phase 5.1: after CR-047 locks an account
identity, task-level proxy overrides are blocked for that locked account
environment, and changing the proxy requires explicit reset/re-login. The
first Plan Cross Validation review found implementation specification gaps, so
the documentation now adds the Phase 5.1 generation algorithm, deterministic
template-selection rule, template catalog, fail-closed enforcement rules,
Playwright/CDP provider contract, identity lifecycle state machine, runtime
snapshot shape, audit events, and test-safety tripwires. These are
documentation gates only; CR-047 code and schema implementation have not
started.
CR-070 Account Environment Export And Import Package is accepted as a Phase
5.2 new capability for moving a single platform account environment between
deployments. It extends the CR-047 identity model with metadata-only and slim
encrypted login-state migration package concepts, including manifest/version/
checksum rules, passphrase encryption, encrypted login/session material
handling, necessary profile state rather than raw whole-profile cache,
platform-account metadata, encrypted proxy host/IP plus port hint without
credentials, target-side proxy mapping, import preflight, post-import
login-state verification, audit logging, and fail-closed `requires_relogin`
behavior. The package scope is explicitly one selected platform account
environment, not a full database backup of tasks, runs, reports, AI traces,
mail logs, users, runtime settings, or business history. V1 creates a new
target account/profile on import and exports avatar metadata only. This is
documentation planning only; no export/import code, schema migration, package
artifact, real profile, cookie, proxy, or login state has been changed.
CR-075 Open Todo MECE Rebaseline And Phase 5.1 Preflight Gate is accepted as a
documentation-governance batch. The current open work is now explicitly
separated into an active Phase 21 frontend visual lane, a Phase 5.1 Preflight
documentation/read-only compatibility lane, the later Phase 5.1 account
identity implementation body, the Phase 5.1 acceptance lane, Phase 5.2 /
CR-070 after CR-047 provider/effective snapshot verification, and independent
deferred items such as CR-037, the unrendered Users And Permissions page, and
Phase 7.1D historical repair. This batch changes task sequencing only; it does
not change code, UI, database schema, runtime data, account profiles, cookies,
proxy configuration, crawler behavior, or deployment configuration.
CR-078, CR-079, and CR-080 are added as future independent backlog lanes after
the CR-075 rebaseline. CR-078 covers future `/monitor-next` frontend stack
migration planning in `docs/MONITOR_NEXT_FRONTEND_PLAN.md` and is not a Phase
21 task. CR-079 covers MediaCrawler internalization and public exposure
boundary planning; its product boundary is accepted, but exact route/mount and
reverse-proxy behavior still needs confirmation after read-only audit. CR-080
covers future crawler provider architecture in
`docs/CRAWLER_PROVIDER_ARCHITECTURE.md` and is separate from Phase 5.1P, which
remains only the current MediaCrawler/CDP/BrowserEnvironmentProvider
compatibility preflight. These three backlog lanes do not block Phase 21,
Phase 5.1P, CR-047/Phase 5.1, or CR-070/Phase 5.2, and they do not change
code, UI, schema, runtime data, routes, crawler behavior, account profiles,
cookies, proxies, or deployment configuration.
CR-081 Atomic Goal Execution Governance And Readiness Gate is accepted as a
documentation-governance layer on top of the CR-075 lane separation. It adds
`docs/GOAL_EXECUTION_GUIDELINES.md` as the source for goal packet structure,
atomicity rules, current execution lanes, test iteration loop, acceptance
standards, and stop conditions. This does not change the current roadmap
priority and does not implement code, UI, schema, runtime data, routes,
crawler behavior, account profiles, cookies, proxies, deployment
configuration, or production changes.
CR-048 Report Center Lead Detail Information Architecture is implemented and
verified for the focused Phase 20E/21M frontend information-architecture
batch. Report Center no longer renders lead detail as a first-level flat
table; report rows expose explicit "查看线索" actions, the lead drawer shows
selected-report scope, count, filter summary, and empty states, and Run Center
rows expose a run-scoped "查看线索" shortcut that opens the same drawer without
turning Report Center into a global lead workbench. Follow-up acceptance tuning
keeps the first-level Report Center toolbar limited to report dimensions
(`律所`, `平台`, date range, and `报告范围`), while `线索状态` appears inside the
lead drawer and filters only the currently selected report or selected run lead
scope. Full Run Detail, per-run lifecycle, and every AI evaluation record remain
CR-034 / Phase 20 responsibilities outside this focused batch.
CR-049 Mail Configuration And Delivery History Action Hierarchy is implemented
and verified for the focused Phase 21I/21M frontend information-architecture
batch. CR-043/CR-044 safety behavior remains intact while Mail Configuration
now keeps edit, test, refresh/status, delivery-status navigation, and the
single real-email switch in the page-level action bar; the old first-level
"SMTP 与发送默认值" and large real-email status panels are removed. Report
Center delivery history is no longer a dominant default panel and opens as a
scoped drawer from a report email-status button or "更多 > 查看交付历史", with
selected-report scope, count, refresh action, latest status, and SMTP
acceptance wording. Later CR-051 through CR-058 Task Center consolidation
removes the report-list entry and row more-menu surface from the current
console; delivery history, resend, and downloads now live under Run Detail's
Report and Email Delivery sections.
The active SQLite schema now provides the foundation tables and columns
required before later implementation work, and the web/API layer now has
session login, administrator/normal-user roles, menu visibility,
owner-scoped business data access, administrator-managed runtime strategy
settings, administrator resource pages with consistent summary, toolbar, modal,
and test interactions, a normal-user task wizard with administrator-only
advanced options, and profile-key based account environments with persisted
account/profile/proxy locks, stale-run recovery, server-side QR login as the
primary administrator flow, structured login states, profile persistence/reuse
checks, deployment gating for local-window login fallback, AI/manual-review
fallback, email-failure-tolerant report generation, report-specific lead
preview switching, run log refresh/copy/download controls, and an automated
server-like validation script that starts the real FastAPI service with
production login flags, persistent profile roots, service restart checks, and
headless browser verification, administrator-operation audit logs, sensitive
value redaction, resource-alert diagnostics, backup guidance, disk-space
  diagnostics, retention-setting diagnostics, Phase 11 local static frontend
  assets, base shell/navigation visual styles, fixed floating-menu behavior,
  responsive desktop/tablet/mobile navigation and layout foundations, Phase
  12A expandable primary navigation groups, operations-home login/session
  landing, grouped account/logout controls, Phase 12B standardized page
  entries with task-loop shortcuts for administrator and normal-user paths,
  Phase 13A dashboard API operations-home aggregates for task health, run
  activity, report activity, email delivery latest state, suspected lead
  metrics, and role-safe resource health, Phase 13B desktop operations
  home visual metrics with drilldowns, and Phase 13C responsive operations
  home role views with detailed diagnostics moved to System Diagnostics,
  CR-033 dashboard data-first visual polish, unclipped floating menus,
  page-shaped loading states, secondary overlay loading feedback, and mobile
  dashboard density reduction, and
  Phase 14 run-center data-model fields for run visibility, run type,
  archived time, and archived user with visible/scheduled backfill and
  recommended indexes, plus Phase 15A run-center API/query pagination,
  filters, default visible-only listing, administrator-only archived access,
  archive/restore APIs, and response metadata for pagination, filters,
  visibility, and run type, plus Phase 15B run-center frontend pagination,
  filters, default operational-record view, administrator archive/restore row
  controls with confirmation, and responsive run-center verification, plus
  Phase 16 email delivery log schema, send-window key helper, delivery-log
  insert/list helpers, customer-safe delivery-log text handling, partial
  unique automatic-send window protection, and Phase 17A scheduler/report
  delivery logic that records automatic attempts, skips duplicate automatic
  sends by schedule window, logs failures without blocking report generation,
  records manual resend separately, keeps report latest-state fields readable,
  and Phase 17B report-center delivery-history UI/API surfaces latest delivery
  state, automatic/manual delivery history, recipient summaries, and
  customer-safe delivery errors without exposing SMTP secrets, plus Phase
  17.1A-B real SMTP safety gating blocks automated/local hidden external sends
  by default, records blocked deliveries as customer-safe skipped states,
  keeps explicit opt-in pilot validation available, and installs an automated
  SMTP tripwire, plus Phase 17.1C/17.2A backend delivery metadata records
  effective recipients, recipient source, trigger source, and effective email
  template provenance for new report snapshots and delivery logs, plus Phase 18A
  report snapshots store task context for new and backfilled reports while
  keeping unrecoverable historical reports readable with limited context, and
  Phase 18B groups report-center rows by active task or stored snapshot while
  preserving preview, lead switching, downloads, delivery history, and row
  actions.

## Implementation Status

- Phase 0 - Documentation: complete.
- Phase 0.5 - Schema Foundation: complete and verified.
- Phase 1 - Users And Permissions: complete and verified.
- Phase 2 - System Settings: complete and verified.
- Phase 3 - Administrator Resource Center: complete and verified.
- Phase 4 - Normal User Task Wizard: complete and verified.
- Phase 5 - Account Environment: complete and verified.
- Phase 6 - Server Login Flow: complete and verified locally.
- Phase 7 - Runs, Reports, And AI: complete and verified locally.
- Phase 7.1 - Runs, Reports, And AI Stuck Recovery Follow-up: partially
  complete and verified locally. Phase 7.1A-C is implemented: new runs persist
  `crawl_runs.job_id`, legacy `summary.job_id` rows are read compatibly and
  dry-run backfillable when resolvable, terminal finalization is idempotent,
  Phase 7.1 lifecycle summaries include phase/heartbeat/retry/error/progress
  evidence, stale Phase 7.1 rows can recover as `interrupted` after the
  confirmed evidence checks, AI item timeout/exception/invalid-result paths
  fall back to `pending_review`, and partial/manual-review reports can be
  generated. Phase 7.1D historical run `8317` remediation remains open and
  still requires backup, rollback, dry-run preview, and explicit operator
  approval.
- Phase 7.2 - AI Evaluation Accuracy And Lead Status Clarity Follow-up:
  complete and verified locally. Phase 7.2A-D is implemented:
  missing AI evaluation rows are never returned, counted, filtered, or rendered
  as no-risk; missing rows surface as unevaluated/limited-context where safe
  mutation is not possible; report/run summaries and risk filters split
  pending-review, unrelated, evaluated no-risk, suspected negative, high-risk,
  and unevaluated buckets; timeout/partial finalization creates
  `pending_review` fallback rows for known unresolved AI candidate IDs when
  safe and records customer-safe fallback evidence; source-keyword-only,
  homonym/geography-only, broad refund/legal, title-evidence, and
  comment-evidence calibration fixtures verify the target-evidence gate. CR-050
  has corrected the Report Center risk-filter precision gap so
  suspected-negative and high-risk filters do not include each other.
- Phase 8 - Server-Like Validation: complete and verified through automated
  server-like validation.
- Phase 9 - Security And Operations: complete and verified locally.
- Phase 10 - Frontend Architecture And Technology Decision: complete as a
  documentation and architecture decision phase.
- Phase 10.5 - Phase 10-18 Global Plan Review Gate: complete as a
  documentation-only review gate.
- Phase 11 - Frontend Design System: complete and verified through Phase
  11A-11D.
- Phase 12 - Navigation And Page Entry Redesign: complete and verified through
  Phase 12A-12B.
- Phase 13 - Overview Operations Home Redesign: complete and verified
  through Phase 13A-13C.
- Phase 14 - Run Center Data Model Preparation: complete and verified.
- Phase 15 - Run Center Governance And Frontend: complete and verified through
  Phase 15A-15B.
- Phase 16 - Email Delivery Data Model Preparation: complete and verified.
- Phase 17 - Email Delivery Governance: complete and verified through Phase
  17A-17B.
- Phase 17.1 - Email Delivery Safety Follow-up: complete and verified locally.
  Phase 17.1A-B real SMTP safety gate and automated-test tripwire are
  implemented. Phase 17.1C effective-recipient traceability is implemented in
  delivery logs, preflight, task copy, mail configuration copy, and
  delivery-history UI. Phase 17.1D historical orphan evidence dry-run/runbook
  work is implemented and verified.
- Phase 17.2 - Report Email Template Governance: complete and verified
  locally. Phase 17.2A effective-template provenance is implemented for new
  report snapshots and email delivery logs, while Phase 17.2B-C blocks new
  body-dropping custom templates, keeps legacy templates readable with a safe
  generated-body fallback, clarifies preview-vs-real-send semantics, and adds
  administrator style presets that preserve the system-generated report body.
- Phase 18 - Report Center Task Grouping: complete and verified through Phase
  18A-18B.
- Phase 19 - Run Center Realtime Progress And Requirement Intake Governance:
  Phase 19A documentation-governance rules are complete and verified. Phase
  19B run-progress data layer is implemented and locally verified: running
  crawler attempts now write provisional collection progress into
  `crawl_runs.summary`, tolerate missing, empty, partially written, and
  malformed JSON/JSONL output files, preserve final `raw_contents`,
  `filtered_contents`, `excluded_contents`, and `new_contents` ingest
  semantics, and expose customer-safe progress fields through run reads. Phase
  19C AI-evaluation progress is implemented and locally verified: active AI
  loops now write `ai_progress` with evaluated/total candidates, successful
  evaluations, fallback/manual-review count, suspected-negative count, high-risk
  count, unresolved count, and a final marker; final AI counts remain exact,
  failed AI items still fall back to `pending_review` so reports can be
  generated, and late or repeated progress writes cannot regress final AI
  progress or reopen a terminal run. Phase 19D Run Center frontend progress
  display and polling is implemented and verified: active visible rows poll
  silently until terminal state, collection progress stays provisional, AI
  progress and lifecycle labels are visible, and stop/log/lead/archive/restore
  actions remain reachable.
- Phase 20 - Run Detail And AI Evaluation Traceability: Phase 20B AI trace
  persistence, Phase 20C Run Detail API, Phase 20D Run Detail frontend, and
  the remaining Phase 20E report-to-run backlink are implemented and verified.
  New
  successful, failed, and fallback AI evaluations persist safe
  `ai_evaluation_traces` snapshots with capped/redacted input, prompt/request,
  provider/model, structured output, response, fallback/error, duration, and
  timestamps; trace writes and retention cleanup are non-blocking, old
  evaluations without trace snapshots return limited-context, and
  `ai_trace_retention_days` defaults to 30 days as an administrator runtime
  setting. The run-detail API now returns scoped overview, crawler logs,
  collected contents, paginated/filterable AI evaluations, reports, email
  delivery logs, and per-evaluation role-safe trace detail. The Run Detail
  frontend is the primary run-scoped entry for logs, contents, reports,
  delivery, and every AI evaluation record; report lead rows with `run_id`
  can return to the originating run detail without turning Report Center into
  a global lead workbench.
- Phase 21 - Formal Console Page-Level UI/UX Refinement: accepted but not
  fully implemented. The focused CR-048/CR-049 frontend information-
  architecture subset and later CR-051/CR-053/CR-069/CR-071/CR-072/CR-073/
  CR-074 Task Center, Run Detail, dropdown/date, drawer-scroll, and refresh
  refinements are verified and now form the current Phase 21 baseline. A
  focused Phase 21A/B/C visual pass has started for the shell, navigation,
  top-right account control, development-copy cleanup, and Operations Home
  density; the second-level navigation hover regression is fixed so hover is
  pure neutral gray and selected state remains teal, including collapsed
  sidebar hover, and CR-075 verifies the desktop/tablet/mobile navigation
  breakpoint model without reintroducing mobile `打开导航` at 1024px/1169px or
  breaking the 390px mobile drawer/header. CR-077 closes the follow-up mobile
  header cascade regression in the live formal page's final inline style layer.
  The broader Phase 21 page-level
  visual refinement workstreams for Monitoring,
  Platform Accounts, Proxies, AI Access, AI Rules, Mail Templates, Runtime
  Strategy, conservative Task Center visual polish, overlay/Run Detail freeze
  verification, System Diagnostics, Login, and cross-page verification remain
  open.
- Minimum Usable Pilot Acceptance Gate: satisfied for first usable pilot. CR-036 /
  Phase 17.1A-B email side-effect safety and CR-035/Phase 7.1A-C run
  lifecycle/AI fallback/partial-report safety are implemented, locally
  verified, and read-only externally reviewed. Automated server-like validation
  passes without relying on the operator's local Chrome. A no-side-effect
  Pilot Gate C evidence checker now provides a structured way to validate
  redacted operator proof for the remaining real workflow. The real platform
  login/crawl, AI-fallback, and redaction portions are verified for the
  recorded Douyin pilot run. A controlled frontend-enabled manual resend
  recorded `delivery_log_id=6` with SMTP `sent` acceptance. The operator
  confirmed both approved recipients received the report email, and the
  redacted local operator evidence JSON passed
  `scripts/pilot_gate_c_evidence.py --check`. CR-043 now replaces the rejected
  CR-042 validation-window design with one administrator Mail Configuration
  switch for real email delivery. A `sent` delivery-log status means the SMTP
  server accepted the message submission; it is not recipient inbox proof by
  itself.
- CR-044 - Mail Test Recipient Coverage And SMTP Acceptance Clarity: complete
  and verified. Mail Configuration test mail submits to all configured global
  default recipients when no explicit target is supplied, reports submitted
  recipient count/source in the API and frontend, and keeps automated
  verification on mocked SMTP so tests do not send real external mail.
- CR-045 - AI Evaluation Accuracy And Unevaluated Lead Status Clarity:
  complete and verified for Phase 7.2A-D. Unevaluated/limited-context status
  safety, active-finalization fallback, source-keyword recall-provenance
  enforcement, target-evidence gating, homonym/geography safeguards, and
  calibration fixtures are implemented and verified locally.
- CR-050 - Report Center Lead Status Filter Precision Regression Fix:
  complete and verified. Report Center and leads API filters now treat
  `高风险` and `疑似负面` as exact status filters; suspected-negative filtering
  no longer includes high-risk rows.
- CR-051 - Task Center And Report Grouping Consolidation: complete and
  verified. The formal console now has one top-level `任务中心`; task/report
  grouping is the default first view, `运行记录` is a subview for operational
  run fields and controls, and the old separate Report Center top-level entry
  and `reports` section are removed. Current Task Center rows expose only
  `详情`; report preview, downloads, resend, delivery history, and lead
  inspection are reached through Run Detail.
- CR-053 - Task Center Field Priority And Global Select Alignment: complete
  and verified. Flat Task Center rows front-load `任务 ID` and `运行 ID`;
  grouped rows hide duplicated `任务 ID` and front-load `运行 ID`; status cells
  stay compact, the duplicate filter-toolbar refresh button is removed, and
  native select dropdowns are no longer clipped by the main content overflow
  rule.
- CR-054 - Task Center Status Badge Compactness Regression Fix: complete and
  verified. Task Center status badges now render short lifecycle labels and do
  not reuse long backend `display_status` text as the visible badge.
- CR-055 - Task Center Status Column Visual Refinement: complete and verified.
  Task Center status cells use a dedicated narrow status column and lightweight
  state-dot badge, while grouped/flat field order and the single `详情` action
  remain unchanged.
- CR-056 - Filter Dropdown Alignment Regression Fix: complete and verified.
  Filter toolbar dropdowns now use fixed-position in-page menus that stay
  aligned with their trigger at `1440x900`, while underlying select values and
  existing filtering behavior remain unchanged.
- CR-057 - Task Center Group Summary Metric Chips: complete and verified.
  Grouped Task Center headers now show run, collection, new-content, risk,
  review, and unevaluated aggregates as compact metric chips instead of one
  long slash-separated sentence.
- CR-058 - Filter Date Picker Alignment Regression Fix: complete and
  verified. CR-059 - Filter Date Picker Edge Anchoring Regression Fix and
  CR-060 - Filter Date Picker Compact Center Alignment Regression Fix are
  verified historical follow-ups; CR-061 - Filter Date Picker Trigger-Width
  Anchoring Regression Fix is a verified historical follow-up: it proved that
  date menus can match the clicked trigger width and align to the trigger's
  left edge after browser review found that a wider centered menu could still
  read as visually offset.
  CR-062 - Filter Date Picker Grid Compression Regression Fix is also complete
  and verified: day cells no longer inherit button padding/auto minimum width
  that can clip the last calendar columns inside the trigger-width menu.
  CR-063 - Filter Date Picker Readable Anchored Popover Regression Fix,
  CR-064 - Filter Date Picker Trigger-Attached Edge Shrink Regression Fix,
  CR-065 - Filter Date Picker Center-Anchored Visual Alignment Regression Fix,
  and CR-066 - Filter Date Picker Trigger-Attached Dropdown Alignment
  Regression Fix are verified historical follow-ups.
  CR-067 - Filter Date Picker Trigger-Width Visual Attachment Regression Fix
  is complete and verified: the current date menu matches the clicked trigger
  width when usable, aligns to the trigger's left edge, keeps the top anchor
  marker aligned to the trigger center, and uses a small minimum readable width
  only for unusually narrow triggers before viewport clamping.
  Browser review found zero overflowing date cells at desktop review width.
  Underlying date values, clear/reset behavior, and existing filtering
  semantics remain unchanged.
- CR-046 - Platform Account Avatar Safe Cache Display Regression Fix:
  complete and verified. Platform-account identity rows now expose only a
  same-origin avatar URL; signed platform image URLs remain server-side
  runtime data and are lazily cached before serving to administrators.
- Phase 5/6 - Account Environment and Server Login: profile key, timeout, and
  lock-storage decisions are accepted; Phase 5 account environment runtime and
  Phase 6 login-flow runtime are complete.
- CR-047 / Phase 5.1 - Account Identity Fidelity: accepted but not
  implemented. Confirmed scope includes persisted per-account identity fields,
  profile-trace versus database-identity responsibility split, stable Account
  Identity Generator, fail-closed Account Identity Validator, China mainland
  region/timezone/locale/accept-language defaults, identity generation before
  first login, locking after successful QR login or accepted Cookie
  validation, login/crawl reuse of the same profile/user-agent/browser-
  platform/timezone/locale/device/proxy policy, explicit reset/re-login for
  locked changes, and a V1 boundary that keeps CloakBrowser out of the first
  implementation while recording Canvas/WebGL/fonts/plugins/extensions/history
  as future/provider-dependent scope. The current documentation also includes
  implementation-level gates for deterministic generation, exact template
  expansion, provider requested/effective probes, runtime snapshots,
  `identity_state`, audit events, and test tripwires; implementation remains
  pending until Phase 5.1P preflight confirms the container/server-like,
  BrowserEnvironmentProvider, MediaCrawler CDP, QR login, Cookie validation,
  login-state check, manual run, scheduler run, runner, and requested/effective
  snapshot compatibility boundary.
- CR-075 - Open Todo MECE Rebaseline And Phase 5.1 Preflight Gate: accepted as
  a documentation-governance sequencing update. It keeps Phase 21 separate as a
  frontend visual-only lane, makes Phase 5.1P the next account-environment
  gate before schema/code implementation, moves container/server-like and
  BrowserEnvironmentProvider work into the Phase 5.1 development/acceptance
  baseline rather than a separate parallel big task, and delays CR-070 /
  Phase 5.2 until CR-047 provider binding plus effective runtime snapshot are
  verified.
- CR-048 - Report Center Lead Detail Information Architecture: focused
  frontend batch complete and verified. Report Center uses explicit
  report-scoped "查看线索" actions and a scoped lead drawer; Run Center also
  exposes run-scoped "查看线索"; the default Report Center no longer renders an
  unlabeled lead table or process-draft preview hint.
- CR-049 - Mail Configuration And Delivery History Action Hierarchy: focused
  frontend batch complete and verified. Mail Configuration primary actions and
  the single real-email switch live in the page-level action bar, duplicated
  first-level SMTP/default panels are removed, and Report Center delivery
  history opens as a scoped drawer from report row/status actions.

The documented V1 product roadmap is implemented through Phase 9 in this
worktree, and the console optimization roadmap is verified through Phase 18B.
CR-041 is now the completed narrower first usable pilot gate. Broader
production handoff can still add deployment-specific validation for additional
platform accounts, SMTP providers, AI providers, and operational runbooks as
separate follow-up work.

## Completed

- Project direction has been clarified as a server-deployed ToB law-firm
  public-opinion monitoring system.
- The first-version boundary has been clarified as single-server,
  low-concurrency, administrator-managed resources, and normal-user task
  creation.
- The role split has been clarified:
  - system administrator maintains account pool, proxies, AI, email, templates,
    runtime strategy, and users;
  - normal user configures platforms, content, frequency, and recipient emails.
- The account-environment model has been clarified:
  task -> platform account -> profile -> proxy -> server browser.
- Server-like validation has been made mandatory for production acceptance.
- Initial governance documents have been added.
- Menu-level product requirements have been documented.
- Change request intake, traceability, and agent workflow documents have been
  added.
- A confirmation gate has been added: ambiguous high-impact requirements must
  be confirmed by the user before becoming accepted product or architecture
  decisions.
- P0 implementation specifications for roles, account environment, runtime
  settings, and data model have been added as planning documents.
- A permission confirmation pack, compatible schema migration plan, and runtime
  configuration example have been added.
- API authentication/authorization and server deployment guides have been
  added.
- Documentation consistency check specification and Phase 0.5 test coverage
  have been added.
- Permission, workspace, authentication, initial administrator, disabled-user
  behavior, audit-log timing, and runtime settings storage decisions have been
  accepted using the V1 recommended options.
- Phase 0.5 schema foundation has been implemented in
  `api/monitoring/database.py`: default workspace, user/session/settings/audit
  tables, ownership columns, profile keys, run timeout fields, account lock
  fields, and proxy `resource_locks`.
- Existing monitoring MVP task/account/login/run/report records still load
  after the schema foundation migration.
- Phase 1 user and permission foundation has been implemented:
  environment-bootstrap administrator creation, bcrypt password hashes,
  session-token cookies backed by `user_sessions`, user management APIs,
  shared FastAPI auth/role dependencies, administrator-only resource APIs,
  normal-user owner scope for jobs/runs/reports/leads, and frontend login/menu
  visibility.
- `scripts/check_docs.py` has been implemented and currently passes.
- Phase 2 runtime strategy has been implemented:
  `api/monitoring/settings.py` defines runtime defaults, YAML mapping,
  validation ranges, apply scopes, and environment locks; `system_settings`
  stores database overrides with audit logging; administrators can edit grouped
  Runtime Strategy tables; normal users cannot access runtime settings APIs;
  scheduler tick/disable, crawl concurrency, crawler retry, run-level timeout,
  QR timeout, login session TTL, lock cleanup buffer, and retention settings
  now read through the runtime settings layer.
- Newly started crawl runs copy `crawler_timeout_seconds` into
  `crawl_runs.timeout_seconds`, compute `deadline_at`, allocate remaining run
  time to platform crawler attempts, and mark deadline-exceeded runs as
  `timeout` while preserving partial platform results.
- Phase 3 administrator resource center has been refined:
  platform accounts keep the single account-detail dialog, proxy resources have
  summary cards plus search/status filters, AI access has summary cards plus
  protocol/test-status filters and a connection-test dialog, mail configuration
  uses edit/test dialogs with masked password behavior, and mail templates have
  summary cards plus search/status filters and live preview.
- Phase 4 normal-user task creation has been simplified:
  normal users see a four-step task wizard for target, collection content,
  schedule, and report recipients; crawl range copy explains the actual V1
  boundaries; account/proxy/AI/template/browser fields are hidden from normal
  users; the API also clears those advanced fields for normal-user create/edit
  requests; administrators still keep advanced task binding controls.
- Phase 5 account environment runtime has been implemented:
  account profile runtime paths are derived from stable `profile_key` values,
  new account environments ignore arbitrary customer-provided profile paths,
  account names are display labels only, account/profile summaries no longer
  expose real server paths, account/profile locks use inline
  `social_accounts` fields, proxy concurrency uses `resource_locks`, run
  cleanup releases locks, and startup/scheduler recovery reconciles timed-out
  running runs before releasing persisted locks.
- Phase 6 server login flow has been implemented:
  administrator account login now starts from server-side QR sessions by
  default, login APIs and the frontend use structured states (`preparing`,
  `waiting_qrcode`, `waiting_scan`, `waiting_confirm`, `success`,
  `needs_verification`, `qrcode_failed`, `timeout`, and `platform_error`),
  legacy login states are normalized for compatibility, successful login is
  re-checked before the account is marked active, profile-key paths are reused
  after the browser session closes, QR-session failures are reconciled against
  same-account MediaCrawler account/Profile validation before showing failure,
  and `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false` hides and blocks local-window
  login fallback for production mode.
- Phase 7 runs, reports, and AI behavior has been verified:
  jobs can complete with AI disabled and email unavailable, new contents enter
  `pending_review` instead of blocking report generation, report wording keeps
  "suspected negative leads" semantics and avoids factual conclusions, report
  preview requests load leads scoped to the selected report ID, and run logs
  expose refresh, copy, and download controls with customer-safe text.
- Phase 8 server-like validation has been implemented and verified:
  `scripts/server_like_validation.py` starts the real FastAPI app as an HTTP
  service with isolated persistent data directories, production login flags
  (`MONITOR_LOGIN_QR_HEADLESS=true` and
  `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`), bootstrap administrator login,
  web QR/status capability checks, local-window login blocking,
  same-platform account profile separation, profile metadata persistence across
  service restart, account/profile/proxy runtime lock enforcement, and
  headless Playwright Chromium availability.
- Phase 9 security and operations has been implemented and verified:
  administrator resource changes write minimal `audit_logs` records without
  plaintext secrets, sensitive text redaction covers API keys, passwords,
  cookies, proxy credentials, encrypted-field labels, and Chinese secret
  labels, readiness now surfaces account invalidation and proxy-error alert
  paths, doctor diagnostics include disk-space, retention-setting, backup-set,
  and resource-alert checks, and deployment docs describe database, profile,
  report, encryption-key, and configuration backups.
- Phase 10-18 console optimization requirements have been accepted in
  documentation:
  - navigation and page entries will be rebuilt around the monitoring task
    loop;
  - the frontend design system will combine Apple-style visual language,
    interaction patterns, and responsive behavior;
  - the operations home will replace the text-heavy overview;
  - run center governance will use logical archive and noise filtering;
  - email automatic sending will use delivery logs and schedule-window
    idempotency;
  - report center grouping will use monitoring task grouping and
    `job_snapshot_json` for orphan report history;
  - the frontend technology stack remains Vanilla JavaScript plus CSS custom
    properties for this redesign round.
- Phase 19 requirement-documentation rules have been added:
  future CRs must classify whether they are a new capability, existing feature
  optimization, regression fix, or documentation-governance change, and must
  include background, purpose, boundaries, related tasks, and acceptance
  criteria.
- CR-031 Run Center Realtime Progress Visibility has been accepted:
  active runs should show provisional collection progress before platform
  subprocess completion, AI progress should update during long evaluation
  batches, and frontend polling should continue while visible runs remain
  active. Phase 19B-19D is now implemented and verified: progress stays in
  `crawl_runs.summary`, final collection/AI counts keep their existing
  semantics, and the Run Center shows active progress without hiding stop,
  log, lead, archive, or restore actions.
- CR-035 Run Lifecycle Finalization And AI Stuck Recovery Regression Fix has
  been recorded as a follow-up regression fix after live task `9297` / run
  `8317` showed collection and partial AI evaluation had progressed while the
  persisted run remained `running`. The fix is documented as Phase 7.1 and
  should precede or be explicitly separated from Phase 19B-19D progress-display
  work. User confirmation on 2026-06-16 accepted `interrupted` as a distinct
  terminal state, active pending-review fallback for unresolved AI candidates,
  AI evaluation progress counts, and prevention-first `job_id` persistence.
  A later confirmation accepted evidence-based stale recovery, a 10-minute
  heartbeat grace period, retry-before-timeout behavior, and
  `ai_item_timeout_seconds=120`.
- CR-036 Test And Local Email Delivery Safety Regression Fix has been recorded
  as a follow-up regression fix after two real emails were traced to temporary
  `海安律所` test/local jobs: `job_id=9686/run_id=8380` and
  `job_id=9759/run_id=8447`. The corresponding automatic delivery logs show
  `status=sent`, while the current `monitor_jobs`, `crawl_runs`, and `reports`
  rows no longer exist for those IDs. The strongest local trigger evidence is
  `test_run_job_blocks_platform_when_login_window_is_open`, which calls
  `run_monitor_job` without mocking report email delivery. The fix is
  documented as Phase 17.1 and should be handled separately from Phase 19 run
  progress and Phase 20 AI traceability. User confirmation on 2026-06-16
  accepted preserving the historical unexpected-email evidence by default, then
  accepted environment-controlled real-email gating, read-only runtime
  visibility, non-sending local/test behavior by default, explicit real-mail
  validation support, and trigger-source/effective-recipient traceability.
- CR-037 Role-Based Email Delivery Governance And Quotas has been recorded as
  a deferred future capability after the user clarified that administrator
  authority, normal-user email send/resend restrictions, and possible daily
  quotas may be needed later. It is not part of the immediate CR-036 safety
  fix.
- CR-040 Formal Console Page-Level UI/UX Refinement has been accepted as Phase
  21. The standalone execution plan defines per-page preservation rules,
  allowed visual changes, testing, verification, and acceptance criteria. It is
  now rebaselined on the current Task Center / Run Detail console rather than
  the older separate Run Center / Report Center structure. The focused CR-048/
  CR-049 information-architecture subset plus the verified CR-051, CR-053,
  CR-069, CR-071, CR-072, CR-073, and CR-074 frontend refinements are baseline
  behavior; the broader Phase 21 page-level visual refinement remains open and
  does not reopen CR-033.
- CR-034 Run Detail And AI Evaluation Traceability has been accepted as a
  run-center optimization with data-model implications. Phase 20B-D plus the
  remaining Phase 20E backlink are implemented and verified: new AI
  evaluations store trace snapshots, scoped run-detail and per-evaluation APIs
  expose role-safe detail, Run Center opens run detail, and report leads with
  `run_id` link back to the originating run detail.

## In Progress

- Phase 10-18
  console optimization is complete and verified through Phase 18B. Phase 19A
  documentation governance is complete, and Phase 19B-19D run-center realtime
  progress is implemented and verified. Phase 7.1A-C, Phase 7.2A-D, CR-043,
  CR-044, CR-045, CR-050, and Phase 20B-E are implemented and verified; Phase
  7.1D remains gated. Phase 21 is accepted but not fully implemented; the
  verified CR-048/CR-049/CR-051/CR-053/CR-069/CR-071/CR-072/CR-073/CR-074
  frontend behavior is the current baseline. CR-075 is accepted as the
  documentation-only MECE sequencing update for the next open work. CR-037 is
  deferred.

## Known Risks

- Phase 5 still stores `profile_path` as a transition-only internal runtime
  field for existing login/crawler code paths, but new identity and path
  resolution are `profile_key` based and customer-facing responses mask real
  paths.
- Current system is closer to a single-team MVP than a production multi-user
  system.
- Server-side QR/login capability and profile persistence now have automated
  server-like validation, but real platform QR scanning, real platform
  crawling, and explicit-opt-in real SMTP delivery still require a live
  server/account pilot with operator-controlled credentials.
- The newly added product documents are initial versions and should be refined
  during implementation.
- Profile migration strategy has been clarified: existing low-volume
  `profile_path` accounts do not need long-term compatibility and can be reset
  or re-logged in under the new `profile_key` model.
- Phase 2/9 retention settings are configurable and visible in diagnostics,
  but automated retention cleanup jobs remain for later operations work.
- Docker/container validation could not be run on this machine. Phase 8 used
  an isolated real FastAPI service process with persistent temp data instead.
- Phase 7 and Phase 8 automated checks do not prove real AI provider, SMTP,
  real platform QR scanning, or real platform crawling behavior; those remain
  deployment and pilot risks.
- CR-041 tightens the first usable pilot boundary: Phase 17.1A-B, Phase
  7.1A-C, and a minimum server-like real workflow are required before first
  pilot use. Phase 21, Phase 19B-D, Phase 20, and CR-037 are not first pilot
  blockers unless a later accepted P0 safety, security, or core-flow regression
  changes the boundary. CR-038 is already implemented and verified as a
  frontend-only accessibility follow-up.
- CR-041 Pilot Gate C now has a default-safe evidence template/checker:
  `scripts/pilot_gate_c_evidence.py` can write
  `docs/pilot_gate_c_evidence.example.json` and validate a separate
  operator-filled evidence file. The checker only reads JSON evidence and
  rejects missing real-workflow proof, placeholders, unchecked redaction
  surfaces, secret-looking values, raw local paths, provider endpoints, proxy
  credentials, cookies, and sensitive evidence keys. It does not start
  services, crawl platforms, call AI, mutate data, or send email.
- CR-031 Phase 19B-19D is implemented and locally verified: active Task Center
  rows use the existing `crawl_runs.summary` lifecycle/progress shape for
  provisional collection and AI progress, poll while visible runs are active,
  and keep terminal counts separate from provisional progress. Real platform
  crawl latency and deployment-specific browser/network behavior still require
  pilot observation.
- CR-035 Phase 7.1A-C is implemented and locally verified. Historical run
  `8317` still must not be repaired automatically; Phase 7.1D requires safe
  operational steps, backup, rollback, dry-run preview, and explicit operator
  approval before changing historical AI rows, reports, or terminal status.
- CR-036 Phase 17.1A-D is implemented and locally verified. The product
  direction is not "never send real mail"; real mail must be intentional,
  visible, and attributable through the administrator Mail Configuration
  "真实邮件发送" switch introduced by CR-043. Recipient-source UI/preflight
  explanation and orphan evidence operations notes are now closed for the
  focused follow-up scope; role/quota governance remains deferred as CR-037.
- CR-039 Phase 17.2A-C is implemented and locally verified for template
  provenance, report-body guardrails, sample-data preview wording, send-time
  template explanation, and administrator style presets that wrap the
  system-generated report body.
- CR-045 Phase 7.2A-D reduces the live pilot safety risk for missing
  `ai_evaluations` rows and broad-keyword recall noise: missing rows now
  surface as unevaluated or limited-context rather than no-risk, active
  finalization creates pending-review fallback rows for known unresolved
  candidates when safe, and keyword-only or homonym/geography-only AI model
  positives are forced back to unrelated unless target evidence appears in
  title, description, author, or actually collected comments. AI output remains
  an initial suspected-lead screen, not a factual determination.
- CR-037 is deferred: normal-user email send/resend quotas and administrator
  policy controls are not yet designed. Existing V1 role permissions remain in
  force until a future confirmed phase changes them.
- CR-034 Phase 20B-E is implemented and locally verified: new AI evaluations
  store capped/redacted trace snapshots and run-detail APIs expose scoped
  business-safe summaries plus administrator-only redacted debug snapshots.
  Run Detail now provides the run-scoped frontend entry for lifecycle, logs,
  contents, every AI evaluation, reports, and email delivery, and report leads
  with `run_id` can return to that run detail. Historical AI evaluations
  without saved trace rows remain limited-context and cannot be treated as
  having exact input snapshots.
- CR-048/CR-049 focused frontend information architecture is verified and
  preserved by Phase 20E: Report Center lead drawers remain report/run-scoped
  shortcuts rather than a standalone global lead workbench, and delivery
  history remains a scoped secondary drawer. The full Phase 21 visual
  refinement remains open.
- Phase 18B report-center task grouping is implemented and verified. The
  current frontend has the complete Phase 11-12 foundation and Phase 13A data
  contract: local static module
  boundary, base desktop shell/navigation/button/card/toolbar styling, shared
  interaction helper/fixed floating-menu behavior, responsive
  desktop/tablet/mobile navigation/layout rules, expandable navigation groups,
  operations-home landing, and standardized page entries with role-safe
  task-loop shortcuts, plus role-scoped operations-home aggregates on
  `/api/monitor/dashboard`, a Phase 13B desktop operations-home view with
  visual metric cards and task-loop drilldowns, and Phase 13C tablet/mobile
  role views with concise administrator health and normal-user business-safe
  resource wording. The current schema also has Phase 14 run visibility and
  run type fields, and Phase 15A exposes the corresponding run-center
  governance API layer. Phase 15B now wires that API into the run-center
  frontend with pagination, filters, archive/restore actions, and operational
  versus test/noise separation. Phase 16 adds the email delivery log table,
  window-key helper, safe delivery-log helpers, and auto-window uniqueness
  foundation. Phase 17A connects scheduler/report send logic to that foundation
  so duplicate automatic sends in the same window are skipped, automatic
  failures are logged with customer-safe text, and manual resend is recorded
  separately. Phase 17B now surfaces this history in the report center with
  customer-safe delivery errors, confirmation for manual resend, and
  desktop/tablet/mobile report-center validation. Phase 18A now adds
  `reports.job_snapshot_json`, new-report snapshot persistence, compatible
  backfill for reports whose `job_id` resolves, deleted-task snapshot context,
  limited-context flags for unrecoverable old reports, and owner/workspace
  filtering that does not trust snapshot content. Phase 18B now consumes those
  fields in the report center to group active reports by task, group deleted or
  missing-task reports by stored snapshot, label deleted and limited-context
  history, and keep preview, lead detail switching, downloads, delivery
  history, and row actions tied to the selected report.
- Phase 11 was completed as four verified batches: Phase 11A module boundary
  and tokens, Phase 11B base layout/navigation visual foundation, Phase 11C
  interaction components and floating menus, and Phase 11D responsive
  foundation. A follow-up Phase 11C regression fix now renders Platform
  Account, Monitoring Task, and AI Evaluation Rule row "more" menus from
  page-level floating containers so table scroll areas and sticky action
  columns cannot cover the popup content.
- Phase 12A replaced detached Resource Management and System Configuration
  popover navigation with expandable groups, routed login/session restore to
  Operations Home, and grouped user identity/logout controls for desktop and
  mobile.
- Phase 12B standardized page entry headers and task-loop shortcuts across
  Operations Home, Monitoring, Run Center, Report Center, resource pages, mail
  configuration, runtime settings, and system diagnostics while preserving
  normal-user role boundaries.
- Phase 13A added an operations-home API data contract under the existing
  dashboard endpoint, preserving old summary fields while exposing task
  health, run activity, report activity, email delivery latest state,
  suspected lead metrics, and concise resource health for Phase 13B/13C.
- Phase 13B replaced the default text-heavy overview with desktop visual
  operations metrics, role-safe drilldowns, concise resource health, and a
  collapsed administrator diagnostics section while keeping the Phase 13A API
  contract and old dashboard compatibility.
- Phase 13C adapted the operations home for 1024px tablet and 390px mobile,
  kept normal-user metrics business-safe, moved detailed readiness/scheduler/
  platform diagnostics to System Diagnostics, and retained only a compact
  administrator health summary on the home page.
- Email delivery-history UI and report task grouping are accepted directions.
  Run visibility/noise-filtering data fields are active schema features after
  Phase 14, archive/restore APIs, pagination, and filters are active after
  Phase 15A, frontend run-center controls are active after Phase 15B, and
  email delivery logs are active schema features after Phase 16. Automatic-send
  idempotency in the scheduler/report delivery workflow is active after Phase
  17A; report-center delivery-history UI is active after Phase 17B; report
  snapshots are active after Phase 18A; report task grouping is active after
  Phase 18B.
- The first global Phase 10-18 review found that Phase 13, Phase 17, and Phase
  18 were too coarse as single goals. The plan now splits them into data/API
  and frontend/responsive batches.
- Phase 10.5 follow-up global review found no remaining P0/P1 blockers.
  Remaining review notes were P2 implementation refinements and did not block
  Phase 11-18 execution. Phase 18B preserved Phase 18A snapshot/permission
  behavior and did not use snapshot content to grant access.

## Next Step

Next allowed implementation order:

Before opening any non-trivial item below, create or confirm the CR-081 goal
packet from `docs/GOAL_EXECUTION_GUIDELINES.md`: owner CR/phase, baseline,
scope, out-of-scope, hard boundaries, start gate, expected touch surface,
execution steps, tests, acceptance, rollback/recovery, documentation updates,
and stop conditions.

1. finish and merge the active Phase 21 worktree as frontend-only visual
   refinement on the current Task Center / Run Detail baseline. Do not run
   multiple Phase 21/UI worktrees that edit `api/monitor_web/index.html`,
   `api/webui/monitor/monitor.css`, or `api/webui/monitor/monitor.js` at the
   same time unless the split is deliberately coordinated;
2. run Phase 5.1P Preflight as a documentation/read-only compatibility goal
   before Phase 5.1 schema or code work. It must map QR login, Cookie
   validation, login-state checks, manual run, scheduler run, runner behavior,
   and MediaCrawler CDP launch/reconnect to one BrowserEnvironmentProvider
   output and one requested/effective snapshot contract. It must not create or
   change schema, code, provider implementation, runtime data, profiles,
   cookies, proxies, crawler behavior, deployment configuration, or database
   state; if any current path cannot be mapped to that provider/snapshot
   contract, stop Phase 5.1 and record the ambiguity instead of starting Phase
   5.1A-D;
3. implement CR-047/Phase 5.1 account identity fidelity only after the
   preflight passes, using the confirmed policy that locked account
   environments reject task-level proxy overrides and using container/server-
   like execution as the development and acceptance baseline;
4. implement CR-070/Phase 5.2 account-environment export/import only after
   CR-047 provider binding and requested/effective runtime snapshot behavior
   are implemented and verified;
5. keep CR-078 `/monitor-next` planning, CR-079 MediaCrawler public exposure
   boundary, and CR-080 crawler provider architecture as future independent
   backlog lanes. They may receive read-only planning or documentation
   refinement, but they must not be treated as current implementation work,
   Phase 21 work, Phase 5.1P prerequisites, or CR-070 prerequisites without a
   later accepted decision;
6. after the active Phase 21 worktree is merged, run a small documentation
   cleanup pass to verify CR numbering, duplicate/overlapping Phase21 boundary
   wording, and whether any Phase21-completed visual or wording items should
   be referenced rather than repeated in CR-078/079/080;
7. keep Phase 17.1D historical orphan email evidence closed as read-only
   dry-run/checklist/runbook work unless the operator explicitly approves a
   backup, rollback, and mutation path;
8. handle CR-035/Phase 7.1D historical run remediation only when the operator
   explicitly approves the dry-run, backup, rollback, and repair path; it is a
   conditional operations task, not a normal feature batch;
9. keep CR-037 role-based email governance and the currently unrendered Users
   And Permissions page as separate future/new-capability work until confirmed;
10. prepare broader production pilot handoff and deployment-specific validation
   for additional live credentials after the first usable pilot baseline.

Test gate hardening recorded:

- CR-047 now has a confirmed no-task-proxy-override policy for locked account
  environments and still requires stable identity generation tests,
  self-consistency validation tests, and fail-closed browser-environment tests.
  It also has a V1 provider boundary: unsupported high-fidelity surfaces must
  be reported as not-managed or future/provider-dependent, not silently claimed.
  Phase 5.1P preflight is now required before implementation so QR login,
  Cookie validation, login-state checks, manual runs, scheduler runs, and
  MediaCrawler CDP launch/reconnect share one provider output and the same
  requested/effective snapshot contract.
- CR-045 now requires a noisy-positive model override fixture so keyword-only
  evidence cannot backdoor target-related negative classification.
- Phase 17.1D now requires dry-run no-op proof plus backup/approval gates
  before any mutation path.
- Phase 19 now requires disappearing-subprocess and repeated-finalization
  coverage so a run cannot stay stuck in provisional progress.
- Phase 20 now requires trace-write-failure and retention-cleanup safety so
  finalization cannot be blocked or mutate business rows.
- CR-048 and CR-049 now require UI tripwires for unlabeled lead tables and
  duplicated mail edit/test actions.
- CR-078, CR-079, and CR-080 are intentionally separate from Phase 21 and
  Phase 5.1P. `/monitor-next` planning cannot modify the current `/monitor`
  console; MediaCrawler public exposure work cannot be treated as frontend
  visual polish; and crawler provider architecture cannot become the
  Phase 5.1P prerequisite unless a later accepted decision changes the
  roadmap.
- CR-081 requires atomic goal packets and the iteration rule before future
  non-trivial work starts. A goal should not advance while targeted tests,
  required broader checks, documentation consistency, acceptance gates, or
  blocking cross-review findings remain open.

Lowest-risk parallel execution lane:

1. Phase 21 frontend-only page-level refinement may proceed in its existing
   worktree. Phase 5.1P can be prepared only as read-only document/code-path
   mapping after Phase 21 merge or in a deliberately coordinated non-UI
   worktree; it must not create schema, code, provider, runtime, profile,
   cookie, proxy, crawler, deployment, or database changes before the preflight
   is explicitly accepted. Phase 5.1 code/schema implementation should wait for
   the preflight result.

Do not run Phase 19 and Phase 20 in parallel, and do not run more than one
frontend worktree that edits the formal console shell at the same time.
CR-038, CR-045, CR-050, and CR-074 are already verified follow-ups and should
remain historical closed items rather than next implementation tasks. CR-070
must not start before CR-047 provider/effective snapshot verification.

## Latest Verification

Phase 17.1D historical orphan email evidence verification on 2026-06-18:

- Added `scripts/review_orphan_email_evidence.py` as a read-only dry-run helper
  for delivery-log rows whose `job_id` or `report_id` no longer resolves to
  active records.
- The helper reports delivery-log id, `job_id`, `report_id`, send type/status,
  sent/created time, job/report/run existence, artifact existence,
  classification, `mode=dry_run`, `mutations_attempted=0`, and the database
  backup, artifact/email backup, explicit operator approval, and rollback
  gates required before any future mutation.
- Documented the observed CR-036 historical evidence for delivery-log rows `60`
  and `81`, `job_id=9686` / `run_id=8380` / `report_id=3959` and
  `job_id=9759` / `run_id=8447` / `report_id=3998`, including exported `.eml`
  references, attachment names, missing job/run/report rows, and the default
  preserve policy.
- Verified the helper does not mutate `email_delivery_logs`, `reports`, or
  `crawl_runs`, does not change artifact files, and keeps existing non-orphan
  report delivery history readable.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_17_1d or phase_17b_email_delivery_history_api_scope_and_safe_fields or phase_17b_report_center_delivery_history_frontend_hooks or phase_18b_report_center_task_grouping_frontend_hooks"`
- Result: 4 passed, 288 deselected, 3 warnings.
- `uv run python -m py_compile scripts\review_orphan_email_evidence.py tests\test_monitoring_mvp.py`
- Result: PASS.

Phase 18B report-center task grouping frontend verification on 2026-06-16:

- Updated the report-center list rendering path to group reports by active
  monitoring task when `job_id` resolves.
- Grouped deleted or missing-task reports using the customer-safe
  `job_snapshot` fields exposed by Phase 18A.
- Added deleted-task, historical snapshot, and limited-context labels without
  exposing raw `job_snapshot_json`.
- Preserved per-report preview, lead detail switching, download links, email
  delivery latest state/history, manual resend menu entry, and row actions.
- Added responsive grouped-report styles for desktop, tablet, and mobile.
- Verified administrator and normal-user role paths without changing API,
  schema, permission, or data-scope behavior.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before documentation update.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_18b or phase_18a or phase_17b or report_resend_email_updates_status or report_history_keeps_law_firm_snapshot_after_job_deleted or leads_api_can_scope_items_to_selected_report"`
- Result: 8 passed, 228 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 236 passed, 3 warnings.
- Inline monitor page script parse check and `python -m py_compile
  tests\test_monitoring_mvp.py`
- Result: PASS.
- Browser validation on isolated service `127.0.0.1:19218` with temporary
  data:
  - `/monitor`, `/static/monitor/monitor.css`, and
    `/static/monitor/monitor.js` returned HTTP 200;
  - administrator login opened Report Center with active-task, deleted-task,
    missing-task snapshot, and limited-context historical groups;
  - grouped report labels, platform/keyword/frequency chips, preview drawer,
    report-specific lead switching, report download menu links, latest email
    status, and delivery-history rows stayed tied to report ID 1;
  - 1440px, 1024px, and 390px report-center checks found four groups, no
    page-level horizontal overflow, and no authenticated console/page errors;
  - normal-user login kept Report Center visible and administrator resource or
    diagnostics entries hidden.

Phase 18A report job snapshot data model verification on 2026-06-16:

- Added `reports.job_snapshot_json` to new database creation and compatible
  existing-database migration.
- Added shared report job snapshot builders for law firm, platforms, search
  keywords, frequency, task ID, and deleted-task context.
- Persisted snapshots for newly generated reports.
- Backfilled snapshots for existing reports whose `job_id` still resolves to
  `monitor_jobs`.
- Preserved `job_id` as the active or historical task relation while marking
  deleted-task reports from the stored snapshot context.
- Kept unrecoverable old reports readable as limited-context historical
  reports.
- Preserved owner/workspace filtering by resolving reports through the current
  report/job/creator scope and never using snapshot content to grant access.
- Exposed customer-safe `job_snapshot`, `job_deleted`,
  `legacy_without_job_snapshot`, and `limited_context` fields through existing
  report views for Phase 18B consumption.
- Did not implement Phase 18B frontend report grouping or grouped report
  layouts.
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

Phase 17B email delivery history frontend verification on 2026-06-16:

- Added a report delivery-history API endpoint scoped by the current
  administrator/normal-user actor and backed by `email_delivery_logs`.
- Kept report visibility and owner/workspace filtering by resolving the report
  through `get_report(..., actor=actor)` before returning delivery logs.
- Returned customer-safe delivery-log fields only and scrubbed sensitive labels
  such as SMTP passwords, tokens, cookies, and proxy secrets from visible
  delivery errors.
- Updated the report center to show latest delivery status, clickable delivery
  status cells, a delivery-history panel, send type, status, time, recipients,
  send-window key, and customer-safe error messages.
- Added a report action for viewing delivery history and required confirmation
  before manual resend; after resend the report list and selected history
  refresh.
- Preserved report preview, lead detail switching, downloads, run-center
  navigation, task-list and task-create entry behavior, logout, and
  administrator/normal-user role visibility.
- Did not add Phase 18 report snapshots, report grouping, schema changes, or
  new frontend dependencies.
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
- Runtime browser validation on isolated service `127.0.0.1:19217`:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200; administrator login opened
  the console; report center loaded sample reports; delivery history displayed
  automatic and manual-resend rows with recipients, window key, status, time,
  and no secret-label leakage; 1440px, 1024px, and 390px report-center checks
  kept the delivery-history surface usable without page-level horizontal
  overflow; report preview drawer, report row menu, run center, task list,
  task-create entry, logout, and normal-user role-visible navigation were
  checked with no console errors.

Phase 17A email idempotency and delivery logic verification on 2026-06-16:

- Connected report automatic email delivery to the Phase 16
  `email_delivery_logs` foundation.
- Used `send_window_key` generation for `daily`, `6h`, `12h`, and `cron`
  through the accepted data-model helper.
- Added automatic-send idempotency by `workspace_id + job_id +
  send_window_key + send_type=auto`; repeated automatic sends in the same
  window record a skipped delivery log and do not call the mailer again.
- Recorded automatic delivery attempts, successes, failures, recipient
  summaries, and customer-safe errors in `email_delivery_logs`.
- Recorded explicit manual resend as a separate `send_type=manual_resend`
  delivery log with the acting user ID while keeping automatic idempotency
  independent.
- Preserved report generation when SMTP is unavailable and kept
  `reports.email_status` / `reports.email_error` readable until Phase 17B
  migrates the report center to delivery history.
- Passed Phase 17A focused and related regression tests, plus the full
  monitoring MVP test suite.
- Did not implement Phase 17B report-center delivery-history frontend or
  Phase 18 report grouping/snapshot behavior.
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

Phase 16 email delivery data model preparation verification on 2026-06-16:

- Added `email_delivery_logs` to new database creation and compatible existing
  database migration.
- Stored `workspace_id`, `job_id`, `report_id`, `send_window_key`,
  `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
  `recipients_json`, and `created_at`.
- Added allowed send types `auto` and `manual_resend`, allowed statuses
  `pending`, `sending`, `sent`, `failed`, and `skipped`, and send-window key
  generation for `daily`, `6h`, `12h`, and `cron`.
- Added Phase 16 indexes:
  `idx_email_delivery_job_window`, `idx_email_delivery_report`, and
  `idx_email_delivery_status`.
- Added partial unique index `idx_email_delivery_auto_window_unique` so one
  pending, sending, or sent automatic delivery can exist for the same
  workspace, task, window, and `send_type=auto`, while failed/skipped retries
  and manual resend rows can be recorded separately.
- Preserved existing `reports.email_status` and `reports.email_error`
  compatibility fields.
- Ensured delivery-log helper output and stored errors use customer-safe
  sensitive text handling and do not store SMTP passwords, proxy credentials,
  or tokens.
- Did not implement Phase 17A scheduler/mailer send-flow idempotency or Phase
  17B delivery-history frontend.
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

Phase 15B run center frontend refinement verification on 2026-06-16:

- Added run-center pagination controls and page metadata rendering.
- Added task/law-firm, status, platform, run type, visibility, date, and page
  size filters wired to the Phase 15A run-list API.
- Added the default `run_type=operational` view so scheduled/manual
  operational records are separated from `test` noise records unless the user
  explicitly filters for test/diagnostic records.
- Added administrator-only archive and restore row actions with confirmation.
  Normal users keep visible-record scope and cannot request archived/all
  records.
- Preserved run-log drawer behavior, including refresh, copy, download, and
  customer-safe log text.
- Verified `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200 in the isolated browser
  service.
- Verified desktop 1440px, tablet 1024px, and mobile 390px run-center
  layouts keep filters, status, actions, summary, pagination, and table
  content reachable without horizontal page overflow.
- Verified administrator archive/restore API behavior through the running
  browser service: run ID 1 moved from visible to archived and restored back
  to visible. Verified normal-user API scope returns `403` for archived
  visibility and archive action.
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

Phase 15A run center API and data governance verification on 2026-06-16:

- Added run API/query pagination with `pagination` response metadata while
  preserving existing `runs` and `running_job_ids` response fields.
- Added filters for task ID, law firm, status, platform, run type, visibility,
  and date range.
- Added administrator-only archive and restore APIs that update run visibility
  without physically deleting records.
- Default run-list API behavior now hides archived records; administrators can
  request archived or all records explicitly, while normal users cannot.
- Preserved owner/workspace scope, existing status values, report links, and
  run-log access for visible runs.
- Did not add Phase 15B frontend pagination, filter controls, or row
  archive/restore controls.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_15a or run_logs or list_runs"`
- Result: 2 passed, 225 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 227 passed, 3 warnings.

Phase 14 run center data model preparation verification on 2026-06-16:

- Added `crawl_runs.visibility`, `crawl_runs.run_type`,
  `crawl_runs.archived_at`, and `crawl_runs.archived_by` to new database
  creation and compatible existing-database migration.
- Backfilled empty existing run rows to `visibility = visible` and
  `run_type = scheduled`.
- Added `idx_crawl_runs_visibility` on
  `(workspace_id, visibility, started_at)` and `idx_crawl_runs_type_status` on
  `(workspace_id, run_type, status)` for Phase 15 filters.
- Verified existing run reads, run list reads, report links, and status values
  remain readable after the migration.
- Did not add Phase 15 pagination, filters, archive/restore APIs, frontend
  controls, email delivery logs, or report grouping.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_14 or phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 13 passed, 213 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 226 passed, 3 warnings.

Phase 13C operations home responsive and role views verification on
2026-06-16:

- Adapted the operations home for tablet and mobile so metric cards, drilldown
  entries, resource signals, and administrator health summary wrap without
  horizontal overflow.
- Replaced the home-page detailed diagnostics block with a compact
  administrator-only system health summary and moved detailed readiness,
  scheduler, platform status, and checklist sections to System Diagnostics.
- Preserved normal-user business-safe resource wording and kept administrator
  resource-health drilldowns and System Diagnostics hidden from normal users.
- Preserved the Phase 13A dashboard API contract and did not add schema,
  email-delivery-log, run-archive, or report-grouping fields.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13c or phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 12 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` and
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator 1440px, 1024px, and 390px checks found five metric cards
  and no horizontal overflow; administrator System Diagnostics drilldown showed
  readiness, scheduler, and platform status details; normal-user 1024px and
  390px checks found business-safe resource wording, no administrator health
  summary, no account/system-diagnostics shortcuts, no horizontal overflow, and
  task drawer, Run Center, Report Center, and logout paths remained reachable.

Phase 13B operations home desktop visual metrics verification on
2026-06-16:

- Replaced the default text-heavy Overview content with an operations-home
  metric surface rendered from the Phase 13A `operations_home` contract, while
  preserving a legacy dashboard summary fallback during migration.
- Added five desktop visual metric cards for task health, run activity, report
  and review status, email delivery latest state, and suspected negative
  leads.
- Added task-loop drilldowns into Monitoring, Run Center, Report Center,
  report email delivery status, and administrator platform-account resources
  where permitted.
- Kept system readiness, scheduler, and platform diagnostics under a collapsed
  administrator-only diagnostics section instead of the default first-screen
  home content.
- Used native HTML/CSS with existing CSS tokens and did not add a chart
  library or other frontend dependency, so no new `DECISIONS.md` entry was
  required.
- Preserved normal-user role safety: normal users receive business-safe
  resource wording and do not see administrator resource drilldowns or system
  diagnostics.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 11 passed, 213 deselected, 3 warnings.
- Inline script parse check for `api/monitor_web/index.html` and
  `node --check api/webui/monitor/monitor.js`
- Result: PASS.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator and normal-user authenticated console paths had no page
  or console errors; administrator 1440px, 1024px, and 390px checks found five
  metric cards and no horizontal overflow; administrator drilldowns reached
  jobs, runs, reports, email delivery status, and accounts; diagnostics were
  collapsed by default; normal-user navigation exposed only `总览`, `舆情监控`,
  `运行中心`, and `报告中心`; normal users saw `资源由管理员维护`, no resource
  drilldown, and no system diagnostics.

Phase 13A operations home data layer verification on
2026-06-15:

- Added `summary.operations_home` to the existing dashboard summary contract
  and returned the same object as top-level `operations_home` from
  `/api/monitor/dashboard` for the Phase 13B frontend migration.
- Preserved existing flat dashboard fields such as `jobs_total`,
  `runs_total`, `reports_total`, `contents_total`,
  `failed_runs_recent`, `skipped_runs_recent`, and administrator resource
  totals.
- Aggregated task health, run activity, report activity, email delivery latest
  state from `reports.email_status`, suspected lead metrics from
  `ai_evaluations`, and concise resource health from existing persisted data.
- Preserved administrator workspace-wide visibility and normal-user
  owner/workspace scoping; normal users receive business-safe resource health
  without platform account, proxy, AI profile, or login-session counts.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency before implementation.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k phase_13a`
- Result: 1 passed, 222 deselected, 3 warnings.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13a or phase_12b or phase_12a or phase_11a or phase_11b or phase_11c or phase_11d or monitor_page_uses or readiness_dashboard"`
- Result: 10 passed, 213 deselected, 3 warnings.

Phase 12B page entry and role flow verification on
2026-06-15:

- Standardized page entry headers across Operations Home, Monitoring, Run
  Center, Report Center, account resources, proxy resources, AI access, AI
  rules, mail configuration, mail templates, runtime settings, and system
  diagnostics.
- Added task-loop shortcuts for creating a monitoring task, viewing runs,
  viewing reports, checking report email delivery status, and resolving
  administrator resource issues where permitted.
- Replaced the header refresh affordance with current-page refresh behavior
  and kept Operations Home using the existing `dashboard` route ID.
- Preserved Phase 12A expandable navigation, login/session landing,
  account/logout grouping, and role visibility behavior.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator path exposed 12 page entries and 5 Operations Home
  shortcuts; task-loop shortcuts opened the task drawer and navigated jobs ->
  runs -> reports; the report email delivery entry was visible; normal-user
  navigation only exposed `总览`, `舆情监控`, `运行中心`, and `报告中心`; normal-user
  Operations Home exposed 4 task-loop shortcuts and no administrator resource
  shortcuts; 1440px, 1024px, and 390px checks found no business-area horizontal
  overflow; mobile navigation opened, switched to Monitoring, and closed; page
  console errors were empty.

Phase 12A navigation structure and login landing verification on
2026-06-15:

- Replaced detached hover popovers for Resource Management and System
  Configuration with expandable navigation groups in
  `api/monitor_web/index.html` and `api/webui/monitor/monitor.css`.
- Routed successful login and session restore to Operations Home when no
  explicit allowed destination is present.
- Grouped authenticated user identity and logout in the desktop top-right
  account area and added a predictable mobile account area in the navigation
  drawer.
- Preserved administrator and normal-user menu visibility rules.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; form login and session restore landed on `dashboard`; administrator
  groups expanded/collapsed; mobile nested navigation reached
  `email_templates` and closed the drawer; normal-user navigation only exposed
  `总览`, `舆情监控`, `运行中心`, and `报告中心`; authenticated console/page errors
  were empty.

Phase 11D responsive foundation verification on
2026-06-15:

- Implemented the accepted desktop `>= 1280px`, tablet `768px - 1279px`, and
  mobile `< 768px` breakpoint foundation in `api/webui/monitor/monitor.css`.
- Added touch-safe mobile navigation hooks in `api/monitor_web/index.html`:
  hamburger toggle, primary sidebar/navigation IDs, and a navigation backdrop.
- Added mobile navigation behavior for open, backdrop close, Escape close,
  page-switch close, and desktop-resize reset.
- Kept dense tables scroll-safe on mobile while leaving page-specific card
  conversions to later page phases.
- Added a normal-user frontend permission guard so mail-template preview
  polling does not call administrator-only endpoints.
- Runtime browser validation on an isolated local service verified `/monitor`,
  `/static/monitor/monitor.css`, and `/static/monitor/monitor.js` returned HTTP
  200; administrator and normal-user authenticated paths loaded with no
  console/page errors; 1440px, 1024px, and 390px checks covered navigation,
  task-create entry, run log drawer, report preview drawer, and report action
  menu.

Phase 11C interaction components and floating menu verification on
2026-06-15:

- Added shared toast, loading, empty-state, modal, drawer, and action-menu
  styles to `api/webui/monitor/monitor.css`.
- Added the `window.MonitorUI` helper boundary in
  `api/webui/monitor/monitor.js` with toast, loading, empty-state,
  close-menu, portal-root, and fixed floating-menu positioning helpers.
- Reworked account, monitoring-task, AI-rule, and report row menus to use
  fixed viewport placement through local helpers instead of a new dependency.
- Verified row menus close on outside click, Escape, page change, and action
  execution. Proxy, AI access, and mail-template surfaces currently use direct
  edit/test/preview actions and have no row-menu clipping surface in this
  batch.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or phase_11c or monitor_page_uses"`
- Result: 5 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright authenticated interaction check:
  account, monitoring-task, AI-rule, and report menus used `position: fixed`,
  stayed inside the viewport, and closed on outside click and Escape; run
  center and report center smoke checks passed at 1024px and 390px.

Phase 11B base layout and navigation visual foundation verification on
2026-06-15:

- Moved base shell, side navigation, header, button, card, metric-card,
  toolbar, page-toolbar, toolbar-action, and page-action styling into
  `api/webui/monitor/monitor.css`.
- Kept page IDs, navigation data attributes, inline JavaScript behavior,
  business data flow, and role/menu visibility unchanged.
- Preserved table, modal, form, report-preview, task-wizard, AI-rule,
  mail-template, and resource-specific styling for later batches.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or phase_11b or monitor_page_uses"`
- Result: 4 passed, 214 deselected, 1 warning.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright desktop 1440px authenticated smoke check:
  login, logout, dashboard, monitoring task list, run center, report center,
  task-create entry, Resource Management popover, and System Configuration
  popover remained reachable with no console or page errors.

Phase 11A frontend module boundary verification on 2026-06-15:

- Added `api/webui/monitor/monitor.css` and
  `api/webui/monitor/monitor.js`.
- Referenced `/static/monitor/monitor.css` before the existing inline
  `<style>` block and `/static/monitor/monitor.js` after the existing inline
  `<script>` block.
- Kept existing inline CSS/JS behavior in place; no visible UI redesign was
  introduced.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_11a or monitor_page_uses"`
- Result: 3 passed, 214 deselected, 4 warnings.
- Runtime HTTP check on isolated local service:
  `/monitor`, `/static/monitor/monitor.css`, and
  `/static/monitor/monitor.js` returned HTTP 200.
- Playwright authenticated smoke check at 1440px, 1024px, and 390px:
  dashboard, monitoring task list, run center, report center, and task-create
  entry remained reachable with no console or page errors.

Phase 10-18 documentation planning verification on 2026-06-15:

- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Phase 10.5 global roadmap review verification on 2026-06-15:

- Phase 10-18 global复审 result: PASS; no P0/P1 blockers.
- Phase 13, Phase 17, and Phase 18 have been split into smaller execution
  batches.
- Phase 11A is allowed as the next execution goal.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Phase 10 frontend architecture verification on 2026-06-15:

- Frontend structure audit found the monitor console is served from
  `api/monitor_web/index.html`, over 4,000 lines long, with inline CSS and
  JavaScript and coarse `1100px`/`720px` breakpoints.
- The FastAPI app keeps `/monitor` as the direct console entry and already
  exposes `/static` for local static assets.
- Decision: keep `/monitor` and the no-build path, but Phase 11 should split
  the design-system layer into local CSS/JS modules instead of expanding the
  inline file.
- Follow-up planning refinement: Phase 11 is split into 11A-11D, Phase 12 is
  split into 12A-12B, and Phase 15 is split into 15A-15B so each batch can be
  executed and verified with a bounded goal.

Phase 9 security and operations verification passed on 2026-06-14:

- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_9 or doctor_reports_deployment_diagnostics or readiness_status_reports_checks or sensitive_text_is_redacted"`
- Result: 6 passed, 210 deselected, 1 warning.
- `uv run python scripts/server_like_validation.py`
- Result: PASS, 11 checks passed: service web UI reachable, administrator
  login over HTTP, web QR/status login flow primary, local-window login
  disabled, same-platform profiles separated, profile-key runtime paths under
  the persistent profile root, account/profile lock limit enforced through
  runtime API, proxy lock enforced through `resource_locks`, profile metadata
  survives restart, no local Chrome dependency, and headless Playwright
  Chromium available.
- `uv run python -m pytest tests/test_monitoring_mvp.py`
- Result: 216 passed, 3 warnings.
- `uv run python scripts/check_docs.py`
- Result: PASS docs consistency.

Earlier Phase 7 and Phase 8 verification remains recorded in
`docs/TEST_RESULTS.md`.
