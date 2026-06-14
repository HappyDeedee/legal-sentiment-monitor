# Permissions Confirmation

This document gathers high-impact permission and workspace decisions that need
user confirmation before Phase 1 implementation.

Status values:

- Recommended: proposed default for V1.
- Alternative: valid option with tradeoffs.
- Needs Confirmation: do not implement until user confirms.

## C-001 - Workspace Strategy

Question:

- Should V1 be single-workspace multi-user, or should multiple workspaces be
  visible and manageable in the first release?

Recommended:

- V1 uses one default workspace.
- Add `workspace_id` to business tables now.
- Hide workspace management UI in V1.

Reason:

- This matches the first-version single-server ToB pilot boundary.
- It keeps future multi-workspace migration possible without adding tenant UI
  now.

Alternative:

- Add visible multi-workspace management in V1.

Tradeoff:

- More complete SaaS foundation, but increases Phase 1 complexity.

Status: Needs Confirmation

## C-002 - Normal User Task Deletion

Question:

- Can normal users delete their own tasks, or only pause them?

Recommended:

- Normal users can delete their own non-running tasks.
- Running tasks must be stopped before deletion.
- Historical runs and reports remain visible as task history.

Alternative:

- Normal users can only pause tasks; administrators delete tasks.

Status: Needs Confirmation

## C-003 - Normal User Report Resend

Question:

- Can normal users resend report emails for their own reports?

Recommended:

- Normal users can resend own reports if email configuration is available.
- Administrators can resend all workspace reports.
- Resend actions should be logged.

Alternative:

- Only administrators can resend emails.

Status: Needs Confirmation

## C-004 - Initial Administrator Creation

Question:

- How should the first administrator be created?

Recommended:

- Environment bootstrap:
  - `MONITOR_ADMIN_EMAIL`
  - `MONITOR_ADMIN_PASSWORD`
- On startup, if no administrator exists, create one from these values.

Reason:

- Works well in server/container deployment.
- Avoids a public first-run setup screen.

Alternative:

- First-run web setup page.

Tradeoff:

- Easier for non-technical users, but riskier if exposed publicly before setup.

Status: Needs Confirmation

## C-005 - Authentication Strategy

Question:

- Should V1 use session-based auth or token/JWT auth?

Recommended:

- Session-based auth with secure HTTP-only cookie.
- Store sessions in database or signed server-side session storage.

Reason:

- Simpler for a server-rendered/admin-style web console.
- Fits low-concurrency single-server V1.

Alternative:

- JWT-based auth.

Tradeoff:

- Better for external API clients, but adds token lifecycle complexity.

Status: Needs Confirmation

## C-006 - Disabled User Task Behavior

Question:

- What happens to scheduled tasks created by a disabled user?

Recommended:

- Disable login immediately.
- Existing enabled tasks continue under workspace ownership.
- Administrators can pause, transfer, or delete them.

Alternative:

- Automatically pause all tasks owned by the disabled user.

Status: Needs Confirmation

## C-007 - Audit Log Timing

Question:

- Should audit logs be included in MVP or Phase 9?

Recommended:

- Add minimal audit log in MVP for administrator security-sensitive actions:
  - user create/disable;
  - account create/delete/login;
  - proxy create/delete;
  - AI/mail setting updates;
  - runtime setting updates.

Alternative:

- Defer full audit log to Phase 9.

Status: Needs Confirmation

