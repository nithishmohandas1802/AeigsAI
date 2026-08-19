from fastapi import HTTPException


class ErrorCode:
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    FORBIDDEN = "FORBIDDEN"
    UNAUTHORIZED = "UNAUTHORIZED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    HTTP_ERROR = "HTTP_ERROR"


class AegisAIException(Exception):
    """Base exception for application-level errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class UserAlreadyExistsError(AegisAIException):
    """Raised when a username or email already exists."""

    def __init__(
        self,
        message: str = "Username or email already exists",
    ):
        super().__init__(
            message=message,
            code=ErrorCode.USER_ALREADY_EXISTS,
            status_code=409,
        )


class UserNotFoundError(AegisAIException):
    """Raised when a requested user does not exist."""

    def __init__(
        self,
        message: str = "User not found",
    ):
        super().__init__(
            message=message,
            code=ErrorCode.USER_NOT_FOUND,
            status_code=404,
        )


class ForbiddenError(AegisAIException):
    """Raised when a user is not allowed to perform an operation."""

    def __init__(
        self,
        message: str = "You are not allowed to perform this action",
    ):
        super().__init__(
            message=message,
            code=ErrorCode.FORBIDDEN,
            status_code=403,
        )


def create_http_exception(
    status_code: int,
    message: str,
    code: str,
):
    return HTTPException(
        status_code=status_code,
        detail=message,
        headers={
            "X-AegisAI-Error-Code": code,
        },
    )
