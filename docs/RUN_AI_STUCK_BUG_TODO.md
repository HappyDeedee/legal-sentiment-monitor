# Run AI Evaluation Stuck Bug TODO

Date: 2026-06-16

Type: Regression fix and run-center progress reliability follow-up

Status: Planning; do not implement from this file alone until the connected
CR, tasks, traceability, and test-plan entries agree.

Related scope:

- CR-035 Run Lifecycle Finalization And AI Stuck Recovery Regression Fix
- Phase 7.1 Runs, Reports, And AI Stuck Recovery Follow-up
- PR-RUNREPORT-001 Runs, Reports, And AI Fallback
- CR-031 Run Center Realtime Progress Visibility
- Phase 19B Run Center Progress Data Layer
- Phase 19C AI Evaluation Progress Updates
- Phase 19D Run Center Frontend Progress Display And Polling

## Summary

Live task `9297` exposed a run lifecycle bug: collection completed and AI
evaluation partially progressed, but the run remained `running` after the
background task was no longer active. Operators could not tell whether the
system was still evaluating, stuck, or waiting for timeout recovery.

The fix should not be a one-off database correction. It should make run
lifecycle finalization, AI evaluation fallback, stale-run recovery, and Run
Center progress display reliable as one connected path.

## Scope Classification

This incident spans both a regression fix and a product optimization. Keep the
two parts separate during implementation and review.

### Regression Fix - CR-035 / Phase 7.1

These items restore the already accepted Phase 7 behavior that AI failure must
not block report generation and runs must not stay indefinitely `running` after
execution disappears:

- P0-REG-1: persist `crawl_runs.job_id` reliably and add legacy-compatible
  reads for rows where only `summary.job_id` exists.
- P0-REG-2: add one idempotent finalization path for success, failure,
  timeout, cancellation, interruption, and partial AI/report results.
- P0-REG-3: make per-item AI errors, invalid JSON, and timeouts degrade to
  `pending_review` and continue when the run deadline allows.
- P0-REG-4: recover stale `running` rows before the wall-clock deadline when
  no active task/lock/heartbeat evidence remains.
- P0-REG-5: generate reports from partial AI/manual-review state when
  collected contents exist.
- P1-REG-1: provide an explicit, authorized remediation path for current run
  `8317` after code-level safety is verified.

### Phase 19B - Run Center Progress Data Layer

These are CR-031 enhancements, not the minimum regression fix:

- provisional collection progress from safe MediaCrawler output files or
  equivalent progress signals;
- safe handling for missing, in-flight, partially written, or malformed output;
- final ingest-count accuracy without treating provisional counts as final.

### Phase 19C - AI Evaluation Progress Updates

These are CR-031 enhancements that build on the regression fix:

- incremental AI evaluated/total progress writes;
- batch or time-interval updates for suspected negative, high-risk, and
  manual-review counts;
- exact final AI counts after the evaluation loop finishes or is finalized.

### Phase 19D - Run Center Frontend Progress Display

These are CR-031 frontend enhancements:

- continuous polling while visible runs remain active;
- phase labels for collection, ingestion, AI evaluation, report generation,
  email delivery, terminal failure, timeout, and interruption;
- clear provisional-vs-final count display on desktop, tablet, and mobile.

### Explicit Non-Scope

CR-034 / Phase 20 AI evaluation traceability is not part of this bug fix. Do
not add raw prompt, request, or response trace views while fixing this stuck
run bug.

## Completed Phase Follow-up Rule

Phase 7 remains historically complete because it was verified against the
available local tests at the time. This incident is a newly observed regression
or coverage gap in the same responsibility area.

Do not rewrite old completion records as incomplete. Instead:

- record a new Regression Fix CR;
- create a follow-up task block under the original responsibility area
  (`Phase 7.1` here);
- link it back to the original requirement in `TRACEABILITY.md`;
- add new tests that would have caught the incident;
- record the new result in `TEST_RESULTS.md` when implementation is complete.

## Incident Evidence

Observed task:

- `monitor_jobs.id`: `9297`
- law firm: `北京海安律所`
- account: `1611`
- latest effective run: `8317`
- platform: Douyin (`dy`)

Observed run `8317`:

- `crawl_runs.status`: `running`
- `crawl_runs.finished_at`: `NULL`
- `crawl_runs.job_id`: `NULL`
- `crawl_runs.summary.job_id`: `9297`
- started: `2026-06-16 14:33:26` Beijing time
- deadline: `2026-06-16 20:33:26` Beijing time
- timeout setting copied into run: `21600` seconds

Collection result in run summary:

- raw contents: `607`
- filtered contents: `461`
- new contents: `271`
- failed platforms: `[]`
- `platform_results.dy.status`: `success`

Crawler log evidence:

- Douyin crawler finished at `2026-06-16 15:14:39`
- browser connection disconnected
- browser process closed

AI evaluation evidence:

- raw contents for run `8317`: `271`
- AI evaluations for run `8317`: `250`
- unevaluated contents: `21`
- latest AI evaluation timestamp: `2026-06-16 15:26:47`
- AI status counts: `ok=247`, `pending_review=3`
- no report exists for run `8317`

Runtime/lock evidence:

- no `monitor_data/locks/job_9297.lock`
- `social_accounts.id=1611` is not locked
- no proxy/resource lock for run `8317`
- backend scheduler ticks continued after the AI evaluation stopped

Evidence gaps to collect before or during implementation:

- active backend process version, start time, and whether it was restarted
  during the incident;
- backend exception logs around the item after the 250th AI evaluation;
- system resource signals at the time, especially memory, CPU, and disk;
- whether another run shared the same account/proxy resources.

Conclusion:

The crawler and part of the AI evaluation finished, but the active run task was
not still alive. The persisted run remained `running` because finalization did
not complete or was not reached.

## Expected Behavior

- A platform collection success should not be hidden behind a stale `running`
  state.
- AI provider errors, invalid JSON, or per-item evaluation failures should turn
  the affected content into `pending_review`, not block report generation.
- If the run task exits unexpectedly, the persisted run should be moved to a
  terminal state or a clear interrupted state.
- Run Center should show the current phase and progress:
  `collecting`, `ingesting`, `ai_evaluating`, `report_generating`,
  `email_sending`, `success`, `partial_failed`, `timeout`, `cancelled`, or
  `interrupted`.
- Operators should be able to see `250/271 AI evaluated` instead of only
  seeing `running`.

## Root Cause Analysis

### 1. AI Evaluation Progress Is Not Persisted Incrementally

The current run summary is updated after platform ingestion and again after the
whole AI evaluation loop returns. During a long AI batch, the database does not
show evaluated count, total candidate count, or the current evaluation phase.

Impact:

- Operators cannot distinguish active AI work from a stuck run.
- If AI evaluation exits mid-loop, the summary keeps the last platform counts
  and never receives AI progress.

### 2. Per-Run Job Identity Is Inconsistent

The live database row for `crawl_runs.id=8317` has `job_id=NULL` while
`summary.job_id=9297`.

Impact:

- APIs that check `crawl_runs.job_id` miss this run.
- stop/delete/running checks can incorrectly conclude the task is not running.
- historical rows become hard to filter by task.

Required investigation:

- Verify whether the currently running service process is using stale code or
  an older schema/write path.
- Add a compatibility read path for existing rows where `summary.job_id` is
  present but the column is null.
- Consider a safe backfill for resolvable historical rows.

### 3. Background Task Failures Are Not Observable Enough

The scheduler wrapper catches exceptions so background tasks do not leak
unhandled exceptions into the event loop. However, the observed logs did not
contain a clear traceback for run `8317`.

Impact:

- A run can disappear from active execution while the persisted status remains
  `running`.
- Operators and agents cannot identify the exact failing call from logs.

### 4. Stale-Run Recovery Waits For Deadline

Run `8317` copied `crawler_timeout_seconds=21600`, so automatic deadline
recovery would wait until `20:33:26` before marking timeout.

Impact:

- A run whose background task is already gone can remain `running` for hours.
- The UI looks alive even when no lock or active task exists.

### 5. Report Generation Depends On Full AI Loop Completion

No report was generated for run `8317`, even though 271 contents were collected
and 250 evaluations existed.

Impact:

- Useful partial results remain hidden from Report Center.
- AI evaluation interruption blocks the user-facing report path, contrary to
  the V1 rule that AI failure should fall back to manual review.

## Fix Principles

- Never leave a run in `running` after its background task has exited.
- AI failure degrades to manual review; it does not block report generation.
- Persist progress at phase boundaries and during long loops.
- Keep final counts exact; mark provisional counts as provisional.
- Preserve owner/workspace scope and customer-safe wording.
- Do not expose raw API keys, cookies, proxy credentials, profile paths,
  provider endpoints, local paths, commands, or platform secrets.
- Progress messages and exception logs must pass through the existing sensitive
  text redaction path before storage or display.
- Do not modify MediaCrawler platform implementations unless progress signals
  are proven unavailable.

## Backend TODO

### P0-REG-1 - Data Integrity And Compatibility

- [ ] Verify `create_run()` always writes `crawl_runs.job_id` in the active
      runtime, not only in the source file.
- [ ] Add tests that new runs persist `job_id` in the column.
- [ ] Add read compatibility for legacy rows where `crawl_runs.job_id` is null
      but `summary.job_id` is resolvable.
- [ ] Update `has_running_run_for_job()` and `cancel_running_runs_for_job()` to
      account for compatible legacy rows.
- [ ] Add a safe backfill helper or migration for rows whose `summary.job_id`
      references an existing `monitor_jobs.id`.
- [ ] Backfill must be dry-run capable and skip rows where `summary.job_id`
      does not resolve to an existing task.
- [ ] Ensure stopping a run by `run_id` works even when `job_id` is missing.

Done when:

- new runs have a non-null `crawl_runs.job_id`;
- legacy rows remain readable and stoppable;
- dry-run backfill reports candidate rows without changing data;
- unresolved historical rows are left untouched with clear logs.

### P0-REG-2 - Finalization Safety

- [ ] Add a single idempotent finalization helper for terminal status writes.
- [ ] Ensure normal success, partial failure, timeout, cancellation,
      interruption, and unexpected exception paths all call the same helper.
- [ ] Finalization must not overwrite an existing terminal status on repeated
      or concurrent calls.
- [ ] Add database-level transition protection: allow active states to move to
      terminal states, but do not allow stale writers to move terminal rows back
      to `running` or another weaker state.
- [ ] Use optimistic transition conditions, a version field, or equivalent
      compare-and-update logic to prevent concurrent status writes from
      overwriting each other.
- [ ] Ensure resource locks are released once after a finalization attempt, and
      repeated releases remain harmless.
- [ ] Ensure `_run_and_release()` logs swallowed background exceptions with
      `run_id`, compatible `job_id`, phase, and redacted error.
- [ ] Include a redacted phase/progress snapshot in exception logs.
- [ ] Document service-restart behavior: persisted `running` rows in active
      phases with no live task evidence should be recovered as `interrupted`
      through startup or scheduler recovery.

Done when:

- every exit path ends in one terminal state or a clear no-op because the run is
  already terminal;
- duplicate finalization calls do not corrupt status, summary, report links, or
  locks;
- logs help diagnose failure without exposing secrets or local runtime paths.

### P0-REG-3 - AI Evaluation Resilience

- [ ] Record AI total candidates before the AI loop starts.
- [ ] Add an outer per-item AI timeout that is independent of provider client
      behavior and bounded by the remaining run deadline.
- [ ] If one item times out, save it as `pending_review` and continue.
- [ ] If one item returns invalid JSON, save it as `pending_review` and
      continue.
- [ ] If one item raises an unexpected exception, save it as `pending_review`
      and continue.
- [ ] If the AI loop itself is interrupted during active finalization, create
      `pending_review` fallback rows for not-yet-evaluated candidate IDs before
      report generation when safe to do so.
- [ ] Keep existing secret redaction for provider errors and progress messages.

Done when:

- a single bad AI item cannot stop the entire run;
- all collected candidates either receive an evaluation row or are explicitly
  left limited by a documented terminal/interrupted state;
- report generation can proceed with manual-review fallback rows.

### P0-REG-4 - Stale Run Recovery Before Deadline

- [ ] Extend recovery beyond deadline-only timeout.
- [ ] Detect stale running runs where:
      - no active job lock exists;
      - no account/resource lock exists;
      - the run has no recent `progress_updated_at`;
      - and the run is still `running`.
- [ ] Mark such runs as `interrupted` with a customer-safe message.
- [ ] Do not auto-create missing `ai_evaluations` during stale recovery unless
      an explicit repair workflow is invoked.
- [ ] Add tests for stale running rows before `deadline_at`.

Done when:

- a disappeared background task is recovered before the full wall-clock
  deadline;
- existing deadline timeout behavior still works;
- stale recovery is owner/workspace safe and idempotent.

### P0-REG-5 - Report Generation With Partial AI

- [ ] Generate reports when AI evaluation partially fails but collected content
      exists.
- [ ] Include collected contents that were converted to `pending_review`.
- [ ] Ensure report summary distinguishes suspected negative leads from manual
      review items.
- [ ] Preserve email-failure-tolerant report generation.
- [ ] If report generation fails, finalize the run with a redacted terminal
      failure state instead of leaving it `running`.

Done when:

- partial AI state produces a report when enough collected data exists;
- report and lead reads remain scoped to the owning user/workspace;
- report failures produce terminal, customer-safe run state.

### Phase 19B/P1 - Run Phase And Heartbeat

- [ ] Add a run progress helper that writes phase fields into
      `crawl_runs.summary`, for example:
      - `phase`
      - `phase_started_at`
      - `progress_updated_at`
      - `progress_message`
      - `collection_progress`
      - `ai_progress`
      - `report_progress`
      - `email_progress`
- [ ] Update phase to `collecting` before platform tasks start.
- [ ] Update phase to `ingesting` before final output ingestion.
- [ ] Update phase to `ai_evaluating` before AI evaluation begins.
- [ ] Update phase to `report_generating` before report creation.
- [ ] Update phase to `email_sending` before email delivery.
- [ ] Update terminal phase together with final run status.
- [ ] Progress updates must be monotonic where possible; stale writers must not
      reduce evaluated counts or replace a newer `progress_updated_at`.

### Phase 19C/P1 - AI Evaluation Progress Updates

- [ ] Update AI evaluated count in batches or time intervals.
- [ ] Keep negative, high-risk, and manual-review counts updated during the
      loop without waiting for all candidates to finish.
- [ ] Ensure final AI summary counts remain exact.

## Frontend TODO

### Phase 19D/P1 - Polling And Progress Display

- [ ] Keep Run Center polling active while visible runs remain active.
- [ ] Recommended polling interval: 5 seconds while a visible run is active;
      allow a later runtime or frontend setting only if needed.
- [ ] Stop polling when all visible runs are terminal:
      `success`, `failed`, `partial_failed`, `timeout`, `cancelled`, or
      `interrupted`.
- [ ] Render active phase labels:
      - collecting
      - ingesting
      - AI evaluating
      - report generating
      - email sending
      - interrupted
- [ ] Display provisional collection progress with a non-color-only indicator,
      for example `250 (provisional)` or `collecting 250`.
- [ ] Display final counts without the provisional indicator, for example
      `collected 271`.
- [ ] Show AI progress as `250 / 271` while phase is `ai_evaluating`, and
      show a final evaluated count when complete.
- [ ] Show partial/interrupted wording that explains collected data may exist.
- [ ] Keep stop/log/report actions visible and unclipped on desktop, tablet,
      and mobile.
- [ ] If a run is stale/interrupted, show operator actions such as view logs,
      view collected report/partial result when available, or start a confirmed
      repair workflow.
- [ ] Do not expose raw file paths, commands, account profile paths, cookies,
      provider endpoints, or API/proxy credentials.

Done when:

- active runs visibly progress without forcing operators to open logs;
- polling does not continue after terminal visible runs;
- provisional counts cannot be confused with final ingested counts;
- mobile and tablet views keep status and actions readable.

## Test TODO

### Unit Tests

- [ ] `create_run()` writes `crawl_runs.job_id`.
- [ ] running-run lookup finds rows by real `job_id`.
- [ ] legacy running-run lookup finds rows by `summary.job_id` when the column
      is null.
- [ ] stopping by `run_id` works when `job_id` is null.
- [ ] safe backfill dry-run lists only resolvable historical rows.
- [ ] AI invalid JSON saves `pending_review` and continues.
- [ ] AI timeout saves `pending_review` and continues.
- [ ] AI unexpected per-item exception saves `pending_review` and continues.
- [ ] AI progress updates evaluated count and total count incrementally.
- [ ] final AI summary counts remain exact.
- [ ] finalization repeated for the same `run_id` is idempotent.
- [ ] concurrent finalization attempts write only one terminal state.
- [ ] progress updates do not overwrite newer progress with older snapshots.
- [ ] redaction covers progress messages and finalization exception logs.

### Integration Tests

- [ ] Simulate collection success with 271 content IDs and AI interruption at
      item 251; the run must not remain `running`.
- [ ] Simulate AI provider failure for all items; the run still generates a
      report with manual-review leads.
- [ ] Simulate report-generation failure after AI progress; the run becomes a
      terminal failure state with redacted error.
- [ ] Simulate stale running run before deadline with no locks and old
      heartbeat; recovery marks it `interrupted`.
- [ ] Simulate deadline timeout; existing timeout behavior still works.
- [ ] Simulate service restart during AI evaluation; startup/scheduler recovery
      marks the run `interrupted` when no live task evidence exists.
- [ ] Simulate two concurrent finalization calls; verify one terminal status
      and safe one-time lock release behavior.
- [ ] Simulate two active runs updating progress; verify summaries remain
      scoped to the correct run.
- [ ] Verify administrator can see workspace-wide progress while normal users
      only see their own run progress.

### Frontend Tests

- [ ] Running row shows collection phase.
- [ ] Running row shows AI progress `evaluated / total`.
- [ ] Running row shows report/email phases.
- [ ] Interrupted row is not displayed as ordinary running.
- [ ] Provisional collection count has a visible non-color-only label.
- [ ] Final counts do not show the provisional label.
- [ ] Polling continues while visible runs are active and stops after all
      visible runs are terminal.
- [ ] Stop/log/report controls remain visible in desktop, tablet, and mobile
      layouts.
- [ ] Normal users see only scoped runs and safe wording.

### Documentation Tests

- [ ] `CR-035` exists in `CHANGE_REQUESTS.md` and is linked in
      `TRACEABILITY.md`.
- [ ] `TASKS.md` has Phase 7.1 follow-up tasks and keeps Phase 19B-19D as
      progress-display enhancements.
- [ ] `TEST_PLAN.md` includes Phase 7.1 regression tests and Phase 19 progress
      tests.
- [ ] `CURRENT_STATE.md` says completed phases remain historical snapshots and
      newly discovered bugs use follow-up regression-fix phases.
- [ ] `uv run python scripts/check_docs.py` passes.

## Current Run 9297 Remediation TODO

Do not perform these automatically without explicit operator confirmation.

Safe sequence:

1. Back up the active database and relevant run/report artifacts.
2. Implement and verify the CR-035 code path on a non-destructive test run.
3. Restart the live service so the active process uses the repaired runtime
   code.
4. Verify new runs no longer get stuck after partial AI evaluation.
5. Only then choose and execute a historical remediation for run `8317`.

Options:

- [ ] Preserve history: mark run `8317` as `interrupted`, keeping existing
      collected content and 250 AI results.
- [ ] Repair into partial report: create pending-review evaluations for the
      remaining 21 contents, generate a report for run `8317`, and finalize the
      run.

Rollback requirements:

- [ ] Keep a database backup from before remediation.
- [ ] Record the exact SQL/API repair commands before execution.
- [ ] If repair creates an incorrect report or status, restore from backup or
      apply the documented inverse update after confirming no newer data was
      written.

## Non-Goals

- Do not change MediaCrawler platform crawler implementations for this bug
  unless no safe progress signal is available outside them.
- Do not introduce high-concurrency worker orchestration.
- Do not implement captcha/SMS bypass.
- Do not expose raw AI request/response traces in customer-facing UI as part of
  this bug fix. That belongs to CR-034/Phase 20 and still needs confirmation.
- Do not expose secrets, cookies, profile paths, proxy credentials, provider
  endpoints, local paths, commands, or local runtime data.

## Recommended Decisions

1. `interrupted` should become a first-class `crawl_runs.status` value.
   Rationale: it is semantically different from `partial_failed`, which means
   the run completed with errors. `interrupted` means the execution disappeared
   or could not safely continue.
2. Unresolved AI candidates should auto-convert to `pending_review` only during
   active finalization, where the code still has a known candidate list and can
   safely generate a partial report. Stale recovery should mark the run
   `interrupted` and avoid changing AI rows unless an explicit repair workflow
   is invoked.
3. Stale heartbeat grace period should default to 10 minutes for V1. This is
   long enough to tolerate slow provider calls and short enough to avoid
   waiting for a multi-hour crawl deadline after the background task is gone.
4. Historical `job_id` backfill should be opt-in, dry-run first, and limited to
   rows whose `summary.job_id` resolves to an existing `monitor_jobs.id`.
5. AI per-item timeout should use a new setting such as
   `ai_item_timeout_seconds`, defaulting to 120 seconds, and it must also be
   capped by the remaining run deadline.
6. `progress_message`, finalization errors, and recovery logs must always be
   passed through the existing redaction helper before storage or display.

## Recommended Implementation Order

1. Add `CR-035` documentation, Phase 7.1 tasks, traceability, test plan, and
   decision notes.
2. Fix `job_id` integrity and legacy-compatible running-run lookup.
3. Add finalization idempotency, background exception logging, and safe lock
   release.
4. Add AI per-item fallback and active-finalization pending-review completion.
5. Add stale heartbeat recovery before deadline.
6. Generate reports from partial AI/manual-review state.
7. Add Phase 19 progress snapshots and frontend polling/display.
8. Add unit, integration, documentation, and responsive frontend tests.
9. Handle historical run `8317` only after the code path is safe and explicitly
   authorized.

## Comprehensive Review Prompt

Use this prompt to ask another agent to review the TODO and connected project
documents before implementation:

```text
请你以只读方式全面审阅 `docs/RUN_AI_STUCK_BUG_TODO.md` 以及它连接到的
`AGENTS.md`, `docs/GOAL.md`, `docs/CURRENT_STATE.md`, `docs/TASKS.md`,
`docs/DECISIONS.md`, `docs/CHANGE_REQUESTS.md`, `docs/TRACEABILITY.md`,
`docs/TEST_PLAN.md`, `docs/PRODUCT_REQUIREMENTS.md`,
`docs/UI_UX_GUIDELINES.md`, `docs/DATA_MODEL.md`,
`docs/SCHEMA_MIGRATION.md`, `docs/SYSTEM_SETTINGS.md`, 以及相关代码
`api/monitoring/runner.py`, `api/monitoring/database.py`,
`api/monitoring/ai.py`, `api/monitoring/scheduler.py`,
`api/monitoring/reporting.py`, `api/routers/monitor.py`,
`api/monitor_web/index.html`, `api/webui/monitor/monitor.css`,
`api/webui/monitor/monitor.js`, `tests/test_monitoring_mvp.py`。

目标：判断这份待办是否足以指导实现，是否正确区分了已完成 Phase 的
follow-up regression fix、CR-031/Phase 19 progress enhancement、以及
CR-034/Phase 20 traceability non-scope。

请从以下维度逐项评分、说明证据、指出必须修改项：

1. 事实证据完整性：任务/运行/日志/数据库/锁/报告/AI评估证据是否足够，
   是否区分事实、推断和仍需补采的证据。
2. 根因分析：是否覆盖 job_id 缺失、AI循环中断、finalization未落库、
   stale recovery等根因链，是否有误判或遗漏。
3. Phase归属：是否正确把 P0 数据完整性、finalization、stale recovery
   归入 CR-035/Phase 7.1；是否把实时进度展示保留在 CR-031/Phase 19B-19D；
   是否明确排除 CR-034/Phase 20。
4. 已完成 Phase 处理规则：是否保留历史完成状态，并通过 follow-up
   regression fix 接新问题；是否会误导后续 agent 重开旧 Phase 或篡改历史。
5. 后端设计：job_id兼容、幂等finalization、状态迁移保护、锁释放、AI
   per-item timeout、pending_review fallback、partial report、stale recovery、
   服务重启恢复是否可落地。
6. 数据模型和迁移：是否需要新增字段、summary字段是否足够、interrupted
   status是否影响现有查询、backfill是否安全、旧数据兼容是否清楚。
7. 并发与幂等：active run、scheduler recovery、startup recovery、重复
   finalization、并发progress update之间是否有竞态风险和测试覆盖。
8. 前端体验：polling频率、停止条件、phase label、provisional/final标识、
   interrupted操作、桌面/平板/手机布局是否清楚且不误导用户。
9. 权限与作用域：admin/normal user在run/progress/report读取上的边界是否
   延续现有owner/workspace scope。
10. 安全与隐私：progress_message、日志、错误、前端字段是否明确脱敏；
    是否避免暴露API key、cookie、profile path、proxy credential、provider
    endpoint、本地路径和命令。
11. 运维与历史修复：9297/8317的处理是否需要授权、备份、回滚、dry-run；
    操作顺序是否安全。
12. 测试覆盖：单元、集成、前端、权限、并发、服务重启、文档一致性测试是否
    能防止复发。
13. 文档一致性：CHANGE_REQUESTS/TASKS/TRACEABILITY/TEST_PLAN/CURRENT_STATE/
    DECISIONS是否互相一致，`uv run python scripts/check_docs.py`是否应该通过。
14. 产品边界：是否符合V1单服务器低并发、AI失败不阻塞报告、不中断MediaCrawler
    平台实现、不引入高并发worker、不做验证码/SMS绕过的边界。
15. 实施顺序和验收：P0/P1优先级、Done标准、回滚边界、最小安全闭环是否清晰。

输出格式：
- A. 总体评分，10分制，并说明扣分原因。
- B. 是否建议进入实现：可以 / 需要先改文档 / 不建议。
- C. 分维度评分表，每项给分、优点、缺口、是否必须修改。
- D. P0/P1/P2问题清单，必须给文件/章节/建议改法。
- E. 最小可执行修复闭环，按顺序列出。
- F. 仍需用户确认的问题。
- G. 你会如何调整Phase/CR归属。

注意：只读审阅，不要修改代码或文档。
```
