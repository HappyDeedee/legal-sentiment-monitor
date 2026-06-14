# Permissions Confirmation

This document gathers high-impact permission and workspace decisions that need
user confirmation before Phase 1 implementation.

Status values:

- Recommended: proposed default for V1.
- Alternative: valid option with tradeoffs.
- Needs Confirmation: do not implement until user confirms.
- Accepted: user has confirmed the option.

## C-001 - Workspace Strategy

Question:

- Should V1 be single-workspace multi-user, or should multiple workspaces be
  visible and manageable in the first release?

Explanation:

- A workspace is the organization-level data boundary.
- Single-workspace V1 means the system has one hidden default workspace.
- Administrators manage all resources in this workspace.
- Normal users belong to the same workspace but still only see what their role
  allows, such as their own tasks and reports.
- Platform accounts, proxies, AI access, email settings, and runtime strategy
  are shared administrator-managed resources inside this workspace.
- This does not mean every normal user can see administrator resources.

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

Confirmed:

- Use the recommended single-workspace V1 strategy.

Status: Accepted

## C-002 - Normal User Task Deletion

Question:

- Can normal users delete their own tasks, or only pause them?

Recommended:

- Normal users can delete their own non-running tasks.
- Running tasks must be stopped before deletion.
- Historical runs and reports remain visible as task history.

Alternative:

- Normal users can only pause tasks; administrators delete tasks.

Confirmed:

- Normal users can delete their own non-running tasks.
- Running tasks must be stopped before deletion.
- Historical runs and reports remain visible.

Status: Accepted

## C-003 - Normal User Report Resend

Question:

- Can normal users resend report emails for their own reports?

Recommended:

- Normal users can resend own reports if email configuration is available.
- Administrators can resend all workspace reports.
- Resend actions should be logged.

Alternative:

- Only administrators can resend emails.

Confirmed:

- Normal users can resend their own reports when email configuration is
  available.
- Administrators can resend all workspace reports.
- Resend actions should be logged.

Status: Accepted

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

Confirmed:

- Use environment bootstrap with `MONITOR_ADMIN_EMAIL` and
  `MONITOR_ADMIN_PASSWORD`.

Status: Accepted

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

Confirmed:

- Use session-based authentication with secure HTTP-only cookie for V1.

Status: Accepted

## C-006 - Disabled User Task Behavior

Question:

- What happens to scheduled tasks created by a disabled user?

Recommended:

- Disable login immediately.
- Existing enabled tasks continue under workspace ownership.
- Administrators can pause, transfer, or delete them.

Alternative:

- Automatically pause all tasks owned by the disabled user.

Confirmed:

- Disabled users cannot log in.
- Existing enabled tasks continue under workspace ownership.
- Administrators can pause, transfer, or delete them.

Status: Accepted

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

Confirmed:

- Include minimal audit log in MVP for security-sensitive administrator
  actions.

Status: Accepted
