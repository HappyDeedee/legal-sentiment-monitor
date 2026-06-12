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
