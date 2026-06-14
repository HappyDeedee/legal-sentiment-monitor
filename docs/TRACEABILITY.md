# Traceability Matrix

Use this file to connect requirements, tasks, code areas, and tests.

| Requirement | Module | Task Area | Code Area | Test Area | Status |
| --- | --- | --- | --- | --- | --- |
| CR-001 | Project governance | Phase 0 | docs, AGENTS.md | Documentation review | Verified |
| CR-002 | Product requirements | Phase 0 | docs/PRODUCT_REQUIREMENTS.md | Documentation review | Implemented |
| CR-003 | Agent workflow | Phase 0 | docs, AGENTS.md | Documentation review | Implemented |
| CR-004 | Agent confirmation gate | Phase 0 | AGENTS.md, docs/AGENT_WORKFLOW.md | Documentation review | Implemented |
| CR-005 | P0 implementation specifications | Phase 0 | docs/ROLES_AND_PERMISSIONS.md, docs/ACCOUNT_ENVIRONMENT.md, docs/SYSTEM_SETTINGS.md, docs/DATA_MODEL.md | Documentation review | Implemented |
| CR-006 | User and workspace permissions | Phase 1 | api/monitoring/auth.py, api/monitoring/auth_context.py, api/monitoring/database.py, api/routers/auth.py, api/routers/monitor.py, api/monitor_web/index.html | tests/test_monitoring_mvp.py::test_phase_1_bootstrap_admin_login_session_and_user_management, tests/test_monitoring_mvp.py::test_phase_1_http_routes_enforce_sessions_roles_and_owner_scope | Verified |
| CR-007 | Account environment and profile migration direction | Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/DATA_MODEL.md | Account/login/server tests | Accepted |
| CR-008 | Runtime settings specification | Phase 2 | api/monitoring/settings.py, api/monitoring/database.py, api/routers/monitor.py, api/monitor_web/index.html, docs/SYSTEM_SETTINGS.md | tests/test_monitoring_mvp.py::test_phase_2_runtime_settings_storage_validation_and_environment_locks, tests/test_monitoring_mvp.py::test_phase_2_runtime_settings_api_is_admin_only, tests/test_monitoring_mvp.py::test_phase_2_scheduler_uses_runtime_settings, tests/test_monitoring_mvp.py::test_phase_2_qrcode_timeout_and_ttl_use_runtime_settings | Verified |
| CR-009 | Permission confirmation pack | Phase 1 | docs/PERMISSIONS_CONFIRMATION.md | Documentation review | Implemented |
| CR-010 | Compatible schema migration plan | Phase 0.5, Phase 1, Phase 5 | api/monitoring/database.py, docs/SCHEMA_MIGRATION.md, docs/DATA_MODEL.md | tests/test_monitoring_mvp.py::test_phase_05_schema_foundation_tables_and_columns_exist, tests/test_monitoring_mvp.py::test_phase_05_schema_defaults_keep_existing_mvp_records_compatible | Verified for Phase 0.5 schema foundation |
| CR-011 | Runtime config example | Phase 0, Phase 2 | monitor.example.yaml, .env.example, deploy/systemd/legal-sentiment-monitor.env.example, api/monitoring/settings.py, docs/SYSTEM_SETTINGS.md | tests/test_monitoring_mvp.py::test_phase_2_runtime_settings_storage_validation_and_environment_locks | Verified |
| CR-012A | Account environment profile key format | Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md | Profile resolver tests | Accepted |
| CR-012B | Account and profile lock timeout | Phase 2, Phase 5, Phase 6, Phase 7 | api/monitoring/runner.py, api/monitoring/database.py, docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md, docs/SYSTEM_SETTINGS.md | tests/test_monitoring_mvp.py::test_phase_2_run_platform_uses_settings_for_retry_and_deadline, tests/test_monitoring_mvp.py::test_phase_2_run_job_marks_run_timeout_with_partial_results | Phase 2 run-level timeout verified; stale-lock recovery remains for Phase 5/6 |
| CR-012C | Account/profile/proxy lock storage | Phase 0.5, Phase 5, Phase 6 | api/monitoring/database.py, docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md | tests/test_monitoring_mvp.py::test_phase_05_schema_foundation_tables_and_columns_exist | Phase 0.5 lock schema verified; runtime lock behavior remains for Phase 5/6 |
| CR-013 | API authentication implementation guide | Phase 1 | api/monitoring/auth.py, api/monitoring/auth_context.py, api/routers/auth.py, api/routers/monitor.py | tests/test_monitoring_mvp.py::test_phase_1_bootstrap_admin_login_session_and_user_management, tests/test_monitoring_mvp.py::test_phase_1_http_routes_enforce_sessions_roles_and_owner_scope | Verified |
| CR-014 | Server deployment guide | Phase 8 | docs/SERVER_DEPLOYMENT.md, docs/TEST_PLAN.md | Server-like acceptance tests | Implemented |
| CR-015 | Documentation consistency check specification | Phase 0, Phase 1 | docs/DOCUMENTATION_CHECKS.md, scripts/check_docs.py | `uv run python scripts/check_docs.py` | Verified |
| CR-016 | Phase 0.5 and code-state documentation hardening | Phase 0, Phase 0.5 | docs/CURRENT_STATE.md, docs/TASKS.md, docs/TEST_PLAN.md, docs/DATA_MODEL.md, docs/AGENT_WORKFLOW.md | Documentation review, migration tests | Implemented |
| CR-017 | Runtime Strategy page layout detail | Phase 2 | api/monitor_web/index.html, docs/PRODUCT_REQUIREMENTS.md, docs/UI_UX_GUIDELINES.md | tests/test_monitoring_mvp.py::test_phase_2_runtime_settings_api_is_admin_only, Node script parse check for api/monitor_web/index.html | Verified |
| CR-018 | Crawl range capability boundaries | Phase 4, Phase 7 | api/monitor_web/index.html, docs/PRODUCT_REQUIREMENTS.md, docs/TEST_PLAN.md | tests/test_monitoring_mvp.py::test_monitor_page_uses_tob_information_architecture_without_customer_facing_engine_traces | Verified for Phase 4 UI copy; Phase 7 runtime/report behavior remains |
| PR-RESOURCE-001 | Administrator resource center | Phase 3 | api/monitor_web/index.html, tests/test_monitoring_mvp.py | tests/test_monitoring_mvp.py::test_monitor_page_uses_tob_information_architecture_without_customer_facing_engine_traces, tests/test_monitoring_mvp.py::test_monitor_page_uses_consistent_buttons_tables_and_modal_actions, Node script parse check for api/monitor_web/index.html | Verified |
| PR-TASK-001 | Normal user task wizard | Phase 4 | api/routers/monitor.py, api/monitor_web/index.html, tests/test_monitoring_mvp.py | tests/test_monitoring_mvp.py::test_phase_4_normal_user_task_api_ignores_advanced_resource_fields, tests/test_monitoring_mvp.py::test_monitor_page_uses_tob_information_architecture_without_customer_facing_engine_traces, Node script parse check for api/monitor_web/index.html | Verified |

## Rules

- Every accepted change request should map to at least one task.
- Every implemented change request should map to at least one verification
  area.
- If a requirement changes product boundaries, add the decision to
  `DECISIONS.md`.
- If a requirement changes UI behavior, update `UI_UX_GUIDELINES.md` or
  `PRODUCT_REQUIREMENTS.md`.
- If a requirement changes server behavior, update `SERVER_DEPLOYMENT.md` when
  that document exists.
