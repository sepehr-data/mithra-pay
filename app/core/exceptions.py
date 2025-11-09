# app/core/exceptions.py


class AppError(Exception):
    """
    Base application error for MithraPay backend.
    """
    status_code = 400
    error_code = "app_error"

    def __init__(self, message: str, status_code: int | None = None, error_code: str | None = None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.message = message

    def to_dict(self):
        return {
            "error": self.error_code,
            "message": self.message,
        }


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "unauthorized"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"
