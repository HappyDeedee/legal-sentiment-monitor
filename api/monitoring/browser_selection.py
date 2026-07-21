from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator

from tools.browser_launcher import BrowserLauncher

from .account_environment import ACCOUNT_PROFILE_ROOT
from .security import MONITOR_DATA_DIR


BROWSER_SELECTION_PATH = MONITOR_DATA_DIR / "browser_selection.json"
SELECTION_CONTRACT_VERSION = 1
SELECTION_LOCK_TIMEOUT_SECONDS = 15.0
_SYSTEM_SOURCES = {
    "system_chrome": "chrome",
    "system_edge": "edge",
    "system_chromium": "chromium",
}
_VALID_CHANNELS = frozenset({"chrome", "edge", "chromium", "playwright", "custom"})
_VALID_SOURCES = frozenset({"explicit", "playwright_bundled", *_SYSTEM_SOURCES})
_MANIFEST_KEYS = {
    "contract_version",
    "browser_source",
    "browser_channel",
    "executable_path",
}


@dataclass(frozen=True)
class BrowserSelection:
    executable_path: Path
    source: str
    channel: str


class BrowserSelectionError(RuntimeError):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def resolve_browser_selection(
    playwright_executable_path: str | Path,
    *,
    allow_system: bool,
    persist: bool = False,
) -> BrowserSelection:
    if persist:
        with _browser_selection_lock():
            return _resolve_browser_selection_unlocked(
                playwright_executable_path,
                allow_system=allow_system,
                persist=True,
            )
    return _resolve_browser_selection_unlocked(
        playwright_executable_path,
        allow_system=allow_system,
        persist=False,
    )


def require_persisted_browser_selection() -> BrowserSelection:
    with _browser_selection_lock():
        saved = _load_saved_selection(validate_system_detection=False)
        if saved is None:
            raise BrowserSelectionError(
                "selection_missing",
                "未找到已保存的浏览器选择，请先运行浏览器预检。",
            )
        if not saved.executable_path.is_file():
            raise BrowserSelectionError(
                "saved_browser_missing",
                "已保存的本机浏览器不存在。请恢复该浏览器，或重置账号登录环境后重新选择。",
            )
        return saved


def _resolve_browser_selection_unlocked(
    playwright_executable_path: str | Path,
    *,
    allow_system: bool,
    persist: bool,
) -> BrowserSelection:
    explicit_value = str(os.environ.get("MONITOR_BROWSER_EXECUTABLE") or "").strip().strip('"')
    saved = _load_saved_selection(validate_system_detection=allow_system)

    if explicit_value:
        explicit_path = _resolved_path(explicit_value, "explicit_browser_invalid")
        if not explicit_path.is_file():
            raise BrowserSelectionError(
                "explicit_browser_missing",
                "MONITOR_BROWSER_EXECUTABLE 指定的浏览器不存在，请修正或清空后重试。",
            )
        if saved and saved.executable_path != explicit_path:
            raise BrowserSelectionError(
                "selection_conflict",
                "MONITOR_BROWSER_EXECUTABLE 与已保存的浏览器选择不一致。更换浏览器前请重置并重新登录账号。",
            )
        selection = saved or BrowserSelection(explicit_path, "explicit", _browser_channel(explicit_path))
        return _persist_selection(selection) if persist else selection

    playwright_path = _resolved_path(playwright_executable_path, "playwright_path_invalid")
    if saved:
        return _resolve_saved_selection(saved, playwright_path, persist=persist)

    if _profile_data_exists():
        return _select_playwright(playwright_path, persist=persist)

    if allow_system:
        for candidate in _detect_system_browser_paths():
            path = _resolved_path(candidate, "system_browser_invalid")
            if not path.is_file():
                continue
            channel = _browser_channel(path)
            source = {
                "chrome": "system_chrome",
                "edge": "system_edge",
                "chromium": "system_chromium",
            }.get(channel)
            if source:
                selection = BrowserSelection(path, source, channel)
                return _persist_selection(selection) if persist else selection

    return _select_playwright(playwright_path, persist=persist)


def _resolve_saved_selection(
    saved: BrowserSelection,
    playwright_path: Path,
    *,
    persist: bool,
) -> BrowserSelection:
    if saved.executable_path.is_file():
        return saved
    if saved.source == "playwright_bundled":
        if not playwright_path.is_file():
            raise BrowserSelectionError(
                "playwright_missing",
                "已选择 Playwright Chromium，但当前版本的浏览器程序尚未安装。",
            )
        updated = BrowserSelection(playwright_path, "playwright_bundled", "playwright")
        return _persist_selection(updated) if persist else updated
    raise BrowserSelectionError(
        "saved_browser_missing",
        "已保存的本机浏览器不存在。请恢复该浏览器，或重置账号登录环境后重新选择。",
    )


def _select_playwright(playwright_path: Path, *, persist: bool) -> BrowserSelection:
    if not playwright_path.is_file():
        raise BrowserSelectionError(
            "playwright_missing",
            "未检测到可用的本机浏览器或 Playwright Chromium。",
        )
    selection = BrowserSelection(playwright_path, "playwright_bundled", "playwright")
    return _persist_selection(selection) if persist else selection


def _load_saved_selection(*, validate_system_detection: bool) -> BrowserSelection | None:
    if not BROWSER_SELECTION_PATH.exists():
        return None
    try:
        if BROWSER_SELECTION_PATH.stat().st_size > 8192:
            raise ValueError("manifest too large")
        payload = json.loads(BROWSER_SELECTION_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or set(payload) != _MANIFEST_KEYS:
            raise ValueError("invalid manifest fields")
        if payload["contract_version"] != SELECTION_CONTRACT_VERSION:
            raise ValueError("invalid manifest version")
        source = str(payload["browser_source"])
        channel = str(payload["browser_channel"])
        if source not in _VALID_SOURCES or channel not in _VALID_CHANNELS:
            raise ValueError("invalid browser selection")
        if source in _SYSTEM_SOURCES and _SYSTEM_SOURCES[source] != channel:
            raise ValueError("inconsistent system browser selection")
        if source == "playwright_bundled" and channel != "playwright":
            raise ValueError("inconsistent Playwright selection")
        executable_path = _resolved_path(payload["executable_path"], "selection_manifest_invalid")
        if source in _SYSTEM_SOURCES:
            if _browser_channel(executable_path) != channel:
                raise ValueError("system browser path does not match channel")
            if validate_system_detection:
                detected_paths = {
                    _resolved_path(path, "selection_manifest_invalid")
                    for path in _detect_system_browser_paths()
                }
                if executable_path not in detected_paths:
                    raise ValueError("system browser path is no longer detectable")
        return BrowserSelection(executable_path, source, channel)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BrowserSelectionError(
            "selection_manifest_invalid",
            "浏览器选择文件无效，请检查本机运行数据后重试。",
        ) from exc


def _persist_selection(selection: BrowserSelection) -> BrowserSelection:
    payload = {
        "contract_version": SELECTION_CONTRACT_VERSION,
        "browser_source": selection.source,
        "browser_channel": selection.channel,
        "executable_path": str(selection.executable_path),
    }
    BROWSER_SELECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = BROWSER_SELECTION_PATH.with_name(
        f"{BROWSER_SELECTION_PATH.name}.tmp.{os.getpid()}"
    )
    try:
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(temporary, BROWSER_SELECTION_PATH)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise BrowserSelectionError(
            "selection_write_failed",
            "保存浏览器选择失败，请检查本机运行数据目录权限。",
        ) from exc
    return selection


@contextmanager
def _browser_selection_lock() -> Iterator[None]:
    lock_path = BROWSER_SELECTION_PATH.with_name(f"{BROWSER_SELECTION_PATH.name}.lock")
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = lock_path.open("a+b")
    except OSError as exc:
        raise BrowserSelectionError(
            "selection_lock_failed",
            "打开浏览器选择锁失败，请检查本机运行数据目录权限。",
        ) from exc

    acquired = False
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        deadline = time.monotonic() + SELECTION_LOCK_TIMEOUT_SECONDS
        while True:
            try:
                _try_lock_handle(handle)
                acquired = True
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise BrowserSelectionError(
                        "selection_lock_timeout",
                        "等待浏览器选择锁超时，请关闭重复启动窗口后重试。",
                    ) from exc
                time.sleep(0.05)
        yield
    finally:
        if acquired:
            try:
                _unlock_handle(handle)
            except OSError:
                pass
        handle.close()


def _try_lock_handle(handle: BinaryIO) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_handle(handle: BinaryIO) -> None:
    handle.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _detect_system_browser_paths() -> list[Path]:
    return [Path(value) for value in BrowserLauncher().detect_browser_paths()]


def _profile_data_exists() -> bool:
    try:
        return ACCOUNT_PROFILE_ROOT.exists() and next(ACCOUNT_PROFILE_ROOT.iterdir(), None) is not None
    except OSError as exc:
        raise BrowserSelectionError(
            "profile_root_unreadable",
            "检查现有账号 Profile 失败，请检查本机运行数据目录权限。",
        ) from exc


def _browser_channel(path: Path) -> str:
    value = str(path).lower().replace("/", "\\")
    if "msedge" in value or "\\microsoft edge" in value or "\\microsoft\\edge" in value:
        return "edge"
    if "chromium" in value:
        return "chromium"
    if "chrome" in value:
        return "chrome"
    return "custom"


def _resolved_path(value: str | Path, reason: str) -> Path:
    text = str(value or "").strip().strip('"')
    if not text or "\x00" in text:
        raise BrowserSelectionError(reason, "浏览器路径无效，请检查配置后重试。")
    try:
        return Path(text).expanduser().resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise BrowserSelectionError(reason, "浏览器路径无效，请检查配置后重试。") from exc
