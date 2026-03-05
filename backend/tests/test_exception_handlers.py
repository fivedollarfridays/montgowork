"""Tests for FastAPI exception handlers."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import AppError, NotFoundError
from app.core.exception_handlers import (
    app_error_handler,
    generic_error_handler,
    register_exception_handlers,
)


def _mock_request(path: str = "/test") -> MagicMock:
    req = MagicMock()
    req.url.path = path
    return req


class TestAppErrorHandler:
    @pytest.mark.anyio
    async def test_returns_error_json(self):
        exc = NotFoundError("item missing")
        resp = await app_error_handler(_mock_request(), exc)
        assert resp.status_code == 404
        assert resp.body is not None

    @pytest.mark.anyio
    async def test_response_body_structure(self):
        exc = AppError("oops", "TEST_ERR", 422)
        resp = await app_error_handler(_mock_request("/api/foo"), exc)
        import json

        body = json.loads(resp.body)
        assert body["error"]["code"] == "TEST_ERR"
        assert body["error"]["message"] == "oops"

    @pytest.mark.anyio
    async def test_logs_warning(self):
        exc = AppError("test")
        with patch("app.core.exception_handlers.logger") as mock_log:
            await app_error_handler(_mock_request(), exc)
            mock_log.warning.assert_called_once()


class TestGenericErrorHandler:
    @pytest.mark.anyio
    async def test_returns_500(self):
        resp = await generic_error_handler(_mock_request(), RuntimeError("boom"))
        assert resp.status_code == 500

    @pytest.mark.anyio
    async def test_response_body_is_generic(self):
        import json

        resp = await generic_error_handler(_mock_request(), ValueError("secret"))
        body = json.loads(resp.body)
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert "secret" not in body["error"]["message"]

    @pytest.mark.anyio
    async def test_logs_exception(self):
        with patch("app.core.exception_handlers.logger") as mock_log:
            await generic_error_handler(_mock_request(), RuntimeError("x"))
            mock_log.exception.assert_called_once()


class TestRegisterExceptionHandlers:
    def test_registers_both_handlers(self):
        mock_app = MagicMock()
        register_exception_handlers(mock_app)
        assert mock_app.add_exception_handler.call_count == 2
