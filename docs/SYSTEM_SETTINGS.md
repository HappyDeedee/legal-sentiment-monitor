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

Do not commit real secrets in `monitor.yaml`; commit only `monitor.example.yaml`.

## Audit

Runtime setting changes should be auditable in production.

Confirmed V1 direction:

- include minimal audit logging in MVP for security-sensitive administrator
  actions, including runtime setting changes.
