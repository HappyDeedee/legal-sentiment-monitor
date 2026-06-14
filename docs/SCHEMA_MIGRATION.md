# Schema Migration Plan

This document proposes a safe migration path from the current monitoring schema
to the target user, workspace, profile_key, and runtime-settings model.

The plan is intentionally compatible-first. It should not break existing local
data during the first migration step.

## Migration Principles

- Add fields before removing or renaming fields.
- Keep legacy `profile_path` readable during transition.
- Backfill existing data into default workspace.
- Do not expose legacy profile paths in UI.
- Keep migration reversible until server-like validation passes.

## Phase 0.5 - Schema Foundation

This phase should happen before full Phase 1 development.

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

Keep:

```text
profile_path TEXT
```

as legacy compatibility until migration is confirmed.

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

Recommended compatibility strategy:

1. Existing accounts keep `profile_path`.
2. New accounts use `profile_key`.
3. A resolver chooses:
   - if `profile_key` exists, resolve under account profile root;
   - else if legacy `profile_path` exists, use it as compatibility fallback.
4. After successful re-login or verified migration, set `profile_key`.
5. Later remove UI and API support for arbitrary profile paths.

Open confirmation:

- Should old profile directories be physically moved, or should compatibility
  fallback remain until re-login?

## Verification

After migration:

- existing tasks still load;
- existing accounts still display;
- existing login profiles can still be resolved;
- new accounts use `profile_key`;
- normal-user UI never sees raw profile paths;
- server-like login/profile reuse test passes.

## Blocking Decisions

Before implementation, confirm:

- workspace strategy;
- authentication strategy;
- profile migration strategy;
- lock table vs lock fields;
- audit log MVP scope.

