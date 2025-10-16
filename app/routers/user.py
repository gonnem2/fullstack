from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user profile",
    response_model=UserOut,
)
async def get_current_user_profile():
    """Получить профиль текущего пользователя."""
    return {"username": "demo_user"}
