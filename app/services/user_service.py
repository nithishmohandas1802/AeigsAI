from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPatch
from sqlalchemy.exc import IntegrityError
from app.exceptions import UserAlreadyExistsError
from app.security.password import hash_password
from app.cache.cache_service import (
    delete_cache,
    get_cache,
    set_cache,
)

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

def get_users(
    db: Session,
    page: int,
    page_size: int,
    username: str | None = None,
    email: str | None = None,
) -> tuple[list[User], int]:
    query = db.query(User)

    if username is not None:
        query = query.filter(User.username == username)

    if email is not None:
        query = query.filter(User.email == email)

    total = query.count()

    offset = (page - 1) * page_size

    users = (
        query
        .order_by(User.id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return users, total

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

    try:
        db.commit()
        db.refresh(existing_user)

    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError(
            "Username or email already exists"
        )
    delete_cache(f"aegisai:user:{user_id}")

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

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise

    delete_cache(f"aegisai:user:{user_id}")

    return True

def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    cache_key = f"aegisai:user:{user_id}"

    cached_user = get_cache(cache_key)

    if cached_user is not None:
        return cached_user

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

    set_cache(
        cache_key,
        user_data,
        ttl=60,
    )

    return user

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

    try:
        db.commit()
        db.refresh(existing_user)

    except IntegrityError:
        db.rollback()
        raise UserAlreadyExistsError(
            "Username or email already exists"
        )
    delete_cache(f"aegisai:user:{user_id}")

    return existing_user
