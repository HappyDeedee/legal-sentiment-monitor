# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/douyin/login.py
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
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from cache.cache_factory import CacheFactory
from tools import utils


class DouYinLogin(AbstractLogin):
    LOGIN_URL = "https://www.douyin.com"
    LOGIN_DIALOG_SELECTOR = "xpath=//div[@id='login-panel-new']"
    LOGIN_BUTTON_SELECTOR = "button:has-text('登录')"
    LOGIN_BUTTON_FALLBACK_SELECTORS = (
        "button:has-text('登录')",
        "xpath=//button[contains(., '登录')]",
        "xpath=//p[text() = '登录']",
        "xpath=//*[normalize-space()='登录' and (self::button or self::div or self::p or self::span)]",
    )
    QRCODE_SELECTOR = "xpath=//div[@id='animate_qrcode_container']//img"
    QRCODE_CAPTURE_METHOD = "tools.utils.find_login_qrcode"
    QRCODE_FLOW_STEPS = (
        "打开 LOGIN_URL",
        "等待 LOGIN_DIALOG_SELECTOR；未出现时点击 LOGIN_BUTTON_SELECTOR 或兼容入口",
        "调用 tools.utils.find_login_qrcode(context_page, QRCODE_SELECTOR) 获取二维码",
        "使用 check_login_state 的 Cookie/localStorage 规则轮询登录结果",
    )
    LOGIN_STATE_COOKIE_RULES = {"LOGIN_STATUS": "1"}
    LOGIN_STATE_LOCAL_STORAGE_RULES = {"HasUserLogin": "1"}
    SUPPORTED_LOGIN_TYPES = ("qrcode", "phone", "cookie")
    MANUAL_VERIFICATION_URL_MARKERS = ("captcha", "verify", "challenge", "risk")
    MANUAL_VERIFICATION_LABELS = {
        "slider": "滑块验证",
        "sms": "短信验证码",
        "captcha": "图形/安全验证码",
    }
    MANUAL_VERIFICATION_TEXT_MARKERS = {
        "slider": (
            "滑块",
            "滑动",
            "请按住滑块",
            "按住滑块",
            "拖动滑块",
            "拖动下方滑块",
            "拖动滑块完成拼图",
            "请拖动滑块完成拼图",
            "请拖动滑块完成验证",
            "拖动滑块完成验证",
            "拖动滑块至正确位置",
            "向右拖动",
            "完成拼图",
        ),
        "sms": (
            "短信验证码",
            "手机验证码",
            "输入验证码",
            "请输入验证码",
            "获取验证码",
            "验证码已发送",
            "重新获取验证码",
            "发送验证码",
        ),
        "captcha": (
            "安全验证",
            "安全检测",
            "风险验证",
            "智能验证",
            "验证中间页",
            "验证码中间页",
            "请通过验证",
            "请完成验证",
            "请完成安全验证",
            "完成验证",
            "安全校验",
            "身份验证",
            "环境存在风险",
            "验证失败",
            "环境异常",
            "verify",
            "captcha",
        ),
    }
    MANUAL_VERIFICATION_SELECTORS = {
        "slider": (
            "#captcha-verify-image",
            "#captcha_container",
            "[class*='slider']",
            "[id*='slider']",
            "[class*='drag']",
            "[id*='drag']",
            "[class*='slide']",
            "[id*='slide']",
        ),
        "captcha": (
            "[class*='captcha']",
            "[id*='captcha']",
            "[class*='verify']",
            "[id*='verify']",
            "[class*='security']",
            "[id*='security']",
            "[class*='safe']",
            "[id*='safe']",
            "[class*='challenge']",
            "[id*='challenge']",
            "[class*='risk']",
            "[id*='risk']",
            "iframe[src*='captcha']",
            "iframe[src*='verify']",
            "iframe[src*='challenge']",
            "iframe[src*='risk']",
            "iframe[src*='slide']",
            "iframe[src*='security']",
        ),
    }

    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext, # type: ignore
                 context_page: Page, # type: ignore
                 login_phone: Optional[str] = "",
                 cookie_str: Optional[str] = ""
                 ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.scan_qrcode_time = 60
        self.cookie_str = cookie_str

    async def begin(self):
        """
            Start login douyin website
            The verification accuracy of the slider verification is not very good... If there are no special requirements, it is recommended not to use Douyin login, or use cookie login
        """

        # popup login dialog
        await self.popup_login_dialog()

        # select login type
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[DouYinLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

        # If the page redirects to the slider verification page, need to slide again
        await asyncio.sleep(6)
        current_page_title = await self.context_page.title()
        if "验证码中间页" in current_page_title:
            await self.check_page_display_slider(move_step=3, slider_level="hard")

        # check login state
        utils.logger.info(f"[DouYinLogin.begin] login finished then check login state ...")
        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info("[DouYinLogin.begin] login failed please confirm ...")
            sys.exit()

        # wait for redirect
        wait_redirect_seconds = 5
        utils.logger.info(f"[DouYinLogin.begin] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self):
        """Check if the current login status is successful and return True otherwise return False"""
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)

        for page in self.browser_context.pages:
            try:
                local_storage = await page.evaluate("() => window.localStorage")
                if local_storage.get("HasUserLogin", "") == "1":
                    return True
            except Exception as e:
                # utils.logger.warn(f"[DouYinLogin] check_login_state waring: {e}")
                await asyncio.sleep(0.1)

        if cookie_dict.get("LOGIN_STATUS") == "1":
            return True

        return False

    async def popup_login_dialog(self):
        """If the login dialog box does not pop up automatically, we will manually click the login button"""
        try:
            # check dialog box is auto popup and wait for 10 seconds
            await self.context_page.wait_for_selector(self.LOGIN_DIALOG_SELECTOR, timeout=1000 * 10)
        except Exception as e:
            utils.logger.error(f"[DouYinLogin.popup_login_dialog] login dialog box does not pop up automatically, error: {e}")
            utils.logger.info("[DouYinLogin.popup_login_dialog] login dialog box does not pop up automatically, we will manually click the login button")
            await self.click_login_button()
            await asyncio.sleep(0.5)

    async def prepare_qrcode_login(self, timeout_ms: int = 10000) -> None:
        """Prepare the MediaCrawler Douyin QR login dialog without waiting for scan completion."""
        try:
            await self.context_page.wait_for_selector(self.LOGIN_DIALOG_SELECTOR, timeout=timeout_ms)
        except Exception as e:
            utils.logger.error(f"[DouYinLogin.prepare_qrcode_login] login dialog box does not pop up automatically, error: {e}")
            await self.click_login_button(timeout_ms=timeout_ms)
            await asyncio.sleep(0.5)

    async def click_login_button(self, timeout_ms: int = 10000) -> None:
        """Click the current Douyin web login entry, with legacy selectors as fallback."""
        last_error: Exception | None = None
        for selector in self.LOGIN_BUTTON_FALLBACK_SELECTORS:
            try:
                login_button_ele = self.context_page.locator(selector).first
                if not await login_button_ele.count():
                    continue
                if not await login_button_ele.is_visible(timeout=500):
                    continue
                await login_button_ele.click(timeout=timeout_ms)
                return
            except Exception as e:
                last_error = e
                continue
        if last_error:
            raise last_error
        raise PlaywrightTimeoutError("Douyin login button not found")

    async def capture_qrcode(self) -> str:
        """Capture the login QR image using MediaCrawler's QR utility."""
        return await utils.find_login_qrcode(
            self.context_page,
            selector=self.QRCODE_SELECTOR
        )

    async def login_by_qrcode(self):
        utils.logger.info("[DouYinLogin.login_by_qrcode] Begin login douyin by qrcode...")
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page,
            selector=self.QRCODE_SELECTOR
        )
        if not base64_qrcode_img:
            utils.logger.info("[DouYinLogin.login_by_qrcode] login qrcode not found please confirm ...")
            sys.exit()

        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)
        await asyncio.sleep(2)

    async def login_by_mobile(self):
        utils.logger.info("[DouYinLogin.login_by_mobile] Begin login douyin by mobile ...")
        mobile_tap_ele = self.context_page.locator("xpath=//li[text() = '验证码登录']")
        await mobile_tap_ele.click()
        await self.context_page.wait_for_selector("xpath=//article[@class='web-login-mobile-code']")
        mobile_input_ele = self.context_page.locator("xpath=//input[@placeholder='手机号']")
        await mobile_input_ele.fill(self.login_phone)
        await asyncio.sleep(0.5)
        send_sms_code_btn = self.context_page.locator("xpath=//span[text() = '获取验证码']")
        await send_sms_code_btn.click()

        # Check if there is slider verification
        await self.check_page_display_slider(move_step=10, slider_level="easy")
        cache_client = CacheFactory.create_cache(config.CACHE_TYPE_MEMORY)
        max_get_sms_code_time = 60 * 2  # Maximum time to get verification code is 2 minutes
        while max_get_sms_code_time > 0:
            utils.logger.info(f"[DouYinLogin.login_by_mobile] get douyin sms code from redis remaining time {max_get_sms_code_time}s ...")
            await asyncio.sleep(1)
            sms_code_key = f"dy_{self.login_phone}"
            sms_code_value = cache_client.get(sms_code_key)
            if not sms_code_value:
                max_get_sms_code_time -= 1
                continue

            sms_code_input_ele = self.context_page.locator("xpath=//input[@placeholder='请输入验证码']")
            await sms_code_input_ele.fill(value=sms_code_value.decode())
            await asyncio.sleep(0.5)
            submit_btn_ele = self.context_page.locator("xpath=//button[@class='web-login-button']")
            await submit_btn_ele.click()  # Click login
            # todo ... should also check the correctness of the verification code, it may be incorrect
            break

    async def check_page_display_slider(self, move_step: int = 10, slider_level: str = "easy"):
        """
        Check if slider verification appears on the page
        :return:
        """
        # Wait for slider verification to appear
        back_selector = "#captcha-verify-image"
        try:
            await self.context_page.wait_for_selector(selector=back_selector, state="visible", timeout=30 * 1000)
        except PlaywrightTimeoutError:  # No slider verification, return directly
            return

        gap_selector = 'xpath=//*[@id="captcha_container"]/div/div[2]/img[2]'
        max_slider_try_times = 20
        slider_verify_success = False
        while not slider_verify_success:
            if max_slider_try_times <= 0:
                utils.logger.error("[DouYinLogin.check_page_display_slider] slider verify failed ...")
                sys.exit()
            try:
                await self.move_slider(back_selector, gap_selector, move_step, slider_level)
                await asyncio.sleep(1)

                # If the slider is too slow or verification failed, it will prompt "The operation is too slow", click the refresh button here
                page_content = await self.context_page.content()
                if "操作过慢" in page_content or "提示重新操作" in page_content:
                    utils.logger.info("[DouYinLogin.check_page_display_slider] slider verify failed, retry ...")
                    await self.context_page.click(selector="//a[contains(@class, 'secsdk_captcha_refresh')]")
                    continue

                # After successful sliding, wait for the slider to disappear
                await self.context_page.wait_for_selector(selector=back_selector, state="hidden", timeout=1000)
                # If the slider disappears, it means the verification is successful, break the loop. If not, it means the verification failed, the above line will throw an exception and be caught to continue the loop
                utils.logger.info("[DouYinLogin.check_page_display_slider] slider verify success ...")
                slider_verify_success = True
            except Exception as e:
                utils.logger.error(f"[DouYinLogin.check_page_display_slider] slider verify failed, error: {e}")
                await asyncio.sleep(1)
                max_slider_try_times -= 1
                utils.logger.info(f"[DouYinLogin.check_page_display_slider] remaining slider try times: {max_slider_try_times}")
                continue

    async def move_slider(self, back_selector: str, gap_selector: str, move_step: int = 10, slider_level="easy"):
        """
        Move the slider to the right to complete the verification
        :param back_selector: Selector for the slider verification background image
        :param gap_selector:  Selector for the slider verification slider
        :param move_step: Controls the ratio of single movement speed, default is 1, meaning the distance moves in 0.1 seconds no matter how far, larger value means slower
        :param slider_level: Slider difficulty easy hard, corresponding to the slider for mobile verification code and the slider in the middle of verification code
        :return:
        """

        # get slider background image
        slider_back_elements = await self.context_page.wait_for_selector(
            selector=back_selector,
            timeout=1000 * 10,  # wait 10 seconds
        )
        slide_back = str(await slider_back_elements.get_property("src")) # type: ignore

        # get slider gap image
        gap_elements = await self.context_page.wait_for_selector(
            selector=gap_selector,
            timeout=1000 * 10,  # wait 10 seconds
        )
        gap_src = str(await gap_elements.get_property("src")) # type: ignore

        # Identify slider position
        slide_app = utils.Slide(gap=gap_src, bg=slide_back)
        distance = slide_app.discern()

        # Get movement trajectory
        tracks = utils.get_tracks(distance, slider_level)
        new_1 = tracks[-1] - (sum(tracks) - distance)
        tracks.pop()
        tracks.append(new_1)

        # Drag slider to specified position according to trajectory
        element = await self.context_page.query_selector(gap_selector)
        bounding_box = await element.bounding_box() # type: ignore

        await self.context_page.mouse.move(bounding_box["x"] + bounding_box["width"] / 2, # type: ignore
                                           bounding_box["y"] + bounding_box["height"] / 2) # type: ignore
        # Get x coordinate center position
        x = bounding_box["x"] + bounding_box["width"] / 2 # type: ignore
        # Simulate sliding operation
        await element.hover() # type: ignore
        await self.context_page.mouse.down()

        for track in tracks:
            # Loop mouse movement according to trajectory
            # steps controls the ratio of single movement speed, default is 1, meaning the distance moves in 0.1 seconds no matter how far, larger value means slower
            await self.context_page.mouse.move(x + track, 0, steps=move_step)
            x += track
        await self.context_page.mouse.up()

    async def login_by_cookies(self):
        utils.logger.info("[DouYinLogin.login_by_cookies] Begin login douyin by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".douyin.com",
                'path': "/"
            }])
