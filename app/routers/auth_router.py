from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token
)

from app.services.user_service import UserService
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# Register
# =========================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    try:

        user = UserService.register(
            db=db,
            user_data=user_data
        )

        return user

    except ValueError as e:

        raise   HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================
# Login - OAuth2
# =========================

@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user_data = UserLogin(
        email=form_data.username,
        password=form_data.password
    )

    try:

        return AuthService.login(
            db=db,
            user_data=user_data
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

