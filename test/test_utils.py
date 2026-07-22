# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/test/test_utils.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# -*- coding: utf-8 -*-

from unittest.mock import AsyncMock

import pytest

from tools import utils
from tools import crawler_util


def test_convert_cookies():
    xhs_cookies = "a1=x000101360; webId=1190c4d3cxxxx125xxx; "
    cookie_dict = utils.convert_str_cookie_to_dict(xhs_cookies)
    assert cookie_dict.get("webId") == "1190c4d3cxxxx125xxx"
    assert cookie_dict.get("a1") == "x000101360"


@pytest.mark.asyncio
async def test_convert_browser_context_cookies_uses_url_filter():
    browser_context = AsyncMock()
    browser_context.cookies.return_value = [{"name": "sessionid", "value": "abc"}]

    cookie_str, cookie_dict = await utils.convert_browser_context_cookies(
        browser_context,
        urls=["https://www.douyin.com"],
    )

    browser_context.cookies.assert_awaited_once_with(urls=["https://www.douyin.com"])
    assert cookie_str == "sessionid=abc"
    assert cookie_dict == {"sessionid": "abc"}


@pytest.mark.asyncio
async def test_cr129_managed_cookie_selection_uses_aborted_browser_request_proof():
    events = []

    class FakeRequest:
        async def all_headers(self):
            events.append("header")
            return {
                "cookie": (
                    "sessionid=browser-first;sessionid=browser-second;"
                    "not-sent-by-browser;"
                    "complex=segment;without-equals;ttwid=synthetic-ttwid"
                )
            }

    class FakeRoute:
        request = FakeRequest()

        def __init__(self):
            self.aborted = False

        async def abort(self):
            self.aborted = True
            events.append("abort")

    class FakePage:
        def __init__(self):
            self.handler = None
            self.route_obj = FakeRoute()
            self.closed = False
            self.unrouted = False

        async def route(self, _url, handler):
            self.handler = handler

        async def goto(self, _url, **_kwargs):
            await self.handler(self.route_obj)

        async def unroute(self, _url, handler):
            assert handler is self.handler
            self.unrouted = True

        async def close(self):
            self.closed = True

    class FakeContext:
        def __init__(self):
            self.page = FakePage()
            self.cookie_urls = None

        async def cookies(self, *, urls):
            self.cookie_urls = urls
            events.append("store")
            return [
                {"name": "", "value": "not-sent-by-browser"},
                {"name": "sessionid", "value": "browser-first"},
                {"name": "sessionid", "value": "browser-second"},
                {"name": "complex", "value": "segment;without-equals"},
                {"name": "ttwid", "value": "synthetic-ttwid"},
            ]

        async def new_page(self):
            return self.page

    browser_context = FakeContext()

    cookie_str, cookie_dict = await utils.convert_browser_context_cookies_for_request(
        browser_context,
        "https://www.douyin.com/",
    )

    assert len(browser_context.cookie_urls) == 1
    assert browser_context.cookie_urls[0].startswith(
        "https://www.douyin.com/?__mediacrawler_cookie_probe__="
    )
    assert browser_context.page.route_obj.aborted is True
    assert events == ["header", "store", "abort"]
    assert browser_context.page.unrouted is True
    assert browser_context.page.closed is True
    assert cookie_str == (
        "sessionid=browser-first;complex=segment;without-equals;"
        "ttwid=synthetic-ttwid"
    )
    assert cookie_dict == {
        "sessionid": "browser-first",
        "complex": "segment;without-equals",
        "ttwid": "synthetic-ttwid",
    }


def test_cr129_managed_cookie_request_proof_must_match_structured_store():
    with pytest.raises(
        utils.ManagedCookieSelectionError,
        match="proof value mismatch",
    ):
        crawler_util._canonical_browser_cookie_header(
            "sessionid=browser-value",
            [{"name": "sessionid", "value": "different-store-value"}],
        )


def test_cr129_managed_cookie_request_proof_skips_spaced_nameless_segment():
    cookie_str, cookie_dict = crawler_util._canonical_browser_cookie_header(
        "nameless-value  ; sessionid=browser-value",
        [
            {"name": "", "value": "nameless-value"},
            {"name": "sessionid", "value": "browser-value"},
        ],
    )

    assert cookie_str == "sessionid=browser-value"
    assert cookie_dict == {"sessionid": "browser-value"}


@pytest.mark.asyncio
async def test_cr129_managed_cookie_request_proof_cleanup_fails_closed():
    class FakeRequest:
        async def all_headers(self):
            return {"cookie": "sessionid=browser-value"}

    class FakeRoute:
        request = FakeRequest()

        async def abort(self):
            return None

    class FakePage:
        async def route(self, _url, handler):
            self.handler = handler

        async def goto(self, _url, **_kwargs):
            await self.handler(FakeRoute())

        async def unroute(self, _url, _handler):
            raise RuntimeError("sensitive browser cleanup detail")

        async def close(self):
            return None

    class FakeContext:
        async def new_page(self):
            return FakePage()

        async def cookies(self, *, urls):
            assert len(urls) == 1
            assert urls[0].startswith(
                "https://www.douyin.com/?__mediacrawler_cookie_probe__="
            )
            return [{"name": "sessionid", "value": "browser-value"}]

    with pytest.raises(
        utils.ManagedCookieSelectionError,
        match="proof cleanup failed",
    ) as error:
        await utils.convert_browser_context_cookies_for_request(
            FakeContext(),
            "https://www.douyin.com/",
        )

    assert "sensitive browser cleanup detail" not in str(error.value)
