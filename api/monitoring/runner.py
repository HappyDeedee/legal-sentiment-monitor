from __future__ import annotations

import asyncio
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ai import evaluate_content
from .database import create_run, finish_run, get_conn, get_job, get_platform_login_config, utc_now
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


async def run_job(job_id: int) -> dict[str, Any]:
    lock_path = _acquire_job_lock(job_id)
    if lock_path is None:
        return {"run_id": None, "status": "already_running", "summary": {"job_id": job_id}, "report": None}
    try:
        return await _run_job_locked(job_id)
    finally:
        _release_job_lock(lock_path)


async def _run_job_locked(job_id: int) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise ValueError("job not found")
    run_id = create_run(job_id)
    summary: dict[str, Any] = {
        "platforms": job.get("platforms", []),
        "keywords": job.get("keywords", []),
        "raw_contents": 0,
        "filtered_contents": 0,
        "excluded_contents": 0,
        "new_contents": 0,
        "negative_count": 0,
        "high_count": 0,
        "failed_platforms": [],
        "platform_results": {},
    }
    run_dir = RUNS_DIR / f"job_{job_id}" / f"run_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        tasks = [run_platform(job, run_id, platform, run_dir) for platform in job.get("platforms", [])]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        content_ids_for_eval: list[int] = []
        for platform, result in zip(job.get("platforms", []), results):
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

        eval_summary = await evaluate_new_contents(job, run_id, content_ids_for_eval)
        summary.update(eval_summary)
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
    except Exception as exc:
        summary["duration_seconds"] = _run_duration_seconds(run_id)
        finish_run(run_id, "failed", summary, f"{type(exc).__name__}: {redact_sensitive(str(exc))}")
        _touch_job_last_run(job_id)
        raise


async def run_platform(job: dict[str, Any], run_id: int, platform: str, run_dir: Path) -> dict[str, Any]:
    async with GLOBAL_SEMAPHORE:
        async with PLATFORM_LOCKS[platform]:
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
                    await asyncio.to_thread(_run_crawler_attempt, job, platform, attempt_out)
                    contents, comments = collect_platform_outputs(attempt_out, platform)
                    result = ingest_outputs(job, run_id, platform, contents, comments)
                    result["attempts"] = attempt
                    result["max_retries"] = max_retries
                    return result
                except RuntimeError as exc:
                    last_error = redact_sensitive(str(exc))
                    if not _should_retry_crawler_error(last_error) or attempt >= total_attempts:
                        break
                    await asyncio.sleep(_crawler_retry_delay_seconds())
            raise RuntimeError(f"MediaCrawler failed after {attempt} attempt(s): {last_error}")


def _run_crawler_attempt(job: dict[str, Any], platform: str, out_dir: Path) -> None:
    cmd = _build_crawler_cmd(job, platform, out_dir)
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    log_path = out_dir / "crawler.log"
    timeout_seconds = int(os.environ.get("MONITOR_CRAWLER_TIMEOUT_SECONDS") or 900)
    try:
        process = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        log_text = redact_sensitive((exc.stdout or "") + "\n" + (exc.stderr or ""))
        log_path.write_text(log_text, encoding="utf-8", errors="ignore")
        raise RuntimeError(f"MediaCrawler timed out after {timeout_seconds}s; see {log_path}") from exc
    except Exception as exc:
        safe_error = redact_sensitive(f"{type(exc).__name__}: {exc}")
        log_path.write_text(safe_error, encoding="utf-8")
        raise RuntimeError(f"MediaCrawler failed to start: {safe_error}; see {log_path}") from exc
    log_text = redact_sensitive((process.stdout or "") + "\n" + (process.stderr or ""))
    log_path.write_text(log_text, encoding="utf-8")
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
        is_related_negative = bool(evaluation["is_related"] and evaluation["is_negative"])
        if is_related_negative:
            negative_count += 1
        if is_related_negative and evaluation["risk_level"] == "high":
            high_count += 1
        _save_evaluation(row["id"], run_id, evaluation)
    return {"negative_count": negative_count, "high_count": high_count}


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


def _build_crawler_cmd(job: dict[str, Any], platform: str, out_dir: Path) -> list[str]:
    headless = os.environ.get("MONITOR_CRAWLER_HEADLESS", "true").lower() not in {"0", "false", "no"}
    connect_existing = os.environ.get("MONITOR_CDP_CONNECT_EXISTING", "false").lower() in {"1", "true", "yes"}
    debug_port = os.environ.get(f"MONITOR_CDP_DEBUG_PORT_{platform.upper()}") or os.environ.get("MONITOR_CDP_DEBUG_PORT")
    debug_port = debug_port or str(PLATFORM_DEBUG_PORTS.get(platform, 9223))
    login_config = get_platform_login_config(platform, masked=False)
    login_type = login_config.get("login_type") or "qrcode"
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
        "search",
        "--save_data_option",
        "json",
        "--keywords",
        ",".join(job.get("keywords", [])),
        "--get_comment",
        "true" if job.get("enable_comments") else "false",
        "--get_sub_comment",
        "false",
        "--headless",
        "true" if headless else "false",
        "--save_data_path",
        str(out_dir),
        "--max_concurrency_num",
        "1",
    ]
    if login_type == "cookie":
        cookies = login_config.get("cookies") or ""
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
