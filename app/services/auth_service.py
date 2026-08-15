from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.security.password import verify_password

def authenticate_user(
    db: Session,
    login_data: LoginRequest,
) -> User | None:
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if user is None:
        return None

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        return None

    return user