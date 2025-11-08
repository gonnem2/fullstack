from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
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
        hashed_password=row.hashed_password,
    )
