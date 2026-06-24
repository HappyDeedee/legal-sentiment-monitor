# Crawler Provider Architecture

This document is the planning source for CR-094. It records future crawler
engine provider architecture and does not implement provider abstraction.

## Status

Status: Needs Confirmation.

CR-094 is separate from Phase 5.1P. Phase 5.1P maps the current
MediaCrawler/CDP/BrowserEnvironmentProvider paths for CR-047 account identity
fidelity. CR-094 is a future extensibility lane for adding or evaluating other
crawler engines without creating parallel product systems.

## Goal

Keep the monitoring product modeled around tasks, platform accounts, proxies,
profiles, AI evaluation, reports, email delivery, Task Center, and Run Detail.
Crawler engines must plug into that product model through a provider contract.

Default model:

```text
Monitoring task / account / proxy / profile_key
-> scheduler and run orchestration
-> Crawler Engine Provider contract
-> MediaCrawlerProvider or future provider
-> normalized contents, logs, errors, reports, and Run Detail evidence
```

## Hard Boundaries

- Do not replace MediaCrawler through CR-094 planning.
- Do not implement a provider interface until a later accepted implementation
  CR.
- Do not add provider tables, profile-binding tables, capability tables, or
  schema fields without a separate data model and migration CR.
- Do not add a parallel task system, account system, profile system, report
  system, permission system, or frontend entry.
- Do not expose raw cookies, proxy credentials, local profile paths, CDP
  endpoints, command lines, provider secrets, or provider debug fields to
  normal users.
- Production providers cannot rely on an operator's local desktop browser.
- Provider-specific profile material must remain under controlled bindings and
  must not pollute the upper-layer account model.

## Provider Declaration

Each future provider must declare:

- provider id and name;
- supported platforms;
- supported login types;
- QR login and Cookie import support;
- login-state/account-check support;
- comment and secondary-comment support;
- time filter, max page, and max item support;
- proxy and account binding support;
- container/server-like support;
- output format version;
- error format version;
- capability limits and unsupported features.

## Task Input Contract

Provider input must be derived from existing monitoring task and run data,
including:

- workspace, task, and run identifiers;
- law firm, aliases, platforms, platform keywords, and exclude words;
- crawl range, comments, timeout, output directory, and run metadata;
- account binding, proxy binding, profile_key, and provider-specific runtime
  binding.

AI evaluation, reports, email delivery, Task Center, and Run Detail must not
depend on provider-private input fields.

## Output Contract

Provider output must normalize into the existing product content model:

- platform and source keyword;
- title, body/description, author, publish time, URL, cover/image URL;
- comments when collected;
- dedupe key and raw item id;
- collected time;
- provider id and run metadata;
- warning/error metadata;
- provider-specific extras in controlled extension fields.

Provider-private fields must not become required upper-layer fields without a
separate accepted CR.

## Error And Lifecycle Contract

Provider errors must normalize into customer-safe lifecycle states, including:

- provider unavailable;
- launch failed;
- login expired;
- account restricted;
- verification required;
- proxy failed;
- timeout;
- cancelled;
- interrupted;
- partial success;
- no result;
- output parse failed;
- unsupported capability;
- rate limited;
- platform changed;
- unknown provider error.

Run Detail should show normalized status and safe diagnostics. Provider raw
exceptions should remain administrator-only and redacted when exposed at all.

## Profile Identity And Binding

The upper layer continues to use `profile_key` as the business account
identity. A future provider may have provider-specific profile material such
as a local profile directory, remote profile id, cookie store, CDP context id,
or other provider-owned reference.

Rules:

- one upper-layer account keeps one `profile_key`;
- provider material binds to that identity through a controlled binding;
- provider material must be persistent or explicitly marked non-persistent;
- provider material cannot be shown to normal users;
- account/profile/proxy locks remain owned by the monitor system;
- providers cannot bypass those locks.

## Capability And Preflight

Before a run, the provider preflight must check:

- platform support;
- login type support;
- account status;
- profile binding;
- proxy support and policy;
- comment and time-filter capability;
- output format support;
- container/server-like availability;
- dependency availability;
- concurrency locks.

Unsupported required capabilities must fail closed or return an explicit
degraded state. Silent fallback to another provider is not allowed unless a
separate policy records the reason, logs, Run Detail evidence, and user-facing
state.

## Server-Like Admission

A provider may enter production only if it can be validated in a server-like
or container environment. The admission review must cover browser needs,
system dependencies, profile/login-state persistence, multi-account isolation,
proxy binding, timeout/cancel behavior, process cleanup, structured outputs,
redacted logs, and Run Detail evidence handoff.

Providers that require a local desktop browser or manual local command line are
development experiments only.

## Future Implementation Order

1. Complete CR-047 provider/effective snapshot behavior or explicitly account
   for its status.
2. Perform a read-only MediaCrawler call-chain audit.
3. Finalize provider contract, capability schema, profile binding, lifecycle,
   and redaction rules.
4. Record any required schema changes in a separate data model/migration CR.
5. Plan a MediaCrawlerProvider adapter without changing current runtime
   behavior.
6. Add tests from `TEST_PLAN.md` before implementation.
