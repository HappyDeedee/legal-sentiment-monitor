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
- accepted CR-070 account-environment export/import packages for
  administrator-only account migration.

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
environment_region
browser_platform
identity_template
fingerprint_seed
user_agent
timezone
locale
accept_language
screen_width
screen_height
viewport_width
viewport_height
device_scale_factor
is_mobile
has_touch
identity_generator_name
identity_generator_version
identity_environment_version
proxy_region_snapshot
browser_environment_locked_at
browser_environment_lock_reason
requires_relogin
identity_state
identity_runtime_snapshot_json
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

CR-047 account identity fields are accepted for future implementation, not yet
active in the current schema unless the Phase 5.1 migration has run. The
fields make the browser identity inputs for a platform account explicit and
persistent:

- `environment_region`: customer-safe region bucket used for consistency
  checks, such as `CN_MAINLAND`, `HK`, or `SG`;
- `browser_platform`: the browser platform fingerprint family such as
  `windows`, `macos`, `linux`, or `android`;
- `identity_template`: final stable device/browser template identifier such as
  `CN_WIN_CHROME_1920`, selected automatically by the generator or from an
  administrator's advanced pre-login template-family choice;
- `fingerprint_seed`: deterministic seed used by a browser-environment
  provider where supported;
- `user_agent`: the account's stable user-agent string;
- `timezone`, `locale`, and `accept_language`: stable browser context
  timezone and language inputs;
- `screen_width`, `screen_height`, `viewport_width`, `viewport_height`,
  `device_scale_factor`, `is_mobile`, and `has_touch`: stable screen,
  viewport, and device-class inputs;
- `identity_generator_name`, `identity_generator_version`, and
  `identity_environment_version`: metadata for stable regeneration,
  compatibility checks, and future migration decisions;
- `proxy_region_snapshot`: redacted/customer-safe proxy region evidence used
  by the validator, not a proxy URL or credential store;
- `browser_environment_locked_at`: set after successful QR login or accepted
  Cookie login validation;
- `browser_environment_lock_reason`: customer-safe reason such as
  `qrcode_login_success` or `cookie_validation_success`;
- `requires_relogin`: marks locked accounts whose identity template or proxy
  region changed in a way that requires explicit administrator reset/re-login.
- `identity_state`: lifecycle state for the CR-047 account identity, such as
  `draft`, `generated`, `validated`, `login_in_progress`, `locked`, `active`,
  `requires_relogin`, or `resetting`;
- `identity_runtime_snapshot_json`: customer-safe requested/effective runtime
  snapshot for Playwright/CDP launches, including provider metadata, effective
  UA/timezone/locale/viewport/screen/device/proxy-region values, unsupported
  field list, and `fallback_used` flag. It must not contain cookies, proxy
  credentials, raw profile paths, CDP endpoints, or noVNC tokens.

`proxy_id` remains the account-bound stable proxy policy field. After CR-047
locks an account identity, task-level proxy overrides are rejected for that
locked account environment; changing the proxy requires explicit reset/re-login.
`proxy_region_snapshot` must use a customer-safe region bucket such as
`CN_MAINLAND`, `HK`, `SG`, `TW`, `JP`, `US`, or `EU`, not an IP address, city,
province, proxy URL, or credential value. The generator and validator
specification lives in `docs/ACCOUNT_ENVIRONMENT.md` and is the source of
truth for deterministic seed derivation, template expansion, state transitions,
fail-closed rules, provider mapping, and runtime snapshot shape.
The migration should be additive, should keep existing accounts readable, and
should not expose raw profile paths, cookies, proxy
credentials, CDP endpoints, noVNC sessions, or fingerprint-debug internals
through normal-user APIs.

CR-070 adds an accepted account-environment export/import capability. The
account row remains the source of truth after import, but package creation and
import need audit-safe metadata. The package manifest may contain the selected
account fields above plus redacted platform-account metadata and compatibility
evidence. It must not contain plaintext cookies, proxy credentials, profile
paths, CDP endpoints, noVNC tokens, package passphrases, or deployment
encryption keys.

The package is scoped to one selected platform account environment. It does
not include monitoring tasks, crawl runs, reports, AI traces, email delivery
logs, users, runtime settings, or full database backup content by default. If
a later product requirement expands package scope, update this data model and
the test plan before implementation.

CR-070 V1 uses a slim login-state migration package, not a raw full profile
copy. Package metadata may describe slim profile-state sections, but the
package should exclude cache, GPU cache, code cache, media cache, crash dumps,
downloads, screenshots, temporary files, and duplicated or regenerable browser
artifacts by default. The encrypted payload may contain a source proxy
host/IP plus port hint for target-side mapping, but it must not contain proxy
username, password, token, authentication header, or provider secret.

CR-094 provider architecture is future planning only. The current data model
does not add provider tables, provider-profile binding tables, capability
tables, or provider-specific account fields for CR-094. Any future provider
schema must be introduced through a separate accepted data model and migration
CR, and it must preserve `profile_key` as the upper-layer account identity
instead of creating a parallel account/profile system.

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

CR-070 export/import audit actions:

```text
account_package_export_requested
account_package_export_ready
account_package_export_completed
account_package_export_failed
account_package_export_cancelled
account_package_export_expired
account_package_import_preflight
account_package_import_completed
account_package_import_failed
account_package_import_requires_relogin
account_package_import_rolled_back
```

Audit `details_json` should include only redacted metadata:

```text
package_mode
package_version
source_platform
source_account_id
target_account_id
identity_environment_version
provider_name
compatibility_result
login_verification_result
redacted_checksum
failure_reason
operation_status
trigger_source
```

It must not include raw cookies, raw profile keys or paths, proxy credentials,
proxy endpoint hints, package passphrases, CDP endpoints, noVNC tokens,
command lines, or deployment encryption keys. Metadata-only export audit is
still treated as sensitive when the package contains CR-047 identity details
such as `fingerprint_seed`, recognized platform account IDs, or runtime
snapshot summaries.

### account_environment_packages

CR-070 accepted optional metadata table. Implementation may choose a temporary
download-only artifact for V1, but if package history is persisted, use an
audit-safe table such as:

```text
id
workspace_id
account_id
platform
package_mode
package_version
identity_environment_version
provider_name
status
redacted_checksum
manifest_summary_json
operation_type
failure_reason
artifact_path_redacted
created_by
created_at
updated_at
expires_at
downloaded_at
deleted_at
```

Rules:

- do not store package plaintext in the database;
- if encrypted package bytes are stored at all, store only in runtime artifact
  storage with retention and cleanup rules, not in Git;
- `manifest_summary_json` must be redacted and customer-safe;
- package rows should support audit, cleanup, and operator diagnostics, not
  long-term secret storage.
- `artifact_path_redacted` may hold an opaque artifact ID or redacted storage
  reference only, not a local filesystem path;
- metadata-only and slim-login-state package rows use the same allowed
  operation-state vocabulary so cleanup and recovery can be generic.

Allowed `operation_type` values:

```text
export
import
```

Allowed export `status` values:

```text
preflight
locked
reading_metadata
snapshotting_profile
building_payload
encrypting
ready_for_download
completed
failed
cancelled
expired
deleted
```

Allowed import `status` values:

```text
preflight
preflight_failed
decrypting
extracting_profile
writing_database
verifying_login
active
requires_relogin
failed
rolled_back
```

Terminal statuses:

```text
ready_for_download
completed
failed
cancelled
expired
deleted
preflight_failed
active
requires_relogin
rolled_back
```

The implementation may split export and import operations into separate tables
later if the state volume grows, but the same redaction, retention,
operation-lock, and terminal-finalization rules remain required.

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

Status: Implemented and verified for CR-034 / Phase 20B-E.

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
  `ai_trace_retention_days`, defaulting to 30 days. Phase 20B implements this
  runtime setting and must not hard-code the retention window in the trace
  persistence layer;
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

Implementation status:

- Phase 20B creates `ai_evaluation_traces`, writes redacted/capped trace
  snapshots for successful, failed, and fallback evaluations, and provides a
  trace-only cleanup helper using `ai_trace_retention_days`;
- Phase 20C exposes these snapshots through role-safe Run Detail and
  per-evaluation detail APIs;
- Phase 20D exposes the run-scoped frontend detail surface, and Phase 20E
  links report leads with `run_id` back to the originating run detail while
  preserving limited-context display for old/no-run data.

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
