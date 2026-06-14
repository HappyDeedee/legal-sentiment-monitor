# Implementation Tasks

Status legend:

- `[ ]` not started
- `[~]` in progress
- `[x]` done
- `[!]` blocked

## Phase 0 - Project Governance

- [x] Create project governance document set.
- [x] Add agent entry file.
- [x] Define documentation update mechanism.
- [x] Define UI/UX consistency rules.
- [x] Add menu-level product requirements.
- [x] Add change request intake document.
- [x] Add requirement/task/test traceability matrix.
- [x] Add detailed agent workflow document.
- [x] Add confirmation gate for ambiguous high-impact requirements.
- [x] Add roles and permissions specification.
- [x] Add account environment specification.
- [x] Add runtime settings specification.
- [x] Add target data model planning document.
- [x] Add permissions confirmation pack.
- [x] Add compatible schema migration plan.
- [x] Add `monitor.example.yaml`.
- [x] Add API authentication and authorization implementation guide.
- [x] Add server deployment and server-like validation guide.
- [ ] Add a documentation check script after the first implementation phase.

## Phase 0.5 - Schema Foundation

This phase is the required implementation foundation before full Phase 1 user
and permission work.

- [ ] Create `workspaces`, `users`, `user_sessions`, `system_settings`, and
      minimal `audit_logs` tables.
- [ ] Add `workspace_id`, `created_by`, and `updated_by` to priority business
      tables.
- [ ] Add `profile_key` to `social_accounts` and `login_sessions`.
- [ ] Backfill existing data into the default workspace with `workspace_id = 1`.
- [ ] Keep old fields during the first migration step, but stop using
      `profile_path` as the identity for new account environments.
- [ ] Verify existing tasks, accounts, runs, and reports still load after the
      schema foundation change.

## Phase 1 - Users And Permissions

- [ ] Add user model.
- [ ] Add role model with administrator and normal user.
- [ ] Add workspace field to core business tables.
- [ ] Add login/session flow.
- [ ] Hide administrator-only menus from normal users.
- [ ] Restrict normal users to their own workspace data.

## Phase 2 - System Settings Center

- [ ] Add runtime settings storage.
- [ ] Add settings precedence: defaults, config file, database, environment lock.
- [ ] Add runtime strategy page for administrators.
- [ ] Add read-only deployment diagnostics.
- [ ] Support configurable global concurrency, platform concurrency, timeouts,
      retries, QR timeout, session TTL, and retention days.

## Phase 3 - Administrator Resource Center

- [ ] Refine platform account pool page.
- [ ] Refine proxy resource page.
- [ ] Refine AI access page.
- [ ] Refine mail configuration page.
- [ ] Refine email template page.
- [ ] Ensure all create/edit/test actions use consistent modal interactions.

## Phase 4 - Normal User Task Wizard

- [ ] Replace complex task form for normal users with a simplified wizard.
- [ ] Include law firm, aliases, platform search terms, platforms, frequency,
      crawl range, comments, and recipient emails.
- [ ] Hide account, proxy, AI profile, template, and browser options from normal
      users.
- [ ] Keep administrator advanced task settings available.

## Phase 5 - Account Environment

- [ ] Add `profile_key` and runtime path resolver.
- [ ] Stop exposing real profile paths in the customer-facing UI.
- [ ] Create one profile per platform account.
- [ ] Ensure account name is display-only and not the profile identity.
- [ ] Add account lock.
- [ ] Add profile lock.
- [ ] Add proxy concurrency control.
- [ ] Ensure login and crawling use the same account proxy when configured.

## Phase 6 - Server Login Flow

- [ ] Make server-side QR login the primary flow.
- [ ] Return structured login states to the frontend.
- [ ] Support waiting QR, waiting scan, waiting confirmation, success,
      verification required, QR failure, timeout, and platform error.
- [ ] Persist profile after successful login.
- [ ] Verify profile reuse after browser close.
- [ ] Hide local-window login from production mode.

## Phase 7 - Runs, Reports, And AI

- [ ] Ensure tasks run even when AI is missing.
- [ ] Mark AI failures as manual-review leads.
- [ ] Ensure tasks run and reports generate even when email is missing.
- [ ] Keep report wording as suspected negative leads.
- [ ] Verify report preview switches correctly across reports.
- [ ] Ensure logs can be refreshed, copied, and downloaded.

## Phase 8 - Server-Like Validation

- [ ] Add a container or server-like deployment path.
- [ ] Verify web-only login in the server-like environment.
- [ ] Verify profile persistence across service restart.
- [ ] Verify multiple same-platform accounts use separate profiles.
- [ ] Verify account/profile/proxy concurrency limits.
- [ ] Verify no local Chrome is required for acceptance.

## Phase 9 - Security And Operations

- [ ] Add audit log for administrator operations.
- [ ] Mask sensitive values in UI and logs.
- [ ] Add backup notes for database, profiles, reports, and encryption key.
- [ ] Add account invalidation alert path.
- [ ] Add proxy error alert path.
- [ ] Add disk and retention diagnostics.
