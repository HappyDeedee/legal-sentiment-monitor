# Phase 5.1P Browser Entrypoint And Provider Map

Status: verified read-only preflight
Owner: CR-047 / Phase 5.1P
Evidence baseline: clean `main@459237f`, matching `origin/main`, before this
documentation-only result was written
Review date: 2026-07-19
Current progress: Phase 5.1A-D and CR-114 are verified, merged, and rechecked
through `main@27389a8`. The separate Phase 5.1 server-like acceptance remains
operator-gated; CR-112 Packet B is verified and Packet C is next.

2026-07-21 status note: the table below preserves its 2026-07-19 baseline
classification. CR-112 Packet B is now `Accepted / Verified`, executes before
CR-070, and selected direct managed-context acquisition while reusing this
provider boundary; no CR-112 implementation is added to the historical Phase
5.1P packet.

## Result

Phase 5.1P passes as a mapping and contract gate. The preflight baseline
runtime did not yet satisfy CR-047 account identity fidelity, but every
browser, login, validation, monitor-run, child-process, CDP, and fallback path
was classified.
The formal monitor paths can consume one immutable
`BrowserEnvironmentProvider` plan and one requested/effective evidence result
without adding another account, Profile, proxy, or browser authority.

This preflight made no code, schema, UI, runtime-data, database, Profile,
Cookie, proxy, crawler, browser-process, or deployment change. Phase 5.1A-D
have since passed their technical implementation, independent-review,
integration, and post-merge gates. CR-114 is also merged and reverified. The
Phase 5.1 acceptance gate must now prove the behavior described here in a
container/server-like environment. All `Current state` columns below remain
historical `main@459237f` preflight evidence, not a description of current
`main@27389a8`.

The central current-state finding is split authority:

```text
monitor login/check code     -> independently selects browser and launch defaults
monitor runner               -> independently selects account/proxy and builds argv/env
MediaCrawler child/CDP       -> independently selects browser/context/fallback defaults
```

The target is:

```text
account + action
  -> BrowserEnvironmentProvider.resolve(...)
  -> one immutable plan
  -> caller-specific launch adapter
  -> one immutable requested/effective result
  -> validation, snapshot, and finalization
```

## Todo Baseline Classification

| Item | Classification | Evidence and treatment |
| --- | --- | --- |
| Phase 21 | historical/already completed | Merged and closed on current `main`; it is not reopened here. |
| Phase 5.1P | current, completed by this preflight | The packet and all mapping tasks are executed by this document. |
| Phase 5.1A | completed and verified | Its additive account identity data-model packet is implemented and independently reviewed. |
| Phase 5.1B | completed and verified | Exact deterministic generation, fail-closed validation, safe creation controls, redaction, and test tripwires are implemented. |
| Phase 5.1C-D | historical/already completed | Both units are merged and post-merge verified through `main@86e9d02`. |
| CR-114 | historical/already completed | Object-scoped Context/Page binding is merged and post-merge verified on `main@27389a8`. |
| Phase 5.1 acceptance | current/operator-gated | The atomic packet requires server-like requested/effective, proxy-effect, manual/scheduler/CLI, restart, and CDP proof. |
| CR-070 / Phase 5.2 | future, dependency-gated | Current accepted order places it after CR-112 Packet D; it later consumes only committed CR-112 account/Profile state. |
| CR-112 | historical 2026-07-19 classification was future/`Needs Confirmation`; current status is `Accepted / Verified (Packet B)` | Reuses the CR-047 provider contract. Packet B selected direct managed Playwright/CDP context acquisition; no CR-112 Profile-promotion/profile-only implementation is assigned to CR-047. |
| CR-092 and CR-094 | future, `Needs Confirmation` | Not Phase 5.1P prerequisites. |
| CR-093 | future, accepted boundary with pending implementation decisions | Its future route-exposure work owns public treatment of legacy `/api/crawler`; it does not block this map. |
| CR-037 and Users And Permissions page | deferred/future | Independent capability work. |
| Phase 7.1D and Phase 17.1D mutation work | operator-gated/historical | No mutation work is opened by this preflight. |

No stale or duplicate unchecked task was found that should supersede Phase
5.1P. The current branch and worktree contained no uncommitted implementation
that could partially satisfy this packet.

## Scope Terms

- **Formal monitor path** means `/api/monitor/...`, the monitor CLI, the
  internal scheduler, `api.monitoring.runner`, and their MediaCrawler child.
- **Legacy raw crawler path** means `/api/crawler/...` through
  `api.services.crawler_manager`. It has no monitor account identity input.
- **Launch-owned CDP** means the application starts a browser and then attaches
  to the CDP endpoint it owns.
- **Connect-existing CDP** means attaching to a browser started elsewhere.
- **Generic Profile** means a per-platform path under `browser_data` rather
  than the account path derived from `profile_key`.
- **Current fact** below describes `main@459237f`. **Target contract** describes
  work that Phase 5.1A-D must implement and later verify.

## Entrypoint Map: Runtime Inputs

Every row is also present in the lifecycle/evidence map that follows.

| ID | Entrypoint and caller | Executable source | Profile source | Proxy source | UA / locale / timezone / viewport source | Headless and owner |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | Web QR create/poll: `POST/GET /api/monitor/login-sessions` -> `_login_browser_command_for_payload` -> `start_qrcode_login_session_with_profile` | `BrowserLauncher.detect_browser_paths()[0]`; `MONITOR_BROWSER_EXECUTABLE` is not read | Command construction always starts with the generic `MONITOR_BROWSER_DATA_DIR/cdp_{platform}_user_data_dir`. It replaces that path with the stored `account.profile_path` only when that field is non-empty; it does not derive a path from `profile_key`. An account with an empty stored path therefore keeps the generic Profile | Active account proxy is passed as Playwright `proxy.server`, including when the Profile silently remains generic | Random `utils.get_user_agent()` per launch; fixed `1920x1080` viewport; locale, timezone, screen, scale, mobile, and touch use process/provider defaults | `MONITOR_LOGIN_QR_HEADLESS`; direct Playwright persistent context owned by `login_qrcode.py` |
| E2 | Visible local login: `/platform-status/{platform}/login-browser` -> `open_login_browser_with_command` | Same auto-detected first Chrome/Edge path as E1 | Same stored-`profile_path` conditional override and generic fallback as E1. `account_environment.account_profile_environment` exists but is not called by this route | Active account proxy becomes browser `--proxy-server`, even if the Profile stayed generic | Browser/process defaults; `--start-maximized`; no requested/effective probes | Always visible; OS subprocess owned by `login_browser.py`; development fallback only |
| E3 | Cookie account validation: `/social-accounts/{id}/check-login` -> `_check_cookie_account` | Auto-detected first Chrome/Edge path | No persistent Profile; `chromium.launch()` plus a new ephemeral context | None, even when the account has a proxy | Random `utils.get_user_agent()` and fixed `1920x1080`; all other fields default | Always headless; direct Playwright browser/context owned by `account_check.py` |
| E4 | Profile login-state/account check: same route -> `_check_profile_account` | Auto-detected first Chrome/Edge path | Account path derived from `profile_key`; missing path fails | None, even when the account has a proxy | Random `utils.get_user_agent()` and fixed `1920x1080`; all other fields default | Always headless; direct Playwright persistent context owned by `account_check.py` |
| E5 | Platform status diagnostic: `/api/monitor/platform-status` -> `list_platform_status` | No browser launch | First active account path, else generic platform path | Displays the selected account proxy metadata but does not prove use | Filesystem timestamps, prior run errors, login-window state, and global platform login config only | No browser; diagnostic-only readiness view |
| E6 | HTTP manual run: `/jobs/{id}/run` -> `launch_job(source="manual")` | No browser until E9-E12 | Account selection is deferred to `runner.run_platform` | Preflight permits current task-proxy priority | No environment resolution at route level | Background task owned by scheduler registry, then runner |
| E7 | Internal scheduler run: `tick` -> `launch_job(source="scheduler")` | Same as E6 | Same as E6 | Same as E6 | Same as E6 | Same scheduler task registry and runner as E6 |
| E8 | Monitor CLI manual/due: `api.monitoring.cli` -> `run_job` | Same as E6 | Same as E6 | Same as E6 | Same as E6 | Foreground CLI coroutine; converges directly on runner |
| E9 | Monitor runner child launch: `run_platform` -> `_run_crawler_attempt` -> `uv run python main.py` | Child resolves its browser later; parent does not pass the documented browser executable | Parent chooses active/bound account and exports `MONITOR_CDP_USER_DATA_DIR` plus platform-specific equivalent; no account produces no account Profile env | Current priority is task proxy, then account proxy. Parent exports HTTP(S)/ALL proxy env values, but does not prove browser egress | Parent passes no persisted identity values. It passes headless and CDP flags in argv; remaining values are rebuilt by the child | `MONITOR_CRAWLER_HEADLESS`; parent owns job/account/proxy locks and child process |
| E10 | Legacy raw crawler API: `/api/crawler/start` -> `CrawlerManager.start` -> `main.py` | Child defaults; no provider/account executable contract | No monitor account/Profile binding; CDP defaults or a generic Profile | Request has no monitor proxy binding; inherited process environment only | Raw request can pass login type, Cookie, and headless; no account identity | Request default is visible; one in-memory raw crawler process; diagnostic/legacy only |
| E11 | MediaCrawler bootstrap and platform `pong`-then-login: `main.py` -> platform `core.start` | Delegates to E12-E14 | Delegates to E12-E14 | `config.ENABLE_IP_PROXY` pool only; formal runner proxy env is not converted into this explicit Playwright/CDP proxy input | Douyin uses provider-default UA; Kuaishou, Bilibili, and Tieba choose random desktop UAs; Weibo chooses a random mobile UA; XHS and Zhihu use fixed Mac UAs; no path consumes CR-047 fields. Per-platform details follow the table | CLI `--headless` sets both Playwright and CDP headless flags |
| E12 | Launch-owned CDP: each monitor platform `launch_browser_with_cdp` -> `CDPBrowserManager.launch_and_connect` | `config.CUSTOM_BROWSER_PATH` if it names a file, else auto-detected Chrome/Edge/Chromium; the documented env variable is not read | `MONITOR_CDP_USER_DATA_DIR_{PLATFORM}`, then global equivalent, else generic `browser_data/cdp_{platform}_user_data_dir` | Browser process receives no `--proxy-server`; `_create_browser_context` only warns that a passed proxy may not work | Existing first CDP context is reused, so requested UA/viewport options for a new context are normally bypassed; locale/timezone/screen/device fields are absent | Formal runner passes connect-existing false and chosen headless value; CDP manager owns launched browser process |
| E13 | Connect-existing CDP: `CDP_CONNECT_EXISTING` -> `_connect_existing_browser` | No executable is selected or launched | External browser's unknown Profile/context; account Profile env is not authority | External browser's unknown network state | Existing context values are unknown; requested context options are bypassed when a context exists | External browser ownership; diagnostic fallback only |
| E14 | CDP-to-standard fallback: every platform `launch_browser_with_cdp` catches broadly and calls `launch_browser` | Douyin/XHS use Playwright Chromium defaults; Kuaishou/Bilibili/Weibo/Tieba/Zhihu request `channel="chrome"` | Generic `browser_data/{platform}_user_data_dir`; ignores account `MONITOR_CDP_USER_DATA_DIR` | Uses `playwright_proxy` from MediaCrawler's own proxy-pool path, normally `None` for monitor runs | Per-platform defaults; no provider result or probes | Keeps requested headless value; context is owned by the platform crawler |

The monitor's supported account platforms are Douyin, Kuaishou, and XHS.
`main.py` and the legacy raw API also expose Bilibili, Weibo, Tieba, and Zhihu.
The following inspection closes the packet's per-platform branch requirement;
the last four remain raw-crawler paths without monitor account binding and are
not CR-047 managed-account acceptance paths.

| Platform / factory key | `pong` and login class | Exposed login branches | CDP failure behavior | Standard-mode identity source |
| --- | --- | --- | --- | --- |
| Douyin / `dy` | `dy_client.pong(browser_context=...)` then `DouYinLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % dy>` when state saving is on; Playwright Chromium default executable and provider-default UA |
| Kuaishou / `ks` | `ks_client.pong()` then `KuaishouLogin` | `qrcode`, `phone`, `cookie`; the current phone handler is empty | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % ks>`; `channel="chrome"`; random desktop UA |
| XHS / `xhs` | `xhs_client.pong()` then `XiaoHongShuLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % xhs>`; Playwright Chromium default executable; fixed Mac Chrome UA |
| Bilibili / `bili` | `bili_client.pong()` then `BilibiliLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % bili>`; `channel="chrome"`; random desktop UA |
| Weibo / `wb` | `wb_client.pong()` then `WeiboLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % wb>`; `channel="chrome"`; random mobile UA |
| Tieba / `tieba` | `tieba_client.pong(browser_context=...)` then `BaiduTieBaLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % tieba>`; `channel="chrome"`; random desktop UA |
| Zhihu / `zhihu` | `zhihu_client.pong()` then `ZhiHuLogin` | `qrcode`, `phone`, `cookie` | Broad exception calls `launch_browser` | Generic `browser_data/<USER_DATA_DIR % zhihu>`; `channel="chrome"`; fixed Mac Chrome UA |

All seven CDP wrappers instantiate the shared `CDPBrowserManager`, pass their
caller-selected UA/proxy/headless values, catch a broad exception, and invoke
their platform `launch_browser`. When `SAVE_LOGIN_STATE` is false, those
standard launchers instead create an ephemeral context; neither mode consumes
the monitor account provider result.

## Entrypoint Map: Lifecycle And Evidence

| ID | Fallback behavior | Current validation | Current locks | Finalization | Requested/effective evidence |
| --- | --- | --- | --- | --- | --- |
| E1 | Before launch, empty `account.profile_path` silently retains the generic platform Profile. QR capture then falls through MediaCrawler adapter, shared QR utility, and DOM screenshot candidate; login-state polling falls through MediaCrawler check, selectors, Cookie rules, and local storage | QR success is followed by E4 account check in the route, which can then inspect a different account-derived Profile | In-memory QR sessions close another QR context using the same path; no persisted account/Profile lock | Context closes on success, expiry, deletion, or explicit close; login session and account status update in the route | No runtime snapshot; returned fields show only customer-safe session state |
| E2 | Empty `account.profile_path` silently retains the generic platform Profile; there is no browser-path fallback after auto-detection, and the visible path is itself a fallback from server QR | Operator closes the window and later invokes E4; window state is a JSON/PID record and may name only the generic Profile | No account/Profile database lock; one platform window record; runner blocks any open window for that platform | Browser process is operator-controlled; state is reconciled by PID checks and later account check | No probes; not acceptance evidence |
| E3 | No Profile fallback because no Profile is used | Inject Cookie into ephemeral context, call MediaCrawler login-state check and client `pong`, then update account status/identity summary | No account/Profile/proxy lock | Ephemeral context/browser closes; encrypted Cookie remains in `social_accounts`; validated state is not promoted into account Profile | No snapshot; browser, proxy, and environment equivalence are unproved |
| E4 | Missing account Profile returns `missing_profile`; legacy stored path only produces a re-login hint | MediaCrawler login-state check plus platform client `pong`; platform identity is sampled on success | No account/Profile/proxy lock | Persistent context closes; account check/status metadata updates | No snapshot; proxy and environment equivalence are unproved |
| E5 | Falls back from active account Profile to generic platform Profile and from account login mode to global platform login config | Filesystem existence/mtime and prior errors only; it is not a platform login check | None | Read-only response | No effective runtime evidence |
| E6 | Preflight may allow global/generic platform state when no account is bound | `build_job_preflight`; no provider validation | Job registry before runner; actual resource locks in E9 | Route returns queued status; E9 owns run result | No provider evidence at queue time |
| E7 | Same as E6 | Same preflight plus due-state checks | Same as E6/E9 | Skipped-run record or E9 result | No provider evidence at queue time |
| E8 | Same runner path as E6/E7 | Same preflight | Runner locks | Structured CLI result | No separate provider evidence |
| E9 | If no active account, an explicit task proxy alone or no binding can continue. Child CDP can later fall back to E14 | Account status and configuration checks only; no requested/effective identity validation | Job filesystem lock, global/platform semaphores, account lock, and proxy lock; all released in `finally` | Run status, logs, output ingestion, report, and email lifecycle are structured | Run summary records safe account/proxy labels, not browser effective values |
| E10 | Uses raw MediaCrawler defaults and may attach existing CDP or fall back to generic standard mode | No monitor preflight/account check | One in-memory raw process lock only | Status becomes idle; exit code is logged but no monitor run/account finalization occurs | None |
| E11 | All seven registered platform cores check API `pong`; failure constructs a QR/phone/Cookie login class according to `config.LOGIN_TYPE` | Platform-specific login class; no CR-047 validator | Inherits only parent process locks when a monitor-supported platform is launched by E9 | Unhandled errors escape `main`; login classes also contain bare `sys.exit()` paths | Browser info logs version/context count/port only; no requested/effective identity snapshot |
| E12 | Any exception in platform CDP wrapper silently invokes E14 | Socket/HTTP CDP readiness and connection only | CDP manager local process ownership; parent runner lock is external | Cleanup closes context, connection, and launched process | `get_browser_info` returns version, context count, port, connected flag only |
| E13 | Waits for external port, then errors; platform wrapper may still invoke E14 | CDP connectivity only | No ownership of external browser/Profile | Cleanup skips external process close | External effective identity is unknown; cannot prove a locked identity |
| E14 | This is the broad fallback itself | No account identity revalidation after fallback | Parent runner lock may still be held, but the fallback Profile is not the locked account Profile | Platform context closes through main cleanup | No `fallback_used` snapshot; current logs are the only evidence |

## Browser Executable Trace

`MONITOR_BROWSER_EXECUTABLE` is documented in `SERVER_DEPLOYMENT.md` and
commented in `monitor.example.yaml`, but current product code has zero
consumers.

Current consumers and bypasses:

1. `login_browser.build_login_browser_command` uses
   `BrowserLauncher.detect_browser_paths()[0]`.
2. `account_check._browser_path` uses the same detector.
3. `CDPBrowserManager._get_browser_path` uses the hard-coded
   `config.CUSTOM_BROWSER_PATH` only when it names an existing file, then uses
   the detector. No CLI or environment adapter populates that config value.
4. Standard-mode Douyin/XHS use Playwright's browser selection; Kuaishou uses
   `channel="chrome"`.
5. Connect-existing CDP selects no executable.

The Dockerfile pins Playwright `1.45.0` and
`PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`, while `BrowserLauncher` searches
fixed system paths and does not search that Playwright root. Repository
evidence therefore does not prove that E1-E4 can select the bundled container
browser. `scripts/server_like_validation.py` launches Playwright Chromium
directly, but it does not launch a real QR/account-check path or a real monitor
crawl. Phase 5.1D must introduce one canonical resolver and the acceptance
gate must exercise it.

Target resolver rules:

- a non-empty explicit executable is authoritative; invalid, non-executable,
  or incompatible input fails closed and does not auto-fallback;
- server/container mode may resolve the pinned Playwright Chromium through the
  Playwright runtime and records source `playwright_bundled`;
- deployment-managed system Chrome/Edge/Chromium records an explicit source
  and version;
- local auto-detection records `diagnostic_auto_detect` and cannot prove a
  locked/active identity;
- every caller receives the same resolved path/family/version/source from the
  provider instead of running another detector.

## Cookie And Profile Trace

Current QR/visible Profile selection has its own split before the Cookie flow:

1. `_login_browser_command_for_payload` first creates a generic platform
   command and Profile directory.
2. It copies the stored `account.profile_path` and `profile_key` into that
   command only when `account.profile_path` is non-empty.
3. It never calls `account_profile_environment` or
   `resolve_account_profile_path`. An account with a valid `profile_key` but an
   empty stored path therefore opens the generic Profile, and can still receive
   the account proxy.
4. The later E4 Profile account check does use the account-environment
   resolver. QR/visible login and validation can consequently address different
   Profiles for the same account.

Current account Cookie flow is split across persistence, validation, and
crawl:

1. `save_social_account` encrypts a Cookie and derives the account Profile path
   from `profile_key`.
2. E3 validates the Cookie in a new ephemeral context without the account
   Profile or account proxy. Closing the context discards the injected browser
   state.
3. A later monitor run selects the account, passes its Profile through
   `MONITOR_CDP_USER_DATA_DIR*`, keeps `--lt cookie`, and puts the decrypted raw
   Cookie in child `--cookies` argv.
4. Launch-owned CDP uses the account Profile only while E12 succeeds. The
   platform client first calls `pong`; only a failed `pong` enters the Cookie
   login class and injects the argv Cookie into that context.
5. E14 changes the Profile to a generic per-platform directory. The parent
   account lock remains held even though the child is no longer using the
   account Profile.
6. Browser/context close can persist Cookie state only for whichever
   persistent Profile was actually opened. No current snapshot proves that it
   was the account Profile.
7. E10 can pass a raw Cookie to the child without any monitor account,
   `profile_key`, account lock, or provider result.

This is the exact current gap Phase 5.1D must expose and fail closed. CR-112,
not CR-047, owns staged Cookie-to-Profile promotion for an existing active
Profile, the future profile-only child cutover, and removal of raw Cookie argv.

## MediaCrawler Login And Exit Contract

Current child parsing exposes exactly `qrcode`, `phone`, and `cookie` through
`cmd_arg.LoginTypeEnum`. The formal monitor restricts customer account choices
to `qrcode` and `cookie`.

- Douyin and XHS implement all three branches.
- Kuaishou declares `qrcode` and `cookie` support, although its `begin` method
  still has a `phone` branch whose method is empty.
- All seven `main.py` platform cores create their API client, call `pong`, and
  construct a platform login class only when `pong` fails.
- `main.py` has no typed login-error mapping. Unhandled failures propagate
  through `tools.app_runner` to a generic process exit.
- Several QR/login failures call bare `sys.exit()`, whose default status is
  zero. The monitor runner treats return code zero as process success, so a
  login failure has no reliable typed exit contract today.
- The monitor runner maps non-zero exit codes generically and adds a login hint
  only by scanning log text. It has no reserved re-login status.

These facts name the adapter points for Phase 5.1D and the future CR-112
profile-only contract; they do not add a new login mode in this phase.

## BrowserEnvironmentProvider Contract

### Single Authority

The provider owns resolution of account, Profile, executable, proxy policy,
identity fields, headless setting, and launch mode. Callers own only their
business action: QR capture, login validation, account check, crawl lifecycle,
or platform-specific page/client behavior.

Resolution is two immutable values with one `resolution_id`:

1. `BrowserEnvironmentPlan`: created before any launch or CDP attach; it is the
   only launch authority.
2. `BrowserEnvironmentResult`: created after launch and probes; it contains the
   exact plan plus effective values and mismatch evidence. Callers cannot
   mutate either value or re-resolve individual fields.

Required logical shape:

```json
{
  "contract_version": 1,
  "resolution_id": "opaque",
  "action": "qr_login|cookie_validation|login_check|crawl",
  "account": {
    "workspace_id": 1,
    "account_id": 123,
    "platform": "dy",
    "identity_state": "validated"
  },
  "browser": {
    "executable_path": "internal-only",
    "family": "chromium",
    "version": "proved-at-launch",
    "source": "explicit|playwright_bundled|system_managed|diagnostic_auto_detect"
  },
  "profile": {
    "profile_key": "1/dy/acc_123",
    "derived_path": "internal-only",
    "mode": "persistent"
  },
  "proxy": {
    "policy": "account_bound|direct_for_unlocked_legacy|diagnostic",
    "proxy_id": 7,
    "region": "CN_MAINLAND",
    "launch_secret": "internal-only",
    "effect_proof": "pending|passed|failed"
  },
  "environment": {
    "browser_platform": "windows",
    "user_agent": "requested value",
    "timezone": "Asia/Shanghai",
    "locale": "zh-CN",
    "accept_language": "zh-CN,zh;q=0.9",
    "viewport": {"width": 1920, "height": 963},
    "screen": {"width": 1920, "height": 1080},
    "device_scale_factor": 1,
    "is_mobile": false,
    "has_touch": false
  },
  "launch": {
    "provider": "playwright_cdp",
    "mode": "persistent_launch|cdp_launch|diagnostic_cdp_attach",
    "headless": true
  },
  "requested": {},
  "effective": {},
  "probes": {},
  "unsupported_fields": [],
  "mismatch_evidence": [],
  "fallback_used": false
}
```

The in-memory plan may contain a proxy credential or raw path required for
launch. Persisted snapshots, logs, audit rows, API responses, and UI summaries
must replace them with safe IDs, source tags, hashes, regions, or booleans.
Cookies are not part of this provider result.

### Caller Adapters

| Current caller | Required adapter | Ownership |
| --- | --- | --- |
| `_login_browser_command_for_payload` and QR start | Replace the current stored-`profile_path` conditional override: resolve one plan from the account identity, never retain the initially built generic Profile for an account, launch from the exact executable/Profile/proxy/environment/headless fields, and probe before success | Phase 5.1C-D |
| Visible login | Consume the same plan with `mode=visible_dev`; record diagnostic source; never count it as server-like proof | Phase 5.1D |
| Cookie validation | For CR-047, consume the same account/environment plan and never use random/process defaults. Existing-active-Profile staged promotion remains outside this adapter | Phase 5.1D for environment binding; CR-112 C.1 for promotion |
| Profile account check | Launch/probe through the same plan, including the account proxy; do not run another browser detector | Phase 5.1D |
| HTTP manual, scheduler, and monitor CLI | Converge before provider resolution and pass the same trigger source into audit/snapshot metadata | Existing runner plus Phase 5.1D |
| `runner.run_platform` | Acquire locks first, resolve once, reject locked task proxy override, and hand the exact plan to the child adapter | Phase 5.1C-D |
| MediaCrawler platform cores | Consume provider-owned launch/context input; do not select another browser, Profile, proxy, or identity field | Phase 5.1D |
| `CDPBrowserManager` | Accept a plan; remove config/env re-resolution; apply identity settings before first navigation; return effective probes | Phase 5.1D |
| CDP standard fallback | For a locked identity, remove silent fallback and return a typed provider failure. Legacy unlocked use may be explicitly diagnostic with `fallback_used=true` and cannot activate/lock an identity | Phase 5.1D |
| Connect-existing CDP | Keep diagnostic-only and reject locked/active identity proof | Phase 5.1D |
| Legacy `/api/crawler` | Keep outside managed-account authority. It cannot accept or claim a locked account identity until a later accepted route/provider change adds an account-bound adapter | CR-093/future; not a Phase 5.1 blocker |

## Field Support And Proof

Classification meanings:

- `required/provable`: a locked identity must request and observe it.
- `supported/not-provable`: it may be configured, but current evidence is not
  sufficient to call a locked identity active.
- `unsupported/not-managed`: V1 records the limit and makes no fidelity claim.
- `diagnostic-only`: the path or value cannot contribute to acceptance.

| Field or surface | V1 classification | Current state | Required proof and failure rule |
| --- | --- | --- | --- |
| `profile_key` and derived Profile | required/provable | Resolver exists, but E1/E2 do not call it and can retain a generic path when stored `profile_path` is empty; E3/E13/E14 also split away from it | DB identity, safe resolver check, launch-owned path, and post-restart reuse; any generic/external Profile fails locked launch |
| Executable family/version/source | required/provable | Four different selection behaviors; documented env ignored | Canonical resolver plus launch version; invalid explicit source fails without fallback |
| Provider mode and headless | required/provable | Values are fragmented across env, CLI, and config | Provider metadata plus actual launch mode; diagnostic attach/visible modes cannot activate identity |
| Account proxy policy and effect | required/provable | QR/visible apply proxy, account checks omit it, CDP browser does not apply it, and HTTP client use is at best implicit | Exact account binding plus browser egress/region proof; hidden task override, unproved egress, or default network fails |
| User agent | required/provable | Random, default, or hard-coded by caller/platform | `navigator.userAgent` and request-header probe must match requested value |
| Timezone | required/provable | Process default | `Intl.DateTimeFormat().resolvedOptions().timeZone` must match |
| Locale and accept-language | required/provable | Process default except hard-coded request headers in XHS client | `navigator.language`, normalized `navigator.languages`, and captured `Accept-Language` header must match the requested semantics |
| Viewport | required/provable | Several paths request `1920x1080`; CDP existing-context reuse can ignore it | `window.innerWidth/innerHeight` must match |
| Screen | required/provable | Not set | `window.screen.width/height` must match |
| Device scale factor | required/provable | Not set | `window.devicePixelRatio` must match |
| Mobile/touch flags | required/provable | Not set | Requested emulation, UA/device consistency, `navigator.maxTouchPoints`, and relevant viewport/media probes must agree |
| `browser_platform` | required/provable as template-family metadata | Stored target only; no current provider input | Validate template, UA, device class, and provider host metadata. Per `ACCOUNT_ENVIRONMENT.md`, this is a template family, not a claim to stealth-spoof the host OS |
| `fingerprint_seed` | generator metadata, not a proved browser surface | Not implemented | Persist and audit generator input/version only; do not claim runtime effect |
| `navigator.webdriver` | diagnostic-only | Current stealth behavior varies by path | Record probe for diagnosis; it is not a locked-field acceptance value |
| Canvas, WebGL, fonts, plugins, extensions, long history, noVNC, provider fingerprint internals | unsupported/not-managed | Partially affected by browser/profile/stealth defaults but not centrally controlled | List in `unsupported_fields`; never call them managed or use them to pass acceptance |
| Local Chrome/Edge auto-detection, visible login, connect-existing CDP | diagnostic-only | Active fallbacks | May aid development; cannot prove locked/active identity |

The pinned local Playwright `1.45.0` API exposes persistent-context inputs for
proxy, user agent, locale, timezone, viewport, screen, device scale factor,
mobile, touch, headers, executable, and headless mode. CDP compatibility still
depends on applying those values before first navigation and proving the
effective result; merely passing a value into a helper is not proof.

## Fail-Closed Matrix

| Condition | Required behavior for a locked identity |
| --- | --- |
| Explicit executable is missing, invalid, not executable, or incompatible | Return `account_identity_provider_unsupported`; do not auto-detect another browser |
| Provider receives missing/empty required identity input | Return `account_identity_missing`; do not fill from config, process, browser, or Playwright defaults |
| Requested/effective probe mismatch | Return `account_identity_snapshot_mismatch`; retain mismatch evidence and do not mark active |
| Required field is unsupported or cannot be probed | Return `account_identity_provider_unsupported`; optional not-managed fields alone may remain in `unsupported_fields` |
| Task proxy differs from locked account proxy | Reject before launch with `account_identity_locked_proxy_override` |
| Proxy effect is absent or unproved | Fail before active/locked acceptance; default network is not a fallback |
| Account `profile_key` is missing/invalid, or its resolved Profile is generic, shared, or outside the resolved root | Return `account_identity_requires_relogin` or provider mismatch; never retain the E1/E2 generic command path or use E14 |
| CDP launch/reconnect fails | Return a typed provider failure; do not invoke standard generic Profile fallback |
| Connect-existing or local auto-detection is requested for acceptance | Mark diagnostic-only and reject locked/active proof |
| Caller attempts a second browser/Profile/proxy resolution | Treat as contract violation; provider plan remains the sole authority |
| Snapshot would contain Cookie, proxy credential, raw path, CDP URL, or noVNC token | Reject persistence and write only a redacted safe result |

## CR-112 Profile-Only Adapter Boundary

CR-112 C.3 remains dependency-gated. The following exact future adapter is
recorded in accepted planning artifacts and remains mapped here without
implementation or ownership transfer:

1. Current `_build_crawler_cmd` keeps `--lt cookie` and raw `--cookies` for
   managed Cookie accounts.
2. Future CR-112 C.3 keeps `--lt cookie`, adds hidden
   `--monitor_profile_only true`, and omits `--cookies`.
3. `_build_crawler_env` passes the exact Phase 5.1 provider Profile/browser/
   proxy result plus account ID, `profile_key`, promotion ID, and
   `profile_runtime_version`, with no Cookie value.
4. `cmd_arg/arg.py` accepts the hidden flag only with `--lt cookie`, rejects
   explicit Cookie input, clears default/process `config.COOKIES`, and rejects
   inconsistent provider/account metadata before `CrawlerFactory` creates a
   crawler.
5. Each monitor platform checks the prepared Profile before constructing any
   QR, Cookie, or phone login class. Failure raises `ProfileLoginRequired`.
6. `main.py` maps only `ProfileLoginRequired` to exit code `42`.
7. `runner.py` maps only exit code `42` to a redacted typed
   `requires_relogin` account/run result; generic failures keep generic
   handling.
8. Missing Profile, provider/CDP mismatch, E14 fallback, default network,
   empty Cookie injection, or unexpected QR opening fails before crawl.
9. Existing QR/Profile child execution stays separate and regression-protected
   unless a later decision changes it.

CR-047 owns the provider result reused by this future contract. CR-112 owns
Profile promotion/journaling, `profile_runtime_version`, the hidden child mode,
Cookie-protocol changes, exit `42`, migration/cutover, and raw-Cookie argv
retirement.

## Server-Like Acceptance Boundary

Phase 5.1 development and acceptance use a container/server-like launch-owned
browser. The acceptance run must exercise, not merely inspect:

1. canonical executable resolution inside the pinned container/runtime;
2. account-bound persistent Profile across service/browser restart;
3. QR launch and post-login account check through the same provider plan;
4. Cookie validation through the same environment plan, while any existing
   active-Profile promotion remains under its owning CR;
5. HTTP manual, scheduler, and monitor CLI runs through the same runner plan;
6. MediaCrawler launch-owned CDP using the same Profile and identity inputs;
7. requested/effective JS and request-header probes;
8. account proxy egress proof or a fail-closed result;
9. `fallback_used=false` and no generic Profile/default network;
10. safe snapshots with no secrets or raw paths.

Local visible login, auto-detected local Chrome/Edge, connect-existing CDP,
raw `/api/crawler`, and the existing lightweight server-like script are useful
diagnostics but cannot individually satisfy this acceptance.

## Phase 5.1 Handoff

Phase 5.1A-D required no additional provider-authority decision under these
boundaries and are now implemented, merged, and independently verified:

1. **5.1A:** add only the accepted additive identity/snapshot fields and keep
   existing accounts readable without guessed backfill.
2. **5.1B:** generate and validate the immutable requested environment; treat
   empty/process-default values as invalid for locked identities.
3. **5.1C:** add login/profile locking, state transitions, reset/re-login, and
   audit ownership before provider launch.
4. **5.1D:** implement the provider plan/result, canonical executable resolver,
   caller adapters, child handoff, probes, snapshot, proxy proof, and removal
   of silent E14 fallback for locked identities.
5. **CR-114:** integrate and post-merge verify object-scoped Context/Page
   binding so numeric object-ID reuse cannot mix plans or skip preparation.
6. **Acceptance:** run the server-like matrix above before calling any locked
   identity active or starting CR-070.

Stop Phase 5.1 and record `Needs Confirmation` if implementation discovers
that a formal monitor caller needs a second authority, a required effective
value cannot be probed, or proxy effect cannot be proved. Do not solve those
conditions by re-enabling process defaults, generic Profiles, default network,
local auto-detection, connect-existing CDP, or raw crawler routes.

## Evidence Index

Primary current-code evidence:

- `api/routers/monitor.py`: QR, visible login, account check, and manual-run
  routes plus account Profile/proxy command adaptation.
- `api/monitoring/login_browser.py`: visible browser detection and launch.
- `api/monitoring/login_qrcode.py`: server QR persistent context and polling.
- `api/monitoring/account_check.py`: ephemeral Cookie validation and persistent
  Profile account check.
- `api/monitoring/account_environment.py` and
  `api/monitoring/database.py`: `profile_key`, path derivation, encrypted
  Cookie, account state, and locks.
- `api/monitoring/scheduler.py` and `api/monitoring/cli.py`: scheduler, HTTP
  manual, and CLI convergence.
- `api/monitoring/runner.py`: account/proxy selection, locks, child argv/env,
  exit/log mapping, and finalization.
- `api/services/crawler_manager.py` and `api/routers/crawler.py`: legacy raw
  crawler bypass.
- `cmd_arg/arg.py`, `main.py`, and `tools/app_runner.py`: child defaults and
  error/exit behavior.
- `media_platform/douyin`, `media_platform/kuaishou`, and
  `media_platform/xhs`: `pong`-then-login and CDP-to-standard fallback.
- `tools/browser_launcher.py` and `tools/cdp_browser.py`: executable, Profile,
  CDP launch/attach, context reuse, proxy warning, and cleanup.
- `Dockerfile`, `docker-compose.yml`, and
  `scripts/server_like_validation.py`: current server-like packaging and proof
  boundary.

No live browser, platform account, Cookie, proxy, Profile, database, crawler,
or deployment state was opened or changed to produce this map.
