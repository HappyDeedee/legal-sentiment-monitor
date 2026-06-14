# Change Requests

Record every meaningful new requirement here before implementation.

Status values:

- Proposed
- Accepted
- In Progress
- Implemented
- Verified
- Deferred
- Rejected

## CR-001 - Documentation Governance Bootstrap

Date: 2026-06-14

Source: user conversation

Module: project governance

Requirement:

Create a Git-tracked documentation system that lets coding agents understand
project goals, update progress, record decisions, and validate changes without
relying on chat history.

Reason:

The project scope is expanding from a crawler wrapper into a server-deployed
ToB monitoring system. Development needs persistent project context.

Status: Verified

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `AGENTS.md` exists;
- goal, tasks, current state, decisions, UI/UX, and test documents exist;
- documents are committed to Git.

## CR-002 - Full Menu Product Coverage

Date: 2026-06-14

Source: user conversation

Module: product requirements

Requirement:

Document every active menu item and page, not only the features discussed in
chat.

Reason:

Future coding agents need complete page-level logic and acceptance criteria.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `PRODUCT_REQUIREMENTS.md` covers overview, monitoring, run center, report
  center, resource management, and system configuration.

## CR-003 - Requirement Intake And Documentation Loop

Date: 2026-06-14

Source: user conversation

Module: agent workflow

Requirement:

When the user raises a new requirement, agents must record it in project
documents, connect it to tasks and tests, and update progress after
implementation.

Reason:

Requirements should not exist only in chat. The project needs a closed-loop
documentation mechanism.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `CHANGE_REQUESTS.md` exists;
- `TRACEABILITY.md` exists;
- `AGENT_WORKFLOW.md` defines when to update documents;
- `AGENTS.md` references the workflow.

## CR-004 - Confirmation Gate For Ambiguous Requirements

Date: 2026-06-14

Source: user conversation

Module: agent workflow

Requirement:

Agents must confirm with the user before turning ambiguous assumptions into
accepted product, permission, deployment, account-environment, security, or
data-model requirements.

Reason:

The project is now governed by documents. Incorrect assumptions in documents can
mislead future coding agents and create product or architecture drift.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`

Acceptance:

- `AGENT_WORKFLOW.md` contains a confirmation gate;
- `AGENTS.md` tells agents to ask before accepting ambiguous high-impact
  requirements;
- assumptions can be drafted only when marked as proposed or needing
  confirmation.
