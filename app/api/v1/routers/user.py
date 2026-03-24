import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.db.database import get_db
from app.schemas.user import UserOut, NewUserRole
from app.service.auth.dependencies import get_current_user, get_admin_user, get_user
from app.service.user.service import UserService

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

    user_out = UserOut(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        day_expense_limit=current_user.day_expense_limit,
        role=current_user.role,
    )
    return user_out


@router.patch(
    "/change_limit", response_model=UserOut, summary="Изменяет лимит трат пользователя"
)
async def change_limit(
    session: Annotated[AsyncSession, Depends(get_db)],
    new_limit: float,
    current_user: Annotated[User, Depends(get_user)],
):
    user_service = UserService(session=session)

    changed_user = await user_service.change_user_expense_limit(current_user, new_limit)
    return changed_user


@router.patch(
    "/admin/{user_id}",
    summary="Изменяет роль пользователя на переданную",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_user(
    current_admin: Annotated[User, Depends(get_admin_user)],
    user_id: int,
    new_user_role: NewUserRole,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user_service = UserService(session=session)

    await user_service.change_user_role(user_id, new_user_role.user_role)


@router.get(
    "/admin/all",
    status_code=status.HTTP_200_OK,
    summary="Возвращает всех пользователей",
    response_model=List[UserOut],
)
async def get_all_users(
    admin_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    user_service = UserService(session=session)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users
