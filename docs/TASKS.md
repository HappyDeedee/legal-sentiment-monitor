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

## CR-091 - Open Todo MECE Rebaseline And Phase 5.1 Preflight Gate

Planning status:

CR-091 is a documentation-governance batch for reorganizing the currently open
todo set before Phase 5.1 code work starts. It does not reopen completed
historical phases and does not implement code, UI, schema, runtime data,
account profiles, cookies, proxies, crawler behavior, or deployment changes.

Open todo layers:

- [x] Keep the active UI lane as Phase 21 only: frontend visual refinement on
      the current `main` formal console baseline, with Task Center, Run Detail,
      drawers, modals, enhanced select/date controls, close behavior,
      `.drawer-scroll-body`, top-bar refresh, scroll logic, and routing frozen
      unless a separate accepted CR changes them.
- [x] Add Phase 5.1 Preflight as the next account-environment lane before any
      Phase 5.1 schema or code work. This lane is documentation/read-only
      compatibility review of container/server-like runtime, provider
      boundaries, QR login, Cookie validation, login-state checks, manual runs,
      scheduler runs, runner behavior, and MediaCrawler CDP launch/reconnect.
- [x] Keep Phase 5.1 implementation as the account identity fidelity body:
      additive fields, generator, validator, `identity_state`, locking,
      reset/re-login, and runtime binding after preflight passes.
- [x] Keep Phase 5.1 acceptance separate from implementation: requested versus
      effective runtime snapshot, provider metadata, unsupported-field list,
      proxy effect proof or fail-closed behavior, manual/scheduler run reuse,
      and container/server-like validation are required before Phase 5.1 is
      considered complete.
- [x] Defer Phase 5.2 / CR-070 until CR-047's provider binding and effective
      runtime snapshot are implemented and verified.
- [x] Keep CR-037 role-based email governance, the currently unrendered Users
      And Permissions page, and Phase 7.1D historical repair as independent
      deferred or operator-gated items, not part of Phase 21 or Phase 5.1.

## CR-095 - Atomic Goal Execution Governance And Readiness Gate

Planning status:

CR-095 is a documentation-governance batch for turning the CR-091 open todo
lanes into executable goal packets. It does not reopen completed phases and
does not implement code, UI, schema, runtime data, account profiles, cookies,
proxies, crawler behavior, route exposure, deployment configuration, or
production changes.

Goal readiness tasks:

- [x] Add `docs/GOAL_EXECUTION_GUIDELINES.md` as the goal-readiness source for
      packet structure, atomicity rules, current execution lanes, test
      iteration loop, acceptance standards, and stop conditions.
- [x] Keep CR-091 as the MECE lane-separation owner and CR-095 as the execution
      governance owner, so task boundaries and goal mechanics do not collapse
      into one mixed concern.
- [x] Require every non-trivial future goal to state owner CR/phase, baseline,
      in scope, out of scope, hard boundaries, start gate, dependencies,
      expected touch surface, execution steps, test loop, acceptance criteria,
      rollback or recovery, documentation updates, and stop conditions.
- [x] Record the current serial execution rhythm: Phase 21 merged and closed on
      `main`, Phase 5.1P read-only preflight, Phase 5.1A-D implementation,
      Phase 5.1 acceptance, then CR-070 / Phase 5.2 after CR-047
      provider/effective snapshot verification. This is the historical CR-095
      baseline; the accepted 2026-07-21 decision now places CR-112 Packet B/C/D
      before CR-070.
- [x] Make Phase 5.1 goal-ready as serial units: preflight, data model,
      generator/validator, locking/re-login, runtime binding, and acceptance
      gate.
- [x] Make CR-070 / Phase 5.2 goal-ready as serial units: package contract and
      security model, export flow, import flow, post-import
      verification/recovery, and test-safety verification.
- [x] Keep CR-092, CR-093, and CR-094 as future independent backlog lanes that
      cannot become hidden prerequisites for Phase 21, Phase 5.1P, Phase 5.1,
      or CR-070 without a later accepted decision.
- [x] Add goal-readiness checks to workflow, documentation-check guidance,
      test plan, traceability, and test results.

## Future Independent Architecture And Boundary Backlog

Planning status:

These items are future independent lanes introduced after the CR-091 MECE
rebaseline. They are not part of Phase 21, Phase 5.1P, CR-047, or CR-070.
They must not change code, UI, schema, runtime data, account profiles, cookies,
proxies, crawler behavior, or deployment configuration until a later
implementation CR is explicitly accepted.

Numbering note:

CR-092 through CR-094 are the current identifiers for these future backlog
lanes. They replace the earlier planning-only CR-078 through CR-080 labels
because completed Phase 21 responsive fixes now own CR-078 through CR-080 as
historical verified records.

### CR-092 - Frontend Stack Migration Evaluation And Monitor Next Plan

- [ ] Keep CR-092 as future planning only. It must not create a frontend
      project, introduce a Node build pipeline, add package dependencies,
      change `/monitor`, change monitor APIs, change permissions, or modify
      Phase 21 work.
- [ ] Maintain `docs/MONITOR_NEXT_FRONTEND_PLAN.md` as the source document for
      future `/monitor-next` architecture.
- [ ] Compare Vite + TypeScript options before implementation starts,
      including Vue 3 and React candidates plus suitable Chinese ToB component
      libraries or headless component options.
- [ ] Define `/monitor-next` coexistence with `/monitor`, monitor-specific
      static asset namespace, API client boundary, route/permission matrix,
      component/state layering, design tokens, responsive strategy, testing,
      replacement gate, and rollback plan.
- [ ] State that `/monitor-next` may call only `/api/auth/...` and
      `/api/monitor/...` by default, not raw MediaCrawler or old crawler/data
      endpoints.
- [ ] Require future page migration CRs only after the architecture plan and
      technology decision are confirmed.
- [ ] Preserve current Task Center, Run Detail, drawer, modal, enhanced
      select/date, report download, email delivery, routing, owner-scope, and
      permission behavior until replacement equivalence is verified.

### CR-093 - MediaCrawler Internalization And Public Exposure Boundary

- [ ] Keep CR-093 as product-boundary and security-hardening planning until a
      route/mount audit confirms the implementation strategy. It must not
      delete MediaCrawler code or disable routes in this documentation batch.
- [ ] Audit FastAPI routers and static mounts before implementation, including
      `/monitor`, `/api/auth`, `/api/monitor`, `/api/crawler`, `/api/data`,
      websocket routes, old WebUI, old assets/logos/static paths, raw file
      browsing/download/preview, and direct crawler control routes.
- [ ] Classify each route as formal product, administrator diagnostic,
      internal dependency, historical/development, or production-disabled.
- [ ] Define the formal public allowlist and authentication/administrator
      requirements.
- [ ] Confirm whether production-disabled paths should return 404, 403, or be
      unmounted before implementation.
- [ ] Design reverse proxy and application-mount boundaries so production does
      not publicly expose old crawler/data/ws/raw-file surfaces.
- [ ] Preserve current task running, platform login, account checks, output
      parsing, Task Center, Run Detail, permissions, drawer/dropdown/date, and
      scroll behavior.
- [ ] Add user-visible wording cleanup only in a later implementation CR and
      keep trusted administrator diagnostics separate.

### CR-094 - Crawler Engine Provider Architecture

- [ ] Keep CR-094 as future architecture planning only. It must not implement
      provider abstraction, schema, runtime, profile, account, proxy, crawler,
      UI, or deployment changes in this documentation batch.
- [ ] Maintain `docs/CRAWLER_PROVIDER_ARCHITECTURE.md` as the source document
      for provider contract planning.
- [ ] Audit existing MediaCrawler login, account check, task run, output
      parsing, error handling, profile use, proxy injection, and Run Detail
      chains before future implementation.
- [ ] Draft provider declarations, task input, output normalization,
      capability/preflight, profile binding, error normalization, lifecycle,
      server-like acceptance, and security/redaction contracts.
- [ ] Preserve `profile_key` as the upper-layer account identity while allowing
      provider-specific profile material only through controlled bindings.
- [ ] State that future providers cannot create parallel task, account,
      profile, report, permission, or frontend entry systems.
- [ ] Require a separate data model and migration CR before adding provider
      tables, profile-binding tables, or capability schema.
- [ ] Keep CR-094 separate from the verified Phase 5.1P current-provider
      compatibility boundary; CR-094 remains future architecture planning.

## Phase 5.1 - Account Identity Fidelity

Planning status:

CR-047 is an accepted existing-feature optimization for the completed Phase 5
account-environment responsibility area. It does not rewrite Phase 5's
historical completion record. It extends the existing
`profile_key = workspace/platform/account` model with a persisted, locked
account identity configuration so the same platform account logs in and crawls
through the same profile traces, browser environment, proxy region/policy, run
binding, and lock/audit state.

The Phase 5.1 goal is account identity fidelity, not a new anti-verification
product. The profile folder stores browser traces such as cookies, local
storage, IndexedDB, cache, history, preferences, service workers, and session
state. The database stores the launch and consistency rules: browser platform,
user agent, timezone, locale, accept-language, viewport/screen/device flags,
fingerprint seed, proxy policy, region, generator metadata, validation state,
lock state, and re-login state.

CloakBrowser-Manager is a reference for the profile-environment idea only:
stable per-profile fields, CDP automation access, and noVNC viewing. Do not
copy its standalone account manager, database, frontend, auth model, or
deployment shape into this project without a separate provider decision.
V1 uses the existing Playwright/CDP provider path and does not introduce
CloakBrowser. Canvas, WebGL, font inventory, plugins, extensions, and long
browsing history are future/provider-dependent, not V1 commitments.

Execution order:

Phase 5.1P Preflight is complete and its verified map is the implementation
boundary. Execute Phase 5.1A-D serially; do not widen a unit beyond the one
BrowserEnvironmentProvider plan/result and requested/effective proof contract
recorded by the preflight.

### Phase 5.1P - Runtime Compatibility And Provider Preflight

Verification status:

Phase 5.1P is complete as a documentation/read-only preflight on 2026-07-19.
`docs/phase-5.1p-browser-entrypoint-map.md` records the complete current-path
map, the single provider plan/result contract, field proof classifications,
fail-closed rules, server-like boundary, and the CR-112 ownership split. It did
not change product code, schema, UI, runtime data, Profiles, Cookies, proxies,
crawler behavior, browser processes, deployment configuration, or database
state. Phase 5.1A is now implemented and independently verified. Phase 5.1B is
the next eligible execution unit.

- [x] Keep Phase 5.1P as read-only mapping only. It must not create or change
      schema, code, provider implementation, runtime data, profiles, cookies,
      proxies, crawler behavior, deployment configuration, or database state.
      If any current path cannot be mapped to one BrowserEnvironmentProvider
      output and one requested/effective runtime snapshot contract, stop Phase
      5.1 and record the ambiguity instead of starting Phase 5.1A-D.
- [x] Map the current QR login, Cookie validation, login-state check, manual
      run, scheduler run, runner, and MediaCrawler CDP launch/reconnect
      entrypoints without changing code.
- [x] Document which current paths launch a server-side browser, attach to an
      existing CDP endpoint, reuse a profile, validate login state, or fall
      back to MediaCrawler defaults.
- [x] Map current Cookie account validation, Profile persistence, raw argv/env,
      MediaCrawler login branches, and CDP-to-standard generic Profile fallback.
      Record the exact adapter a future CR-112 internal `profile_only` mode
      would need to replace managed `login_type=cookie` child execution, while
      keeping current QR/Profile execution separate, without implementing or
      assigning that mode to CR-047.
- [x] Map Cookie CLI defaults, `main.py` error handling, each platform's
      login-state/login-class branch, CDP fallback, runner exit/log mapping, and
      existing Profile environment variables needed by the future hidden flag
      and reserved relogin exit contract.
- [x] Define the BrowserEnvironmentProvider contract that Phase 5.1
      implementation must use for all login and crawl entrypoints.
- [x] Confirm which identity fields the existing Playwright/CDP provider can
      honor and prove in V1: `profile_key`, proxy policy, user agent,
      timezone, locale, accept-language, viewport/screen, device scale factor,
      mobile/touch flags, provider mode, and runtime snapshot probes.
- [x] Mark unsupported or not-managed high-fidelity surfaces explicitly:
      Canvas, WebGL, font inventory, plugins, extensions, long browsing
      history, noVNC, and provider-specific fingerprint internals.
- [x] Define fail-closed behavior when a required identity value cannot be
      honored, when requested and effective values differ, or when a locked
      account would fall back to process defaults.
- [x] Confirm container/server-like execution as the Phase 5.1 development and
      acceptance baseline. Local Chrome/Edge auto-detection, local-window
      login, and CDP connect-existing are development fallbacks only and cannot
      prove locked or active account identity.
- [x] Treat local Chrome/Edge auto-detection, local-window login, CDP
      connect-existing, process defaults, and default-network fallback as
      diagnostic fallbacks only. They cannot prove Phase 5.1 locked or active
      account identity.
- [x] Define how proxy effect will be proven or marked fail-closed before a
      locked account is called active, including the rule that hidden task
      proxy overrides and default-network fallback are rejected.
- [x] Produce a preflight review note or goal output that future Phase 5.1A-D
      work can follow without guessing provider, MediaCrawler, or deployment
      compatibility.

### Phase 5.1A - Account Identity Data Model

Implementation status:

The additive schema and compatibility tests are implemented and independently
verified in the isolated `codex/phase-5.1a-account-identity-schema` worktree
against `main@8b55c2a`. Focused tests passed (`2` Phase 5.1A tests and `7`
schema/account regression tests), the full monitoring suite passed (`352
passed`), and the final read-only review returned `READY` with no finding.
Phase 5.1B is also implemented and verified. Phase 5.1C lifecycle work is
implemented, independently verified, merged, and rechecked; Phase 5.1D is
merged and post-merge verified. CR-114 is also merged and reverified; final
server-like acceptance is active.

- [x] Start only after Phase 5.1P is complete and confirms the provider,
      MediaCrawler, and container/server-like compatibility boundary. Verified
      by `docs/phase-5.1p-browser-entrypoint-map.md` on 2026-07-19.
- [x] The fixed-environment proxy override policy is confirmed and recorded:
      after CR-047 locks an account identity, task-level proxy overrides are
      rejected for that locked account environment. Changing the proxy requires
      explicit reset/re-login.
- [x] Add additive account identity fields for platform accounts:
      `environment_region`, `browser_platform`, `identity_template`,
      `fingerprint_seed`, `user_agent`, `timezone`, `locale`,
      `accept_language`, `screen_width`, `screen_height`, `viewport_width`,
      `viewport_height`, `device_scale_factor`, `is_mobile`, `has_touch`,
      identity generator metadata, identity environment version,
      `requires_relogin`, `identity_state`,
      `identity_runtime_snapshot_json`, environment lock status, and lock
      timestamp/reason.
- [x] Keep `proxy_id` as the account-bound stable proxy policy field and
      add a customer-safe proxy region snapshot so identity validation can
      detect region/timezone/locale drift without exposing proxy secrets.
- [x] Keep existing active accounts readable, do not silently backfill guessed
      identity values, and represent their ungenerated environment as
      `identity_state = draft` without moving old profile directories. Runtime
      confirmation/re-login enforcement remains Phase 5.1C-D work.
- [x] Keep old accounts readable and avoid exposing raw `profile_path` in
      masked detail and list reads.

### Phase 5.1B - Account Identity Generation And Validation

Implementation status (2026-07-19): complete on
`codex/phase-5.1b-account-identity-generator` against merged Phase 5.1A
baseline `main@f8be522`. Focused Phase 5.1B tests pass (`9 passed`) and the
full monitor suite passes (`361 passed`). Final independent diff review and
integration evidence are recorded in `TEST_RESULTS.md`. Phase 5.1C lifecycle
work is implemented, independently verified, merged, and rechecked; Phase
5.1D is merged and post-merge verified. CR-114 is also merged and reverified;
final server-like acceptance is active.

- [x] Add an Account Identity Generator that uses workspace, platform,
      account, proxy/region policy, automatic template selection or a
      pre-login administrator template-family choice, and seed salt to produce
      stable account identity output before first QR login or Cookie
      validation.
- [x] Ensure the generator is stable, differentiated, self-consistent, and
      explainable: same input produces the same identity, different accounts
      normally differ, and each output can be traced to a customer-safe
      template/version.
- [x] Make automatic template selection the default: normal users cannot choose
      identity templates, ordinary administrator account creation does not
      require template choice, and administrators may only choose a template
      family before first login through an advanced path.
- [x] Do not expose field-level identity editing for UA, viewport, screen,
      timezone, locale, accept-language, device scale factor, mobile flag, or
      touch flag; these fields must come from the selected catalog template and
      region bundle.
- [x] Add China mainland generation rules: `environment_region =
      CN_MAINLAND`, `timezone = Asia/Shanghai`, `locale = zh-CN`,
      `accept_language = zh-CN` for catalog v2, and a coherent desktop/mobile
      device template instead of province-level overfitting.
- [x] Support a small template catalog such as `CN_WIN_CHROME_1920`,
      `CN_WIN_CHROME_1536`, `CN_MAC_CHROME_1440`, `CN_ANDROID_CHROME`,
      `HK_DESKTOP_CHROME`, and `SG_DESKTOP_CHROME`, with generator metadata
      persisted on each account.
- [x] Implement the deterministic generation algorithm from
      `ACCOUNT_ENVIRONMENT.md`: deterministic template-selection seed,
      documented catalog-order selection from eligible templates, HMAC-SHA256
      fingerprint seed derivation from workspace, platform, account, region,
      selected template, and salt; exact template expansion; no random or
      process-default fallback.
- [x] Add an Account Identity Validator that fails closed when proxy region,
      timezone, locale, accept-language, UA, browser platform, viewport/screen,
      mobile/touch flags, or locked fields are missing or contradictory.
- [x] Reject silent fallback to Playwright/process defaults at the validator
      boundary when a locked identity exists. Phase 5.1D still owns mandatory
      invocation from every launch/attach adapter and effective-value proof.
- [x] Add test safety tripwires so automated tests and local diagnostics cannot
      touch real profile roots, cookies, proxy credentials, or real platform
      login sessions without explicit opt-in environment variables. Current
      Playwright account-check/QR entrypoints are blocked by default in pytest;
      Phase 5.1D owns narrow Runner/login-window process-provider guards.

### Phase 5.1C - Account Identity Locking And Re-Login

Implementation status (2026-07-19): verified. Code, UI, CR-113, focused tests,
the full `378`-test monitoring suite, Python compile, documentation gates,
desktop/mobile browser checks, and an independent Claude Code full-diff review
pass in `codex/phase-5.1c-account-identity-lifecycle` from `main@100001e`.
PR #4 is merged as `main@2adf661`; post-merge full monitoring, compile, and
documentation gates pass. Phase 5.1D later merged through PR #5 and passed
post-merge verification on `main@86e9d02`; CR-114 then merged through PR #6
and passed post-merge verification on `main@27389a8`.

- [x] Implement the persisted `identity_state` lifecycle from
      `ACCOUNT_ENVIRONMENT.md`: `draft`, `generated`, `validated`,
      `login_in_progress`, `locked`, `active`, `requires_relogin`, and
      `resetting`.
- [x] Implement the template-family change transitions from
      `ACCOUNT_ENVIRONMENT.md`: `draft` can regenerate, `generated` and
      `validated` return to `draft`, `login_in_progress` rejects changes, and
      `locked` or `active` requires `requires_relogin` plus reset/re-login.
- [x] Lock the browser-environment configuration after successful QR login or
      accepted Cookie validation.
- [x] Block silent edits to locked environment fields.
- [x] Add an explicit administrator reset/re-login path for changing a locked
      environment, with audit logging and clear consequences.
- [x] Mark identity-template or proxy-region changes that invalidate an
      existing locked identity as `requires_relogin` instead of silently
      changing future crawl launches.
- [x] Preserve one account/profile concurrency locks and server-side QR login
      behavior.
- [x] Register and verify CR-113 so new-account QR draft creation forwards only
      the accepted safe region and template-family choices.
- [x] Complete the independent read-only full-diff review and documentation
      consistency checks before marking Phase 5.1C technically verified.
- [x] Integrate the Phase 5.1C branch and complete post-merge verification
      before starting Phase 5.1D code.

### Phase 5.1D - Login And Crawl Runtime Binding

Implementation status (2026-07-19): merged and post-merge verified. PR #5
merged `codex/phase-5.1d-browser-runtime-binding` into `main@86e9d02`. The
atomic execution packet is
`docs/superpowers/plans/2026-07-19-phase-5.1d-browser-runtime-binding.md`.
Post-merge focused Phase 5.1B-D tests pass (`131 passed`) and the complete
monitoring suite passes (`484 passed`). Compile, documentation, JavaScript
parse, desktop/mobile browser checks, and the independent Claude Code full-diff
review pass. CR-114 now owns the later-discovered object-ID reuse regression;
it does not rewrite Phase 5.1D history. Phase 5.1 acceptance remains a separate
gate after CR-114 integrates.

- [x] Ensure QR login launch options use the persisted environment values
      rather than process defaults for user agent, viewport/screen, locale,
      timezone, proxy, and browser-platform/fingerprint provider inputs where
      supported.
- [x] Ensure crawler/CDP launch and reconnect paths use the same persisted
      account environment as login.
- [x] Add a browser-environment provider boundary so existing Playwright/CDP
      remains the V1 provider and unsupported high-fidelity surfaces are
      reported as future/provider-dependent rather than silently claimed.
- [x] Map persisted identity values to Playwright context options and runtime
      probes exactly as specified in `ACCOUNT_ENVIRONMENT.md`, and fail closed
      if a required value cannot be honored.
- [x] Persist `identity_runtime_snapshot_json` with requested versus effective
      values, provider metadata, unsupported field list, and `fallback_used`
      evidence after successful login/crawl launches.
- [x] Verify service restart, scheduler run, and manual run paths do not change
      the stored account browser environment.
- [x] Ensure MediaCrawler integration receives the higher-priority account
      identity input when present, while preserving current MediaCrawler
      defaults only for accounts that do not yet have a Phase 5.1 identity.
- [x] Add negative tests proving locked environments reject task-level proxy
      overrides, hidden process-default fallback, and default-network fallback
      before browser or crawler launch.

### CR-114 - Browser Runtime Binding Object Identity Collision Regression Fix

Implementation status (2026-07-19): verified and merged. PR #6 integrated the
fix as `main@27389a8`; post-merge full (`485 passed`), focused (`132 passed`),
compile, and documentation gates pass.

- [x] Reproduce the Context/Page numeric-ID reuse defect with a deterministic
      regression test before changing production code.
- [x] Replace process-global numeric-ID plan/runtime/prepared collections with
      exact object-scoped bindings tied to the current resolution and attempt.
- [x] Preserve fail-closed CDP command ordering, safe result handling, and all
      Phase 5.1D managed no-fallback boundaries.
- [x] Run adjacent CDP tests, focused Phase 5.1B-D tests, and the full monitor
      suite serially.
- [x] Complete Python compile, documentation checks, and independent read-only
      full-diff review with no blocking or material finding.
- [x] Integrate through PR #6 and rerun post-merge verification.

### CR-115 - Server-Like Validation Temporary Data Cleanup Regression Fix

Implementation status (2026-07-20): verified and merged. Two repeated Windows
lower-strength preflight runs on `main@808822a` left generated SQLite/WAL files
because one `ignore_errors=True` removal silently lost a transient lock error.
PR #8 merged the bounded cleanup as `main@84cabff`; focused/full/real
lower-strength/docs/compile gates pass after merge.

- [x] Add a synthetic RED that simulates transient Windows removal failures.
- [x] Retry bounded temporary cleanup after the validation service stops.
- [x] Return structured cleanup failure instead of reporting success with
      generated files still present.
- [x] Preserve explicit `--data-dir` and `--keep-data` retention behavior.
- [x] Rerun the real lower-strength preflight and prove its generated directory
      is absent after exit.
- [x] Complete focused/full/docs/compile and independent read-only review.
- [x] Merge this follow-up and complete post-merge verification before resuming
      Phase 5.1 Task 3.

### CR-116 - Persistent Context Runtime Proof Regression Fix

Implementation status (2026-07-20): merged through PR #10 on `main@cd640f0`
and verified. A real local QR
attempt on merged `main@a66b3f8` reproduced the Phase 5.1D effective-proof
failure; the corrected flow now captures a QR image and closes cleanly. The
completed Phase 5.1D history remains closed; CR-116 owns this regression.

- [x] Add a deterministic RED for a persistent Playwright context whose
      `context.browser` is `None`.
- [x] Read the effective Chromium version from the exact page's CDP
      `Browser.getVersion` response and detach the temporary session.
- [x] Align catalog `1.1/v2` with pinned Playwright 1.45 Chromium metadata and
      provider-effective locale; require explicit reset/re-login for v1.
- [x] Preserve Browser-object proof, field-scoped version mismatch evidence,
      fail-closed behavior, and existing QR/Profile/proxy ownership.
- [x] Verify the real local managed flow reaches QR capture, then close the
      diagnostic browser session without retaining QR or Cookie material.
- [x] Run focused/full/compile/documentation gates and independent read-only
      review before closing CR-116.

### Phase 5.1 Acceptance Gate - Runtime Snapshot And Server-Like Verification

Execution status (2026-07-20): the atomic packet is documentation-consistent
and independently reviewed `READY`. Task 2 evidence-checker TDD is implemented
and independently reviewed `PASS`; its formal CLI requires the exact deployed
commit and 49 targeted, 183 focused, and 534 full tests pass. CR-115 is merged
and post-merge verified with a current `538`-test full suite. Task 3 local
preflight passes Compose parsing, pinned host Chromium, and the corrected
12-check lower-strength validator, but stops operator-blocked because this
machine has no WSL distribution or reachable Docker Linux engine. No container
mount, `RUNTIME_COMMIT`, real proxy probe, account, or platform action exists;
Tasks 4-7 remain operator-gated.

- [x] Start only after Phase 5.1P and Phase 5.1A-D are complete and verified,
      and the CR-114 object-identity regression fix is merged and reverified.
- [x] Create the atomic acceptance packet at
      `docs/superpowers/plans/2026-07-19-phase-5.1-server-like-acceptance.md`.
- [x] Implement and verify the redacted acceptance evidence checker before any
      real acceptance action.
- [ ] Verify QR login, Cookie validation, login-state checks, manual runs,
      scheduler runs, runner behavior, and MediaCrawler CDP launch/reconnect
      resolve the same BrowserEnvironmentProvider output.
- [ ] Verify requested versus effective runtime snapshots include provider
      metadata, supported values, unsupported/not-managed fields, mismatch
      evidence, and `fallback_used = false` for locked active identities.
- [ ] Verify proxy effect is proven for the resolved account proxy policy, or
      the account fails closed. Hidden task-level proxy override,
      process-default fallback, and default-network fallback must not mark the
      identity active.
- [ ] Verify container/server-like execution is the acceptance baseline. Local
      Chrome/Edge auto-detection, local-window login, and CDP connect-existing
      remain diagnostic fallbacks only.
- [ ] Verify Platform Accounts UI/API expose only customer-safe identity and
      provider summaries, without cookies, proxy credentials, raw profile
      paths, CDP endpoints, noVNC tokens, or fingerprint-debug output.
- [ ] Record the Phase 5.1 acceptance evidence in `docs/TEST_RESULTS.md`
      before closing the CR-047 gate. Under the accepted 2026-07-21 sequence,
      this does not start CR-070; the CR-112 Packet D dependency is now
      satisfied, while CR-047's Linux/server-like acceptance stays independent.

### Phase 5.1E - Optional CloakBrowser-Style Provider Evaluation

This optional provider-evaluation block is not part of the current
Phase 5.1A-D implementation path or Phase 5.1 acceptance gate. It must not
start before a separate accepted provider decision or future CR explicitly
makes it current work.

- [ ] Keep CloakBrowser and CloakBrowser-Manager out of V1 implementation.
- [ ] If future high-fidelity browser-persona work is accepted, first evaluate
      whether CloakBrowser or CloakBrowser-Manager-style CDP/noVNC management
      should become an optional provider.
- [ ] Review license, deployment, authentication, noVNC access-control,
      profile storage, server resource use, and sensitive-data redaction before
      any provider is enabled.
- [ ] Keep optional provider endpoints administrator-only and consistent with
      existing account/profile/proxy locks.
- [ ] Record a separate decision before making CloakBrowser or
      CloakBrowser-Manager a required production dependency.
- [ ] Use the current planning estimate for future high-fidelity work: 1-2
      days for provider/license/deployment review, 3-5 days for a local
      one-platform prototype, 1-2 weeks for optional provider integration, and
      3-6+ weeks for production-grade browser-pool/profile-history capability.

## Phase 5.2 - Account Environment Export And Import Package

Planning status:

CR-070 is an accepted new capability for account-environment migration. It does
not reopen Phase 5 or CR-047. Its CR-112 Packet D dependency is satisfied as of
2026-07-22; implementation still starts with a fresh todo baseline review and
an atomic Phase 5.2 execution packet. The required CR-047 provider binding and
requested/effective runtime snapshot implementation already exists;
the separate CR-047 Linux/server-like real acceptance remains independently
operator-gated. CR-070 should reuse only committed CR-112 Profile/account state
and CR-047 identity fields. Because the capability can move cookies,
browser profile traces, and platform account metadata between deployments,
implementation must remain administrator-only, encrypted, audited, and
fail-closed.

The package moves one selected platform account environment. It is not a
general database backup/restore feature. Monitoring tasks, crawl runs, reports,
AI traces, email delivery logs, users, runtime settings, and customer business
history remain outside the default package unless a later export requirement
explicitly adds them.

Confirmed V1 decisions:

- [x] V1 supports metadata-only export and a slim encrypted login-state
      migration package. The migration package should export configuration,
      login/session state, and necessary profile state, not a raw whole
      browser profile copy.
- [x] V1 uses passphrase-based package encryption. Target-deployment public-key
      encryption is future scope.
- [x] V1 may include the source proxy endpoint hint such as host/IP and port
      inside the encrypted package payload, but must not export proxy username,
      password, token, authentication header, or provider secret. Audit logs,
      manifest summaries, and ordinary API responses must not expose the
      endpoint hint.
- [x] V1 imports create a new target account/profile by default. Replace,
      merge, and overwrite are future scope.
- [x] V1 exports avatar metadata only. Cached avatar image bytes are future
      scope.

### Phase 5.2A - Package Contract And Security Model

- [ ] Define the account package manifest schema, package version,
      compatibility fields, checksum/signature fields, redaction rules, and
      package modes.
- [ ] Define the exact package file structure from
      `ACCOUNT_ENVIRONMENT.md`: encrypted `.maepkg` outer envelope,
      `manifest.json`, `account/account.json`,
      `account/identity_runtime_snapshot_redacted.json`,
      optional `profile/slim_profile.zip`, and `checksums/sha256.json`.
- [ ] Define allowed and forbidden package contents, including account identity
      fields, encrypted login material, slim profile state, platform-account
      metadata, and proxy mapping metadata.
- [ ] Define slim profile state rules: include provider-owned login/session
      files and profile configuration needed for login-state reuse; exclude
      cache, GPU cache, code cache, media cache, crash dumps, downloads,
      screenshots, temporary files, and other duplicated or regenerable
      browser artifacts.
- [ ] Keep package scope to the selected platform account environment and
      explicitly exclude tasks, runs, reports, AI traces, mail delivery logs,
      users, runtime settings, and full database backup content.
- [ ] Treat metadata-only packages as sensitive by default when they contain
      real identity fields such as `fingerprint_seed`, runtime snapshot
      summaries, or recognized platform account IDs; use the same encrypted
      package envelope unless a later redacted diagnostic export is confirmed.
- [ ] Define package encryption/decryption and secret-handling rules so export
      files never contain plaintext cookies, proxy credentials, package
      passphrases, profile paths, CDP endpoints, noVNC tokens, or deployment
      encryption keys.
- [ ] Specify and implement V1 passphrase encryption details:
      library-based encryption, Argon2id KDF, AES-256-GCM, authenticated clear
      header, no persisted passphrase, and tested failure behavior for missing
      KDF support.
- [ ] Define package retention and storage behavior: generated packages are
      operator-download artifacts, not committed runtime data, and cleanup
      guidance is visible to administrators.
- [ ] Define safe package audit fields and forbidden audit fields using the
      examples in `ACCOUNT_ENVIRONMENT.md`.

### Phase 5.2B - Export Flow

- [ ] Add administrator-only metadata export for account identity and
      platform-account metadata without cookies or profile traces.
- [ ] Add administrator-only slim login-state migration export that packages
      encrypted login material and the necessary profile state under
      `profile_key`, without raw whole-profile cache and temporary artifacts.
- [ ] Ensure export is blocked or marked incomplete when the account is
      currently locked by a run, login session, or reset workflow.
- [ ] Implement the export operation state machine from
      `ACCOUNT_ENVIRONMENT.md`, including preflight, account package operation
      lock, metadata read, optional slim profile state, payload build,
      encryption, ready-for-download, failure, cancellation, expiry, and
      deletion states.
- [ ] Ensure export finalization releases locks and deletes staged files on
      failure, cancellation, timeout, interruption recovery, or expiry.
- [ ] Fail export with `account_package_state_changed` if account identity,
      login state, profile lock, or proxy binding changes after preflight and
      before package completion.
- [ ] Write export audit logs with package type, account, platform, version,
      and redacted checksum evidence, without raw secrets or paths.
- [ ] Enforce package retention: package bytes are runtime artifacts only,
      recommended temporary expiry is 24 hours after generation/download, and
      optional persisted metadata uses `expires_at`.

### Phase 5.2C - Import Flow

- [ ] Add administrator-only import preflight that validates package integrity,
      manifest schema, package version, source/target compatibility, provider
      compatibility, identity environment version, and path safety before any
      write.
- [ ] Validate package encryption metadata, KDF parameters, checksum manifest,
      required JSON sections, and unknown package modes before decrypting into
      a staging workspace.
- [ ] Import into a new target account/profile by default, deriving the target
      `profile_key` from the target workspace/platform/account ID instead of
      trusting the source filesystem path.
- [ ] Reject replace, merge, or in-place profile overwrite in V1 unless a
      later explicit conflict policy is confirmed; duplicate detection may warn
      administrators but must not overwrite target records.
- [ ] Require target-side proxy mapping when the package references a proxy
      policy or region; do not silently fall back to no proxy or a mismatched
      proxy.
- [ ] Use decrypted source proxy endpoint hints only to help the administrator
      choose a target proxy; never treat host/IP/port hints as usable proxy
      credentials and never log or expose them through ordinary APIs.
- [ ] Validate target proxy existence, workspace ownership, active status, and
      region compatibility before an imported account can become active.
- [ ] Preserve CR-047 identity state and runtime snapshot metadata only when
      compatible; otherwise mark the imported account as needing reset/re-login.
- [ ] Implement the import operation state machine from
      `ACCOUNT_ENVIRONMENT.md`, including preflight, decrypting,
      extracting_profile, writing_database, verifying_login, active,
      requires_relogin, failed, and rolled_back.
- [ ] Add package and target-account/profile operation locks so the same
      package or target account cannot be imported concurrently.
- [ ] Write import audit logs with source package metadata, target account ID,
      compatibility result, login verification result, and redacted failure
      reasons.

### Phase 5.2D - Post-Import Verification And Recovery

- [ ] Run login-state verification after import before allowing crawl use.
- [ ] Mark successful imports active only after the imported profile and
      login material pass the same platform account check used by server login
      reconciliation.
- [ ] Mark failed or incompatible imports `requires_relogin` and prevent
      silent crawl launch until an administrator re-logins under the target
      deployment.
- [ ] Keep imported profile writes under the configured profile root and add
      traversal/corrupt-archive rollback behavior.
- [ ] Validate slim profile-state archive quotas and safety before extraction:
      no absolute paths, drive-letter paths, UNC paths, traversal, symlinks,
      hardlinks, junctions, unsafe Windows device names, duplicate conflicting
      entries, unsupported compression, corrupt archives, or profile format
      mismatch.
- [ ] Enforce V1 package safety limits from `ACCOUNT_ENVIRONMENT.md`:
      512 MiB encrypted package size by default, 20,000 profile files by
      default, and at least twice declared uncompressed size plus 256 MiB free
      disk before extraction.
- [ ] Make import/export cleanup idempotent so repeated recovery cannot reopen
      terminal states, recreate package bytes, or leave locks stuck.
- [ ] Add clear administrator diagnostics for import success, partial import,
      requires-relogin state, proxy mapping mismatch, provider mismatch, and
      package integrity failure.

### Phase 5.2E - Test Safety And Verification

- [ ] Add fixture-based package export/import tests that use disposable
      profile roots and fake cookies.
- [ ] Add tripwires so automated tests cannot export real profiles, cookies,
      proxy credentials, or live account packages without explicit opt-in.
- [ ] Add CR-070-specific tripwire environment gates:
      `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_EXPORT=true` and
      `TEST_ALLOW_REAL_ACCOUNT_PACKAGE_IMPORT=true`; tests must still use fake
      cookies, fake proxy references, disposable profile roots, and fixture
      packages by default.
- [ ] Add negative tests for plaintext secret leakage in package files, audit
      logs, API responses, and diagnostic messages.
- [ ] Add tests for exact package schema, encrypted envelope metadata, KDF
      rules, checksum validation, package retention cleanup, and redacted audit
      examples.
- [ ] Add export-state tests for active-account lock rejection, state-change
      failure, cancellation, timeout, interruption cleanup, lock release, and
      staged-file deletion.
- [ ] Add import-state tests for preflight failure, decrypt failure,
      extraction rollback, database-write failure, login verification failure,
      terminal-state idempotency, and stuck-lock recovery.
- [ ] Add proxy-mapping tests for missing mapping, wrong workspace, inactive
      target proxy, region mismatch, and no silent direct/default-network
      fallback.
- [ ] Add compatibility tests for metadata-only import requiring re-login,
      slim login-state package import with verified login state, and slim
      login-state package import that fails verification and becomes
      `requires_relogin`.
- [ ] Verify docs consistency after the implementation and record results in
      `docs/TEST_RESULTS.md`.

## Phase 6 - Server Login Flow

- [x] Make server-side QR login the primary flow.
- [x] Return structured login states to the frontend.
- [x] Support waiting QR, waiting scan, waiting confirmation, success,
      verification required, QR failure, timeout, and platform error.
- [x] Persist profile after successful login.
- [x] Verify profile reuse after browser close.
- [x] Hide local-window login from production mode.
- [x] Reconcile QR-session failures with same-account MediaCrawler login-state
      checks before showing login failure.

## Phase 7 - Runs, Reports, And AI

- [x] Ensure tasks run even when AI is missing.
- [x] Mark AI failures as manual-review leads.
- [x] Ensure tasks run and reports generate even when email is missing.
- [x] Keep report wording as suspected negative leads.
- [x] Verify report preview switches correctly across reports.
- [x] Ensure logs can be refreshed, copied, and downloaded.

## Phase 7.1 - Runs, Reports, And AI Stuck Recovery Follow-up

Planning status:

Phase 7.1 is an accepted follow-up regression fix for CR-035. It does not
rewrite Phase 7's historical completion record. It restores the Phase 7
guarantee that AI failure or interruption must not block report generation or
leave a run indefinitely `running`.

Confirmed CR-035 decision summary:

- [x] Confirm whether `interrupted` becomes a first-class terminal
      `crawl_runs.status`.
- [x] Confirm the stale-recovery algorithm should inspect step-level progress,
      live task evidence, resource locks, retry state, last safe return value,
      and redacted last error before marking a run interrupted.
- [x] Confirm retry policy should reuse existing crawler retry controls for
      platform/browser/network failures and apply a separate AI item retry
      budget within the run deadline.
- [x] Confirm `ai_item_timeout_seconds` should default to 120 seconds and be
      capped by the remaining run deadline.
- [x] Confirm future `crawl_runs.job_id` gaps must be prevented first, while
      dry-run-first historical `job_id` backfill from `summary.job_id` is only
      a fallback for rows whose task still exists.
- [x] Confirm active finalization may create `pending_review` rows for known
      unresolved AI candidates, while stale recovery does not rewrite AI rows
      unless an explicit repair workflow is invoked.
- [x] Confirm run summaries should include AI evaluation counts for total
      candidates, successful evaluations, failed/fallback evaluations,
      pending-review items, and unresolved items where available.

### Phase 7.1A - Run Identity Compatibility

- [x] Verify active runtime writes `crawl_runs.job_id` for new runs.
- [x] Add compatible reads for legacy rows where `crawl_runs.job_id` is null
      but `summary.job_id` resolves to an existing task.
- [x] Update running-run lookup, stop/cancel behavior, and safe backfill logic
      for compatible legacy rows.
- [x] Ensure backfill is dry-run capable and skips unresolved historical rows.

### Phase 7.1B - Idempotent Finalization And Recovery

- [x] Add one idempotent finalization helper for success, failure, timeout,
      cancellation, interruption, and partial AI/report paths.
- [x] Protect terminal status transitions from repeated or concurrent writers.
- [x] Release resource locks safely after finalization attempts, with repeated
      release as a harmless no-op.
- [x] Persist step-level run lifecycle progress in `crawl_runs.summary`,
      including phase, phase started time, progress heartbeat, retry state,
      last safe return value or customer-safe result, and redacted last error.
- [x] Log background task exceptions with `run_id`, compatible `job_id`, phase,
      progress snapshot, and redacted error.
- [x] Recover stale `running` rows before the wall-clock deadline only after
      evaluating live task evidence, resource locks, progress heartbeat, retry
      state, last step result, and redacted interruption cause.
- [x] Ensure startup/scheduler stale recovery does not auto-repair historical
      stuck runs such as `8317`; historical repair must use the Phase 7.1D
      approval workflow.

### Phase 7.1C - AI Fallback And Partial Report Generation

- [x] Add per-item AI timeout/failure/invalid-JSON fallback to
      `pending_review` when the run can safely continue.
- [x] During active finalization, create `pending_review` rows for known
      not-yet-evaluated candidates when safe before report generation.
- [x] Track AI evaluation progress counts for total candidates, successful
      evaluations, failed/fallback evaluations, pending-review items, and
      unresolved items.
- [x] Generate reports from partial AI/manual-review state when collected
      content exists.
- [x] Finalize report-generation failures into a terminal redacted failure
      state instead of leaving the run `running`.

### Phase 7.1D - Current Run Remediation Gate

- [ ] Do not modify historical run `8317` without explicit operator
      confirmation.
- [ ] Before repair, back up the database and document rollback steps.
- [ ] Provide a dry-run-first repair helper or operator checklist for run
      `8317`, showing proposed terminal status, unresolved AI counts,
      pending-review rows to create, report-generation effect, and rollback
      path before any mutation.
- [ ] After code safety is verified, choose either preserving run `8317` as
      `interrupted` or repairing it into a partial report with the remaining
      21 contents marked for manual review.

## Phase 7.2 - AI Evaluation Accuracy And Lead Status Clarity Follow-up

Planning status:

Phase 7.2 is an accepted follow-up regression fix for CR-045. It does not
rewrite Phase 7 or Phase 7.1 historical completion records. It tightens the
AI evaluation and report-lead safety contract after live pilot inspection found
that missing AI evaluation rows could be displayed as "no risk" and broad
target-bearing keywords could recall many unrelated refund/legal posts.

Safety priority:

Phase 7.2 is the first ordinary implementation priority before operators rely
on broad-keyword AI risk labels in pilot use. Phase 7.2A-B is implemented and
verified locally: missing AI evaluation records are treated as unevaluated or
limited-context instead of no-risk, report/run counts and filters split the
major lead states, and active timeout/partial finalization creates
pending-review fallback rows for known unresolved candidates when safe. Phase
7.2C-D relevance hardening and calibration fixtures are retained as historical
CR-045 verification. CR-096 supersedes the application-layer target-evidence
gate as current behavior: `source_keyword` remains prompt guidance, while
valid model semantics are no longer overwritten by hardcoded postprocessing.

### Phase 7.2A - Unevaluated Lead Status Safety

- [x] Audit Report Center, Run Center, leads API, report generation, and lead
      filters for any path that treats missing `ai_evaluations` rows as
      no-risk content.
- [x] Add an explicit unevaluated or limited-context lead state for missing AI
      evaluation records where safe mutation is not possible.
- [x] Ensure frontend status rendering distinguishes unrelated, evaluated
      no-risk, suspected negative, high-risk, pending manual review, and
      unevaluated/limited-context history.
- [x] Update report counts and filters so pending-review, unrelated, no-risk,
      and unevaluated rows are not collapsed into one "no risk" bucket.

### Phase 7.2B - Timeout And Partial-Finalization AI Fallback

- [x] Ensure timeout and partial-failure finalization attempt to create
      `pending_review` fallback rows for known unresolved AI candidate IDs
      before report generation when mutation is safe.
- [x] Preserve idempotent finalization and do not rewrite terminal historical
      rows outside an explicit repair workflow.
- [x] Record customer-safe summary evidence for unresolved AI candidates,
      fallback rows created, and limited-context rows left unchanged.

### Phase 7.2C - AI Relevance And Prompt Hardening

- [x] Update AI evaluation rules so `source_keyword` is recall provenance only
      and cannot by itself prove target-law-firm relatedness.
- [x] Add or enforce a target-evidence gate using title, description, author,
      or sampled comments before marking content as target-related or negative.
- [x] Treat homonyms and geography such as "海安" as insufficient for target
      law-firm relatedness unless the content also points to the law firm or an
      accepted alias.
- [x] Preserve support for sampled comments as evidence when comments are
      actually collected and passed into the AI payload.
- [x] If additional structured fields are added, such as target-match level,
      negative signal level, confidence, or review reason, document schema and
      role-safe display before implementation.
- [x] Add a regression fixture proving a noisy positive model output still
      cannot turn a `source_keyword`-only fixture into a target-related negative
      lead without target evidence.

### Phase 7.2D - Calibration Fixtures And Regression Tests

- [x] Add fixture coverage for broad refund/legal posts collected by
      target-bearing keywords but lacking target-law-firm evidence; they must
      not become target-related negative leads.
- [x] Add fixture coverage for title, description, or comment evidence that
      clearly names the target law firm or alias and contains a negative
      signal; it must remain eligible for suspected-negative classification.
- [x] Add regression coverage proving missing AI evaluation rows are never
      rendered or filtered as no-risk for Phase 7.2A.
- [x] Add regression coverage for timeout/partial-finalization fallback from
      unresolved candidates to pending review for Phase 7.2B.
- [x] Run docs consistency and targeted monitoring tests before marking the
      Phase 7.2A-D safety batch implemented.

## CR-096 - AI Evaluation Postprocessing Scope Reduction

Planning status:

CR-096 is a verified regression fix for the completed CR-045/Phase 7.2 AI
evaluation responsibility area. It does not reopen Phase 7, Phase 7.1, or
Phase 7.2 historical completion records. It narrows AI evaluation
postprocessing to format validation plus trace/storage safety so valid model
semantic output cannot be erased by hardcoded target-word, alias,
`source_keyword`, or quote matching.

- [x] Remove application-layer target-evidence semantic rewriting from
      `api/monitoring/ai.py`.
- [x] Delete the unused target-evidence gate helpers that forced valid model
      output to `irrelevant`.
- [x] Keep JSON parsing, required-field checks, boolean coercion,
      `risk_level` enum validation, and `evidence_quotes` normalization.
- [x] Preserve `pending_review` fallback behavior for malformed JSON, missing
      fields, invalid risk levels, provider errors, and timeouts.
- [x] Preserve AI trace/log redaction and prompt/request/response/comment
      truncation guardrails.
- [x] Add regression coverage for valid model output preservation, including
      the `北京海安律所` versus `北京海安律师事务所` variant case.
- [x] Update CR-045/Phase 7.2 documentation to treat the previous
      target-evidence gate as historical and CR-096 as the current
      postprocessing rule.

## CR-050 - Report Center Lead Status Filter Precision Regression Fix

Planning status:

CR-050 is a verified follow-up regression fix for the completed CR-045/Phase
7.2A-B filter-safety work. It does not reopen Phase 7, Phase 7.1, or Phase
7.2A-B historical completion records. It corrects the Report Center risk
filter semantics after manual acceptance found that the `疑似负面` filter could
still include `高风险` lead rows.

- [x] Keep `/api/monitor/leads?risk=high` exact to `lead_status=high_risk`.
- [x] Change `/api/monitor/leads?risk=negative` to exact
      `lead_status=suspected_negative` instead of all negative rows.
- [x] Add a derived exact `suspected_negative_count` summary field so
      `/api/monitor/reports?risk=negative` does not use total negative count
      that includes high-risk rows.
- [x] Preserve existing total negative summary/report-template compatibility
      while preventing it from driving exact status filters.
- [x] Add regression coverage proving high-risk and suspected-negative filters
      do not include each other.
- [x] Verify docs, targeted monitoring tests, Python compile, and frontend
      syntax after the fix.

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

## Phase 10 - Frontend Architecture And Technology Decision

Planning status:

Phase 10 is complete as a documentation and architecture decision phase. It did
not implement UI code changes.

- [x] Create and maintain `FRONTEND_ARCHITECTURE.md` as the frontend
      architecture source of truth.
- [x] Confirm the frontend stack before UI implementation.
- [x] Keep the accepted stack as Vanilla JavaScript plus CSS custom properties,
      with optional lightweight libraries only for focused charting or floating
      menu placement.
- [x] Keep the no-build deployment path unless a later CR changes it.
- [x] Update `AGENTS.md`, `AGENT_WORKFLOW.md`, and `scripts/check_docs.py` so
      agents discover `FRONTEND_ARCHITECTURE.md`.
- [x] Audit the current frontend file structure and decide the first redesign
      pass keeps `/monitor` as the entry while introducing local static CSS/JS
      module boundaries for Phase 11.

## Phase 10.5 - Phase 10-18 Global Plan Review Gate

Planning status:

Phase 10.5 is complete as a documentation-only review gate before Phase 11
implementation. It reviewed Phase 10-18 as one connected roadmap, not as
isolated phase readiness checks, and found no P0/P1 blockers after the
Phase 13, Phase 17, and Phase 18 granularity refinements.

- [x] Review whether Phase 10-18 as a whole can reach the final console goal:
      a task-loop-centered operations console covering task creation, runs,
      reports, and email delivery.
- [x] Review cross-phase dependencies and ordering, especially Phase 11 -> 12
      -> 13, Phase 14 -> 15, Phase 16 -> 17, and Phase 18 dependencies on
      frontend foundation and report snapshot data.
- [x] Review whether each phase and sub-phase has enough implementation
      granularity: clear files or data areas, allowed changes, forbidden
      changes, verification steps, and rollback path.
- [x] Review cross-phase impact risks: frontend module split, navigation
      rewrite, responsive behavior, run archive/noise fields, email delivery
      logs, report grouping, role visibility, and owner/workspace scope.
- [x] Review whether implementation batches protect existing core flows:
      login/logout, navigation, task wizard, run logs, report preview,
      account login, resource pages, modal behavior, and toasts.
- [x] Review whether data-model phases include compatible migration and
      backfill plans before frontend phases depend on new fields.
- [x] Record any accepted planning fixes in `TASKS.md`,
      `FRONTEND_ARCHITECTURE.md`, `TEST_PLAN.md`, `TRACEABILITY.md`, and
      `TEST_RESULTS.md` before generating a phase-specific execution goal.
- [x] Do not generate a Phase 11A-only execution goal until the global
      Phase 10-18 plan review has no P0/P1 blockers.

## Phase 11 - Frontend Design System

Planning status:

Phase 11 is planned and depends on Phase 10 and the completed Phase 10.5
global plan review gate. Do not implement Phase 11 as one large goal. Execute
it as Phase 11A-11D so each batch has a clear file boundary, verification
scope, and rollback path.

### Phase 11A - Frontend Module Boundary And CSS Token Layer

- [x] Create `api/webui/monitor/monitor.css`.
- [x] Create `api/webui/monitor/monitor.js`.
- [x] Reference the new local CSS/JS assets from `api/monitor_web/index.html`
      without removing existing inline CSS/JS.
- [x] Load `monitor.css` before the existing inline `<style>` block and load
      `monitor.js` after the existing inline `<script>` block.
- [x] Define CSS custom-property tokens for colors, typography, spacing,
      radius, shadows, z-index, status colors, and breakpoint values.
- [x] Use namespaced token variables such as `--color-*`, `--space-*`, and
      `--font-*`; do not define legacy aliases such as `--bg` or `--primary`
      in Phase 11A.
- [x] Keep `monitor.js` as a quiet module boundary with no console logging and
      no global variable/function definitions or UI behavior in Phase 11A.
- [x] Keep the visible UI unchanged in this batch.
- [x] Verify `/monitor` loads and the new CSS/JS assets return HTTP 200.
- [x] Verify login, navigation, task list, run center, and report preview still
      work through a browser smoke check.
- [x] Verify 1440px desktop, 1024px tablet, and 390px mobile layouts are
      unchanged.

### Phase 11B - Base Layout And Navigation Visual Foundation

- [x] Move base layout, shell, header, navigation, button, card, and toolbar
      styling into `monitor.css`.
- [x] Keep page structure and business data flow unchanged.
- [x] Apply the accepted Apple-style visual foundation to desktop layout and
      navigation.
- [x] Keep administrator and normal-user menu visibility unchanged.
- [x] Verify desktop 1440px navigation, page switching, login/logout, and core
      pages have no visible regressions.

### Phase 11C - Interaction Components And Floating Menu Fix

- [x] Add standard toast, loading, empty-state, modal, and action-menu styles
      to `monitor.css`.
- [x] Add a `MonitorUI` helper boundary in `monitor.js` for toast, loading,
      empty-state, menu close, and floating menu positioning helpers.
- [x] Replace clipped row action menu behavior with fixed or portal-style
      positioning.
- [x] Implement or equivalent `positionFloatingMenu(triggerEl, menuEl)`
      behavior.
- [x] Decide whether a local helper is enough or a lightweight floating
      positioning library is needed; record any new dependency in
      `DECISIONS.md` before adding it.
- [x] Ensure menus close on outside click, escape, page change, and successful
      action.
- [x] Verify account, proxy, report, AI, mail-template, and modal-contained row
      menus are not clipped by scroll containers or modal boundaries.
      Account, monitoring-task, AI-rule, and report row menus were verified
      with fixed viewport placement. Proxy, AI access, and mail-template
      surfaces currently expose direct edit/test/preview actions rather than
      row menus, so no clipped row-menu surface exists there in Phase 11C.
- [x] Move account, monitoring-task, and AI-rule row "more" menu content into
      page-level floating containers so table scroll areas and sticky action
      columns cannot cover the popup content.

### Phase 11D - Responsive Foundation

- [x] Implement the accepted breakpoints: mobile `< 768px`, tablet
      `768px - 1279px`, desktop `>= 1280px`.
- [x] Add mobile navigation using a top-left hamburger button and left-side
      drawer, or document an equivalent touch-safe alternative before
      implementation.
- [x] Make toolbars, form grids, metric grids, modals, and dense tables usable
      on tablet and mobile.
- [x] Keep dense operational tables at least scroll-safe on mobile; page-level
      card conversions can be completed in the later page-specific phases.
- [x] Verify 1440px desktop, 1024px tablet, and 390px mobile layouts have no
      severe overlap, hidden primary actions, or hover-only required paths.

## Phase 12 - Navigation And Page Entry Redesign

Planning status:

Phase 12 is planned and depends on Phase 11. Execute it as Phase 12A-12B.

### Phase 12A - Navigation Structure And Login Landing

- [x] Route login success to Operations Home.
- [x] Move authenticated user identity and logout into one top-right control
      group on desktop and a predictable account area on mobile.
- [x] Replace Resource Management and System Configuration popover navigation
      with expandable navigation groups.
- [x] Preserve administrator and normal-user menu visibility rules.
- [x] Verify login, logout, session restore, and page switching.

### Phase 12B - Page Entry And Role Flow

- [x] Rebuild page entries around the monitoring task loop: Operations Home,
      Monitoring, Run Center, Report Center, Email Delivery status, and
      administrator resource support.
- [x] Standardize page title, description, primary action, and toolbar areas.
- [x] Add task-loop shortcuts where useful: create task, view runs, view
      reports, inspect email delivery, and resolve resource issues.
- [x] Verify administrator and normal-user paths separately.
- [x] Confirm no hidden administrator resource details leak into normal-user
      entry points.

## Phase 13 - Overview Operations Home Redesign

Planning status:

Phase 13 is planned and depends on Phase 10-12. Execute it as Phase 13A-13C.
Do not rebuild data aggregation, desktop visual layout, and responsive/role
views in one goal.

### Phase 13A - Operations Home Data Layer

- [x] Define the operations-home API contract under the existing monitor API
      surface, reusing `api/routers/monitor.py` unless a small helper module is
      justified.
- [x] Define data sources for task health, run activity, report activity,
      email delivery status, suspected lead metrics, and resource health.
- [x] Reuse existing tables where possible and document any missing metric as
      a later enhancement instead of fabricating data.
- [x] Preserve administrator and normal-user owner/workspace scope in every
      aggregate.
- [x] Keep the existing `/api/monitor/dashboard` response compatible until the
      frontend migration is complete, or document the response versioning
      strategy before changing it.
- [x] Verify API results for administrator and normal-user data scopes.

### Phase 13B - Operations Home Desktop Visual Metrics

- [x] Replace the text-heavy overview content with a desktop operations home
      using Phase 11 design tokens and component patterns.
- [x] Add visual task, run, report, email delivery, suspected lead, and concise
      resource-health metric sections.
- [x] Add drilldown links into Monitoring, Run Center, Report Center, Email
      Delivery status, and administrator resource pages where permitted.
- [x] Decide whether a chart library is needed; record any chart dependency in
      `DECISIONS.md` before adding it.
- [x] Keep long system-running, scheduler, platform, browser, and deployment
      diagnostic blocks out of the default home page.
- [x] Verify desktop 1440px layout, drilldowns, and role-safe metric wording.

### Phase 13C - Operations Home Responsive And Role Views

- [x] Adapt the operations home for 1024px tablet and 390px mobile layouts.
- [x] Ensure normal users see only own tasks, runs, reports, and business-safe
      health signals.
- [x] Ensure administrators see resource health as concise signals with
      drilldowns to the correct resource pages.
- [x] Move detailed system diagnostics to System Diagnostics or keep only a
      compact health summary on the home page.
- [x] Verify no horizontal overflow, overlapping metric cards, hidden primary
      actions, or role leakage on tablet and mobile.

## CR-097 - Operations Home Visual Density Reduction

Planning status:

CR-097 is an existing-feature optimization for the current Operations Home.
It keeps the same data contract and drilldowns while making the first screen
more visual and less wordy.

- [x] Compress the Operations Home first viewport so the data reads like a
      cockpit rather than a prose summary.
- [x] Prefer visual encodings and compact numeric signals over explanatory
      helper copy on the home surface.
- [x] Replace the old large detail/workbench feeling with five compact KPI
      meters, one dominant flow chart, platform breakdown with heatmap blocks,
      delivery/lead composition, and a compact visual priority panel.
- [x] Keep desktop, tablet, and mobile layouts readable with no overflow or
      overlap.
- [x] Keep desktop and tablet Operations Home within the shell/navigation
      height by hiding the shortcut dock outside mobile and using a bounded
      chart-first grid.
- [x] Preserve role-safe resource visibility and administrator diagnostics
      gating.

## CR-098 - Operations Home Data-First Visual Refit

Planning status:

CR-098 is the follow-up existing-feature optimization for the current
Operations Home. It keeps CR-097 verified as history while tightening the home
into a data-first dashboard that follows the existing project design system.

- [x] Refit the Operations Home to use the Phase 21 light enterprise shell,
      teal accent, compact typography, modest radii, and restrained risk color.
- [x] Replace the remaining status/prose-heavy read with KPI micro bars, a
      five-stage flow chart, compact priority bars, platform/delivery
      breakdowns, and resource bars.
- [x] Hide the shortcut dock through the final CR-098 cascade so it no longer
      increases the desktop/tablet or mobile page length.
- [x] Keep the desktop 1440x900 and tablet 1024x768 Operations Home content
      within the left navigation/shell height.
- [x] Keep mobile chart-first and remove duplicated page-kicker copy from the
      mobile overview.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-099 - Operations Home Legend-First Visual Clarity

Planning status:

CR-099 is the follow-up existing-feature optimization for the current
Operations Home. It keeps CR-098 verified as history while making the visual
language more self-explanatory through visible keys, normalized icon scale,
and calmer palette separation.

- [x] Add visible legend/direct-key treatment to the flow chart,
      delivery/review chart, attention panel, and resource chart.
- [x] Normalize KPI and alert icon sizes so they stay visually secondary to
      the values and bars.
- [x] Change the platform breakdown to a donut plus labeled bar list with a
      category palette that stays distinct from status colors.
- [x] Keep the desktop 1440x900 and tablet 1024x768 Operations Home content
      within the left navigation/shell height.
- [x] Keep mobile readable with the same chart-first order, visible keys, and
      no horizontal overflow.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-100 - Operations Home Dense Visual Composition

Planning status:

CR-100 is the follow-up existing-feature optimization for the current
Operations Home. It keeps CR-099 verified as history while reducing empty
surface through content-sized layout rules and denser chart composition.

- [x] Stop stretching desktop/tablet dashboard panels to fill empty viewport
      height when the real data is sparse.
- [x] Keep the same one-screen maximum height boundary relative to the left
      navigation/shell.
- [x] Add denser graphical structure to the flow chart without changing its
      real field meaning.
- [x] Keep the page chart-first and avoid adding prose/table filler.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-101 - Operations Home Flow Chart Layer Separation

Planning status:

CR-101 is the follow-up existing-feature optimization for the current
Operations Home after live browser review of CR-100. It keeps CR-100 verified
as history while refining only the `流程总览` internal layering.
After CR-105, this is historical/archive-only evidence and must not be treated
as a current requirement to preserve `流程总览` or `operations-stage-*` DOM.

- [x] Split the flow chart into a clear head layer and a separate internal plot
      area.
- [x] Keep the same one-screen maximum height boundary relative to the left
      navigation/shell.
- [x] Reduce the visual weight of the stage backdrop columns so they behave as
      substrate instead of competing cards.
- [x] Keep the stage nodes as the foreground layer with clearer labels, counts,
      and pending-state readability.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-102 - Operations Home Flow Chart Node Simplification

Planning status:

CR-102 is the follow-up existing-feature optimization for the current
Operations Home after live browser review of CR-101. It keeps CR-101 verified
as history while refining only the `流程总览` node payload and density.
After CR-105, this is historical/archive-only evidence and must not be treated
as a current requirement to preserve `流程总览` or `operations-stage-*` DOM.

- [x] Remove the separate node helper-text row from the flow chart body.
- [x] Keep pending state visible only as a compact chip when non-zero.
- [x] Tighten node spacing, orb size, connector placement, and bar height so
      the plot reads as one coherent chart block.
- [x] Keep the same one-screen maximum height boundary relative to the left
      navigation/shell.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-103 - Operations Home Flow Chart Semantic Trend Rebuild

Planning status:

CR-103 is the follow-up existing-feature optimization for the current
Operations Home after live browser review of CR-102. It keeps CR-101 and
CR-102 verified as history while rebuilding only the `流程总览` chart semantics.
After CR-105, this is historical/archive-only evidence and must not be treated
as a current requirement to preserve `流程总览` or `operations-stage-*` DOM.

- [x] Rebuild `流程总览` as one chart-first stage trend view instead of mixed
      orb/bar node cards.
- [x] Keep the visible legend explicit for `总量` and `异常 / 待处理`.
- [x] Keep the same five monitoring stages and current dashboard data
      contract without inventing historical time-series fields.
- [x] Keep the same one-screen maximum height boundary relative to the left
      navigation/shell.
- [x] Preserve all existing dashboard data contracts, drilldowns, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-104 - Operations Home Data Cockpit Moderate Rebuild

Planning status:

CR-104 is the follow-up existing-feature optimization for the current
Operations Home after CR-103. It keeps CR-097 through CR-103 verified as
history while rebuilding the overall first-screen composition into a chart-
first data cockpit.

- [x] Keep the existing `/api/monitor/dashboard` contract and current
      drilldown targets.
- [x] Add a frontend overview view-model layer for the current Operations Home.
- [x] Use read-only frontend aggregation from `/runs` and `/reports` when the
      dashboard payload does not include 7-day or 14-day trend buckets.
- [x] Replace the current first-screen composition with compact KPI strip,
      `监控走势`, `问题分布`, `平台分布`, and `交付 / 复核`.
- [x] Reduce resource health to an administrator-only compact entry and hide
      the resource block entirely for normal users.
- [x] Keep the same one-screen maximum height boundary relative to the left
      navigation/shell.
- [x] Preserve all existing dashboard data contracts, role gating,
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, and report-scope behavior.

## CR-105 - Operations Home ECharts Dashboard Rebaseline

Implementation status:

CR-105A is implemented and verified for the `/monitor` Operations Home first
screen. It replaces the CR-104 handcrafted chart baseline with locally
vendored ECharts for the core dashboard charts, while keeping CR-097 through
CR-103 as historical/archive-only design iterations and preserving Task
Center, Run Detail, drawer, modal, enhanced select/date, routing, owner-scope,
report-scope, and top-bar refresh behavior.

- [x] Perform a todo baseline review for Operations Home requirements across
      `TASKS.md`, `CHANGE_REQUESTS.md`, `CURRENT_STATE.md`, `TRACEABILITY.md`,
      `TEST_PLAN.md`, current code, and existing dashboard tests.
- [x] Classify CR-097 through CR-103 as historical/archive-only for future
      dashboard work while preserving them as verified implementation history.
- [x] Keep CR-104 as the code baseline before CR-105 implementation:
      compact KPI strip, `监控走势`, `问题分布`, `平台分布`, `交付 / 复核`,
      administrator-only resource health, current dashboard API, role gating,
      drilldowns, and shell-height boundary.
- [x] Accept Apache ECharts as the current `/monitor` charting library for the
      core CR-105 dashboard charts; the library must be vendored locally under
      the existing static asset path and must not be loaded from a CDN. The
      expected file path is
      `api/webui/monitor/vendor/echarts.min.js`, served as
      `/static/monitor/vendor/echarts.min.js`.
- [x] Explicitly reject continuing CR-104 handcrafted SVG path geometry or
      custom DOM chart layout calculations for core CR-105 dashboard charts;
      SVG icons and ECharts internal rendering remain allowed, but
      `.operations-trend-svg`, `operationsTrendLinePath()`, and
      `operationsTrendAreaPath()` are the current baseline to replace.
- [x] Define the chart plan: KPI micro charts, 7/14-day dual-line trend with
      optional 30-day mode only when existing data supports bounded frontend
      aggregation, issue-distribution horizontal bars, platform distribution
      bar/donut-plus-bar, delivery/review stacked bars, and administrator
      resource segmented bars, with future heatmap/matrix only when data
      density justifies it.
- [x] Define the dashboard goal and reading path: help users judge within
      about 10 seconds whether today's monitoring is normal, where the risk or
      exception is, and where to click next.
- [x] Define the reusable first-version data set from current APIs:
      tasks, runs, reports, mail state, suspected negative/high-risk leads,
      manual review, platform distribution, and administrator-only resource
      health.
- [x] Defer later enhancement data explicitly: task funnel, platform risk
      matrix, keyword heat, AI quality, and task rankings cannot be invented
      as required persisted metrics for the first CR-105 implementation.
- [x] Keep missing trend buckets as frontend read-only aggregation from
      existing `/runs` and `/reports` for the first CR-105 implementation;
      backend trend buckets require a later accepted CR.
- [x] Define the dashboard color ledger, role boundaries, visible legend/direct
      label rule, responsive layout, interactions, loading/empty/stale/error
      states, and non-goals.
- [x] Define module alignment as a hard CR-105 acceptance rule: card edges,
      gutters, title/header heights, key numbers, legends, chart plot origins,
      KPI internals, lower-card heights, and normal-user reflow must align
      rather than appearing as independent uneven panels.
- [x] Define the six stable containers and desktop/tablet/mobile layout:
      KPI strip, `监控走势`, `问题分布`, `平台分布`, `交付 / 复核`, and
      administrator-only `资源健康`, with normal-user lower modules reflowing
      to fill the hidden resource-health space.
- [x] Remove current planning/test language that would require preserving
      `流程总览`, `operations-stage-*`, or earlier no-chart-library constraints
      in the verified CR-105 implementation.
- [x] Add local Apache ECharts vendor asset at
      `api/webui/monitor/vendor/echarts.min.js` before chart implementation and
      verify it is served as `/static/monitor/vendor/echarts.min.js` without a
      CDN or frontend build pipeline.
- [x] Implement the CR-105 chart-dashboard UI, keeping
      Task Center, Run Detail, drawer, modal, enhanced select/date, routing,
      owner-scope, report-scope, and top-bar refresh behavior unchanged.
- [x] Verify CR-105A with targeted static tests, JavaScript parse checks,
      local-vendor HTTP checks, in-app browser role checks for administrator
      and normal-user sessions, and responsive checks at `1440x900`,
      `1024x768`, and `390x844`.

## CR-106A - Operations Home Data-Aware Signal Refinement

Implementation status:

CR-106A is implemented and verified as the current Operations Home optimization
after CR-105A. It stays within the existing frontend and dashboard-data
boundaries: no backend schema changes, no new persisted metrics, no Task Center
or Run Detail behavior changes, and no hidden resource details for normal
users.

- [x] Preserve CR-105A as the verified ECharts dashboard baseline and keep
      CR-097 through CR-103 historical/archive-only.
- [x] Record a read-only local data baseline as planning evidence, making clear
      that sample counts can change and are not product acceptance constants.
- [x] Refine the Operations Home top status summary so today's health is
      readable in one concise line before decoding individual charts.
- [x] Adjust `问题分布` semantics so high-risk leads, pending review, mail
      failure, and run failure/skip are prioritized by action severity.
- [x] Adjust `平台分布` semantics so platform volume and platform failure
      signals can be distinguished from existing run summary data.
- [x] Clarify the `邮件` module as report-level delivery state from
      `reports.email_status` for CR-106A.
- [x] Keep `email_delivery_logs` dashboard aggregation out of CR-106A and
      track it under CR-106B until explicitly accepted.
- [x] Make administrator `资源健康` action-oriented while preserving
      normal-user hiding of account/proxy/AI/SMTP/session details.
- [x] Improve mobile first-screen density so KPI cards do not prevent
      `监控走势` and `问题分布` from appearing early.
- [x] Verify administrator and normal-user views at `1440x900`, `1024x768`,
      and `390x844`.
- [x] Update `CURRENT_STATE.md`, `TEST_RESULTS.md`, and `TRACEABILITY.md` after
      implementation and verification.

## CR-106B - Email Delivery Log Dashboard Aggregation

Planning status:

CR-106B is a candidate follow-up and remains `Needs Confirmation`. It must not
be implemented as part of CR-106A.

- [ ] If accepted later, define dashboard mail-health aggregation from existing
      `email_delivery_logs` while preserving report-level
      `reports.email_status` compatibility.
- [ ] If accepted later, add scoped/safe-count tests proving no recipients,
      SMTP secrets, proxy URLs, cookies, profile paths, account details, or raw
      sensitive delivery errors are exposed on Operations Home.

## CR-107 - Windows One-Click Local Startup Launcher And Browser URL Separation

Lifecycle status:

CR-107 is implemented and verified on current `main`. It does not change
backend APIs, dashboard behavior, crawler behavior, or browser UI. It adds a
Windows one-click startup wrapper and the supporting tests/docs that prove the
bind host and browser URL stay separate.

- [x] Add a shared startup helper that computes the service bind host/port and
      the browser open URL as separate values.
- [x] Add a Windows launcher entry point that starts the service, waits for
      health, and opens the browser URL.
- [x] Preserve the existing service-only startup commands.
- [x] Update the startup instructions in `README.md` and
      `docs/SERVER_DEPLOYMENT.md`.
- [x] Verify the new launcher with targeted tests, docs consistency, and
      `git diff --check`.

Implementation status:

- [x] Add a shared startup helper that computes the service bind host/port and
      the browser open URL as separate values.
- [x] Add a Windows launcher entry point that starts the service, waits for
      health, and opens the browser URL.
- [x] Preserve the existing service-only startup commands.
- [x] Update the startup instructions in `README.md` and
      `docs/SERVER_DEPLOYMENT.md`.
- [x] Verify the new launcher with targeted tests, docs consistency, and
      `git diff --check`.

## CR-122 - Browser Sync New-Account Entry And Promotion Reliability

Implementation status (2026-07-21): verified.

- [x] Register the new-account entry regression and preserve QR, manual Cookie,
      Profile-authority, and server-first boundaries.
- [x] Show browser auto-sync for an unsaved account when its capability gate
      passes, and require an account name before any login action.
- [x] Reuse the existing account persistence path before browser launch so the
      session is bound to an account ID and generated `profile_key` without a
      QR session.
- [x] Add bounded Cookie hydration, invalid empty-name artifact filtering,
      valid empty-value preservation, and owned-process exit-race handling.
- [x] Add deterministic regression coverage and verify the new-account button
      state through the running monitor UI.
- [x] Complete documentation/compile/diff gates and independent read-only
      full-diff review.
- [x] Complete one disposable new-account browser-sync operator acceptance
      without generating QR first, then pass the normal account Profile check.

## CR-123 - Platform Account Login Method Hierarchy And Cookie Roundtrip

Implementation status (2026-07-21): verified.

- [x] Register the UI hierarchy and structured Cookie import regression.
- [x] Add RED coverage for three peer login panels and structured browser-sync
      export roundtrip through Cookie login.
- [x] Implement peer QR, Browser, and Cookie UI modes without adding a backend
      login type or duplicating the Cookie entry.
- [x] Route QR and browser progress to their own panels and preserve local
      visible-login fallback behavior.
- [x] Accept Structured Cookie Protocol V1 JSON and plain Cookie headers through
      the same Cookie promotion endpoint without losing scoped attributes.
- [x] Run focused/full/syntax/docs/diff/browser gates and independent read-only
      full-diff review.

## CR-124 - Saved Login Recheck, Test Isolation, And Portable Cookie Clarity

Implementation status (2026-07-21): verified.

- [x] Register the real-runtime contamination and Cookie portability regression.
- [x] Select disposable test database, key, and Profile paths before application
      imports and remove them after the test session.
- [x] Add saved Cookie/Profile recheck as the first recovery action for an
      account incorrectly or legitimately marked `requires_relogin`.
- [x] Clarify that administrator reveal/copy returns the complete structured
      cross-computer Cookie artifact accepted by Cookie login.
- [x] Add different-installation-key roundtrip and runtime-isolation regression
      coverage.
- [x] Restore and validate the affected saved Profile, verify the managed
      browser window opens, and complete final docs/review gates.

## CR-125 - Platform Account Identity List Simplification

Implementation status (2026-07-21): verified.

- [x] Register the list-density optimization and preserve the detail/API data
      boundary.
- [x] Add RED/GREEN coverage for hidden raw identity text and dedicated
      recognition-time column order.
- [x] Keep avatar/display name in the identity cell and move recognition time
      immediately before recent validation.
- [x] Verify desktop and mobile table geometry plus detail open/close behavior.
- [x] Run focused and complete monitoring regression plus syntax checks.
- [x] Complete documentation gates and independent read-only review.

## CR-126 - Xiaohongshu Self-Info Display Name Extraction

Implementation status (2026-07-21): verified.

- [x] Register the missing Xiaohongshu display-name regression and stable-ID
      boundary.
- [x] Add RED coverage for self-info identity extraction and profile/API merge.
- [x] Reuse the signed readiness response for display name and avatar metadata.
- [x] Preserve the profile URL identifier while merging display metadata.
- [x] Pass focused, complete monitoring, and current saved-Profile checks.
- [x] Complete documentation gates and independent read-only review.

## CR-127 - Unified Account Login Authority And Cookie/Profile Reliability

Implementation status (2026-07-21): verified.

- [x] Register the coupled login-authority, QR-image, Cookie-promotion, reveal,
      and account-form regressions with explicit data/security boundaries.
- [x] Add RED coverage for cross-method supersession, promoted authority,
      non-QR rejection, interrupted manual promotion, unconditional reveal
      registration, Cookie/Profile import, and simplified UI structure.
- [x] Implement one account-scoped login-attempt supersession path used by QR,
      Browser, visible-browser, and manual Cookie entry points.
- [x] Validate QR image bytes before returning them and keep verification/SMS
      states distinct from QR extraction failure.
- [x] Preserve and deterministically repair committed Cookie/Profile authority;
      make startup recovery terminal-safe for interrupted manual promotions.
- [x] Always register administrator no-store Cookie reveal and keep stored
      Cookie access independent from Browser-sync feature availability.
- [x] Remove duplicate source/notes/error controls and move SVG reveal/copy
      controls inside the complete Cookie field.
- [x] Verify focused/full/syntax/docs/diff/live browser/current Profile/minimal
      collection gates.
- [x] Complete independent read-only review and close CR-125/CR-126/CR-127
      documentation state together.

## CR-128 - Saved Cookie Recovery After Profile Drift

Implementation status (2026-07-22): verified.

- [x] Register the saved-Cookie/Profile-drift regression and keep Profile as
      normal crawl authority with Cookie as recovery material.
- [x] Add RED/GREEN coverage for limited-account recovery, source
      preservation, one account-scoped login attempt, candidate identity
      mismatch rollback, active identity mismatch rollback, and UI visibility.
- [x] Reuse the existing account lock, login-session arbitration, canonical
      Cookie validator, and fixed-path promotion journal for explicit recovery.
- [x] Require the already-bound platform account identity in both candidate and
      post-swap active Profile checks; preserve all prior material on failure.
- [x] Verify an expired saved Cookie returns a terminal conflict and leaves the
      active account/Profile, encrypted Cookie, source, locks, and sessions
      intact.
- [x] Hold the account login-start lock across Profile recheck and recovery so
      an older recovery cannot supersede a newer QR/Browser/Cookie login.
- [x] Reject missing or unknown Cookie provenance before promotion and return
      customer-actionable messages instead of internal reason codes.
- [x] Complete fresh designated Xiaohongshu browser-sync login, final service
      restart, real crawl, post-crawl Profile check, and cleanup verification.
- [x] Close the final focused independent re-review after focused `14`, adjacent
      `101`, complete monitoring `696`, compile, documentation, whitespace, and
      live runtime gates pass.

## CR-121 - Crawler Account Identity Snapshot Header Binding

Implementation status (2026-07-20): verified. This is a crawler regression
follow-up and does not reopen completed Phase 5.1 or CR-118.

- [x] Register the observed designated-account mismatch and strict-validation
      boundary.
- [x] Add RED coverage for prepared-page versus background-page request
      evidence.
- [x] Scope request evidence to the prepared managed page.
- [x] Re-run controlled collection and prove at least one stored content row.
- [x] Run focused/full/docs/compile/diff gates and independent review.

## CR-129 - Account Profile And Platform Request Identity Consistency

Implementation status (2026-07-22): Verified. Packets A-E, automatic
compatibility, and the designated Douyin/XHS real and restart lanes pass. This
is a new follow-up
after the verified CR-128 baseline. It does not reopen Phase 5.1, CR-112, or
the verified CR-119 through CR-128 history.

Baseline review classification:

- CR-112 and CR-119 through CR-128: already completed / historical Verified;
  preserve their boundaries and evidence.
- CR-047 Linux/server-like identity proof: operator-gated and independent.
- CR-070: future-valid and remains after CR-112 and CR-129.
- CR-092 through CR-094: future-valid or Needs Confirmation; outside this lane.
- Platform request identity split: active/current CR-129 follow-up.

Readiness gate: passed on 2026-07-22 after two Claude read-only review rounds.

- [x] Complete the CR-095-compatible plan and formal-document synchronization.
- [x] Complete deep plan-cross-validation with Claude Code using only Read,
      Grep, and Glob.
- [x] Classify all TODO items and resolve every blocker/material refinement.
- [x] Reach `Overall verdict=READY`, `Blocking findings=None`, and
      `Material refinements=None` before code implementation.
- [x] Run docs consistency, documentation tests, and `git diff --check`.

Hard boundaries:

- [x] Keep the committed Profile as crawl/browser authority and encrypted
      Cookie as initialization, refresh, recovery, and migration material.
- [x] Keep BrowserEnvironmentProvider as the only browser/Profile/UA/proxy
      resolver and make platform clients consume its frozen request projection.
- [x] Keep account, platform, `profile_key`, identity revision, browser,
      proxy, resolution, attempt, and run binding explicit and immutable per
      attempt.
- [x] Preserve CR-112 same-machine Windows and Packet B component decisions;
      keep CR-070 after this lane.
- [x] Use only designated real accounts 8972 (Douyin) and 9196 (XHS);
      protect 9197 and 9198 from collection.

Atomic packages:

- [x] Packet A: add the versioned immutable PlatformRequestEnvironment (or
      reviewed equivalent) and safe validation/serialization.
- [x] Packet A: add RED tests for missing/conflicting/expired/cross-account
      environment and secret-leak cases.
- [x] Packet B: bind XHS Cookie, a1, web_session, UA/UA-CH,
      Accept-Language, URL/query/body, signer, final headers, Profile, and
      proxy to one frozen environment.
- [x] Packet B: prove identity mismatch and signature/request drift fail before
      dispatch while preserving committed Profile/Cookie authority.
- [x] Packet C: bind Douyin Cookie, webid, verifyFp, msToken, ttwid, a_bogus,
      UA/UA-CH, page/local-storage evidence, request values, Profile, and
      proxy to one frozen environment.
- [x] Packet C: remove unbound fixed/cross-account request values and add
      account-isolation and signer/input equality tests.
- [x] Packet D: add typed platform/environment errors, bounded transient-only
      retry, terminal session states, stale callback guards, and safe child
      handles with argv/environment/log tripwires.
- [x] Packet E: verify QR, Browser, manual Cookie, saved Profile, restart,
      manual, scheduled, server-like, and normal monitor paths.
- [x] Packet E: serially prove exact identity and at least one stored real item
      for designated Douyin 8972 and XHS 9196 with `fallback_used=false`.
- [x] Packet E: prove designated Douyin 8972 strong identity, normal monitor
      collection, three persisted new items, contract-v3 endpoint policy, and
      `fallback_used=false` without using protected accounts.
- [x] Packet E: complete designated XHS 9196 strong identity and persisted-item
      proof, then restart the service and repeat bounded Profile checks/crawls.

Per-package gates:

- [x] Reproduce the issue and add a failing RED test before the fix.
- [x] Verify focused and affected/full tests, compile, JavaScript checks,
      documentation checks, whitespace, and independent read-only review.
- [x] Synchronize CHANGE_REQUESTS, TASKS, CURRENT_STATE, TEST_RESULTS,
      TRACEABILITY, DECISIONS, and specialist documents after each package.
- [x] Create one atomic commit only after the package evidence is complete.

Packet A receipt (2026-07-22): `19` focused tests, `228` affected tests, and
`715` complete monitoring tests passed. Compile, docs consistency,
documentation regression, whitespace, and independent Claude read-only review
passed. No real account, Profile, Cookie, proxy, browser, or platform traffic
was used. Packet D owns the remaining full child-process tripwires.

Packet D receipt (2026-07-22): `84` dedicated request/terminal tests and `704`
complete monitoring tests pass. The implementation adds the strict terminal
contract, transient-only bounded retry, one-use plan/result handles, Windows
process-tree cleanup, pre-write managed-log redaction, and typed XHS/Douyin
platform failures. The first independent review findings were either fixed
with RED/GREEN coverage or disproved by current call-chain evidence; focused
re-review returned `PASS`, no remaining P0/P1/P2, and atomic readiness `YES`.
The complete repository collection reports `817 passed, 8 skipped, 7 failed`:
six Redis-dependent failures while local Redis is not running and the
documented pre-existing XHS Excel factory assertion. Packet E remains the real
compatibility/identity gate.

Packet E receipt (2026-07-22): affected regression passes `809` and the CR-129
monitor selection passes `10`. Repository-wide collection reports `836 passed,
8 skipped, 7 failed, 4 warnings`; the seven failures remain the six local-Redis
dependencies and the pre-existing XHS Excel factory assertion. Douyin run
`16854` used exact account `8972`,
stored three new items, emitted contract-v3 request proof with
`fallback_used=false`, and passed strong identity and real-log leakage checks.
After service restart, run `16855` again passed and stored one new item with
the same safe proof; focused Claude re-review returned `PASS` with no P0/P1/P2.
The audit also found scheduled run `16846` had automatically selected protected
account `9198` from an unbound existing daily job before the explicit guard; it
stopped at `requires_relogin` preflight, made no platform request, stored no
content, and left Profile/Cookie digests unchanged.
XHS sessions `6422` through `6425` reached bounded timeout and preserved the
committed authority. Diagnostic session `6426` exposed the lowercase
`user-agent` signed-UA mismatch; RED/GREEN coverage fixed the case-insensitive
header projection and removed its failed candidate. Session `6427` and
promotion `518` succeeded. Exact account `9196` passed strong identity before
and after restart; monitor runs `16856` and `16857` persisted 20 and 8 new XHS
contents with contract-v3 signed HTTP 200 proof and `fallback_used=false`.
Acceptance artifact/log and current-process argument scans found zero exact
Cookie fragments or pairs. Protected accounts `9197` and `9198` were not used
by the designated/manual acceptance lane.

## CR-130 - Cookie Account Save Promotion Consistency

Implementation status (2026-07-22): Verified. This is a regression follow-up
to the verified CR-123/CR-127 Cookie login flow and does not reopen those
completed CRs.

- [x] Register the observed new-account Cookie submission gap and preserve the
      Profile/Cookie authority boundary.
- [x] Reproduce the gap: footer `保存账号` persisted metadata without invoking
      Cookie promotion, leaving no committed Cookie/Profile material.
- [x] Add RED/GREEN frontend contract and browser-behavior coverage for both
      Cookie save controls, empty new-account input, and existing-account
      metadata-only save.
- [x] Route pending Cookie submission from the footer through the existing
      candidate Profile promotion service.
- [x] Run affected/full monitoring regression, compile, JavaScript, docs,
      whitespace, and independent read-only review.
- [x] Fix the review finding on the promotion failure return contract and
      rerun focused/full regression and final checks.
- [x] Update the live service and verify a disposable operator account can be
      created from a copied Cookie and pass identity/login-state checking.
- [x] Record final evidence and close the CR as Verified.

Live receipt (2026-07-22): test account `9212` reached login session `6434`
`success`, promotion `525` `committed`, Profile runtime version `1`, and
account `active` with no current error. No protected collection account was
changed.

## CR-133 - Windows Clean-Computer One-Click Bootstrap

Implementation status (2026-07-22): implementation, isolated Windows
first-run verification, and independent review pass; second-computer operator
acceptance remains pending. CR-117 and CR-132 browser selection and
account/Profile/Cookie behavior remain closed historical baselines.

- [x] Audit the clean-Windows launcher, dependency, data-directory,
      administrator, port, browser-install, and proxy boundaries.
- [x] Register the requirement, decisions, scope, tests, and traceability.
- [x] Add a shared PowerShell bootstrap for project-local `uv`, locked
      dependency sync, and both local launcher modes.
- [x] Add startup preflight for data storage, disk space, port, schema, and
      initial administrator setup.
- [x] Bound Playwright Chromium installation and preserve safe actionable
      diagnostics.
- [x] Add focused regression coverage without using real accounts or runtime
      data.
- [x] Run an isolated fresh-environment first start and verify owned-process
      health plus `/monitor` reachability.
- [x] Run adjacent/full/static/documentation gates.
- [x] Complete independent read-only full-diff review.
- [ ] Record second-computer pull/start/login acceptance after the reviewed
      change is available on `main`.

## CR-135 - Second-Computer Login Budget And Profile Preservation

Implementation status (2026-07-23): implementation and local verification are
complete after controlled affected-computer diagnostics on `main@6d70ee0`
proved the QR fallback-budget, 90-second Browser-sync cap, and
HasUserLogin-only Profile-loss regressions. Merge and affected-computer
operator acceptance remain.

- [x] Reproduce and classify the affected-computer QR, timeout, and
      Browser-sync candidate failures with redacted evidence.
- [x] Confirm the effective 90-second wrapper around the configured 600-second
      operator-login wait.
- [x] Confirm that Browser sync clears the candidate's LocalStorage before
      Cookie-only validation and that the captured Douyin Cookie set lacks
      `LOGIN_STATUS` while the visible Profile has `HasUserLogin=1`.
- [x] Add RED coverage for short QR probing, independent acquisition/validation
      timing, and retained Browser-sync candidate storage.
- [x] Preserve the exact Browser-sync candidate Profile while keeping manual
      Cookie promotion on a fresh empty candidate.
- [x] Separate the operator-login deadline from candidate and active Profile
      validation bounds.
- [x] Run focused, adjacent, complete monitoring, static, docs, whitespace, and
      real local Browser/QR verification.
- [x] Complete independent read-only review after final documentation sync.
- [ ] Record affected-computer pull/start/Douyin QR and Browser-login acceptance
      after the reviewed change is merged to `main`.

## CR-134 - Managed Login Environment Injection And Retry

Implementation status (2026-07-22): implementation and independent review
verified and merged through PR #17 on `main@d45de1a` after second-computer
Douyin and Xiaohongshu Browser login both failed managed environment validation
before operator login. Affected-computer operator acceptance remains pending.

- [x] Trace the shared failure to post-navigation environment validation.
- [x] Confirm that generated environment fields are desired injected state.
- [x] Add RED coverage for persistent-page injection, unprepared-page rejection,
      safe mismatch detail, transient wait probes, and serialized retry.
- [x] Apply the complete managed environment before platform navigation across
      Browser, QR, account-check, Profile-validation, and crawler paths.
- [x] Negotiate browser-version capability: keep core identity fields strict and
      record ineffective optional device fields as unsupported.
- [x] Default Windows one-click QR acquisition to headless while keeping Browser
      auto-sync headed.
- [x] Prevent Xiaohongshu QR/phone method copy from becoming a false SMS gate.
- [x] Accept tightly cropped platform QR images through an in-memory detection
      quiet zone and exclude generic Xiaohongshu `dragger` controls from slider
      detection.
- [x] Preserve overall login bounds while tolerating transient waiting probes.
- [x] Wait for remote cancellation before a replacement Browser session starts.
- [x] Run focused/full/static/docs, repository-wide baseline, real-Chrome
      hold/retry, and real headless Douyin/Xiaohongshu QR checks.
- [x] Complete independent read-only review.
- [ ] Record second-computer pull/start/Douyin/Xiaohongshu login acceptance
      after the reviewed change is available on `main`.

## CR-132 - Windows Login Bootstrap And Bounded Browser Startup

Implementation status (2026-07-22): implementation verified and independent
re-review passed; second-computer post-merge acceptance remains
operator-gated. This is a second-computer
Windows regression follow-up to CR-117, CR-120, CR-122, and CR-127. Their
verified account/Profile authority remains closed history.

- [x] Register the observed clean-computer launcher, new-account entry, QR
      timeout-cleanup, and browser startup-stage gaps.
- [x] Confirm Windows local browser auto-sync defaults and direct new-account
      Browser entry with the operator.
- [x] Add RED coverage for launcher defaults/instance ownership, new-account
      visible Browser entry, QR cleanup bounds, and browser-sync startup stage.
- [x] Apply reversible Windows local defaults without changing service-only or
      production/server behavior.
- [x] Bound and report QR/browser startup and cleanup stages without changing
      account attempt, Profile, Cookie, or promotion authority.
- [x] Reap driver-owned browser descendants on failed startup and require
      managed cleanup completion before Profile rollback; retain an
      unconfirmed cleanup as `recovery_required` without filesystem mutation.
- [x] Run focused and adjacent login regressions after the route, account-check,
      Profile-validation, launcher, and frontend timeout fixes.
- [x] Run complete monitoring, syntax/docs/whitespace, and rendered-browser
      gates.
- [x] Complete independent read-only re-review and close implementation.
- [ ] Record second-computer pull/start/login acceptance after the reviewed
      change is available on `main`.

## CR-120 - Local Visible Login Automatic Reconciliation

Implementation status (2026-07-20): verified. This is a local fallback
follow-up and does not reopen completed Phase 5.1 or CR-118.

- [x] Register the account-specific Profile authority and local-only boundary.
- [x] Add RED coverage for the missing automatic reconciliation path.
- [x] Add loopback CDP login-state probing and owned-window cleanup.
- [x] Automatically run the normal account Profile check after detection or
      operator close.
- [x] Add serial frontend polling, stale-attempt guards, and safe UI states.
- [x] Verify an already-authenticated local window through the live service.
- [x] Run focused/full/docs/compile/diff gates and independent review.

## CR-119 - Platform Account Recent Error Single-Line Truncation

Implementation status (2026-07-20): verified as a bounded Platform Accounts
frontend regression fix. It does not reopen completed Phase 3 or Phase 21.

- [x] Register the regression, display boundary, and verification contract.
- [x] Add RED coverage for one-line overflow and complete-text title handling.
- [x] Truncate both account-detail recent-error displays to one visible line.
- [x] Preserve the complete advanced error field and all account workflows.
- [x] Run focused/full/static/docs/browser gates.
- [x] Complete independent read-only review and close the CR.

## CR-118 - QR Login Success Monotonicity And Profile Restart Verification

Implementation status (2026-07-20): merged through PR #10 on `main@cd640f0`
and verified as a bounded Phase 5.1 login-flow
regression found by a designated local test account. Its post-restart session remains
successful after later polls and normal browser cleanup.

- [x] Record the real account/session evidence and regression boundary.
- [x] Add RED tests for terminal route lookup, persisted success monotonicity,
      and serial frontend polling.
- [x] Preserve successful login-session status and skip closed-browser polling
      for terminal sessions.
- [x] Serialize QR creation, concurrent GET polling, verification-code POSTs,
      and deletion for one session; prevent stale frontend callbacks from
      clearing a newer active session.
- [x] Check an existing persistent Profile before preparing a new QR login and
      cancel/await bounded polling tasks during timeout or cleanup.
- [x] Replace overlapping frontend interval polling with serial scheduling.
- [x] Restart the service and verify the designated test account through its existing
      `profile_key` Profile without re-login.
- [x] Run focused/full/docs/compile/diff gates and independent review.

## CR-117 - Windows Local Browser Selection And Playwright Chromium Bootstrap

Implementation status (2026-07-20): merged through PR #10 on `main@cd640f0`
and verified. The implementation adds one
stable local browser selection per deployment, preserves existing Profiles,
treats valid version changes as telemetry, and keeps server/Docker/per-account/
CR-112 boundaries. Final independent full-diff review returns `FINAL PASS`.

- [x] Register the accepted requirement, scope, test boundary, and traceability
      before changing startup code.
- [x] Add deterministic tests for local browser priority, persisted selection,
      existing-Profile compatibility, missing/conflicting saved browsers,
      Playwright repair, and non-blocking valid version changes.
- [x] Implement the versioned deployment-local browser selection manifest and
      connect it to the managed Provider.
- [x] Update both Windows local launchers to run the shared browser preflight
      without changing their service lifecycle.
- [x] Add a readable `uv` prerequisite check to the combined batch launcher.
- [x] Preserve CR-107 host/port/browser URL behavior and service-only/Docker
      boundaries.
- [x] Update startup/account/data-model documentation and record focused/full/
      docs/compile/real-read-only selection evidence.
- [x] Verify runtime browser version changes remain observable but do not force
      re-login when all other environment probes pass.
- [x] Complete final independent read-only review before closing CR-117.

## CR-108 - Local/Server Login Initialization And Verification Flow Hardening

Lifecycle status:

CR-108 is implemented and verified on current `main` after its documentation
gate. The older worktree
`C:\Users\Administrator\.codex\worktrees\1d0a\MediaCrawler` is a source of
historical server/Docker/SMS evidence, not a branch to merge directly. Its old
CR-107 and CR-108 entries must be remapped into this current CR-108.

Documentation gate:

- [x] Record CR-108 in `CHANGE_REQUESTS.md` with the current mainline CR
      number and explicit old-worktree remapping rule.
- [x] Add this CR-108 task block before any non-document code change.
- [x] Add CR-108 test coverage expectations to `TEST_PLAN.md`.
- [x] Add CR-108 traceability row in `TRACEABILITY.md`.
- [x] Update `CURRENT_STATE.md` to name CR-108 as the current objective after
      CR-107 and classify old worktree evidence.
- [x] Run `uv run python scripts/check_docs.py` for the docs-only gate.
- [x] Run `git diff --check` for the docs-only gate.

Docker/server packaging migration:

- [x] Selectively migrate `.dockerignore`, `Dockerfile`, `docker-compose.yml`,
      `deploy/docker/README.md`, and `deploy/docker/monitor.env.example` from
      the old server-login worktree.
- [x] Keep Docker defaults server-like: container-internal Playwright browser,
      `MONITOR_LOGIN_QR_HEADLESS=true`,
      `MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=false`, scheduler disabled, and AI
      skipped unless an operator enables them.
- [x] Document that `docker compose config` validates project packaging only
      and does not prove host Docker Desktop/WSL health.
- [x] Verify Docker packaging with `docker compose config` after migration.

Profile contention and first-run login flow:

- [x] Add failing regression coverage for starting a QR login while a same
      account/profile local login window is open.
- [x] Add failing regression coverage for starting a QR login while a same
      `profile_key` local login window is open.
- [x] Add failing regression coverage for switching from an active QR login
      session to a local manual login window.
- [x] Make the backend treat QR and local-window login as mutually exclusive
      for the same `profile_key`/runtime profile path.
- [x] Return customer-safe conflict states and messages instead of surfacing
      raw Playwright `TargetClosedError`/Profile contention text.
- [x] Keep production/server mode blocking local-window login and directing
      administrators back to the web QR/status flow.
- [x] Ensure local Windows first-run flow tells the operator to finish manual
      verification, close the browser window, and run account check/continue
      confirmation to persist the login state.

QR initialization hang hardening:

- [x] Add failing regression coverage for a half-initialized QR startup that
      hangs before a QR handle is registered.
- [x] Add failing regression coverage that fresh `preparing` sessions stay
      pending while QR startup is still inside the timeout window.
- [x] Add regression coverage that stale `preparing` sessions without a QR
      handle can expire to `qrcode_failed` after the timeout window.
- [x] Wrap server-side QR startup in an outer timeout and return a
      customer-safe timeout message instead of leaving the API request blocked.
- [x] Close partial Playwright/browser context state when QR startup is
      cancelled by the timeout.
- [x] Keep polling from overwriting a fresh initializing session with
      "browser session not running" before initialization has had time to
      complete.
- [x] Add failing regression coverage for a scan-time polling request that
      hangs inside MediaCrawler login-state detection.
- [x] Add failing regression coverage for a scan-time polling request that
      hangs while trying to rediscover the QR image.
- [x] Add failing regression coverage for the scan-time case where the
      MediaCrawler login-state method times out but same-account cookies already
      prove login success.
- [x] Bound QR polling substeps so the API keeps returning a pending
      `waiting_confirm` state instead of blocking the frontend polling loop.
- [x] Keep the MediaCrawler login-state method bounded without wrapping
      `_is_logged_in()` in an equal outer timeout, so cookie/session fallback can
      still advance the QR session to success after scanning.

Selective SMS/diagnostic migration:

- [x] Review old worktree diagnostics and SMS UI changes as source material
      only.
- [x] Do not migrate Douyin `#uc-second-verify` SMS submission in this CR-108
      batch because current main does not expose the old worktree's SMS submit
      route; keep the exact visible `验证` selector as future source material.
- [x] Keep the current customer-facing login modal action-oriented and do not
      migrate the old worktree's larger technical-diagnostics UI in this batch.
- [x] Do not add SMS receiving automation or verification bypass behavior.

Verification and documentation close-out:

- [x] Run
      `uv run python -m pytest tests/test_monitoring_mvp.py -k "windows_oneclick_launcher or login_session or qrcode or login_browser or verification_code or manual_sms"`.
- [x] Run `node --check api/webui/monitor/monitor.js`.
- [x] Run the existing inline monitor script parse check.
- [x] Run `uv run python scripts/check_docs.py`.
- [x] Run `git diff --check`.
- [x] Update `TEST_RESULTS.md` with what was verified on current main, what
      remains old-worktree/Tencent evidence, and what was not revalidated.
- [x] Update this task block and `TRACEABILITY.md` to match the final
      verified status.

## CR-109 - Monitoring Task Collection Rule Explanation Removal

Lifecycle status:

CR-109 is implemented and verified on current `main` as a narrow Monitoring
page UI cleanup. It removes the standalone "采集规则说明" helper block under the
task list without changing task workflows or backend behavior.

- [x] Record CR-109 in `CHANGE_REQUESTS.md`.
- [x] Remove the monitoring task page "采集规则说明" disclosure block.
- [x] Remove task-page CSS rules that only targeted the deleted disclosure.
- [x] Update static frontend coverage to assert that the monitoring task
      section no longer contains "采集规则说明".
- [x] Verify with the targeted Monitoring task visual-regression test,
      JavaScript syntax check, docs consistency, and `git diff --check`.

## CR-110 - QR Login SMS Verification Manual Submission Regression Fix

Lifecycle status:

CR-110 is implemented and verified on current `main` as a focused regression
fix after live Douyin QR testing showed that the CR-108 login UI could detect
SMS verification but lacked the older worktree's manual send/input/submit flow.

- [x] Record CR-110 in `CHANGE_REQUESTS.md` as a follow-up regression fix,
      without rewriting CR-108 historical verification.
- [x] Add backend login-session routes for requesting and submitting manually
      received SMS verification codes.
- [x] Add server-side QR browser helpers that click SMS send controls, fill a
      manually received code, and prefer Douyin `#uc-second-verify` exact
      visible `验证` submit controls.
- [x] Add the account login modal SMS verification panel with send, input,
      inline validation, submit, and continue-confirm actions.
- [x] Preserve the typed SMS code while the login session panel re-renders.
- [x] Keep SMS receiving automation, captcha/slider/device bypass, the older
      technical diagnostics UI, crawler behavior, tasks, reports, AI, email,
      permissions, and profile-locking out of scope.
- [x] Add regression tests for backend routes, server-page SMS submit, send
      request, Douyin exact submit selection, frontend rendering, and inline
      validation.
- [x] Verify the targeted red/green tests and the broader login regression
      subset.

## CR-111 - Current-Main Documentation State Synchronization

Planning status:

CR-111 is a documentation-governance synchronization against clean
`main@abb4d66`. It must not change product code, UI behavior, schema, runtime
data, sensitive files, or the old server-login worktree.

- [x] Register CR-111 in `CHANGE_REQUESTS.md`, `TEST_PLAN.md`, and
      `TRACEABILITY.md` before synchronizing lifecycle labels.
- [x] Compare every open task group and CR lifecycle label against current
      main, code, task completion, traceability, and recorded test evidence.
- [x] Mark the five CR-107 planning items complete because the matching
      implementation checklist and verification evidence are complete.
- [x] Synchronize verified CR lifecycle labels without changing accepted,
      future, deferred, `Needs Confirmation`, operator-gated, or partially
      verified work.
- [x] Repair `CURRENT_STATE.md` pre-merge wording and keep Phase 5.1P as the
      first unblocked lane.
- [x] Add the missing CR-052 traceability row and CR-066 lifecycle status.
- [x] Add a failing documentation-check regression test, then scope
      `Needs Confirmation` parsing to one CR section and rerun it green.
- [x] Document the manual semantic lifecycle review boundary without claiming
      that `scripts/check_docs.py` already automates it.
- [x] Run documentation consistency, machine-readable dry-run validation,
      relevant tests, Docker Compose configuration, and `git diff --check`.
- [x] Append CR-111 evidence to `TEST_RESULTS.md` and close this task block
      only after all checks pass.

## CR-112 - Local Browser Auto-Sync Cookie Acquisition

Planning status:

CR-112 is `Verified (Same-Machine Windows V1 / Packet D Real-Account Lane)` as
of 2026-07-22.
Acceptance approves the same-machine Windows scope, reuse-first/minimal-
adaptation evaluation, CR-112-before-CR-070 order, Profile/Cookie authority,
  administrator Cookie reveal, and Douyin/Xiaohongshu Packet D matrix. Packet
  B and C.1-C.3 are verified within their recorded proof boundaries. Packet D
  completed the designated Douyin and Xiaohongshu same-machine real-account
  lane: administrator reveal/copy, exact identity/Profile validation, final
  service restart, bounded normal-monitor crawls, persisted content,
  `fallback_used=false`, no raw Cookie in child argv/environment, post-crawl
  Profile checks, and cleanup. Phase 5.1P and Phase 5.1A-D plus the current
  merged regression fixes are verified; the separate CR-047 Linux/server-like
  real acceptance and any second-physical-computer deployment claim remain
  independent gates.

Documentation synchronization:

- [x] Register CR-112 in `CHANGE_REQUESTS.md` with background, purpose,
      classification, proposed boundaries, non-goals, dependencies,
      confirmations, and acceptance criteria.
- [x] Keep the reviewed master roadmap and four goal packets under
      `docs/superpowers/plans/` and link them from formal governance docs.
- [x] Add proposed account/security and local/server boundaries to
      `ACCOUNT_ENVIRONMENT.md` and `SERVER_DEPLOYMENT.md` without changing
      accepted V1 behavior.
- [x] Add CR-112 planning/future tests and traceability while preserving
      Phase 5.1P, CR-047, and CR-070 ownership.
- [x] Run documentation consistency, whitespace validation, and focused
      independent read-only review; then append exact evidence to
      `TEST_RESULTS.md`.
- [x] Record the audit correction: loopback requires server-side peer and
      Origin enforcement plus reverse-proxy exclusion; preserving
      `runner.py --cookies` carries a pre-existing process-argument exposure
      that requires an explicit Packet C decision gate.
- [x] Re-run documentation checks and focused Claude Code review after the
      audit remediation; close only when no blocking or material plan issue
      remains.
- [x] The 2026-07-19 proposed-plan package staged and committed all five CR-112
      plan files and its formal references atomically. The 2026-07-21 accepted
      rebaseline has its own open atomic-commit gate below.
- [x] Record the 2026-07-19 user-confirmed login-material decision: QR and
      accepted Cookie login converge on the same account-bound persistent
      Profile; encrypted Cookie remains bootstrap/refresh/recovery/migration
      material; failed refresh preserves the prior Profile and Cookie; the
      target child argv contains no raw Cookie.
- [x] Verify the persistent-Profile decision sync with documentation
      consistency, the focused documentation regression test, whitespace
      validation, stale-contract scanning, and independent read-only review.
- [x] Deep-cross-validate the supplemented CR-112 plan with Claude Code and
      iterate to `READY`: define fresh-candidate crash recovery, operation
      marker/directory matrix, browser-sync/manual promotion, exact hidden
      profile-only parent/child contract and cutover, C.2-only flag ownership,
      timed cleanup/export blocking, structured Cookie acquisition, pinned
      route-absence baseline evidence, and explicit status boundaries.
- [x] Rebaseline CR-112 on 2026-07-21 against
      `main@2ea2c1e96675297e302368b1226ec7aac05f2bb1`, synchronize the accepted
      decisions and TODO classifications across formal documents and Packet
      B/C/D.

Accepted decisions and gated execution:

- [x] Confirm same-machine Windows V1 scope; keep remote/cross-host Bridge out.
- [x] Confirm reuse-first/minimal-adaptation evaluation for Extension,
      Connector, and protocol; Packet B evidence selects direct reuse, minimal
      adaptation, or one focused component replacement.
- [x] Confirm CR-112 executes before CR-070.
- [x] Confirm Profile as normal crawl-login authority and encrypted Cookie as
      initialization/refresh/recovery/migration material.
- [x] Confirm administrator-only complete Cookie reveal/copy with default mask,
      no-store response, normal-user 403, and no Cookie in Storage, URL, logs,
      audit details, diagnostics, argv, or environment.
- [x] Confirm Douyin and Xiaohongshu as mandatory Packet D real platforms and
      Kuaishou as Deferred.
- [x] Complete Phase 5.1P under CR-047 before CR-112 product implementation.
- [x] Complete Phase 5.1A-D and current merged provider/login/crawl regression
      fixes. Keep the separate CR-047 Linux/server-like real acceptance
      operator-gated and do not present CR-112 local proof as its completion.
- [x] Rerun the latest-main scoped Windows provider/preflight unit before
      Packet B: Compose configuration passed, deployment browser preflight
      resolved persisted Chrome, isolated server-like validation passed all 12
      checks with cleanup, and the Phase 5.1/CR-116-121 focused regression
      passed (`234 passed`). This proves only the local inherited authority and
      does not close CR-047 Linux/server-like acceptance.
- [x] Commit the complete 2026-07-21 CR-112 decision, governance, specialist,
      and Packet B/C/D plan set atomically before marking Packet B
      `In Progress`: commit `44baf78`.
- [x] Execute Packet B as a disposable compatibility/acquisition spike. Measure
      the reference Extension/Connector and prove the selected direct managed-
      context acquisition on Chrome and Edge with synthetic Cookies only.
- [x] Produce the Packet B Extension/Connector/protocol matrix with direct
      reuse, minimal adaptation, or single-component replacement plus license,
      runtime, distribution, and contract evidence.
- [x] In Packet B, prove the rejected Cookie-bridge route remains absent in the
      pinned runtime (HTTP 404 and unmatched-WebSocket 403). The selected V1
      direct path mounts no WebSocket route and has no Origin/client/pairing
      boundary.
- [x] In Packet B, fix structured Cookie Protocol V1 fields and Chrome/Edge
      limits and prove domain/path/security attributes survive exact routing and
      temporary Profile restart without touching real account material.
- [x] Record that the reference Extension fails current Chrome managed loading,
      has path-dependent unpacked identity, and loses structured Cookie scope;
      select managed Playwright/CDP context as the Extension/Connector
      replacement and clean every temporary Profile.
- [x] Complete the required Packet B validation, documentation/whitespace
      checks, and final gate; Packet B is `Verified` within its synthetic local
      proof boundary.
- [x] Commit the verified Packet B result and synchronized formal documents
      atomically before marking Packet C `In Progress`.
- [x] Start Packet C only after Packet B passes and data-model/migration,
      distribution, runtime, permission, and security decisions are accepted.
- [x] Packet C.1: implement the shared browser-sync/manual canonical Cookie service,
      fixed-active-path promotion journal, same-volume candidate/rollback swap,
      active-path recheck, restart recovery, bounded cleanup, and existing
      account migration without enabling Bridge. Candidates are fresh provider
      outputs and never clone/mutate the active Profile before `swapping`;
      recovery follows the commit-authority/directory-shape/operation-marker
      table; the run/promotion lock exclusion is atomic, candidate creation
      requires a `256 MiB` reserve, and cleanup runs after success, on
      timer/startup, and before refresh.
- [x] Verify Packet C.1 with focused protocol/journal/recovery/route tests, the
      full monitoring suite (`606 passed`), Python compile, documentation checks,
      and `git diff --check`; leave C.2 gated until the atomic commit.
- [x] Start Packet C.2 after the C.1 atomic delivery and verification gates;
      C.3 and Packet D remained gated until C.2 acceptance evidence existed.
- [x] Packet C.2: implement feature-gated direct exact-context acquisition/API/UI
      on C.1; feature-off removes only C.2 and preserves advanced manual Cookie.
      Only C.2 router/UI/readiness/managed-browser code may read
      `MONITOR_BROWSER_COOKIE_SYNC_ENABLED`.
- [x] Packet C.2: implement the administrator-only Cookie reveal POST endpoint
      and default-masked eye/copy UI. Return no-store/no-cache, reject normal
      users with 403, keep standard account payloads masked, and prove Cookie
      reveal material never enters browser persistent Storage, URL, logs,
      audit details, diagnostics, or a new child process. C.2 does not claim
      the existing crawler Cookie argv/env is retired; that remains C.3.
- [x] Verify Packet C.2 with `19` focused tests, `269` adjacent Phase 5.1/login/
      crawl regressions, the complete monitoring suite (`625 passed`), desktop
      and phone browser checks, Python/JavaScript/documentation/whitespace
      gates, and a controlled account-bound start/cancel run. The controlled
      run preserved the existing active account/Profile, removed the candidate,
      and left no owned Chromium process after cancellation.
- [x] Packet C.3: implement the internal profile-only runner, migrate or mark
      every `login_type=cookie` account, reject login/generic/default-network
      fallback, and retire raw Cookie argv/env with effective command/environment
      construction proof.
      Use hidden `--monitor_profile_only`, exact provider env, Cookie clearing,
      exit-code-42 relogin mapping, and a paused maintenance cutover with no
      runnable version-0 account. Existing QR/Profile execution remains
      regression-protected. Accepted rollback preserves C.1/C.3 and never
      restores argv exposure.
- [x] Verify Packet C.3 with `17` focused tests, `190` adjacent Phase 5.1D/
      CR-117/login/runner regressions, the complete monitoring suite (`642 passed`),
      Python compile, and documentation/whitespace gates.
      Effective child command/environment inspection proves no synthetic Cookie reaches the
      effective argv/environment; real OS process inspection remains Packet D.
- [x] Start Packet D only after Packet C tests pass and C.3 is delivered
      atomically in commit `1d62677`.
- [x] Complete the Packet D local deployment matrix within its recorded proof
      boundary: isolated browser bootstrap/selection, multi-account isolation,
      promotion checkpoint crash/restart, C.1/C.2/C.3 rollback, structured
      Cookie fidelity, server QR non-regression, and bounded operation-artifact
      cleanup. A second physical computer and CR-047 Linux/server-like action
      remain separate operator gates.
- [x] Run the bounded 2026-07-21 Douyin preflight with designated account
      selection: the existing Profile passed login checks before and after the
      attempt; the managed Chromium process used a managed Profile and no
      Cookie argument; the operator-login window timed out; the login session
      and promotion ended safely; the browser process and candidate Profile
      material were cleaned; and the original account/Profile stayed active.
- [x] Record the later CR-122/CR-124 Douyin evidence: no-QR browser sync
      committed a candidate Profile and encrypted 54-record structured Cookie,
      normal and post-restart saved-Profile checks passed, and the normal
      monitor entry persisted five real content rows with
      `fallback_used=false`.
- [x] Satisfy the real-account start gate with two explicit administrator-
      approved project-managed accounts, one for Douyin and one for
      Xiaohongshu. No other real account was used for Packet D collection.
- [x] Packet D: for both designated platforms acquire and validate the real
      Cookie through the selected direct managed-browser service, exercise
      administrator reveal/copy, promote a fresh account-bound candidate,
      restart, prove `fallback_used=false`, and persist real content through
      the normal monitor entry. Clear acquisition handles/state, restart the
      service, and re-prove both Profile checks plus bounded crawls.
- [x] Keep Kuaishou `Deferred`; do not count it as Packet D failure or claim it
      was tested.

## Phase 14 - Run Center Data Model Preparation

Planning status:

Phase 14 is complete and verified. It only prepared the run-center data model;
Phase 15 must still implement pagination, filters, archive/restore APIs, and
frontend governance.

- [x] Add `crawl_runs.visibility` with values `visible` and `archived`.
- [x] Add `crawl_runs.run_type` with values `scheduled`, `manual`, and `test`.
- [x] Add `crawl_runs.archived_at`.
- [x] Add `crawl_runs.archived_by`.
- [x] Backfill existing runs with `visibility = visible` and
      `run_type = scheduled`.
- [x] Add recommended indexes for visibility/date and run type/status filters,
      following `SCHEMA_MIGRATION.md`.
- [x] Update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md` with migration details.

## Phase 15 - Run Center Governance And Frontend

Planning status:

Phase 15 depends on Phase 14. Phase 15A and Phase 15B are complete and
verified. Phase 16, Phase 17A, Phase 17B, Phase 18A, and Phase 18B are also
complete and verified.

### Phase 15A - Run Center API And Data Governance

- [x] Add run pagination at the API/query layer.
- [x] Add filters for task, law firm, status, run type, visibility, date, and
      platform.
- [x] Add archive and restore APIs.
- [x] Hide archived records from default API/list behavior while preserving
      administrator access through explicit filters.
- [x] Preserve the existing run-list response fields while adding pagination,
      filter metadata, visibility, and run-type fields.
- [x] Preserve run logs, report links, owner/workspace scope, and existing
      status values.
- [x] Verify API tests for pagination, filters, archive, restore, and default
      visibility behavior.

### Phase 15B - Run Center Frontend Refinement

- [x] Add pagination UI.
- [x] Add task/law-firm, status, platform, run type, visibility, and date
      filters.
- [x] Add archive and restore row actions with confirmation.
- [x] Separate operational records from test/noise records in the default view.
- [x] Keep run logs refreshable, copyable, and downloadable.
- [x] Verify desktop, tablet, and mobile run-center layouts.

## Phase 16 - Email Delivery Data Model Preparation

Planning status:

Phase 16 is complete and verified. It only prepared the email delivery data
model; Phase 17A connected delivery logic, scheduler idempotency, and manual
resend logging to this foundation.

- [x] Add `email_delivery_logs`.
- [x] Store `workspace_id`, `job_id`, `report_id`, `send_window_key`,
      `send_type`, `sent_by`, `sent_at`, `status`, `error_message`,
      `recipients_json`, and `created_at`.
- [x] Use `send_type = auto` for scheduler sends and
      `send_type = manual_resend` for explicit resend.
- [x] Use `daily` window keys as `{job_id}_{YYYY-MM-DD}`.
- [x] Use `6h`, `12h`, and `cron` window keys as
      `{job_id}_{YYYY-MM-DD}_{HH}`.
- [x] Add indexes or uniqueness rules needed for automatic-send idempotency.
- [x] Update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`.

## Phase 17 - Email Delivery Governance

Planning status:

Phase 17 depends on Phase 16. Phase 17A and Phase 17B are complete and
verified. Phase 17B kept report-center delivery-history UI separate from the
backend delivery-governance work and did not implement Phase 18 report
grouping.

### Phase 17A - Email Idempotency And Delivery Logic

- [x] Implement `send_window_key` generation for `daily`, `6h`, `12h`, and
      `cron` using the accepted rules in `DATA_MODEL.md` and
      `SCHEMA_MIGRATION.md`.
- [x] Add automatic-send idempotency by `workspace_id + job_id +
      send_window_key + send_type=auto`.
- [x] Record automatic delivery attempts, successes, failures, recipient
      summaries, and customer-safe error messages in `email_delivery_logs`.
- [x] Allow manual resend while recording a separate
      `send_type = manual_resend` delivery log.
- [x] Preserve report generation when SMTP is unavailable.
- [x] Keep existing latest-state report fields readable until the frontend is
      migrated to delivery history.
- [x] Verify repeated scheduler triggers do not send duplicate automatic
      emails and manual resend creates a separate delivery record.

### Phase 17B - Email Delivery History Frontend

- [x] Surface latest delivery status and delivery history in the report center
      without exposing SMTP secrets.
- [x] Add manual resend UI with confirmation and clear success/failure
      feedback.
- [x] Show send type, status, time, recipient summary, and customer-safe error
      message.
- [x] Preserve report preview, lead detail switching, and report downloads.
- [x] Verify administrator and normal-user owner/workspace scope for delivery
      history and manual resend.
- [x] Verify desktop, tablet, and mobile report-center delivery surfaces.

## Phase 17.1 - Email Delivery Safety Follow-up

Planning status:

Phase 17.1 is an accepted follow-up regression fix for CR-036. It does not
rewrite Phase 17's historical completion record. It restores the intended
safety boundary that automated tests, local diagnostics, and accidental local
execution must not send hidden real external report emails.

Confirmed CR-036 decision summary:

- [x] Confirm the explicit real-email validation model must allow intentional
      production/pilot SMTP validation while preventing routine automated tests
      and local diagnostics from sending hidden real mail.
- [x] Confirm `MONITOR_ALLOW_REAL_EMAIL_SEND` should be environment-controlled
      and surfaced read-only in runtime settings.
- [x] Confirm local manual-resend behavior under the safety gate should be
      allowed only when the explicit real-mail validation policy allows it;
      otherwise it remains a non-sending validation path.
- [x] Confirm historical handling for orphan delivery-log rows `60` and `81`
      and their report artifacts. Do not mutate them without operator approval.

### Phase 17.1A - Real SMTP Safety Gate

- [x] Add one shared delivery-safety helper used before real SMTP side effects.
- [x] Prevent routine automated tests and local diagnostics from hidden real
      SMTP side effects unless the confirmed explicit validation path is used.
- [x] Apply the safety helper consistently to automatic report delivery, manual
      resend, and mail-test paths according to the confirmed scope.
- [x] When delivery is blocked by the safety gate, preserve report generation
      and write a customer-safe skipped delivery state.
- [x] Keep production/pilot real email delivery and explicit real-mail
      validation working when the confirmed allow conditions and SMTP
      configuration are complete.

### Phase 17.1B - Test Isolation And Regression Coverage

- [x] Update `test_run_job_blocks_platform_when_login_window_is_open` so it
      cannot invoke real SMTP while still verifying the platform-blocking
      behavior.
- [x] Add a test-level SMTP tripwire that fails if the automated suite reaches
      `smtplib.SMTP` or `smtplib.SMTP_SSL` without explicit opt-in.
- [x] Audit `run_monitor_job` tests and report-generation tests for unmocked
      email delivery paths.
- [x] Verify the full test suite can run with a real SMTP config in the active
      database without sending external mail.
- [x] Add a separate real-mail validation test path or runbook that is skipped
      by default and can only send when the confirmed explicit validation
      conditions are present.

### Phase 17.1C - Effective Recipient Traceability

- [x] Centralize effective-recipient resolution so report delivery and delivery
      logs use the same recipient list.
- [x] Keep recipient precedence explicit in code: task recipients win,
      global default recipients are fallback-only, and SMTP sender is not a
      delivery target.
- [x] Record final effective recipients in `email_delivery_logs`, including
      recipients inherited from global default-recipient fallback.
- [x] Define and persist recipient metadata consistently:
      `recipients_json` for the task/request snapshot,
      `effective_recipients_json` for final resolved recipients,
      `effective_recipient_source` for recipient origin, and `trigger_source`
      for the send trigger.
- [x] Record delivery trigger source so future role policy and quota logic can
      distinguish automatic, manual, test, diagnostic, and explicit validation
      sends.
- [x] Show the effective-recipient source in preflight/delivery surfaces, e.g.
      task recipients versus global default-recipient fallback.
- [x] Update email-configuration and task-configuration copy so operators can
      see that filling task recipients overrides the global default recipients.
- [x] Preserve customer-safe recipient display without storing SMTP secrets.
- [x] Keep automatic-send idempotency by `workspace_id + job_id +
      send_window_key + send_type=auto` unchanged.

### Phase 17.1D - Historical Orphan Evidence And Operations Notes

- [x] Document the observed orphan evidence from `job_id` 9686 and 9759:
      sent delivery-log rows, existing report artifacts, and missing
      job/run/report rows.
- [x] Provide a dry-run-first helper or operator checklist for reviewing
      orphan delivery logs and report artifacts.
- [x] Add or link an operator runbook for orphan email evidence review,
      backup-before-mutation, approval, and rollback.
- [x] Require database backup and explicit operator approval before deleting,
      annotating, or otherwise mutating historical delivery evidence.
- [x] Ensure preview or dry-run mode performs no mutation and shows the
      proposed effect plus rollback path before any write is allowed.
- [x] Ensure report-center delivery-history and run/report grouping remain
      readable for existing non-orphan reports.

## Phase 17.2 - Report Email Template Governance

Planning status:

CR-039 is an accepted existing-feature optimization for report email template
predictability and historical diagnosis. Phase 17.2A overlaps with CR-036's
delivery-log metadata work and should be implemented with Phase 17.1C when
practical to avoid repeated `email_delivery_logs` schema churn. Phase 17.2B-C
is now implemented as the focused guardrail/preset-direction batch: new custom
HTML templates cannot be saved without `{report_html}` or `{report_body}`,
legacy templates remain readable, and the UI steers administrators toward
system-body-preserving style presets.

### Phase 17.2A - Effective Template Provenance

- [x] Centralize effective-template resolution for report snapshots and
      delivery logs so task-bound versus active-global fallback behavior is
      preserved for generated reports.
- [x] Record effective email template id, template name, subject template, and
      template source in report snapshots.
- [x] Record effective template metadata in email delivery logs without storing
      secrets or unsafe raw HTML.
- [x] Make historical report/email detail able to explain why a delivered email
      differed from the currently previewed or currently active template.

### Phase 17.2B - Template Body Guardrails

- [x] Validate or warn/block custom templates that omit `{report_html}` and
      `{report_body}` so delivered emails cannot silently drop the generated
      report body.
- [x] Clarify in the mail-template UI that editor preview uses sample data and
      real sends use the generated report HTML for the actual run.
- [x] Preserve subject-template flexibility while keeping required body content
      system-controlled.

### Phase 17.2C - Preset Style Direction

- [x] Replace the long-term product direction of unrestricted HTML editing with
      administrator-selectable preset report-email styles.
- [x] Ensure preset styles wrap the system-generated report body instead of
      letting users remove required report sections.
- [x] Keep old templates readable for compatibility, but do not require normal
      users to edit HTML.

## Deferred Backlog - Email Delivery Role Governance

Planning status:

CR-037 is deferred. It records the user's broader direction that email sending
and resend should eventually be governed by role, administrator policy, and
possibly per-user or per-day quotas. It should not be implemented as part of
CR-036/Phase 17.1.

- [!] Confirm the future UI location for administrator email governance:
      Users And Permissions, Runtime Strategy, or a dedicated Email Governance
      section.
- [!] Confirm whether normal-user send and resend quotas are per user, per
      task, per report, per day, or a combination.
- [!] Confirm whether automatic scheduled delivery and manual resend use the
      same policy or separate policies.

## Minimum Usable Pilot Acceptance Gate

Planning status:

CR-041 is an accepted documentation-governance gate for deciding when the
system can be used first in a small pilot. It tightens acceptance around the
minimum safety and lifecycle conditions without making Phase 21 UI refinement,
Phase 19 realtime progress, Phase 20 AI traceability, CR-038 drawer
accessibility, or CR-037 quota governance blockers for the first usable pilot.

This gate is complete after the referenced implementation phases and the real
SMTP validation are implemented, verified, and recorded in `TEST_RESULTS.md`.
For SMTP, a `sent` delivery-log status means the configured SMTP server
accepted the message submission; Pilot Gate C also requires operator
confirmation that an approved recipient actually received the message in inbox
or spam/quarantine.

Implementation order for satisfying this gate follows `CURRENT_STATE.md`:
Phase 17.1A-B, Phase 17.1C/17.2A, Phase 7.1A-C, automated server-like
validation, one real Douyin server-side login/crawl, explicit-opt-in real SMTP
submission, recipient-side receipt confirmation, and a passing redacted
operator evidence JSON are verified. Preserve the Pilot Gate D
non-blocker/remediation boundary throughout.

### Pilot Gate A - Email Side-Effect Safety

- [x] Complete and verify CR-036/Phase 17.1A-B so automated tests, local
      diagnostics, and ordinary local report-delivery paths cannot send hidden
      real SMTP email.
- [x] Verify real SMTP is blocked by default even when the active database has
      complete SMTP configuration and default recipients.
- [x] Verify automatic report delivery, manual resend, and mail-test paths all
      use the same delivery-safety gate.
- [x] Verify blocked delivery still allows report generation and writes a
      customer-safe skipped delivery state or confirmed equivalent.
- [x] Verify the automated test suite has a tripwire that fails on
      `smtplib.SMTP` or `smtplib.SMTP_SSL` without explicit opt-in.

### Pilot Gate B - Run Lifecycle And Partial Result Safety

- [x] Complete and verify CR-035/Phase 7.1A-C so new runs persist
      `crawl_runs.job_id`, lifecycle finalization is idempotent, and terminal
      statuses cannot be reopened by stale writers.
- [x] Verify success, failure, timeout, cancellation, interruption, and partial
      AI/report paths all finalize to a terminal status and release locks
      safely.
- [x] Verify AI item timeout, exception, and invalid JSON save
      `pending_review` and continue when the run can safely continue.
- [x] Verify collected partial results can generate a report when AI is
      unavailable, partially interrupted, or degraded to manual review.
- [x] Verify a simulated reduced-size equivalent of the 271-content
      interruption class cannot remain indefinitely `running`; it finalizes and
      produces a partial/manual-review report. The real historical run `8317`
      remains governed by Phase 7.1D.

### Pilot Gate C - Minimum Server-Like Real Workflow

- [x] Run server-like validation without relying on the operator's local Chrome.
- [x] Verify administrator web-UI login and server-side platform QR/profile
      flow in the server-like environment.
- [x] Add a default-safe Pilot Gate C evidence template and checker that can
      validate operator-filled real-workflow evidence without starting
      services, crawling platforms, calling AI, mutating databases, or sending
      email.
- [x] Verify at least one real platform login and crawl path with persistent
      server-side account profile before pilot handoff.
      Verified on 2026-06-17 in the `cr041-pilot-evidence` server-like
      worktree with Douyin run `run_id=3`, report `report_id=3`, 14 raw/new
      contents, and profile key `1/dy/acc_1`.
- [x] Verify AI unavailable or AI failure fallback does not block report
      generation. The same real run produced 14 `pending_review` items with
      `ai_failed_fallback_evaluations=14` and still generated a report.
- [x] Verify explicit-opt-in SMTP delivery can submit through the configured
      SMTP server in pilot/production mode while default local/test/diagnostic
      behavior remains non-sending. On 2026-06-17, a controlled
      frontend-enabled real SMTP manual resend for `report_id=3` produced
      delivery-log row `id=6` with `status=sent`,
      `trigger_source=manual_resend`, and two effective default recipients.
      This proves SMTP acceptance only, not
      pilot receipt; recipient-side confirmation is tracked by the next task.
- [x] Verify at least one approved recipient confirms receipt of the pilot
      report email in inbox or spam/quarantine before closing Pilot Gate C.
      On 2026-06-17, the operator confirmed both approved recipients received
      the report email for delivery-log row `id=6`; mailbox addresses and
      message content are not stored in docs.
- [x] Verify automated local/server-like logs, reports, delivery records, and
      UI surfaces do not expose API keys, SMTP passwords, cookies, proxy
      credentials, raw profile paths, provider endpoints, local paths, or
      command lines.
- [x] Verify the real-platform pilot run's customer-facing outputs do not
      expose API keys, SMTP passwords, cookies, proxy credentials, signed URL
      query parameters, raw profile paths, provider endpoints, local paths, or
      command lines. This covers the external report downloads, run/report
      APIs, delivery-log API, run-log API, and social-account API for
      `run_id=3` / `report_id=3`; internal raw crawler artifacts are not
      customer-facing acceptance artifacts.
- [x] After real external validation, fill a redacted operator evidence JSON
      based on `docs/pilot_gate_c_evidence.example.json` and pass
      `uv run python scripts/pilot_gate_c_evidence.py --check <evidence.json>`
      before closing Pilot Gate C. The evidence must include both the delivery
      log reference and a redacted recipient receipt confirmation reference.
      Verified with ignored local evidence file
      `data_server_like\pilot_gate_c_evidence.pending.json`; checker result:
      PASS.

### Pilot Gate D - Non-Blocker Boundary

- [x] Confirm Phase 21, CR-038, Phase 19B-D, Phase 20, and CR-037 are not
      required for first usable pilot readiness unless a later accepted P0
      safety, security, or core-flow regression changes the boundary.
- [x] Confirm historical run `8317` remediation and orphan delivery evidence
      cleanup remain dry-run, backup, rollback, and explicit-operator-approval
      gated and are not performed automatically as part of pilot readiness.

## Administrator Frontend Real Email Send Toggle

Planning status:

CR-043 supersedes the rejected CR-042 validation-window design. The accepted
product shape is one administrator-controlled Mail Configuration switch backed
by the persisted `real_email_delivery` runtime setting. The switch defaults
off. There is no deployment frontend gate, scheduler-exclusion gate, expiry
window, or single-use validation-window workflow for daily operation.

- [x] Confirm the user-facing design is one administrator frontend switch only.
- [x] Keep `real_email_delivery` default-off and persisted as a runtime
      setting.
- [x] Make `real_email_delivery` admin-editable and normal-user inaccessible.
- [x] Put the switch on Mail Configuration and remove the old open/close
      validation-window buttons from the UI.
- [x] Keep Runtime Strategy focused on Crawling, Login, Scheduler, and
      Retention so the same email switch is not exposed in a second place.
- [x] Make mail test, manual resend, and automatic report delivery follow the
      same switch: blocked when off, allowed when on and SMTP config is
      complete.
- [x] Preserve report generation and customer-safe skipped/failed delivery
      records when the switch is off or SMTP fails.
- [x] Keep SMTP acceptance wording explicit: `sent` means SMTP accepted the
      submission, not recipient inbox proof.
- [x] Keep the automated SMTP tripwire and mocked-SMTP tests so verification
      does not send real external mail.
- [x] Verify CR-043 with targeted pytest, docs check, and frontend syntax
      checks after the documentation and UI cleanup.

## Phase 18 - Report Center Task Grouping

Planning status:

Phase 18 depends on Phase 10-11 and the accepted report snapshot data model.
Execute it as Phase 18A-18B so snapshot persistence lands before frontend
grouping consumes it. Phase 18A and Phase 18B are complete and verified.

### Phase 18A - Report Job Snapshot Data Model

- [x] Add `reports.job_snapshot_json`.
- [x] Save law firm, platforms, search keywords, frequency, task ID, and
      deleted-task context into the report snapshot for newly generated
      reports.
- [x] Backfill `job_snapshot_json` for existing reports whose `job_id` still
      resolves to a monitoring task.
- [x] Leave unrecoverable old reports visible with a limited-context fallback
      instead of blocking reads.
- [x] Preserve `job_id` for active task relations and never use snapshot
      content to bypass owner/workspace permissions.
- [x] Verify new reports contain snapshots, backfilled reports remain readable,
      and reports still load after their task is deleted or missing.

### Phase 18B - Report Center Task Grouping Frontend

- [x] Group reports by monitoring task when `job_id` resolves.
- [x] Group orphan or deleted-task reports using `job_snapshot_json`.
- [x] Show deleted-task or limited-context labels where appropriate.
- [x] Preserve report preview and lead detail switching by selected report.
- [x] Preserve download links, email delivery status/history, and row actions.
- [x] Verify grouped report behavior for active, deleted, missing-task, and
      limited-context reports on desktop, tablet, and mobile.

## Phase 19 - Run Center Realtime Progress And Requirement Intake Governance

Planning status:

Phase 19 is the next planned optimization batch after the completed Phase
10-18 console roadmap. It covers one documentation-governance rule update and
one product optimization for active run progress visibility. Phase 19 must not
change MediaCrawler platform implementations, add high-concurrency worker
architecture, or expose raw crawler paths/secrets unless a later accepted CR
changes those boundaries.

Phase 19B-19D should be implemented after the CR-035/Phase 7.1 run-lifecycle
regression fix is implemented and verified, or deliberately split into a
smaller safe batch.
Phase 19 progress display may depend on Phase 7.1 fields such as phase,
heartbeat, terminal `interrupted` state, and AI progress fallback behavior.

### Phase 19A - Requirement Intake Classification Rules

- [x] Add a CR classification rule for new capabilities, existing feature
      optimizations, regression fixes, and documentation-governance changes.
- [x] Document required future CR fields: background, purpose, type, scope
      boundary, non-goals when useful, related tasks, and acceptance criteria.
- [x] Update `AGENTS.md`, `AGENT_WORKFLOW.md`, `CHANGE_REQUESTS.md`, and
      `DOCUMENTATION_CHECKS.md` so future agents can find and apply the rule.

### Phase 19B - Run Center Progress Data Layer

- [x] Treat Phase 7.1 lifecycle fields as the preferred dependency for active
      progress storage: `phase`, `phase_started_at`, `progress_updated_at`,
      retry state, last safe result, and progress snapshots in
      `crawl_runs.summary`.
- [x] If Phase 19B is deliberately implemented before Phase 7.1, use only a
      small compatible provisional-progress shape and document how it will
      merge into the Phase 7.1 summary structure. Do not add a conflicting
      second progress model.
- [x] Add a safe progress snapshot mechanism for running crawler attempts,
      using MediaCrawler output files or equivalent progress signals while the
      subprocess is still alive.
- [x] Store provisional progress in `crawl_runs.summary` without marking it as
      final ingested counts.
- [x] Tolerate missing, in-flight, partially written, or malformed JSON/JSONL
      output files without crashing the run.
- [x] Preserve the existing final collect-and-ingest semantics for
      `raw_contents`, `filtered_contents`, `excluded_contents`, and
      `new_contents`.
- [x] Preserve owner/workspace scope, logs, stop action, archive/restore,
      timeout handling, and customer-safe wording.
- [x] Prove that a disappearing crawler subprocess or repeated finalization
      still converges to one terminal run state and never leaves a run stuck in
      a provisional-progress state.

### Phase 19C - AI Evaluation Progress Updates

- [x] Update AI evaluation progress in batches or time intervals while the
      evaluation loop is running.
- [x] Track evaluated count, total evaluation candidates, suspected negative
      count, high-risk count, and manual-review count without waiting for the
      full AI batch to finish.
- [x] Preserve AI-failure fallback to manual review and report generation.
- [x] Ensure final AI counts remain exact after the evaluation loop completes.
- [x] Prove late or repeated progress writes cannot regress a terminal run or
      alter final counts after completion.

### Phase 19D - Run Center Frontend Progress Display And Polling

- [x] Keep Run Center polling active while visible runs remain active instead
      of stopping after a short fixed polling window.
- [x] Display active collection, ingestion, AI evaluation, report generation,
      email delivery, timeout, and completion states clearly.
- [x] Distinguish provisional collection progress from final ingested counts.
- [x] Keep desktop, tablet, and mobile layouts usable without overlap, clipped
      actions, or hidden stop/log controls.
- [x] Verify normal users only see own scoped progress and administrators keep
      workspace-wide visibility.

## Phase 20 - Run Detail And AI Evaluation Traceability

**IN PROGRESS**

Planning status:

Phase 20 is being implemented after CR-034 confirmation items were resolved.
Trace retention is an administrator-configurable runtime setting with a 30-day
default, not a hard-coded value. Permission visibility is confirmed: normal
users see only business-safe summaries for their own runs, administrators may
see redacted prompt/request/response debug snapshots, and unredacted raw
responses must not be exposed to any role. Trace storage uses a new
`ai_evaluation_traces` table with capped/redacted JSON fields. Phase 20 remains
separate from Phase 19 because it adds historical AI traceability, run-detail
APIs, and run-detail frontend surfaces, while Phase 19 focuses on run progress
visibility.

### Phase 20A - Traceability Confirmation And Data Model Design

- [x] Confirm visibility boundary: normal users see only business-safe
      summaries for their own runs; administrators may see redacted
      prompt/request/response debug snapshots; unredacted raw responses are not
      exposed to any role.
- [x] Confirm trace retention policy: make retention configurable through
      administrator runtime settings, defaulting to 30 days.
- [x] Confirm raw response visibility: normal users cannot see raw model
      responses; administrators may see redacted raw model responses; no role
      may see unredacted raw model responses.
- [x] Confirm maximum stored size defaults: each trace is about 64KB, prompt
      snapshot up to 16KB, request snapshot up to 24KB, response snapshot up to
      24KB, and sampled comments up to 20 comments with per-comment truncation.
- [x] Confirm storage shape: new `ai_evaluation_traces` table with
      redacted/capped JSON fields, linked to `run_id`, `raw_content_id`, and
      `ai_evaluations.id`.
- [x] After confirmation, update `DATA_MODEL.md` and `SCHEMA_MIGRATION.md`
      from proposed notes to accepted implementation details.

### Phase 20B - AI Evaluation Trace Persistence

- [x] Persist new AI evaluation trace snapshots at evaluation time, including
      business input payload, prompt/request snapshot, provider/model metadata,
      structured output, raw/redacted response, fallback/error detail, duration,
      and timestamps.
- [x] Preserve existing `ai_evaluations` final-result behavior and keep
      historical rows readable.
- [x] Show an explicit limited-context state for old evaluations that do not
      have trace snapshots.
- [x] Ensure trace persistence redacts secrets, authorization headers, cookies,
      proxy credentials, profile paths, and server-local paths.

### Phase 20C - Run Detail And AI Evaluation API

- [x] Add or extend run-detail APIs so a run can return lifecycle summary,
      crawler logs, content list, AI evaluation list, and report/email links in
      one scoped response.
- [x] Add paginated/filterable AI evaluation detail reads by `run_id`, status,
      risk level, platform, keyword, and content title.
- [x] Add a per-evaluation detail endpoint for input/output trace snapshots
      with role-safe field filtering.
- [x] Preserve owner/workspace scope and administrator-only access to confirmed
      debug fields.
- [x] Ensure run-detail collection logs and trace text redact server-local
      paths, including Windows paths with spaces and residual path fragments,
      without exposing implementation field names such as `profile_path`.
- [x] Ensure trace-write failure or retention cleanup cannot block report
      generation or mutate `ai_evaluations`, reports, or delivery logs.

### Phase 20D - Run Detail Frontend

- [x] Add a Run Center "详情" action that opens a per-run detail drawer or
      page grouped by `run_id`.
- [x] Treat Run Detail as the primary operational entry for run-scoped leads
      and AI evaluation records, including records that exist before report
      generation.
- [x] Show tabs or sections for Overview, Collection Logs, Collected Contents,
      AI Evaluation, Report, and Email Delivery.
- [x] In the AI Evaluation tab, list every evaluation candidate/result for the
      run and allow opening a single evaluation's input/output detail.
- [x] Keep crawler logs visible in the same run-detail surface instead of
      making operators choose between logs and AI details.
- [x] Verify desktop, tablet, and mobile layouts keep the run detail readable
      without hiding stop/log/detail actions.

### Phase 20E - Report Center Lead Detail Clarity

Planning note:

CR-048 refines this phase by making Report Center lead detail scope explicit.
Report Center may show report-scoped leads or drawer-local filtered leads after
the operator opens a selected report/run lead drawer, but it must not present an
unlabeled flat list that looks like a global lead workbench. Run Center / Run
Detail remains the primary home for run-scoped lead and AI evaluation
inspection; Report Center provides report-scoped shortcuts.

- [x] Add an explicit "view leads" action to report rows or report groups so
      line details are not hidden behind the report preview action.
- [x] Link report leads back to the originating run detail when `run_id` is
      available.
- [x] Show a visible lead-detail scope label, count, and applied filter summary
      for selected report, selected group, originating run, or drawer-local
      filters.
- [x] Avoid default flat "all leads" presentation; lead-state filtering is
      drawer-local after a report or run scope is selected.
- [x] Add empty states that distinguish no selected report, selected report has
      no leads, and drawer-local filters have no matching leads.
- [x] Keep Report Center focused on final reports, report leads, downloads, and
      email delivery history rather than running-process observability.
- [x] Add a UI regression test that fails if the lead table renders without a
      visible scope label and count.

## Formal Console Full-Coverage Positive UI Optimization

Planning status:

This is a verified frontend-only optimization pass after the completed Phase
10-18 console roadmap. It preserves the latest formal `/monitor` frontend
functions and does not implement Phase 19B-19D run-progress product changes.

- [x] Keep the formal navigation structure unchanged: dashboard, monitoring,
      run center, report center, resource management, and system configuration
      remain separate pages.
- [x] Preserve existing account, task, resource, AI, mail, run, report, and
      diagnostics buttons, filters, batch actions, more menus, drawers, and
      modals.
- [x] Apply a cleaner low-noise enterprise visual layer without adding a new
      framework or build step.
- [x] Reprioritize the dashboard so operations data and closed-loop status
      appear before the 01-05 shortcut flow.
- [x] Add page-shaped skeleton/loading states for dashboard, accounts,
      resources, AI, mail, runtime, runs, reports, and diagnostics.
- [x] Add stable button-level loading feedback for secondary drawers and
      modals, including account QR/Cookie login, resource saves, AI tests,
      mail tests, and template preview.
- [x] Keep row more menus as floating menus that are not clipped by table
      scroll containers.
- [x] Compress the mobile dashboard so key metrics and closed-loop status
      remain usable at 390px without horizontal overflow.
- [x] Verify desktop 1440px, tablet 1024px, and mobile 390px browser behavior
      for page reachability, core modals, floating menus, and overflow.

## Formal Console Drawer Close Accessibility Follow-up

Planning status:

CR-038 is implemented and verified as a frontend-only follow-up to the verified
formal console optimization pass. It fixes scrollable drawer close
accessibility without reopening CR-033 or changing backend behavior.

Queue note:

CR-038 was handled as a small frontend quick fix before Phase 21. It is closed
without starting Phase 21 page-level UI refinement.

- [x] Make shared drawer/modal headers sticky within scrollable drawers so the
      top-right close button remains visible while content scrolls.
- [x] Preserve backdrop click-to-close, Escape close where supported, and
      existing bottom save/close action bars.
- [x] Add visual separation for sticky headers using solid background and
      border/shadow treatment so form content cannot bleed through.
- [x] Verify task edit, account, proxy, AI profile, mail config, mail template,
      run log, and report preview drawers for reachable close controls.
- [x] Verify desktop, tablet, and mobile layouts avoid overlapping sticky
      header controls with content, scrollbars, or footer action bars.

## CR-044 - Mail Test Recipient Coverage And SMTP Acceptance Clarity

Planning status:

CR-044 is an accepted regression fix for the administrator Mail Configuration
test-mail path. It does not reopen CR-043's one-switch design and does not
change report-delivery recipient precedence.

- [x] Diagnose why a successful test-mail message could be perceived as not
      received when multiple default recipients were configured.
- [x] Change test-mail recipient resolution so, without an explicit target, it
      submits the test message to all configured global default recipients
      instead of only the first default recipient.
- [x] Return test-mail recipient count and recipient source from the API
      without exposing SMTP secrets.
- [x] Update Mail Configuration test-console success text to show submitted
      recipient count and preserve the warning that SMTP acceptance is not
      inbox proof.
- [x] Add mocked-SMTP regression coverage proving the multi-recipient default
      list is submitted in one test message and automated verification does not
      send external mail.

## CR-046 - Platform Account Avatar Safe Cache Display Regression Fix

Planning status:

CR-046 is a verified regression fix for the administrator Platform Accounts
identity display. It does not reopen Phase 5/6 login-state behavior or Phase 21
visual refinement.

- [x] Diagnose why the recognized Douyin account avatar disappeared even
      though `platform_avatar_url` was stored.
- [x] Preserve signed external avatar URLs as server-side runtime data only and
      stop sending those external URLs to the frontend.
- [x] Return a same-origin account-avatar URL from the social-account API when
      a platform avatar source exists.
- [x] Add an administrator-only avatar endpoint that lazily fetches, validates,
      caches, and serves account-avatar images from runtime storage.
- [x] Reject normal-user avatar access and path traversal attempts.
- [x] Keep avatar cache files as runtime data outside Git.
- [x] Add regression tests for signed-avatar redaction, same-origin avatar
      output, avatar serving, normal-user denial, traversal rejection, and
      existing profile/cookie hiding behavior.

## Phase 21 - Formal Console Page-Level UI/UX Refinement

Lifecycle status:

CR-040 / Phase 21 is implemented, verified, merged, and closed as a
frontend-only page-level UI/UX refinement for the formal `/monitor` console.
It does not reopen CR-033 or replace the formal console with the static
prototype. The protected implementation baseline on current `main` is:
one top-level `任务中心`, default task/report grouping, `运行记录` as the
run-record subview, Run Detail with `概览` / `采集日志` / `采集内容` /
`AI 评估` / `报告` / `邮件交付`, CR-071/CR-072 enhanced controls,
CR-073 drawer scroll normalization, and CR-074 top-bar refresh behavior.
Future UI work must use a separate accepted follow-up CR and must not restore
the old separate Run Center / Report Center structure or change Task Center,
Run Detail, drawer, modal, menu, select/date, close, scroll, or routing logic
without that explicit boundary.

- [x] Create `docs/FORMAL_CONSOLE_UI_REFINEMENT_PLAN.md` with complete
      execution guidance for what to do, where to do it, how to test it, how to
      verify it, what target experience to reach, and how acceptance will be
      judged.
- [x] Confirm CR-040 as the accepted Phase 21 implementation scope.
- [x] Confirm that the currently unrendered `Users And Permissions` surface is
      out of Phase 21 scope. If the user wants it implemented later, record a
      separate new-capability CR instead of treating it as visual refinement.
- [x] Rebaseline Phase 21 planning docs on 2026-06-19 against the current Task
      Center / Run Detail frontend after CR-051, CR-053, CR-069, CR-071,
      CR-072, CR-073, and CR-074.
- [x] Implement Phase 21 in small frontend workstreams A-O with local
      smoke-checks before the final Phase 21P cross-page verification gate.

### Phase 21A - Global Shell And Design Tokens

- [x] Refine formal-console neutral, primary, border, background, text,
      status, focus, disabled, toast, empty-state, error-state, skeleton, and
      modal base styles in the formal frontend.
- [x] Keep the no-build Vanilla JavaScript plus CSS custom-property stack.
- [x] Verify login and all logged-in pages still render without console errors
      or horizontal overflow.

### Phase 21B - Navigation Hierarchy

- [x] Apply the focused navigation visual refinement for the current formal
      console shell: light sidebar, compact icon-supported first/second-level
      entries, desktop collapse-to-icon rail, compact top-right account menu,
      and system-aligned teal active state.
- [x] Split navigation hover and active styles so first-level and second-level
      hover states use pure neutral light gray while selected entries keep the
      restrained Phase 21 accent; add regression coverage so hover/active
      combined selectors do not return and collapsed sidebar hover does not
      reuse the teal selected palette.
- [x] Implement CR-075 responsive navigation consistency: desktop keeps the
      full/collapsible sidebar, tablet/narrow desktop defaults to the persistent
      collapsed icon side rail without the top-left mobile trigger, and true
      mobile keeps the drawer trigger/backdrop/Escape/page-selection close
      behavior.
- [x] Implement CR-076 mobile header layout resilience: on true mobile, keep
      the drawer trigger while moving the title and status chips into their own
      readable rows so status, refresh, and account controls cannot squeeze the
      title into one-character vertical wrapping.
- [x] Implement CR-077 mobile header final-cascade resilience: mirror the
      accepted mobile header grid in the formal page's final inline style layer
      and update regression coverage to inspect all inline style blocks, so
      later inline rules cannot re-squeeze the title after `monitor.css` loads.
- [x] Implement CR-078 mobile and tablet navigation layout resilience: keep the
      final mobile header title horizontal, keep representative resource pages
      inside the phone viewport, keep closed mobile drawer width off-canvas, and
      keep the tablet collapsed side rail's final item out of the bottom
      collapse-button hit area.
- [x] Implement CR-079 mobile header compact rail resilience: keep the phone
      header on a compact icon navigation trigger plus a stable title column,
      move status chips to a wrapping row, and prevent resource pages such as
      `代理资源` from squeezing Chinese text into one-character columns.
- [x] Implement CR-080 tablet side-rail horizontal-scrollbar cleanup: prevent
      the `768px - 1279px` collapsed icon rail from exposing a bottom
      horizontal scrollbar while keeping the collapse button, vertical rail
      scrolling, and administrator final navigation entries reachable.
- [x] Implement CR-084 tablet side-rail narrow-width collapse regression fix:
      keep the `768px - 1279px` collapsed icon rail contracted to the intended
      narrow width in the final cascade at `1024x768`, while preserving the
      collapse button and vertically scrollable navigation rail.
- [x] Implement CR-085 narrow tablet inline-cascade side-rail regression fix:
      mirror the accepted `768px - 1279px` icon-rail width, mobile-trigger
      hiding, and collapse-button visibility in the final inline style layer so
      an in-app panel around `809px` cannot reserve the wrong shell grid track.
- [x] Strengthen the visual difference between first-level task-loop pages and
      second-level Resource Management/System Configuration pages.
- [x] Preserve administrator and normal-user menu visibility.
- [x] Verify desktop, tablet, and mobile navigation open, close, switch pages,
      and preserve active state.

### Phase 21C - Operations Home Refinement

- [x] Reduce the onboarding feeling of the `01-05` quick-entry block while
      preserving all five shortcuts.
- [x] Prioritize operational data, urgent exceptions, report output, email
      delivery, and resource impact before guidance content.
- [x] Add layout-resilience safeguards for Operations Home closed-loop,
      shortcut, metric, and resource-health sections so desktop, tablet, and
      mobile views wrap or collapse before text becomes one-character vertical
      columns.
- [x] Verify administrator and normal-user Operations Home views remain
      role-safe and usable at `1440x900`, `1024x768`, and `390x844`.
- [x] Capture or record dashboard layout checks proving no text overlap,
      unreadable card labels, hidden primary actions, horizontal overflow, or
      one-character-per-line wrapping.

### Phase 21D - Monitoring Tasks And Task Drawer

- [x] Refine the Monitoring page and task drawer hierarchy without removing
      any formal fields, filters, row actions, more-menu actions, or drawer
      actions.
- [x] Preserve normal-user simplified task creation and administrator advanced
      task settings.
- [x] Verify task create/edit, sample fill, clear, save, close, run, stop,
      pause/resume, and delete flows.

### Phase 21E - Platform Accounts

- [x] Refine the Platform Accounts page and account dialog as a complete
      account-maintenance workflow, not a generic configuration modal.
- [x] Preserve QR login, local-window fallback where allowed, Cookie login,
      login records, account identity/details, filters, attention filter,
      batch actions, row detail, and row more menu.
- [x] Verify every login status, batch action, row-menu action, save, delete,
      and close path at desktop, tablet, and mobile widths.

### Phase 21F - Proxy Resources

- [x] Refine proxy list density, masked-secret readability, health/error
      scanning, and proxy drawer layout.
- [x] Preserve add, CR-074 top-bar refresh, view accounts, search, status
      filter, clear filters, row edit/delete, clear, save, and close.

### Phase 21G - AI Access

- [x] Refine AI Access resource layout, model selection, model-list loading,
      default state, delete action, and connection-test feedback.
- [x] Preserve add, refresh, view rules, search, protocol/test filters, clear
      filters, edit, test, set default, delete, model list, save, and close.
- [x] Apply CR-081 during Phase 21G verification so AI Access, proxy, account,
      mail, task, and test drawers keep fixed footer actions outside
      `.drawer-scroll-body`, with the scrollbar limited to the middle content
      region.

### Phase 21G.1 - AI Access Model Helper Copy Removal Regression Fix

- [x] Remove the persistent helper sentence under the AI Access model combobox
      so the model section no longer occupies a full extra line.
- [x] Preserve the `获取模型列表` button, manual model-name entry, selection
      list, drawer layout, fixed footer, close behavior, and connection-test
      flow.
- [x] Update the AI Access regression test to stop requiring the removed helper
      sentence and instead assert the combobox remains usable without the extra
      copy.
- [x] Run targeted frontend tests, inline script parse, syntax checks, docs
      check, and browser verification at desktop, tablet, and phone widths.

### Phase 21H - AI Evaluation Rules

- [x] Refine the AI rule editor into clearer sections while preserving every
      rule field, prompt preview, sample test field, result area, row action,
      and more-menu action.
- [x] Preserve rule testing, default switching, restore default, save, delete,
      and close flows.

### Phase 21I - Mail Configuration

- [x] Refine SMTP form layout, sender/recipient wording, default-recipient
      explanation, masked password display, and mail-test feedback.
- [x] Apply CR-049 action hierarchy: keep edit configuration, send test mail,
      refresh/status, delivery-status navigation, and compact real-email state
      in one page-level action bar.
- [x] Remove or demote duplicated edit/test controls from the SMTP/defaults
      summary section so that section reads as configuration/status summary.
- [x] Render the real-email send state as a compact labeled toolbar
      toggle/button with concise state text while preserving explicit
      confirmation before enabling real SMTP.
- [x] Preserve edit config, send test mail, refresh config, view delivery
      status, save, cancel, close, and test-console behavior.
- [x] Add a DOM regression test that fails if the SMTP/defaults summary repeats
      the primary edit/test actions already present in the header.
- [x] Add Phase 21I static regression coverage for the mail summary cards,
      compact real-email switch, mail configuration drawer, mail test drawer,
      fixed footer boundaries, and CR-074 duplicate-refresh protection.
- [x] Verify Mail Configuration at `1440x900`, `1024x768`, and `390x844`:
      page opens, required actions remain present, no browser console error,
      no horizontal overflow, no one-character Chinese text columns, and mail
      config/test drawer scrollbars remain between the fixed header and footer.

### Phase 21J - Mail Templates

- [x] Refine mail-template list, variable hints, active/current state, raw HTML
      editor, subject field, and iframe preview stability.
- [x] Preserve add, refresh, view mail config, search/status filters, row edit,
      set current where available, delete, save, refresh preview, clear, close,
      and iframe preview.
- [x] Keep CR-039 governed preset direction as future product work and do not
      remove free-form HTML editing in this visual refinement batch.

### CR-089 - Mail Template Row Helper Text And Update-Time Compactness

- [x] Remove the visible `正文占位符已保留` row helper sentence from the mail
      template list.
- [x] Compact the `更新时间` cell with the same wrap-safe time treatment used
      by the AI rule table so the row does not widen.
- [x] Verify the mail template list still supports add, refresh, view mail
      config, search/status filters, row edit, set current, delete, save,
      refresh preview, clear, close, and iframe preview at desktop, tablet,
      and mobile widths.

### CR-090 - AI Rule List And Modal Field Width Compactness

- [x] Narrow the `AI 评估规则` list table so the rule-name, last-test, update-
      time, and action columns read as a denser configuration surface.
- [x] Rebalance the `AI 评估规则` modal's internal grid and section spacing so
      the basic info, rule configuration, schema, sample, and result regions
      feel more proportional; the current narrow follow-up also needs the
      basic-info card to keep `规则名称` as a single full-width field and the
      sample/test split to read more evenly.
- [x] Preserve rule workflow, test/save/restore/default actions, and modal
      close behavior while keeping the layout readable at desktop, tablet, and
      mobile widths.

### Phase 21K - Runtime Strategy

- [x] Refine grouped runtime-setting tables for scanability, locked-state
      readability, valid range, apply scope, and save feedback.
- [x] Preserve refresh strategy, save strategy, view diagnostics, grouped
      tables, current values, inputs, valid ranges, apply scopes, and lock
      states.

### Phase 21L - Task Center Conservative Visual Pass

- [x] Refine the current Task Center only as a conservative visual pass:
      colors, contrast, density, metric-chip styling, table separators, status
      treatment, loading/empty/error states, focus states, and responsive
      wrapping.
- [x] Preserve the single top-level `任务中心`, default task/report grouping,
      `运行记录` subview, filters, pagination, top-bar page refresh, scoped
      refresh actions, compact status badges, grouped metric chips, and one
      first-level `详情` route into Run Detail.
- [x] Preserve report preview, report-scoped lead inspection, delivery history,
      resend, downloads, run logs, copy/download log actions, and report/email
      evidence through Run Detail or the accepted scoped secondary surfaces.
- [x] Do not restore separate top-level Run Center / Report Center pages,
      reintroduce duplicate first-level log/preview/lead/delivery/download row
      actions, move lead-state filters into the first-level Task Center
      toolbar, or change grouping, `运行记录`, Run Detail tab, pagination,
      filter, owner-scope, or report-scope semantics.

### Phase 21M - Overlay And Run Detail Freeze Gate

- [x] Refine only overlay chrome and visual states for existing drawers,
      modals, row menus, Run Detail, report preview, delivery history, run/log
      surfaces, enhanced select menus, and local attached date menus.
- [x] Preserve Run Detail's six sections, task drawer structure, account/proxy/
      AI/mail/template drawer and modal categories, close buttons, backdrop and
      Escape behavior, bottom actions, `.drawer-scroll-body`, enhanced select
      labels/values, task edit date-picker behavior, report scope behavior, and
      all existing copy/download/resend/refresh/preview/detail actions.
- [x] Do not move fields/actions into a different workflow category, replace
      drawers with new pages/cards, change Run Detail routing, change AI
      evaluation filtering, alter delivery-history scope, move close buttons,
      or simplify away operational fields for visual neatness.
- [x] Verify Phase 21M with static checks, targeted frontend regression tests,
      and browser checks at `1440x900`, `1024x768`, and `390x844`, including
      Run Detail six-tab switching, log copy/download actions, enhanced
      select/date menus, representative fixed-footer drawers, no console
      errors, no document horizontal overflow, and no one-character Chinese
      text columns.
- [x] Apply CR-048 scope clarity so lead detail reads as selected-report or
      clearly labeled filtered-aggregate detail, not an unlabeled global lead
      table.
- [x] Make "view leads" visually discoverable separately from report preview
      while preserving preview-driven context switching.
- [x] Apply CR-049 delivery-history hierarchy so delivery history is opened as
      scoped secondary detail from a report row/status action and does not
      dominate the initial report archive layout.
- [x] Preserve report filters, refresh report, refresh email status, refresh
      history, preview, more menu, delivery history, resend, HTML/Excel/
      Markdown downloads, lead detail, and preview iframe.
- [x] Add a browser/layout regression test that fails if lead detail or
      delivery history renders as an unlabeled global table or default-dominant
      panel.

## CR-051 - Task Center And Report Grouping Consolidation

Planning status:

CR-051 is a verified frontend information-architecture optimization after
Run Detail, report grouping, and scoped lead/delivery drawers were already in
place. It consolidates the former top-level Run Center and Report Center entry
points into one `任务中心` without changing backend APIs, data model,
permissions, crawler behavior, AI behavior, SMTP behavior, or report
generation semantics.

- [x] Rename the primary run/report navigation entry to `任务中心`.
- [x] Remove the separate top-level Report Center nav entry and `<section
      id="reports">` page section from the formal console.
- [x] Reuse the existing report-by-monitoring-task grouping inside Task Center
      as the default first view.
- [x] Add a `运行记录` subview inside Task Center for the old run-record table,
      filters, pagination, stop, archive, restore, and Run Detail actions.
- [x] Keep Task Center's first-level task grouping focused on monitoring-task
      identity and result summary instead of copying every old run-record
      column.
- [x] Keep run ID, task ID, type, visibility, duration, and full failure reason
      available in `运行记录` and Run Detail.
- [x] Keep Run Detail as the deep drilldown for lifecycle, logs, AI
      evaluation, per-run report, and email delivery inspection.
- [x] Keep report preview, report-scoped lead inspection, delivery history,
      resend, and downloads reachable from the task-group row secondary
      actions or `更多` menu.
- [x] Preserve CR-048 / CR-049 scoped drawer behavior and avoid reintroducing
      a first-level global lead or delivery-history panel.
- [x] Add a CR-051 regression test proving there is one Task Center entry,
      grouped reports live inside it, run records are a subview, and legacy
      report shortcuts normalize to the task-group view.

## CR-052 - Task Center Row Action Deduplication

Planning status:

CR-052 is a verified frontend information-architecture cleanup after CR-051.
It removes first-level row actions that duplicate Run Detail content while
preserving the underlying log and report preview capabilities.

- [x] Remove the run-record row-level `查看日志` button.
- [x] Keep run logs available in Run Detail's `采集日志` section.
- [x] Preserve log copy and download actions from the Run Detail log section.
- [x] Remove the task-group report row-level `预览` button.
- [x] Keep report preview available in Run Detail's `报告` section.
- [x] Keep task-group report rows focused on `运行详情` and `更多`, with
      `更多` retaining report-scoped leads, delivery history, resend, and
      downloads.
- [x] Add regression checks preventing the duplicate row-level actions from
      returning.

## CR-053 - Task Center Field Priority And Global Select Alignment

Planning status:

CR-053 is a verified frontend information-density and interaction-stability
follow-up after CR-051/CR-052. It keeps Task Center as the single entry while
making the run table easier to scan and fixing global select/dropdown
alignment.

- [x] Put `任务 ID`, `运行 ID`, and compact `状态` at the beginning of flat
      Task Center run tables.
- [x] In grouped mode, hide duplicated `任务 ID` inside the group table and
      start group rows with `运行 ID` followed by compact `状态`.
- [x] Keep terminal success rows short and move full progress detail to Run
      Detail instead of the first-level status cell.
- [x] Keep grouped mode on the same run-row field mapping while using the
      group header for task ID, task name, platform, and keyword context.
- [x] Remove the duplicate filter-toolbar refresh button and keep the page
      header refresh as the single Task Center refresh entry.
- [x] Reorder the filter toolbar so task/law firm, status, platform, and date
      range come before secondary run type, visibility, and page size.
- [x] Fix global native select/dropdown visual alignment by preventing the
      main content container from clipping vertical overflow.
- [x] Add targeted regression checks for field order, compact status, single
      refresh, and dropdown-safe content overflow.

## CR-054 - Task Center Status Badge Compactness Regression Fix

Planning status:

CR-054 is a verified frontend regression fix for the CR-053 compact-status
contract. It prevents long backend display/progress text from becoming the
first-level Task Center status badge.

- [x] Normalize Task Center status badge labels to short lifecycle states such
      as `已完成`, `运行中`, `运行超时`, `已取消`, and `执行中断`.
- [x] Prevent long `display_status` or progress text from rendering inside the
      first-level status badge.
- [x] Keep active-run short progress cues below the badge while leaving full
      progress detail in Run Detail.
- [x] Strengthen Task Center CSS so status badges remain text-sized and do not
      stretch into full-width bars.
- [x] Add targeted regression checks for compact status labels and badge
      width rules.
- [x] Verify syntax, targeted frontend tests, docs consistency, and local
      browser behavior.

## CR-055 - Task Center Status Column Visual Refinement

Planning status:

CR-055 is a verified frontend-only follow-up to CR-054. It reduces the visual
weight of the Task Center status column without changing grouping, field order,
run lifecycle wording, Run Detail, reports, AI traceability, or email delivery.

- [x] Add a stable `col-status` table class for `状态` headers and cells.
- [x] Stop rendering first-level Task Center run status badges with the global
      `.status` pill class.
- [x] Restyle run status badges as narrow state-dot labels and constrain the
      status column width in grouped and flat modes.
- [x] Preserve compact lifecycle labels, short active progress helper text, and
      all existing Task Center row/detail behavior.
- [x] Update regression tests and documentation for the refined status column.
- [x] Verify syntax, targeted frontend tests, docs consistency, and local
      browser behavior.

## CR-056 - Filter Dropdown Alignment Regression Fix

Planning status:

CR-056 is a verified frontend-only regression fix after browser review found
that the CR-053 native-select overflow fix was still insufficient at
`1440x900`. It keeps existing filter values and page logic while replacing the
visible dropdown surface for filter-region selects with a fixed-position
in-page floating menu.

- [x] Enhance only `.page-filter-region select` controls, leaving ordinary
      form/configuration selects native.
- [x] Keep each original select element in place so existing `val(...)`,
      inline `onchange`, and event-listener filter logic still reads the same
      value.
- [x] Render the visible filter dropdown as a button plus fixed-position menu
      appended to the document body.
- [x] Close the filter menu on outside click, Escape, scroll, resize, and
      selection.
- [x] Synchronize visible button text when code paths such as clear filters or
      role mode update the underlying select value.
- [x] Add regression coverage for filter-region scope, fixed menu positioning,
      original change-event dispatch, and Task Center filter preservation.
- [x] Verify syntax, targeted frontend tests, docs consistency, and browser
      behavior at `1440x900`.

## CR-057 - Task Center Group Summary Metric Chips

Planning status:

CR-057 is a verified frontend-only Task Center density refinement after browser
review found the grouped-run header summary too copy-like. It preserves
grouping, counts, filters, Run Detail, and role behavior while making the
aggregate values scannable.

- [x] Replace the grouped-run header's long slash-separated aggregate sentence
      with compact labeled metric chips.
- [x] Keep run count, collected count, new count, suspected negative, high risk,
      manual-review, and unevaluated values visible in the group header.
- [x] Keep limited-context, deleted-task, and historical-context explanations as
      a short note only when needed.
- [x] Preserve the grouped table, flat table, filters, single `详情` row action,
      Run Detail entry, and CR-056 filter dropdown behavior.
- [x] Verify syntax, targeted frontend tests, docs consistency, and browser
      behavior at `1440x900`.

## CR-058 - Filter Date Picker Alignment Regression Fix

Planning status:

CR-058 is a verified frontend-only regression fix after browser review found
that Task Center date filters could still misalign after CR-056. CR-056 covered
filter-region selects; this follow-up keeps page-level date filter behavior
stable by replacing only the visible date-picker surface inside
`.page-filter-region` with a fixed-position in-page menu.

- [x] Enhance only `.page-filter-region input[type="date"]` controls, leaving
      ordinary form/configuration date inputs native.
- [x] Keep each original date input in place so existing `val(...)`, inline
      `onchange`, and event-listener filter logic still reads the same value.
- [x] Render the visible date picker as a button plus fixed-position date menu
      appended to the document body.
- [x] Selecting or clearing a date updates the original input value and
      dispatches the same `change` event existing filters use.
- [x] Synchronize visible date button text when code paths such as
      `clearRunFilters()` update the underlying date value.
- [x] Keep date filter menus visually anchored to the trigger by centering the
      wider menu on the trigger by default and clamping inward only as needed
      to stay inside the viewport.
- [x] Add regression coverage for filter-date scope, fixed menu positioning,
      original change-event dispatch, and Task Center filter preservation.
- [x] Verify syntax, targeted frontend tests, docs consistency, and browser
      behavior at the desktop review viewport.

## CR-059 - Filter Date Picker Edge Anchoring Regression Fix

Planning status:

CR-059 is a verified frontend-only regression fix after browser review found
CR-058's centered wider date menu could still look visually offset in the Task
Center date filters. It keeps the same custom date menu, original input values,
and filter semantics, but changes the position rule to edge anchoring.

- [x] Keep CR-058's scope limited to `.page-filter-region input[type="date"]`.
- [x] Align the date menu's left edge to the clicked trigger when there is
      enough room.
- [x] Align the date menu's right edge to the clicked trigger near the right
      viewport edge when needed to avoid overflow.
- [x] Keep viewport clamping as a final fallback.
- [x] Preserve date selection, clear/reset synchronization, original
      `change` events, and ordinary form/configuration date inputs.
- [x] Verify syntax, targeted frontend tests, docs consistency, and browser
      coordinate behavior at the desktop review viewport.

## CR-060 - Filter Date Picker Compact Center Alignment Regression Fix

Planning status:

CR-060 is a verified frontend-only regression fix after browser review found
CR-059's edge-aligned date menu still felt visually offset because the calendar
surface was much wider than the date trigger. It keeps the same custom date
menu, original input values, and filter semantics, but changes the visual rule
to a compact calendar width with trigger-center alignment.

- [x] Keep CR-058's scope limited to `.page-filter-region input[type="date"]`.
- [x] Reduce the date menu's minimum visual width so it stays close to narrow
      date filter buttons.
- [x] Align the date menu center line to the clicked trigger center line when
      space allows.
- [x] Keep viewport clamping as a final fallback.
- [x] Preserve date selection, clear/reset synchronization, original
      `change` events, and ordinary form/configuration date inputs.
- [x] Verify syntax, targeted frontend tests, docs consistency, and browser
      coordinate behavior at the desktop review viewport.

## CR-061 - Filter Date Picker Trigger-Width Anchoring Regression Fix

Planning status:

CR-061 is a verified frontend-only regression fix after browser review found
CR-060's mathematically centered date menu still felt visually offset because
the menu was wider than the date trigger. It keeps the same custom date menu,
original input values, and filter semantics, but changes the visual rule to a
trigger-width menu aligned to the trigger's left edge.

- [x] Keep CR-058's scope limited to `.page-filter-region input[type="date"]`.
- [x] Match the date menu width to the clicked date trigger when viewport
      space allows.
- [x] Align the date menu left edge to the clicked trigger left edge so it
      reads as attached to the filter box.
- [x] Compact the month grid, navigation, and quick actions so the calendar
      remains readable inside the trigger-width menu.
- [x] Keep viewport clamping as a final fallback.
- [x] Preserve date selection, clear/reset synchronization, original
      `change` events, and ordinary form/configuration date inputs.
- [x] Verify syntax, targeted frontend tests, and browser coordinate behavior
      at the desktop review viewport.

## CR-062 - Filter Date Picker Grid Compression Regression Fix

Planning status:

CR-062 is a verified frontend-only regression fix after browser review found
CR-061's trigger-width date menu shell was aligned, but the internal calendar
grid could still look wrong because browser button padding and auto minimum
width compressed or clipped the last day columns.

- [x] Keep CR-061's trigger-width menu and left-edge anchoring behavior.
- [x] Reset date-cell minimum width and padding so the seven day columns share
      the available grid width without overflow.
- [x] Preserve weekdays, day cells, selected-day state, today state, quick
      actions, date selection, clearing, original `change` events, and ordinary
      form/configuration date input behavior.
- [x] Add regression coverage for readable non-overflowing date cells inside
      the trigger-width menu.
- [x] Verify targeted frontend tests and browser visual/coordinate behavior at
      the desktop review viewport.

## CR-063 - Filter Date Picker Readable Anchored Popover Regression Fix

Planning status:

CR-063 is a verified frontend-only regression fix after browser review found
that CR-062's trigger-width date menu was coordinate-correct but still felt
visually wrong because the calendar was too cramped. It keeps the same scoped
custom date menu and original date-input semantics, but makes the calendar a
readable compact popover with a trigger-aligned anchor marker.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Use a readable compact calendar width for narrow desktop date triggers
      instead of forcing the menu to the trigger width.
- [x] Add a top anchor marker aligned to the clicked trigger center so the
      wider calendar still reads as attached.
- [x] Right-align near the viewport edge and clamp only as a final overflow
      fallback.
- [x] Preserve date selection, clearing, reset synchronization, original
      `change` events, weekday/day grid, and existing filtering behavior.
- [x] Add regression coverage for the readable anchored popover rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop, tablet, and mobile widths.

## CR-064 - Filter Date Picker Trigger-Attached Edge Shrink Regression Fix

Planning status:

CR-064 is a verified frontend-only regression fix after browser review found
that CR-063's right-edge alignment still made the right-side date menu look
offset. It keeps the readable custom date menu and original date-input
semantics, but changes edge handling so the menu stays attached to the clicked
date field whenever a slight readable-width shrink can keep it inside the
visual viewport.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Prefer trigger-left attachment for both left-side and right-side date
      filters.
- [x] Use visual viewport width for fixed-position date-menu edge checks.
- [x] Near the right edge, shrink the readable menu within a safe lower bound
      before falling back to right alignment or viewport clamping.
- [x] Preserve the top anchor marker, date selection, clearing, reset
      synchronization, original `change` events, weekday/day grid, and existing
      filtering behavior.
- [x] Add regression coverage for the trigger-attached shrink rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop, tablet, and mobile widths.

## CR-065 - Filter Date Picker Center-Anchored Visual Alignment Regression Fix

Planning status:

CR-065 is a verified historical frontend-only regression fix after browser review found
that CR-064 still made the right-side date menu read as offset at desktop
review width. It keeps the same scoped custom date menu and original date-input
semantics, but changes the visual rule so the floating menu is centered on the
clicked trigger when the viewport can accommodate it. It is superseded by
CR-066 after browser review found the centered readable menu still looked
detached from the date field.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Use visual viewport width for fixed-position date-menu edge checks.
- [x] Use a compact readable calendar width while centering the menu on the
      clicked trigger.
- [x] Clamp inward only when center alignment would overflow the visual
      viewport.
- [x] Preserve the top anchor marker, date selection, clearing, reset
      synchronization, original `change` events, weekday/day grid, and existing
      filtering behavior.
- [x] Add regression coverage for the center-anchored visual rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop, tablet, and mobile widths.

## CR-066 - Filter Date Picker Trigger-Attached Dropdown Alignment Regression Fix

Planning status:

CR-066 is a verified historical frontend-only regression fix after browser review found
that CR-065's mathematically centered readable calendar still looked detached
from the date input at desktop review width. It keeps the same scoped custom
date menu and original date-input semantics, but changes the visual rule so the
floating menu opens from the clicked trigger's left edge, like the other filter
dropdowns, while shrinking near the right edge before clamping. It is
superseded by CR-067 after browser review found that a wider-than-trigger menu
could still look visually detached even when its left edge was aligned.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Use visual viewport width for fixed-position date-menu edge checks.
- [x] Use a compact readable calendar width while aligning the menu's left edge
      to the clicked trigger when space allows.
- [x] Shrink the menu first when the readable width would overflow the visual
      viewport on the right, then clamp only as the final fallback.
- [x] Preserve the top anchor marker, date selection, clearing, reset
      synchronization, original `change` events, weekday/day grid, and existing
      filtering behavior.
- [x] Add regression coverage for the trigger-attached dropdown rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop review width.

## CR-067 - Filter Date Picker Trigger-Width Visual Attachment Regression Fix

Planning status:

CR-067 is a verified frontend-only regression fix after browser review found
that CR-066's left-attached menu could still look offset because the right-side
date menu remained wider than the clicked trigger. It keeps the same scoped
custom date menu and original date-input semantics, but changes the current
visual rule so the menu matches the clicked trigger width whenever that width
is usable.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Use visual viewport width for fixed-position date-menu edge checks.
- [x] Match the visible date menu width to the clicked trigger width when the
      trigger is wide enough for the seven-column grid.
- [x] Use a small minimum readable width only for unusually narrow trigger
      fields.
- [x] Clamp or shrink only when the attached menu would overflow the visual
      viewport.
- [x] Preserve the top anchor marker, date selection, clearing, reset
      synchronization, original `change` events, weekday/day grid, and existing
      filtering behavior.
- [x] Add regression coverage for the trigger-width visual attachment rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop review width.

## CR-068 - Filter Date Picker Local Attached Menu Regression Fix

Planning status:

CR-068 is a verified frontend-only regression fix after browser review found
that CR-067's trigger-width fixed-position date menu could still read as
visually offset at `1440x900`. It keeps the same scoped custom date menu and
original date-input semantics, but changes the current visual rule so the
active menu is mounted inside the clicked date control wrapper and positioned
locally under that field.

- [x] Keep `.page-filter-region input[type="date"]` as the only enhanced date
      input scope; ordinary form/configuration date inputs remain native.
- [x] Move the active date menu into the clicked `.filter-date-enhanced`
      wrapper before positioning.
- [x] Use wrapper-local `position: absolute`, `left: 0`, and
      `top: calc(100% + 4px)` so the date menu opens directly below the
      clicked field.
- [x] Keep the visible date menu width equal to the clicked trigger width.
- [x] Preserve the top anchor marker, date selection, clearing, reset
      synchronization, original `change` events, weekday/day grid, and
      existing filtering behavior.
- [x] Add regression coverage for the local attached menu rule.
- [x] Verify targeted frontend tests, inline script parse, docs consistency,
      and browser behavior at desktop review width.

## CR-069 - Run Detail AI Evaluation Lead Entry Consolidation

Planning status:

CR-069 is a verified information-architecture optimization after Task
Center acceptance found that report `查看线索` and Run Detail `AI 评估`
duplicated the same lead/evaluation detail path. The intended current rule is
that `AI 评估` is the single primary lead/evaluation table, while report
`查看线索` is only a report-scoped filter shortcut into that table.

- [x] Record CR-069 as an existing-feature optimization without rewriting
      CR-048/CR-051 historical verification.
- [x] Add Run Detail API support for `report_id` AI-evaluation filtering with
      existing owner scope and role-safe redaction preserved.
- [x] Add Run Detail `AI 评估` filters for report, status, risk, platform,
      keyword, and title.
- [x] Change report `查看线索` to switch to the same `AI 评估` tab with the
      selected report filter applied.
- [x] Remove the duplicate report-lead drawer/table from the current UI
      surface while keeping `/leads` compatibility for old API paths.
- [x] Keep report preview, downloads, delivery history, resend, per-evaluation
      AI trace detail, and limited-context old rows available.
- [x] Keep the `报告范围` selector visible only when a run has multiple reports;
      use a read-only scope note for runs with zero or one report.
- [x] Keep Run Detail `AI 评估` filter dropdowns visually consistent with
      first-level Task Center page-filter dropdowns.
- [x] Run targeted Phase 20/CR-048/CR-051 regression tests, syntax checks,
      docs check, and browser acceptance.

## CR-071 - Drawer And Modal Select Dropdown Consistency

Planning status:

CR-071 is a verified frontend-only interaction consistency optimization after
browser review found that selected drawer/modal form dropdowns still used
native select rendering while Task Center filters and Run Detail AI filters
used the enhanced `.page-filter-region select` dropdown mechanism.

- [x] Record CR-071 as an existing-feature optimization without rewriting
      CR-056 or CR-068 historical verification.
- [x] Opt the accepted secondary surfaces into the existing
      `.page-filter-region select` enhancement: task edit drawer, platform
      account detail drawer, proxy edit drawer, AI access edit drawer, AI rule
      edit modal, mail configuration edit drawer, and mail template edit
      drawer.
- [x] Keep AI Access `模型名称` on its existing combobox interaction and out of
      the filter dropdown enhancement.
- [x] Keep task edit drawer custom date inputs native and preserve CR-068's
      date-picker scope.
- [x] Synchronize enhanced button labels after dynamic account, proxy, AI
      profile, email template, platform-login, and disabled-state option
      updates.
- [x] Keep modal opt-in regions visually neutral while reusing the same
      `.filter-select-*` dropdown classes and menu.
- [x] Add static regression coverage for the drawer/modal opt-in surfaces,
      dynamic sync hooks, AI model-name exclusion, and native date-input
      boundary.
- [x] Verify targeted frontend tests, syntax checks, inline script parse, docs
      consistency, and browser behavior on representative drawer/modal
      dropdowns.

## CR-072 - Task Edit Custom Date Picker Consistency

Planning status:

CR-072 is a verified frontend-only interaction consistency follow-up to
CR-071. It does not rewrite CR-071's historical verification, but supersedes
the task-edit-date exception for exactly the Monitoring task edit drawer's
`custom_start` and `custom_end` fields.

- [x] Record CR-072 as an existing-feature optimization linked to CR-068 and
      CR-071.
- [x] Opt `custom_start` and `custom_end` into the existing
      `.page-filter-region input[type="date"]` enhancement by placing them in
      a neutral `.page-filter-region.modal-filter-region` scope.
- [x] Reuse the existing `.filter-date-enhanced`,
      `.filter-select-button.filter-date-button`, and `.filter-date-menu`
      local attached date-picker mechanism.
- [x] Preserve the original date input values, form save payload, and `change`
      event behavior when selecting or clearing dates.
- [x] Keep unrelated ordinary business date fields native unless separately
      accepted.
- [x] Add regression coverage for the task edit custom date opt-in, date-menu
      local attachment, and CR-071 preserved exclusions.
- [x] Verify targeted frontend tests, syntax checks, inline script parse, docs
      consistency, and browser behavior for both task edit custom date fields.

## CR-073 - Scrollable Drawer Corner Radius Regression Fix

Planning status:

CR-073 is a verified frontend-only visual regression fix after browser review
found that scrollable drawers could show a full-height scrollbar starting at
the absolute top edge, visually flattening the top-right rounded corner. It
does not reopen CR-038, CR-071, or CR-072.

- [x] Record CR-073 as a regression fix linked to CR-038 scrollable drawer
      close controls and CR-071/CR-072 drawer/modal interaction consistency.
- [x] Keep shared drawers scrollable by moving content scrolling into a
      normalized `.drawer-scroll-body`, while the outer drawer shell keeps the
      rounded chrome and header controls outside the scrollbar.
- [x] Keep the top-right close button in the header's top-right position; do
      not move it toward the center as the corner-radius workaround.
- [x] Preserve sticky header, backdrop/Escape close behavior, enhanced select
      dropdowns, and task edit custom date picker behavior.
- [x] Add static regression coverage for shared drawer inner-scroll structure,
      scrollbar/radius styling, and representative drawer surfaces.
- [x] Verify targeted frontend tests, syntax checks, inline script parse, docs
      consistency, and browser behavior on a long Monitoring task drawer.

## CR-081 - Scrollable Drawer Fixed Footer Boundary Regression Fix

Planning status:

CR-081 is a focused frontend regression fix raised during Phase 21G review after
scrollable drawers showed footer action bars inside the scrolling content area.
It extends the CR-073 `.drawer-scroll-body` structure without reopening the
historical CR-073 completion state.

- [x] Record CR-081 as a regression fix linked to CR-073 and Phase 21G.
- [x] Keep `.drawer-scroll-body` as the content scroll owner while moving
      `.form-actions`, `.resource-modal-actions`, `.account-flow-actions`,
      `.ai-test-actions`, and `.rule-modal-actions` to direct drawer footer
      chrome.
- [x] Preserve close buttons, backdrop/Escape behavior, enhanced select/date
      behavior, Run Detail tabs, Task Center, owner/report scope, and top-bar
      refresh semantics.
- [x] Add static regression coverage for footer extraction, `.drawer-fixed-footer`
      CSS, and the absence of the old in-scroll sticky action boundary.
- [x] Verify representative scrollable drawers/modals in browser at desktop,
      tablet, and phone widths.

## CR-082 - Drawer Scrollbar Header Footer Boundary Recheck

Planning status:

CR-082 is a focused frontend regression recheck raised after CR-081 when user
browser review clarified that every scrollable overlay's visible scrollbar must
stay between the fixed header and fixed footer, not merely keep footer buttons
outside the scroll body.

- [x] Record CR-082 as a regression fix linked to CR-081, CR-073, and Phase
      21 overlay freeze requirements.
- [x] Ensure all drawer/modal open paths call shared normalization through
      `openDrawerChrome(...)` before activation.
- [x] Keep `.drawer-scroll-body` as the content scroll owner and mark it with
      `data-scroll-owner="drawer-content"` for verification.
- [x] Keep fixed footer drawers marked with `has-fixed-footer`, with footer
      action groups as direct `.drawer-fixed-footer` children.
- [x] Preserve close buttons, backdrop/Escape/page-switch close behavior,
      enhanced select/date behavior, Run Detail tabs, Task Center,
      owner/report scope, top-bar refresh, and bottom action buttons.
- [x] Verify Mail Configuration, Monitoring task drawer, and Mail Template
      drawer browser geometry at desktop and phone widths: header/body/footer
      gaps are zero, footer buttons are outside `.drawer-scroll-body`, and
      document horizontal overflow is zero.

## CR-074 - Console Refresh Action Deduplication And Icon Loading

Planning status:

CR-074 is a verified frontend-only existing-feature optimization after
browser review found that many formal console pages still had duplicate
refresh actions: the shared top-bar current-page refresh plus a page-local
button that reloaded the same data. It keeps scoped refresh actions when they
operate on a drawer, preview, log, delivery history, schedule recomputation, or
run detail.

- [x] Record CR-074 as an existing-feature optimization without changing
      backend APIs, data model, permissions, crawler, AI, SMTP, reports,
      scheduler, or deployment behavior.
- [x] Keep one top-bar page-level refresh entry for the active first-level
      page.
- [x] Remove redundant page-header and filter-toolbar refresh buttons that
      merely duplicate the active page reload.
- [x] Render refresh actions as icon-only SVG buttons with accessible labels
      rather than visible Chinese refresh text.
- [x] Add loading/spinning state to refresh icons while their associated work
      is pending and restore the button after completion.
- [x] Preserve semantically scoped refresh actions for schedule recomputation,
      delivery history, email-template preview, run logs, and Run Detail.
- [x] Add static regression coverage for refresh-action deduplication,
      icon-only rendering, and loading-state hooks.
- [x] Verify targeted frontend tests, syntax checks, inline script parse, docs
      consistency, and browser behavior on representative pages.

## CR-086 - Explanatory Helper Copy Tooltip Consolidation

Planning status:

CR-086 is a focused frontend-only visual-density optimization raised after
Phase 21P. It moves targeted explanatory helper copy out of always-visible
small text and into consistent question-mark tooltips while preserving the
original copy and all existing workflows.

- [x] Record CR-086 as an existing-feature optimization linked to Phase 21
      visual-density and overlay preservation rules.
- [x] Add static regression coverage that locks the helper-tooltip component,
      original tooltip copy, removed always-visible helper copy, and preserved
      Task Center / Run Detail / overlay structure.
- [x] Add a unified `?` helper tooltip affordance with hover, focus, and
      click/focus access.
- [x] Migrate the targeted account, proxy, AI, rule, mail-template, Task
      Center, and Monitoring helper copy into adjacent label/title tooltips.
- [x] Preserve operational state text, empty/error/loading feedback, status
      values, buttons, filters, row actions, downloads, refresh, save/test, and
      confirmation flows.
- [x] Verify targeted frontend tests, syntax checks, docs consistency, and
      browser behavior at representative desktop, tablet, and mobile widths.

## CR-087 - Explanatory Helper Tooltip Removal

Planning status:

CR-087 is a focused frontend-only visual-density follow-up to CR-086 after
acceptance review found that the `?` helper affordances still added noise. It
removes the helper-tooltip layer entirely and does not restore the removed
explanatory small text.

- [x] Record CR-087 as an existing-feature optimization linked to CR-086 and
      Phase 21 visual-density rules.
- [x] Add static regression coverage that forbids helper-tooltip markup, CSS,
      JavaScript helpers, `data-tooltip` content, and the removed explanatory
      copy returning as visible text.
- [x] Remove the `?` helper tooltip markup from formal console headers, labels,
      account cells, resource lists, Task Center, Monitoring, and representative
      overlays.
- [x] Remove the helper-tooltip click/keyboard/open/close JavaScript and
      helper-specific CSS.
- [x] Preserve operational state text, empty/error/loading feedback, status
      values, buttons, filters, row actions, downloads, refresh, save/test, and
      confirmation flows.
- [x] Verify targeted frontend tests, syntax checks, docs consistency, and
      browser behavior at representative desktop, tablet, and mobile widths,
      including the AI rule modal residual helper-text cleanup.

### Phase 21Q - AI Rule Modal Residual Helper Text Removal

- [x] Remove the `AI 状态` line, legacy-prompt notice, and default empty
      result hint from the `AI 评估规则` modal.
- [x] Preserve rule sections, sample inputs, test action, save action, and
      rendered test output.
- [x] Verify the modal remains reachable and readable at desktop, tablet, and
      mobile widths without re-expanding the layout because of explanatory
      helper text.

### Phase 21N - System Diagnostics

- [x] Refine diagnostics into clearer summary, impact, next action, runtime
      state, scheduler state, platform state, and action-card hierarchy.
- [x] Preserve rerun diagnosis, run system diagnosis, process account
      resources, readiness/action cards, and customer-safe diagnostic wording.
- [x] Verify System Diagnostics at `1440x900`, `1024x768`, and `390x844`,
      including rerun diagnosis, run system diagnosis feedback, account-resource
      routing, readiness/actions, scheduler state, platform state, no console
      errors, no document horizontal overflow, and no one-character Chinese
      text columns.

### Phase 21O - Login Page

- [x] Refine login trust, focus, loading, and error states without changing the
      session/authentication flow.
- [x] Preserve email, password, login, error feedback, and route-to-Operations
      Home behavior after successful login.

### Phase 21P - Cross-Page Verification

- [x] Run static checks: `node --check api/webui/monitor/monitor.js`, inline
      script parse check for `api/monitor_web/index.html`, and
      `uv run python scripts/check_docs.py`.
- [x] Run targeted frontend regression tests covering CR-033, formal console
      pages, secondary overlays, loading feedback, and floating menus.
- [x] Run browser verification at `1440x900`, `1024x768`, and `390x844` for
      administrator and normal-user paths.
- [x] Stress-check card/grid layouts with long law-firm names, platform names,
      account labels, failure reasons, and status text across dashboard, runs,
      reports, resources, and secondary overlays; fail the batch if any module
      collapses text into one-character vertical columns or hides actions.
- [x] Record implementation verification in `docs/TEST_RESULTS.md` only after
      code changes are actually implemented and tested.
