from __future__ import annotations

import json
from typing import Any

import httpx

from .database import get_ai_config, validate_temperature


DEFAULT_PROMPT = """你是舆情线索初筛助手。请判断内容是否与目标律所相关，以及是否属于疑似负面舆情。
负面包括投诉、避雷、退费、收费争议、服务差、欺诈质疑、维权、曝光等。
同名无关、普通法律科普、普通广告、无法判断时不要标为明确负面。
只输出 JSON，不要输出解释性前后缀。
字段：is_related(boolean), is_negative(boolean), risk_level(high|medium|low|irrelevant), reason(string), evidence_quotes(string[]), recommended_action(string)。"""


async def evaluate_content(job: dict[str, Any], content: dict[str, Any], comments: list[dict[str, Any]]) -> dict[str, Any]:
    cfg = get_ai_config(masked=False)
    if not cfg.get("api_key") or not cfg.get("model") or not cfg.get("base_url"):
        return _fallback("AI 配置未完成", content)

    prompt = cfg.get("prompt") or DEFAULT_PROMPT
    user_payload = {
        "law_firm_name": job.get("law_firm_name"),
        "aliases": job.get("aliases", []),
        "exclude_words": job.get("exclude_words", []),
        "platform": content.get("platform_label") or content.get("platform"),
        "source_keyword": content.get("source_keyword"),
        "title": content.get("title"),
        "description": content.get("description"),
        "comments": [c.get("content", "") for c in comments[:10] if c.get("content")],
    }
    try:
        if cfg.get("provider") == "anthropic":
            raw = await _call_anthropic(cfg, prompt, user_payload)
        else:
            raw = await _call_openai(cfg, prompt, user_payload)
        data = _parse_json(raw)
        return {
            "status": "ok",
            "is_related": bool(data.get("is_related")),
            "is_negative": bool(data.get("is_negative")),
            "risk_level": _normalize_risk(data.get("risk_level")),
            "reason": str(data.get("reason") or ""),
            "evidence_quotes": data.get("evidence_quotes") if isinstance(data.get("evidence_quotes"), list) else [],
            "recommended_action": str(data.get("recommended_action") or ""),
            "raw_response": raw,
        }
    except Exception as exc:
        return _fallback(f"AI 评估失败：{type(exc).__name__}: {exc}", content)


async def test_ai(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _merge_test_config(payload)
    prompt = cfg.get("prompt") or DEFAULT_PROMPT
    sample = {
        "law_firm_name": "测试律所",
        "aliases": ["测试律师事务所"],
        "exclude_words": [],
        "platform": "抖音",
        "source_keyword": "测试律所避雷",
        "title": payload.get("sample_title") or "这家测试律所服务太差，退费拖了很久",
        "description": payload.get("sample_text") or "我想曝光一下，沟通很差，收费也不透明。",
        "comments": [],
    }
    if cfg.get("provider") == "anthropic":
        raw = await _call_anthropic(cfg, prompt, sample)
    else:
        raw = await _call_openai(cfg, prompt, sample)
    data = _parse_json(raw)
    return _validate_ai_output(data)


async def _call_openai(cfg: dict[str, Any], prompt: str, payload: dict[str, Any]) -> str:
    url = _build_endpoint(str(cfg.get("base_url", "")), "/v1/chat/completions")
    async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
        res = await client.post(
            url,
            headers={"Authorization": f"Bearer {cfg.get('api_key')}", "Content-Type": "application/json"},
            json={
                "model": cfg.get("model"),
                "temperature": float(cfg.get("temperature", 0) or 0),
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
            },
        )
        res.raise_for_status()
        data = res.json()
    return data["choices"][0]["message"]["content"]


async def _call_anthropic(cfg: dict[str, Any], prompt: str, payload: dict[str, Any]) -> str:
    url = _build_endpoint(str(cfg.get("base_url", "")), "/v1/messages")
    async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
        res = await client.post(
            url,
            headers={
                "x-api-key": cfg.get("api_key"),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg.get("model"),
                "max_tokens": 800,
                "temperature": float(cfg.get("temperature", 0) or 0),
                "system": prompt,
                "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            },
        )
        res.raise_for_status()
        data = res.json()
    parts = data.get("content") or []
    return "".join(part.get("text", "") for part in parts if part.get("type") == "text")


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("AI output is not a JSON object")
    return data


def _validate_ai_output(data: dict[str, Any]) -> dict[str, Any]:
    required = {
        "is_related": bool,
        "is_negative": bool,
        "risk_level": str,
        "reason": str,
        "evidence_quotes": list,
        "recommended_action": str,
    }
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError("AI 输出缺少字段：" + "、".join(missing))
    invalid = [key for key, expected_type in required.items() if not isinstance(data.get(key), expected_type)]
    if invalid:
        raise ValueError("AI 输出字段类型错误：" + "、".join(invalid))
    if _normalize_risk(data.get("risk_level")) != data.get("risk_level"):
        raise ValueError("AI 输出 risk_level 必须是 high、medium、low 或 irrelevant")
    return {
        "is_related": data["is_related"],
        "is_negative": data["is_negative"],
        "risk_level": data["risk_level"],
        "reason": data["reason"],
        "evidence_quotes": [str(item) for item in data["evidence_quotes"]],
        "recommended_action": data["recommended_action"],
    }


def _merge_test_config(payload: dict[str, Any]) -> dict[str, Any]:
    current = get_ai_config(masked=False)
    cfg = dict(current)
    for key in ("provider", "base_url", "api_key", "model", "temperature", "prompt"):
        value = payload.get(key)
        if value not in (None, ""):
            cfg[key] = value
    if cfg.get("provider") not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    cfg["temperature"] = validate_temperature(cfg.get("temperature", 0) or 0)
    missing = [key for key in ("base_url", "api_key", "model") if not cfg.get(key)]
    if missing:
        raise ValueError("AI 配置未完成：" + "、".join(missing))
    return cfg


def _build_endpoint(base_url: str, endpoint: str) -> str:
    base = base_url.rstrip("/")
    if not base:
        raise ValueError("base_url is required")
    endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    lower_base = base.lower()
    lower_endpoint = endpoint.lower()
    if lower_base.endswith(lower_endpoint):
        return base
    if lower_base.endswith("/v1") and lower_endpoint.startswith("/v1/"):
        return f"{base}{endpoint[3:]}"
    return f"{base}{endpoint}"


def _normalize_risk(value: Any) -> str:
    raw = str(value or "irrelevant").lower()
    return raw if raw in {"high", "medium", "low", "irrelevant"} else "irrelevant"


def _fallback(reason: str, content: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "pending_review",
        "is_related": True,
        "is_negative": False,
        "risk_level": "low",
        "reason": reason,
        "evidence_quotes": [content.get("title") or content.get("description") or ""],
        "recommended_action": "AI 未完成判断，请人工复核。",
        "raw_response": "",
    }
