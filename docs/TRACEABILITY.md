# Traceability Matrix

Use this file to connect requirements, tasks, code areas, and tests.

| Requirement | Module | Task Area | Code Area | Test Area | Status |
| --- | --- | --- | --- | --- | --- |
| CR-001 | Project governance | Phase 0 | docs, AGENTS.md | Documentation review | Verified |
| CR-002 | Product requirements | Phase 0 | docs/PRODUCT_REQUIREMENTS.md | Documentation review | Implemented |
| CR-003 | Agent workflow | Phase 0 | docs, AGENTS.md | Documentation review | Implemented |
| CR-004 | Agent confirmation gate | Phase 0 | AGENTS.md, docs/AGENT_WORKFLOW.md | Documentation review | Implemented |

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
