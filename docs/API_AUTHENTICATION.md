# API Authentication And Authorization

This document defines the V1 authentication and authorization implementation
contract for the Legal Sentiment Monitor web/API layer.

## Confirmed V1 Decisions

- V1 uses session-based authentication, not JWT.
- Browser sessions use a secure HTTP-only cookie.
- The initial administrator is bootstrapped from deployment environment
  variables.
- V1 uses one hidden default workspace.
- Normal users can access their own monitoring tasks, runs, and reports.
- Administrators can manage all resources in the default workspace.
- Minimal audit logging is required for security-sensitive administrator
  actions.

## Bootstrap Administrator

On startup:

1. check whether any active administrator exists;
2. if none exists, read `MONITOR_ADMIN_EMAIL` and `MONITOR_ADMIN_PASSWORD`;
3. create the first administrator with a hashed password;
4. do not log the plaintext bootstrap password.

If no administrator exists and the bootstrap variables are missing, the service
should start in a guarded state and return an actionable administrator-only
setup error, not expose a public first-run setup page.

## Session Storage

Use the `user_sessions` table from `DATA_MODEL.md`.

Required behavior:

- store only a session token hash in the database;
- set the browser cookie to the raw random session token;
- rotate the session token on login;
- update `last_active_at` on authenticated API activity;
- expire sessions based on `login_session_ttl_seconds` or the dedicated auth
  session TTL if introduced later;
- delete or mark the session inactive on logout.

Recommended cookie settings:

```text
name = monitor_session
httpOnly = true
secure = true in production
sameSite = lax
path = /
```

Local development may allow `secure = false`; server-like acceptance should use
the production cookie behavior where HTTPS is available.

## API Endpoints

Minimum V1 endpoints:

| Endpoint | Method | Roles | Notes |
| --- | --- | --- | --- |
| `/api/auth/login` | POST | anonymous | email/password login |
| `/api/auth/logout` | POST | authenticated | invalidate current session |
| `/api/auth/session` | GET | authenticated | return current user, role, and menu permissions |
| `/api/users` | GET/POST | administrator | manage users |
| `/api/users/{id}` | PATCH | administrator | disable, update role, reset password |

Responses from `/api/auth/session` should include:

```text
user_id
email
display_name
role
workspace_id
menu_permissions
```

Do not return password hashes, session tokens, cookies, profile paths, API keys,
SMTP passwords, proxy credentials, or deployment paths.

## Authorization Dependencies

Every protected endpoint should use shared authorization helpers rather than
inline role checks.

Required helpers:

- get current session from cookie;
- load active user;
- reject missing or expired sessions with 401;
- reject disabled users with 401;
- require one or more roles;
- apply normal-user data scope filters.

Preferred FastAPI shape:

```text
current_user = Depends(require_authenticated_user)
admin_user = Depends(require_role("administrator"))
```

## Data Scope Rules

Administrator:

- can read and manage all data in the default workspace;
- can access platform accounts, proxies, AI access, mail settings, runtime
  strategy, diagnostics, and user management.

Normal user:

- can create monitoring tasks;
- can read, edit, run, stop, and delete only their own allowed tasks;
- can view runs and reports for their own tasks;
- can resend their own reports when email configuration is available;
- cannot access administrator resource APIs.

Implementation rule:

- filter normal-user task queries by creator/owner;
- filter runs and reports through the owned task relationship;
- never rely only on frontend menu hiding for authorization.

## Error Behavior

Use consistent API responses:

| Case | Status | Behavior |
| --- | --- | --- |
| Missing/expired session | 401 | frontend redirects to login |
| Disabled user | 401 | frontend shows account disabled message |
| Insufficient role | 403 | frontend shows permission-denied page |
| Resource outside user scope | 404 or 403 | prefer 404 when revealing existence is sensitive |

## Audit Requirements

Record minimal audit logs for:

- user create, disable, role change, and password reset;
- platform account create, delete, login, and reset;
- proxy create, delete, and credential update;
- AI/mail/runtime setting updates;
- administrator-triggered report resend.

Audit logs must not contain plaintext secrets.

## Implementation Order

1. Complete Phase 0.5 schema foundation.
2. Add password hashing and bootstrap administrator creation.
3. Add login, logout, and session APIs.
4. Add shared authorization dependencies.
5. Apply API data-scope filters.
6. Update frontend menu rendering from `/api/auth/session`.
7. Add permission and session tests from `TEST_PLAN.md`.
