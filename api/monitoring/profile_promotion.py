"""Crash-safe Cookie-to-Profile promotion for CR-112 Packet C.1."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import threading
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.browser_environment import (
    BrowserEnvironmentError,
    BrowserEnvironmentPlan,
    close_managed_browser_session,
    launch_managed_browser_context,
    managed_browser_processes,
    verify_managed_page,
)

from . import account_environment
from .account_environment import resolve_account_profile_path
from .browser_environment_provider import resolve_account_browser_environment
from .cookie_material import (
    COOKIE_LOGIN_HYDRATION_WAIT_MS,
    canonicalize_cookie_records,
    serialize_cookie_material,
    to_playwright_cookie_items,
)
from .mediacrawler_login import get_mediacrawler_login_capability


PROFILE_OPERATION_MARKER = ".mediacrawler-profile-operation.json"
PROFILE_OPERATION_ROOT_NAME = ".profile_ops"
PROFILE_LOCK_ROOT_NAME = ".profile_locks"
PROMOTION_CLEANUP_DELAY = timedelta(hours=24)
PROMOTION_MIN_FREE_BYTES = 256 * 1024 * 1024


class ProfilePromotionError(RuntimeError):
    """A redacted promotion failure with a stable machine-readable reason."""

    def __init__(self, reason: str, promotion_id: int | None = None, *, recovery_required: bool = False) -> None:
        self.reason = reason
        self.promotion_id = promotion_id
        self.recovery_required = recovery_required
        super().__init__(reason)


@dataclass(frozen=True)
class ProfilePromotionPaths:
    active: Path
    operation_root: Path
    candidate: Path
    rollback: Path
    quarantine: Path
    marker_name: str = PROFILE_OPERATION_MARKER

    @property
    def candidate_marker(self) -> Path:
        return self.candidate / self.marker_name

    @property
    def active_marker(self) -> Path:
        return self.active / self.marker_name


BrowserRunner = Callable[
    [BrowserEnvironmentPlan, Sequence[Mapping[str, Any]] | None],
    Awaitable[dict[str, Any]],
]

_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


def profile_promotion_paths(
    *,
    account_id: int,
    profile_key: str,
    promotion_id: int,
) -> ProfilePromotionPaths:
    account_id = _positive_id(account_id, "account_id")
    promotion_id = _positive_id(promotion_id, "promotion_id")
    active = resolve_account_profile_path(profile_key)
    root = Path(account_environment.ACCOUNT_PROFILE_ROOT).resolve()
    operation_root = (root / PROFILE_OPERATION_ROOT_NAME / str(account_id) / str(promotion_id)).resolve()
    _assert_within(operation_root, root)
    return ProfilePromotionPaths(
        active=active,
        operation_root=operation_root,
        candidate=operation_root / "candidate",
        rollback=operation_root / "rollback",
        quarantine=operation_root / "quarantine",
    )


@contextmanager
def profile_operation_lock(account_id: int, profile_key: str, timeout: float = 20.0):
    """Hold an in-process and cross-process lock for one account Profile."""

    account_id = _positive_id(account_id, "account_id")
    root = Path(account_environment.ACCOUNT_PROFILE_ROOT).resolve()
    lock_root = root / PROFILE_LOCK_ROOT_NAME
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"{account_id}.lock"
    key = str(lock_path).lower()
    with _THREAD_LOCKS_GUARD:
        thread_lock = _THREAD_LOCKS.setdefault(key, threading.Lock())
    if not thread_lock.acquire(timeout=max(0.1, float(timeout))):
        raise ProfilePromotionError("profile_promotion_lock_timeout")
    handle = None
    acquired = False
    try:
        handle = lock_path.open("a+b")
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        _lock_file(handle, timeout)
        acquired = True
        _reject_active_run_lock(account_id)
        yield
    finally:
        if handle is not None:
            if acquired:
                _unlock_file(handle)
            handle.close()
        thread_lock.release()


@asynccontextmanager
async def async_profile_operation_lock(account_id: int, profile_key: str, timeout: float = 20.0):
    """Acquire the cross-process Profile lock without blocking the event loop."""

    manager = profile_operation_lock(account_id, profile_key, timeout)
    enter_task = asyncio.create_task(asyncio.to_thread(manager.__enter__))
    try:
        await asyncio.shield(enter_task)
    except asyncio.CancelledError:
        await enter_task
        await asyncio.to_thread(manager.__exit__, None, None, None)
        raise
    try:
        yield
    finally:
        await asyncio.to_thread(manager.__exit__, None, None, None)


async def promote_cookie_to_profile(
    account_id: int,
    cookie_records: Sequence[Mapping[str, Any]] | None,
    *,
    cookie_source: str,
    login_session_id: int | None = None,
    actor_id: int | None = None,
    acquisition_generation: int = 1,
    provider_plan: BrowserEnvironmentPlan | None = None,
    browser_runner: BrowserRunner | None = None,
    expected_platform_account_id: str = "",
) -> dict[str, Any]:
    """Validate Cookie material and promote a fresh candidate to the fixed path."""

    from .database import (
        create_account_profile_promotion,
        create_login_session,
        get_social_account,
        update_account_profile_promotion,
    )

    account_id = _positive_id(account_id, "account_id")
    account = get_social_account(account_id, masked=False)
    if not account:
        raise ProfilePromotionError("profile_promotion_account_missing")
    platform = str(account.get("platform") or "").strip().lower()
    records = (
        canonicalize_cookie_records(platform, cookie_records)
        if cookie_records is not None
        else None
    )
    serialized_material = serialize_cookie_material(platform, records) if records is not None else ""
    if login_session_id is None:
        session = create_login_session(
            {
                "platform": platform,
                "account_id": account_id,
                "profile_key": account.get("profile_key") or "",
                "cookie_source": cookie_source,
                "acquisition_generation": acquisition_generation,
                "message": "正在验证 Cookie 并初始化网页登录态。",
            }
        )
        login_session_id = int(session["id"])

    try:
        await asyncio.to_thread(recover_profile_promotions, account_id)
    except ValueError as exc:
        _mark_login_session_failed(login_session_id, str(exc))
        raise ProfilePromotionError(str(exc)) from exc
    await asyncio.to_thread(cleanup_profile_promotion_artifacts, account_id)
    await asyncio.to_thread(_reject_retained_promotion_artifacts, account_id)
    owned_playwright = None
    promotion: dict[str, Any] | None = None
    paths: ProfilePromotionPaths | None = None
    swapped = False
    had_active = False
    try:
        async with async_profile_operation_lock(account_id, str(account.get("profile_key") or "")):
            account = get_social_account(account_id, masked=False) or account
            active_path = resolve_account_profile_path(str(account.get("profile_key") or ""))
            had_active = _existing_active_profile(active_path)

            if provider_plan is None:
                from playwright.async_api import async_playwright

                owned_playwright = await async_playwright().start()
                provider_plan = _resolve_provider_plan(account, owned_playwright)
            else:
                _validate_provider_plan_binding(provider_plan, account, active_path)

            promotion = create_account_profile_promotion(
                account_id=account_id,
                login_session_id=login_session_id,
                cookie_source=cookie_source,
                acquisition_generation=acquisition_generation,
                had_active_profile=had_active,
                created_by=actor_id,
            )
            # The database-generated ID is the operation directory identity.
            paths = profile_promotion_paths(
                account_id=account_id,
                profile_key=str(account["profile_key"]),
                promotion_id=int(promotion["id"]),
            )
            _cleanup_stale_operation_root(paths.operation_root)
            _ensure_profile_storage_capacity(paths)
            _prepare_operation_paths(paths, promotion)
            _set_had_active_profile(int(promotion["id"]), had_active)

            runner = browser_runner
            if runner is None:
                runner = _default_browser_runner(platform, owned_playwright)

            candidate_plan = replace(
                provider_plan,
                action="login_check",
                trigger_source="cookie_profile_promotion",
                profile_mode="persistent",
                launch_mode="persistent_launch",
                profile_path=str(paths.candidate),
            )
            candidate_result = await runner(candidate_plan, records)
            _require_validation(candidate_result, "profile_candidate_validation_failed", int(promotion["id"]))
            _require_expected_platform_identity(
                candidate_result,
                expected_platform_account_id,
                "profile_candidate_identity_mismatch",
                int(promotion["id"]),
            )
            if records is None:
                acquired_records = candidate_result.get("cookie_records") if isinstance(candidate_result, Mapping) else None
                if not isinstance(acquired_records, Sequence) or isinstance(acquired_records, (str, bytes, bytearray)):
                    raise ProfilePromotionError("profile_cookie_capture_missing", int(promotion["id"]))
                records = canonicalize_cookie_records(platform, acquired_records)
                serialized_material = serialize_cookie_material(platform, records)
            update_account_profile_promotion(int(promotion["id"]), "candidate_ready", checkpoint="candidate_ready_at")

            update_account_profile_promotion(int(promotion["id"]), "swapping", checkpoint="swap_started_at")
            swapped = True
            if had_active:
                _rename_directory(paths.active, paths.rollback)
                update_account_profile_promotion(int(promotion["id"]), "swapping", checkpoint="active_moved_at")
            _rename_directory(paths.candidate, paths.active)
            update_account_profile_promotion(int(promotion["id"]), "swapping", checkpoint="candidate_moved_at")

            active_plan = replace(candidate_plan, profile_path=str(paths.active))
            active_result = await runner(active_plan, None)
            _require_validation(active_result, "profile_active_recheck_failed", int(promotion["id"]))
            _require_expected_platform_identity(
                active_result,
                expected_platform_account_id,
                "profile_active_identity_mismatch",
                int(promotion["id"]),
            )
            update_account_profile_promotion(int(promotion["id"]), "active_recheck", checkpoint="active_rechecked_at")

            from .database import commit_account_profile_promotion

            committed = commit_account_profile_promotion(
                int(promotion["id"]),
                serialized_cookie_material=serialized_material,
                provider_resolution_id=str(provider_plan.resolution_id),
                browser_attempt_id=str(provider_plan.attempt_id),
                runtime_snapshot_json=str(active_result.get("runtime_snapshot_json") or ""),
                identity=active_result.get("identity") if isinstance(active_result.get("identity"), dict) else {},
            )
            if not had_active:
                _remove_marker_if_owned(paths.active, promotion)
            else:
                _set_cleanup_after(int(promotion["id"]), datetime.now(timezone.utc) + PROMOTION_CLEANUP_DELAY)
            return {
                "ok": True,
                "promotion": committed,
                "account": get_social_account(account_id, masked=False) or {},
                "provider_resolution_id": str(provider_plan.resolution_id),
                "browser_attempt_id": str(provider_plan.attempt_id),
            }
    except ProfilePromotionError as exc:
        if promotion and paths and not _promotion_is_committed(int(promotion["id"])):
            _recover_failed_promotion(promotion, paths, swapped, exc.reason)
        if not promotion or not _promotion_is_committed(int(promotion["id"])):
            _mark_login_session_failed(login_session_id, exc.reason)
        raise
    except asyncio.CancelledError as exc:
        if promotion and paths:
            _recover_failed_promotion(promotion, paths, swapped, "cancelled")
        _mark_login_session_failed(login_session_id, "cancelled")
        raise ProfilePromotionError("profile_promotion_cancelled", int(promotion["id"]) if promotion else None) from exc
    except Exception as exc:
        if promotion and paths:
            reason = _promotion_exception_reason(exc)
            _recover_failed_promotion(promotion, paths, swapped, reason)
            _mark_login_session_failed(login_session_id, reason)
            if reason == "profile_active_recheck_failed":
                raise ProfilePromotionError(reason, int(promotion["id"])) from exc
            raise ProfilePromotionError("profile_promotion_failed", int(promotion["id"])) from exc
        _mark_login_session_failed(login_session_id, _promotion_exception_reason(exc))
        raise ProfilePromotionError(_promotion_exception_reason(exc)) from exc
    finally:
        if owned_playwright is not None:
            try:
                await owned_playwright.stop()
            except Exception:
                pass


def recover_profile_promotions(account_id: int | None = None) -> list[dict[str, Any]]:
    """Reconcile non-terminal journals before an account is used."""

    from .database import (
        get_account_profile_promotion,
        list_account_profile_promotions,
        update_account_profile_promotion,
    )

    rows = list_account_profile_promotions(account_id, include_terminal=False)
    results: list[dict[str, Any]] = []
    busy = False
    for row in rows:
        promotion_id = int(row["id"])
        try:
            paths = profile_promotion_paths(
                account_id=int(row["account_id"]),
                profile_key=str(row["profile_key"]),
                promotion_id=promotion_id,
            )
            with profile_operation_lock(int(row["account_id"]), str(row["profile_key"])):
                current = get_account_profile_promotion(promotion_id) or row
                if str(current.get("state") or "") in {
                    "committed",
                    "rolled_back",
                    "failed",
                    "recovery_required",
                }:
                    results.append({"promotion_id": promotion_id, "state": str(current["state"])})
                    continue
                result = _recover_one_promotion(current, paths)
                results.append({"promotion_id": promotion_id, **result})
        except ProfilePromotionError as exc:
            if exc.reason in {"profile_promotion_account_busy", "profile_promotion_lock_timeout"}:
                busy = True
                results.append({"promotion_id": promotion_id, "state": "busy", "reason": exc.reason})
                continue
            _mark_recovery_required(promotion_id, int(row["account_id"]), exc.reason)
            results.append({"promotion_id": promotion_id, "state": "recovery_required", "reason": exc.reason})
        except Exception:
            _mark_recovery_required(promotion_id, int(row["account_id"]), "filesystem_evidence_contradiction")
            results.append({"promotion_id": promotion_id, "state": "recovery_required", "reason": "filesystem_evidence_contradiction"})
    if busy:
        raise ValueError("profile_promotion_account_busy")
    return results


def cleanup_profile_promotion_artifacts(account_id: int | None = None) -> list[dict[str, Any]]:
    """Remove due rollback artifacts without ever deleting the fixed active path."""

    from .database import list_account_profile_promotions, update_account_profile_promotion

    now = datetime.now(timezone.utc)
    rows = list_account_profile_promotions(account_id, include_terminal=True)
    results: list[dict[str, Any]] = []
    for row in rows:
        if str(row.get("state")) != "committed" or not row.get("cleanup_after"):
            continue
        try:
            due = _parse_time(row["cleanup_after"])
            if due and due > now:
                continue
            paths = profile_promotion_paths(
                account_id=int(row["account_id"]),
                profile_key=str(row["profile_key"]),
                promotion_id=int(row["id"]),
            )
            with profile_operation_lock(int(row["account_id"]), str(row["profile_key"])):
                if paths.rollback.exists():
                    _remove_owned_tree(paths.rollback, row)
                if paths.candidate.exists():
                    _remove_owned_tree(paths.candidate, row)
                if paths.active.exists():
                    _remove_marker_if_owned(paths.active, row)
                update_account_profile_promotion(
                    int(row["id"]),
                    "committed",
                    checkpoint="finalized_at",
                    cleanup_after="",
                )
                from .database import get_conn, utc_now

                with get_conn() as conn:
                    conn.execute(
                        "UPDATE account_profile_promotions SET failure_category='', recovery_action='' WHERE id=?",
                        (int(row["id"]),),
                    )
                    conn.execute(
                        "UPDATE social_accounts SET last_error='', updated_at=? WHERE id=? AND last_error=?",
                        (utc_now(), int(row["account_id"]), "Profile 清理需要处理"),
                    )
                results.append({"promotion_id": int(row["id"]), "state": "committed", "cleaned": True})
        except ProfilePromotionError as exc:
            if exc.reason in {"profile_promotion_account_busy", "profile_promotion_lock_timeout"}:
                results.append(
                    {
                        "promotion_id": int(row["id"]),
                        "state": "committed",
                        "cleaned": False,
                        "deferred": True,
                        "reason": exc.reason,
                    }
                )
                continue
            try:
                update_account_profile_promotion(
                    int(row["id"]),
                    "committed",
                    failure_category="cleanup_failed",
                    recovery_action="operator_remediation_required",
                )
                from .database import get_conn, utc_now

                with get_conn() as conn:
                    conn.execute(
                        "UPDATE social_accounts SET last_error=?, updated_at=? WHERE id=?",
                        ("Profile 清理需要处理", utc_now(), int(row["account_id"])),
                    )
            except Exception:
                pass
            results.append({"promotion_id": int(row["id"]), "state": "committed", "cleaned": False})
        except Exception:
            try:
                update_account_profile_promotion(
                    int(row["id"]),
                    "committed",
                    failure_category="cleanup_failed",
                    recovery_action="operator_remediation_required",
                )
                from .database import get_conn, utc_now

                with get_conn() as conn:
                    conn.execute(
                        "UPDATE social_accounts SET last_error=?, updated_at=? WHERE id=?",
                        ("Profile 清理需要处理", utc_now(), int(row["account_id"])),
                    )
            except Exception:
                pass
            results.append({"promotion_id": int(row["id"]), "state": "committed", "cleaned": False})
    return results


def cleanup_after_successful_managed_run(account_id: int) -> list[dict[str, Any]]:
    """Make retained predecessor cleanup due after a successful crawl."""

    from .database import list_account_profile_promotions

    now = datetime.now(timezone.utc)
    for row in list_account_profile_promotions(account_id, include_terminal=True):
        if str(row.get("state")) != "committed" or not bool(row.get("had_active_profile")):
            continue
        paths = profile_promotion_paths(
            account_id=int(row["account_id"]),
            profile_key=str(row["profile_key"]),
            promotion_id=int(row["id"]),
        )
        if paths.rollback.exists() or paths.active_marker.exists():
            _set_cleanup_after(int(row["id"]), now)
    return cleanup_profile_promotion_artifacts(account_id)


def _default_browser_runner(platform: str, playwright: Any) -> BrowserRunner:
    async def run(plan: BrowserEnvironmentPlan, injected_records: Sequence[Mapping[str, Any]] | None) -> dict[str, Any]:
        if playwright is None:
            raise ProfilePromotionError("profile_promotion_browser_unavailable")
        session = await launch_managed_browser_context(playwright, plan)
        context = session.context
        owned_processes = managed_browser_processes(context)
        try:
            if os.name == "nt" and not owned_processes:
                raise ProfilePromotionError("profile_browser_process_ownership_unavailable")
            if injected_records is not None:
                await context.add_cookies(to_playwright_cookie_items(injected_records))
            page = context.pages[0] if getattr(context, "pages", None) else await context.new_page()
            page.set_default_timeout(15000)
            capability = get_mediacrawler_login_capability(platform)
            await page.goto(str(capability.get("login_url") or ""), wait_until="domcontentloaded", timeout=15000)
            provider_result = await verify_managed_page(context, page)
            if provider_result is None or not provider_result.ok:
                return {"ok": False, "reason": "account_identity_snapshot_mismatch"}
            await page.wait_for_timeout(COOKIE_LOGIN_HYDRATION_WAIT_MS)
            from .account_check import _extract_platform_identity, _login_baseline, _verify_collectable_login

            baseline = await _login_baseline(platform, context)
            verified = await _verify_collectable_login(platform, context, page, 15000, baseline)
            if not verified.get("ok"):
                return {"ok": False, "reason": "profile_login_invalid", "provider_result": provider_result}
            return {
                "ok": True,
                "provider_result": provider_result,
                "runtime_snapshot_json": json.dumps(provider_result.snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                "identity": await _extract_platform_identity(platform, page),
            }
        finally:
            await close_managed_browser_session(context, session.browser, owned_processes)

    return run


def default_profile_browser_runner(platform: str, playwright: Any) -> BrowserRunner:
    """Return the standard managed Profile validator for C.2 acquisition."""

    return _default_browser_runner(platform, playwright)


def _resolve_provider_plan(account: Mapping[str, Any], playwright: Any) -> BrowserEnvironmentPlan:
    proxy = None
    proxy_id = account.get("proxy_id")
    if proxy_id:
        from .database import get_proxy_profile

        proxy = get_proxy_profile(int(proxy_id), masked=False)
    return resolve_account_browser_environment(
        account,
        action="login_check",
        trigger_source="cookie_profile_promotion",
        headless=True,
        launch_mode="persistent_launch",
        proxy=proxy,
        playwright_executable_path=str(playwright.chromium.executable_path),
    )


def _validate_provider_plan_binding(plan: BrowserEnvironmentPlan, account: Mapping[str, Any], active: Path) -> None:
    if (
        int(plan.account_id) != int(account.get("id") or 0)
        or int(plan.workspace_id) != int(account.get("workspace_id") or 0)
        or str(plan.platform) != str(account.get("platform") or "")
        or str(plan.profile_key) != str(account.get("profile_key") or "")
        or Path(plan.profile_path).resolve() != active.resolve()
    ):
        raise ProfilePromotionError("profile_promotion_provider_mismatch")


def _prepare_operation_paths(paths: ProfilePromotionPaths, promotion: Mapping[str, Any]) -> None:
    root = Path(account_environment.ACCOUNT_PROFILE_ROOT).resolve()
    paths.operation_root.mkdir(parents=True, exist_ok=True)
    _assert_same_volume(paths.active.parent, paths.operation_root)
    if paths.candidate.exists() or paths.rollback.exists() or paths.quarantine.exists():
        raise ProfilePromotionError("profile_promotion_operation_artifact_exists", int(promotion["id"]))
    paths.candidate.mkdir(parents=True, exist_ok=False)
    _assert_within(paths.candidate, root)
    marker = {
        "promotion_id": int(promotion["id"]),
        "account_id": int(promotion["account_id"]),
        "profile_key_hash": _profile_key_hash(str(promotion["profile_key"])),
        "role": "candidate",
    }
    temporary = paths.candidate_marker.with_name(f"{paths.candidate_marker.name}.tmp")
    temporary.write_text(json.dumps(marker, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    os.replace(temporary, paths.candidate_marker)


def reset_candidate_profile_for_cookie_injection(paths: ProfilePromotionPaths, promotion: Mapping[str, Any]) -> None:
    """Remove browser storage acquired during login while retaining the journal marker."""

    if not paths.candidate.exists() or not paths.candidate.is_dir() or paths.candidate.is_symlink():
        raise ProfilePromotionError("profile_candidate_missing", int(promotion["id"]))
    if not _marker_matches(paths.candidate, promotion):
        raise ProfilePromotionError("profile_marker_mismatch", int(promotion["id"]), recovery_required=True)
    for child in paths.candidate.iterdir():
        if child.name == PROFILE_OPERATION_MARKER:
            continue
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)
        else:
            raise ProfilePromotionError("profile_artifact_invalid", int(promotion["id"]), recovery_required=True)


def _recover_failed_promotion(
    promotion: Mapping[str, Any],
    paths: ProfilePromotionPaths,
    swapped: bool,
    reason: str,
) -> None:
    from .database import update_account_profile_promotion

    promotion_id = int(promotion["id"])
    try:
        if swapped:
            update_account_profile_promotion(
                promotion_id,
                "rolling_back",
                failure_category=reason,
                recovery_action="restore_predecessor",
            )
            _restore_predecessor(paths, promotion)
            update_account_profile_promotion(
                promotion_id,
                "rolled_back",
                failure_category=reason,
                recovery_action="restored_predecessor",
            )
        else:
            _remove_owned_tree(paths.candidate, promotion)
            update_account_profile_promotion(
                promotion_id,
                "failed",
                failure_category=reason,
                recovery_action="candidate_removed",
            )
    except Exception as exc:
        _mark_recovery_required(promotion_id, int(promotion["account_id"]), "rollback_failed")
        raise ProfilePromotionError("profile_promotion_recovery_required", promotion_id, recovery_required=True) from exc


def _restore_predecessor(paths: ProfilePromotionPaths, promotion: Mapping[str, Any]) -> None:
    had_active = bool(promotion.get("had_active_profile"))
    active_exists = paths.active.exists()
    active_is_candidate = active_exists and _marker_matches(paths.active, promotion)
    rollback_exists = paths.rollback.exists()
    if had_active:
        if active_is_candidate:
            if not rollback_exists:
                raise ProfilePromotionError("rollback_predecessor_missing", int(promotion["id"]), recovery_required=True)
            _move_to_quarantine(paths.active, paths.quarantine)
            _rename_directory(paths.rollback, paths.active)
        elif active_exists:
            if rollback_exists:
                raise ProfilePromotionError("filesystem_evidence_contradiction", int(promotion["id"]), recovery_required=True)
        elif rollback_exists:
            _rename_directory(paths.rollback, paths.active)
        else:
            raise ProfilePromotionError("rollback_predecessor_missing", int(promotion["id"]), recovery_required=True)
    else:
        if rollback_exists:
            raise ProfilePromotionError("filesystem_evidence_contradiction", int(promotion["id"]), recovery_required=True)
        if active_exists:
            if not active_is_candidate:
                raise ProfilePromotionError("filesystem_evidence_contradiction", int(promotion["id"]), recovery_required=True)
            _move_to_quarantine(paths.active, paths.quarantine)
    _remove_owned_tree(paths.candidate, promotion)
    if paths.quarantine.exists():
        _remove_owned_tree(paths.quarantine, promotion)


def _recover_one_promotion(row: Mapping[str, Any], paths: ProfilePromotionPaths) -> dict[str, Any]:
    from .database import update_account_profile_promotion

    state = str(row.get("state") or "")
    if state in {"preparing", "candidate_ready"}:
        if paths.rollback.exists() or (paths.active.exists() and _marker_matches(paths.active, row)):
            raise ProfilePromotionError("filesystem_evidence_contradiction", int(row["id"]), recovery_required=True)
        if paths.candidate.exists():
            _remove_owned_tree(paths.candidate, row)
        update_account_profile_promotion(int(row["id"]), "failed", failure_category="restart_before_swap", recovery_action="candidate_removed")
        return {"state": "failed", "recovery_action": "candidate_removed"}

    if state in {"swapping", "active_recheck", "rolling_back"}:
        _restore_predecessor(paths, row)
        update_account_profile_promotion(int(row["id"]), "rolling_back" if state != "rolling_back" else state, recovery_action="restore_predecessor")
        update_account_profile_promotion(int(row["id"]), "rolled_back", recovery_action="restored_predecessor")
        return {"state": "rolled_back", "recovery_action": "restored_predecessor"}

    raise ProfilePromotionError("filesystem_evidence_contradiction", int(row["id"]), recovery_required=True)


def _mark_recovery_required(promotion_id: int, account_id: int, reason: str) -> None:
    from .database import update_account_profile_promotion

    try:
        update_account_profile_promotion(
            promotion_id,
            "recovery_required",
            failure_category=reason,
            recovery_action="operator_review_required",
        )
    finally:
        from .database import get_conn, utc_now

        with get_conn() as conn:
            conn.execute(
                "UPDATE social_accounts SET requires_relogin=1, identity_state='requires_relogin', status='limited', last_error=?, updated_at=? WHERE id=?",
                ("Profile 提升恢复需要处理", utc_now(), int(account_id)),
            )


def _set_had_active_profile(promotion_id: int, had_active: bool) -> None:
    from .database import get_conn

    with get_conn() as conn:
        conn.execute(
            "UPDATE account_profile_promotions SET had_active_profile=?, updated_at=? WHERE id=?",
            (1 if had_active else 0, _utc_now(), int(promotion_id)),
        )


def _set_cleanup_after(promotion_id: int, value: datetime) -> None:
    from .database import get_conn

    with get_conn() as conn:
        conn.execute(
            "UPDATE account_profile_promotions SET cleanup_after=?, updated_at=? WHERE id=?",
            (value.astimezone(timezone.utc).isoformat(), _utc_now(), int(promotion_id)),
        )


def _existing_active_profile(path: Path) -> bool:
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise ProfilePromotionError("profile_active_path_invalid")
    return path.is_dir()


def _rename_directory(source: Path, target: Path) -> None:
    if not source.exists() or not source.is_dir() or source.is_symlink():
        raise ProfilePromotionError("profile_directory_missing")
    if target.exists():
        raise ProfilePromotionError("profile_directory_target_exists")
    source.rename(target)


def _move_to_quarantine(source: Path, target: Path) -> None:
    if target.exists():
        raise ProfilePromotionError("profile_quarantine_exists", recovery_required=True)
    source.rename(target)


def _remove_owned_tree(path: Path, promotion: Mapping[str, Any]) -> None:
    if not path.exists():
        return
    if path.is_symlink() or not path.is_dir():
        raise ProfilePromotionError("profile_artifact_invalid", int(promotion["id"]), recovery_required=True)
    if path.name not in {"candidate", "rollback", "quarantine"}:
        raise ProfilePromotionError("profile_artifact_invalid", int(promotion["id"]), recovery_required=True)
    if path.name in {"candidate", "quarantine"} and not _marker_matches(path, promotion):
        raise ProfilePromotionError("profile_marker_mismatch", int(promotion["id"]), recovery_required=True)
    shutil.rmtree(path)


def _remove_marker_if_owned(path: Path, promotion: Mapping[str, Any]) -> None:
    marker = path / PROFILE_OPERATION_MARKER
    if not marker.exists():
        return
    if not _marker_matches(path, promotion):
        raise ProfilePromotionError("profile_marker_mismatch", int(promotion["id"]), recovery_required=True)
    marker.unlink()


def _marker_matches(path: Path, promotion: Mapping[str, Any]) -> bool:
    marker = path / PROFILE_OPERATION_MARKER
    if not marker.is_file() or marker.is_symlink():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False
    return payload == {
        "promotion_id": int(promotion["id"]),
        "account_id": int(promotion["account_id"]),
        "profile_key_hash": _profile_key_hash(str(promotion["profile_key"])),
        "role": "candidate",
    }


def _cleanup_stale_operation_root(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise ProfilePromotionError("profile_operation_root_invalid")
    path.parent.mkdir(parents=True, exist_ok=True)


def _ensure_profile_storage_capacity(paths: ProfilePromotionPaths) -> None:
    try:
        available = shutil.disk_usage(paths.operation_root.parent).free
    except OSError as exc:
        raise ProfilePromotionError("profile_storage_check_failed") from exc
    if available < PROMOTION_MIN_FREE_BYTES:
        raise ProfilePromotionError("profile_storage_insufficient")


def _assert_same_volume(first: Path, second: Path) -> None:
    first.mkdir(parents=True, exist_ok=True)
    second.mkdir(parents=True, exist_ok=True)
    if os.stat(first).st_dev != os.stat(second).st_dev:
        raise ProfilePromotionError("profile_operation_cross_volume")


def _assert_within(path: Path, root: Path) -> None:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ProfilePromotionError("profile_operation_path_invalid") from exc


def _require_validation(result: Any, reason: str, promotion_id: int) -> None:
    if not isinstance(result, Mapping) or result.get("ok") is not True:
        raise ProfilePromotionError(reason, promotion_id)


def _require_expected_platform_identity(
    result: Any,
    expected_platform_account_id: str,
    reason: str,
    promotion_id: int,
) -> None:
    expected = str(expected_platform_account_id or "").strip()
    if not expected:
        return
    identity = result.get("identity") if isinstance(result, Mapping) else None
    actual = str(identity.get("platform_account_id") or "").strip() if isinstance(identity, Mapping) else ""
    if not actual or actual != expected:
        raise ProfilePromotionError(reason, promotion_id)


def _promotion_exception_reason(exc: BaseException) -> str:
    if isinstance(exc, ProfilePromotionError):
        return exc.reason
    if isinstance(exc, BrowserEnvironmentError):
        return exc.reason
    text = str(exc).lower()
    if "recheck" in text or "invalid" in text:
        return "profile_active_recheck_failed"
    if "permission" in text or "access is denied" in text:
        return "profile_filesystem_permission"
    return "profile_promotion_failed"


def _promotion_is_committed(promotion_id: int) -> bool:
    from .database import get_account_profile_promotion

    row = get_account_profile_promotion(promotion_id)
    return bool(row and row.get("state") == "committed")


def _mark_login_session_failed(login_session_id: int | None, reason: str) -> None:
    if not login_session_id:
        return
    from .database import update_login_session_status

    try:
        update_login_session_status(
            int(login_session_id),
            "platform_error",
            f"Cookie 登录态初始化失败：{str(reason or 'profile_promotion_failed')[:96]}",
        )
    except Exception:
        pass


def _reject_retained_promotion_artifacts(account_id: int) -> None:
    from .database import list_account_profile_promotions

    for row in list_account_profile_promotions(account_id, include_terminal=True):
        if row.get("state") != "committed":
            continue
        paths = profile_promotion_paths(
            account_id=int(row["account_id"]),
            profile_key=str(row["profile_key"]),
            promotion_id=int(row["id"]),
        )
        if paths.rollback.exists() or paths.candidate.exists() or paths.quarantine.exists():
            raise ProfilePromotionError("profile_promotion_cleanup_pending", int(row["id"]))


def _positive_id(value: Any, field: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ProfilePromotionError("profile_promotion_id_invalid") from exc
    if parsed <= 0:
        raise ProfilePromotionError("profile_promotion_id_invalid")
    return parsed


def _profile_key_hash(profile_key: str) -> str:
    return hashlib.sha256(str(profile_key).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_time(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _reject_active_run_lock(account_id: int) -> None:
    from .database import get_conn

    with get_conn() as conn:
        row = conn.execute("SELECT locked_by_run_id FROM social_accounts WHERE id=?", (account_id,)).fetchone()
    if row and row["locked_by_run_id"]:
        raise ProfilePromotionError("profile_promotion_account_busy")


def _lock_file(handle: Any, timeout: float) -> None:
    deadline = time.monotonic() + max(0.1, float(timeout))
    if os.name == "nt":
        import msvcrt

        while True:
            try:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                if time.monotonic() >= deadline:
                    raise ProfilePromotionError("profile_promotion_lock_timeout")
                time.sleep(0.05)
    else:
        import fcntl

        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except OSError:
                if time.monotonic() >= deadline:
                    raise ProfilePromotionError("profile_promotion_lock_timeout")
                time.sleep(0.05)


def _unlock_file(handle: Any) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
    else:
        import fcntl

        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
