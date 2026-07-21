from __future__ import annotations

import asyncio
import copy
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest

from tools.platform_request_environment import (
    REQUEST_RESULT_PATH_ENV_NAME,
    PlatformRequestEnvironment,
    read_platform_request_result,
    write_platform_request_environment,
)


def _environment(
    *,
    account_id: int = 8972,
    proxy_policy: str = "direct",
    proxy_id: int | None = None,
) -> PlatformRequestEnvironment:
    created = datetime.now(timezone.utc)
    return PlatformRequestEnvironment(
        contract_version=2,
        workspace_id=1,
        account_id=account_id,
        platform="dy",
        profile_key=f"1/dy/acc_{account_id}",
        browser_family="chromium",
        browser_source="playwright_bundled",
        browser_channel="chromium",
        effective_browser_version="127.0.6533.17",
        browser_proof_digest="b" * 64,
        proxy_policy=proxy_policy,
        proxy_id=proxy_id,
        proxy_revision=f"proxy-revision-{account_id}",
        identity_revision=f"identity-revision-{account_id}",
        resolution_id=f"resolution-dy-{account_id}",
        attempt_id=f"attempt-dy-{account_id}",
        run_id=19002,
        browser_platform="windows",
        locale="zh-CN",
        timezone="Asia/Shanghai",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.6533.17 Safari/537.36"
        ),
        accept_language="zh-CN,zh;q=0.9",
        screen_width=1920,
        screen_height=1080,
        viewport_width=1920,
        viewport_height=963,
        device_scale_factor=1.0,
        is_mobile=False,
        has_touch=False,
        cookie_material_revision=f"cookie-material-{account_id}",
        created_at=created.isoformat(),
        expires_at=(created + timedelta(minutes=15)).isoformat(),
        fallback_used=False,
    )


def _cookie_dict(account_id: int = 8972) -> dict[str, str]:
    return {
        "sessionid": f"session-{account_id}",
        "ttwid": f"ttwid-{account_id}",
        "s_v_web_id": f"verify_{account_id}_synthetic",
        "odin_tt": f"odin-{account_id}",
    }


def _cookie_header(account_id: int = 8972) -> str:
    return ";".join(f"{name}={value}" for name, value in _cookie_dict(account_id).items())


def _page_snapshot(account_id: int = 8972) -> dict[str, object]:
    return {
        "navigator_user_agent": _environment(account_id=account_id).user_agent,
        "navigator_platform": "Win32",
        "ua_brands": (
            ("Not.A/Brand", "99"),
            ("Chromium", "127"),
        ),
        "ua_platform": "Windows",
        "ua_mobile": False,
        "hardware_concurrency": 8,
        "device_memory": 8,
        "screen_width": 1920,
        "screen_height": 1080,
        "viewport_width": 1920,
        "viewport_height": 963,
        "ms_token": f"ms-token-{account_id}",
        "web_id": f"7{account_id:018d}"[-19:],
    }


def _headers(environment: PlatformRequestEnvironment, account_id: int = 8972) -> dict[str, str]:
    return {
        "User-Agent": environment.user_agent,
        "Accept-Language": environment.accept_language,
        "Cookie": _cookie_header(account_id),
        "sec-ch-ua": '"Not.A/Brand";v="99", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Host": "www.douyin.com",
        "Origin": "https://www.douyin.com/",
        "Referer": "https://www.douyin.com/",
    }


def _identity(
    *,
    environment: PlatformRequestEnvironment | None = None,
    account_id: int = 8972,
    proxy_url: str | None = None,
):
    from media_platform.douyin.request_identity import build_douyin_request_identity

    environment = environment or _environment(account_id=account_id)
    return build_douyin_request_identity(
        environment=environment,
        cookie_header=_cookie_header(account_id),
        cookie_dict=_cookie_dict(account_id),
        headers=_headers(environment, account_id),
        proxy_url=proxy_url,
        page_snapshot=_page_snapshot(account_id),
    )


@pytest.mark.parametrize(
    ("target", "key", "message"),
    [
        ("page", "ms_token", "msToken"),
        ("page", "web_id", "webid"),
        ("cookie", "ttwid", "ttwid"),
        ("cookie", "s_v_web_id", "verifyFp"),
    ],
)
def test_cr129_packet_c_douyin_identity_requires_profile_material(target, key, message):
    from media_platform.douyin.request_identity import (
        DouyinRequestIdentityError,
        build_douyin_request_identity,
    )

    environment = _environment()
    cookies = _cookie_dict()
    page_snapshot = _page_snapshot()
    if target == "cookie":
        cookies.pop(key)
        cookie_header = ";".join(f"{name}={value}" for name, value in cookies.items())
    else:
        page_snapshot[key] = ""
        cookie_header = _cookie_header()

    with pytest.raises(DouyinRequestIdentityError, match=message):
        build_douyin_request_identity(
            environment=environment,
            cookie_header=cookie_header,
            cookie_dict=cookies,
            headers={**_headers(environment), "Cookie": cookie_header},
            proxy_url=None,
            page_snapshot=page_snapshot,
        )


def test_cr129_packet_c_douyin_identity_rejects_cookie_ua_screen_and_proxy_drift():
    from media_platform.douyin.request_identity import (
        DouyinRequestIdentityError,
        build_douyin_request_identity,
    )

    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    common = {
        "environment": environment,
        "cookie_header": _cookie_header(),
        "cookie_dict": _cookie_dict(),
        "headers": _headers(environment),
        "proxy_url": "http://user:pass@proxy.invalid:8080",
        "page_snapshot": _page_snapshot(),
    }

    with pytest.raises(DouyinRequestIdentityError, match="cookie"):
        build_douyin_request_identity(
            **{**common, "cookie_dict": {**_cookie_dict(), "ttwid": "stale"}}
        )
    with pytest.raises(DouyinRequestIdentityError, match="user-agent"):
        build_douyin_request_identity(
            **{
                **common,
                "headers": {**_headers(environment), "User-Agent": "stale-user-agent"},
            }
        )
    with pytest.raises(DouyinRequestIdentityError, match="screen"):
        build_douyin_request_identity(
            **{
                **common,
                "page_snapshot": {**_page_snapshot(), "screen_width": 1536},
            }
        )
    with pytest.raises(DouyinRequestIdentityError, match="proxy"):
        build_douyin_request_identity(**{**common, "proxy_url": None})


def test_cr129_packet_c_douyin_safe_projection_excludes_raw_material():
    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    identity = _identity(
        environment=environment,
        proxy_url="http://user:pass@proxy.invalid:8080",
    )

    safe = json.dumps(identity.to_safe_dict(), ensure_ascii=False)
    for raw in (
        "session-8972",
        "ttwid-8972",
        "verify_8972_synthetic",
        "ms-token-8972",
        "7000000000000008972",
        "user:pass@proxy.invalid",
    ):
        assert raw not in safe
    assert "cookie_digest" in safe
    assert "client_hints_digest" in safe


def test_cr129_packet_c_capture_reads_profile_values_once(monkeypatch):
    from media_platform.douyin.request_identity import capture_douyin_page_snapshot

    calls = []

    class Page:
        async def evaluate(self, script):
            calls.append(script)
            return _page_snapshot()

    first = asyncio.run(capture_douyin_page_snapshot(Page()))
    first["ms_token"] = "changed-after-capture"

    assert len(calls) == 1
    assert "window.localStorage" not in calls[0]
    assert "__tea_cache_tokens_6383" in calls[0]


def test_cr129_packet_c_douyin_signer_and_http_dispatch_share_frozen_inputs(monkeypatch):
    from media_platform.douyin import client as client_module
    from media_platform.douyin.client import DouYinClient

    environment = _environment(proxy_policy="account_bound", proxy_id=77)
    identity = _identity(
        environment=environment,
        proxy_url="http://user:pass@proxy.invalid:8080",
    )
    captured: dict[str, object] = {}

    async def fake_sign(uri, params, post_data, user_agent, page):
        captured["sign_uri"] = uri
        captured["sign_query"] = params
        captured["sign_body"] = copy.deepcopy(post_data)
        captured["sign_user_agent"] = user_agent
        return "synthetic-a-bogus"

    class Response:
        status_code = 200
        text = '{"status_code":0,"data":[{"aweme_info":{"aweme_id":"1"}}]}'

        def json(self):
            return {"status_code": 0, "data": [{"aweme_info": {"aweme_id": "1"}}]}

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

    monkeypatch.setattr(client_module, "get_a_bogus", fake_sign)
    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    monkeypatch.setattr(
        client_module,
        "get_web_id",
        lambda: (_ for _ in ()).throw(AssertionError("managed webid must come from Profile")),
    )

    client = DouYinClient(
        proxy="http://user:pass@proxy.invalid:8080",
        headers=_headers(environment),
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    result = asyncio.run(
        client.get("/aweme/v1/web/general/search/single/", {"keyword": "synthetic", "count": 1})
    )

    assert result["status_code"] == 0
    query = parse_qs(urlsplit(str(captured["url"])).query)
    assert query["msToken"] == [identity.ms_token]
    assert query["webid"] == [identity.web_id]
    assert query["verifyFp"] == [identity.verify_fp]
    assert query["fp"] == [identity.verify_fp]
    assert query["a_bogus"] == ["synthetic-a-bogus"]
    assert query["browser_platform"] == ["Win32"]
    assert query["browser_version"] == [environment.effective_browser_version]
    assert query["screen_width"] == ["1920"]
    assert query["screen_height"] == ["1080"]
    assert "MacIntel" not in str(captured["url"])
    assert "125.0.0.0" not in str(captured["url"])
    assert "synthetic-a-bogus" not in str(captured["sign_query"])
    signed_query = parse_qs(str(captured["sign_query"]))
    assert signed_query["verifyFp"] == [identity.verify_fp]
    assert signed_query["fp"] == [identity.verify_fp]
    assert captured["sign_user_agent"] == environment.user_agent
    sent_headers = captured["kwargs"]["headers"]
    assert sent_headers["Cookie"] == _cookie_header()
    assert sent_headers["sec-ch-ua"] == _headers(environment)["sec-ch-ua"]
    assert client.safe_request_proofs[-1]["signed"] is True


def test_cr129_packet_c_page_or_header_changes_after_freeze_do_not_change_request(monkeypatch):
    from media_platform.douyin import client as client_module
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    identity = _identity(environment=environment)
    captured = {}

    async def fake_sign(uri, params, post_data, user_agent, page):
        return "frozen-signature"

    class MutatedPage:
        async def evaluate(self, script):
            raise AssertionError("managed requests must not re-read Page state")

    class Response:
        status_code = 200
        text = '{"status_code":0}'

        def json(self):
            return {"status_code": 0}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            captured["url"] = url
            captured["headers"] = kwargs["headers"]
            return Response()

    monkeypatch.setattr(client_module, "get_a_bogus", fake_sign)
    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    headers = _headers(environment)
    client = DouYinClient(
        proxy=None,
        headers=headers,
        playwright_page=MutatedPage(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    headers["Cookie"] = "sessionid=changed"
    client.headers["User-Agent"] = "changed"

    with pytest.raises(Exception, match="user-agent"):
        asyncio.run(client.get("/aweme/v1/web/aweme/detail/", {"aweme_id": "1"}))

    client.headers = identity.headers
    asyncio.run(client.get("/aweme/v1/web/aweme/detail/", {"aweme_id": "1"}))
    assert identity.ms_token in str(captured["url"])
    assert captured["headers"]["Cookie"] == identity.cookie_header


def test_cr129_packet_c_creator_request_uses_profile_verify_fp(monkeypatch):
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    identity = _identity(environment=environment)
    client = DouYinClient(
        proxy=None,
        headers=_headers(environment),
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    captured = {}

    async def fake_get(uri, params=None, headers=None):
        captured.update(params or {})
        return {"ok": True}

    monkeypatch.setattr(client, "get", fake_get)
    asyncio.run(client.get_user_aweme_posts("synthetic-user"))

    assert captured["verifyFp"] == identity.verify_fp
    assert captured["fp"] == identity.verify_fp
    assert "ma3hrt8n" not in json.dumps(captured)


def test_cr129_packet_c_two_accounts_do_not_share_profile_material(monkeypatch):
    first = _identity(account_id=8972)
    second = _identity(account_id=9190)

    assert first.environment.profile_key != second.environment.profile_key
    assert first.cookie_digest != second.cookie_digest
    assert first.ms_token != second.ms_token
    assert first.web_id != second.web_id
    assert first.verify_fp != second.verify_fp
    assert first.ttwid != second.ttwid


def test_cr129_packet_c_managed_cookie_update_requires_new_resolution():
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    client = DouYinClient(
        proxy=None,
        headers=_headers(environment),
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=_identity(environment=environment),
    )

    with pytest.raises(Exception, match="new request resolution"):
        asyncio.run(client.update_cookies(object()))


def test_cr129_packet_c_rejects_stale_identity_environment():
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    stale = _identity(environment=replace(environment, attempt_id="attempt-stale"))

    with pytest.raises(Exception, match="environment mismatch"):
        DouYinClient(
            proxy=None,
            headers=_headers(environment),
            playwright_page=object(),
            cookie_dict=_cookie_dict(),
            request_environment=environment,
            request_identity=stale,
        )


def test_cr129_packet_c_stale_token_or_tampered_signed_url_stops_before_http(monkeypatch):
    from media_platform.douyin import client as client_module
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    identity = _identity(environment=environment)
    dispatched = False

    async def fake_sign(uri, params, post_data, user_agent, page):
        return "signed-current-input"

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            nonlocal dispatched
            dispatched = True
            raise AssertionError("identity drift reached HTTP")

    monkeypatch.setattr(client_module, "get_a_bogus", fake_sign)
    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    client = DouYinClient(
        proxy=None,
        headers=_headers(environment),
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )

    with pytest.raises(Exception, match="msToken mismatch"):
        asyncio.run(client.get("/api/test", {"msToken": "stale-ms-token"}))
    assert dispatched is False
    with pytest.raises(Exception, match="verifyFp mismatch"):
        asyncio.run(client.get("/api/test", {"verifyFp": "stale-verify-fp"}))
    assert dispatched is False

    _, signed_headers = asyncio.run(
        client._DouYinClient__process_req_params(
            "/api/test",
            {"keyword": "synthetic"},
            client.headers,
        )
    )
    with pytest.raises(Exception, match="target changed"):
        asyncio.run(
            client.request(
                "GET",
                signed_headers.expected_url + "&a_bogus=stale",
                headers=signed_headers,
            )
        )
    assert dispatched is False


def test_cr129_packet_c_douyin_proof_persists_and_runner_requires_signed_success(
    monkeypatch,
    tmp_path,
):
    from api.monitoring import runner as runner_module
    from media_platform.douyin import client as client_module
    from media_platform.douyin.client import DouYinClient

    environment = _environment()
    identity = _identity(environment=environment)
    destination = tmp_path / "request-result.json"
    monkeypatch.setenv(REQUEST_RESULT_PATH_ENV_NAME, str(destination))
    write_platform_request_environment(environment)

    async def fake_sign(uri, params, post_data, user_agent, page):
        return "proof-signature"

    class Response:
        status_code = 200
        text = '{"status_code":0}'

        def json(self):
            return {"status_code": 0}

    class HttpClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def request(self, method, url, **kwargs):
            return Response()

    monkeypatch.setattr(client_module, "get_a_bogus", fake_sign)
    monkeypatch.setattr(client_module, "make_async_client", lambda proxy: HttpClient())
    client = DouYinClient(
        proxy=None,
        headers=_headers(environment),
        playwright_page=object(),
        cookie_dict=_cookie_dict(),
        request_environment=environment,
        request_identity=identity,
    )
    asyncio.run(client.get("/api/test", {"keyword": "synthetic"}))

    restored, proofs = read_platform_request_result(destination)
    assert restored == environment
    assert len(proofs) == 1
    proof_text = json.dumps(proofs[0], ensure_ascii=False)
    assert identity.ms_token not in proof_text
    assert identity.verify_fp not in proof_text
    runner_module._validate_managed_dispatch_proofs("dy", environment, tuple(proofs))
    with pytest.raises(RuntimeError, match="Douyin request dispatch proof is missing"):
        runner_module._validate_managed_dispatch_proofs("dy", environment, ())
