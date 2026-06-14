# Data Model

This document describes the target data model for V1. It is a planning document
and may require migration from the current schema.

## Implementation Status

This is a target planning document. Most Phase 0.5 tables and fields described
here do not exist in the current codebase yet.

Phase 0.5 will add:

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

Current code should be checked before implementation work begins. Do not assume
these tables or columns already exist until Phase 0.5 is completed and verified.

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
```

Run status should include `timeout` for runs stopped by the run-level wall-clock
deadline. Timeout runs may still have partial results.

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

### reports

Reports should include:

```text
workspace_id
job_id
run_id
created_by
send_status
```

## Migration Principles

- Add new fields without deleting current fields first.
- Current low-volume `profile_path` accounts can be reset or re-logged in under
  the new `profile_key` model.
- Do not expose legacy paths in UI.
- Keep secret values encrypted.
- Do not treat expired locks as directly reusable; recover the owning run before
  releasing persisted locks.

## Confirmed Items

- V1 uses one default workspace.
- Normal users can delete their own non-running tasks.
- MVP includes minimal audit log for security-sensitive administrator actions.
- Profile keys use `{workspace_id}/{platform}/acc_{account_id}`.
- Account/profile locks use inline fields; proxy concurrency uses
  `resource_locks`.
- Administrator task timeout is a run-level wall-clock deadline and is not
  estimated from crawl range.
