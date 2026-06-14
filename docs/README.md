# Project Documents

This directory contains the working documents for Legal Sentiment Monitor.

Recommended reading order for contributors and coding agents:

1. `GOAL.md` - product goal, scope, and non-goals.
2. `CURRENT_STATE.md` - current project state and next step.
3. `TASKS.md` - implementation checklist.
4. `DECISIONS.md` - append-only product and technical decisions.
5. `CHANGE_REQUESTS.md` - requirement intake and status.
6. `TRACEABILITY.md` - requirement, task, and test mapping.
7. `PRODUCT_REQUIREMENTS.md` - menu and page-level product behavior.
8. `ROLES_AND_PERMISSIONS.md` - role, menu, action, API, and data-scope rules.
9. `API_AUTHENTICATION.md` - session auth, API authorization, and data scope.
10. `ACCOUNT_ENVIRONMENT.md` - account, profile, proxy, login, and browser rules.
11. `SYSTEM_SETTINGS.md` - runtime setting and configuration rules.
12. `DATA_MODEL.md` - target schema and migration planning.
13. `PERMISSIONS_CONFIRMATION.md` - user confirmation items for Phase 1.
14. `SCHEMA_MIGRATION.md` - compatible schema migration plan.
15. `SERVER_DEPLOYMENT.md` - server/container deployment and validation rules.
16. `DOCUMENTATION_CHECKS.md` - future documentation consistency check spec.
17. `UI_UX_GUIDELINES.md` - UI and interaction rules.
18. `AGENT_WORKFLOW.md` - how agents read and update documents.
19. `TEST_PLAN.md` - acceptance and regression test plan.
20. `TEST_RESULTS.md` - latest verification notes.

Existing crawler-origin documents remain in this directory for reference, but
the files above are the active project governance documents for the monitoring
system.

When product behavior changes, update `PRODUCT_REQUIREMENTS.md`. When a new
requirement is accepted, add it to `CHANGE_REQUESTS.md`. When implementation is
completed, update `TASKS.md`, `CURRENT_STATE.md`, and `TEST_RESULTS.md`.
