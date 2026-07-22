from __future__ import annotations

import asyncio
import copy
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

import pytest
import httpx

from tools.platform_request_environment import (
    REQUEST_RESULT_PATH_ENV_NAME,
    PlatformRequestEnvironment,
    PlatformRequestEnvironmentError,
    append_platform_request_dispatch_proof,
    read_platform_request_result,
    write_platform_request_environment,
)


def _environment(*, proxy_policy: str = "direct", proxy_id: int | None = None) -> PlatformRequestEnvironment:
    created = datetime.now(timezone.utc)
    return PlatformRequestEnvironment(
        contract_version=3,
        workspace_id=1,
        account_id=9196,
        platform="xhs",
        profile_key="1/xhs/acc_9196",
        browser_family="chromium",
        browser_source="playwright_bundled",
        browser_channel="chromium",
        effective_browser_version="127.0.6533.17",
        browser_proof_digest="a" * 64,
        proxy_policy=proxy_policy,
        proxy_id=proxy_id,
        proxy_revision="proxy-revision-1",
        identity_revision="identity-revision-1",
        resolution_id="resolution-xhs-1",
        attempt_id="attempt-xhs-1",
        run_id=19001,
        browser_platform="windows",
        locale="zh-CN",
        timezone="Asia/Shanghai",
        user_agent="Mozilla/5.0 Chrome/127.0.6533.17",
        accept_language="zh-CN,zh;q=0.9",
        screen_width=1920,
        screen_height=1080,
        viewport_width=1920,
        viewport_height=963,
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        cookie_material_revision="cookie-material-1",
        created_at=created.isoformat(),
        expires_at=(created + timedelta(minutes=15)).isoformat(),
        fallback_used=False,
    )


def _headers(environment: PlatformRequestEnvironment) -> dict[str, str]:
    return {
        "accept": "application/json, text/plain, */*",
        "accept-language": environment.accept_language,
        "content-type": "application/json;charset=UTF-8",
        "user-agent": environment.user_agent,
        "sec-ch-ua": '"Chromium";v="127", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cookie": "a1=a1-value;web_session=session-value;other=other-value",
    }


def _cookie_dict() -> dict[str, str]:
    return {
        "a1": "a1-value",
        "web_session": "session-value",
        "other": "other-value",
    }


def test_cr129_packet_b_xhs_identity_requires_a1_and_web_session():
    from media_platform.xhs.request_identity import XhsRequestIdentityError, build_xhs_request_identity

    environment = _environment()
    with pytest.raises(XhsRequestIdentityError, match="a1"):
        build_xhs_request_identity(
            environment=environment,
            cookie_header="web_session=session-value",
            cookie_dict={"web_session": "session-value"},
            headers=_headers(environment),
            proxy_url=None,
        )


def test_cr129_packet_b_xhs_identity_rejects_cookie_header_or_environment_drift():
    from media_platform.xhs.request_identity import XhsRequestIdentityError, build_xhs_request_identity

    environment = _environment()
    headers = _headers(environment)
    with pytest.raises(XhsRequestIdentityError, match="cookie"):
        build_xhs_request_identity(
            environment=environment,
            cookie_header="a1=wrong;web_session=session-value",
            cookie_dict=_cookie_dict(),
            headers=headers,
            proxy_url=None,
        )

    mismatched_headers = {**headers, "user-agent": "Mozilla/5.0 Chrome/126.0.0.0"}
    with pytest.raises(XhsRequestIdentityError, match="user-agent"):
        build_xhs_request_identity(
            environment=environment,
            cookie_header=headers["Cookie"],
            cookie_dict=_cookie_dict(),
            headers=mismatched_headers,
            proxy_url=None,
        )


def test_cr129_packet_b_xhs_identity_safe_projection_has_only_digests():
    from media_platform.xhs.request_identity import build_xhs_request_identity

    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=_headers(environment)["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=_headers(environment),
        proxy_url="http://user:password@proxy.invalid:8080",
    )
    safe = json.dumps(identity.to_safe_dict(), ensure_ascii=False)
    assert "a1-value" not in safe
    assert "session-value" not in safe
    assert "password@proxy.invalid" not in safe
    assert "cookie_digest" in safe
    assert "proxy_digest" in safe


def test_cr129_packet_b_xhs_signer_and_dispatch_use_one_frozen_request(monkeypatch):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.playwright_sign import _build_sign_string
    from media_platform.xhs.request_identity import build_xhs_request_identity

    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url="http://user:password@proxy.invalid:8080",
    )
    captured: dict[str, object] = {}

    def fake_sign(**kwargs):
        captured["signed_data"] = copy.deepcopy(kwargs["data"])
        captured["signing_content"] = _build_sign_string(
            kwargs["uri"], kwargs["data"], kwargs["method"]
        )
        # A signer must not be able to mutate the request snapshot used later.
        if isinstance(kwargs["data"], dict):
            kwargs["data"]["keyword"] = "signer-mutated"
        return {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-x-s-common",
            "x-b3-traceid": "synthetic-trace",
        }

    class Response:
        status_code = 200
        headers: dict[str, str] = {}
        text = '{"success": true, "data": {"ok": true}}'

        def json(self):
            return {"success": True, "data": {"ok": True}}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            captured["method"] = method
            captured["url"] = url
            captured["kwargs"] = kwargs
            return Response()

    monkeypatch.setattr(client_module, "sign_with_xhshow", fake_sign)
    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    client = XiaoHongShuClient(
        proxy="http://user:password@proxy.invalid:8080",
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    result = asyncio.run(client.get("/api/sns/web/v1/search/notes", {"keyword": "原始词", "page": 1}))

    assert result == {"ok": True}
    assert captured["signed_data"] == {"keyword": "原始词", "page": 1}
    assert "keyword=原始词" in unquote(str(captured["url"]))
    assert captured["url"] == f"https://edith.xiaohongshu.com{captured['signing_content']}"
    assert "signer-mutated" not in str(captured["url"])
    sent_headers = captured["kwargs"]["headers"]
    assert sent_headers["Cookie"] == headers["Cookie"]
    assert sent_headers["User-Agent"] == environment.user_agent
    assert client.safe_request_proofs
    proof = client.safe_request_proofs[-1]
    proof_text = json.dumps(proof, ensure_ascii=False)
    assert "a1-value" not in proof_text
    assert "password@proxy.invalid" not in proof_text

    recased = asyncio.run(client._pre_headers("/api/test", params={"page": 1}))
    recased["cookie"] = recased.pop("Cookie")
    recased_result = asyncio.run(
        client.request("GET", recased.expected_url, headers=recased)
    )
    assert recased_result == {"ok": True}

    complex_payload = {
        "keyword": "引号\"与反斜杠\\",
        "nested": {"items": ["中文", 1, True, None]},
    }
    post_result = asyncio.run(client.post("/api/test", complex_payload))
    assert post_result == {"ok": True}
    assert captured["signing_content"] == f"/api/test{captured['kwargs']['data']}"


def test_cr129_packet_e_unmanaged_xhs_signer_preserves_lowercase_user_agent():
    from media_platform.xhs.client import XiaoHongShuClient

    user_agent = "Mozilla/5.0 Chrome/127.0.6533.17"
    client = XiaoHongShuClient(
        headers={
            "accept": "application/json, text/plain, */*",
            "user-agent": user_agent,
            "Cookie": "a1=a1-value; web_session=session-value",
        },
        playwright_page=object(),
        cookie_dict={"a1": "a1-value", "web_session": "session-value"},
    )

    signed_headers = asyncio.run(
        client._pre_headers("/api/sns/web/v1/user/me", params={})
    )

    assert signed_headers.signed_user_agent == user_agent
    client._validate_signed_headers(
        signed_headers,
        method="GET",
        url=signed_headers.expected_url,
        body=None,
    )


def test_cr129_packet_b_xhs_managed_cookie_update_requires_new_resolution(monkeypatch):
    from media_platform.xhs.client import ManagedRequestIdentityError, XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )

    class Context:
        async def cookies(self, urls=None):
            return [
                {"name": "a1", "value": "new-a1"},
                {"name": "web_session", "value": "new-session"},
            ]

    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    with pytest.raises(ManagedRequestIdentityError, match="Cookie"):
        asyncio.run(client.update_cookies(Context()))


def test_cr129_packet_b_xhs_dispatch_proof_is_bound_and_persisted(tmp_path, monkeypatch):
    from api.monitoring import runner as runner_module
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )
    destination = tmp_path / "platform-request-result.json"
    monkeypatch.setenv(REQUEST_RESULT_PATH_ENV_NAME, str(destination))
    write_platform_request_environment(environment)

    class Response:
        status_code = 200
        headers: dict[str, str] = {}
        text = '{"success": true, "data": {"ok": true}}'

        def json(self):
            return {"success": True, "data": {"ok": True}}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            await asyncio.sleep(0)
            return Response()

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    async def dispatch_many():
        await asyncio.gather(
            *(
                client.get("/api/sns/web/v1/search/notes", {"keyword": "词", "page": index})
                for index in range(40)
            )
        )

    asyncio.run(dispatch_many())

    restored, proofs = read_platform_request_result(destination)
    assert restored == environment
    assert len(proofs) == 32
    assert [proof["request_index"] for proof in proofs] == [1, *range(10, 41)]
    assert [proof["request_index"] for proof in client.safe_request_proofs] == [1, *range(10, 41)]
    proof_text = json.dumps(proofs[0], ensure_ascii=False)
    assert "a1-value" not in proof_text
    assert "web_session" not in proof_text
    assert proofs[0]["account_id"] == environment.account_id
    assert proofs[0]["profile_key"] == environment.profile_key
    runner_module._validate_managed_dispatch_proofs("xhs", environment, tuple(proofs))
    with pytest.raises(RuntimeError, match="dispatch proof is missing"):
        runner_module._validate_managed_dispatch_proofs("xhs", environment, ())
    stale = dict(proofs[-1])
    stale["request_index"] = 2
    with pytest.raises(PlatformRequestEnvironmentError, match="request_index"):
        append_platform_request_dispatch_proof(environment, stale)


def test_cr129_packet_b_xhs_sign_string_and_final_query_are_byte_identical():
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.playwright_sign import _build_sign_string

    uri = "/api/sns/web/v1/search/notes"
    params = {"note_ids": ["first", "second"], "keyword": "原始词", "page": 1}
    signed_content = _build_sign_string(uri, params, "GET")
    final_content = f"{uri}?{XiaoHongShuClient._build_query_string(params)}"

    assert signed_content == final_content


def test_cr129_packet_b_xhs_target_body_and_proxy_drift_stop_before_dispatch(monkeypatch):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import ManagedRequestIdentityError, XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity

    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    headers = _headers(environment)
    proxy = "http://user:password@proxy.invalid:8080"
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=proxy,
    )
    dispatched = False

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            nonlocal dispatched
            dispatched = True
            raise AssertionError("identity drift reached HTTP transport")

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy_url: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        proxy=proxy,
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    signed_get = asyncio.run(client._pre_headers("/api/test", params={"page": 1}))
    with pytest.raises(ManagedRequestIdentityError, match="target"):
        asyncio.run(
            client.request(
                "GET",
                "https://edith.xiaohongshu.com/api/test?page=2",
                headers=signed_get,
            )
        )

    signed_post = asyncio.run(client._pre_headers("/api/test", payload={"page": 1}))
    with pytest.raises(ManagedRequestIdentityError, match="body"):
        asyncio.run(
            client.request(
                "POST",
                "https://edith.xiaohongshu.com/api/test",
                headers=signed_post,
                data='{"page":2}',
            )
        )

    client.proxy = "http://other.invalid:8080"
    with pytest.raises(ManagedRequestIdentityError, match="proxy"):
        asyncio.run(
            client.request(
                "GET",
                signed_get.expected_url,
                headers=signed_get,
            )
        )
    assert dispatched is False


def test_cr129_packet_b_concurrent_xhs_clients_keep_account_material_isolated(monkeypatch):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity

    first_environment = _environment(proxy_policy="account_bound", proxy_id=77)
    second_environment = replace(
        first_environment,
        account_id=9195,
        profile_key="1/xhs/acc_9195",
        proxy_id=78,
        proxy_revision="proxy-revision-2",
        identity_revision="identity-revision-2",
        resolution_id="resolution-xhs-2",
        attempt_id="attempt-xhs-2",
        run_id=19002,
        cookie_material_revision="cookie-material-2",
    )
    sent: list[tuple[str | None, str]] = []

    class Response:
        status_code = 200
        headers: dict[str, str] = {}
        text = '{"success": true, "data": {"ok": true}}'

        def json(self):
            return {"success": True, "data": {"ok": True}}

    class HttpClient:
        def __init__(self, proxy_url):
            self.proxy_url = proxy_url

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            await asyncio.sleep(0)
            sent.append((self.proxy_url, kwargs["headers"]["Cookie"]))
            return Response()

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy=None: HttpClient(proxy))
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )

    def build_client(environment, suffix, proxy_url):
        cookies = {"a1": f"a1-{suffix}", "web_session": f"session-{suffix}"}
        headers = {
            **_headers(environment),
            "Cookie": f"a1=a1-{suffix};web_session=session-{suffix}",
        }
        identity = build_xhs_request_identity(
            environment=environment,
            cookie_header=headers["Cookie"],
            cookie_dict=cookies,
            headers=headers,
            proxy_url=proxy_url,
        )
        return XiaoHongShuClient(
            proxy=proxy_url,
            headers=headers,
            playwright_page=object(),
            cookie_dict=cookies,
            request_environment=environment,
            request_identity=identity,
        )

    first = build_client(first_environment, "first", "http://first.invalid:8080")
    second = build_client(second_environment, "second", "http://second.invalid:8080")

    async def run_both():
        await asyncio.gather(
            first.get("/api/test", {"account": "first"}),
            second.get("/api/test", {"account": "second"}),
        )

    asyncio.run(run_both())

    assert set(sent) == {
        ("http://first.invalid:8080", "a1=a1-first;web_session=session-first"),
        ("http://second.invalid:8080", "a1=a1-second;web_session=session-second"),
    }


def test_cr129_packet_b_xhs_environment_expiry_stops_before_http(monkeypatch):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import ManagedRequestIdentityError, XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity
    from tools import platform_request_environment as environment_module

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )
    dispatched = False

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            nonlocal dispatched
            dispatched = True
            raise AssertionError("expired environment reached HTTP")

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    signed = asyncio.run(client._pre_headers("/api/test", params={"page": 1}))

    class FutureDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(timezone.utc) + timedelta(hours=1)

    monkeypatch.setattr(environment_module, "datetime", FutureDatetime)
    with pytest.raises(ManagedRequestIdentityError, match="expired"):
        asyncio.run(client.request("GET", signed.expected_url, headers=signed))
    assert dispatched is False


def test_cr129_packet_b_unmanaged_xhs_client_keeps_account_check_compatibility(monkeypatch):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient

    class Response:
        status_code = 200
        headers: dict[str, str] = {}
        text = '{"success": true, "data": {"ok": true}}'

        def json(self):
            return {"success": True, "data": {"ok": True}}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            return Response()

    class Context:
        async def cookies(self, urls=None):
            return [{"name": "legacy", "value": "updated"}]

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers={
            "User-Agent": "legacy-agent",
            "accept-language": "zh-CN",
            "Cookie": "legacy=original",
        },
        playwright_page=object(),
        cookie_dict={"legacy": "original"},
    )

    assert asyncio.run(client.get("/api/test", {"page": 1})) == {"ok": True}
    asyncio.run(client.update_cookies(Context()))
    assert client.headers["Cookie"] == "legacy=updated"
    assert client.cookie_dict == {"legacy": "updated"}
    assert client.safe_request_proofs == []


@pytest.mark.parametrize("payload", [[], "not-an-object"])
def test_cr129_packet_d_managed_xhs_rejects_non_object_response(monkeypatch, payload):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity
    from tools.crawler_attempt import CrawlerAttemptFailure

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )

    class Response:
        status_code = 200
        text = "synthetic-invalid-response"

        def json(self):
            return payload

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            return Response()

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    with pytest.raises(CrawlerAttemptFailure) as exc_info:
        asyncio.run(client.get("/api/test", {"page": 1}))

    assert exc_info.value.category == "platform_protocol_changed"
    assert exc_info.value.reason_code == "xhs_response_invalid"


def test_cr129_packet_d_managed_xhs_invalid_json_is_typed_without_inner_retry(
    monkeypatch,
):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity
    from tools.crawler_attempt import CrawlerAttemptFailure

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )
    calls = 0

    class Response:
        status_code = 200
        text = "synthetic-invalid-json"

        def json(self):
            raise ValueError("synthetic parse detail")

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            nonlocal calls
            calls += 1
            return Response()

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    with pytest.raises(CrawlerAttemptFailure) as exc_info:
        asyncio.run(client.get("/api/test", {"page": 1}))

    assert calls == 1
    assert exc_info.value.category == "platform_protocol_changed"
    assert exc_info.value.reason_code == "xhs_response_invalid"


@pytest.mark.parametrize(
    ("response_or_error", "expected_category"),
    [
        (
            httpx.ReadTimeout(
                "synthetic timeout",
                request=httpx.Request("GET", "https://edith.xiaohongshu.com/api/test"),
            ),
            "timeout",
        ),
        (503, "transient_network"),
        (408, "timeout"),
    ],
)
def test_cr129_packet_d_managed_xhs_classifies_transient_boundaries(
    monkeypatch,
    response_or_error,
    expected_category,
):
    from media_platform.xhs import client as client_module
    from media_platform.xhs.client import XiaoHongShuClient
    from media_platform.xhs.request_identity import build_xhs_request_identity
    from tools.crawler_attempt import CrawlerAttemptFailure

    environment = _environment()
    headers = _headers(environment)
    identity = build_xhs_request_identity(
        environment=environment,
        cookie_header=headers["Cookie"],
        cookie_dict=_cookie_dict(),
        headers=headers,
        proxy_url=None,
    )

    response_status = response_or_error if isinstance(response_or_error, int) else 200

    class Response:
        status_code = response_status
        text = "synthetic gateway response"

        def json(self):
            return {"success": True, "data": {"ok": True}}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, **kwargs):
            if isinstance(response_or_error, BaseException):
                raise response_or_error
            return Response()

    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "sign_with_xhshow",
        lambda **kwargs: {
            "x-s": "synthetic-x-s",
            "x-t": "synthetic-x-t",
            "x-s-common": "synthetic-common",
            "x-b3-traceid": "synthetic-trace",
        },
    )
    client = XiaoHongShuClient(
        headers=headers,
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    with pytest.raises(CrawlerAttemptFailure) as exc_info:
        asyncio.run(client.get("/api/test", {"page": 1}))

    assert exc_info.value.category == expected_category


def test_cr129_packet_d_managed_xhs_core_propagates_client_failure():
    from media_platform.xhs.core import XiaoHongShuCrawler
    from media_platform.xhs.exception import DataFetchError

    crawler = object.__new__(XiaoHongShuCrawler)
    crawler.platform_request_environment = _environment()

    class Client:
        async def get_note_by_id(self, note_id, xsec_source, xsec_token):
            raise DataFetchError("synthetic managed failure")

    crawler.xhs_client = Client()

    with pytest.raises(DataFetchError, match="synthetic managed failure"):
        asyncio.run(
            crawler.get_note_detail_async_task(
                "synthetic-note",
                "pc_search",
                "synthetic-xsec-token",
                asyncio.Semaphore(1),
            )
        )


def test_cr129_packet_d_managed_xhs_retry_error_preserves_terminal_category():
    from tenacity import Future, RetryError

    from media_platform.xhs.core import XiaoHongShuCrawler
    from tools.crawler_attempt import CrawlerAttemptFailure

    crawler = object.__new__(XiaoHongShuCrawler)
    crawler.platform_request_environment = _environment()
    attempt = Future(1)
    attempt.set_exception(
        CrawlerAttemptFailure(
            "captcha_or_human_verification",
            "xhs_human_verification",
        )
    )

    class Client:
        async def get_note_by_id(self, note_id, xsec_source, xsec_token):
            raise RetryError(attempt)

    crawler.xhs_client = Client()

    with pytest.raises(CrawlerAttemptFailure) as exc_info:
        asyncio.run(
            crawler.get_note_detail_async_task(
                "synthetic-note",
                "pc_search",
                "synthetic-xsec-token",
                asyncio.Semaphore(1),
            )
        )

    assert exc_info.value.category == "captcha_or_human_verification"
    assert exc_info.value.reason_code == "xhs_human_verification"
