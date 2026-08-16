from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import user
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service
from app.security.jwt import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(
        db,
        login_data,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(
    {
        "sub": str(user.id),
        "email": user.email,
    }
)

    return {
    "access_token": access_token,
    "token_type": "bearer",
}