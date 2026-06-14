from __future__ import annotations

import asyncio
import json
import os
import subprocess
import threading
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ai import evaluate_content
from .database import (
    create_run,
    finish_run,
    get_conn,
    get_job,
    get_platform_login_config,
    get_proxy_profile,
    get_social_account,
    list_social_accounts,
    update_run_summary,
    utc_now,
)
from .mailer import send_report
from .normalizer import (
    collect_platform_outputs,
    douyin_publish_time_type,
    in_time_window,
    normalize_comment,
    normalize_content,
)
from .platform_status import list_platform_status
from .reporting import create_report, update_report_email_status
from .security import MONITOR_DATA_DIR, redact_sensitive


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = MONITOR_DATA_DIR / "runs"
LOCKS_DIR = MONITOR_DATA_DIR / "locks"
GLOBAL_SEMAPHORE = asyncio.Semaphore(2)
PLATFORM_LOCKS: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
PLATFORM_DEBUG_PORTS = {"dy": 9223, "ks": 9224, "xhs": 9225}
JOB_LOCK_TTL_SECONDS = int(os.environ.get("MONITOR_JOB_LOCK_TTL_SECONDS") or 21600)
DEFAULT_CRAWLER_MAX_RETRIES = 1
DEFAULT_CRAWLER_RETRY_DELAY_SECONDS = 3.0
STOP_REQUESTS: set[int] = set()
RUN_PROCESSES: dict[int, set[subprocess.Popen]] = defaultdict(set)
PROCESS_LOCK = threading.Lock()


class CrawlerStopped(Exception):
    """Raised when an operator requests the current job to stop."""


def clear_stop_request(job_id: int) -> None:
    with PROCESS_LOCK:
        STOP_REQUESTS.discard(int(job_id))
        RUN_PROCESSES.pop(int(job_id), None)


def request_stop_job(job_id: int) -> int:
    job_id = int(job_id)
    with PROCESS_LOCK:
        STOP_REQUESTS.add(job_id)
        processes = list(RUN_PROCESSES.get(job_id, set()))
    stopped = 0
    for process in processes:
        if _terminate_process(process):
            stopped += 1
    return stopped


def is_stop_requested(job_id: int) -> bool:
    with PROCESS_LOCK:
        return int(job_id) in STOP_REQUESTS


async def run_job(job_id: int) -> dict[str, Any]:
    lock_path = _acquire_job_lock(job_id)
    if lock_path is None:
        return {"run_id": None, "status": "already_running", "summary": {"job_id": job_id}, "report": None}
    try:
        return await _run_job_locked(job_id)
    finally:
        _release_job_lock(lock_path)
        clear_stop_request(job_id)


async def _run_job_locked(job_id: int) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    summary: dict[str, Any] = {
        "job_id": job_id,
        "law_firm_name": job.get("law_firm_name") or "",
        "platforms": job.get("platforms", []),
        "keywords": job.get("keywords", []),
        "recipients": job.get("recipients", []),
        "raw_contents": 0,
        "filtered_contents": 0,
        "excluded_contents": 0,
        "new_contents": 0,
        "negative_count": 0,
        "high_count": 0,
        "pending_review_count": 0,
        "failed_platforms": [],
        "cancelled_platforms": [],
        "platform_results": {},
    }
    run_id = create_run(job_id, summary)
    run_dir = RUNS_DIR / f"job_{job_id}" / f"run_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary["run_dir"] = str(run_dir)
    update_run_summary(run_id, summary)
    try:
        _raise_if_stop_requested(job_id)
        tasks = [run_platform(job, run_id, platform, run_dir) for platform in job.get("platforms", [])]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        content_ids_for_eval: list[int] = []
        stopped = is_stop_requested(job_id)
        for platform, result in zip(job.get("platforms", []), results):
            if isinstance(result, CrawlerStopped):
                stopped = True
                summary["cancelled_platforms"].append(platform)
                summary["platform_results"][platform] = {"status": "cancelled", "error": redact_sensitive(str(result))}
                continue
            if isinstance(result, Exception):
                error = redact_sensitive(str(result))
                summary["failed_platforms"].append(platform)
                summary["platform_results"][platform] = {"status": "failed", "error": error}
                continue
            summary["platform_results"][platform] = result
            summary["raw_contents"] += result.get("raw_contents", 0)
            summary["filtered_contents"] += result.get("filtered_contents", 0)
            summary["excluded_contents"] += result.get("excluded_contents", 0)
            summary["new_contents"] += result.get("new_contents", 0)
            content_ids_for_eval.extend(result.get("content_db_ids", []))
        update_run_summary(run_id, summary)

        if stopped:
            summary["cancelled"] = True
            summary["duration_seconds"] = _run_duration_seconds(run_id)
            finish_run(run_id, "cancelled", summary, "任务已手动停止")
            _touch_job_last_run(job_id)
            return {"run_id": run_id, "status": "cancelled", "summary": summary, "report": None}

        _raise_if_stop_requested(job_id)
        eval_summary = await evaluate_new_contents(job, run_id, content_ids_for_eval)
        summary.update(eval_summary)
        _raise_if_stop_requested(job_id)
        report = create_report(run_id, job, summary)
        ok, error = send_report(job, report)
        error = redact_sensitive(error)
        update_report_email_status(report["id"], "sent" if ok else "failed", error)
        summary["email_status"] = "sent" if ok else "failed"
        if error:
            summary["email_error"] = error
        final_status = "partial_failed" if summary["failed_platforms"] else "success"
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        finish_run(run_id, final_status, summary)
        _touch_job_last_run(job_id)
        return {"run_id": run_id, "status": final_status, "summary": summary, "report": report}
    except CrawlerStopped as exc:
        summary["cancelled"] = True
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        finish_run(run_id, "cancelled", summary, redact_sensitive(str(exc)))
        _touch_job_last_run(job_id)
        return {"run_id": run_id, "status": "cancelled", "summary": summary, "report": None}
    except asyncio.CancelledError:
        request_stop_job(job_id)
        summary["cancelled"] = True
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        finish_run(run_id, "cancelled", summary, "任务已取消")
        _touch_job_last_run(job_id)
        raise
    except Exception as exc:
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        finish_run(run_id, "failed", summary, f"{type(exc).__name__}: {redact_sensitive(str(exc))}")
        _touch_job_last_run(job_id)
        raise


async def run_platform(job: dict[str, Any], run_id: int, platform: str, run_dir: Path) -> dict[str, Any]:
    _raise_if_stop_requested(job["id"])
    async with GLOBAL_SEMAPHORE:
        async with PLATFORM_LOCKS[platform]:
            _raise_if_stop_requested(job["id"])
            _ensure_login_window_closed(platform)
            platform_root = run_dir / platform
            platform_root.mkdir(parents=True, exist_ok=True)
            max_retries = _crawler_max_retries()
            total_attempts = max_retries + 1
            last_error = ""
            for attempt in range(1, total_attempts + 1):
                attempt_out = _attempt_output_dir(platform_root, attempt, total_attempts)
                attempt_out.mkdir(parents=True, exist_ok=True)
                try:
                    _raise_if_stop_requested(job["id"])
                    account_binding = _resolve_platform_account_binding(platform, job)
                    await asyncio.to_thread(_run_crawler_attempt, job, platform, attempt_out, account_binding)
                    _raise_if_stop_requested(job["id"])
                    contents, comments = collect_platform_outputs(attempt_out, platform)
                    result = ingest_outputs(job, run_id, platform, contents, comments)
                    result["attempts"] = attempt
                    result["max_retries"] = max_retries
                    if account_binding:
                        result["account"] = _account_summary(account_binding)
                    if account_binding and account_binding.get("proxy_id"):
                        result["proxy"] = _proxy_summary(account_binding)
                    return result
                except CrawlerStopped:
                    raise
                except RuntimeError as exc:
                    last_error = redact_sensitive(str(exc))
                    if not _should_retry_crawler_error(last_error) or attempt >= total_attempts:
                        break
                    _raise_if_stop_requested(job["id"])
                    await asyncio.sleep(_crawler_retry_delay_seconds())
            raise RuntimeError(f"MediaCrawler failed after {attempt} attempt(s): {last_error}")


def _run_crawler_attempt(
    job: dict[str, Any],
    platform: str,
    out_dir: Path,
    account_binding: dict[str, Any] | None = None,
) -> None:
    _raise_if_stop_requested(job["id"])
    cmd = _build_crawler_cmd(job, platform, out_dir, account_binding)
    env = _build_crawler_env(account_binding)
    log_path = out_dir / "crawler.log"
    timeout_seconds = int(os.environ.get("MONITOR_CRAWLER_TIMEOUT_SECONDS") or 900)
    process: subprocess.Popen | None = None
    try:
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        log_lines = [redact_sensitive("Starting crawler: " + " ".join(cmd))]
        if account_binding and account_binding.get("profile_path"):
            log_lines.append(
                "[monitor] Account profile enabled: "
                + redact_sensitive(f"{account_binding.get('account_name') or '-'} {account_binding.get('profile_path') or ''}")
            )
        if account_binding and account_binding.get("proxy_id"):
            log_lines.append(
                "[monitor] Proxy enabled: "
                + redact_sensitive(
                    f"{account_binding.get('proxy_name') or '-'} "
                    f"({account_binding.get('provider') or '-'}) "
                    f"{account_binding.get('proxy_url') or ''}"
                )
            )
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8", errors="ignore")
        with log_path.open("a", encoding="utf-8", errors="ignore") as log_file:
            process = subprocess.Popen(
                cmd,
                cwd=PROJECT_ROOT,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
            _register_process(job["id"], process)
            try:
                process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired as exc:
                _terminate_process(process)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
                log_file.write(f"\n[monitor] MediaCrawler timed out after {timeout_seconds}s\n")
                log_file.flush()
                raise RuntimeError(f"MediaCrawler timed out after {timeout_seconds}s; see {log_path}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"MediaCrawler timed out after {timeout_seconds}s; see {log_path}") from exc
    except RuntimeError:
        raise
    except Exception as exc:
        if isinstance(exc, CrawlerStopped):
            raise
        safe_error = redact_sensitive(f"{type(exc).__name__}: {exc}")
        log_path.write_text(safe_error, encoding="utf-8", errors="ignore")
        raise RuntimeError(f"MediaCrawler failed to start: {safe_error}; see {log_path}") from exc
    finally:
        if process:
            _unregister_process(job["id"], process)
    raw_log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    log_text = redact_sensitive(raw_log_text)
    if log_text != raw_log_text:
        log_path.write_text(log_text, encoding="utf-8", errors="ignore")
    if is_stop_requested(job["id"]):
        raise CrawlerStopped(f"任务已手动停止；see {log_path}")
    if process.returncode != 0:
        hint = "；检测到登录态失效，请先重新登录该平台账号" if _looks_like_login_required(log_text) else ""
        raise RuntimeError(f"MediaCrawler exited with {process.returncode}{hint}; see {log_path}")


def _ensure_login_window_closed(platform: str) -> None:
    statuses = {item["platform"]: item for item in list_platform_status()}
    status = statuses.get(platform) or {}
    if status.get("login_window_open"):
        label = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}.get(platform, platform)
        raise RuntimeError(f"{label}登录窗口未关闭，请关闭窗口后再运行采集")


def ingest_outputs(
    job: dict[str, Any],
    run_id: int,
    platform: str,
    contents: list[dict[str, Any]],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    normalized_contents = [c for c in (normalize_content(platform, item, job) for item in contents) if c]
    time_filtered_contents = [c for c in normalized_contents if in_time_window(c, job)]
    filtered_contents = [c for c in time_filtered_contents if not _matches_exclude_words(c, job)]
    normalized_comments = [c for c in (normalize_comment(platform, item) for item in comments) if c]
    content_db_ids: list[int] = []
    now = utc_now()
    with get_conn() as conn:
        for item in filtered_contents:
            existing = conn.execute(
                "SELECT id FROM raw_contents WHERE job_id=? AND platform=? AND content_id=?",
                (job["id"], item["platform"], item["content_id"]),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE raw_contents SET last_seen_at=? WHERE id=?",
                    (now, existing["id"]),
                )
                continue
            cur = conn.execute(
                """
                INSERT INTO raw_contents (
                    platform, content_id, job_id, run_id, law_firm_name, source_keyword, title,
                    description, author_name, content_url, cover_url, publish_time, comment_count,
                    raw_json, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["platform"],
                    item["content_id"],
                    job["id"],
                    run_id,
                    item["law_firm_name"],
                    item["source_keyword"],
                    item["title"],
                    item["description"],
                    item["author_name"],
                    item["content_url"],
                    item["cover_url"],
                    item["publish_time"],
                    item["comment_count"],
                    item["raw_json"],
                    now,
                    now,
                ),
            )
            content_db_ids.append(int(cur.lastrowid))
        for comment in normalized_comments:
            conn.execute(
                """
                INSERT OR IGNORE INTO raw_comments (
                    platform, comment_id, content_id, content, author_name, create_time, raw_json, first_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    comment["platform"],
                    comment["comment_id"],
                    comment["content_id"],
                    comment["content"],
                    comment["author_name"],
                    comment["create_time"],
                    comment["raw_json"],
                    now,
                ),
            )
    return {
        "status": "success",
        "raw_contents": len(normalized_contents),
        "filtered_contents": len(filtered_contents),
        "excluded_contents": len(time_filtered_contents) - len(filtered_contents),
        "new_contents": len(content_db_ids),
        "content_db_ids": content_db_ids,
    }


async def evaluate_new_contents(job: dict[str, Any], run_id: int, content_ids: list[int]) -> dict[str, Any]:
    negative_count = 0
    high_count = 0
    pending_review_count = 0
    with get_conn() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM raw_contents WHERE id IN (%s)" % ",".join("?" for _ in content_ids),
                content_ids,
            ).fetchall()
        ] if content_ids else []
    for row in rows:
        comments = _load_comments(row["platform"], row["content_id"])
        evaluation = await evaluate_content(job, row, comments)
        if evaluation["status"] == "pending_review":
            pending_review_count += 1
        is_related_negative = bool(evaluation["is_related"] and evaluation["is_negative"])
        if is_related_negative:
            negative_count += 1
        if is_related_negative and evaluation["risk_level"] == "high":
            high_count += 1
        _save_evaluation(row["id"], run_id, evaluation)
    return {"negative_count": negative_count, "high_count": high_count, "pending_review_count": pending_review_count}


def _save_evaluation(content_db_id: int, run_id: int, evaluation: dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO ai_evaluations (
                raw_content_id, run_id, status, is_related, is_negative, risk_level, reason,
                evidence_quotes, recommended_action, raw_response, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                content_db_id,
                run_id,
                evaluation["status"],
                1 if evaluation["is_related"] else 0,
                1 if evaluation["is_negative"] else 0,
                evaluation["risk_level"],
                evaluation["reason"],
                json.dumps(evaluation.get("evidence_quotes", []), ensure_ascii=False),
                evaluation["recommended_action"],
                redact_sensitive(evaluation.get("raw_response", "")),
                utc_now(),
            ),
        )


def _load_comments(platform: str, content_id: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM raw_comments WHERE platform=? AND content_id=? ORDER BY id LIMIT 20",
                (platform, content_id),
            ).fetchall()
        ]


def _build_crawler_cmd(
    job: dict[str, Any],
    platform: str,
    out_dir: Path,
    account_binding: dict[str, Any] | None = None,
) -> list[str]:
    headless = os.environ.get("MONITOR_CRAWLER_HEADLESS", "true").lower() not in {"0", "false", "no"}
    connect_existing = os.environ.get("MONITOR_CDP_CONNECT_EXISTING", "false").lower() in {"1", "true", "yes"}
    debug_port = os.environ.get(f"MONITOR_CDP_DEBUG_PORT_{platform.upper()}") or os.environ.get("MONITOR_CDP_DEBUG_PORT")
    debug_port = debug_port or str(PLATFORM_DEBUG_PORTS.get(platform, 9223))
    login_config = get_platform_login_config(platform, masked=False)
    login_type = (account_binding or {}).get("login_type") or login_config.get("login_type") or "qrcode"
    if login_type not in {"qrcode", "cookie"}:
        login_type = "qrcode"
    target_type = str(job.get("target_type") or "search")
    output_mode = str(job.get("output_mode") or "internal")
    save_option = "excel" if output_mode == "excel" else "json"
    max_items = _job_int(job, "max_items", 50)
    max_pages = _job_int(job, "max_pages", 1)
    start_page = _job_int(job, "start_page", 1)
    crawler_max_items = max(max_items, max_pages * 10)
    cmd = [
        "uv",
        "run",
        "python",
        "main.py",
        "--platform",
        platform,
        "--lt",
        login_type,
        "--type",
        target_type,
        "--save_data_option",
        save_option,
        "--start",
        str(start_page),
        "--keywords",
        ",".join(job.get("keywords", [])),
        "--get_comment",
        "true" if job.get("enable_comments") else "false",
        "--get_sub_comment",
        "true" if job.get("enable_sub_comments") else "false",
        "--headless",
        "true" if headless else "false",
        "--save_data_path",
        str(out_dir),
        "--max_concurrency_num",
        "1",
        "--crawler_max_notes_count",
        str(crawler_max_items),
    ]
    if target_type == "detail":
        cmd.extend(["--specified_id", ",".join(job.get("keywords", []))])
    if target_type == "creator":
        cmd.extend(["--creator_id", ",".join(job.get("keywords", []))])
    if login_type == "cookie":
        cookies = (account_binding or {}).get("cookies") or login_config.get("cookies") or ""
        if not cookies:
            raise ValueError(f"{platform} Cookie 登录未配置 Cookie")
        cmd.extend(["--cookies", cookies])
    if platform == "dy":
        cmd.extend(["--publish_time_type", str(douyin_publish_time_type(job))])
    if platform == "xhs":
        cmd.extend(["--sort_type", "time_descending"])
    cmd.extend(
        [
            "--cdp_connect_existing",
            "true" if connect_existing else "false",
            "--cdp_debug_port",
            str(debug_port),
        ]
    )
    return cmd


def _job_int(job: dict[str, Any], key: str, default: int) -> int:
    try:
        return max(1, int(job.get(key) or default))
    except (TypeError, ValueError):
        return default


def _build_crawler_env(account_binding: dict[str, Any] | None = None) -> dict[str, str]:
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    if not account_binding:
        return env
    profile_path = str(account_binding.get("profile_path") or "").strip()
    platform = str(account_binding.get("platform") or "").strip()
    if profile_path:
        env["MONITOR_CDP_USER_DATA_DIR"] = profile_path
        if platform:
            env[f"MONITOR_CDP_USER_DATA_DIR_{platform.upper()}"] = profile_path
        env["MONITOR_ACTIVE_ACCOUNT_ID"] = str(account_binding.get("account_id") or "")
        env["MONITOR_ACTIVE_ACCOUNT_NAME"] = str(account_binding.get("account_name") or "")
    proxy_url = str(account_binding.get("proxy_url") or "").strip()
    if proxy_url:
        env.update(
            {
                "HTTP_PROXY": proxy_url,
                "HTTPS_PROXY": proxy_url,
                "ALL_PROXY": proxy_url,
                "http_proxy": proxy_url,
                "https_proxy": proxy_url,
                "all_proxy": proxy_url,
                "MONITOR_ACTIVE_PROXY_ID": str(account_binding.get("proxy_id") or ""),
                "MONITOR_ACTIVE_PROXY_NAME": str(account_binding.get("proxy_name") or ""),
            }
        )
    return env


def _resolve_platform_account_binding(platform: str, job: dict[str, Any] | None = None) -> dict[str, Any] | None:
    job = job or {}
    explicit_account_id = _safe_int(job.get("account_id"))
    explicit_proxy_id = _safe_int(job.get("proxy_id"))
    accounts: list[dict[str, Any]] = []
    if explicit_account_id:
        account = get_social_account(explicit_account_id, masked=False)
        if account:
            accounts.append(account)
    else:
        accounts.extend(list_social_accounts(masked=False))
    for account in accounts:
        if account.get("is_draft"):
            continue
        if account.get("platform") != platform:
            continue
        if account.get("status") != "active":
            continue
        binding: dict[str, Any] = {
            "account_id": account.get("id"),
            "account_name": account.get("name") or "",
            "platform": platform,
            "login_type": account.get("login_type") or "qrcode",
            "cookies": account.get("cookies") or "",
            "profile_path": account.get("profile_path") or "",
        }
        proxy_id = explicit_proxy_id or account.get("proxy_id")
        if proxy_id:
            proxy = get_proxy_profile(int(proxy_id), masked=False)
            if proxy and proxy.get("status") == "active" and proxy.get("proxy_url"):
                binding.update(
                    {
                        "proxy_id": proxy.get("id"),
                        "proxy_name": proxy.get("name") or "",
                        "provider": proxy.get("provider") or "",
                        "proxy_url": proxy.get("proxy_url") or "",
                    }
                )
        if binding.get("profile_path") or binding.get("proxy_id") or binding.get("cookies"):
            return binding
    if explicit_proxy_id:
        proxy = get_proxy_profile(explicit_proxy_id, masked=False)
        if proxy and proxy.get("status") == "active" and proxy.get("proxy_url"):
            return {
                "account_id": None,
                "account_name": "",
                "platform": platform,
                "profile_path": "",
                "proxy_id": proxy.get("id"),
                "proxy_name": proxy.get("name") or "",
                "provider": proxy.get("provider") or "",
                "proxy_url": proxy.get("proxy_url") or "",
            }
    return None


def _resolve_platform_proxy_binding(platform: str, job: dict[str, Any] | None = None) -> dict[str, Any] | None:
    binding = _resolve_platform_account_binding(platform, job)
    return binding if binding and binding.get("proxy_id") else None


def _safe_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _account_summary(account_binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": account_binding.get("account_id"),
        "account_name": account_binding.get("account_name") or "",
        "platform": account_binding.get("platform") or "",
        "profile_path": str(account_binding.get("profile_path") or ""),
    }


def _proxy_summary(proxy_binding: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": proxy_binding.get("account_id"),
        "account_name": proxy_binding.get("account_name") or "",
        "proxy_id": proxy_binding.get("proxy_id"),
        "proxy_name": proxy_binding.get("proxy_name") or "",
        "provider": proxy_binding.get("provider") or "",
        "proxy_url": redact_sensitive(str(proxy_binding.get("proxy_url") or "")),
    }


def _touch_job_last_run(job_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE monitor_jobs SET last_run_at=?, updated_at=? WHERE id=?",
            (utc_now(), utc_now(), job_id),
        )


def _matches_exclude_words(content: dict[str, Any], job: dict[str, Any]) -> bool:
    exclude_words = [str(word).strip().lower() for word in job.get("exclude_words", []) if str(word).strip()]
    if not exclude_words:
        return False
    haystack = " ".join(
        str(content.get(key) or "")
        for key in ("title", "description", "source_keyword", "author_name")
    ).lower()
    return any(word in haystack for word in exclude_words)


def _run_duration_seconds(run_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT started_at FROM crawl_runs WHERE id=?", (run_id,)).fetchone()
    if not row or not row["started_at"]:
        return 0
    try:
        started = datetime.fromisoformat(str(row["started_at"]).replace("Z", "+00:00"))
        now = datetime.fromisoformat(utc_now())
        return max(0, int((now - started).total_seconds()))
    except ValueError:
        return 0


def _looks_like_login_required(log_text: str) -> bool:
    lower = log_text.lower()
    markers = [
        "no login",
        "login failed",
        "begin login",
        "login state result: false",
        "qrcode",
        "登录",
        "未登录",
        "扫码",
    ]
    return any(marker in lower for marker in markers)


def _crawler_max_retries() -> int:
    return max(0, _int_env("MONITOR_CRAWLER_MAX_RETRIES", DEFAULT_CRAWLER_MAX_RETRIES))


def _crawler_retry_delay_seconds() -> float:
    try:
        return max(0.0, float(os.environ.get("MONITOR_CRAWLER_RETRY_DELAY_SECONDS") or DEFAULT_CRAWLER_RETRY_DELAY_SECONDS))
    except ValueError:
        return DEFAULT_CRAWLER_RETRY_DELAY_SECONDS


def _should_retry_crawler_error(error: str) -> bool:
    if _looks_like_login_required(error) or "登录窗口未关闭" in error:
        return False
    return True


def _attempt_output_dir(platform_root: Path, attempt: int, total_attempts: int) -> Path:
    if total_attempts <= 1:
        return platform_root
    return platform_root / f"attempt_{attempt}"


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name) or default)
    except ValueError:
        return default


def _raise_if_stop_requested(job_id: int) -> None:
    if is_stop_requested(job_id):
        raise CrawlerStopped("任务已手动停止")


def _register_process(job_id: int, process: subprocess.Popen) -> None:
    with PROCESS_LOCK:
        RUN_PROCESSES[int(job_id)].add(process)


def _unregister_process(job_id: int, process: subprocess.Popen) -> None:
    with PROCESS_LOCK:
        processes = RUN_PROCESSES.get(int(job_id))
        if not processes:
            return
        processes.discard(process)
        if not processes:
            RUN_PROCESSES.pop(int(job_id), None)


def _terminate_process(process: subprocess.Popen) -> bool:
    if process.poll() is not None:
        return False
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            process.terminate()
        return True
    except Exception:
        try:
            process.kill()
            return True
        except Exception:
            return False


def _acquire_job_lock(job_id: int) -> Path | None:
    LOCKS_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCKS_DIR / f"job_{job_id}.lock"
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if _job_lock_is_expired(lock_path):
            _release_job_lock(lock_path)
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except OSError:
                return None
        else:
            return None
    except OSError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"job_id": job_id, "created_at": utc_now()}, ensure_ascii=False))
    return lock_path


def _release_job_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def _job_lock_is_expired(lock_path: Path) -> bool:
    try:
        raw = json.loads(lock_path.read_text(encoding="utf-8") or "{}")
        created_at = raw.get("created_at")
        created = datetime.fromisoformat(str(created_at).replace("Z", "+00:00")) if created_at else None
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created:
            return (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).total_seconds() > JOB_LOCK_TTL_SECONDS
    except Exception:
        pass
    try:
        age = datetime.now(timezone.utc).timestamp() - lock_path.stat().st_mtime
        return age > JOB_LOCK_TTL_SECONDS
    except OSError:
        return True
