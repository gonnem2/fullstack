from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Category


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
    """Получение категории по id"""

    stmt = select(Category).where(Category.id == category_id)
    result = await db.scalars(stmt)
    return result.first()
