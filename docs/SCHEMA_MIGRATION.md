# Schema Migration Plan

This document proposes a safe migration path from the current monitoring schema
to the target user, workspace, profile_key, and runtime-settings model.

The plan is intentionally compatible-first. It should not break existing local
data during the first migration step.

## Migration Principles

- Add new fields before deleting old fields.
- Backfill existing data into default workspace when workspace strategy is
  confirmed.
- Do not expose profile paths in UI.
- Because the current account count is low and the project is still in agile
  development, long-term `profile_path` compatibility is not required.
- Existing account profiles may be reset or re-logged in under the new
  `profile_key` model.

## Phase 0.5 - Schema Foundation

This phase should happen before full Phase 1 development.

Confirmed:

- Phase 0.5 can proceed using compatibility-safe schema additions before full
  Phase 1 feature implementation.
- Do not remove old fields in the first schema foundation step.

### Step 1 - Add Foundation Tables

Create:

```text
workspaces
users
user_sessions
system_settings
audit_logs
```

### Step 2 - Add Workspace And Ownership Fields

Add to business tables:

```text
workspace_id
created_by
updated_by
```

Priority tables:

- monitor_jobs;
- social_accounts;
- proxy_profiles;
- login_sessions;
- crawl_runs;
- raw_contents;
- raw_comments;
- ai_evaluations;
- reports;
- email_templates;
- ai_key_profiles.

Backfill:

```text
workspace_id = 1
created_by = NULL
updated_by = NULL
```

### Step 3 - Add Profile Key Fields

Add to `social_accounts`:

```text
profile_key TEXT
```

Add to `login_sessions`:

```text
profile_key TEXT
```

Existing `profile_path` can remain temporarily during schema transition, but it
should not be used as the primary identity for new account environments.

### Step 4 - Add Runtime Settings

Create `system_settings` table. Recommended flexible shape:

```text
id
workspace_id
key
value_json
value_type
is_locked
source
updated_by
updated_at
```

Confirmed:

- use the flexible key-value `system_settings` table for V1.

### Step 5 - Add Run Timeout And Lock Fields

Add run-level timeout tracking to `crawl_runs`:

```text
timeout_seconds INTEGER
deadline_at TEXT
timeout_reason TEXT
```

Rules:

- `timeout_seconds` stores the effective administrator timeout copied at run
  start;
- `deadline_at` stores `started_at + timeout_seconds`;
- `timeout_reason` records `subprocess_timeout`, `scheduler_check`,
  `startup_recovery`, or another safe internal reason;
- V1 should support `status = "timeout"` for runs that exceed the run-level
  wall-clock deadline.

Confirmed fields for account/profile locking:

```text
social_accounts.locked_by_run_id
social_accounts.locked_at
social_accounts.lock_expires_at
```

The account row lock also protects its `profile_key`.

Confirmed table for proxy concurrency:

```text
resource_locks
  id
  resource_type
  resource_id
  run_id
  locked_at
  expires_at
```

Recommended indexes/constraints:

```text
idx_account_lock_status on social_accounts(locked_by_run_id, lock_expires_at)
unique resource_locks(resource_type, resource_id, run_id)
idx_resource_lock_lookup on resource_locks(resource_type, resource_id, expires_at)
idx_resource_lock_cleanup on resource_locks(expires_at)
```

Confirmed approach:

- use inline lock fields for single-resource account/profile locks;
- use `resource_locks` for proxy concurrency because multiple runs may share a
  proxy up to `max_concurrency`;
- acquire proxy locks inside a transaction so concurrent runs cannot both pass
  the capacity check before inserting a lock.

Confirmed timeout behavior:

- task timeout is a run-level wall-clock deadline from administrator Runtime
  Strategy;
- V1 does not estimate timeout from crawl range;
- `lock_expires_at = deadline_at + lock_cleanup_buffer_seconds`;
- expired locks are released only by recovery logic after verifying the owning
  run state;
- startup recovery must reconcile persisted `running` runs and locks after a
  service restart.

## Profile Migration Strategy

Confirmed direction:

1. Existing low-volume account profiles do not need compatibility migration.
2. New accounts use `profile_key`.
3. Old accounts can be marked as needing re-login.
4. New login creates a new server-side profile under the new profile root.
5. UI and API should stop accepting arbitrary profile paths.

## Verification

After migration:

- existing tasks still load;
- existing accounts still display;
- old profile-path-based accounts are clearly marked as needing re-login or
  reset;
- new accounts use `profile_key`;
- normal-user UI never sees raw profile paths;
- server-like login/profile reuse test passes.

## Phase 14 - Run Center Visibility Fields

This phase is planned for the console optimization roadmap and is not
implemented yet.

Add fields to `crawl_runs`:

```text
visibility TEXT DEFAULT "visible"
run_type TEXT DEFAULT "scheduled"
archived_at TEXT NULL
archived_by INTEGER NULL
```

Backfill:

```text
visibility = "visible" where null
run_type = "scheduled" where null
archived_at = null
archived_by = null
```

Compatibility rules:

- do not delete old run records;
- do not physically delete archived runs;
- old list APIs may keep returning all runs until Phase 15 adds filters, but
  the default Phase 15 UI should show visible records first;
- keep existing `status` semantics separate from `visibility`.

Recommended indexes:

```text
idx_crawl_runs_visibility on crawl_runs(workspace_id, visibility, started_at)
idx_crawl_runs_type_status on crawl_runs(workspace_id, run_type, status)
```

## Phase 16 - Email Delivery Logs

This phase is planned for the console optimization roadmap and is not
implemented yet.

Create `email_delivery_logs`:

```text
id INTEGER PRIMARY KEY
workspace_id INTEGER NOT NULL
job_id INTEGER NOT NULL
report_id INTEGER NULL
send_window_key TEXT NOT NULL
send_type TEXT NOT NULL
sent_by INTEGER NULL
sent_at TEXT NULL
status TEXT NOT NULL
error_message TEXT NULL
recipients_json TEXT NULL
created_at TEXT NOT NULL
```

Allowed `send_type` values:

```text
auto
manual_resend
```

Allowed `status` values:

```text
pending
sending
sent
failed
skipped
```

Window-key rules:

```text
daily -> {job_id}_{YYYY-MM-DD}
6h -> {job_id}_{YYYY-MM-DD}_{HH}
12h -> {job_id}_{YYYY-MM-DD}_{HH}
cron -> {job_id}_{YYYY-MM-DD}_{HH}
```

Recommended indexes and constraints:

```text
idx_email_delivery_job_window on email_delivery_logs(workspace_id, job_id, send_window_key)
idx_email_delivery_report on email_delivery_logs(workspace_id, report_id, created_at)
idx_email_delivery_status on email_delivery_logs(workspace_id, status, created_at)
```

Automatic-send idempotency should enforce one active or successful automatic
send for the same `workspace_id + job_id + send_window_key + send_type=auto`.
SQLite may require this through a partial unique index or transactional
application logic, depending on the current migration helper capabilities.

Compatibility rules:

- keep existing report `email_status` and `email_error` as latest-state fields
  during migration;
- backfill is optional for old reports because old attempts were not recorded;
- do not store SMTP credentials or full secret configuration in delivery logs.

## Phase 18 - Report Job Snapshot

This phase is planned for the console optimization roadmap and is not
implemented yet.

Add field to `reports`:

```text
job_snapshot_json TEXT NULL
```

Recommended snapshot:

```json
{
  "job_id": 123,
  "law_firm_name": "Example law firm",
  "platforms": ["xhs", "dy"],
  "keywords": ["keyword A", "keyword B"],
  "frequency": "daily",
  "deleted_at": null
}
```

Backfill strategy:

1. For reports whose `job_id` still resolves to `monitor_jobs`, populate the
   snapshot from the current task row.
2. For reports with missing or null `job_id`, leave `job_snapshot_json` null or
   populate only safely recoverable report context.
3. Report center should label unrecoverable rows as historical reports with
   limited context, not as current active tasks.

Compatibility rules:

- do not require `job_snapshot_json` for old reports at first read;
- never use snapshot content to bypass workspace or owner filtering;
- keep `job_id` for active task relations.

## Blocking Decisions

No CR-012 account-environment decisions remain open.

Confirmed:

- workspace strategy uses one default workspace;
- authentication strategy uses session-based auth;
- profile migration uses the direct new `profile_key` model;
- final `profile_key` format is `{workspace_id}/{platform}/acc_{account_id}`;
- account/profile locks use inline fields;
- proxy concurrency uses `resource_locks`;
- lock timeout follows the run deadline plus cleanup buffer;
- minimal audit log is included in MVP.
- Phase 10-18 run archive uses `visibility = visible | archived`.
- Phase 10-18 run type uses `scheduled | manual | test`.
- Phase 10-18 email delivery uses `email_delivery_logs`.
- Phase 10-18 report orphan handling uses `reports.job_snapshot_json`.
