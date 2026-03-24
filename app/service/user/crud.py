from typing import List

from sqlalchemy import update, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encode_password
from app.core.settings import settings
from app.db import User
from app.db.models.user import UserRoles
from app.schemas.dataclasses.user import UserDTO


async def change_expense_limit(
    db: AsyncSession, user: User, new_limit: float
) -> UserDTO:
    """Обновляет user в БД, меняя его лимит трат"""

    stmt = (
        update(User)
        .where(User.id == user.id)
        .values(day_expense_limit=new_limit)
        .returning(
            User.id,
            User.username,
            User.email,
            User.hashed_password,
            User.day_expense_limit,
        )
    )
    res = await db.execute(stmt)
    row = res.first()
    return UserDTO(
        id=row.id,
        username=row.username,
        day_expense_limit=row.day_expense_limit,
        email=row.email,
        role=row.role,
        hashed_password=row.hashed_password,
    )


async def create_admin_user(session: AsyncSession):

    exists = await session.get(User, 0)
    if exists:
        return

    stmt = insert(User).values(
        id=0,
        username=settings.admin_username,
        email="example@example.com",
        hashed_password=encode_password(settings.admin_password),
        role=UserRoles.ADMIN.name,
    )
    await session.execute(stmt)


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserDTO:
    """Получаем пользователя по id"""

    stmt = select(User).where(User.id == user_id)
    res = await session.scalars(stmt)
    row = res.one_or_none()

    if not row:
        return None
    return UserDTO(
        id=row.id,
        username=row.username,
        day_expense_limit=row.day_expense_limit,
        email=row.email,
        hashed_password=row.hashed_password,
        role=row.role,
    )


async def change_user_role(
    session: AsyncSession, user_id: int, new_user_role: UserRoles
):
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(role=new_user_role.name)
        .returning(User)
    )
    result = await session.execute(stmt)
    row = result.scalar()
    if not row:
        return None

    return UserDTO(
        id=row.id,
        username=row.username,
        day_expense_limit=row.day_expense_limit,
        email=row.email,
        hashed_password=row.hashed_password,
        role=row.role,
    )


async def get_all_users(session: AsyncSession, skip: int, limit: int) -> List[UserDTO]:
    """Возвращает всех пользователей"""
    stmt = select(User).offset(skip).limit(limit)
    res = await session.scalars(stmt)
    users = list()

    for row in res:
        users.append(
            UserDTO(
                id=row.id,
                username=row.username,
                day_expense_limit=row.day_expense_limit,
                email=row.email,
                hashed_password=row.hashed_password,
                role=row.role,
            )
        )

    return users
