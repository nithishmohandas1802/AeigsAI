from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate,UserPatch, UserResponse
from app.services.user_service import (
    create_user as create_user_service,
    get_users as get_users_service,
    get_user_by_id as get_user_by_id_service,
    patch_user as patch_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user_service(db, user)

@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_users_service(db)
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id_service(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this user",
        )

    updated_user = update_user_service(
        db,
        user_id,
        user,
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return updated_user

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def patch_user(
    user_id: int,
    user: UserPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this user",
        )

    updated_user = patch_user_service(
        db,
        user_id,
        user,
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return updated_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_user_service(db, user_id)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this user",
        )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return None