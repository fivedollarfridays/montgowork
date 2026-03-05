"""Tests for credit proxy — error handling and success path."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

VALID_PAYLOAD = {
    "current_score": 580,
    "overall_utilization": 45.0,
    "account_summary": {"total_accounts": 5, "open_accounts": 3},
    "payment_history_pct": 85.0,
    "average_account_age_months": 24,
}


def _mock_httpx_client(mock_cls, *, side_effect=None, return_value=None):
    """Wire up a mock httpx.AsyncClient context manager."""
    instance = AsyncMock()
    if side_effect:
        instance.post.side_effect = side_effect
    else:
        instance.post.return_value = return_value
    instance.__aenter__ = AsyncMock(return_value=instance)
    instance.__aexit__ = AsyncMock(return_value=False)
    mock_cls.return_value = instance


class TestCreditProxyErrors:
    @pytest.mark.anyio
    async def test_connect_error_returns_503(self, client):
        """ConnectError should return 503."""
        with patch("app.routes.credit.httpx.AsyncClient") as mock_cls:
            _mock_httpx_client(mock_cls, side_effect=httpx.ConnectError("refused"))
            resp = await client.post("/api/credit/assess", json=VALID_PAYLOAD)
            assert resp.status_code == 503
            assert "unavailable" in resp.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_timeout_returns_504(self, client):
        """TimeoutException should return 504."""
        with patch("app.routes.credit.httpx.AsyncClient") as mock_cls:
            _mock_httpx_client(mock_cls, side_effect=httpx.TimeoutException("timed out"))
            resp = await client.post("/api/credit/assess", json=VALID_PAYLOAD)
            assert resp.status_code == 504
            assert "timed out" in resp.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_non_json_error_response(self, client):
        """Non-JSON error body should not cause 500."""
        mock_resp = AsyncMock()
        mock_resp.status_code = 502
        mock_resp.json.side_effect = Exception("not JSON")
        mock_resp.text = "<html>Bad Gateway</html>"

        with patch("app.routes.credit.httpx.AsyncClient") as mock_cls:
            _mock_httpx_client(mock_cls, return_value=mock_resp)
            resp = await client.post("/api/credit/assess", json=VALID_PAYLOAD)
            assert resp.status_code == 502

    @pytest.mark.anyio
    async def test_other_network_error_returns_502(self, client):
        """Other httpx errors (ReadError, etc.) should return 502."""
        with patch("app.routes.credit.httpx.AsyncClient") as mock_cls:
            _mock_httpx_client(mock_cls, side_effect=httpx.ReadError("connection reset"))
            resp = await client.post("/api/credit/assess", json=VALID_PAYLOAD)
            assert resp.status_code == 502
            assert "network error" in resp.json()["detail"].lower()


class TestCreditProxySuccess:
    @pytest.mark.anyio
    async def test_success_returns_api_response(self, client):
        """200 from credit API should pass through the response body."""
        credit_response = {
            "barrier_severity": "medium",
            "barrier_details": [{"type": "utilization", "severity": "medium"}],
            "readiness": {"score": 45, "fico_score": 580, "score_band": "poor"},
            "thresholds": [{"threshold_name": "fair", "threshold_score": 650}],
            "dispute_pathway": {"steps": [], "total_estimated_days": 90},
            "eligibility": [{"product_name": "auto loan", "status": "not_eligible"}],
            "disclaimer": "This is not financial advice.",
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = credit_response

        with patch("app.routes.credit.httpx.AsyncClient") as mock_cls:
            _mock_httpx_client(mock_cls, return_value=mock_resp)
            resp = await client.post("/api/credit/assess", json=VALID_PAYLOAD)
            assert resp.status_code == 200
            assert resp.json() == credit_response
