# Decisions

This file is append-only. Add new dated decisions instead of rewriting history.

## 2026-06-14

- The system is positioned as a server-deployed ToB law-firm public-opinion
  monitoring system.
- The first version targets single-server, low-concurrency internal or
  customer-pilot use.
- The first version does not include complex account rotation, captcha bypass,
  SMS automation, high-concurrency worker clusters, public SaaS onboarding, or
  billing.
- System administrators maintain account pools, proxy IPs, AI access, email
  settings, templates, runtime settings, and users.
- Normal users only create monitoring tasks by choosing platforms, entering
  platform search terms, setting frequency, and entering report recipient
  emails.
- Normal users must not need to manage platform accounts, proxies, browser
  profiles, API keys, SMTP passwords, or local paths.
- Server-like validation is mandatory. A task that only works through a local
  Chrome window is not production-ready.
- Each platform account must have an independent profile.
- Account names are display labels. Profile identity must use a stable key such
  as workspace, platform, and account ID.
- Same account and same profile are single-concurrency resources.
- Proxy priority is task-bound proxy, then account-bound proxy, then default
  network.
- Login and crawling should use the same account proxy when configured.
- Customer-facing UI must not expose real server paths, profile paths, raw
  secrets, command lines, debug wording, or implementation-only details.
- Create/edit/test interactions should be visually consistent. First-version
  UI should prefer modal dialogs for secondary operations to avoid mixed drawer
  and inline form behavior.
- Every active menu item must be covered by product requirements, not only the
  features explicitly discussed in chat.
- Meaningful new user requirements must be recorded in `CHANGE_REQUESTS.md`
  and connected to tasks and tests before being treated as complete.
- Agent work must update project documents as part of the completion criteria.
- Parallel agent/worktree development is allowed only with clear module/file
  ownership and document updates in each branch.
- Ambiguous high-impact requirements must be confirmed with the user before
  they are marked accepted or implemented in stable product documents.
- P0 specialist documents may contain proposed implementation details, but
  sections marked as open confirmation items must be confirmed before coding
  the affected phase.
- Profile migration does not need long-term legacy compatibility. Because the
  current account count is low and the project is still in agile development,
  existing profile-path-based accounts can be reset or re-logged in under the
  new `profile_key` model.
