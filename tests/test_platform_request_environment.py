from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.browser_environment import BrowserEnvironmentPlan, BrowserEnvironmentResult
from tools.platform_request_environment import (
    REQUEST_BINDING_ENV_NAME,
    REQUEST_RESULT_PATH_ENV_NAME,
    PlatformRequestEnvironmentError,
    build_platform_request_binding,
    build_platform_request_environment,
    build_platform_request_environment_from_binding,
    establish_platform_request_environment,
    platform_request_binding_from_json,
    platform_request_binding_to_json,
    platform_request_environment_from_json,
    read_platform_request_environment,
    platform_request_environment_to_json,
    request_binding_from_environment,
    reset_platform_request_environment_cache_for_tests,
    write_platform_request_environment,
)


def _plan() -> BrowserEnvironmentPlan:
    return BrowserEnvironmentPlan(
        contract_version=1,
        resolution_id="resolution-test-1",
        attempt_id="attempt-test-1",
        action="crawl",
        trigger_source="manual",
        workspace_id=1,
        account_id=8972,
        platform="dy",
        identity_state="active",
        identity_template="WIN_CHROME",
        browser_executable_path=r"C:\runtime\chromium.exe",
        browser_family="chromium",
        browser_source="playwright_bundled",
        browser_version="127.0.6533.17",
        profile_key="1/dy/acc_8972",
        profile_path=r"C:\runtime\profiles\1\dy\acc_8972",
        profile_mode="persistent",
        proxy_policy="direct",
        proxy_id=None,
        proxy_region="CN_MAINLAND",
        proxy_url="",
        browser_platform="windows",
        user_agent="Mozilla/5.0 Chrome/127.0.6533.17",
        timezone="Asia/Shanghai",
        locale="zh-CN",
        accept_language="zh-CN,zh;q=0.9",
        screen_width=1920,
        screen_height=1080,
        viewport_width=1920,
        viewport_height=947,
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        provider_name="playwright",
        launch_mode="cdp_launch",
        headless=True,
    )


def _result(plan: BrowserEnvironmentPlan, *, fallback_used: bool = False) -> BrowserEnvironmentResult:
    effective = {
        "user_agent": plan.user_agent,
        "timezone": plan.timezone,
        "locale": plan.locale,
        "accept_language": plan.accept_language,
        "screen_width": plan.screen_width,
        "screen_height": plan.screen_height,
        "viewport_width": plan.viewport_width,
        "viewport_height": plan.viewport_height,
        "device_scale_factor": 1.0,
        "is_mobile": False,
        "has_touch": False,
        "proxy_region_snapshot": plan.proxy_region,
    }
    snapshot = {
        "contract_version": 1,
        "resolution_id": plan.resolution_id,
        "attempt_id": plan.attempt_id,
        "action": plan.action,
        "trigger_source": plan.trigger_source,
        "account": {
            "workspace_id": plan.workspace_id,
            "account_id": plan.account_id,
            "platform": plan.platform,
            "identity_state": plan.identity_state,
        },
        "browser": {
            "family": plan.browser_family,
            "version": plan.browser_version,
            "source": plan.browser_source,
        },
        "profile": {"profile_key": plan.profile_key, "mode": plan.profile_mode},
        "proxy": {
            "policy": plan.proxy_policy,
            "proxy_id": plan.proxy_id,
            "region": plan.proxy_region,
            "effect_proof": "not_applicable",
        },
        "requested": {
            "identity_template": plan.identity_template,
            "browser_platform": plan.browser_platform,
            "user_agent": plan.user_agent,
            "timezone": plan.timezone,
            "locale": plan.locale,
            "accept_language": plan.accept_language,
            "screen_width": plan.screen_width,
            "screen_height": plan.screen_height,
            "viewport_width": plan.viewport_width,
            "viewport_height": plan.viewport_height,
            "device_scale_factor": 1.0,
            "is_mobile": False,
            "has_touch": False,
            "proxy_region_snapshot": plan.proxy_region,
        },
        "effective": effective,
        "provider": {"name": "playwright", "mode": "cdp_launch", "version": "1.45.0"},
        "probes": {
            "navigator_user_agent": plan.user_agent,
            "navigator_language": plan.locale,
            "navigator_languages": ["zh-CN", "zh"],
            "timezone": plan.timezone,
            "screen_width": plan.screen_width,
            "screen_height": plan.screen_height,
            "viewport_width": plan.viewport_width,
            "viewport_height": plan.viewport_height,
            "device_scale_factor": 1.0,
            "max_touch_points": 0,
            "is_mobile": False,
            "webdriver": True,
        },
        "unsupported_fields": ["canvas", "webgl", "fonts", "plugins"],
        "mismatch_evidence": [],
        "fallback_used": fallback_used,
        "ok": True,
        "reason": "",
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    return BrowserEnvironmentResult(ok=True, reason="", snapshot=snapshot)


def _build(plan: BrowserEnvironmentPlan | None = None, result: BrowserEnvironmentResult | None = None):
    plan = plan or _plan()
    result = result or _result(plan)
    created = datetime.now(timezone.utc)
    return build_platform_request_environment(
        plan,
        result,
        run_id=12001,
        identity_revision="identity-rev-1",
        cookie_material_revision="cookie-material-rev-1",
        created_at=created.isoformat(),
        expires_at=(created + timedelta(minutes=15)).isoformat(),
    )


def test_cr129_packet_a_projects_safe_immutable_request_environment():
    environment = _build()

    assert environment.account_id == 8972
    assert environment.platform == "dy"
    assert environment.profile_key == "1/dy/acc_8972"
    assert environment.resolution_id == "resolution-test-1"
    assert environment.attempt_id == "attempt-test-1"
    assert environment.run_id == 12001
    assert environment.fallback_used is False
    safe = environment.to_safe_dict()
    encoded = json.dumps(safe, ensure_ascii=False)
    assert "profile_path" not in encoded
    assert "proxy_url" not in encoded
    assert "Cookie" not in encoded
    assert "sessionid=synthetic-secret" not in encoded
    assert "C:\\runtime" not in encoded


@pytest.mark.parametrize(
    ("executable", "expected_channel"),
    [
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "chrome"),
        (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "edge"),
        (r"C:\runtime\Chromium\chrome.exe", "chromium"),
    ],
)
def test_cr129_packet_b_explicit_browser_channel_is_derived_without_persisting_path(
    executable,
    expected_channel,
):
    plan = replace(
        _plan(),
        browser_source="explicit",
        browser_executable_path=executable,
    )
    environment = _build(plan, _result(plan))

    assert environment.browser_channel == expected_channel
    assert executable not in json.dumps(environment.to_safe_dict())


def test_cr129_packet_a_rejects_result_account_or_resolution_drift():
    plan = _plan()
    mismatched = json.loads(json.dumps(_result(plan).snapshot))
    mismatched["account"]["account_id"] = 9196
    with pytest.raises(PlatformRequestEnvironmentError, match="account"):
        _build(plan, BrowserEnvironmentResult(ok=True, reason="", snapshot=mismatched))

    stale = json.loads(json.dumps(_result(plan).snapshot))
    stale["resolution_id"] = "resolution-other"
    with pytest.raises(PlatformRequestEnvironmentError, match="resolution"):
        _build(plan, BrowserEnvironmentResult(ok=True, reason="", snapshot=stale))


def test_cr129_packet_a_rejects_fallback_or_missing_revision():
    plan = _plan()
    with pytest.raises(PlatformRequestEnvironmentError, match="fallback"):
        _build(plan, _result(plan, fallback_used=True))

    with pytest.raises(PlatformRequestEnvironmentError, match="cookie_material_revision"):
        build_platform_request_environment(
            plan,
            _result(plan),
            run_id=12001,
            identity_revision="identity-rev-1",
            cookie_material_revision="",
            created_at="2026-07-22T10:00:00+00:00",
            expires_at="2026-07-22T10:15:00+00:00",
        )


def test_cr129_packet_a_safe_roundtrip_and_expiry_guard():
    environment = _build()
    restored = platform_request_environment_from_json(platform_request_environment_to_json(environment))
    assert restored == environment

    expired = environment.to_safe_dict()
    expired["expires_at"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    with pytest.raises(PlatformRequestEnvironmentError, match="expired"):
        platform_request_environment_from_json(json.dumps(expired, ensure_ascii=False))


def test_cr129_packet_a_rejects_cross_attempt_request_binding():
    environment = _build()
    with pytest.raises(PlatformRequestEnvironmentError, match="attempt"):
        environment.assert_request_binding(
            account_id=environment.account_id,
            platform=environment.platform,
            profile_key=environment.profile_key,
            resolution_id=environment.resolution_id,
            attempt_id="attempt-other",
            proxy_revision=environment.proxy_revision,
            identity_revision=environment.identity_revision,
            cookie_material_revision=environment.cookie_material_revision,
        )


def test_cr129_packet_a_safe_parent_binding_projects_child_environment(monkeypatch):
    plan = _plan()
    binding = build_platform_request_binding(
        plan,
        run_id=12001,
        identity_revision="identity-rev-1",
        cookie_material_revision="cookie-material-rev-1",
        proxy_revision="proxy-rev-1",
        created_at="2026-07-22T10:00:00+00:00",
        expires_at="2026-07-22T10:15:00+00:00",
    )
    payload = platform_request_binding_to_json(binding)
    assert platform_request_binding_from_json(payload) == binding
    assert "profile_path" not in payload
    assert "proxy_url" not in payload
    assert r"C:\runtime" not in payload

    reset_platform_request_environment_cache_for_tests()
    monkeypatch.setenv(REQUEST_BINDING_ENV_NAME, payload)
    restored = request_binding_from_environment(required=True)
    assert restored == binding
    assert REQUEST_BINDING_ENV_NAME not in os.environ

    environment = build_platform_request_environment_from_binding(
        plan,
        _result(plan),
        restored,
    )
    assert environment.run_id == 12001
    assert environment.proxy_revision == "proxy-rev-1"


def test_cr129_packet_a_binding_rejects_stale_browser_attempt():
    plan = _plan()
    binding = build_platform_request_binding(
        plan,
        run_id=12001,
        identity_revision="identity-rev-1",
        cookie_material_revision="cookie-material-rev-1",
        proxy_revision="proxy-rev-1",
    )
    stale = json.loads(platform_request_binding_to_json(binding))
    stale["attempt_id"] = "attempt-other"
    stale_binding = platform_request_binding_from_json(json.dumps(stale))

    with pytest.raises(PlatformRequestEnvironmentError, match="attempt_id"):
        build_platform_request_environment_from_binding(
            plan,
            _result(plan),
            stale_binding,
        )


def test_cr129_packet_a_request_proof_file_is_safe_and_bound(tmp_path, monkeypatch):
    environment = _build()
    destination = tmp_path / "attempt" / "request-environment.json"
    destination.parent.mkdir(parents=True)
    monkeypatch.setenv(REQUEST_RESULT_PATH_ENV_NAME, str(destination))

    write_platform_request_environment(environment)
    restored = read_platform_request_environment(destination)

    assert restored == environment
    payload = destination.read_text(encoding="utf-8")
    assert "profile_path" not in payload
    assert "proxy_url" not in payload
    assert r"C:\runtime" not in payload


def test_cr129_packet_a_runner_handoff_includes_only_safe_request_binding(tmp_path):
    from api.monitoring import runner

    plan = _plan()
    account_binding = {
        "account_id": plan.account_id,
        "platform": plan.platform,
        "login_type": "qrcode",
        "profile_key": plan.profile_key,
        "profile_path": plan.profile_path,
        "proxy_id": None,
        "proxy_url": "",
        "_account": {
            "id": plan.account_id,
            "workspace_id": plan.workspace_id,
            "platform": plan.platform,
            "profile_key": plan.profile_key,
            "identity_generator_version": "1.1",
            "identity_environment_version": "v2",
            "profile_runtime_version": 2,
            "cookie_source": "browser_sync",
        },
    }
    binding = runner._build_request_binding_for_attempt(
        account_binding,
        plan,
        run_id=12001,
        expires_at="2026-07-22T10:15:00+00:00",
        created_at="2026-07-22T10:00:00+00:00",
    )
    browser_result = tmp_path / "browser-result.json"
    request_result = tmp_path / "request-result.json"
    env = runner._build_crawler_env(
        account_binding,
        plan,
        browser_result,
        request_binding=binding,
        request_result_path=request_result,
    )

    restored = platform_request_binding_from_json(env[REQUEST_BINDING_ENV_NAME])
    assert restored.account_id == plan.account_id
    assert restored.attempt_id == plan.attempt_id
    assert env[REQUEST_RESULT_PATH_ENV_NAME] == str(request_result.resolve())
    safe_payload = env[REQUEST_BINDING_ENV_NAME]
    assert plan.profile_path not in safe_payload
    assert "profile_path" not in safe_payload
    assert "proxy_url" not in safe_payload


def test_cr129_packet_a_child_establishes_and_writes_current_environment(tmp_path, monkeypatch):
    plan = _plan()
    now = datetime.now(timezone.utc)
    binding = build_platform_request_binding(
        plan,
        run_id=12001,
        identity_revision="identity-rev-current",
        cookie_material_revision="cookie-material-rev-current",
        proxy_revision="proxy-rev-current",
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=15)).isoformat(),
    )
    destination = tmp_path / "request-environment.json"
    reset_platform_request_environment_cache_for_tests()
    monkeypatch.setenv(REQUEST_BINDING_ENV_NAME, platform_request_binding_to_json(binding))
    monkeypatch.setenv(REQUEST_RESULT_PATH_ENV_NAME, str(destination))

    environment = establish_platform_request_environment(plan, _result(plan))

    assert environment == read_platform_request_environment(destination)
    assert REQUEST_BINDING_ENV_NAME not in os.environ
    assert environment.run_id == binding.run_id
    assert environment.attempt_id == binding.attempt_id


def test_cr129_packet_a_runner_loads_only_current_bound_child_proof(tmp_path):
    from api.monitoring import runner

    plan = _plan()
    now = datetime.now(timezone.utc)
    binding = build_platform_request_binding(
        plan,
        run_id=12001,
        identity_revision="identity-rev-current",
        cookie_material_revision="cookie-material-rev-current",
        proxy_revision="proxy-rev-current",
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=15)).isoformat(),
    )
    environment = build_platform_request_environment_from_binding(
        plan,
        _result(plan),
        binding,
    )
    destination = tmp_path / "request-environment.json"
    destination.write_text(
        platform_request_environment_to_json(environment),
        encoding="utf-8",
    )

    restored = runner._load_managed_child_request_environment(
        destination,
        plan,
        binding,
    )
    assert restored == environment

    stale_payload = restored.to_safe_dict()
    stale_payload["attempt_id"] = "attempt-stale"
    destination.write_text(json.dumps(stale_payload), encoding="utf-8")
    with pytest.raises(PlatformRequestEnvironmentError, match="attempt"):
        runner._load_managed_child_request_environment(destination, plan, binding)


def test_cr129_packet_a_request_proof_order_rejects_late_attempt_result():
    from api.monitoring import runner

    existing = [
        {
            "attempt": 2,
            "status": "validated",
            "proof": {"attempt_id": "attempt-2"},
        }
    ]
    with pytest.raises(RuntimeError, match="stale"):
        runner._merge_request_environment_attempt(
            existing,
            {
                "attempt": 1,
                "status": "validated",
                "proof": {"attempt_id": "attempt-1"},
            },
        )

    merged = runner._merge_request_environment_attempt(
        existing,
        {
            "attempt": 2,
            "status": "validated",
            "proof": {"attempt_id": "attempt-2"},
        },
    )
    assert [item["attempt"] for item in merged] == [2]


def test_cr129_packet_a_safe_request_channels_reject_synthetic_secret_material(tmp_path):
    from api.monitoring import runner

    plan = _plan()
    account_binding = {
        "account_id": plan.account_id,
        "platform": plan.platform,
        "login_type": "qrcode",
        "profile_key": plan.profile_key,
        "profile_path": plan.profile_path,
        "proxy_id": None,
        "_account": {
            "id": plan.account_id,
            "workspace_id": plan.workspace_id,
            "platform": plan.platform,
            "profile_key": plan.profile_key,
            "cookie_source": "browser_sync",
        },
    }
    binding = runner._build_request_binding_for_attempt(
        account_binding,
        plan,
        run_id=12001,
    )
    binding_payload = platform_request_binding_to_json(binding)
    proof_payload = platform_request_environment_to_json(_build())
    for payload in (binding_payload, proof_payload):
        assert "sessionid=synthetic-secret" not in payload
        assert "msToken=synthetic-secret" not in payload
        assert "proxy-password-synthetic" not in payload
        assert "ws://synthetic-cdp" not in payload
        assert "X-S: synthetic-signature" not in payload


def test_cr129_packet_a_concurrent_account_projections_stay_isolated():
    from concurrent.futures import ThreadPoolExecutor
    from dataclasses import replace

    first = _plan()
    second = replace(
        first,
        account_id=9196,
        profile_key="1/xhs/acc_9196",
        platform="xhs",
        resolution_id="resolution-test-2",
        attempt_id="attempt-test-2",
    )

    def project(plan):
        return _build(plan, _result(plan))

    with ThreadPoolExecutor(max_workers=2) as pool:
        environments = list(pool.map(project, (first, second)))

    assert {(item.account_id, item.platform, item.profile_key) for item in environments} == {
        (8972, "dy", "1/dy/acc_8972"),
        (9196, "xhs", "1/xhs/acc_9196"),
    }


@pytest.mark.parametrize(
    ("module_name", "crawler_name", "factory_name", "client_name"),
    [
        ("media_platform.douyin.core", "DouYinCrawler", "create_douyin_client", "DouYinClient"),
        ("media_platform.xhs.core", "XiaoHongShuCrawler", "create_xhs_client", "XiaoHongShuClient"),
    ],
)
def test_cr129_packet_a_platform_client_receives_verified_request_environment(
    module_name,
    crawler_name,
    factory_name,
    client_name,
    monkeypatch,
):
    import asyncio
    import importlib

    module = importlib.import_module(module_name)
    crawler = getattr(module, crawler_name).__new__(getattr(module, crawler_name))
    plan = _plan()
    if module_name.endswith("xhs.core"):
        plan = replace(
            plan,
            account_id=9196,
            platform="xhs",
            profile_key="1/xhs/acc_9196",
        )
    environment = _build(plan, _result(plan))
    crawler.platform_request_environment = environment
    crawler.browser_environment_plan = plan
    crawler.user_agent = environment.user_agent
    crawler.browser_context = object()
    crawler.context_page = object()
    crawler.cookie_urls = ["https://synthetic.invalid"]
    crawler.index_url = "https://synthetic.invalid"
    crawler.ip_proxy_pool = None
    captured = {}

    async def fake_cookies(*args, **kwargs):
        if module_name.endswith("xhs.core"):
            return "a1=synthetic-a1;web_session=synthetic-session", {
                "a1": "synthetic-a1",
                "web_session": "synthetic-session",
            }
        return "synthetic=1", {"synthetic": "1"}

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(module.utils, "convert_browser_context_cookies", fake_cookies)
    monkeypatch.setattr(module, client_name, FakeClient)
    if module_name.endswith("douyin.core"):
        async def fake_evaluate(*args, **kwargs):
            return environment.user_agent

        crawler.context_page = type("Page", (), {"evaluate": fake_evaluate})()

    asyncio.run(getattr(crawler, factory_name)(None))

    assert captured["request_environment"] is environment
    if module_name.endswith("xhs.core"):
        assert captured["request_identity"].environment is environment
        assert 'v="127"' in captured["headers"]["sec-ch-ua"]
        assert 'v="136"' not in captured["headers"]["sec-ch-ua"]


def test_cr129_packet_a_xhs_signed_cookie_cannot_change_before_dispatch(monkeypatch):
    import asyncio

    from media_platform.xhs.client import XiaoHongShuClient

    plan = replace(
        _plan(),
        account_id=9196,
        platform="xhs",
        profile_key="1/xhs/acc_9196",
    )
    environment = _build(plan, _result(plan))
    client = XiaoHongShuClient(
        proxy=None,
        headers={
            "User-Agent": environment.user_agent,
            "accept-language": environment.accept_language,
            "sec-ch-ua": '"Chromium";v="127", "Not.A/Brand";v="99"',
            "Cookie": "a1=synthetic-a1;web_session=synthetic-session",
        },
        playwright_page=object(),
        cookie_dict={"a1": "synthetic-a1", "web_session": "synthetic-session"},
        request_environment=environment,
    )
    monkeypatch.setattr(
        "media_platform.xhs.client.sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-s",
            "x-t": "synthetic-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    signed = asyncio.run(client._pre_headers("/synthetic", params={"q": "1"}))
    signed["Cookie"] = "sessionid=changed"
    with pytest.raises(Exception, match="Cookie changed"):
        asyncio.run(client.request("GET", "https://synthetic.invalid", headers=signed))


def test_cr129_packet_a_managed_proxy_expiry_does_not_refresh():
    import asyncio

    from proxy.proxy_mixin import ManagedProxyEnvironmentError, ProxyRefreshMixin

    class ExpiredPool:
        def is_current_proxy_expired(self):
            return True

        async def get_or_refresh_proxy(self):
            raise AssertionError("managed request must not refresh proxy")

    class Client(ProxyRefreshMixin):
        request_environment = object()

    client = Client()
    client.init_proxy_pool(ExpiredPool())
    with pytest.raises(ManagedProxyEnvironmentError, match="new resolution"):
        asyncio.run(client._refresh_proxy_if_expired())


def test_cr129_packet_a_douyin_managed_request_requires_profile_ms_token(monkeypatch):
    import asyncio

    from media_platform.douyin.client import DouYinClient

    environment = _build()

    class Page:
        async def evaluate(self, script):
            return {}

    client = DouYinClient(
        proxy=None,
        headers={"User-Agent": environment.user_agent, "Cookie": "sessionid=synthetic"},
        playwright_page=Page(),
        cookie_dict={"sessionid": "synthetic"},
        request_environment=environment,
    )
    with pytest.raises(RuntimeError, match="msToken"):
        asyncio.run(
            client._DouYinClient__process_req_params(
                "/aweme/v1/web/search/item/",
                {"keyword": "synthetic"},
                client.headers,
            )
        )
