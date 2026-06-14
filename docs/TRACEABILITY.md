# Traceability Matrix

Use this file to connect requirements, tasks, code areas, and tests.

| Requirement | Module | Task Area | Code Area | Test Area | Status |
| --- | --- | --- | --- | --- | --- |
| CR-001 | Project governance | Phase 0 | docs, AGENTS.md | Documentation review | Verified |
| CR-002 | Product requirements | Phase 0 | docs/PRODUCT_REQUIREMENTS.md | Documentation review | Implemented |
| CR-003 | Agent workflow | Phase 0 | docs, AGENTS.md | Documentation review | Implemented |
| CR-004 | Agent confirmation gate | Phase 0 | AGENTS.md, docs/AGENT_WORKFLOW.md | Documentation review | Implemented |
| CR-005 | P0 implementation specifications | Phase 0 | docs/ROLES_AND_PERMISSIONS.md, docs/ACCOUNT_ENVIRONMENT.md, docs/SYSTEM_SETTINGS.md, docs/DATA_MODEL.md | Documentation review | Implemented |
| CR-006 | User and workspace permissions | Phase 1 | docs/ROLES_AND_PERMISSIONS.md, docs/PERMISSIONS_CONFIRMATION.md | Permission tests | Accepted |
| CR-007 | Account environment and profile design | Phase 5, Phase 6 | docs/ACCOUNT_ENVIRONMENT.md, docs/DATA_MODEL.md | Account/login/server tests | Needs Confirmation |
| CR-008 | Runtime settings specification | Phase 2 | docs/SYSTEM_SETTINGS.md | Runtime settings tests | Accepted |
| CR-009 | Permission confirmation pack | Phase 1 | docs/PERMISSIONS_CONFIRMATION.md | Documentation review | Implemented |
| CR-010 | Compatible schema migration plan | Phase 1, Phase 5 | docs/SCHEMA_MIGRATION.md, docs/DATA_MODEL.md | Migration tests | Implemented |
| CR-011 | Runtime config example | Phase 0, Phase 2 | monitor.example.yaml, docs/SYSTEM_SETTINGS.md | Configuration loading tests | Implemented |

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
