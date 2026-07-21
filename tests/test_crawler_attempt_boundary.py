from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
from types import SimpleNamespace

import httpx
import pytest

from tools.platform_request_environment import (
    PlatformRequestBinding,
    build_platform_request_binding,
)


def _binding() -> PlatformRequestBinding:
    from tests.test_platform_request_environment import _plan

    now = datetime.now(timezone.utc)
    return build_platform_request_binding(
        _plan(),
        run_id=12904,
        identity_revision="identity-revision-fixed",
        cookie_material_revision="cookie-revision-fixed",
        proxy_revision="proxy-revision-fixed",
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=15)).isoformat(),
    )


def test_cr129_packet_d_only_transient_network_is_retryable() -> None:
    from tools.crawler_attempt import (
        CRAWLER_FAILURE_CATEGORIES,
        is_retryable_crawler_category,
    )

    expected = {
        "login_required",
        "second_verification",
        "captcha_or_human_verification",
        "rate_limited",
        "proxy_or_ip_blocked",
        "signature_mismatch",
        "cookie_invalid",
        "browser_environment_mismatch",
        "account_identity_mismatch",
        "transient_network",
        "platform_protocol_changed",
        "timeout",
        "cancelled",
        "process_crashed",
    }
    assert CRAWLER_FAILURE_CATEGORIES == expected
    assert is_retryable_crawler_category("transient_network") is True
    assert all(
        not is_retryable_crawler_category(category)
        for category in expected - {"transient_network"}
    )


def test_cr129_packet_d_exception_classification_is_typed_and_secret_free() -> None:
    from tools.crawler_attempt import classify_crawler_exception

    request = httpx.Request("GET", "https://platform.invalid/items")
    cases = [
        (httpx.ConnectError("synthetic-token-value", request=request), "transient_network"),
        (httpx.ReadTimeout("synthetic timeout detail", request=request), "timeout"),
        (RuntimeError("second verification required"), "second_verification"),
        (RuntimeError("captcha required"), "captcha_or_human_verification"),
        (RuntimeError("rate limit exceeded"), "rate_limited"),
        (RuntimeError("signature mismatch"), "signature_mismatch"),
        (RuntimeError("cookie invalid"), "cookie_invalid"),
        (RuntimeError("unexpected response schema"), "platform_protocol_changed"),
        (RuntimeError("synthetic-token-value"), "process_crashed"),
    ]

    for error, expected in cases:
        classified = classify_crawler_exception(error)
        assert classified.category == expected
        assert "synthetic-token-value" not in classified.reason_code


def test_cr129_packet_d_terminal_result_round_trip_is_bound_and_redacted(tmp_path) -> None:
    from tools.crawler_attempt import (
        build_crawler_attempt_result,
        read_crawler_attempt_result,
        write_crawler_attempt_result,
    )

    binding = _binding()
    started_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    result = build_crawler_attempt_result(
        binding,
        status="failed",
        category="signature_mismatch",
        reason_code="douyin_signature_mismatch",
        retry_ordinal=2,
    )
    destination = tmp_path / "attempt-result.json"
    write_crawler_attempt_result(destination, result)

    restored = read_crawler_attempt_result(
        destination,
        expected_binding=binding,
        expected_retry_ordinal=2,
        child_started_at=started_at,
    )
    payload = destination.read_text(encoding="utf-8")

    assert restored == result
    assert restored.retryable is False
    for forbidden in (
        "sessionid=raw-cookie-value",
        "raw-token-value",
        "http://user:proxy-password@proxy.invalid:8080",
        r"c:\profiles\account-8972",
        "synthetic-secret-value",
    ):
        assert forbidden not in payload.lower()


def test_cr129_packet_d_terminal_result_rejects_stale_or_cross_attempt(tmp_path) -> None:
    from tools.crawler_attempt import (
        CrawlerAttemptResultError,
        build_crawler_attempt_result,
        read_crawler_attempt_result,
        write_crawler_attempt_result,
    )

    binding = _binding()
    stale = build_crawler_attempt_result(
        binding,
        status="failed",
        category="transient_network",
        reason_code="httpx_transport_error",
        retry_ordinal=1,
        recorded_at=(datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
    )
    destination = tmp_path / "stale-result.json"
    write_crawler_attempt_result(destination, stale)

    with pytest.raises(CrawlerAttemptResultError, match="stale"):
        read_crawler_attempt_result(
            destination,
            expected_binding=binding,
            expected_retry_ordinal=1,
            child_started_at=datetime.now(timezone.utc),
        )

    current = build_crawler_attempt_result(
        binding,
        status="failed",
        category="transient_network",
        reason_code="httpx_transport_error",
        retry_ordinal=1,
    )
    write_crawler_attempt_result(destination, current)
    other_attempt = replace(binding, attempt_id="attempt-other")
    with pytest.raises(CrawlerAttemptResultError, match="binding"):
        read_crawler_attempt_result(
            destination,
            expected_binding=other_attempt,
            expected_retry_ordinal=1,
            child_started_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )


@pytest.mark.parametrize(
    "category",
    [
        "login_required",
        "second_verification",
        "captcha_or_human_verification",
        "rate_limited",
        "proxy_or_ip_blocked",
        "signature_mismatch",
        "cookie_invalid",
        "browser_environment_mismatch",
        "account_identity_mismatch",
        "platform_protocol_changed",
        "timeout",
        "cancelled",
        "process_crashed",
    ],
)
def test_cr129_packet_d_terminal_categories_do_not_enter_retry(category) -> None:
    from tools.crawler_attempt import CrawlerAttemptFailure

    failure = CrawlerAttemptFailure(category, f"{category}_synthetic")
    assert failure.retryable is False


def test_cr129_packet_d_retry_failure_is_explicit() -> None:
    from tools.crawler_attempt import CrawlerAttemptFailure

    failure = CrawlerAttemptFailure(
        "transient_network",
        "httpx_transport_error",
    )
    assert failure.retryable is True
    assert "transient_network" in str(failure)


def test_cr129_packet_d_current_terminal_writer_consumes_safe_handles(
    tmp_path,
    monkeypatch,
) -> None:
    from tools.crawler_attempt import (
        CRAWLER_ATTEMPT_RESULT_ENV_NAME,
        CRAWLER_RETRY_ORDINAL_ENV_NAME,
        read_crawler_attempt_result,
        record_current_crawler_attempt_result,
    )
    from tools.platform_request_environment import (
        REQUEST_BINDING_ENV_NAME,
        platform_request_binding_to_json,
        reset_platform_request_environment_cache_for_tests,
    )

    binding = _binding()
    destination = tmp_path / "current-result.json"
    started_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    reset_platform_request_environment_cache_for_tests()
    monkeypatch.setenv(REQUEST_BINDING_ENV_NAME, platform_request_binding_to_json(binding))
    monkeypatch.setenv(CRAWLER_ATTEMPT_RESULT_ENV_NAME, str(destination))
    monkeypatch.setenv(CRAWLER_RETRY_ORDINAL_ENV_NAME, "3")

    result = record_current_crawler_attempt_result(
        status="success",
        reason_code="crawler_completed",
    )
    restored = read_crawler_attempt_result(
        destination,
        expected_binding=binding,
        expected_retry_ordinal=3,
        child_started_at=started_at,
    )

    assert result == restored
    assert CRAWLER_ATTEMPT_RESULT_ENV_NAME not in os.environ
    assert CRAWLER_RETRY_ORDINAL_ENV_NAME not in os.environ
    assert REQUEST_BINDING_ENV_NAME not in os.environ
    reset_platform_request_environment_cache_for_tests()


def test_cr129_packet_d_runner_rejects_missing_or_conflicting_terminal_result(
    tmp_path,
) -> None:
    from api.monitoring import runner
    from tools.crawler_attempt import (
        CrawlerAttemptFailure,
        build_crawler_attempt_result,
        write_crawler_attempt_result,
    )

    binding = _binding()
    started_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    destination = tmp_path / "attempt-result.json"
    with pytest.raises(CrawlerAttemptFailure) as missing:
        runner._load_managed_child_attempt_result(
            destination,
            binding,
            retry_ordinal=1,
            child_started_at=started_at,
            returncode=1,
        )
    assert missing.value.category == "process_crashed"

    success = build_crawler_attempt_result(
        binding,
        status="success",
        reason_code="crawler_completed",
        retry_ordinal=1,
    )
    write_crawler_attempt_result(destination, success)
    with pytest.raises(CrawlerAttemptFailure) as conflict:
        runner._load_managed_child_attempt_result(
            destination,
            binding,
            retry_ordinal=1,
            child_started_at=started_at,
            returncode=43,
        )
    assert conflict.value.category == "process_crashed"
    assert not destination.exists()


def test_cr129_packet_d_plan_handle_is_single_use(tmp_path, monkeypatch) -> None:
    from tests.test_platform_request_environment import _plan
    from tools.browser_environment import (
        PLAN_ENV_NAME,
        PLAN_PATH_ENV_NAME,
        BrowserEnvironmentError,
        browser_environment_plan_to_json,
        plan_from_environment,
        reset_browser_environment_cache_for_tests,
        write_browser_environment_plan_handle,
    )

    plan = _plan()
    destination = tmp_path / "browser-plan.json"
    write_browser_environment_plan_handle(destination, plan)
    reset_browser_environment_cache_for_tests()
    monkeypatch.setenv(PLAN_PATH_ENV_NAME, str(destination))

    assert plan_from_environment(required=True) == plan
    assert not destination.exists()
    assert PLAN_PATH_ENV_NAME not in os.environ

    write_browser_environment_plan_handle(destination, plan)
    reset_browser_environment_cache_for_tests()
    monkeypatch.setenv(PLAN_PATH_ENV_NAME, str(destination))
    monkeypatch.setenv(PLAN_ENV_NAME, browser_environment_plan_to_json(plan))
    with pytest.raises(BrowserEnvironmentError, match="plan_authority"):
        plan_from_environment(required=True)
    reset_browser_environment_cache_for_tests()


def test_cr129_packet_d_managed_main_writes_bound_failure_terminal(
    tmp_path,
    monkeypatch,
) -> None:
    import main as crawler_main
    from tools.crawler_attempt import (
        CRAWLER_ATTEMPT_FAILURE_EXIT_CODE,
        CRAWLER_ATTEMPT_RESULT_ENV_NAME,
        CRAWLER_RETRY_ORDINAL_ENV_NAME,
        CrawlerAttemptFailure,
        read_crawler_attempt_result,
    )
    from tools.platform_request_environment import (
        REQUEST_BINDING_ENV_NAME,
        platform_request_binding_to_json,
        reset_platform_request_environment_cache_for_tests,
    )

    binding = _binding()
    destination = tmp_path / "main-attempt-result.json"
    started_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    class FailingCrawler:
        async def start(self):
            raise CrawlerAttemptFailure(
                "second_verification",
                "douyin_second_verification",
            )

    async def fake_parse_cmd():
        return SimpleNamespace(init_db=None)

    reset_platform_request_environment_cache_for_tests()
    monkeypatch.setenv(REQUEST_BINDING_ENV_NAME, platform_request_binding_to_json(binding))
    monkeypatch.setenv(CRAWLER_ATTEMPT_RESULT_ENV_NAME, str(destination))
    monkeypatch.setenv(CRAWLER_RETRY_ORDINAL_ENV_NAME, "1")
    monkeypatch.setattr(crawler_main.cmd_arg, "parse_cmd", fake_parse_cmd)
    monkeypatch.setattr(
        crawler_main.CrawlerFactory,
        "create_crawler",
        lambda platform: FailingCrawler(),
    )

    with pytest.raises(SystemExit) as exc_info:
        asyncio.run(crawler_main.main())

    restored = read_crawler_attempt_result(
        destination,
        expected_binding=binding,
        expected_retry_ordinal=1,
        child_started_at=started_at,
    )
    assert exc_info.value.code == CRAWLER_ATTEMPT_FAILURE_EXIT_CODE
    assert restored.status == "failed"
    assert restored.category == "second_verification"
    assert restored.reason_code == "douyin_second_verification"
    crawler_main.crawler = None
    reset_platform_request_environment_cache_for_tests()
