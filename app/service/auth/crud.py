from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encode_password
from app.db import User
from app.schemas.dataclasses.user import UserDTO
from app.schemas.user import UserCreate


async def get_user_by_email_or_username(
    db: AsyncSession, email: str, username: str
) -> User:
    """Возвращает пользователя по его email или username"""

    stmt = select(User).where(or_(User.email == email, User.username == username))
    result = await db.scalars(stmt)
    return result.first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Создание нового пользователя"""

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=encode_password(user.password),
        day_expense_limit=user.day_expense_limit,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user


async def get_user_by_username(db: AsyncSession, username: str):
    """Возвращает пользователя по username"""

    stmt = select(User).where(User.username == username)
    result = await db.scalars(stmt)
    return result.first()


async def get_user_by_id(u_id: int, db: AsyncSession) -> User:
    """Возвращает пользователя по id из БД"""

    stmt = select(User).where(User.id == u_id)
    result = await db.scalars(stmt)
    return result.first()
