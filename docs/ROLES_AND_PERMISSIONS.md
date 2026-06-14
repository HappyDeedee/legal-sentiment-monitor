# Roles And Permissions

This document defines V1 user roles, menu visibility, action permissions, data
scope, and unresolved confirmation items.

## V1 Role Model

V1 uses two active roles:

- system administrator;
- normal user.

Reserved roles:

- reviewer;
- read-only viewer;
- workspace administrator;
- platform super administrator.

## Workspace Scope

V1 implementation assumption, pending user confirmation:

- start with one default workspace;
- add `workspace_id` to business data now;
- keep the model ready for future multi-workspace use;
- do not build complex SaaS tenant onboarding in V1.

Open confirmation:

- Should V1 be single-workspace multi-user only, or should multiple workspaces
  be visible in the first release?

## Menu Permissions

| Menu | Administrator | Normal User |
| --- | --- | --- |
| Overview | visible | visible |
| Monitoring | visible | visible |
| Run Center | visible | visible |
| Report Center | visible | visible |
| Resource Management / Platform Accounts | visible | hidden |
| Resource Management / Proxy Resources | visible | hidden |
| Resource Management / AI Access | visible | hidden |
| System Configuration / Users And Permissions | visible | hidden |
| System Configuration / AI Evaluation Rules | visible | hidden |
| System Configuration / Mail Configuration | visible | hidden |
| System Configuration / Mail Templates | visible | hidden |
| System Configuration / Runtime Strategy | visible | hidden |
| System Configuration / System Diagnostics | visible | hidden |

## Action Permissions

| Action | Administrator | Normal User |
| --- | --- | --- |
| Create monitoring task | yes | yes |
| Edit own monitoring task | yes | yes |
| Edit all monitoring tasks | yes | no |
| Delete own monitoring task | yes | yes, if not running |
| Delete all monitoring tasks | yes | no |
| Run task immediately | yes | yes, own tasks only |
| Stop running task | yes | own tasks only |
| View own run logs | yes | yes |
| View all run logs | yes | no |
| View own reports | yes | yes |
| View all reports | yes | no |
| Resend report email | yes | own reports only, pending product confirmation |
| Manage platform accounts | yes | no |
| Manage proxies | yes | no |
| Manage AI access | yes | no |
| Manage SMTP | yes | no |
| Manage mail templates | yes | no |
| Manage runtime strategy | yes | no |
| Manage users | yes | no |
| View system diagnostics | yes | no |

Open confirmation:

- Should normal users be allowed to delete tasks, or only pause them?
- Should normal users be allowed to resend report emails?

## Data Scope

Administrator:

- can view and manage all data in the workspace;
- can view resource errors;
- can view system diagnostics.

Normal user:

- can view own tasks;
- can view runs and reports for own tasks;
- cannot view account pool, proxy URLs, AI keys, SMTP settings, cookies,
  profile paths, or raw deployment paths.

## API Permission Policy

Every API endpoint should declare:

- required role;
- data scope;
- whether secrets are masked;
- whether the action is audited.

Endpoint groups:

| API Group | Administrator | Normal User |
| --- | --- | --- |
| auth/session | yes | yes |
| jobs | yes, all workspace | own tasks |
| runs | yes, all workspace | own task runs |
| reports | yes, all workspace | own task reports |
| platform accounts | yes | no |
| proxies | yes | no |
| AI access | yes | no |
| mail config/templates | yes | no |
| runtime settings | yes | no |
| diagnostics | yes | no |

## User Lifecycle

Minimum V1 flow, pending implementation:

1. create initial administrator by bootstrap command or first-run setup;
2. administrator creates normal users;
3. disabled users cannot log in;
4. disabled users' existing scheduled tasks should be paused or reassigned,
   pending user confirmation;
5. deleting a user should not delete historical reports automatically.

Open confirmation:

- Initial administrator creation method: bootstrap CLI, environment variable, or
  first-run web setup?
- Disabled-user task behavior: pause tasks or keep running under workspace?

