# Change Requests

Record every meaningful new requirement here before implementation.

Status values:

- Proposed
- Needs Confirmation
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

## CR-005 - P0 Implementation Specification Documents

Date: 2026-06-14

Source: external documentation review

Module: project governance

Requirement:

Create P0 specialist documents for roles and permissions, account environment,
system settings, and data model so coding agents do not need to guess critical
implementation details.

Reason:

The review found that the project governance loop exists, but implementation
specifications for Phase 1, Phase 2, and Phase 5 were missing or too high-level.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 1 in `TASKS.md`
- Phase 2 in `TASKS.md`
- Phase 5 in `TASKS.md`

Acceptance:

- `ROLES_AND_PERMISSIONS.md` exists;
- `ACCOUNT_ENVIRONMENT.md` exists;
- `SYSTEM_SETTINGS.md` exists;
- `DATA_MODEL.md` exists;
- open assumptions are marked as needing user confirmation.

## CR-006 - User And Workspace Permission Design

Date: 2026-06-14

Source: external documentation review

Module: users and permissions

Requirement:

Define role permissions, workspace data scope, menu visibility, API access
policy, and user lifecycle before implementing Phase 1.

Reason:

Without this, Phase 1 requires guessing user, role, and workspace behavior.

Status: Needs Confirmation

Related tasks:

- Phase 1 in `TASKS.md`

Acceptance:

- user confirms V1 workspace strategy;
- user confirms initial administrator creation flow;
- user confirms disabled-user task behavior.

## CR-007 - Account Environment And Profile Design

Date: 2026-06-14

Source: external documentation review

Module: account environment

Requirement:

Define platform account, profile, proxy, browser session, login session, lock,
and migration behavior before implementing Phase 5 and Phase 6.

Reason:

The current code still has legacy `profile_path` concepts, while product
decisions require stable `profile_key` and hidden real paths.

Status: Needs Confirmation

Related tasks:

- Phase 5 in `TASKS.md`
- Phase 6 in `TASKS.md`

Acceptance:

- user confirms profile key format;
- user confirms lock timeout behavior;
- user confirms legacy profile migration approach.

## CR-008 - Runtime Settings Specification

Date: 2026-06-14

Source: external documentation review

Module: system settings

Requirement:

Define runtime settings, configuration precedence, editable fields, locked
fields, validation ranges, and config-file shape before implementing Phase 2.

Reason:

Runtime settings are currently spread across code defaults and environment
variables.

Status: Needs Confirmation

Related tasks:

- Phase 2 in `TASKS.md`

Acceptance:

- user confirms configuration precedence;
- user confirms flexible key-value vs typed settings table;
- user confirms whether audit logs are required in MVP.

## CR-009 - Permission Confirmation Pack

Date: 2026-06-14

Source: external documentation review

Module: users and permissions

Requirement:

Gather Phase 1 blocking permission, workspace, initial administrator, auth, and
disabled-user behavior questions into a single confirmation document with
recommended and alternative options.

Reason:

Phase 1 cannot start safely until high-impact permission decisions are
confirmed.

Status: Implemented

Related tasks:

- Phase 1 in `TASKS.md`

Acceptance:

- `PERMISSIONS_CONFIRMATION.md` exists;
- every blocking item has a recommended option and alternative;
- status is clearly marked as Needs Confirmation.

## CR-010 - Compatible Schema Migration Plan

Date: 2026-06-14

Source: external documentation review

Module: data model

Requirement:

Create a compatible schema migration plan before user, workspace, profile_key,
system settings, and lock fields are implemented.

Reason:

The target data model is ahead of the current schema. A migration plan is needed
to avoid breaking existing monitoring data and account profiles.

Status: Implemented

Related tasks:

- Phase 1 in `TASKS.md`
- Phase 5 in `TASKS.md`

Acceptance:

- `SCHEMA_MIGRATION.md` exists;
- migration steps add fields before removing legacy fields;
- legacy `profile_path` compatibility is documented.

## CR-011 - Runtime Config Example

Date: 2026-06-14

Source: external documentation review

Module: system settings

Requirement:

Add a committed `monitor.example.yaml` that documents the intended runtime
configuration shape without real secrets.

Reason:

Phase 2 needs a concrete configuration example and deployment operators need a
safe starting point.

Status: Implemented

Related tasks:

- Phase 0 in `TASKS.md`
- Phase 2 in `TASKS.md`

Acceptance:

- `monitor.example.yaml` exists;
- the file contains runtime, platform, login, scheduler, and retention examples;
- deployment-only values remain environment-variable based.
