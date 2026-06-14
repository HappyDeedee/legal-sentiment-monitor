# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/media_platform/kuaishou/login.py
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
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from tools import utils


class KuaishouLogin(AbstractLogin):
    LOGIN_URL = "https://www.kuaishou.com/?isHome=1"
    LOGIN_BUTTON_SELECTOR = "xpath=//p[text()='登录']"
    QRCODE_SELECTOR = "xpath=//div[@class='qrcode-img']//img"
    QRCODE_CAPTURE_METHOD = "tools.utils.find_login_qrcode"
    QRCODE_FLOW_STEPS = (
        "打开 LOGIN_URL",
        "点击 LOGIN_BUTTON_SELECTOR",
        "调用 tools.utils.find_login_qrcode(context_page, QRCODE_SELECTOR) 获取二维码",
        "使用 check_login_state 的 passToken Cookie 规则轮询登录结果",
    )
    LOGIN_STATE_COOKIE_RULES = {"passToken": None}
    SUPPORTED_LOGIN_TYPES = ("qrcode", "cookie")
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
            "[class*='slider']",
            "[id*='slider']",
            "[class*='drag']",
            "[id*='drag']",
            "[class*='slide']",
            "[id*='slide']",
            "[class*='kwai-captcha']",
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
            "iframe[src*='kuaishou'][src*='captcha']",
            "iframe[src*='kuaishou'][src*='verify']",
            "[class*='captcha-container']",
        ),
    }

    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str] = "",
                 cookie_str: str = ""
                 ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    async def begin(self):
        """Start login xiaohongshu"""
        utils.logger.info("[KuaishouLogin.begin] Begin login kuaishou ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError("[KuaishouLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
            Check if the current login status is successful and return True otherwise return False
            retry decorator will retry 20 times if the return value is False, and the retry interval is 1 second
            if max retry times reached, raise RetryError
        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        kuaishou_pass_token = cookie_dict.get("passToken")
        if kuaishou_pass_token:
            return True
        return False

    async def login_by_qrcode(self):
        """login kuaishou website and keep webdriver login state"""
        utils.logger.info("[KuaishouLogin.login_by_qrcode] Begin login kuaishou by qrcode ...")

        # click login button
        login_button_ele = self.context_page.locator(
            self.LOGIN_BUTTON_SELECTOR
        )
        await login_button_ele.click()

        # find login qrcode
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page,
            selector=self.QRCODE_SELECTOR
        )
        if not base64_qrcode_img:
            utils.logger.info("[KuaishouLogin.login_by_qrcode] login failed , have not found qrcode please check ....")
            sys.exit()


        # show login qrcode
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] waiting for scan code login, remaining time is 20s")
        try:
            await self.check_login_state()
        except RetryError:
            utils.logger.info("[KuaishouLogin.login_by_qrcode] Login kuaishou failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[KuaishouLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def prepare_qrcode_login(self, timeout_ms: int = 10000) -> None:
        """Prepare the MediaCrawler Kuaishou QR login dialog without waiting for scan completion."""
        login_button_ele = self.context_page.locator(
            self.LOGIN_BUTTON_SELECTOR
        )
        await login_button_ele.click(timeout=timeout_ms)

    async def capture_qrcode(self) -> str:
        """Capture the login QR image using MediaCrawler's QR utility."""
        return await utils.find_login_qrcode(
            self.context_page,
            selector=self.QRCODE_SELECTOR
        )

    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        utils.logger.info("[KuaishouLogin.login_by_cookies] Begin login kuaishou by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            await self.browser_context.add_cookies([{
                'name': key,
                'value': value,
                'domain': ".kuaishou.com",
                'path': "/"
            }])
