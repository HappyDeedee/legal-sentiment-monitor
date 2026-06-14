# Legal Sentiment Monitor Agent Guide

This file is the entry point for coding agents working on this repository.
Always treat the project documents as the source of truth. Do not rely on chat
history alone.

## Required Reading

Before changing code or UI, read these files in order:

1. `docs/GOAL.md`
2. `docs/CURRENT_STATE.md`
3. `docs/TASKS.md`
4. `docs/DECISIONS.md`
5. `docs/CHANGE_REQUESTS.md`
6. `docs/TRACEABILITY.md`
7. `docs/TEST_PLAN.md`

Read the relevant specialist document before touching a related area:

- UI changes: `docs/UI_UX_GUIDELINES.md`
- Product/page behavior: `docs/PRODUCT_REQUIREMENTS.md`
- Role or permission changes: `docs/ROLES_AND_PERMISSIONS.md`
- API authentication or authorization changes: `docs/API_AUTHENTICATION.md`
- Permission decisions awaiting user confirmation:
  `docs/PERMISSIONS_CONFIRMATION.md`
- Account, profile, proxy, or login changes: `docs/ACCOUNT_ENVIRONMENT.md`
- Data model changes: `docs/DATA_MODEL.md`
- Schema migration changes: `docs/SCHEMA_MIGRATION.md`
- Server deployment or browser login changes: `docs/SERVER_DEPLOYMENT.md` and
  `docs/TEST_PLAN.md`
- System setting changes: `docs/SYSTEM_SETTINGS.md`
- Agent process details: `docs/AGENT_WORKFLOW.md`

Before Phase 1 implementation, complete the Phase 0.5 schema foundation in
`docs/TASKS.md` and `docs/SCHEMA_MIGRATION.md`.

If documents conflict, use this order:

1. `docs/DECISIONS.md`
2. relevant specialist documents
3. `docs/CURRENT_STATE.md`
4. `docs/TASKS.md`
5. general product or workflow documents

## Product Boundary

The first version is a single-server, low-concurrency ToB public-opinion
monitoring system for law-firm monitoring operations.

The administrator maintains resources:

- platform account pool
- proxy IP pool
- AI access profiles
- email and templates
- runtime strategy
- users and permissions

The normal user only creates monitoring tasks:

- target law firm
- platforms to crawl
- platform search terms
- task frequency
- report recipient emails

## Non Goals For V1

Do not implement these in the first version unless the product plan changes:

- complex account rotation
- captcha or SMS bypass
- dynamic proxy scheduling
- high-concurrency crawling cluster
- public self-service SaaS onboarding
- billing
- field-level permission model

## Server-First Rule

Production validation must use a server-like environment. A local Chrome window
on the operator's computer is not an acceptance path.

The production login flow is:

1. the server starts a browser session,
2. the web UI shows the QR code or status,
3. the operator scans in the web UI,
4. the server persists the account profile,
5. later tasks reuse the server-side profile.

Local browser window login can exist only as a development fallback and must not
be required for production use.

## Documentation Update Rule

After each meaningful change, update:

- `docs/TASKS.md`
- `docs/CURRENT_STATE.md`
- `docs/TEST_RESULTS.md`
- `docs/TRACEABILITY.md` when requirements, tasks, or tests are added

If a new product or technical decision is made, append it to:

- `docs/DECISIONS.md`

If the user raises a new requirement, first record it in:

- `docs/CHANGE_REQUESTS.md`

Then connect it to tasks and tests before or during implementation. Meaningful
new requirements should not exist only in chat history.

If a requirement is ambiguous or requires a product, permission, security,
deployment, account-environment, or data-model decision, ask the user for
confirmation before treating it as accepted. Draft assumptions may be recorded,
but they must be marked as proposed or needing confirmation.

A task is not complete until code, verification, and documentation state agree.

## Sensitive Data Rule

Never commit real secrets or runtime data:

- API keys
- SMTP passwords
- proxy URLs with credentials
- cookies
- QR login session data
- account profiles
- local databases
- local `.env` or deployment-only `monitor.yaml`

Commit examples only, such as `.env.example` and `monitor.example.yaml`.
