# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tests/conftest.py
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

"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import smtplib
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Return project root path"""
    return project_root


@pytest.fixture
def sample_xhs_note():
    """Sample Xiaohongshu note data for testing"""
    return {
        "note_id": "test_note_123",
        "type": "normal",
        "title": "Test Title",
        "desc": "This is a test description",
        "video_url": "",
        "time": 1700000000,
        "last_update_time": 1700000000,
        "user_id": "user_123",
        "nickname": "Test User",
        "avatar": "https://example.com/avatar.jpg",
        "liked_count": 100,
        "collected_count": 50,
        "comment_count": 25,
        "share_count": 10,
        "ip_location": "Shanghai",
        "image_list": "https://example.com/img1.jpg,https://example.com/img2.jpg",
        "tag_list": "test,programming,Python",
        "note_url": "https://www.xiaohongshu.com/explore/test_note_123",
        "source_keyword": "test keyword",
        "xsec_token": "test_token_123"
    }


@pytest.fixture(autouse=True)
def smtp_tripwire(monkeypatch):
    if str(os.environ.get("MONITOR_ALLOW_REAL_EMAIL_SEND") or "").strip().lower() in {"1", "true", "yes", "on"}:
        return

    class BlockedSMTP:
        def __init__(self, *args, **kwargs):
            raise AssertionError(
                "Automated tests must not reach real smtplib.SMTP/SMTP_SSL without MONITOR_ALLOW_REAL_EMAIL_SEND=true"
            )

    monkeypatch.setattr(smtplib, "SMTP", BlockedSMTP)
    monkeypatch.setattr(smtplib, "SMTP_SSL", BlockedSMTP)


@pytest.fixture(autouse=True)
def browser_selection_tripwire(monkeypatch, tmp_path):
    from api.monitoring import browser_selection

    monkeypatch.delenv("MONITOR_BROWSER_EXECUTABLE", raising=False)
    monkeypatch.setattr(
        browser_selection,
        "BROWSER_SELECTION_PATH",
        tmp_path / "browser_selection.json",
    )
    monkeypatch.setattr(
        browser_selection,
        "ACCOUNT_PROFILE_ROOT",
        tmp_path / "account_profiles",
    )


def _env_enabled(name, environ=None):
    values = os.environ if environ is None else environ
    return str(values.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _account_identity_tripwire_policy(environ=None):
    required_flags = (
        "TEST_ALLOW_REAL_ACCOUNT_IDENTITY",
        "TEST_ALLOW_REAL_PLATFORM_LOGIN",
    )
    return {
        "blocked": not all(_env_enabled(name, environ) for name in required_flags),
        "proxy_allowed": _env_enabled("TEST_ALLOW_REAL_PROXY", environ),
    }


@pytest.fixture(autouse=True)
def account_identity_tripwire(monkeypatch, tmp_path):
    from api.monitoring import account_check, login_qrcode, runner
    from api.routers import monitor as monitor_router

    synthetic_browser = tmp_path / "tripwire-playwright-chromium.exe"
    synthetic_browser.write_bytes(b"pytest browser tripwire fixture")
    monkeypatch.setattr(
        monitor_router,
        "_playwright_chromium_executable_path",
        lambda: str(synthetic_browser),
    )
    monkeypatch.setattr(
        runner,
        "_playwright_chromium_executable_path",
        lambda: str(synthetic_browser),
    )

    if not os.environ.get("MONITOR_ACCOUNT_IDENTITY_SEED_SALT"):
        monkeypatch.setenv("MONITOR_ACCOUNT_IDENTITY_SEED_SALT", "pytest-disposable-account-identity-salt")

    required_flags = (
        "TEST_ALLOW_REAL_ACCOUNT_IDENTITY",
        "TEST_ALLOW_REAL_PLATFORM_LOGIN",
    )
    policy = _account_identity_tripwire_policy()
    blocked = policy["blocked"]

    if blocked:
        class BlockedAsyncPlaywright:
            async def start(self):
                raise AssertionError(
                    "Automated tests must not reach real account Playwright without "
                    "TEST_ALLOW_REAL_ACCOUNT_IDENTITY=true and "
                    "TEST_ALLOW_REAL_PLATFORM_LOGIN=true"
                )

        monkeypatch.setattr(account_check, "async_playwright", lambda: BlockedAsyncPlaywright())
        monkeypatch.setattr(login_qrcode, "async_playwright", lambda: BlockedAsyncPlaywright())
    elif not policy["proxy_allowed"]:
        original_start = login_qrcode._start_qrcode_login_session_with_profile_once

        async def guarded_proxy_start(*args, **kwargs):
            command = kwargs.get("command") or (args[2] if len(args) > 2 else {})
            if isinstance(command, dict) and command.get("proxy_url"):
                raise AssertionError(
                    "Automated tests must not reach a real proxy without TEST_ALLOW_REAL_PROXY=true"
                )
            return await original_start(*args, **kwargs)

        monkeypatch.setattr(login_qrcode, "_start_qrcode_login_session_with_profile_once", guarded_proxy_start)

    return {
        "blocked": blocked,
        "required_flags": required_flags,
        "policy": _account_identity_tripwire_policy,
    }


@pytest.fixture
def sample_xhs_comment():
    """Sample Xiaohongshu comment data for testing"""
    return {
        "comment_id": "comment_123",
        "create_time": 1700000000,
        "ip_location": "Beijing",
        "note_id": "test_note_123",
        "content": "This is a test comment",
        "user_id": "user_456",
        "nickname": "Comment User",
        "avatar": "https://example.com/avatar2.jpg",
        "sub_comment_count": 5,
        "pictures": "",
        "parent_comment_id": 0,
        "like_count": 15
    }


@pytest.fixture
def sample_xhs_creator():
    """Sample Xiaohongshu creator data for testing"""
    return {
        "user_id": "creator_123",
        "nickname": "Creator Name",
        "gender": "Female",
        "avatar": "https://example.com/creator_avatar.jpg",
        "desc": "This is the creator bio",
        "ip_location": "Guangzhou",
        "follows": 500,
        "fans": 10000,
        "interaction": 50000,
        "tag_list": '{"profession": "Designer", "interest": "Photography"}'
    }
