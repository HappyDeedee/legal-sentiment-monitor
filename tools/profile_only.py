from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Sequence

from tools.browser_environment import (
    BrowserEnvironmentError,
    BrowserEnvironmentPlan,
    plan_from_environment,
)


PROFILE_LOGIN_REQUIRED_EXIT_CODE = 42
PROFILE_ONLY_FLAG = "MONITOR_PROFILE_ONLY"
PROFILE_ONLY_ACCOUNT_ID_ENV = "MONITOR_PROFILE_ONLY_ACCOUNT_ID"
PROFILE_ONLY_PROFILE_KEY_ENV = "MONITOR_PROFILE_ONLY_PROFILE_KEY"
PROFILE_ONLY_PROMOTION_ID_ENV = "MONITOR_PROFILE_ONLY_PROMOTION_ID"
PROFILE_ONLY_RUNTIME_VERSION_ENV = "MONITOR_PROFILE_ONLY_RUNTIME_VERSION"


class ProfileLoginRequired(RuntimeError):
    def __init__(self, reason: str = "requires_relogin") -> None:
        self.reason = str(reason or "requires_relogin")
        super().__init__(self.reason)


@dataclass(frozen=True)
class ProfileOnlyMetadata:
    account_id: int
    profile_key: str
    promotion_id: int
    runtime_version: int


def validate_profile_only_cli(
    enabled: bool,
    login_type: str,
    _cookie_value: str,
    argv: Sequence[str],
) -> ProfileOnlyMetadata | None:
    if not enabled:
        return None
    if str(login_type or "") != "cookie":
        raise ValueError("profile_only_requires_cookie_login")
    if any(
        arg == "--cookies" or str(arg).startswith("--cookies=")
        for arg in argv
    ):
        raise ValueError("profile_only_cookie_forbidden")
    return profile_only_metadata()


def profile_only_metadata(plan: BrowserEnvironmentPlan | None = None) -> ProfileOnlyMetadata:
    managed_plan = plan or plan_from_environment(required=True)
    if managed_plan is None:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "profile_only")
    account_id = _positive_int_env(PROFILE_ONLY_ACCOUNT_ID_ENV)
    promotion_id = _positive_int_env(PROFILE_ONLY_PROMOTION_ID_ENV)
    runtime_version = _positive_int_env(PROFILE_ONLY_RUNTIME_VERSION_ENV)
    profile_key = str(os.environ.get(PROFILE_ONLY_PROFILE_KEY_ENV) or "").strip()
    if (
        account_id != managed_plan.account_id
        or profile_key != managed_plan.profile_key
        or runtime_version < 1
        or managed_plan.action != "crawl"
        or managed_plan.profile_mode != "persistent"
        or managed_plan.launch_mode != "cdp_launch"
    ):
        raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "profile_only")
    metadata = ProfileOnlyMetadata(
        account_id=account_id,
        profile_key=profile_key,
        promotion_id=promotion_id,
        runtime_version=runtime_version,
    )
    if not _profile_only_persistence_matches(metadata, managed_plan):
        raise BrowserEnvironmentError("account_identity_snapshot_mismatch", "profile_only")
    return metadata


def should_begin_platform_login(
    logged_in: bool,
    plan: BrowserEnvironmentPlan | None,
) -> bool:
    import config

    if not bool(getattr(config, "MONITOR_PROFILE_ONLY", False)):
        return not bool(logged_in)
    profile_only_metadata(plan)
    if not logged_in:
        raise ProfileLoginRequired()
    return False


def _positive_int_env(name: str) -> int:
    try:
        value = int(os.environ.get(name) or 0)
    except (TypeError, ValueError) as exc:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "profile_only") from exc
    if value <= 0:
        raise BrowserEnvironmentError("account_identity_provider_unsupported", "profile_only")
    return value


def _profile_only_persistence_matches(
    metadata: ProfileOnlyMetadata,
    plan: BrowserEnvironmentPlan,
) -> bool:
    from api.monitoring.account_environment import resolve_account_profile_path
    from api.monitoring.browser_selection import require_persisted_browser_selection
    from api.monitoring.database import (
        PROFILE_PROMOTION_NONTERMINAL_STATES,
        get_account_profile_promotion,
        get_proxy_profile,
        get_social_account,
        list_account_profile_promotions,
    )
    from api.monitoring.browser_environment_provider import resolve_account_browser_environment

    account = get_social_account(metadata.account_id, masked=True)
    promotion = get_account_profile_promotion(metadata.promotion_id)
    promotions = list_account_profile_promotions(metadata.account_id, include_terminal=True)
    latest_committed = next(
        (row for row in promotions if str(row.get("state") or "") == "committed"),
        None,
    )
    base_matches = bool(
        account
        and promotion
        and latest_committed
        and int(latest_committed.get("id") or 0) == metadata.promotion_id
        and not any(
            str(row.get("state") or "") in PROFILE_PROMOTION_NONTERMINAL_STATES
            for row in promotions
        )
        and int(account.get("workspace_id") or 0) == plan.workspace_id
        and str(account.get("platform") or "") == plan.platform
        and str(account.get("login_type") or "") == "cookie"
        and str(account.get("profile_key") or "") == metadata.profile_key
        and int(account.get("profile_runtime_version") or 0) == metadata.runtime_version
        and not bool(account.get("requires_relogin"))
        and str(account.get("status") or "") == "active"
        and int(promotion.get("account_id") or 0) == metadata.account_id
        and int(promotion.get("workspace_id") or 0) == plan.workspace_id
        and str(promotion.get("profile_key") or "") == metadata.profile_key
        and str(promotion.get("state") or "") == "committed"
    )
    if not base_matches:
        return False
    try:
        expected_profile_path = resolve_account_profile_path(metadata.profile_key)
        if Path(plan.profile_path).resolve() != expected_profile_path:
            return False
        browser_selection = require_persisted_browser_selection()
        if (
            Path(plan.browser_executable_path).resolve() != browser_selection.executable_path
            or plan.browser_source != browser_selection.source
        ):
            return False
        proxy = (
            get_proxy_profile(int(account["proxy_id"]), masked=False)
            if account.get("proxy_id")
            else None
        )
        expected_plan = resolve_account_browser_environment(
            account,
            action="crawl",
            trigger_source=plan.trigger_source,
            headless=os.environ.get("MONITOR_CRAWLER_HEADLESS", "true").lower()
            not in {"0", "false", "no"},
            launch_mode="cdp_launch",
            proxy=proxy,
            task_proxy_id=plan.proxy_id,
            playwright_executable_path=str(browser_selection.executable_path),
        )
    except Exception:
        return False
    ignored = {"resolution_id", "attempt_id"}
    return all(
        getattr(plan, field.name) == getattr(expected_plan, field.name)
        for field in fields(BrowserEnvironmentPlan)
        if field.name not in ignored
    )
