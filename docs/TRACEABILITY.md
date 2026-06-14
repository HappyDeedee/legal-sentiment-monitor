# Traceability Matrix

Use this file to connect requirements, tasks, code areas, and tests.

| Requirement | Module | Task Area | Code Area | Test Area | Status |
| --- | --- | --- | --- | --- | --- |
| CR-001 | Project governance | Phase 0 | docs, AGENTS.md | Documentation review | Verified |
| CR-002 | Product requirements | Phase 0 | docs/PRODUCT_REQUIREMENTS.md | Documentation review | Implemented |
| CR-003 | Agent workflow | Phase 0 | docs, AGENTS.md | Documentation review | Implemented |
| CR-004 | Agent confirmation gate | Phase 0 | AGENTS.md, docs/AGENT_WORKFLOW.md | Documentation review | Implemented |
| CR-005 | P0 implementation specifications | Phase 0 | docs/ROLES_AND_PERMISSIONS.md, docs/ACCOUNT_ENVIRONMENT.md, docs/SYSTEM_SETTINGS.md, docs/DATA_MODEL.md | Documentation review | Implemented |
| CR-006 | User and workspace permissions | Phase 1 after Phase 0.5 | docs/ROLES_AND_PERMISSIONS.md, docs/PERMISSIONS_CONFIRMATION.md | Permission tests | Accepted; Phase 0.5 not yet implemented, so Phase 1 is blocked until schema foundation exists |
| CR-007 | Account environment and profile migration direction | Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/DATA_MODEL.md | Account/login/server tests | Accepted |
| CR-008 | Runtime settings specification | Phase 2 | docs/SYSTEM_SETTINGS.md | Runtime settings tests | Accepted |
| CR-009 | Permission confirmation pack | Phase 1 | docs/PERMISSIONS_CONFIRMATION.md | Documentation review | Implemented |
| CR-010 | Compatible schema migration plan | Phase 0.5, Phase 1, Phase 5 | docs/SCHEMA_MIGRATION.md, docs/DATA_MODEL.md | Migration tests | Implemented |
| CR-011 | Runtime config example | Phase 0, Phase 2 | monitor.example.yaml, docs/SYSTEM_SETTINGS.md | Configuration loading tests | Implemented |
| CR-012A | Account environment profile key format | Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md | Profile resolver tests | Accepted |
| CR-012B | Account and profile lock timeout | Phase 2, Phase 5, Phase 6, Phase 7 | docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md, docs/SYSTEM_SETTINGS.md | Run timeout and stale-lock recovery tests | Accepted |
| CR-012C | Account/profile/proxy lock storage | Phase 0.5, Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/SCHEMA_MIGRATION.md | Account/profile/proxy lock tests | Accepted |
| CR-013 | API authentication implementation guide | Phase 1 | docs/API_AUTHENTICATION.md, docs/ROLES_AND_PERMISSIONS.md | Auth and permission tests | Implemented |
| CR-014 | Server deployment guide | Phase 8 | docs/SERVER_DEPLOYMENT.md, docs/TEST_PLAN.md | Server-like acceptance tests | Implemented |
| CR-015 | Documentation consistency check specification | Phase 0 | docs/DOCUMENTATION_CHECKS.md, docs/AGENT_WORKFLOW.md | Documentation review | Implemented |
| CR-016 | Phase 0.5 and code-state documentation hardening | Phase 0, Phase 0.5 | docs/CURRENT_STATE.md, docs/TASKS.md, docs/TEST_PLAN.md, docs/DATA_MODEL.md, docs/AGENT_WORKFLOW.md | Documentation review, migration tests | Implemented |
| CR-017 | Runtime Strategy page layout detail | Phase 2 | docs/PRODUCT_REQUIREMENTS.md, docs/UI_UX_GUIDELINES.md | Runtime settings UI tests | Accepted |
| CR-018 | Crawl range capability boundaries | Phase 4, Phase 7 | docs/PRODUCT_REQUIREMENTS.md, docs/TEST_PLAN.md | Crawl range validation and timeout tests | Accepted |

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
