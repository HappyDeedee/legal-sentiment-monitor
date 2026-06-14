from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MONITOR_YAML_PATH = PROJECT_ROOT / "monitor.yaml"


@dataclass(frozen=True)
class RuntimeSettingDefinition:
    key: str
    group: str
    label: str
    value_type: str
    default: Any
    minimum: int | None
    maximum: int | None
    apply_scope: str
    yaml_path: str
    env_lock: str


RUNTIME_SETTING_DEFINITIONS: tuple[RuntimeSettingDefinition, ...] = (
    RuntimeSettingDefinition("global_crawl_concurrency", "Crawling", "全局采集并发", "integer", 2, 1, 16, "immediate", "runtime.global_crawl_concurrency", "MONITOR_GLOBAL_CRAWL_CONCURRENCY"),
    RuntimeSettingDefinition("per_platform_concurrency.dy", "Crawling", "抖音平台并发", "integer", 1, 1, 8, "immediate", "platforms.dy.max_concurrency", "MONITOR_PLATFORM_CONCURRENCY_DY"),
    RuntimeSettingDefinition("per_platform_concurrency.xhs", "Crawling", "小红书平台并发", "integer", 1, 1, 8, "immediate", "platforms.xhs.max_concurrency", "MONITOR_PLATFORM_CONCURRENCY_XHS"),
    RuntimeSettingDefinition("per_platform_concurrency.ks", "Crawling", "快手平台并发", "integer", 1, 1, 8, "immediate", "platforms.ks.max_concurrency", "MONITOR_PLATFORM_CONCURRENCY_KS"),
    RuntimeSettingDefinition("crawler_timeout_seconds", "Crawling", "任务运行超时", "integer", 900, 60, 21600, "next run", "runtime.crawler_timeout_seconds", "MONITOR_CRAWLER_TIMEOUT_SECONDS"),
    RuntimeSettingDefinition("lock_cleanup_buffer_seconds", "Crawling", "锁清理缓冲", "integer", 300, 60, 3600, "next run", "runtime.lock_cleanup_buffer_seconds", "MONITOR_LOCK_CLEANUP_BUFFER_SECONDS"),
    RuntimeSettingDefinition("crawler_retry_count", "Crawling", "采集重试次数", "integer", 1, 0, 5, "next run", "runtime.crawler_retry_count", "MONITOR_CRAWLER_MAX_RETRIES"),
    RuntimeSettingDefinition("crawler_retry_delay_seconds", "Crawling", "采集重试间隔", "integer", 3, 0, 300, "next run", "runtime.crawler_retry_delay_seconds", "MONITOR_CRAWLER_RETRY_DELAY_SECONDS"),
    RuntimeSettingDefinition("login_qr_timeout_seconds", "Login", "二维码等待超时", "integer", 20, 5, 300, "next session", "login.qr_timeout_seconds", "MONITOR_LOGIN_QR_TIMEOUT_SECONDS"),
    RuntimeSettingDefinition("login_session_ttl_seconds", "Login", "登录会话有效期", "integer", 600, 60, 3600, "next session", "login.session_ttl_seconds", "MONITOR_LOGIN_QR_TTL_SECONDS"),
    RuntimeSettingDefinition("scheduler_tick_seconds", "Scheduler", "调度检查间隔", "integer", 60, 10, 600, "scheduler reload or restart", "scheduler.tick_seconds", "MONITOR_SCHEDULER_TICK_SECONDS"),
    RuntimeSettingDefinition("scheduler_disabled", "Scheduler", "暂停自动调度", "boolean", False, None, None, "scheduler reload or restart", "scheduler.disabled", "MONITOR_DISABLE_SCHEDULER"),
    RuntimeSettingDefinition("run_log_retention_days", "Retention", "运行日志保留天数", "integer", 90, 1, 3650, "cleanup job", "retention.run_log_days", "MONITOR_RUN_LOG_RETENTION_DAYS"),
    RuntimeSettingDefinition("report_retention_days", "Retention", "报告保留天数", "integer", 180, 1, 3650, "cleanup job", "retention.report_days", "MONITOR_REPORT_RETENTION_DAYS"),
)

DEFINITIONS_BY_KEY = {item.key: item for item in RUNTIME_SETTING_DEFINITIONS}


def load_monitor_yaml(path: Path = MONITOR_YAML_PATH) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def flatten_yaml_settings(data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for definition in RUNTIME_SETTING_DEFINITIONS:
        value = _get_nested(data, definition.yaml_path)
        if value is not None:
            result[definition.key] = value
    return result


def effective_runtime_settings(db_values: dict[str, Any] | None = None, yaml_values: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    db_values = db_values or {}
    yaml_values = yaml_values if yaml_values is not None else flatten_yaml_settings(load_monitor_yaml())
    result: dict[str, dict[str, Any]] = {}
    for definition in RUNTIME_SETTING_DEFINITIONS:
        value = definition.default
        source = "default"
        if definition.key in yaml_values:
            value = yaml_values[definition.key]
            source = "config"
        if definition.key in db_values:
            value = db_values[definition.key]
            source = "database"
        env_value = os.environ.get(definition.env_lock)
        locked = env_value not in (None, "")
        if locked:
            value = env_value
            source = "environment"
        coerced = validate_runtime_setting(definition.key, value)
        result[definition.key] = {
            "key": definition.key,
            "group": definition.group,
            "label": definition.label,
            "value_type": definition.value_type,
            "value": coerced,
            "default": definition.default,
            "minimum": definition.minimum,
            "maximum": definition.maximum,
            "range": _range_text(definition),
            "apply_scope": definition.apply_scope,
            "source": source,
            "is_locked": locked,
            "lock_reason": "deployment configuration" if locked else "",
            "yaml_path": definition.yaml_path,
        }
    return result


def validate_runtime_setting(key: str, value: Any) -> Any:
    definition = DEFINITIONS_BY_KEY.get(key)
    if not definition:
        raise ValueError(f"unknown runtime setting: {key}")
    if definition.value_type == "boolean":
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"{key} must be true or false")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be an integer") from exc
    if definition.minimum is not None and number < definition.minimum:
        raise ValueError(f"{key} must be at least {definition.minimum}")
    if definition.maximum is not None and number > definition.maximum:
        raise ValueError(f"{key} must be at most {definition.maximum}")
    return number


def setting_value_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _get_nested(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _range_text(definition: RuntimeSettingDefinition) -> str:
    if definition.value_type == "boolean":
        return "true/false"
    return f"{definition.minimum}-{definition.maximum}"
