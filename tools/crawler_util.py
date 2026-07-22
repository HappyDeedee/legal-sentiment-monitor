# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools/crawler_util.py
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
# @Author  : relakkes@gmail.com
# @Time    : 2023/12/2 12:53
# @Desc    : Crawler utility functions

import base64
import json
import random
import re
import urllib
import urllib.parse
import uuid
from io import BytesIO
from typing import Dict, List, Optional, Tuple, cast

import httpx
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageShow
from playwright.async_api import BrowserContext, Cookie, Page

from . import utils
from .httpx_util import make_async_client


async def find_login_qrcode(page: Page, selector: str) -> str:
    """find login qrcode image from target selector"""
    try:
        elements = await page.wait_for_selector(
            selector=selector,
        )
        for source in await _login_qrcode_image_sources(page, elements):
            login_qrcode_img = await _login_qrcode_source_to_base64(page, source)
            if is_qrcode_image_data(login_qrcode_img):
                return login_qrcode_img
        screenshot = await _login_qrcode_element_screenshot(elements)
        return screenshot if is_qrcode_image_data(screenshot) else ""

    except Exception as e:
        print(e)
        return ""


async def _login_qrcode_image_sources(page: Page, element) -> List[str]:
    sources: List[str] = []
    for attr in ("src", "currentSrc", "data-src"):
        try:
            value = await element.get_attribute(attr)
            if value:
                sources.append(str(value))
        except Exception:
            continue
    try:
        value = await element.evaluate(
            """el => {
                const style = window.getComputedStyle(el);
                const bg = style && style.backgroundImage ? style.backgroundImage : '';
                const match = bg.match(/url\\(["']?(.*?)["']?\\)/);
                return el.currentSrc || el.src || el.getAttribute('src') || el.getAttribute('data-src') || (match ? match[1] : '');
            }"""
        )
        if value:
            sources.append(str(value))
    except Exception:
        pass

    cleaned: List[str] = []
    for source in sources:
        source = str(source or "").strip()
        if not source or source.startswith("JSHandle@"):
            continue
        if source not in cleaned:
            cleaned.append(source)
    return cleaned


async def _login_qrcode_source_to_base64(page: Page, source: str) -> str:
    source = str(source or "").strip()
    if not source:
        return ""
    if source.startswith("data:image"):
        return _strip_data_url(source)
    if source.startswith("blob:"):
        return _strip_data_url(await _login_qrcode_blob_to_data_url(page, source))
    source = await _login_qrcode_absolute_url(page, source)
    if source.startswith("http://") or source.startswith("https://"):
        return await _fetch_login_qrcode_image(page, source)
    return ""


async def _login_qrcode_absolute_url(page: Page, source: str) -> str:
    if source.startswith("//"):
        return "https:" + source
    if source.startswith("http://") or source.startswith("https://") or source.startswith("data:image") or source.startswith("blob:"):
        return source
    try:
        return await page.evaluate("(src) => new URL(src, location.href).toString()", source)
    except Exception:
        return source


async def _fetch_login_qrcode_image(page: Page, source: str) -> str:
    try:
        response = await page.context.request.get(source, headers={"User-Agent": get_user_agent()})
        if getattr(response, "ok", False):
            utils.logger.info("[find_login_qrcode] fetched candidate image by browser request")
            return base64.b64encode(await response.body()).decode("utf-8")
    except Exception:
        pass
    try:
        async with make_async_client(follow_redirects=True) as client:
            utils.logger.info("[find_login_qrcode] fetched candidate image by URL")
            resp = await client.get(source, headers={"User-Agent": get_user_agent()})
            if resp.status_code == 200:
                return base64.b64encode(resp.content).decode("utf-8")
            raise Exception(f"fetch login image url failed, response message:{resp.text}")
    except Exception:
        return ""


async def _login_qrcode_blob_to_data_url(page: Page, source: str) -> str:
    try:
        return await page.evaluate(
            """async (src) => {
                const response = await fetch(src);
                const blob = await response.blob();
                const buffer = await blob.arrayBuffer();
                let binary = '';
                const bytes = new Uint8Array(buffer);
                for (let i = 0; i < bytes.byteLength; i += 1) binary += String.fromCharCode(bytes[i]);
                return `data:${blob.type || 'image/png'};base64,${btoa(binary)}`;
            }""",
            source,
        )
    except Exception:
        return ""


async def _login_qrcode_element_screenshot(element) -> str:
    try:
        screenshot = await element.screenshot()
        return base64.b64encode(screenshot).decode("utf-8")
    except Exception:
        return ""


def is_qrcode_image_data(image_data: str) -> bool:
    """Return true only when decoded image bytes contain a detectable QR code."""

    source = _strip_data_url(str(image_data or "").strip())
    if not source:
        return False
    try:
        encoded = "".join(source.split())
        if len(encoded) > 8 * 1024 * 1024:
            return False
        content = base64.b64decode(encoded, validate=True)
        if not content or len(content) > 6 * 1024 * 1024:
            return False
        image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        if image is None:
            return False
        height, width = image.shape[:2]
        if min(width, height) < 64 or max(width, height) > 4096:
            return False
        detector = cv2.QRCodeDetector()
        detected, points = detector.detect(image)
        if not detected or points is None:
            quiet_zone = max(4, int(round(min(width, height) * 0.125)))
            padded = cv2.copyMakeBorder(
                image,
                quiet_zone,
                quiet_zone,
                quiet_zone,
                quiet_zone,
                cv2.BORDER_CONSTANT,
                value=255,
            )
            detected, points = detector.detect(padded)
        return bool(detected and points is not None)
    except (ValueError, cv2.error):
        return False


def _strip_data_url(source: str) -> str:
    source = str(source or "").strip()
    if ";base64," not in source:
        return source
    return source.split(";base64,", 1)[1]


async def find_qrcode_img_from_canvas(page: Page, canvas_selector: str) -> str:
    """
    find qrcode image from canvas element
    Args:
        page:
        canvas_selector:

    Returns:

    """

    # Wait for Canvas element to load
    canvas = await page.wait_for_selector(canvas_selector)

    # Take screenshot of Canvas element
    screenshot = await canvas.screenshot()

    # Convert screenshot to base64 format
    base64_image = base64.b64encode(screenshot).decode('utf-8')
    return base64_image


def show_qrcode(qr_code) -> None:  # type: ignore
    """parse base64 encode qrcode image and show it"""
    if "," in qr_code:
        qr_code = qr_code.split(",")[1]
    qr_code = base64.b64decode(qr_code)
    image = Image.open(BytesIO(qr_code))

    # Add a square border around the QR code and display it within the border to improve scanning accuracy.
    width, height = image.size
    new_image = Image.new('RGB', (width + 20, height + 20), color=(255, 255, 255))
    new_image.paste(image, (10, 10))
    draw = ImageDraw.Draw(new_image)
    draw.rectangle((0, 0, width + 19, height + 19), outline=(0, 0, 0), width=1)
    del ImageShow.UnixViewer.options["save_all"]
    new_image.show()


def get_user_agent() -> str:
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.5112.79 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5060.53 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5112.79 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5060.53 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4844.84 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5112.79 Safari/537.36"
    ]
    return random.choice(ua_list)


def get_mobile_user_agent() -> str:
    ua_list = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(ua_list)


def convert_cookies(cookies: Optional[List[Cookie]]) -> Tuple[str, Dict]:
    if not cookies:
        return "", {}
    cookies_str = ";".join([f"{cookie.get('name')}={cookie.get('value')}" for cookie in cookies])
    cookie_dict = dict()
    for cookie in cookies:
        cookie_dict[cookie.get('name')] = cookie.get('value')
    return cookies_str, cookie_dict


class ManagedCookieSelectionError(ValueError):
    """The browser request Cookie proof is missing or conflicts with its store."""


def _canonical_browser_cookie_header(
    cookie_header: str,
    cookies: Optional[List[Cookie]],
) -> Tuple[str, Dict]:
    available = []
    seen_pairs: set[tuple[str, str]] = set()
    nameless_values: set[str] = set()
    for cookie in cookies or []:
        name = str(cookie.get("name") or "").strip()
        value = str(cookie.get("value") or "")
        if not name:
            nameless_values.add(value)
            continue
        pair = (name, value)
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            available.append((f"{name}={value}", name, value))
    available.sort(key=lambda item: len(item[0]), reverse=True)

    raw_header = str(cookie_header or "")
    cookie_dict: Dict[str, str] = {}
    ordered: list[tuple[str, str]] = []
    position = 0
    while position < len(raw_header):
        while position < len(raw_header) and raw_header[position] in " \t":
            position += 1
        if position >= len(raw_header):
            break
        matched = next(
            (
                item
                for item in available
                if raw_header.startswith(item[0], position)
                and (
                    position + len(item[0]) == len(raw_header)
                    or raw_header[position + len(item[0])] == ";"
                )
            ),
            None,
        )
        if matched is None:
            delimiter_position = raw_header.find(";", position)
            segment_end = (
                len(raw_header) if delimiter_position < 0 else delimiter_position
            )
            segment = raw_header[position:segment_end].strip()
            if "=" not in segment:
                if segment in nameless_values:
                    position = (
                        len(raw_header)
                        if delimiter_position < 0
                        else delimiter_position + 1
                    )
                    continue
                raise ManagedCookieSelectionError(
                    "managed browser cookie request proof name-only segment"
                )
            segment_name, _ = segment.split("=", 1)
            segment_name = segment_name.strip()
            if not segment_name:
                raise ManagedCookieSelectionError(
                    "managed browser cookie request proof empty-name segment"
                )
            known_names = {item[1] for item in available}
            reason = (
                "managed browser cookie request proof value mismatch"
                if segment_name in known_names
                else "managed browser cookie request proof name mismatch"
            )
            raise ManagedCookieSelectionError(reason)
        token, name, value = matched
        if name not in cookie_dict:
            cookie_dict[name] = value
            ordered.append((name, value))
        position += len(token)
        if position == len(raw_header):
            break
        if raw_header[position] != ";":
            raise ManagedCookieSelectionError(
                "managed browser cookie request proof malformed"
            )
        position += 1
    return ";".join(f"{name}={value}" for name, value in ordered), cookie_dict


async def _capture_browser_cookie_proof(
    browser_context: BrowserContext,
    request_url: str,
) -> Tuple[str, List[Cookie]]:
    parsed = urllib.parse.urlsplit(str(request_url or ""))
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ManagedCookieSelectionError("managed cookie request URL invalid")
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("__mediacrawler_cookie_probe__", uuid.uuid4().hex))
    probe_url = urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path or "/",
            urllib.parse.urlencode(query),
            "",
        )
    )
    page = await browser_context.new_page()
    captured: dict[str, object] = {
        "seen": False,
        "cookie": "",
        "cookies": [],
    }

    async def capture(route) -> None:
        headers = await route.request.all_headers()
        cookie_header = next(
            (
                str(value)
                for name, value in headers.items()
                if str(name).casefold() == "cookie"
            ),
            "",
        )
        structured_cookies = await browser_context.cookies(urls=[probe_url])
        captured["cookie"] = cookie_header
        captured["cookies"] = structured_cookies
        captured["seen"] = True
        await route.abort()

    route_registered = False
    try:
        await page.route(probe_url, capture)
        route_registered = True
        try:
            await page.goto(probe_url, wait_until="commit", timeout=5000)
        except Exception:
            if not captured["seen"]:
                raise ManagedCookieSelectionError(
                    "managed browser cookie request proof missing"
                )
    finally:
        cleanup_failed = False
        if route_registered:
            try:
                await page.unroute(probe_url, capture)
            except Exception:
                cleanup_failed = True
        try:
            await page.close()
        except Exception:
            cleanup_failed = True
        if cleanup_failed:
            raise ManagedCookieSelectionError(
                "managed browser cookie request proof cleanup failed"
            )
    if not captured["seen"]:
        raise ManagedCookieSelectionError(
            "managed browser cookie request proof missing"
        )
    return str(captured["cookie"]), cast(List[Cookie], captured["cookies"])


async def convert_browser_context_cookies(
    browser_context: BrowserContext, urls: Optional[List[str]] = None
) -> Tuple[str, Dict]:
    cookies = (
        await browser_context.cookies(urls=urls)
        if urls
        else await browser_context.cookies()
    )
    return convert_cookies(cookies)


async def convert_browser_context_cookies_for_request(
    browser_context: BrowserContext,
    request_url: str,
) -> Tuple[str, Dict]:
    cookie_header, cookies = await _capture_browser_cookie_proof(
        browser_context,
        request_url,
    )
    return _canonical_browser_cookie_header(cookie_header, cookies)


def convert_str_cookie_to_dict(cookie_str: str) -> Dict:
    cookie_dict: Dict[str, str] = dict()
    if not cookie_str:
        return cookie_dict
    for cookie in cookie_str.split(";"):
        cookie = cookie.strip()
        if not cookie:
            continue
        cookie_list = cookie.split("=")
        if len(cookie_list) != 2:
            continue
        cookie_value = cookie_list[1]
        if isinstance(cookie_value, list):
            cookie_value = "".join(cookie_value)
        cookie_dict[cookie_list[0]] = cookie_value
    return cookie_dict


def match_interact_info_count(count_str: str) -> int:
    if not count_str:
        return 0

    match = re.search(r'\d+', count_str)
    if match:
        number = match.group()
        return int(number)
    else:
        return 0


def format_proxy_info(ip_proxy_info) -> Tuple[Optional[Dict], Optional[str]]:
    """format proxy info for playwright and httpx"""
    # fix circular import issue
    from proxy.proxy_ip_pool import IpInfoModel
    ip_proxy_info = cast(IpInfoModel, ip_proxy_info)

    # Playwright proxy server should be in format "host:port" without protocol prefix
    server = f"{ip_proxy_info.ip}:{ip_proxy_info.port}"
    
    playwright_proxy = {
        "server": server,
    }
    
    # Only add username and password if they are not empty
    if ip_proxy_info.user and ip_proxy_info.password:
        playwright_proxy["username"] = ip_proxy_info.user
        playwright_proxy["password"] = ip_proxy_info.password
    
    # httpx 0.28.1 requires passing proxy URL string directly, not a dictionary
    if ip_proxy_info.user and ip_proxy_info.password:
        httpx_proxy = f"http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
    else:
        httpx_proxy = f"http://{ip_proxy_info.ip}:{ip_proxy_info.port}"
    return playwright_proxy, httpx_proxy


def extract_text_from_html(html: str) -> str:
    """Extract text from HTML, removing all tags."""
    if not html:
        return ""

    # Remove script and style elements
    clean_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
    # Remove all other tags
    clean_text = re.sub(r'<[^>]+>', '', clean_html).strip()
    return clean_text

def extract_url_params_to_dict(url: str) -> Dict:
    """Extract URL parameters to dict"""
    url_params_dict = dict()
    if not url:
        return url_params_dict
    parsed_url = urllib.parse.urlparse(url)
    url_params_dict = dict(urllib.parse.parse_qsl(parsed_url.query))
    return url_params_dict
