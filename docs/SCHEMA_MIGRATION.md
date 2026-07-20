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

### Accepted Phase 5.1 - Add Account Identity Fields

Status: implemented and independently verified in the isolated Phase 5.1A
worktree against `main@8b55c2a`. The additive migration extends the existing
`profile_key` model with storage for a persisted, locked account identity while
Phase 5.1B now supplies INSERT-only deterministic generation and validation.
Phase 5.1C implements locking/reset/audit behavior without a new migration;
provider/runtime binding remains Phase 5.1D.

CR-117 adds a versioned deployment-local browser selection manifest and does
not add or migrate SQLite columns. Existing Profile data without the manifest
keeps the pre-CR-117 explicit-or-Playwright authority.

Additive fields for `social_accounts`:

```text
environment_region TEXT NOT NULL DEFAULT ''
browser_platform TEXT NOT NULL DEFAULT ''
identity_template TEXT NOT NULL DEFAULT ''
fingerprint_seed TEXT NOT NULL DEFAULT ''
user_agent TEXT NOT NULL DEFAULT ''
timezone TEXT NOT NULL DEFAULT ''
locale TEXT NOT NULL DEFAULT ''
accept_language TEXT NOT NULL DEFAULT ''
screen_width INTEGER
screen_height INTEGER
viewport_width INTEGER
viewport_height INTEGER
device_scale_factor REAL
is_mobile INTEGER NOT NULL DEFAULT 0
has_touch INTEGER NOT NULL DEFAULT 0
identity_generator_name TEXT NOT NULL DEFAULT ''
identity_generator_version TEXT NOT NULL DEFAULT ''
identity_environment_version TEXT NOT NULL DEFAULT ''
proxy_region_snapshot TEXT NOT NULL DEFAULT ''
browser_environment_locked_at TEXT
browser_environment_lock_reason TEXT NOT NULL DEFAULT ''
requires_relogin INTEGER NOT NULL DEFAULT 0
identity_state TEXT NOT NULL DEFAULT 'draft'
identity_runtime_snapshot_json TEXT NOT NULL DEFAULT ''
```

Migration and compatibility:

- use the generation, validation, provider, lifecycle, and snapshot
  specifications in `docs/ACCOUNT_ENVIRONMENT.md` as the implementation source
  of truth;
- generate or assign account identity values before first QR login or accepted
  Cookie validation;
- keep generation stable, differentiated, self-consistent, and explainable by
  persisting template and generator metadata;
- validate region/timezone/locale/accept-language, UA/platform, screen/
  viewport/device flags, proxy policy, and required locked fields before
  login/crawl launch;
- for China mainland proxies, use self-consistent defaults such as
  `environment_region = CN_MAINLAND`, `timezone = Asia/Shanghai`, `locale =
  zh-CN`, and `accept_language = zh-CN` for catalog v2;
- lock the account identity after successful QR login or accepted Cookie
  validation;
- keep existing accounts readable, do not silently backfill guessed identity
  values, and mark them as needing environment confirmation/re-login;
- existing rows added by migration start as `identity_state = draft` with
  empty identity fields; they are readable but cannot launch through CR-047
  locked-identity paths until regenerated and re-logged in;
- nullable dimension and scale fields use SQL `NULL` for not generated, while
  `TEXT NOT NULL DEFAULT ''` fields use an empty string for not generated;
  Phase 5.1B validation distinguishes `NULL` from numeric zero;
- do not move old profile directories during this migration;
- keep `proxy_id` as the account-bound stable proxy policy field and reject
  task-level proxy overrides for locked account environments; changing the
  proxy requires explicit reset/re-login;
- block silent edits to locked account identity fields and require an audited
  reset/re-login path;
- mark locked accounts `requires_relogin` when a template or proxy-region
  change would make the old identity inconsistent;
- store requested/effective runtime identity evidence in
  `identity_runtime_snapshot_json` after successful login validation or crawl
  launch when effective values are available;
- add indexes for operational queries:
  `idx_social_accounts_identity_state`,
  `idx_social_accounts_requires_relogin`, and
  `idx_social_accounts_identity_template`;
- do not expose raw profile paths, cookies, proxy credentials, CDP endpoints,
  noVNC sessions, or fingerprint-debug output through customer-facing APIs.

Phase 5.1A implementation uses one idempotent
`_ensure_phase_51_account_identity_schema` helper, reuses the existing
`_ensure_column` migration authority, and creates each documented index as a
non-unique workspace-scoped index. Reopening the same database is a no-op for
existing columns and indexes.

Phase 5.1B does not add another schema migration. It uses the Phase 5.1A
columns through one bounded identity UPDATE inside the new-account INSERT
transaction. Existing rows and all account UPDATE paths keep their current
identity values until the explicit Phase 5.1C lifecycle/reset flow runs.

### Accepted CR-112 - Persistent Profile Promotion And Browser-Sync Metadata

Status: `Implemented / Verified (Packet C.1-C.3); Dependency-Gated (Packet D)`. Packet B is verified. C.1 now
applies this additive, backward-compatible migration after Packet B fixed the
direct acquisition/protocol boundary. It is not part of Phase 5.1P or the
historical CR-047 schema body; C.2 and C.3 are verified within their recorded
proof boundaries, and D remains gated.

Accepted Packet C additions are specified in `DATA_MODEL.md`:

- `social_accounts.cookie_source`;
- `social_accounts.profile_runtime_version` with safe default `0`;
- `social_accounts.profile_ready_at`;
- `account_profile_promotions` durable journal;
- `login_sessions.cookie_source`, `profile_promotion_id`,
  `acquisition_generation`, `provider_resolution_id`, and
  `browser_attempt_id`.

Migration is delivered in serial Packet C sub-packets:

1. **C.1 Profile service:** add backward-compatible reads and the promotion
   journal. Existing rows stay `profile_runtime_version = 0`; no row is marked
   Profile-ready without a real candidate validation, fixed-path promotion,
   crawler-equivalent active-path recheck, and committed account update. The
   candidate is initialized fresh from the Phase 5.1 provider inputs; it does
   not clone active Profile storage.
2. **C.2 Browser acquisition:** add exact-context session metadata and the
   default-off direct acquisition API/UI. This migration unit is verified.
   No Connector binding table or Cookie-bridge WebSocket route is added.
3. **C.3 Profile-only runner:** keep each committed version-1
   `login_type=cookie` account, mark invalid/missing version-0 accounts
   `requires_relogin`, enable the
   internal profile-only child contract for those accounts, and retire raw
   Cookie argv after fake-process inspection and regression evidence pass.
   Existing QR/Profile execution remains regression-protected and is not
   silently reclassified by CR-112 V1.

C.3 uses one maintenance cutover. Pause scheduler/new manual runs, migrate or
classify every Cookie account, and require zero runnable version-0 Cookie
accounts before activating the new command builder. After activation, version
1 always uses hidden `--monitor_profile_only true` plus the exact provider
environment and no `--cookies`; version 0 is `identity_state=requires_relogin`,
limited/non-active, and rejected before child spawn. The reserved child exit
code `42` maps only the profile-login guard to `requires_relogin`. There is no
mixed-mode account fallback.

Migration and recovery rules:

- schema additions precede all runtime activation and tolerate old rows;
- startup recovery reconciles every non-terminal promotion journal before
  login, account check, export, reset, or crawl can use that account;
- the fixed active path remains derived from `profile_key`; candidate and
  rollback paths are operation artifacts and never become database identity;
- each rename completes before its checkpoint write; a checkpoint may lag one
  rename, so commit state plus the operation marker and exact directory-shape
  table in `ACCOUNT_ENVIRONMENT.md` govern recovery;
- a pre-commit crash restores the previous active Profile and leaves the
  previous encrypted Cookie/account row unchanged;
- contradictory filesystem/journal evidence marks `recovery_required` and
  `requires_relogin`, blocks execution, and preserves remaining files;
- candidate/rollback cleanup is idempotent, same-volume, lock-aware, excluded
  from backups/exports, and triggered after the first successful managed run,
  by startup/periodic `cleanup_after` scan, and synchronously before a new
  promotion; a retained rollback or failed cleanup blocks the next refresh so
  at most one rollback artifact exists per account;
- the account-run lock and non-terminal promotion journal use a shared atomic
  exclusion predicate, so a crawl and Profile promotion cannot win separate
  locks and mutate the same active Profile concurrently;
- migration logs and audit rows contain opaque operation IDs and redacted
  categories, not secret values or raw paths.

Rollback boundaries:

- before C.3 acceptance, deployments may remain on the unchanged current
  runner baseline while C.1/C.2 are still disabled;
- `MONITOR_BROWSER_COOKIE_SYNC_ENABLED=false` rolls back C.2 only and must leave C.1
  advanced-manual Cookie support usable;
- the browser-sync flag is referenced only by C.2 route/UI/readiness/managed-
  browser launch. C.1 validation/promotion/recovery/manual Cookie and C.3
  command/child/platform guards neither read nor import-gate on that flag;
- after C.3 acceptance, rollback must preserve C.1 and the profile-only runner;
  it must not restore raw Cookie argv;
- schema deletion is never the first rollback. Older code must ignore additive
  fields/tables, and unresolved promotion journals must be finalized before a
  binary downgrade that cannot read them.

The administrator full-Cookie reveal adds no plaintext schema field, cache
table, or durable response copy. It reads the existing encrypted account value
only after authorization and returns it through the dedicated no-store POST
response. Audit schema stores only redacted access metadata.

### Accepted Phase 5.2 - Account Environment Export/Import Package

Status: Accepted for CR-070 planning. Implementation should follow the
confirmed V1 policy: metadata-only export plus slim passphrase-encrypted
login-state migration package, proxy host/IP plus port hint allowed only inside
the encrypted payload, no proxy credentials, create-new import by default, and
avatar metadata only.

No schema change is strictly required for a first metadata-only design if
packages are generated as immediate encrypted download artifacts and audit logs
record the action. The package is scoped to one selected platform account
environment and is not a full database backup of monitoring tasks, crawl runs,
reports, AI traces, email delivery logs, users, runtime settings, or customer
business history. The migration package is a slim login-state package, not a
raw full browser profile copy; exclude cache, GPU cache, code cache, media
cache, crash dumps, downloads, screenshots, temporary files, and duplicated or
regenerable browser artifacts by default. If persisted package history is
accepted, add an optional
metadata table:

```text
account_environment_packages
  id INTEGER PRIMARY KEY
  workspace_id INTEGER NOT NULL
  account_id INTEGER NOT NULL
  platform TEXT NOT NULL
  package_mode TEXT NOT NULL
  package_version TEXT NOT NULL
  identity_environment_version TEXT NOT NULL DEFAULT ''
  provider_name TEXT NOT NULL DEFAULT ''
  status TEXT NOT NULL
  redacted_checksum TEXT NOT NULL DEFAULT ''
  manifest_summary_json TEXT NOT NULL DEFAULT '{}'
  operation_type TEXT NOT NULL DEFAULT 'export'
  failure_reason TEXT NOT NULL DEFAULT ''
  artifact_path_redacted TEXT NOT NULL DEFAULT ''
  created_by INTEGER
  created_at TEXT NOT NULL
  updated_at TEXT
  expires_at TEXT
  downloaded_at TEXT
  deleted_at TEXT
```

Recommended indexes:

```text
idx_account_packages_account on account_environment_packages(workspace_id, account_id, created_at)
idx_account_packages_status on account_environment_packages(workspace_id, status, created_at)
idx_account_packages_expiry on account_environment_packages(expires_at)
```

Compatibility and safety:

- this table stores package metadata only, not plaintext package content;
- encrypted package bytes, if retained, must live in runtime artifact storage
  with cleanup guidance and must never be committed to Git;
- `manifest_summary_json` must be redacted and must not include cookies,
  platform tokens, proxy credentials, proxy endpoint hints, raw profile paths,
  package passphrases, CDP endpoints, noVNC tokens, command lines, or
  deployment encryption keys;
- export and import actions should also write `audit_logs` rows using the
  redacted event names defined in `DATA_MODEL.md`;
- `status` values should use the export/import operation-state vocabulary from
  `DATA_MODEL.md` and `ACCOUNT_ENVIRONMENT.md`, including terminal states for
  ready, completed, failed, cancelled, expired, deleted, preflight_failed,
  active, requires_relogin, and rolled_back;
- `artifact_path_redacted` may contain only an opaque runtime artifact ID or
  redacted storage reference, never a local path;
- metadata-only package metadata is still sensitive when it includes CR-047
  identity details such as `fingerprint_seed`, recognized platform account
  IDs, or runtime snapshot summaries. The recommended V1 package envelope is
  encrypted unless a later redacted diagnostic export is confirmed;
- slim login-state package payload may include source proxy host/IP plus port
  only as an encrypted endpoint hint for target-side mapping. The database,
  audit logs, manifest summaries, and ordinary APIs must not store or expose
  this endpoint hint;
- package operation locks must prevent concurrent export/import, login, crawl,
  reset, or profile mutation for the same account while a package operation is
  non-terminal;
- when CR-112 exists on the source deployment, export includes only the fixed
  committed active Profile and committed account metadata. Candidate/rollback
  directories and non-terminal promotion journals are excluded; due cleanup must remove any
  retained rollback and active operation marker before export proceeds;
- export operations must release locks and delete staging files on success,
  failure, cancellation, timeout, process interruption recovery, expiry, or
  deletion;
- metadata-only import creates or updates an account as needing login;
- slim login-state import must write only validated slim profile-state files
  under the target account profile root and must reject traversal, absolute
  paths, full raw-profile cache dumps, and corrupt archives before any account
  becomes active;
- imported accounts should be marked active only after login-state verification
  succeeds; otherwise mark `requires_relogin` or an equivalent account state.
- import cleanup must be idempotent: repeated recovery cannot reopen terminal
  states, overwrite an existing target account, or leave package/profile locks
  stuck.

### Future CR-094 - Crawler Provider Architecture Schema Boundary

Status: Needs Confirmation for CR-094 planning. No schema migration is accepted
for CR-094 in the current documentation-governance batch.

Rules:

- do not add provider tables, provider-profile binding tables, capability
  tables, provider-runtime snapshot tables, or provider-specific account fields
  as part of CR-094 planning;
- do not fold CR-094 schema work into Phase 5.1P, because Phase 5.1P is the
  read-only current MediaCrawler/CDP compatibility preflight for CR-047;
- if a future provider implementation needs schema, record a separate data
  model/migration CR before coding;
- future schema must preserve `profile_key`, monitor-owned account/profile/
  proxy locks, audit redaction, and the existing task/report/Run Detail model
  instead of creating parallel provider-specific product systems.

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

### Accepted Phase 20 - Add AI Evaluation Trace Snapshots

Status: Phase 20B implemented and verified for CR-034 trace persistence.
Phase 20B adds a configurable `ai_trace_retention_days` runtime setting with a
30-day default and creates `ai_evaluation_traces` with capped/redacted JSON
fields. Visibility is confirmed for the later Phase 20C APIs: normal-user APIs
return only business-safe summaries, administrator APIs may return redacted
prompt/request/response debug snapshots, unredacted raw responses must not be
stored or exposed, and normal-user APIs must not return raw responses.

Accepted compatible migration:

```text
CREATE TABLE ai_evaluation_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL,
    raw_content_id INTEGER NOT NULL,
    ai_evaluation_id INTEGER,
    attempt_index INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    prompt_snapshot TEXT NOT NULL DEFAULT '',
    input_payload_json TEXT NOT NULL DEFAULT '{}',
    request_snapshot_json TEXT NOT NULL DEFAULT '{}',
    response_snapshot TEXT NOT NULL DEFAULT '',
    parsed_result_json TEXT NOT NULL DEFAULT '{}',
    error_message TEXT NOT NULL DEFAULT '',
    duration_ms INTEGER,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL
)
```

Accepted indexes:

```text
workspace_id + run_id + raw_content_id
workspace_id + ai_evaluation_id
workspace_id + status + created_at
```

Compatibility:

- do not backfill exact prompt/request snapshots for historical evaluations
  because they were not persisted at evaluation time;
- historical evaluations should stay readable through `ai_evaluations` and be
  marked limited-context in the run-detail UI;
- migration must be additive and must not rewrite or delete existing
  `ai_evaluations`, `raw_contents`, or `raw_comments` rows.
- Phase 20B adds `ai_trace_retention_days` to runtime settings,
  `monitor.example.yaml`, validation, and diagnostics/cleanup visibility in the
  same implementation batch; trace retention is not hard-coded.
- Accepted default size caps must be enforced before storage and before
  trace-detail API responses: each trace is about 64KB, prompt snapshot up to
  16KB, request snapshot up to 24KB, response snapshot up to 24KB, and sampled
  comments up to 20 comments with per-comment truncation. Oversized fields
  should be truncated with a visible `truncated=true` marker rather than
  failing AI evaluation or report generation.

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

CR-035 confirmed compatibility:

- support `status = "interrupted"` as a first-class terminal state for stale or
  disappeared background tasks that cannot safely complete normal
  finalization;
- keep `partial_failed` for runs that complete with known partial failures;
- treat new `crawl_runs.job_id` persistence as the primary fix and historical
  backfill as fallback-only;
- do not add dedicated progress columns in the first CR-035 fix unless needed;
  store `phase`, `phase_started_at`, `progress_updated_at`, retry state, last
  safe result or return value, redacted last error, and progress snapshots in
  `crawl_runs.summary`;
- add dry-run-first migration/backfill logic for historical rows where
  `crawl_runs.job_id` is null and `summary.job_id` resolves to an existing
  `monitor_jobs.id`;
- skip unresolved rows and log a redacted summary instead of guessing.

### Step 5A - Add Email Delivery Metadata Follow-Ups

CR-036 and CR-039 should share one additive email-delivery metadata migration
when implemented together. Add nullable or default-empty fields to
`email_delivery_logs`:

```text
trigger_source TEXT NOT NULL DEFAULT ''
effective_recipients_json TEXT NOT NULL DEFAULT '[]'
effective_recipient_source TEXT NOT NULL DEFAULT ''
email_template_id INTEGER
email_template_name TEXT NOT NULL DEFAULT ''
email_template_source TEXT NOT NULL DEFAULT ''
email_subject_template TEXT NOT NULL DEFAULT ''
```

Compatibility:

- existing `recipients_json` remains readable as the historical task/request
  recipient snapshot;
- for historical rows, `effective_recipients_json` may be backfilled from
  `recipients_json` only when that value is non-empty and clearly represented
  the final delivery target;
- historical rows whose final recipient list is not recoverable should keep
  `effective_recipients_json = []` and use a customer-safe limited-context
  label rather than guessing;
- template provenance for historical rows is best-effort only. If the exact
  template cannot be proven from persisted data, leave the template fields empty
  or mark the source as limited context;
- the migration must not store raw SMTP secrets, raw template HTML, cookies,
  proxy credentials, profile paths, API keys, or local report paths in delivery
  metadata.

CR-039 also extends new `reports.job_snapshot_json` payloads with
customer-safe email-template provenance. Existing report snapshots should not
be rewritten unless a dry-run backfill can prove the exact template used.

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

This phase is implemented and verified for the console optimization roadmap.
It prepares the data model only; Phase 15 must still add API filters,
archive/restore actions, default visible-only behavior, and frontend controls.

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

Implementation notes:

- new database creation includes the four fields with compatible defaults;
- existing database migration adds missing fields through `_ensure_column`;
- empty existing `visibility` values are backfilled to `visible`;
- empty existing `run_type` values are backfilled to `scheduled`;
- tests verify the fields, indexes, backfill, and compatibility with run,
  run-list, report-link, and status reads.

## Phase 16 - Email Delivery Logs

This phase is implemented and verified for the console optimization roadmap.
It prepared the data model only; Phase 17A has connected scheduler/mailer
delivery logic, automatic-send idempotency, and manual resend logging to this
foundation. Phase 17B has surfaced scoped delivery history in the report
center. Phase 18A report snapshots are now separate implemented schema work.

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
trigger_source TEXT NULL
effective_recipients_json TEXT NULL
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
idx_email_delivery_auto_window_unique on email_delivery_logs(workspace_id, job_id, send_window_key, send_type)
  where send_type = "auto" and status in ("pending", "sending", "sent")
```

Automatic-send idempotency foundation is implemented through a SQLite partial
unique index. It enforces one active or successful automatic delivery row for
the same `workspace_id + job_id + send_window_key + send_type=auto`, while
allowing failed/skipped retries and repeated manual resend rows.

Compatibility rules:

- keep existing report `email_status` and `email_error` as latest-state fields
  during migration;
- backfill is optional for old reports because old attempts were not recorded;
- CR-036 adds `trigger_source` and `effective_recipients_json` compatibly for
  new and future delivery logs;
- existing delivery rows can backfill `trigger_source` from known `send_type`
  where clear, but should not guess unknown effective recipients;
- do not store SMTP credentials or full secret configuration in delivery logs.

Implementation notes:

- new database creation includes `email_delivery_logs`;
- existing database migration creates the table if missing and ensures every
  required column exists;
- invalid legacy `send_type` values are normalized to `auto`;
- invalid legacy `status` values are normalized to `pending`;
- missing `recipients_json` values are normalized to `[]`;
- missing `trigger_source` values can be normalized from `send_type` where
  possible;
- missing `effective_recipients_json` values become `[]` unless safely known;
- tests verify the fields, indexes, partial unique index behavior, window-key
  rules, old report email fields, and delivery-log secret redaction.

## Phase 18 - Report Job Snapshot

Phase 18A is implemented and verified for the console optimization roadmap. It
prepares the data model for Phase 18B frontend task grouping.

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
   snapshot from the current task row. This is implemented in compatible
   schema initialization.
2. For reports with missing or null `job_id`, leave `job_snapshot_json` null or
   populate only safely recoverable report context.
3. Report center should label unrecoverable rows as historical reports with
   limited context, not as current active tasks. Phase 18A exposes the
   limited-context data flags; Phase 18B must render the final grouped labels.

Compatibility rules:

- do not require `job_snapshot_json` for old reports at first read;
- never use snapshot content to bypass workspace or owner filtering;
- keep `job_id` for active task relations.
- when a task is deleted through the monitor API, update the report snapshot's
  `deleted_at` context before removing the task row.
- keep Phase 18A data-model behavior separate from Phase 18B frontend grouping.

Implementation notes:

- new database creation includes `reports.job_snapshot_json`;
- existing database migration ensures the column exists and backfills
  resolvable reports;
- report creation persists a snapshot immediately;
- report reads expose customer-safe `job_snapshot`, `job_deleted`,
  `legacy_without_job_snapshot`, and `limited_context` fields for later
  grouping;
- tests verify new-report persistence, backfill, deleted-task readability,
  unrecoverable limited context, and owner/workspace scope.

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
