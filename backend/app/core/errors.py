"""Custom exception classes for standardized error handling."""


class AppError(Exception):
    """Base exception class for all application errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        error_code: str = "APP_ERROR",
        status_code: int = 500,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", error_code: str = "VALIDATION_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=400)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(message=message, error_code=error_code, status_code=404)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication failed", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=401)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service error", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(message=message, error_code=error_code, status_code=502)
