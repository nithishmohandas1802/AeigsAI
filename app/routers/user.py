from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    new_user = User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("")
def get_users(
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    return users

@router.put("/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        return {"message": "User not found"}

    existing_user.username = user.username
    existing_user.email = user.email

    db.commit()
    db.refresh(existing_user)

    return existing_user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        return {"message": "User not found"}

    db.delete(existing_user)
    db.commit()

    return {"message": "User deleted successfully"}