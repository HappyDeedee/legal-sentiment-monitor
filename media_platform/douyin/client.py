# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/douyin/client.py
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

import asyncio
import copy
import json
import os
import urllib.parse
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Dict, Union, Optional

import httpx
from playwright.async_api import BrowserContext

from base.base_crawler import AbstractApiClient
from proxy.proxy_mixin import ProxyRefreshMixin
from tools import utils
from tools.httpx_util import make_async_client
from tools.platform_request_environment import (
    REQUEST_RESULT_PATH_ENV_NAME,
    PlatformRequestEnvironmentError,
    append_platform_request_dispatch_proof,
)
from var import request_keyword_var

if TYPE_CHECKING:
    from proxy.proxy_ip_pool import ProxyIpPool
    from tools.platform_request_environment import PlatformRequestEnvironment

from .exception import *
from .field import *
from .help import *
from .request_identity import (
    DouyinRequestIdentity,
    DouyinRequestIdentityError,
    safe_digest,
)


class ManagedDouyinRequestIdentityError(RuntimeError):
    """A managed Douyin request changed a frozen identity input."""


class _SignedHeaders(dict):
    signed_cookie: str
    signed_user_agent: str
    expected_method: str
    expected_url: str
    expected_body_digest: str
    signer_input_digest: str
    signer_output_digest: str


class DouYinClient(AbstractApiClient, ProxyRefreshMixin):

    def __init__(
        self,
        timeout=60,  # If the crawl media option is turned on, Douyin’s short videos will require a longer timeout.
        proxy=None,
        *,
        headers: Dict,
        playwright_page: Optional[Page],
        cookie_dict: Dict,
        proxy_ip_pool: Optional["ProxyIpPool"] = None,
        request_environment: Optional["PlatformRequestEnvironment"] = None,
        request_identity: Optional[DouyinRequestIdentity] = None,
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.headers = dict(headers)
        self._host = "https://www.douyin.com"
        self.cookie_urls = [
            "https://douyin.com",
            self._host,
            "https://creator.douyin.com",
            "https://douhot.douyin.com",
            "https://live.douyin.com",
        ]
        self.playwright_page = playwright_page
        self.cookie_dict = dict(cookie_dict)
        self.request_environment = request_environment
        self.request_identity = request_identity
        self.safe_request_proofs: list[dict[str, Any]] = []
        self._request_sequence = 0
        if self.request_environment is not None:
            if self.request_identity is None:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request identity is missing"
                )
            if self.request_identity.environment != self.request_environment:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request environment mismatch"
                )
            try:
                self.request_identity.assert_runtime(
                    headers=self.headers,
                    proxy_url=self.proxy,
                )
            except DouyinRequestIdentityError as exc:
                raise ManagedDouyinRequestIdentityError(str(exc)) from exc
            self.headers = self.request_identity.headers
            self.cookie_dict = self.request_identity.cookie_dict
        # Initialize proxy pool (from ProxyRefreshMixin)
        self.init_proxy_pool(proxy_ip_pool)

    async def __process_req_params(
        self,
        uri: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        request_method="GET",
    ):
        if not params:
            params = {}
        headers = headers or self.headers
        if self.request_environment is not None:
            if request_method != "GET":
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin POST signer is unsupported"
                )
            if self.request_identity is None:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request identity is missing"
                )
            try:
                self.request_identity.assert_runtime(
                    headers=headers,
                    proxy_url=self.proxy,
                )
            except DouyinRequestIdentityError as exc:
                raise ManagedDouyinRequestIdentityError(str(exc)) from exc

            request_params = copy.deepcopy(params)
            for name, value in self.request_identity.common_params.items():
                if name in request_params and str(request_params[name]) != value:
                    raise ManagedDouyinRequestIdentityError(
                        f"managed Douyin request {name} mismatch"
                    )
                request_params[name] = value
            for name in ("verifyFp", "fp"):
                if (
                    name in request_params
                    and str(request_params[name]) != self.request_identity.verify_fp
                ):
                    raise ManagedDouyinRequestIdentityError(
                        f"managed Douyin request {name} mismatch"
                    )
                request_params[name] = self.request_identity.verify_fp

            query_string = urllib.parse.urlencode(request_params, doseq=True)
            a_bogus = await get_a_bogus(
                uri,
                query_string,
                {},
                self.request_identity.environment.user_agent,
                self.playwright_page,
            )
            if not isinstance(a_bogus, str) or not a_bogus:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request a_bogus is missing"
                )
            request_params["a_bogus"] = a_bogus
            final_query = urllib.parse.urlencode(request_params, doseq=True)

            signed_headers = _SignedHeaders(headers)
            signed_headers.signed_cookie = self.request_identity.cookie_header
            signed_headers.signed_user_agent = (
                self.request_identity.environment.user_agent
            )
            signed_headers.expected_method = "GET"
            signed_headers.expected_url = f"{self._host}{uri}?{final_query}"
            signed_headers.expected_body_digest = safe_digest("")
            signed_headers.signer_input_digest = safe_digest(
                {
                    "method": "GET",
                    "uri": uri,
                    "query": query_string,
                    "body_digest": safe_digest(""),
                    "cookie_digest": self.request_identity.cookie_digest,
                    "user_agent_digest": self.request_identity.user_agent_digest,
                    "client_hints_digest": self.request_identity.client_hints_digest,
                    "proxy_digest": self.request_identity.proxy_digest,
                }
            )
            signed_headers.signer_output_digest = safe_digest(a_bogus)
            return request_params, signed_headers

        local_storage: Dict = await self.playwright_page.evaluate("() => window.localStorage")  # type: ignore
        common_params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "version_code": "190600",
            "version_name": "19.6.0",
            "update_version_code": "170400",
            "pc_client_type": "1",
            "cookie_enabled": "true",
            "browser_language": "zh-CN",
            "browser_platform": "MacIntel",
            "browser_name": "Chrome",
            "browser_version": "125.0.0.0",
            "browser_online": "true",
            "engine_name": "Blink",
            "os_name": "Mac OS",
            "os_version": "10.15.7",
            "cpu_core_num": "8",
            "device_memory": "8",
            "engine_version": "109.0",
            "platform": "PC",
            "screen_width": "2560",
            "screen_height": "1440",
            'effective_type': '4g',
            "round_trip_time": "50",
            "webid": get_web_id(),
            "msToken": local_storage.get("xmst"),
        }
        params.update(common_params)
        query_string = urllib.parse.urlencode(params)

        # 20240927 a-bogus update (JS version)
        post_data = {}
        if request_method == "POST":
            post_data = params

        if "/v1/web/general/search" not in uri:
            a_bogus = await get_a_bogus(uri, query_string, post_data, headers["User-Agent"], self.playwright_page)
            params["a_bogus"] = a_bogus
        return params, headers

    def _validate_managed_headers(self, headers: Dict[str, str]) -> None:
        if self.request_environment is None:
            return
        if self.request_identity is None:
            raise ManagedDouyinRequestIdentityError(
                "managed Douyin request identity is missing"
            )
        try:
            self.request_identity.assert_runtime(
                headers=headers,
                proxy_url=self.proxy,
            )
        except DouyinRequestIdentityError as exc:
            raise ManagedDouyinRequestIdentityError(str(exc)) from exc

    @staticmethod
    def _header_value(headers: Dict[str, str], name: str) -> str:
        values = [
            str(value)
            for key, value in headers.items()
            if str(key).lower() == name
        ]
        if len(values) != 1:
            raise ManagedDouyinRequestIdentityError(
                f"signed Douyin request {name} header is ambiguous"
            )
        return values[0]

    @staticmethod
    def _validate_signed_headers(
        headers: Dict[str, str],
        *,
        method: str,
        url: str,
        body: Any,
    ) -> None:
        if not isinstance(headers, _SignedHeaders):
            return
        if DouYinClient._header_value(headers, "cookie") != headers.signed_cookie:
            raise ManagedDouyinRequestIdentityError(
                "signed Douyin request Cookie changed before dispatch"
            )
        if (
            DouYinClient._header_value(headers, "user-agent")
            != headers.signed_user_agent
        ):
            raise ManagedDouyinRequestIdentityError(
                "signed Douyin request user-agent changed before dispatch"
            )
        if method.upper() != headers.expected_method or url != headers.expected_url:
            raise ManagedDouyinRequestIdentityError(
                "signed Douyin request target changed before dispatch"
            )
        if safe_digest(body if body is not None else "") != headers.expected_body_digest:
            raise ManagedDouyinRequestIdentityError(
                "signed Douyin request body changed before dispatch"
            )

    async def request(self, method, url, **kwargs):
        # Check whether the proxy has expired before each request
        await self._refresh_proxy_if_expired()

        if self.request_environment is not None:
            try:
                self.request_environment.assert_active()
            except PlatformRequestEnvironmentError as exc:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request environment expired"
                ) from exc
            original_headers = kwargs.get("headers")
            if not isinstance(original_headers, dict):
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request headers are missing"
                )
            request_headers: Dict[str, str]
            if isinstance(original_headers, _SignedHeaders):
                request_headers = _SignedHeaders(original_headers)
                for name in (
                    "signed_cookie",
                    "signed_user_agent",
                    "expected_method",
                    "expected_url",
                    "expected_body_digest",
                    "signer_input_digest",
                    "signer_output_digest",
                ):
                    setattr(request_headers, name, getattr(original_headers, name))
            else:
                request_headers = dict(original_headers)
            kwargs["headers"] = request_headers
            body = kwargs.get("data", kwargs.get("content", kwargs.get("json")))
            self._validate_signed_headers(
                request_headers,
                method=method,
                url=url,
                body=body,
            )
            self._validate_managed_headers(request_headers)

        async with make_async_client(proxy=self.proxy) as client:
            response = await client.request(method, url, timeout=self.timeout, **kwargs)
        if self.request_environment is not None:
            self._record_safe_request_proof(
                method=method,
                url=url,
                body=kwargs.get("data", kwargs.get("content", kwargs.get("json"))),
                headers=kwargs["headers"],
                response_status=int(response.status_code),
            )
        try:
            if response.text == "" or response.text == "blocked":
                utils.logger.error(f"request params incrr, response.text: {response.text}")
                raise Exception("account blocked")
            return response.json()
        except Exception as e:
            raise DataFetchError(f"{e}, {response.text}")

    async def get(self, uri: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        """
        GET请求
        """
        request_params, request_headers = await self.__process_req_params(
            uri,
            params,
            headers,
        )
        if self.request_environment is not None:
            return await self.request(
                method="GET",
                url=request_headers.expected_url,
                headers=request_headers,
            )
        return await self.request(
            method="GET",
            url=f"{self._host}{uri}",
            params=request_params,
            headers=request_headers,
        )

    async def post(self, uri: str, data: dict, headers: Optional[Dict] = None):
        request_data, request_headers = await self.__process_req_params(
            uri,
            data,
            headers,
            request_method="POST",
        )
        return await self.request(
            method="POST",
            url=f"{self._host}{uri}",
            data=request_data,
            headers=request_headers,
        )

    async def pong(self, browser_context: BrowserContext) -> bool:
        local_storage = await self.playwright_page.evaluate("() => window.localStorage")
        if local_storage.get("HasUserLogin", "") == "1":
            return True

        _, cookie_dict = await utils.convert_browser_context_cookies(
            browser_context,
            urls=self.cookie_urls,
        )
        return cookie_dict.get("LOGIN_STATUS") == "1"

    async def update_cookies(self, browser_context: BrowserContext, urls: Optional[list[str]] = None):
        if self.request_environment is not None:
            raise ManagedDouyinRequestIdentityError(
                "managed Douyin Cookie changed; create a new request resolution"
            )
        cookie_str, cookie_dict = await utils.convert_browser_context_cookies(
            browser_context,
            urls=urls or self.cookie_urls,
        )
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    def _record_safe_request_proof(
        self,
        *,
        method: str,
        url: str,
        body: Any,
        headers: Dict[str, str],
        response_status: int,
    ) -> None:
        if self.request_identity is None:
            raise ManagedDouyinRequestIdentityError(
                "managed Douyin request identity is missing"
            )
        signed = isinstance(headers, _SignedHeaders)
        self._request_sequence += 1
        proof = {
            **self.request_identity.to_safe_dict(),
            "request_index": self._request_sequence,
            "method": method.upper(),
            "target_digest": safe_digest(url),
            "body_digest": safe_digest(body if body is not None else ""),
            "request_header_digest": safe_digest(dict(headers)),
            "signer_input_digest": (
                headers.signer_input_digest
                if signed
                else safe_digest("not_applicable")
            ),
            "signer_output_digest": (
                headers.signer_output_digest
                if signed
                else safe_digest("not_applicable")
            ),
            "signed": signed,
            "response_status": response_status,
            "dispatched_at": datetime.now(timezone.utc).isoformat(),
        }
        self.safe_request_proofs.append(proof)
        if len(self.safe_request_proofs) > 32:
            self.safe_request_proofs = [
                self.safe_request_proofs[0],
                *self.safe_request_proofs[-31:],
            ]
        if os.environ.get(REQUEST_RESULT_PATH_ENV_NAME):
            try:
                append_platform_request_dispatch_proof(
                    self.request_identity.environment,
                    proof,
                )
            except PlatformRequestEnvironmentError as exc:
                raise ManagedDouyinRequestIdentityError(
                    "managed Douyin request proof persistence failed"
                ) from exc

    async def search_info_by_keyword(
        self,
        keyword: str,
        offset: int = 0,
        search_channel: SearchChannelType = SearchChannelType.GENERAL,
        sort_type: SearchSortType = SearchSortType.GENERAL,
        publish_time: PublishTimeType = PublishTimeType.UNLIMITED,
        search_id: str = "",
    ):
        """
        DouYin Web Search API
        :param keyword:
        :param offset:
        :param search_channel:
        :param sort_type:
        :param publish_time: ·
        :param search_id: ·
        :return:
        """
        query_params = {
            'search_channel': search_channel.value,
            'enable_history': '1',
            'keyword': keyword,
            'search_source': 'tab_search',
            'query_correct_type': '1',
            'is_filter_search': '0',
            'from_group_id': '7378810571505847586',
            'offset': offset,
            'count': '15',
            'need_filter_settings': '1',
            'list_type': 'multi',
            'search_id': search_id,
        }
        if sort_type.value != SearchSortType.GENERAL.value or publish_time.value != PublishTimeType.UNLIMITED.value:
            query_params["filter_selected"] = json.dumps({"sort_type": str(sort_type.value), "publish_time": str(publish_time.value)})
            query_params["is_filter_search"] = 1
            query_params["search_source"] = "tab_search"
        referer_url = f"https://www.douyin.com/search/{keyword}?aid=f594bbd9-a0e2-4651-9319-ebe3cb6298c1&type=general"
        headers = copy.copy(self.headers)
        headers["Referer"] = urllib.parse.quote(referer_url, safe=':/')
        return await self.get("/aweme/v1/web/general/search/single/", query_params, headers=headers)

    async def get_video_by_id(self, aweme_id: str) -> Any:
        """
        DouYin Video Detail API
        :param aweme_id:
        :return:
        """
        params = {"aweme_id": aweme_id}
        headers = copy.copy(self.headers)
        del headers["Origin"]
        res = await self.get("/aweme/v1/web/aweme/detail/", params, headers)
        return res.get("aweme_detail", {})

    async def get_aweme_comments(self, aweme_id: str, cursor: int = 0):
        """get note comments

        """
        uri = "/aweme/v1/web/comment/list/"
        params = {"aweme_id": aweme_id, "cursor": cursor, "count": 20, "item_type": 0}
        keywords = request_keyword_var.get()
        referer_url = "https://www.douyin.com/search/" + keywords + '?aid=3a3cec5a-9e27-4040-b6aa-ef548c2c1138&publish_time=0&sort_type=0&source=search_history&type=general'
        headers = copy.copy(self.headers)
        headers["Referer"] = urllib.parse.quote(referer_url, safe=':/')
        return await self.get(uri, params)

    async def get_sub_comments(self, aweme_id: str, comment_id: str, cursor: int = 0):
        """
            获取子评论
        """
        uri = "/aweme/v1/web/comment/list/reply/"
        params = {
            'comment_id': comment_id,
            "cursor": cursor,
            "count": 20,
            "item_type": 0,
            "item_id": aweme_id,
        }
        keywords = request_keyword_var.get()
        referer_url = "https://www.douyin.com/search/" + keywords + '?aid=3a3cec5a-9e27-4040-b6aa-ef548c2c1138&publish_time=0&sort_type=0&source=search_history&type=general'
        headers = copy.copy(self.headers)
        headers["Referer"] = urllib.parse.quote(referer_url, safe=':/')
        return await self.get(uri, params)

    async def get_aweme_all_comments(
        self,
        aweme_id: str,
        crawl_interval: float = 1.0,
        is_fetch_sub_comments=False,
        callback: Optional[Callable] = None,
        max_count: int = 10,
    ):
        """
        获取帖子的所有评论，包括子评论
        :param aweme_id: 帖子ID
        :param crawl_interval: 抓取间隔
        :param is_fetch_sub_comments: 是否抓取子评论
        :param callback: 回调函数，用于处理抓取到的评论
        :param max_count: 一次帖子爬取的最大评论数量
        :return: 评论列表
        """
        result = []
        comments_has_more = 1
        comments_cursor = 0
        while comments_has_more and len(result) < max_count:
            comments_res = await self.get_aweme_comments(aweme_id, comments_cursor)
            comments_has_more = comments_res.get("has_more", 0)
            comments_cursor = comments_res.get("cursor", 0)
            comments = comments_res.get("comments", [])
            if not comments:
                continue
            if len(result) + len(comments) > max_count:
                comments = comments[:max_count - len(result)]
            result.extend(comments)
            if callback:  # If there is a callback function, execute the callback function
                await callback(aweme_id, comments)

            await asyncio.sleep(crawl_interval)
            if not is_fetch_sub_comments:
                continue
            # Get secondary reviews
            for comment in comments:
                reply_comment_total = comment.get("reply_comment_total")

                if reply_comment_total > 0:
                    comment_id = comment.get("cid")
                    sub_comments_has_more = 1
                    sub_comments_cursor = 0

                    while sub_comments_has_more:
                        sub_comments_res = await self.get_sub_comments(aweme_id, comment_id, sub_comments_cursor)
                        sub_comments_has_more = sub_comments_res.get("has_more", 0)
                        sub_comments_cursor = sub_comments_res.get("cursor", 0)
                        sub_comments = sub_comments_res.get("comments", [])

                        if not sub_comments:
                            continue
                        result.extend(sub_comments)
                        if callback:  # If there is a callback function, execute the callback function
                            await callback(aweme_id, sub_comments)
                        await asyncio.sleep(crawl_interval)
        return result

    async def get_user_info(self, sec_user_id: str):
        uri = "/aweme/v1/web/user/profile/other/"
        params = {
            "sec_user_id": sec_user_id,
            "publish_video_strategy_type": 2,
            "personal_center_strategy": 1,
        }
        return await self.get(uri, params)

    async def get_user_aweme_posts(self, sec_user_id: str, max_cursor: str = "") -> Dict:
        uri = "/aweme/v1/web/aweme/post/"
        verify_fp = (
            self.request_identity.verify_fp
            if self.request_identity is not None
            else str(self.cookie_dict.get("s_v_web_id") or "")
        )
        params = {
            "sec_user_id": sec_user_id,
            "count": 18,
            "max_cursor": max_cursor,
            "locate_query": "false",
            "publish_video_strategy_type": 2,
        }
        if verify_fp:
            params["verifyFp"] = verify_fp
            params["fp"] = verify_fp
        return await self.get(uri, params)

    async def get_all_user_aweme_posts(self, sec_user_id: str, callback: Optional[Callable] = None):
        posts_has_more = 1
        max_cursor = ""
        result = []
        while posts_has_more == 1:
            aweme_post_res = await self.get_user_aweme_posts(sec_user_id, max_cursor)
            posts_has_more = aweme_post_res.get("has_more", 0)
            max_cursor = aweme_post_res.get("max_cursor")
            aweme_list = aweme_post_res.get("aweme_list") if aweme_post_res.get("aweme_list") else []
            utils.logger.info(f"[DouYinClient.get_all_user_aweme_posts] get sec_user_id:{sec_user_id} video len : {len(aweme_list)}")
            if callback:
                await callback(aweme_list)
            result.extend(aweme_list)
        return result

    async def get_aweme_media(self, url: str) -> Union[bytes, None]:
        async with make_async_client(proxy=self.proxy) as client:
            try:
                response = await client.request("GET", url, timeout=self.timeout, follow_redirects=True)
                response.raise_for_status()
                if not response.reason_phrase == "OK":
                    utils.logger.error(f"[DouYinClient.get_aweme_media] request {url} err, res:{response.text}")
                    return None
                else:
                    return response.content
            except httpx.HTTPError as exc:  # some wrong when call httpx.request method, such as connection error, client error, server error or response status code is not 2xx
                utils.logger.error(f"[DouYinClient.get_aweme_media] {exc.__class__.__name__} for {exc.request.url} - {exc}")  # Keep the original exception type name for developers to debug
                return None

    async def resolve_short_url(self, short_url: str) -> str:
        """
        解析抖音短链接,获取重定向后的真实URL
        Args:
            short_url: 短链接,如 https://v.douyin.com/iF12345ABC/
        Returns:
            重定向后的完整URL
        """
        async with make_async_client(proxy=self.proxy, follow_redirects=False) as client:
            try:
                utils.logger.info(f"[DouYinClient.resolve_short_url] Resolving short URL: {short_url}")
                response = await client.get(short_url, timeout=10)

                # Short links usually return a 302 redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    redirect_url = response.headers.get("Location", "")
                    utils.logger.info(f"[DouYinClient.resolve_short_url] Resolved to: {redirect_url}")
                    return redirect_url
                else:
                    utils.logger.warning(f"[DouYinClient.resolve_short_url] Unexpected status code: {response.status_code}")
                    return ""
            except Exception as e:
                utils.logger.error(f"[DouYinClient.resolve_short_url] Failed to resolve short URL: {e}")
                return ""
