from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.db import User
from app.schemas.user import UserOut
from app.service.auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user profile",
    response_model=UserOut,
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получить профиль текущего пользователя."""
    return current_user
