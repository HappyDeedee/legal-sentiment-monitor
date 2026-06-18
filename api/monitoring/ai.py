from __future__ import annotations

import json
import os
import re
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx

from .database import get_active_ai_key_profile, get_ai_config, get_ai_key_profile, validate_temperature
from .prompts import DEFAULT_PROMPT
from .security import redact_sensitive


AI_CONNECTION_TEST_MESSAGE = "hi"
AI_CONNECTION_TEST_MAX_TOKENS = 1000


def ai_api_disabled() -> bool:
    return str(os.environ.get("MONITOR_SKIP_AI_API") or "").strip().lower() in {"1", "true", "yes", "on"}


async def evaluate_content(job: dict[str, Any], content: dict[str, Any], comments: list[dict[str, Any]]) -> dict[str, Any]:
    started_at = _trace_now()
    start_time = time.perf_counter()
    if ai_api_disabled():
        return _with_trace(
            _fallback("AI 服务未启用，本条内容待人工复核。", content),
            _build_trace_snapshot(
                job,
                content,
                comments,
                status="pending_review",
                started_at=started_at,
                start_time=start_time,
                error_message="AI 服务未启用，本条内容待人工复核。",
            ),
        )

    cfg = _job_ai_config(job)
    if not cfg.get("api_key") or not cfg.get("model") or not cfg.get("base_url"):
        return _with_trace(
            _fallback("AI 配置未完成", content),
            _build_trace_snapshot(
                job,
                content,
                comments,
                cfg=cfg,
                status="pending_review",
                started_at=started_at,
                start_time=start_time,
                error_message="AI 配置未完成",
            ),
        )

    prompt = cfg.get("prompt") or DEFAULT_PROMPT
    user_payload = build_evaluation_payload(job, content, comments)
    try:
        if cfg.get("provider") == "anthropic":
            raw = await _call_anthropic(cfg, prompt, user_payload)
            request_snapshot = _anthropic_request_snapshot(cfg, prompt, user_payload)
        else:
            raw = await _call_openai(cfg, prompt, user_payload)
            request_snapshot = _openai_request_snapshot(cfg, prompt, user_payload)
        data = _validate_ai_output(_parse_json(raw))
        data = _apply_target_evidence_gate(data, job, content, comments)
        result = {
            "status": "ok",
            "is_related": data["is_related"],
            "is_negative": data["is_negative"],
            "risk_level": data["risk_level"],
            "reason": data["reason"],
            "evidence_quotes": data["evidence_quotes"],
            "recommended_action": data["recommended_action"],
            "raw_response": raw,
        }
        return _with_trace(
            result,
            _build_trace_snapshot(
                job,
                content,
                comments,
                cfg=cfg,
                prompt=prompt,
                input_payload=user_payload,
                request_snapshot=request_snapshot,
                response_snapshot=raw,
                parsed_result=result,
                status="ok",
                started_at=started_at,
                start_time=start_time,
            ),
        )
    except Exception as exc:
        fallback = _fallback(f"AI 评估失败：{type(exc).__name__}: {_redact_ai_error(exc)}", content)
        return _with_trace(
            fallback,
            _build_trace_snapshot(
                job,
                content,
                comments,
                cfg=cfg,
                prompt=prompt,
                input_payload=user_payload,
                request_snapshot=_safe_request_snapshot(cfg, prompt, user_payload),
                parsed_result=fallback,
                status="pending_review",
                started_at=started_at,
                start_time=start_time,
                error_message=f"{type(exc).__name__}: {_redact_ai_error(exc)}",
            ),
        )


async def test_ai(payload: dict[str, Any]) -> dict[str, Any]:
    if ai_api_disabled():
        raise ValueError("AI 服务当前未启用；采集不受影响，内容会进入待人工复核。")

    cfg = _merge_test_config(payload)
    prompt = cfg.get("prompt") or DEFAULT_PROMPT
    sample = _sample_payload(payload)
    if cfg.get("provider") == "anthropic":
        raw = await _call_anthropic(cfg, prompt, sample)
    else:
        raw = await _call_openai(cfg, prompt, sample)
    data = _parse_json(raw)
    return _validate_ai_output(data)


async def test_ai_connection(payload: dict[str, Any]) -> dict[str, Any]:
    if ai_api_disabled():
        raise ValueError("AI 服务当前未启用；采集不受影响，内容会进入待人工复核。")

    cfg = _merge_test_config(payload)
    if cfg.get("provider") == "anthropic":
        raw_response = await _ping_anthropic(cfg)
        endpoint = _build_endpoint(str(cfg.get("base_url", "")), "/v1/messages")
    else:
        raw_response = await _ping_openai(cfg)
        endpoint = _build_endpoint(str(cfg.get("base_url", "")), "/v1/chat/completions")
    raw = _extract_model_text(raw_response) if isinstance(raw_response, (dict, list)) else str(raw_response or "")
    if not str(raw or "").strip():
        raise ValueError("模型服务已响应，但没有返回文本；返回结构：" + _compact_response_preview(raw_response))
    return {
        "ok": True,
        "provider": cfg.get("provider"),
        "protocol": cfg.get("provider"),
        "model": cfg.get("model"),
        "endpoint": endpoint,
        "message": "连接测试通过，模型已返回文本",
        "request_message": AI_CONNECTION_TEST_MESSAGE,
        "response_text": str(raw).strip(),
        "response_preview": str(raw).strip()[:200],
    }


async def list_ai_models(payload: dict[str, Any]) -> dict[str, Any]:
    if ai_api_disabled():
        raise ValueError("AI 服务当前未启用；暂不能获取模型列表。")

    cfg = _merge_model_list_config(payload)
    if cfg.get("provider") == "anthropic":
        endpoint, raw_response = await _fetch_anthropic_models(cfg)
    else:
        endpoint, raw_response = await _fetch_openai_models(cfg)
    models = _extract_model_ids(raw_response)
    if not models:
        raise ValueError("模型列表接口已响应，但没有返回模型名称；返回结构：" + _compact_response_preview(raw_response))
    return {
        "ok": True,
        "provider": cfg.get("provider"),
        "protocol": cfg.get("provider"),
        "endpoint": endpoint,
        "models": models,
        "count": len(models),
    }


def offline_check(payload: dict[str, Any]) -> dict[str, Any]:
    cfg = _merge_test_config(payload, require_api_key=False)
    endpoint = _build_endpoint(
        str(cfg.get("base_url", "")),
        "/v1/messages" if cfg.get("provider") == "anthropic" else "/v1/chat/completions",
    )
    prompt = cfg.get("prompt") or DEFAULT_PROMPT
    warnings = []
    if not cfg.get("api_key"):
        warnings.append("未填写 API Key；离线自检不会验证密钥是否可用")
    if ai_api_disabled():
        warnings.append("AI 服务当前未启用；采集评估会跳过外部 AI")
    return {
        "ok": True,
        "mode": "offline",
        "ai_api_disabled": ai_api_disabled(),
        "provider": cfg.get("provider"),
        "model": cfg.get("model"),
        "endpoint": endpoint,
        "temperature": cfg.get("temperature"),
        "api_key_present": bool(cfg.get("api_key")),
        "prompt_chars": len(prompt),
        "sample_payload": _sample_payload(payload),
        "expected_output_fields": [
            "is_related",
            "is_negative",
            "risk_level",
            "reason",
            "evidence_quotes",
            "recommended_action",
        ],
        "warnings": warnings,
    }


def _job_ai_config(job: dict[str, Any]) -> dict[str, Any]:
    global_config = get_ai_config(masked=False)
    profile_id = job.get("ai_profile_id")
    if profile_id:
        try:
            profile = get_ai_key_profile(int(profile_id), masked=False)
        except (TypeError, ValueError):
            profile = None
        if profile:
            profile["prompt"] = global_config.get("prompt") or DEFAULT_PROMPT
            return profile
    active = get_active_ai_key_profile(masked=False)
    if active:
        active["prompt"] = global_config.get("prompt") or DEFAULT_PROMPT
        return active
    return global_config


def _with_trace(result: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    merged = dict(result or {})
    merged["_ai_trace"] = trace
    return merged


def _build_trace_snapshot(
    job: dict[str, Any],
    content: dict[str, Any],
    comments: list[dict[str, Any]],
    *,
    cfg: dict[str, Any] | None = None,
    prompt: str | None = None,
    input_payload: dict[str, Any] | None = None,
    request_snapshot: dict[str, Any] | None = None,
    response_snapshot: Any | None = None,
    parsed_result: dict[str, Any] | None = None,
    status: str = "",
    started_at: str = "",
    start_time: float | None = None,
    error_message: str = "",
) -> dict[str, Any]:
    payload = input_payload or _trace_input_payload(job, content, comments)
    duration_ms = int(max(0, (time.perf_counter() - (start_time or time.perf_counter())) * 1000))
    return {
        "workspace_id": job.get("workspace_id") or 1,
        "run_id": content.get("run_id") or job.get("run_id") or 0,
        "raw_content_id": content.get("id") or 0,
        "attempt_index": 1,
        "status": status or "pending_review",
        "provider": (cfg or {}).get("provider", ""),
        "model": (cfg or {}).get("model", ""),
        "prompt_snapshot": prompt or (cfg or {}).get("prompt") or DEFAULT_PROMPT,
        "input_payload": payload,
        "request_snapshot": request_snapshot or _safe_request_snapshot(cfg or {}, prompt or DEFAULT_PROMPT, payload),
        "response_snapshot": response_snapshot or "",
        "parsed_result": parsed_result or {},
        "error_message": error_message or "",
        "duration_ms": duration_ms,
        "started_at": started_at,
        "finished_at": _trace_now(),
    }


def _trace_input_payload(job: dict[str, Any], content: dict[str, Any], comments: list[dict[str, Any]]) -> dict[str, Any]:
    payload = build_evaluation_payload(job, content, comments)
    payload["job_id"] = job.get("id")
    payload["run_id"] = content.get("run_id") or job.get("run_id")
    payload["raw_content_id"] = content.get("id")
    payload["evaluated_at"] = _trace_now()
    return payload


def _trace_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _openai_request_snapshot(cfg: dict[str, Any], prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "endpoint": _build_endpoint(str(cfg.get("base_url", "")), "/v1/chat/completions"),
        "headers": {"Authorization": "Bearer [REDACTED]", "Content-Type": "application/json"},
        "json": {
            "model": cfg.get("model"),
            "temperature": float(cfg.get("temperature", 0) or 0),
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        },
    }


def _anthropic_request_snapshot(cfg: dict[str, Any], prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "endpoint": _build_endpoint(str(cfg.get("base_url", "")), "/v1/messages"),
        "headers": {"x-api-key": "[REDACTED]", "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        "json": {
            "model": cfg.get("model"),
            "max_tokens": 800,
            "temperature": float(cfg.get("temperature", 0) or 0),
            "system": prompt,
            "messages": [{"role": "user", "content": _anthropic_text_content(json.dumps(payload, ensure_ascii=False))}],
        },
    }


def _safe_request_snapshot(cfg: dict[str, Any], prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        if cfg.get("provider") == "anthropic":
            return _anthropic_request_snapshot(cfg, prompt, payload)
        return _openai_request_snapshot(cfg, prompt, payload)
    except Exception:
        return {"provider": cfg.get("provider"), "model": cfg.get("model"), "snapshot_error": "request snapshot unavailable"}


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
    return _extract_model_text(data)


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
                "messages": [{"role": "user", "content": _anthropic_text_content(json.dumps(payload, ensure_ascii=False))}],
            },
        )
        res.raise_for_status()
        data = res.json()
    return _extract_model_text(data)


async def _ping_openai(cfg: dict[str, Any]) -> Any:
    url = _build_endpoint(str(cfg.get("base_url", "")), "/v1/chat/completions")
    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        res = await client.post(
            url,
            headers={"Authorization": f"Bearer {cfg.get('api_key')}", "Content-Type": "application/json"},
            json={
                "model": cfg.get("model"),
                "temperature": 0,
                "max_tokens": 32,
                "messages": [{"role": "user", "content": AI_CONNECTION_TEST_MESSAGE}],
            },
        )
        res.raise_for_status()
        return res.json()


async def _ping_anthropic(cfg: dict[str, Any]) -> Any:
    url = _build_endpoint(str(cfg.get("base_url", "")), "/v1/messages")
    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        res = await client.post(
            url,
            headers={
                "x-api-key": cfg.get("api_key"),
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg.get("model"),
                "max_tokens": AI_CONNECTION_TEST_MAX_TOKENS,
                "temperature": 0,
                "messages": [{"role": "user", "content": _anthropic_text_content(AI_CONNECTION_TEST_MESSAGE)}],
            },
        )
        res.raise_for_status()
        return res.json()


async def _fetch_openai_models(cfg: dict[str, Any]) -> tuple[str, Any]:
    headers = {"Authorization": f"Bearer {cfg.get('api_key')}", "Content-Type": "application/json"}
    return await _fetch_models_from_candidates(str(cfg.get("base_url", "")), headers)


async def _fetch_anthropic_models(cfg: dict[str, Any]) -> tuple[str, Any]:
    api_key = cfg.get("api_key")
    headers = {
        "x-api-key": api_key,
        "Authorization": f"Bearer {api_key}",
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    return await _fetch_models_from_candidates(str(cfg.get("base_url", "")), headers)


async def _fetch_models_from_candidates(base_url: str, headers: dict[str, str]) -> tuple[str, Any]:
    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
        for url in _model_endpoint_candidates(base_url):
            try:
                res = await client.get(url, headers=headers)
                res.raise_for_status()
                return url, res.json()
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code in {404, 405}:
                    continue
                raise
    if last_error:
        raise last_error
    raise ValueError("AI 接入未配置完整：base_url")


def _anthropic_text_content(text: str) -> list[dict[str, str]]:
    return [{"type": "text", "text": text}]


def _extract_model_text(data: Any) -> str:
    texts: list[str] = []

    def collect(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                texts.append(value.strip())
            return
        if isinstance(value, list):
            for item in value:
                collect(item)
            return
        if not isinstance(value, dict):
            return
        for key in ("text", "output_text", "completion", "answer"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                texts.append(raw.strip())
        message = value.get("message")
        if isinstance(message, dict):
            collect(message.get("content"))
        elif isinstance(message, str):
            collect(message)
        content = value.get("content")
        if content is not None:
            collect(content)
        delta = value.get("delta")
        if isinstance(delta, dict):
            collect(delta.get("content"))

    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                collect(choice)
        collect(data.get("content"))
        for key in ("output", "output_text", "text", "completion", "answer", "message"):
            collect(data.get(key))
    else:
        collect(data)
    deduped: list[str] = []
    for text in texts:
        if text not in deduped:
            deduped.append(text)
    return "\n".join(deduped).strip()


def _compact_response_preview(data: Any, limit: int = 800) -> str:
    try:
        text = json.dumps(data, ensure_ascii=False)
    except TypeError:
        text = str(data)
    text = redact_sensitive(text)
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:limit] + "...") if len(text) > limit else (text or "空响应")


def _extract_model_ids(data: Any) -> list[str]:
    models: list[str] = []

    def collect(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str):
            if value.strip():
                models.append(value.strip())
            return
        if isinstance(value, list):
            for item in value:
                collect(item)
            return
        if not isinstance(value, dict):
            return
        for key in ("id", "name", "model"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                models.append(raw.strip())
                return
        for key in ("data", "models", "items"):
            collect(value.get(key))

    collect(data)
    deduped: list[str] = []
    for model in models:
        if model not in deduped:
            deduped.append(model)
    return deduped


def _parse_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    fenced = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    candidates = fenced + [text]
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            data = json.loads(_extract_json_object(candidate))
            break
        except Exception as exc:
            last_error = exc
    else:
        raise ValueError(f"AI output is not valid JSON: {last_error}") from last_error
    if not isinstance(data, dict):
        raise ValueError("AI output is not a JSON object")
    return data


def _validate_ai_output(data: dict[str, Any]) -> dict[str, Any]:
    data = _unwrap_ai_output(data)
    required = {"is_related", "is_negative", "risk_level", "reason", "evidence_quotes", "recommended_action"}
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError("AI 输出缺少字段：" + "、".join(missing))
    is_related = _coerce_bool(data.get("is_related"), "is_related")
    is_negative = _coerce_bool(data.get("is_negative"), "is_negative")
    risk_level = _coerce_risk(data.get("risk_level"))
    return {
        "is_related": is_related,
        "is_negative": is_negative,
        "risk_level": risk_level,
        "reason": str(data.get("reason") or ""),
        "evidence_quotes": _coerce_quotes(data.get("evidence_quotes")),
        "recommended_action": str(data.get("recommended_action") or ""),
    }


def _apply_target_evidence_gate(
    data: dict[str, Any],
    job: dict[str, Any],
    content: dict[str, Any],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    if not data.get("is_related") and not data.get("is_negative"):
        return data
    if _has_target_evidence(job, content, comments):
        return data
    adjusted = dict(data)
    adjusted["is_related"] = False
    adjusted["is_negative"] = False
    adjusted["risk_level"] = "irrelevant"
    reason = str(adjusted.get("reason") or "").strip()
    guardrail = "未在标题、正文、作者或已采集评论中找到目标律所/别名证据；搜索词仅作为召回来源。"
    adjusted["reason"] = f"{guardrail} 原模型理由：{reason}" if reason else guardrail
    adjusted["recommended_action"] = "作为召回噪声处理；如原文另有目标律所证据，请人工复核。"
    adjusted["evidence_quotes"] = _filter_target_evidence_quotes(adjusted.get("evidence_quotes"), job, content, comments)
    return adjusted


def _has_target_evidence(job: dict[str, Any], content: dict[str, Any], comments: list[dict[str, Any]]) -> bool:
    terms = _target_terms(job)
    if not terms:
        return False
    evidence_text = "\n".join(
        [
            str(content.get("title") or ""),
            str(content.get("description") or ""),
            str(content.get("author_name") or ""),
            *[str(comment.get("content") or "") for comment in comments if str(comment.get("content") or "").strip()],
            *[str(comment.get("author_name") or "") for comment in comments if str(comment.get("author_name") or "").strip()],
        ]
    )
    normalized_text = _normalize_evidence_text(evidence_text)
    if not normalized_text:
        return False
    return any(term in normalized_text for term in terms)


def _target_terms(job: dict[str, Any]) -> list[str]:
    raw_terms: list[Any] = [job.get("law_firm_name")]
    aliases = job.get("aliases") or []
    if isinstance(aliases, str):
        raw_terms.extend(re.split(r"[,，;；\s]+", aliases))
    elif isinstance(aliases, list):
        raw_terms.extend(aliases)
    terms: list[str] = []
    for raw in raw_terms:
        normalized = _normalize_evidence_text(str(raw or ""))
        if len(normalized) >= 2 and normalized not in terms:
            terms.append(normalized)
    return terms


def _normalize_evidence_text(value: str) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower()


def _filter_target_evidence_quotes(
    value: Any,
    job: dict[str, Any],
    content: dict[str, Any],
    comments: list[dict[str, Any]],
) -> list[str]:
    quotes = _coerce_quotes(value)
    terms = _target_terms(job)
    if not terms:
        return []
    allowed_text = _normalize_evidence_text(
        "\n".join(
            [
                str(content.get("title") or ""),
                str(content.get("description") or ""),
                str(content.get("author_name") or ""),
                *[str(comment.get("content") or "") for comment in comments if str(comment.get("content") or "").strip()],
                *[str(comment.get("author_name") or "") for comment in comments if str(comment.get("author_name") or "").strip()],
            ]
        )
    )
    filtered = []
    for quote in quotes:
        normalized = _normalize_evidence_text(quote)
        if normalized and normalized in allowed_text and any(term in normalized for term in terms):
            filtered.append(quote)
    return filtered


def _extract_json_object(text: str) -> str:
    cleaned = text.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def _unwrap_ai_output(data: dict[str, Any]) -> dict[str, Any]:
    required = {"is_related", "is_negative", "risk_level", "reason", "evidence_quotes", "recommended_action"}
    if required & set(data):
        return data
    for key in ("result", "data", "evaluation", "output"):
        nested = data.get(key)
        if isinstance(nested, dict) and required & set(nested):
            return nested
    return data


def _coerce_bool(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        truthy = {"true", "1", "yes", "y", "是", "相关", "有关", "负面", "疑似负面"}
        falsy = {"false", "0", "no", "n", "否", "不相关", "无关", "非负面", "不是"}
        if normalized in truthy:
            return True
        if normalized in falsy:
            return False
    raise ValueError(f"AI 输出字段类型错误：{field}")


def _coerce_risk(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    mapping = {
        "high": "high",
        "高": "high",
        "高风险": "high",
        "medium": "medium",
        "middle": "medium",
        "中": "medium",
        "中风险": "medium",
        "low": "low",
        "低": "low",
        "低风险": "low",
        "irrelevant": "irrelevant",
        "none": "irrelevant",
        "无": "irrelevant",
        "无关": "irrelevant",
        "不相关": "irrelevant",
    }
    if normalized not in mapping:
        raise ValueError("AI 输出 risk_level 必须是 high、medium、low 或 irrelevant")
    return mapping[normalized]


def _coerce_quotes(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value] if value.strip() else []
    raise ValueError("AI 输出字段类型错误：evidence_quotes")


def _sample_payload(payload: dict[str, Any]) -> dict[str, Any]:
    platform_code = str(payload.get("sample_platform") or "dy").strip()
    platform_labels = {"dy": "抖音", "ks": "快手", "xhs": "小红书"}
    if platform_code not in platform_labels:
        platform_code = "dy"
    law_firm_name = str(payload.get("sample_law_firm_name") or "海安律所").strip() or "海安律所"
    source_keyword = str(payload.get("sample_source_keyword") or "海安律所避雷").strip() or "海安律所避雷"
    comments = _sample_comments(payload)
    return build_evaluation_payload(
        {
            "law_firm_name": law_firm_name,
            "aliases": ["海安律师事务所", "海安律师"],
            "exclude_words": [],
        },
        {
            "platform": platform_code,
            "platform_label": platform_labels[platform_code],
            "source_keyword": source_keyword,
            "title": payload.get("sample_title") or "海安律所避雷：退费拖了很久",
            "description": payload.get("sample_text") or "我想曝光一下，沟通很差，收费也不透明，投诉后一直没人处理。",
            "author_name": "海安用户",
            "content_url": "https://www.douyin.com/video/haian-selftest",
            "cover_url": "https://example.com/haian-cover.jpg",
            "publish_time": 1781280000,
            "comment_count": len(comments),
        },
        comments,
    )


def _sample_comments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "sample_comments" not in payload:
        items = ["我也遇到退费慢的问题", "建议先保留沟通证据再投诉"]
    else:
        raw = payload.get("sample_comments")
        if isinstance(raw, list):
            items = []
            for item in raw:
                if isinstance(item, dict):
                    text = str(item.get("content") or item.get("text") or "").strip()
                else:
                    text = str(item or "").strip()
                if text:
                    items.append(text)
        else:
            text = str(raw or "")
            for sep in ("；", ";"):
                text = text.replace(sep, "\n")
            items = [line.strip() for line in text.splitlines() if line.strip()]
    return [
        {"content": content, "author_name": f"评论用户{index + 1}", "create_time": 1781280100 + index * 100}
        for index, content in enumerate(items[:10])
    ]


def build_evaluation_payload(
    job: dict[str, Any],
    content: dict[str, Any],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    comment_samples = [
        {
            "content": str(comment.get("content") or "")[:500],
            "author_name": comment.get("author_name") or "",
            "create_time": comment.get("create_time"),
        }
        for comment in comments[:10]
        if str(comment.get("content") or "").strip()
    ]
    comments_text = [item["content"] for item in comment_samples]
    comment_total = _safe_int(content.get("comment_count"))
    observed_total = len([comment for comment in comments if str(comment.get("content") or "").strip()])
    return {
        "law_firm_name": job.get("law_firm_name"),
        "aliases": job.get("aliases", []),
        "exclude_words": job.get("exclude_words", []),
        "platform": content.get("platform_label") or content.get("platform"),
        "platform_code": content.get("platform"),
        "source_keyword": content.get("source_keyword"),
        "title": content.get("title"),
        "description": content.get("description"),
        "author_name": content.get("author_name"),
        "content_url": content.get("content_url"),
        "cover_url": content.get("cover_url"),
        "publish_time": content.get("publish_time"),
        "comment_count": comment_total,
        "comments": comments_text,
        "comment_samples": comment_samples,
        "comment_summary": {
            "declared_count": comment_total,
            "observed_count": observed_total,
            "sample_count": len(comment_samples),
            "sample_text": "；".join(comments_text[:5]),
        },
    }


def _safe_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def _merge_test_config(payload: dict[str, Any], require_api_key: bool = True) -> dict[str, Any]:
    global_config = get_ai_config(masked=False)
    active_profile = get_active_ai_key_profile(masked=False)
    cfg = dict(active_profile or global_config)
    if active_profile:
        cfg["prompt"] = global_config.get("prompt") or DEFAULT_PROMPT
    for key in ("provider", "base_url", "api_key", "model", "temperature", "prompt"):
        value = payload.get(key)
        if value not in (None, ""):
            cfg[key] = value
    if cfg.get("provider") not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    cfg["temperature"] = validate_temperature(cfg.get("temperature", 0) or 0)
    required = ["base_url", "model"]
    if require_api_key:
        required.append("api_key")
    missing = [key for key in required if not cfg.get(key)]
    if missing:
        raise ValueError("AI 配置未完成：" + "、".join(missing))
    return cfg


def _merge_model_list_config(payload: dict[str, Any]) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    for key in ("provider", "base_url", "api_key"):
        value = payload.get(key)
        if value is not None:
            cfg[key] = str(value).strip()
    cfg["provider"] = cfg.get("provider") or "openai"
    if cfg.get("provider") not in {"openai", "anthropic"}:
        raise ValueError("invalid AI provider")
    missing = [key for key in ("base_url", "api_key") if not cfg.get(key)]
    if missing:
        raise ValueError("AI 接入未配置完整：" + "、".join(missing))
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


def _model_endpoint_candidates(base_url: str) -> list[str]:
    base = base_url.rstrip("/")
    candidates = [
        _build_endpoint(base, "/v1/models"),
        _build_endpoint(base, "/models"),
    ]
    parsed = urlsplit(base)
    path = parsed.path.rstrip("/")
    if path:
        parent_path = path.rsplit("/", 1)[0]
        parent_base = urlunsplit((parsed.scheme, parsed.netloc, parent_path, "", ""))
        if parent_base and parent_base != base:
            candidates.extend([
                _build_endpoint(parent_base, "/models"),
                _build_endpoint(parent_base, "/v1/models"),
            ])
    deduped: list[str] = []
    for candidate in candidates:
        if candidate not in deduped:
            deduped.append(candidate)
    return deduped


def _normalize_risk(value: Any) -> str:
    raw = str(value or "irrelevant").lower()
    return raw if raw in {"high", "medium", "low", "irrelevant"} else "irrelevant"


def _redact_ai_error(exc: Exception) -> str:
    text = redact_sensitive(str(exc))
    return re.sub(r"https?://[^\s'\"<>]+", "[AI_ENDPOINT_REDACTED]", text)


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
