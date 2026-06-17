from __future__ import annotations

import hashlib
import mimetypes
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .security import MONITOR_DATA_DIR


AVATAR_CACHE_DIR = MONITOR_DATA_DIR / "account_avatars"
MAX_AVATAR_BYTES = 2 * 1024 * 1024


def cache_account_avatar(account_id: int, avatar_url: Any, *, timeout: float = 10.0) -> Path | None:
    url = str(avatar_url or "").strip()
    if not _is_cacheable_avatar_url(url):
        return None
    AVATAR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    target = _cache_path(account_id, url)
    if target.exists() and target.stat().st_size > 0:
        return target
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 LegalSentimentMonitor/1.0",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = str(response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            if content_type and not content_type.startswith("image/"):
                return None
            data = response.read(MAX_AVATAR_BYTES + 1)
    except Exception:
        return None
    if not data or len(data) > MAX_AVATAR_BYTES or not _looks_like_image(data):
        return None
    target.write_bytes(data)
    _remove_stale_account_avatars(account_id, keep=target)
    return target


def avatar_media_type(path: Path) -> str:
    guessed = mimetypes.guess_type(path.name)[0]
    return guessed or "image/jpeg"


def has_cacheable_avatar_url(avatar_url: Any) -> bool:
    return _is_cacheable_avatar_url(str(avatar_url or "").strip())


def _is_cacheable_avatar_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def _cache_path(account_id: int, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    suffix = _suffix_from_url(url)
    return AVATAR_CACHE_DIR / f"account_{int(account_id)}_{digest}{suffix}"


def _suffix_from_url(url: str) -> str:
    path_suffix = Path(urlsplit(url).path).suffix.lower()
    if path_suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"}:
        return path_suffix
    return ".jpg"


def _looks_like_image(data: bytes) -> bool:
    return data.startswith(
        (
            b"\xff\xd8\xff",
            b"\x89PNG\r\n\x1a\n",
            b"GIF87a",
            b"GIF89a",
            b"RIFF",
            b"<svg",
            b"<?xml",
            b"\x00\x00\x00",
        )
    )


def _remove_stale_account_avatars(account_id: int, *, keep: Path) -> None:
    pattern = f"account_{int(account_id)}_*"
    for path in AVATAR_CACHE_DIR.glob(pattern):
        if path != keep:
            try:
                path.unlink()
            except OSError:
                pass
