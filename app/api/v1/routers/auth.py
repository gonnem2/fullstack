from typing import Annotated
from fastapi import APIRouter, Depends, Body, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.token import TokenOut
from app.schemas.user import UserCreate, UserOut
from app.service.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post(
    "/register",
    summary="Register a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
)
async def register_user(
    user: Annotated[UserCreate, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Регистрация нового пользователя."""
    new_user = await auth_service.create_user(db, user)
    return new_user


@router.post(
    "/token",
    summary="Login and get JWT tokens",
    response_model=TokenOut,
)
async def login_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Авторизация пользователя."""
    access_token, refresh_token = await auth_service.get_tokens(db, user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post(
    "/refresh",
    summary="Refresh access token",
    response_model=TokenOut,
)
async def refresh_token(
    refresh_token: Annotated[str, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Обновить access токен по refresh токену."""
    access_token, refresh_token = await auth_service.refresh_token(db, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
