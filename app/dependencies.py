from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.exceptions import ErrorCode, create_http_exception
from app.models.user import User
from app.security.jwt import decode_access_token


security = HTTPBearer(
    auto_error=False,
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:

    if credentials is None:
        raise create_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Not authenticated",
            code=ErrorCode.UNAUTHORIZED,
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except Exception:
        raise create_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token",
            code=ErrorCode.UNAUTHORIZED,
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise create_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
            code=ErrorCode.UNAUTHORIZED,
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise create_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="User not found",
            code=ErrorCode.UNAUTHORIZED,
        )

    return user