from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPatch
from sqlalchemy.exc import IntegrityError
from app.exceptions import UserAlreadyExistsError
from app.security.password import hash_password


def create_user(db: Session, user_data: UserCreate) -> User:
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError(
            "Username or email already exists"
        )

    return new_user

def get_users(db: Session) -> list[User]:
    return db.query(User).all()

def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate,
) -> User | None:
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if existing_user is None:
        return None

    existing_user.username = user_data.username
    existing_user.email = user_data.email

    db.commit()
    db.refresh(existing_user)

    return existing_user

def delete_user(
    db: Session,
    user_id: int,
) -> bool:
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if existing_user is None:
        return False

    db.delete(existing_user)
    db.commit()

    return True

def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

def patch_user(
    db: Session,
    user_id: int,
    user_data: UserPatch,
) -> User | None:
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if existing_user is None:
        return None

    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_user, field, value)

    db.commit()
    db.refresh(existing_user)

    return existing_user