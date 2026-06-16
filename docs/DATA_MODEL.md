# Data Model

This document describes the target data model for V1. It is a planning document
and may require migration from the current schema.

## Implementation Status

This is a target planning document. Phase 0.5 schema foundation has been
implemented and verified in the current codebase.

Phase 0.5 added:

- `workspaces`;
- `users`;
- `user_sessions`;
- `system_settings`;
- `audit_logs`;
- `workspace_id`, `created_by`, and `updated_by` fields on priority business
  tables;
- `profile_key` on account/login-session tables;
- run-level timeout fields on `crawl_runs`;
- account/profile lock fields on `social_accounts`;
- `resource_locks` for proxy concurrency.

Current code should still be checked before implementation work begins, but the
Phase 0.5 foundation is now an active schema feature in this worktree.

Phase 10-18 console optimization planning has been accepted. Phase 14, Phase
16, and Phase 18A have implemented and verified these data-model fields:

- run visibility and run type fields on `crawl_runs`;
- `crawl_runs.archived_at`;
- `crawl_runs.archived_by`;
- `email_delivery_logs` for email delivery history and automatic-send
  idempotency foundation;
- `reports.job_snapshot_json` for deleted or missing task report grouping.

Remaining planned additions include Phase 18B frontend grouping behavior, not a
new schema field.

## Scope

V1 should support:

- users and roles;
- workspace-ready business data;
- administrator-managed platform accounts and proxies;
- runtime settings;
- monitoring tasks;
- crawl runs;
- raw content;
- AI evaluations;
- reports.
- Phase 10-18 console governance for run visibility, report grouping, and
  email delivery history.

## Workspace Strategy

Confirmed V1 strategy:

- create one default workspace;
- add `workspace_id` to business tables now;
- do not build public SaaS onboarding in V1.

## Core Tables

### workspaces

```text
id
name
status
created_at
updated_at
```

### users

```text
id
workspace_id
email
display_name
password_hash
role
status
last_login_at
created_at
updated_at
```

Confirmed authentication direction:

- use email/password login with session-based authentication for V1;
- use secure HTTP-only cookie for the browser session.
- store password hashes using bcrypt or argon2, never plaintext passwords.

### user_sessions

Target fields:

```text
id
user_id
session_token_hash
status
created_at
expires_at
last_active_at
user_agent
ip_address
```

Only the session token hash should be stored in the database.

### monitor_jobs

Existing job table should add:

```text
workspace_id
created_by
updated_by
```

Normal-user jobs should not require direct account/proxy/AI/template selection.

### social_accounts

Target fields:

```text
id
workspace_id
name
platform
login_type
status
profile_key
profile_path_legacy
proxy_id
cookies_encrypted
notes
last_login_at
last_checked_at
last_error
locked_by_run_id
locked_at
lock_expires_at
created_by
updated_by
created_at
updated_at
```

`profile_path_legacy` is optional during transition only. The confirmed
direction is to use new `profile_key` profiles and require old low-volume
accounts to re-login instead of preserving long-term legacy path compatibility.
The inline lock fields protect both the account and its `profile_key`.

### proxy_profiles

Target fields:

```text
id
workspace_id
name
provider
proxy_url_encrypted
status
max_concurrency
notes
last_checked_at
last_error
created_by
updated_by
created_at
updated_at
```

### login_sessions

Target fields:

```text
id
workspace_id
account_id
platform
status
current_step
qr_image
message
profile_key
created_at
updated_at
expires_at
```

### system_settings

See `SYSTEM_SETTINGS.md`.

### resource_locks

Proxy concurrency locks:

```text
id
workspace_id
resource_type
resource_id
run_id
locked_at
expires_at
```

V1 uses `resource_type = "proxy"` for proxy concurrency. The table can be
extended later for other shared resources. Use a unique constraint on
`resource_type + resource_id + run_id` and indexes for active lock lookup and
expiry cleanup.

### audit_logs

Minimal MVP audit fields:

```text
id
workspace_id
user_id
action_type
resource_type
resource_id
details_json
ip_address
created_at
```

Audit logs are required for security-sensitive administrator actions in MVP.

### crawl_runs

Existing run table should add:

```text
workspace_id
created_by
account_id
proxy_id
timeout_seconds
deadline_at
timeout_reason
visibility
run_type
archived_at
archived_by
```

Run status should include `timeout` for runs stopped by the run-level wall-clock
deadline. Timeout runs may still have partial results. CR-035 confirms
`interrupted` as a first-class terminal status for runs whose execution path
stopped or disappeared before normal finalization could complete.

CR-035 confirmed:

- add `interrupted` as a first-class terminal run status for cases where the
  background task is no longer active before normal success/failure/timeout
  finalization can complete;
- keep `partial_failed` for runs that completed with known partial failures;
- active finalization may create `pending_review` rows for known unresolved AI
  candidates when safe, while historical interrupted runs must not rewrite AI
  rows without an explicit repair workflow;
- run summaries should include AI progress counts for total candidates,
  successful evaluations, failed/fallback evaluations, pending-review items,
  and unresolved items where available;
- preventing future `crawl_runs.job_id` gaps is the primary fix; historical
  backfill is compatibility fallback only.
- store run phase, heartbeat, and progress snapshots in `crawl_runs.summary`
  unless a later accepted migration adds dedicated columns;
- read legacy rows compatibly when `crawl_runs.job_id` is null but
  `summary.job_id` resolves to an existing `monitor_jobs.id`;
- allow a dry-run-first backfill from `summary.job_id` into `crawl_runs.job_id`
  only for resolvable historical rows;
- represent lifecycle step result, retry state, and interruption cause in a
  customer-safe way for frontend display;
- do not use snapshot or summary fields to bypass workspace or owner scope.

Phase 10-18 run-center governance fields:

```text
visibility TEXT DEFAULT "visible"
run_type TEXT DEFAULT "scheduled"
archived_at TEXT NULL
archived_by INTEGER NULL
```

`visibility` values:

- `visible`: default operational record;
- `archived`: hidden from the default list but available through administrator
  filters.

`run_type` values:

- `scheduled`: scheduler-triggered run;
- `manual`: user-triggered immediate run;
- `test`: test or diagnostic run that may be hidden by default when noise
  filtering is enabled.

### raw_contents

Content identity:

```text
workspace_id
platform
content_id
```

Unique constraint:

```text
workspace_id + platform + content_id
```

### ai_evaluation_traces

Status: Accepted for CR-034 / Phase 20, not implemented yet.

Purpose:

Persist exact AI evaluation trace snapshots for new evaluations so operators
can inspect the input/output used for a specific run and content item without
reconstructing historical requests from mutable rules or current content.

Accepted fields:

```text
id
workspace_id
run_id
raw_content_id
ai_evaluation_id
attempt_index
status
provider
model
prompt_snapshot
input_payload_json
request_snapshot_json
response_snapshot
parsed_result_json
error_message
duration_ms
started_at
finished_at
created_at
```

Confirmed rules:

- trace retention must be controlled by the administrator runtime setting
  `ai_trace_retention_days`, defaulting to 30 days. Phase 20 must not hard-code
  the retention window in the trace persistence layer;
- normal-user trace APIs must return only business-safe input/output summaries
  for the user's own runs. They must not return full prompt snapshots, request
  payload snapshots, administrator debug metadata, or raw model responses;
- raw model responses must be redacted before storage. Normal-user APIs must
  not return raw model responses. Administrator APIs may return redacted raw
  model responses for diagnosis. Unredacted raw model responses must not be
  stored or exposed to any role;

Additional rules:

- prompt, request, response, and error fields must be redacted before storage;
- API keys, authorization headers, cookies, proxy credentials, profile paths,
  account-session data, and server-local paths must never be stored in trace
  snapshots;
- prompt, request, response, and comment snapshots must follow the accepted
  default size guardrails: each trace is about 64KB, prompt snapshot up to
  16KB, request snapshot up to 24KB, response snapshot up to 24KB, and sampled
  comments up to 20 comments with each comment truncated to a safe
  per-comment length;
- size limits are storage and API guardrails, not product-visible business
  rules. They should be applied before writing trace snapshots and before
  returning trace detail responses so one large prompt, request, model
  response, or comment set cannot make the database row or API payload
  unexpectedly large;
- if size caps are accepted, oversized snapshots should be truncated and marked
  with `truncated=true`; truncation must not block AI evaluation, report
  generation, or final run status;
- old evaluations without trace snapshots remain readable through
  `ai_evaluations` and should display a limited-context message.

### reports

Reports should include:

```text
workspace_id
job_id
run_id
created_by
send_status
job_snapshot_json
```

`job_id` may be nullable for old or orphaned report history. Phase 18A adds
`job_snapshot_json` so report grouping does not depend only on the current task
row.

Recommended `job_snapshot_json` fields:

```json
{
  "job_id": 123,
  "law_firm_name": "Example law firm",
  "platforms": ["xhs", "dy"],
  "keywords": ["keyword A", "keyword B"],
  "frequency": "daily",
  "email_template": {
    "id": 12,
    "name": "Daily report",
    "source": "task_bound",
    "subject_template": "Daily {law_firm_name}"
  },
  "deleted_at": null
}
```

Rules:

- capture the snapshot when the report is created;
- backfill the snapshot when an existing report's `job_id` still resolves to a
  monitoring task;
- if a task is later deleted or unavailable, keep the report grouped by the
  snapshot business context;
- for new reports, include customer-safe effective email-template provenance
  so historical reports can explain task-bound versus active-global/default
  template source without storing raw template HTML;
- keep unrecoverable old reports readable as limited-context historical
  reports;
- do not use the snapshot to bypass owner/workspace permissions.

### email_delivery_logs

Phase 16 adds a dedicated table for email delivery history and automatic-send
idempotency foundation:

```text
id
workspace_id
job_id
report_id
send_window_key
send_type
sent_by
sent_at
status
error_message
recipients_json
trigger_source
effective_recipients_json
effective_recipient_source
email_template_id
email_template_name
email_template_source
email_subject_template
created_at
```

`send_type` values:

- `auto`: automatic scheduler/report delivery;
- `manual_resend`: explicit user-triggered resend.

`status` values:

- `pending`;
- `sending`;
- `sent`;
- `failed`;
- `skipped`.

`send_window_key` rules for current scheduler frequencies:

- `daily`: `{job_id}_{YYYY-MM-DD}`;
- `6h`: `{job_id}_{YYYY-MM-DD}_{HH}`;
- `12h`: `{job_id}_{YYYY-MM-DD}_{HH}`;
- `cron`: `{job_id}_{YYYY-MM-DD}_{HH}`.

Idempotency rules:

- the schema enforces at most one `pending`, `sending`, or `sent` automatic
  delivery row for the same
  `workspace_id + job_id + send_window_key + send_type=auto`;
- failed or skipped automatic rows may be followed by a later retry row;
- manual resend may repeat and should not consume the automatic-send idempotency
  key;
- delivery attempts should preserve recipient summary and failure text without
  storing SMTP secrets;
- CR-036 adds `trigger_source` so delivery history can distinguish
  `scheduler_auto`, `manual_resend`, `test_mail`, `diagnostic`, or another
  confirmed trigger source;
- CR-036 keeps `recipients_json` as the task-specific recipients supplied by
  `monitor_jobs` or the request context. It may be empty when a task relies on
  global default recipients;
- CR-036 adds `effective_recipients_json` as the final recipient list that the
  delivery path attempted to use after task recipients, global
  default-recipient fallback, or a test/diagnostic target is resolved;
- CR-036 adds `effective_recipient_source` so operators can distinguish
  `task_recipients`, `global_default_fallback`, `test_target`,
  `manual_override`, or another confirmed source. `trigger_source` answers why
  the send path ran; `effective_recipient_source` answers where the recipient
  list came from;
- CR-039/Phase 17.2A should land together with the CR-036 delivery metadata
  migration when practical. It adds `email_template_id`,
  `email_template_name`, `email_template_source`, and `email_subject_template`
  to record the effective template used for the delivery without storing raw
  template HTML;
- Phase 17A connects scheduler/report delivery logic to this schema so
  automatic sends are idempotent by schedule window, duplicate automatic
  attempts are skipped, automatic failures are logged without blocking report
  generation, and manual resend uses separate `manual_resend` rows. Phase 17B
  still needs to expose this delivery history in the report center.

Template provenance values:

- `email_template_source = task_bound`: task has an explicit
  `email_template_id`;
- `email_template_source = active_global_fallback`: task has no explicit
  template and delivery used the current active global template;
- `email_template_source = default_renderer`: no persisted template was used
  and the system default report email renderer produced the body.

Report snapshots:

`reports.job_snapshot_json` should remain a customer-safe historical snapshot.
CR-039 adds template provenance to the snapshot for new reports:

```json
{
  "email_template": {
    "id": 123,
    "name": "Standard report",
    "source": "task_bound",
    "subject_template": "..."
  }
}
```

Do not store raw HTML template bodies in `job_snapshot_json`; store only the
metadata needed to explain which template was used.

## Migration Principles

- Add new fields without deleting current fields first.
- Current low-volume `profile_path` accounts can be reset or re-logged in under
  the new `profile_key` model.
- Do not expose legacy paths in UI.
- Keep secret values encrypted.
- Do not treat expired locks as directly reusable; recover the owning run before
  releasing persisted locks.
- Add Phase 10-18 fields in compatibility steps with defaults and without
  deleting current report, run, or email status fields.

## Confirmed Items

- V1 uses one default workspace.
- Normal users can delete their own non-running tasks.
- MVP includes minimal audit log for security-sensitive administrator actions.
- Profile keys use `{workspace_id}/{platform}/acc_{account_id}`.
- Account/profile locks use inline fields; proxy concurrency uses
  `resource_locks`.
- Administrator task timeout is a run-level wall-clock deadline and is not
  estimated from crawl range.
- Phase 10-18 frontend stack remains Vanilla JavaScript plus CSS custom
  properties.
- Run archive uses `visibility = visible | archived` and does not hard delete
  records.
- Run type uses `scheduled | manual | test`.
- Report grouping uses `reports.job_snapshot_json` for orphan/deleted-task
  report history.
- Email idempotency uses `email_delivery_logs` and schedule-window keys:
  daily by date; `6h`, `12h`, and `cron` by hour.
