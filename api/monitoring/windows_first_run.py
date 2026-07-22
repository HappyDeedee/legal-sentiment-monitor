from __future__ import annotations

import argparse
import getpass
import os
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from .database import bootstrap_admin_from_env, has_active_administrator, init_db
from .security import MONITOR_DATA_DIR


MIN_FREE_BYTES = 1024**3
MIN_NODE_MAJOR_VERSION = 16
DEFAULT_ADMIN_DISPLAY_NAME = "系统管理员"
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+$")
_NODE_VERSION_PATTERN = re.compile(r"^v?(\d+)(?:\.\d+){0,2}$")


class FirstRunPreflightError(RuntimeError):
    pass


@dataclass(frozen=True)
class FirstRunPreflightResult:
    data_dir: Path
    free_bytes: int
    admin_source: str


def run_first_run_preflight(
    bind_host: str,
    port: int,
    *,
    data_dir: Path = MONITOR_DATA_DIR,
    min_free_bytes: int = MIN_FREE_BYTES,
    interactive: bool | None = None,
    environ: Mapping[str, str] | None = None,
    input_fn: Callable[[str], str] | None = None,
    password_fn: Callable[[str], str] | None = None,
) -> FirstRunPreflightResult:
    check_command_runtime("uv")
    check_javascript_runtime()
    resolved_data_dir, free_bytes = check_data_directory(data_dir, min_free_bytes)
    check_port_available(bind_host, port)
    try:
        init_db()
    except Exception as exc:
        raise FirstRunPreflightError(
            f"本地数据库初始化失败（{type(exc).__name__}）。请检查数据目录权限和磁盘状态。"
        ) from exc
    try:
        admin_source = ensure_initial_administrator(
            interactive=sys.stdin.isatty() if interactive is None else interactive,
            environ=os.environ if environ is None else environ,
            input_fn=input if input_fn is None else input_fn,
            password_fn=getpass.getpass if password_fn is None else password_fn,
        )
    except FirstRunPreflightError:
        raise
    except Exception as exc:
        raise FirstRunPreflightError(
            f"管理员账号检查失败（{type(exc).__name__}）。"
        ) from exc
    return FirstRunPreflightResult(
        data_dir=resolved_data_dir,
        free_bytes=free_bytes,
        admin_source=admin_source,
    )


def check_data_directory(data_dir: Path, min_free_bytes: int = MIN_FREE_BYTES) -> tuple[Path, int]:
    resolved = Path(data_dir).expanduser().resolve()
    probe = resolved / f".startup_write_test_{os.getpid()}"
    try:
        resolved.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        raise FirstRunPreflightError(
            f"运行数据目录不可写：{resolved}。请检查目录权限或 MONITOR_DATA_DIR。"
        ) from exc
    finally:
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass

    try:
        free_bytes = int(shutil.disk_usage(resolved).free)
    except OSError as exc:
        raise FirstRunPreflightError("运行数据目录的磁盘空间检查失败。") from exc
    required = max(0, int(min_free_bytes))
    if free_bytes < required:
        required_gb = required / (1024**3)
        free_gb = free_bytes / (1024**3)
        raise FirstRunPreflightError(
            f"运行数据所在磁盘剩余 {free_gb:.1f} GB，启动至少需要 {required_gb:.1f} GB。"
        )
    return resolved, free_bytes


def check_port_available(bind_host: str, port: int) -> None:
    normalized_host = str(bind_host or "0.0.0.0").strip() or "0.0.0.0"
    normalized_port = int(port)
    if not 1 <= normalized_port <= 65535:
        raise FirstRunPreflightError("MONITOR_PORT 必须是 1 到 65535 之间的端口号。")
    family = socket.AF_INET6 if ":" in normalized_host else socket.AF_INET
    address: tuple[str, int] | tuple[str, int, int, int]
    address = (normalized_host, normalized_port, 0, 0) if family == socket.AF_INET6 else (normalized_host, normalized_port)
    try:
        with socket.socket(family, socket.SOCK_STREAM) as probe:
            probe.bind(address)
    except OSError as exc:
        raise FirstRunPreflightError(
            f"端口 {normalized_port} 已被占用或当前地址不可绑定。请关闭旧服务，或设置新的 MONITOR_PORT。"
        ) from exc


def check_command_runtime(command: str) -> Path:
    executable = shutil.which(command)
    if not executable:
        raise FirstRunPreflightError(
            f"运行命令 {command} 在当前服务 PATH 中不可用，请重新运行 Windows 一键启动。"
        )
    return Path(executable).resolve()


def resolve_node_executable() -> Path:
    system_node = shutil.which("node")
    if system_node and _node_major_version(Path(system_node)) >= MIN_NODE_MAJOR_VERSION:
        return Path(system_node).resolve()

    import playwright

    bundled_node = Path(playwright.__file__).resolve().parent / "driver" / "node.exe"
    if bundled_node.is_file() and _node_major_version(bundled_node) >= MIN_NODE_MAJOR_VERSION:
        return bundled_node.resolve()
    raise FirstRunPreflightError(
        f"未检测到 Node.js {MIN_NODE_MAJOR_VERSION} 或更高版本，且 Playwright 内置 Node 不可用。"
    )


def check_javascript_runtime() -> Path:
    node_path = check_command_runtime("node")
    if _node_major_version(node_path) < MIN_NODE_MAJOR_VERSION:
        raise FirstRunPreflightError(
            f"Node.js 版本过低，项目至少需要 {MIN_NODE_MAJOR_VERSION}。"
        )
    bootstrap_password = os.environ.pop("MONITOR_ADMIN_PASSWORD", None)
    try:
        import execjs
        from media_platform.douyin.help import douyin_sign_obj

        runtime_name = str(execjs.get().name or "")
        signature = douyin_sign_obj.call("sign_datail", "keyword=test", "Mozilla/5.0")
        if "node" not in runtime_name.lower() or not isinstance(signature, str) or not signature:
            raise RuntimeError("unexpected Douyin JavaScript runtime result")
    except Exception as exc:
        raise FirstRunPreflightError("Node.js 运行时检查失败，抖音采集尚未就绪。") from exc
    finally:
        if bootstrap_password is not None:
            os.environ["MONITOR_ADMIN_PASSWORD"] = bootstrap_password
    return node_path


def _node_major_version(executable: Path) -> int:
    child_env = dict(os.environ)
    child_env.pop("MONITOR_ADMIN_PASSWORD", None)
    try:
        result = subprocess.run(
            [str(executable), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=child_env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 0
    version_text = str(result.stdout or result.stderr or "").strip()
    match = _NODE_VERSION_PATTERN.fullmatch(version_text)
    return int(match.group(1)) if result.returncode == 0 and match else 0


def ensure_initial_administrator(
    *,
    interactive: bool,
    environ: Mapping[str, str],
    input_fn: Callable[[str], str],
    password_fn: Callable[[str], str],
) -> str:
    if has_active_administrator():
        return "existing"

    email = str(environ.get("MONITOR_ADMIN_EMAIL") or "").strip().lower()
    password = str(environ.get("MONITOR_ADMIN_PASSWORD") or "")
    display_name = str(environ.get("MONITOR_ADMIN_DISPLAY_NAME") or "").strip()
    if bool(email) != bool(password):
        raise FirstRunPreflightError(
            "首次管理员环境变量不完整，请同时设置 MONITOR_ADMIN_EMAIL 和 MONITOR_ADMIN_PASSWORD。"
        )
    if email:
        _validate_admin_email(email)
        created = bootstrap_admin_from_env(email, password, display_name or DEFAULT_ADMIN_DISPLAY_NAME)
        if not created or not has_active_administrator():
            raise FirstRunPreflightError("首次管理员创建后校验失败。")
        return "environment"

    if not interactive:
        raise FirstRunPreflightError(
            "当前没有管理员账号。请在可交互的 Windows 控制台运行一键启动，"
            "或同时设置 MONITOR_ADMIN_EMAIL 和 MONITOR_ADMIN_PASSWORD。"
        )

    email, display_name, password = _prompt_initial_administrator(input_fn, password_fn)
    created = bootstrap_admin_from_env(email, password, display_name)
    if not created or not has_active_administrator():
        raise FirstRunPreflightError("首次管理员创建后校验失败。")
    return "interactive"


def _prompt_initial_administrator(
    input_fn: Callable[[str], str],
    password_fn: Callable[[str], str],
) -> tuple[str, str, str]:
    print("首次启动：请创建系统管理员账号。密码输入时不会显示在屏幕上。", flush=True)
    for _ in range(3):
        email = str(input_fn("管理员邮箱: ") or "").strip().lower()
        try:
            _validate_admin_email(email)
        except FirstRunPreflightError as exc:
            print(str(exc), flush=True)
            continue
        display_name = str(input_fn(f"显示名称 [{DEFAULT_ADMIN_DISPLAY_NAME}]: ") or "").strip()
        password = str(password_fn("管理员密码（至少 8 位）: ") or "")
        confirmation = str(password_fn("再次输入管理员密码: ") or "")
        if len(password) < 8:
            print("管理员密码至少需要 8 位。", flush=True)
            continue
        if password != confirmation:
            print("两次输入的密码不一致。", flush=True)
            continue
        return email, display_name or DEFAULT_ADMIN_DISPLAY_NAME, password
    raise FirstRunPreflightError("管理员账号连续三次录入未通过，请重新运行一键启动。")


def _validate_admin_email(email: str) -> None:
    if not _EMAIL_PATTERN.fullmatch(str(email or "").strip()):
        raise FirstRunPreflightError("管理员邮箱格式不正确，邮箱必须包含 @。")


def main(argv: list[str] | None = None) -> int:
    bootstrap_environ = dict(os.environ)
    os.environ.pop("MONITOR_ADMIN_PASSWORD", None)
    parser = argparse.ArgumentParser(description="Windows local first-run preflight")
    parser.add_argument("--host", default=os.environ.get("MONITOR_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MONITOR_PORT", "8080")))
    parser.add_argument("--non-interactive", action="store_true")
    parser.add_argument("--print-node-executable", action="store_true")
    args = parser.parse_args(argv)

    if args.print_node_executable:
        try:
            print(resolve_node_executable())
            return 0
        except FirstRunPreflightError as exc:
            print(f"Node.js 预检失败: {exc}", file=sys.stderr, flush=True)
            return 1

    try:
        result = run_first_run_preflight(
            args.host,
            args.port,
            interactive=False if args.non_interactive else None,
            environ=bootstrap_environ,
        )
    except (FirstRunPreflightError, ValueError) as exc:
        print(f"启动预检失败: {exc}", file=sys.stderr, flush=True)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("启动预检已取消。", file=sys.stderr, flush=True)
        return 1

    free_gb = result.free_bytes / (1024**3)
    print(f"数据目录检查通过，剩余空间 {free_gb:.1f} GB。", flush=True)
    print(f"端口检查通过: {args.host}:{args.port}", flush=True)
    if result.admin_source == "existing":
        print("管理员检查通过：已存在可用管理员账号。", flush=True)
    else:
        print("管理员检查通过：首次管理员账号已创建。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
