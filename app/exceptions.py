class AegisAIException(Exception):
    """Base exception for application-level errors."""

    def __init__(
        self,
        message: str,
        code: str,
    ):
        self.message = message
        self.code = code
        super().__init__(message)


class UserAlreadyExistsError(AegisAIException):
    """Raised when a username or email already exists."""

    def __init__(self, message: str = "Username or email already exists"):
        super().__init__(
            message=message,
            code="USER_ALREADY_EXISTS",
        )
