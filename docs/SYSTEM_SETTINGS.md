# System Settings

This document defines runtime settings, configuration precedence, editable
fields, locked fields, and validation rules.

## Configuration Precedence

Effective configuration is built in this order:

1. code defaults;
2. `monitor.yaml`;
3. database runtime settings;
4. environment variable locks.

Environment locks override UI and database values. When a value is locked by
deployment configuration, the UI should show it as read-only.

Confirmed V1 direction:

- environment variables lock deployment-level or explicitly locked values;
- ordinary runtime values can be edited through the database-backed
  administrator UI unless locked by deployment configuration.

## Editable Runtime Settings

| Setting | Type | Default | Range | Apply |
| --- | --- | --- | --- | --- |
| global_crawl_concurrency | integer | 2 | 1-16 | immediate |
| per_platform_concurrency.dy | integer | 1 | 1-8 | immediate |
| per_platform_concurrency.xhs | integer | 1 | 1-8 | immediate |
| per_platform_concurrency.ks | integer | 1 | 1-8 | immediate |
| crawler_timeout_seconds | integer | 900 | 60-21600 | next run |
| lock_cleanup_buffer_seconds | integer | 300 | 60-3600 | next run |
| crawler_retry_count | integer | 1 | 0-5 | next run |
| crawler_retry_delay_seconds | integer | 3 | 0-300 | next run |
| login_qr_timeout_seconds | integer | 20 | 5-300 | next session |
| login_session_ttl_seconds | integer | 600 | 60-3600 | next session |
| scheduler_tick_seconds | integer | 60 | 10-600 | restart or scheduler reload |
| scheduler_disabled | boolean | false | true/false | restart or scheduler reload |
| run_log_retention_days | integer | 90 | 1-3650 | cleanup job |
| report_retention_days | integer | 180 | 1-3650 | cleanup job |

Single-account and single-profile concurrency are fixed safety rules and should
not be editable in V1.

## Task Timeout And Lock Recovery

`crawler_timeout_seconds` is the administrator-controlled run-level wall-clock
deadline for a newly started crawl run. It is not computed from crawl range.

Rules:

- copy the effective timeout into `crawl_runs.timeout_seconds` when the run
  starts;
- compute `crawl_runs.deadline_at = started_at + timeout_seconds`;
- platform crawler subprocesses should use the remaining run time rather than
  each receiving a full independent timeout budget;
- before retrying or starting another platform, check whether the run deadline
  has already passed;
- when the run deadline is exceeded, stop active crawler processes, set run
  status to `timeout`, keep already collected partial results, and release
  locks through recovery.

Example:

```text
crawler_timeout_seconds = 900
run starts at 10:00:00
deadline_at = 10:15:00

Platform A starts at 10:01:40 -> subprocess timeout must be at most 800 seconds.
Platform B starts at 10:08:20 -> subprocess timeout must be at most 400 seconds.
At 10:15:00, any unfinished crawler process is stopped and the run is marked
timeout.
```

This intentionally differs from the current MVP subprocess-level timeout. Phase
2 implementation should migrate timeout handling from "each crawler attempt gets
the full timeout" to "each crawler attempt gets only the remaining run time."

`lock_cleanup_buffer_seconds` is added after the run deadline when calculating
account/profile/proxy lock expiry:

```text
lock_expires_at = crawl_runs.deadline_at + lock_cleanup_buffer_seconds
```

Expired locks are recovery signals only. A new run must not directly reuse an
expired lock before recovery verifies the owning run state.

## Read-Only Or Deployment-Locked Settings

| Setting | Reason |
| --- | --- |
| data_dir | changing can move database and profiles |
| account_profile_root | changing can break login persistence |
| database_url | deployment-level infrastructure |
| encryption_key_path | security-sensitive |
| browser_executable_path | deployment/runtime concern |
| service_port | process manager concern |
| cors_origins | deployment/security concern |
| worker_count | scheduler duplication risk |

## Database Storage

Confirmed V1 direction:

- use a flexible key-value `system_settings` table.

Target table:

```text
system_settings
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

Strongly typed runtime settings can be reconsidered later if the settings model
stabilizes and needs stricter schema enforcement.

## monitor.yaml Shape

`monitor.example.yaml` is the committed safe example. Real deployments may copy
it to `monitor.yaml`, but must not commit deployment-specific values or secrets.

Example shape:

```yaml
runtime:
  global_crawl_concurrency: 2
  crawler_timeout_seconds: 900
  lock_cleanup_buffer_seconds: 300
  crawler_retry_count: 1
  crawler_retry_delay_seconds: 3

platforms:
  dy:
    max_concurrency: 1
  xhs:
    max_concurrency: 1
  ks:
    max_concurrency: 1

login:
  qr_timeout_seconds: 20
  session_ttl_seconds: 600

scheduler:
  tick_seconds: 60
  disabled: false

retention:
  run_log_days: 90
  report_days: 180
```

The database keys should use stable snake_case names such as
`scheduler_tick_seconds` and `scheduler_disabled`; the YAML file may use nested
sections for operator readability.

YAML-to-database key mapping:

| YAML Path | Database Key |
| --- | --- |
| runtime.global_crawl_concurrency | global_crawl_concurrency |
| runtime.crawler_timeout_seconds | crawler_timeout_seconds |
| runtime.lock_cleanup_buffer_seconds | lock_cleanup_buffer_seconds |
| runtime.crawler_retry_count | crawler_retry_count |
| runtime.crawler_retry_delay_seconds | crawler_retry_delay_seconds |
| platforms.dy.max_concurrency | per_platform_concurrency.dy |
| platforms.xhs.max_concurrency | per_platform_concurrency.xhs |
| platforms.ks.max_concurrency | per_platform_concurrency.ks |
| login.qr_timeout_seconds | login_qr_timeout_seconds |
| login.session_ttl_seconds | login_session_ttl_seconds |
| scheduler.tick_seconds | scheduler_tick_seconds |
| scheduler.disabled | scheduler_disabled |
| retention.run_log_days | run_log_retention_days |
| retention.report_days | report_retention_days |

Do not commit real secrets in `monitor.yaml`; commit only `monitor.example.yaml`.

## Audit

Runtime setting changes should be auditable in production.

Confirmed V1 direction:

- include minimal audit logging in MVP for security-sensitive administrator
  actions, including runtime setting changes.
