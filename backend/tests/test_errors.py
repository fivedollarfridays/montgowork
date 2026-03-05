"""Tests for custom exception classes."""

from app.core.errors import (
    AppError,
    AuthenticationError,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
)


class TestAppError:
    def test_defaults(self):
        err = AppError()
        assert err.message == "An error occurred"
        assert err.error_code == "APP_ERROR"
        assert err.status_code == 500

    def test_custom_values(self):
        err = AppError("custom msg", "CUSTOM_CODE", 418)
        assert err.message == "custom msg"
        assert err.error_code == "CUSTOM_CODE"
        assert err.status_code == 418

    def test_str(self):
        err = AppError("boom", "BANG")
        assert str(err) == "[BANG] boom"

    def test_is_exception(self):
        err = AppError()
        assert isinstance(err, Exception)


class TestValidationError:
    def test_defaults(self):
        err = ValidationError()
        assert err.status_code == 400
        assert err.error_code == "VALIDATION_ERROR"
        assert err.message == "Validation failed"

    def test_custom_message(self):
        err = ValidationError("bad input")
        assert err.message == "bad input"
        assert err.status_code == 400


class TestNotFoundError:
    def test_defaults(self):
        err = NotFoundError()
        assert err.status_code == 404
        assert err.error_code == "NOT_FOUND"

    def test_custom_message(self):
        err = NotFoundError("user 42 missing")
        assert err.message == "user 42 missing"


class TestAuthenticationError:
    def test_defaults(self):
        err = AuthenticationError()
        assert err.status_code == 401
        assert err.error_code == "AUTHENTICATION_ERROR"


class TestExternalServiceError:
    def test_defaults(self):
        err = ExternalServiceError()
        assert err.status_code == 502
        assert err.error_code == "EXTERNAL_SERVICE_ERROR"
