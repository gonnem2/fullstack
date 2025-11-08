from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.db.database import get_db
from app.schemas.user import UserOut
from app.service.auth.dependencies import get_current_user
from app.service.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
user_service = UserService()


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


@router.patch(
    "/change_limit", response_model=UserOut, summary="Изменяет лимит трат пользователя"
)
async def change_limit(
    db: Annotated[AsyncSession, Depends(get_db)],
    new_limit: float,
    current_user: Annotated[User, Depends(get_current_user)],
):
    changed_user = await user_service.change_user_expense_limit(
        db, current_user, new_limit
    )
    return changed_user
