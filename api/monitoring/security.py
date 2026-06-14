import base64
import os
import re
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONITOR_DATA_DIR = Path(os.environ.get("MONITOR_DATA_DIR") or PROJECT_ROOT / "monitor_data").resolve()
KEY_PATH = MONITOR_DATA_DIR / "secret.key"


def _get_fernet() -> Fernet:
    MONITOR_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()
    else:
        key = Fernet.generate_key()
        KEY_PATH.write_bytes(key)
    return Fernet(key)


def encrypt_secret(value: str | None) -> str:
    if not value:
        return ""
    return _get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str | None) -> str:
    if not value:
        return ""
    try:
        return _get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        try:
            return base64.b64decode(value.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""


def mask_secret(value: str | None) -> str:
    raw = decrypt_secret(value)
    if not raw:
        return ""
    if len(raw) <= 8:
        return "*" * len(raw)
    return f"{raw[:3]}{'*' * 8}{raw[-4:]}"


def redact_sensitive(text: str | None) -> str:
    if not text:
        return ""
    result = str(text)
    patterns = [
        (r"(?i)\b(https?|socks5h?|socks4)://([^:/@\s]+):([^@/\s]+)@", r"\1://[REDACTED]@"),
        (r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(x-api-key\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(password\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(smtp[_-]?password\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(cookie\s*[:=]\s*)[^\r\n]+", r"\1[REDACTED]"),
        (r"(?i)(token\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"(?i)(secret\s*[:=]\s*)[^\s,;'\"]+", r"\1[REDACTED]"),
        (r"\bsk-[A-Za-z0-9_\-]{12,}\b", "sk-[REDACTED]"),
    ]
    for pattern, repl in patterns:
        result = re.sub(pattern, repl, result)
    return result


def customer_safe_text(text: str | None) -> str:
    """Convert internal diagnostics into product-facing wording."""
    if not text:
        return ""
    result = redact_sensitive(str(text))
    replacements = [
        (r"MediaCrawler failed after \d+ attempt\(s\):\s*", ""),
        (r"MediaCrawler timed out after \d+s", "平台采集服务运行超时"),
        (r"MediaCrawler failed to start", "平台采集服务启动失败"),
        (r"MediaCrawler exited with \d+[；;]?", "平台采集服务运行失败；"),
        (r"MediaCrawler", "平台采集服务"),
        (r"MONITOR_SKIP_AI_API(?:=true|=false)?", "AI 服务未启用"),
        (r"AI API 已通过 AI 服务未启用 临时关闭", "AI 服务未启用"),
        (r"AI API 已通过 AI 离线测试模式 临时关闭", "AI 服务未启用"),
        (r"AI 服务当前处于离线测试模式", "AI 服务未启用"),
        (r"离线自检", "规则检查"),
        (r"离线模式", "待人工复核模式"),
        (r"离线测试模式", "待人工复核模式"),
        (r"selftest-report", "系统自检报告"),
        (r"selftest", "系统自检"),
        (r"本地自测", "系统自检"),
        (r"MVP自测律所", "海安律所"),
        (r"登录窗口测试律所", "海安律所"),
        (r"上线验收", "系统运行"),
        (r"待验收", "配置待完善"),
        (r"验收模板", "测试数据模板"),
        (r"验收", "确认"),
        (r"项目进展", "系统状态"),
        (r"真实测试 AI", "连接测试"),
        (r"本地冒烟自检", "系统自检"),
        (r"生成自测报告", "生成系统自检报告"),
        (r"浏览器 Profile", "网页登录态"),
        (r"默认 Profile", "默认网页登录态"),
        (r"\bProfile\b", "网页登录态"),
        (r"运行三平台采集", "运行平台采集"),
        (r"first commit", "初始化提交"),
        (r"\bCLI\b", "命令行工具"),
        (r"\buv run python main\.py\b[^；。\n]*", "平台采集服务"),
        (r"\bmain\.py\b", "采集入口"),
        (r"\bdebug\b", "诊断"),
        (r"\bDEBUG\b", "诊断"),
    ]
    for pattern, repl in replacements:
        result = re.sub(pattern, repl, result)
    result = re.sub(r"; see .*$", "", result)
    result = re.sub(r"；see .*$", "", result)
    result = re.sub(r"see [A-Za-z]:\\[^\s，。；]+", "", result)
    result = re.sub(r"[A-Za-z]:\\[^\s，。；]+", "运行日志", result)
    result = result.replace("AI API 已通过 AI 离线测试模式 临时关闭", "AI 服务未启用")
    if "AI 服务未启用" in result and ("待人工复核模式" in result or "规则检查" in result):
        return "AI 服务未启用；采集不受影响，内容会进入待人工复核。"
    return result.strip()
