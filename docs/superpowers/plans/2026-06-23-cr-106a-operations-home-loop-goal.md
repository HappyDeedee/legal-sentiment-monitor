# CR-106A Operations Home Loop Goal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement CR-106A so the `/monitor` Operations Home first screen becomes more data-aware and action-first on top of the verified CR-105A local-ECharts dashboard baseline.

**Architecture:** Keep the current no-build Vanilla JavaScript `/monitor` frontend and local ECharts renderer. Refine only the Operations Home view-model, labels, chart options, static tests, responsive CSS, and verification docs; do not change backend schema, dashboard API contracts, Task Center, Run Detail, routes, permissions, drawers, modals, select/date behavior, crawler behavior, AI behavior, or email execution behavior.

**Tech Stack:** HTML with inline Vanilla JavaScript in `api/monitor_web/index.html`, CSS in `api/webui/monitor/monitor.css`, locally vendored Apache ECharts at `api/webui/monitor/vendor/echarts.min.js`, pytest static/API coverage in `tests/test_monitoring_mvp.py`, project docs under `docs/`.

---

## Execution Mode

Choose one execution mode before implementation starts:

1. **Subagent-Driven (recommended)**: execute each task with a fresh subagent, review the result after each task, then continue to the next loop only after the current loop passes. This is preferred for CR-106A because it has multiple UI/data/test/browser acceptance loops and needs frequent boundary review.
2. **Inline Execution**: execute the plan in the current session with checkpoint reviews between loops. Use this when the user wants tighter interactive control or does not want separate subagents.

Default mode for `/goal` execution: Subagent-Driven unless the user explicitly asks for Inline Execution.

## Loop Engineering Contract

CR-106A must be executed as a sequence of closed loops:

```text
baseline -> failing/strengthened test -> minimal change -> targeted check
-> browser or static acceptance -> documentation sync -> next loop
```

Do not batch the whole dashboard change and test only at the end. Each loop must either pass and move forward, or stay in that loop until the failure is fixed. If a loop reveals a need for backend fields, `email_delivery_logs` dashboard aggregation, permissions, routes, Task Center, Run Detail, overlay behavior, or external email/crawler/AI behavior changes, stop and record the blocker instead of expanding CR-106A.

## Current Baseline

- CR-105A is implemented and verified as the current `/monitor` Operations Home ECharts baseline.
- CR-097 through CR-103 are historical/archive-only and must not reintroduce `流程总览`, `.operations-stage-*`, heatmap-block, or no-chart-library constraints.
- CR-104 is the historical pre-ECharts handcrafted chart baseline; do not restore `.operations-trend-svg`, `operationsTrendLinePath()`, or `operationsTrendAreaPath()`.
- CR-106A is accepted and documentation/planning-ready.
- CR-106B remains `Needs Confirmation`; any Operations Home aggregation from `email_delivery_logs` is out of CR-106A.
- Current key implementation surface:
  - `api/monitor_web/index.html`: `operationsOverviewViewModel()`, `renderOperationsHome()`, `renderOperationsTrendChart()`, `renderOperationsIssueChart()`, `renderOperationsBreakdowns()`, `renderOperationsResourceHealth()`, `operationsTrendOption()`, `operationsIssueOption()`, `operationsPlatformOption()`, `operationsDeliveryOption()`, `operationsResourceOption()`, chart action routing, and trend aggregation helpers.
  - `api/webui/monitor/monitor.css`: CR-105 Operations Home layout and responsive rules.
  - `tests/test_monitoring_mvp.py`: Phase 13A API aggregate coverage plus Phase 13B/13C Operations Home static and responsive role assertions.

## In Scope

- Refine the Operations Home top status so a user can read today's health before decoding every chart.
- Make `问题分布` action-first: high-risk leads, pending review, mail failure, then run failure/skip should not be buried by raw count ordering.
- Make `平台分布` distinguish volume from failure signal using existing dashboard/runs/reports fields such as `platform_results` and `failed_platforms` when available.
- Label and map the `邮件` module as report-level delivery state from `reports.email_status`.
- Keep `email_delivery_logs` out of Operations Home dashboard aggregation.
- Make administrator `资源健康` more action-oriented while normal users see no account/proxy/AI/SMTP/session details and no empty resource placeholder.
- Improve mobile first-screen density so KPI cards do not dominate before `监控走势` and `问题分布`.
- Preserve local ECharts, stable chart container dimensions, no remote chart assets, role-safe reflow, and current drilldowns.
- Update tests and docs after implementation.

## Out Of Scope

- Backend schema changes, migrations, or new persisted dashboard metrics.
- `/api/monitor/dashboard` data contract changes that require new backend aggregation.
- CR-106B `email_delivery_logs` dashboard aggregation.
- Task Center, Run Detail, drawers, modals, enhanced select/date controls, route normalization, permission model, owner/report scope, top-bar refresh behavior.
- Crawler behavior, AI provider behavior, report generation behavior, SMTP/email execution behavior, real platform login, real crawling, or real email sending.
- Task funnel, risk matrix, keyword heat, AI quality analytics, task ranking, 30-day backend trend buckets, React/Vue/build pipeline migration.

## Hard Boundaries

- Do not add remote ECharts, CDN, unpkg, jsdelivr, Chart.js, React, Vue, Vite, Tailwind, or component-framework dependencies.
- Do not query, aggregate, expose, or reference `email_delivery_logs` from the Operations Home dashboard section for CR-106A.
- Do not display recipients, SMTP secrets, proxy URLs, cookies, profile paths, account names, raw delivery errors, or administrator-only resource details to normal users.
- Red is reserved for failure, exception, or high-risk meaning. Platform category colors must not imply failure unless separately encoded as a failure signal.
- Loading, empty, stale, and chart-local error states must keep layout dimensions stable.
- Local sample counts are planning evidence only; tests must use bounded fixtures or safe assertions, not hard-code the current local database counts as product truth.

## Start Gate

Before code changes:

- [ ] Read `AGENTS.md`.
- [ ] Read `docs/GOAL.md`.
- [ ] Read `docs/CURRENT_STATE.md`.
- [ ] Read `docs/TASKS.md`.
- [ ] Read `docs/DECISIONS.md`.
- [ ] Read `docs/CHANGE_REQUESTS.md`.
- [ ] Read `docs/TRACEABILITY.md`.
- [ ] Read `docs/TEST_PLAN.md`.
- [ ] Read `docs/FRONTEND_ARCHITECTURE.md`.
- [ ] Read `docs/UI_UX_GUIDELINES.md`.
- [ ] Read `docs/PRODUCT_REQUIREMENTS.md`.
- [ ] Read `docs/TEST_RESULTS.md`.
- [ ] Read `api/monitor_web/index.html`.
- [ ] Read `api/webui/monitor/monitor.css`.
- [ ] Read `api/webui/monitor/monitor.js`.
- [ ] Read `tests/test_monitoring_mvp.py`.
- [ ] Confirm CR-105A is the current verified baseline.
- [ ] Confirm CR-106A is the current executable goal.
- [ ] Confirm CR-106B remains `Needs Confirmation`.
- [ ] Confirm current worktree same-file changes are understandable. Stop if same-file conflicts make it impossible to separate this work from existing unfinished edits.

## Expected Touch Surface

- Modify: `api/monitor_web/index.html`
- Modify: `api/webui/monitor/monitor.css`
- Modify: `tests/test_monitoring_mvp.py`
- Modify after verification: `docs/TASKS.md`
- Modify after verification: `docs/CURRENT_STATE.md`
- Modify after verification: `docs/TEST_RESULTS.md`
- Modify after verification: `docs/TRACEABILITY.md`

Avoid editing:

- `api/routers/monitor.py`
- `api/monitoring/database.py`
- `api/monitoring/reporting.py`
- `api/monitoring/mailer.py`
- Task Center, Run Detail, drawer, modal, select/date, route, permission, crawler, AI, and email execution code.

## Task 1: Baseline And Tripwire Tests

**Files:**

- Modify: `tests/test_monitoring_mvp.py`
- Read: `api/monitor_web/index.html`

- [ ] **Step 1: Strengthen static baseline tests**

Add or extend CR-106A assertions near the existing Phase 13B/13C Operations Home tests. The assertions should prove:

```python
page = Path("api/monitor_web/index.html").read_text(encoding="utf-8")
dashboard_section = _monitor_section(page, "dashboard")
operations_block = page.split("const operationsOverviewState = {", 1)[1].split("function metricSkeletonGrid", 1)[0]

assert "function operationsOverviewViewModel(home, trendPayload=null)" in page
assert "function operationsIssueOption(model)" in page
assert "function operationsPlatformOption(model)" in page
assert "function operationsDeliveryOption(model)" in page
assert "reports.email_status" in page or "report-level" in page or "报告级" in page
assert "email_delivery_logs" not in dashboard_section
assert "email_delivery_logs" not in operations_block
assert "operationsTrendLinePath" not in operations_block
assert "operationsTrendAreaPath" not in operations_block
assert 'class="operations-trend-svg"' not in operations_block
```

- [ ] **Step 2: Add semantic test markers for CR-106A**

Add assertions that fail until the implementation has explicit CR-106A semantics:

```python
for marker in [
    "operationsHealthSummary",
    "operationsIssueSeverityRank",
    "operationsPlatformFailureRows",
    "报告级邮件状态",
    "CR-106A data-aware signal refinement",
]:
    assert marker in page
```

- [ ] **Step 3: Run the targeted test and verify it fails before implementation**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c" -q
```

Expected before implementation: failure on the new CR-106A markers only. If unrelated failures appear, stay in Task 1 and understand them before editing code.

## Task 2: Top Status And Action-First Issue Model

**Files:**

- Modify: `api/monitor_web/index.html`
- Test: `tests/test_monitoring_mvp.py`

- [ ] **Step 1: Add a health-summary helper**

Add a small helper near `operationsToneLabel()` or `operationsOverviewViewModel()`:

```javascript
function operationsHealthSummary(model){
  const issueTotal=model.priorities.reduce((sum, item)=>sum + visualValue(item.value), 0);
  const highRisk=model.priorities.find(item=>item.key === 'high_risk');
  const pending=model.priorities.find(item=>item.key === 'pending_review');
  if(highRisk && visualValue(highRisk.value) > 0){
    return {tone:'risk', title:'今日有高风险线索', detail:`${visualValue(highRisk.value)} 条高风险，优先进入任务中心复核`};
  }
  if(pending && visualValue(pending.value) > 0){
    return {tone:'review', title:'今日有待复核事项', detail:`${visualValue(pending.value)} 项待复核，建议先处理问题分布`};
  }
  if(issueTotal > 0){
    return {tone:'attention', title:'今日有异常待处理', detail:`${issueTotal} 项异常或待处理，点击图表进入任务中心`};
  }
  return {tone:'ok', title:'今日监控正常', detail:'暂无高风险、待复核或交付异常'};
}
```

- [ ] **Step 2: Replace raw count sorting for issues with severity ranking**

In `operationsOverviewViewModel()`, give priority rows stable keys and severity ranks:

```javascript
function operationsIssueSeverityRank(key){
  return {
    high_risk: 10,
    pending_review: 9,
    mail_failed: 8,
    run_failed: 7,
    run_skipped: 6,
    mail_unsent: 5,
  }[key] || 1;
}
```

Build `priorities` with keys and sort by severity first, then count:

```javascript
const priorities=[
  {key:'high_risk', label:'高风险', value: leadHigh, tone:'risk', tab:'runs', grouped:'1', target:'task_center_panel'},
  {key:'pending_review', label:'待复核', value: Math.max(reportAttention, leadReview), tone:'review', tab:'runs', grouped:'1', target:'task_center_panel'},
  {key:'mail_failed', label:'邮件失败', value: deliveryFailed, tone:'attention', tab:'runs', grouped:'1', target:'task_center_panel'},
  {key:'run_failed', label:'运行失败', value: runFailed, tone:'attention', tab:'runs', grouped:'0', target:'task_center_panel'},
  {key:'run_skipped', label:'运行跳过', value: runSkipped, tone:'review', tab:'runs', grouped:'0', target:'task_center_panel'},
  {key:'mail_unsent', label:'邮件待发', value: deliveryUnsent, tone:'review', tab:'runs', grouped:'1', target:'task_center_panel'},
].filter(item=>visualValue(item.value) > 0).sort((a,b)=>{
  const rankDiff=operationsIssueSeverityRank(b.key) - operationsIssueSeverityRank(a.key);
  return rankDiff || visualValue(b.value) - visualValue(a.value);
});
```

- [ ] **Step 3: Surface the summary in the context bar**

Have `operationsOverviewViewModel()` assign:

```javascript
const health=operationsHealthSummary({priorities});
```

and include it in the returned model. Render it in `renderOperationsContextBar()` or the current context bar path as a concise top-line signal.

- [ ] **Step 4: Run the loop checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c" -q
node --check api/webui/monitor/monitor.js
```

Expected: Phase 13B/13C pass or fail only on still-unimplemented CR-106A markers. `node --check` passes.

## Task 3: Platform Volume Versus Failure Signal

**Files:**

- Modify: `api/monitor_web/index.html`
- Test: `tests/test_monitoring_mvp.py`

- [ ] **Step 1: Add platform failure derivation from existing summaries**

Do not add backend fields. Add a frontend helper that can consume existing run/report summaries already fetched for trend or current dashboard payload:

```javascript
function operationsPlatformFailureRows(sourceRows=[]){
  const failures=new Map();
  (sourceRows||[]).forEach(item=>{
    const summary=item.summary || item || {};
    const failed=Array.isArray(summary.failed_platforms) ? summary.failed_platforms : [];
    const results=summary.platform_results || {};
    failed.forEach(platform=>{
      const key=String(platform||'').toLowerCase();
      if(!key) return;
      failures.set(key, (failures.get(key) || 0) + 1);
    });
    Object.entries(results).forEach(([platform, result])=>{
      const status=String(result?.status || '').toLowerCase();
      if(!['failed','timeout','cancelled','skipped'].includes(status)) return;
      const key=String(platform||'').toLowerCase();
      if(!key) return;
      failures.set(key, (failures.get(key) || 0) + 1);
    });
  });
  return failures;
}
```

- [ ] **Step 2: Add failure metadata to platform chart rows**

Keep volume bars as volume. Add failure count as metadata and label/cue, not as the same color semantics as volume:

```javascript
const platformFailures=operationsPlatformFailureRows(home.platform_signal_rows || []);
const platforms=Object.entries(platformCounts)
  .map(([key, value], index)=>({
    label: platformChartLabel(key),
    value: visualValue(value),
    failures: visualValue(platformFailures.get(String(key).toLowerCase()) || 0),
    ratio: 0,
    tone: platformFailures.get(String(key).toLowerCase()) ? 'attention' : 'live',
    color: platformPalette[index % platformPalette.length],
    tab: 'runs',
    grouped: '0',
    target: 'task_center_panel',
  }))
```

If `home.platform_signal_rows` is not currently available, keep the helper and wire it to the existing frontend aggregated runs/reports data in the smallest safe way; do not add backend fields.

- [ ] **Step 3: Update platform labels**

Update `operationsPlatformOption()` formatter so failure signal is visible without turning category color red:

```javascript
formatter: params => {
  const row=rows[params.dataIndex] || {};
  const failureText=row.failures ? ` / 异常${row.failures}` : '';
  return `${params.value} / ${row.ratio || 0}%${failureText}`;
},
```

- [ ] **Step 4: Run the loop checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c" -q
```

Expected: platform CR-106A markers pass, and no test requires new backend fields or sample counts.

## Task 4: Report-Level Mail Semantics And Negative Guard

**Files:**

- Modify: `api/monitor_web/index.html`
- Test: `tests/test_monitoring_mvp.py`

- [ ] **Step 1: Add explicit mail-source copy**

In the mail KPI or delivery chart legend, add concise copy such as:

```text
报告级邮件状态
```

This copy must make clear the module reflects `reports.email_status`, not complete delivery-attempt history.

- [ ] **Step 2: Keep Operations Home free of delivery-log aggregation**

Do not add references to:

```text
email_delivery_logs
list_email_delivery_logs
delivery_logs
recipients_json
effective_recipients_json
error_message
```

inside the dashboard/Operations Home rendering block.

- [ ] **Step 3: Run the loop checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c or phase_16 or phase_17b" -q
```

Expected: Operations Home CR-106A tests pass; existing email history tests still pass; no normal-user leakage appears.

## Task 5: Resource Health And Normal-User Reflow

**Files:**

- Modify: `api/monitor_web/index.html`
- Modify: `api/webui/monitor/monitor.css`
- Test: `tests/test_monitoring_mvp.py`

- [ ] **Step 1: Make admin resource labels action-oriented**

Keep resource data safe and count/status based. Examples of acceptable labels:

```text
账号待配置
代理待配置
AI 待配置
会话待登录
```

Do not expose account names, proxy URLs, SMTP values, profile paths, cookies, or raw errors.

- [ ] **Step 2: Keep normal-user resource empty**

For `model.resourceScope !== 'workspace'`, `renderOperationsResourceHealth(model)` must continue returning an empty string and disposing the resource chart:

```javascript
if(model.resourceScope !== 'workspace'){
  disposeOperationsChart('resource');
  return '';
}
```

- [ ] **Step 3: Preserve CSS reflow**

Ensure the CR-105 user-overview rule still hides resource health and fills the lower grid:

```css
body #dashboard.active .operations-home.is-user-overview #operations_home_resource {
  display: none;
}
```

Keep the lower modules aligned. Do not leave a third-column blank slot for normal users.

- [ ] **Step 4: Run the loop checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13c or phase_21" -q
```

Expected: normal-user role visibility and responsive assertions pass. If unrelated Phase 21 tests fail, narrow to the Operations Home tests and document the reason before continuing.

## Task 6: Mobile Density And Stable Layout

**Files:**

- Modify: `api/webui/monitor/monitor.css`
- Test: `tests/test_monitoring_mvp.py`

- [ ] **Step 1: Adjust only Operations Home mobile rules**

In the CR-105 Operations Home CSS block, compact mobile KPI card height, gaps, and chart surfaces enough that `监控走势` and `问题分布` appear early at `390x844`. Do not change global shell, navigation, Task Center, Run Detail, drawer, modal, select, or date CSS.

- [ ] **Step 2: Keep stable chart dimensions**

Preserve explicit chart surface dimensions through responsive constraints:

```css
body #dashboard.active .operations-chart-surface {
  min-height: 120px;
}
```

Use existing project spacing tokens and avoid viewport-scaled font sizes.

- [ ] **Step 3: Run static checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c" -q
```

Expected: CSS selectors and responsive role assertions pass.

## Task 7: Browser Acceptance Loop

**Files:**

- Read/verify rendered `/monitor`
- No code edits unless acceptance fails

- [ ] **Step 1: Start or reuse the local monitor service**

Use the repo's existing local server entrypoint. If a port is occupied, use another port and record it in `TEST_RESULTS.md`.

- [ ] **Step 2: Verify administrator view**

Check:

```text
1440x900
1024x768
390x844
```

Administrator acceptance:

- First screen reads as a chart cockpit, not a state-card collage.
- Top status answers normal/abnormal/next action in about 10 seconds.
- `问题分布` surfaces high-risk/pending/mail/run issues in action-first order.
- `平台分布` distinguishes volume from failure signal.
- `邮件` is labeled as report-level delivery state.
- `资源健康` is visible, safe, action-oriented, and aligned.
- No overlap, horizontal scroll, one-character Chinese columns, or layout jump.

- [ ] **Step 3: Verify normal-user view**

Check the same viewports.

Normal-user acceptance:

- `资源健康` is not rendered.
- No account/proxy/AI/SMTP/session details appear.
- Lower modules reflow without blank slot or uneven third-column gap.
- Existing Task Center, Run Detail, overlay, select/date, route, and refresh behavior still works.

- [ ] **Step 4: Fix and rerun within this loop**

If any browser check fails, fix only the relevant Operations Home HTML/CSS/JS, rerun targeted tests, and repeat the browser viewport that failed before moving forward.

## Task 8: Full Verification And Documentation Sync

**Files:**

- Modify: `docs/TASKS.md`
- Modify: `docs/CURRENT_STATE.md`
- Modify: `docs/TEST_RESULTS.md`
- Modify: `docs/TRACEABILITY.md`

- [ ] **Step 1: Run required automatic checks**

Run:

```powershell
uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"
node --check api/webui/monitor/monitor.js
uv run python scripts/check_docs.py
git diff --check
```

Also complete inline monitor script parse using the existing project test or script path. If no separate script exists, document that the existing pytest parse/static checks covered the inline script and do not invent an unrelated tool.

- [ ] **Step 2: Update docs after verification**

Update:

- `docs/TASKS.md`: mark CR-106A tasks complete only after code and browser checks pass.
- `docs/CURRENT_STATE.md`: state CR-106A implemented/verified and preserve CR-106B as `Needs Confirmation`.
- `docs/TRACEABILITY.md`: move CR-106A from Accepted to Verified with exact files and checks.
- `docs/TEST_RESULTS.md`: add a top entry that states what this proves and what it does not prove.

- [ ] **Step 3: Run docs checks again**

Run:

```powershell
uv run python scripts/check_docs.py
git diff --check
```

Expected: docs consistency passes; diff check passes or reports only known Windows LF/CRLF warnings.

## Completion Definition

CR-106A is complete only when all are true:

- Code, tests, and docs agree.
- `uv run python -m pytest tests/test_monitoring_mvp.py -k "phase_13b or phase_13c"` passes.
- `node --check api/webui/monitor/monitor.js` passes.
- Inline monitor script parse is completed through the existing project path.
- `uv run python scripts/check_docs.py` passes.
- `git diff --check` passes or only reports known Windows LF/CRLF warnings.
- Administrator and normal-user browser acceptance passes at `1440x900`, `1024x768`, and `390x844`.
- CR-105A remains the current ECharts baseline and historical CR-097 through CR-104 constraints are not reopened.
- CR-106B remains `Needs Confirmation` and no `email_delivery_logs` Operations Home aggregation is implemented.
- `docs/TEST_RESULTS.md` records what was proved and what was not proved.

## Stop Conditions

Stop and report instead of expanding scope if:

- CR-106A cannot meet the goal without backend schema fields or new persisted metrics.
- Correct mail health requires Operations Home `email_delivery_logs` aggregation.
- The implementation needs permission, route, Task Center, Run Detail, drawer, modal, select/date, crawler, AI, or email execution behavior changes.
- Local ECharts vendor is missing or cannot be served from `/static/monitor/vendor/echarts.min.js`.
- Browser checks reveal a same-file conflict that makes existing user changes indistinguishable from this task's edits.
- Required checks fail for reasons outside Operations Home and cannot be safely isolated.
