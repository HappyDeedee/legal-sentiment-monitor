from __future__ import annotations

import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any


PLATFORM_LABELS = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}
PLATFORM_OUTPUT_DIRS = {"dy": "douyin", "ks": "kuaishou", "xhs": "xhs"}


def parse_json_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def parse_jsonl_file(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            items.append(data)
    return items


def collect_platform_outputs(run_dir: Path, platform: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contents: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    output_name = PLATFORM_OUTPUT_DIRS.get(platform, platform)
    candidate_roots = [run_dir / output_name, run_dir / platform, run_dir]
    for root in candidate_roots:
        platform_dir = root / "json"
        if not platform_dir.exists():
            pass
        else:
            for path in platform_dir.glob("*_contents_*.json"):
                contents.extend(parse_json_file(path))
            for path in platform_dir.glob("*_comments_*.json"):
                comments.extend(parse_json_file(path))
        jsonl_dir = root / "jsonl"
        if not jsonl_dir.exists():
            continue
        for path in jsonl_dir.glob("*_contents_*.jsonl"):
            contents.extend(parse_jsonl_file(path))
        for path in jsonl_dir.glob("*_comments_*.jsonl"):
            comments.extend(parse_jsonl_file(path))
    return contents, comments


def normalize_content(platform: str, item: dict[str, Any], job: dict[str, Any]) -> dict[str, Any] | None:
    if platform == "dy":
        content_id = str(item.get("aweme_id") or "")
        title = item.get("title") or item.get("desc") or ""
        content_url = item.get("aweme_url") or (f"https://www.douyin.com/video/{content_id}" if content_id else "")
        cover_url = item.get("cover_url") or item.get("note_download_url") or ""
        publish_time = _int_or_none(item.get("create_time"))
        comment_count = _int_or_none(item.get("comment_count"))
    elif platform == "ks":
        content_id = str(item.get("video_id") or "")
        title = item.get("title") or item.get("desc") or ""
        content_url = item.get("video_url") or (f"https://www.kuaishou.com/short-video/{content_id}" if content_id else "")
        cover_url = item.get("video_cover_url") or item.get("cover_url") or ""
        publish_time = _int_or_none(item.get("create_time") or item.get("timestamp"))
        comment_count = _int_or_none(item.get("comment_count"))
    elif platform == "xhs":
        content_id = str(item.get("note_id") or "")
        title = item.get("title") or item.get("desc") or ""
        content_url = item.get("note_url") or (f"https://www.xiaohongshu.com/explore/{content_id}" if content_id else "")
        cover_url = _first_media_url(item.get("image_list"))
        publish_time = _int_or_none(item.get("time") or item.get("last_update_time"))
        comment_count = _int_or_none(item.get("comment_count"))
    else:
        return None
    if not content_id:
        return None
    return {
        "platform": platform,
        "platform_label": PLATFORM_LABELS.get(platform, platform),
        "content_id": content_id,
        "law_firm_name": job.get("law_firm_name") or "",
        "source_keyword": item.get("source_keyword") or _infer_keyword(item, job, str(title)),
        "title": str(title)[:1000],
        "description": str(item.get("desc") or title or "")[:5000],
        "author_name": item.get("nickname") or "",
        "content_url": content_url,
        "cover_url": cover_url,
        "publish_time": publish_time,
        "comment_count": comment_count,
        "raw_json": json.dumps(item, ensure_ascii=False),
    }


def normalize_comment(platform: str, item: dict[str, Any]) -> dict[str, Any] | None:
    if platform == "dy":
        comment_id = str(item.get("comment_id") or "")
        content_id = str(item.get("aweme_id") or "")
    elif platform == "ks":
        comment_id = str(item.get("comment_id") or "")
        content_id = str(item.get("video_id") or "")
    elif platform == "xhs":
        comment_id = str(item.get("comment_id") or "")
        content_id = str(item.get("note_id") or "")
    else:
        return None
    if not comment_id or not content_id:
        return None
    return {
        "platform": platform,
        "comment_id": comment_id,
        "content_id": content_id,
        "content": item.get("content") or "",
        "author_name": item.get("nickname") or "",
        "create_time": _int_or_none(item.get("create_time")),
        "raw_json": json.dumps(item, ensure_ascii=False),
    }


def in_time_window(content: dict[str, Any], job: dict[str, Any]) -> bool:
    publish_time = content.get("publish_time")
    if not publish_time:
        return True
    start, end = resolve_window(job)
    ts = datetime.fromtimestamp(_epoch_seconds(int(publish_time)), timezone.utc)
    return start <= ts <= end


def resolve_window(job: dict[str, Any]) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    window_type = job.get("time_window_type") or "recent_1d"
    if window_type == "recent_7d":
        delta_days = 7
    elif window_type == "recent_30d":
        delta_days = 30
    elif window_type == "custom":
        start = _parse_dt(job.get("custom_start")) or now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = _parse_dt(job.get("custom_end"), end_of_day=True) or now
        return start, end
    else:
        delta_days = 1
    return now.replace(microsecond=0) - timedelta(days=delta_days), now


def douyin_publish_time_type(job: dict[str, Any]) -> int:
    window_type = job.get("time_window_type") or "recent_1d"
    if window_type == "recent_1d":
        return 1
    if window_type == "recent_7d":
        return 7
    if window_type in {"recent_30d", "custom"}:
        return 180
    return 0


def _parse_dt(value: str | None, end_of_day: bool = False) -> datetime | None:
    if not value:
        return None
    try:
        if len(value) == 10 and value.count("-") == 2:
            base_date = datetime.fromisoformat(value).date()
            dt_time = time.max if end_of_day else time.min
            return datetime.combine(base_date, dt_time, tzinfo=timezone.utc)
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _epoch_seconds(value: int) -> int:
    if value > 10_000_000_000:
        return value // 1000
    return value


def _first_csv(value: str) -> str:
    return value.split(",")[0].strip() if value else ""


def _first_media_url(value: Any) -> str:
    if isinstance(value, list):
        if not value:
            return ""
        first = value[0]
        if isinstance(first, dict):
            return str(first.get("url") or first.get("trace_id") or "")
        return str(first)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            parsed = json.loads(text)
            return _first_media_url(parsed)
        except json.JSONDecodeError:
            return _first_csv(text)
    return ""


def _infer_keyword(item: dict[str, Any], job: dict[str, Any], title: str) -> str:
    haystack = f"{title} {item.get('desc') or ''}".lower()
    for keyword in job.get("keywords", []):
        if str(keyword).lower() in haystack:
            return str(keyword)
    keywords = job.get("keywords", [])
    return str(keywords[0]) if keywords else ""
