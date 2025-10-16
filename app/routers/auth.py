from typing import Annotated
from fastapi import APIRouter, Depends, Body, status

from app.schemas.token import TokenOut
from app.schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    summary="Register a new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: Annotated[UserCreate, Body(...)],
):
    """Регистрация нового пользователя."""
    return {"message": "User registered"}


@router.post(
    "/login",
    summary="Login and get JWT tokens",
    response_model=TokenOut,
)
async def login_user(
    user: Annotated[UserLogin, Body(...)],
):
    """Авторизация пользователя."""
    return {"access_token": "token", "refresh_token": "refresh"}


@router.post(
    "/refresh",
    summary="Refresh access token",
    response_model=TokenOut,
)
async def refresh_token(
    refresh_token: Annotated[str, Body(...)],
):
    """Обновить access токен по refresh токену."""
    return {"access_token": "new_token", "refresh_token": "new_refresh"}
