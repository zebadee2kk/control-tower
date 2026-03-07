"""
Unit tests for src/integrations/cost_tracker.py

The cost tracker client must degrade gracefully when the service is absent.
All HTTP calls are mocked — no live network required.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.integrations.cost_tracker import CostTrackerClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def enabled_client() -> CostTrackerClient:
    """Client configured with a URL and token."""
    return CostTrackerClient(
        base_url="http://tracker.local:5000",
        token="test-token-abc",
        account_id="test-account",
    )


@pytest.fixture
def disabled_client() -> CostTrackerClient:
    """Client with no URL or token — disabled mode."""
    return CostTrackerClient(base_url="", token="")


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInit:
    def test_enabled_when_url_and_token_set(self, enabled_client: CostTrackerClient) -> None:
        assert enabled_client.enabled is True

    def test_disabled_when_url_missing(self) -> None:
        client = CostTrackerClient(base_url="", token="tok")
        assert client.enabled is False

    def test_disabled_when_token_missing(self) -> None:
        client = CostTrackerClient(base_url="http://example.com", token="")
        assert client.enabled is False

    def test_disabled_client_is_disabled(self, disabled_client: CostTrackerClient) -> None:
        assert disabled_client.enabled is False


# ---------------------------------------------------------------------------
# health_check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_returns_true_when_healthy(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "healthy"}
        mock_resp.raise_for_status.return_value = None

        with patch("src.integrations.cost_tracker.requests.get", return_value=mock_resp):
            result = enabled_client.health_check()
        assert result is True

    def test_returns_false_when_unhealthy_status(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "degraded"}
        mock_resp.raise_for_status.return_value = None

        with patch("src.integrations.cost_tracker.requests.get", return_value=mock_resp):
            result = enabled_client.health_check()
        assert result is False

    def test_returns_false_when_disabled(self, disabled_client: CostTrackerClient) -> None:
        result = disabled_client.health_check()
        assert result is False

    def test_returns_false_on_connection_error(self, enabled_client: CostTrackerClient) -> None:
        with patch(
            "src.integrations.cost_tracker.requests.get",
            side_effect=requests.exceptions.ConnectionError("refused"),
        ):
            result = enabled_client.health_check()
        assert result is False


# ---------------------------------------------------------------------------
# log_usage
# ---------------------------------------------------------------------------

class TestLogUsage:
    def test_returns_true_on_success(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None

        with patch("src.integrations.cost_tracker.requests.post", return_value=mock_resp):
            result = enabled_client.log_usage(
                provider="anthropic",
                model="claude-haiku-4-5-20251001",
                tokens=200,
                cost=0.00004,
            )
        assert result is True

    def test_payload_contains_required_fields(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None

        patch_path = "src.integrations.cost_tracker.requests.post"
        with patch(patch_path, return_value=mock_resp) as mock_post:
            enabled_client.log_usage(
                provider="ollama",
                model="qwen2.5-coder:1.5b",
                tokens=150,
                cost=0.0,
                context={"task": "classification", "issue_number": 7},
            )

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
        assert payload["provider"] == "ollama"
        assert payload["model"] == "qwen2.5-coder:1.5b"
        assert payload["tokens"] == 150
        assert payload["account_id"] == "test-account"
        assert "timestamp" in payload
        assert payload["context"]["issue_number"] == 7

    def test_returns_false_on_connection_error(self, enabled_client: CostTrackerClient) -> None:
        with patch(
            "src.integrations.cost_tracker.requests.post",
            side_effect=requests.exceptions.ConnectionError("service down"),
        ):
            result = enabled_client.log_usage("anthropic", "haiku", 100, 0.00002)
        assert result is False

    def test_returns_false_on_timeout(self, enabled_client: CostTrackerClient) -> None:
        with patch(
            "src.integrations.cost_tracker.requests.post",
            side_effect=requests.exceptions.Timeout("timed out"),
        ):
            result = enabled_client.log_usage("anthropic", "haiku", 100, 0.00002)
        assert result is False

    def test_returns_false_on_http_error(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500)
        )
        with patch("src.integrations.cost_tracker.requests.post", return_value=mock_resp):
            result = enabled_client.log_usage("anthropic", "haiku", 100, 0.00002)
        assert result is False

    def test_disabled_client_returns_false_without_calling_api(
        self, disabled_client: CostTrackerClient
    ) -> None:
        with patch("src.integrations.cost_tracker.requests.post") as mock_post:
            result = disabled_client.log_usage("anthropic", "haiku", 100, 0.00002)
        assert result is False
        mock_post.assert_not_called()

    def test_cost_rounded_to_8dp(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None

        post_path = "src.integrations.cost_tracker.requests.post"
        with patch(post_path, return_value=mock_resp) as mock_post:
            enabled_client.log_usage("anthropic", "haiku", 1, 0.000000001234567)

        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
        assert len(str(payload["cost_usd"]).replace("0.", "").lstrip("0")) <= 8


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------

class TestSummaries:
    def test_get_daily_summary_calls_api(self, enabled_client: CostTrackerClient) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"total_cost": 0.12, "requests": 45}
        mock_resp.raise_for_status.return_value = None

        with patch("src.integrations.cost_tracker.requests.get", return_value=mock_resp):
            result = enabled_client.get_daily_summary("2026-03-07")

        assert result is not None
        assert result["total_cost"] == 0.12

    def test_get_daily_summary_returns_none_on_error(  # noqa: E501
        self, enabled_client: CostTrackerClient
    ) -> None:
        with patch(
            "src.integrations.cost_tracker.requests.get",
            side_effect=requests.exceptions.ConnectionError("offline"),
        ):
            result = enabled_client.get_daily_summary()
        assert result is None

    def test_get_monthly_summary_returns_none_when_disabled(
        self, disabled_client: CostTrackerClient
    ) -> None:
        result = disabled_client.get_monthly_summary()
        assert result is None

    def test_get_monthly_summary_defaults_to_current_month(
        self, enabled_client: CostTrackerClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"month": "2026-03", "total_cost": 1.50}
        mock_resp.raise_for_status.return_value = None

        get_path = "src.integrations.cost_tracker.requests.get"
        with patch(get_path, return_value=mock_resp) as mock_get:
            enabled_client.get_monthly_summary()

        params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
        assert "month" in params
