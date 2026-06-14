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
```

Optional, pending user confirmation:

```text
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

Open confirmation:

- flexible key-value settings vs strongly typed runtime settings table.

### Step 5 - Add Lock Fields

Proposed fields for account locking:

```text
social_accounts.locked_by_run_id
social_accounts.locked_at
```

Proposed fields for proxy concurrency may be implemented through runtime rows
or a separate lock table:

```text
resource_locks
  id
  resource_type
  resource_id
  run_id
  locked_at
  expires_at
```

Open confirmation:

- Use explicit lock fields or a generic `resource_locks` table?

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
- existing login profiles can still be resolved;
- new accounts use `profile_key`;
- normal-user UI never sees raw profile paths;
- server-like login/profile reuse test passes.

## Blocking Decisions

Before implementation, still confirm:

- lock table vs lock fields.

Confirmed:

- workspace strategy uses one default workspace;
- authentication strategy uses session-based auth;
- profile migration uses the direct new `profile_key` model;
- minimal audit log is included in MVP.
