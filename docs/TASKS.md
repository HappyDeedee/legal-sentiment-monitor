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
- [x] Add documentation consistency check specification.
- [x] Add a documentation check script during Phase 1 close-out, after Phase
      0.5 schema foundation and basic auth/session implementation are verified.

## Phase 0.5 - Schema Foundation

Blocking prerequisite:

Phase 0.5 must be completed before starting Phase 1-9 implementation. Without
these tables and fields, authentication, permissions, workspace filtering,
runtime settings, and profile-key migration cannot function safely.

This phase is the required implementation foundation before full Phase 1 user
and permission work.

- [x] Create `workspaces`, `users`, `user_sessions`, `system_settings`, and
      minimal `audit_logs` tables.
- [x] Add `workspace_id`, `created_by`, and `updated_by` to priority business
      tables.
- [x] Add `profile_key` to `social_accounts` and `login_sessions`.
- [x] Add run-level timeout fields to `crawl_runs`: `timeout_seconds`,
      `deadline_at`, and `timeout_reason`.
- [x] Add account/profile lock fields to `social_accounts`.
- [x] Create `resource_locks` for proxy concurrency.
- [x] Backfill existing data into the default workspace with `workspace_id = 1`.
- [x] Keep old fields during the first migration step, but stop using
      `profile_path` as the identity for new account environments.
- [x] Verify existing tasks, accounts, runs, and reports still load after the
      schema foundation change.

## Phase 1 - Users And Permissions

- [x] Add user model.
- [x] Add role model with administrator and normal user.
- [x] Add workspace field to core business tables.
- [x] Add login/session flow.
- [x] Hide administrator-only menus from normal users.
- [x] Restrict normal users to their own workspace data.
- [x] Implement `scripts/check_docs.py` before closing Phase 1.

## Phase 2 - System Settings Center

- [x] Add runtime settings storage.
- [x] Add settings precedence: defaults, config file, database, environment lock.
- [x] Add runtime strategy page for administrators.
- [x] Add read-only deployment diagnostics.
- [x] Support configurable global concurrency, platform concurrency, timeouts,
      retries, QR timeout, session TTL, and retention days.
- [x] Treat `crawler_timeout_seconds` as a run-level wall-clock deadline for
      newly started runs.
- [x] Add `lock_cleanup_buffer_seconds` for stale-lock recovery.
- [x] Replace hard-coded global crawl semaphore with
      `global_crawl_concurrency` from runtime settings.
- [x] Replace hard-coded platform locks/concurrency with per-platform runtime
      settings.
- [x] Replace hard-coded scheduler tick interval with `scheduler_tick_seconds`.

## Phase 3 - Administrator Resource Center

- [x] Refine platform account pool page.
- [x] Refine proxy resource page.
- [x] Refine AI access page.
- [x] Refine mail configuration page.
- [x] Refine email template page.
- [x] Ensure all create/edit/test actions use consistent modal interactions.

## Phase 4 - Normal User Task Wizard

- [x] Replace complex task form for normal users with a simplified wizard.
- [x] Include law firm, aliases, platform search terms, platforms, frequency,
      crawl range, comments, and recipient emails.
- [x] Explain crawl range boundaries: max items is a cap, max pages is
      approximate, start page and time window depend on platform support.
- [x] Hide account, proxy, AI profile, template, and browser options from normal
      users.
- [x] Keep administrator advanced task settings available.

## Phase 5 - Account Environment

- [x] Add `profile_key` and runtime path resolver.
- [x] Stop exposing real profile paths in the customer-facing UI.
- [x] Create one profile per platform account.
- [x] Ensure account name is display-only and not the profile identity.
- [x] Add account lock.
- [x] Add profile lock.
- [x] Add proxy concurrency control.
- [x] Add startup and scheduler recovery for stale running runs and expired
      locks.
- [x] Ensure login and crawling use the same account proxy when configured.

## Phase 6 - Server Login Flow

- [x] Make server-side QR login the primary flow.
- [x] Return structured login states to the frontend.
- [x] Support waiting QR, waiting scan, waiting confirmation, success,
      verification required, QR failure, timeout, and platform error.
- [x] Persist profile after successful login.
- [x] Verify profile reuse after browser close.
- [x] Hide local-window login from production mode.

## Phase 7 - Runs, Reports, And AI

- [x] Ensure tasks run even when AI is missing.
- [x] Mark AI failures as manual-review leads.
- [x] Ensure tasks run and reports generate even when email is missing.
- [x] Keep report wording as suspected negative leads.
- [x] Verify report preview switches correctly across reports.
- [x] Ensure logs can be refreshed, copied, and downloaded.

## Phase 8 - Server-Like Validation

- [x] Add a container or server-like deployment path.
- [x] Verify the web QR/status login path is primary in the server-like
      environment with local-window login disabled.
- [x] Verify profile metadata persistence across service restart.
- [x] Verify multiple same-platform accounts use separate profiles.
- [x] Verify account/profile/proxy concurrency limits.
- [x] Verify no local Chrome is required for automated server-like
      validation.

## Phase 9 - Security And Operations

- [x] Add audit log for administrator operations.
- [x] Mask sensitive values in UI and logs.
- [x] Add backup notes for database, profiles, reports, and encryption key.
- [x] Add account invalidation alert path.
- [x] Add proxy error alert path.
- [x] Add disk and retention diagnostics.
