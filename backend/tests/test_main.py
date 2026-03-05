"""Tests for app entry point — root endpoint and lifespan."""

from unittest.mock import AsyncMock, patch

import pytest


class TestRootEndpoint:
    @pytest.mark.anyio
    async def test_returns_status(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "MontGoWork API"
        assert body["status"] == "running"


class TestLifespan:
    @pytest.mark.anyio
    async def test_startup_and_shutdown(self):
        from app.main import lifespan, app

        mock_engine = AsyncMock()
        with patch("app.main.get_engine", return_value=mock_engine) as mock_ge, \
             patch("app.main.init_db", new_callable=AsyncMock) as mock_init:
            async with lifespan(app):
                mock_ge.assert_called_once()
                mock_init.assert_awaited_once_with(mock_engine)
