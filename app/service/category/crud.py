from typing import List

from sqlalchemy import select, insert
from sqlalchemy.engine import row
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Category
from app.schemas.category import CreateCategory
from app.schemas.dataclasses.category import CategoryDTO


async def get_category_by_id(db: AsyncSession, category_id: int) -> CategoryDTO | None:
    """Получение категории по id"""

    stmt = select(Category).where(Category.id == category_id)
    result = await db.scalars(stmt)
    row: Category = result.first()
    if not row:
        return None

    return CategoryDTO(
        id=row.id,
        title=row.title,
        user_id=row.user_id,
        type_of_category=row.type_of_category,
    )


async def create_category(
    db: AsyncSession,
    category: CreateCategory,
    user_id: int,
) -> CategoryDTO | None:
    """Добавление категории в БД"""

    stmt = (
        insert(Category)
        .values(**category.model_dump(), user_id=user_id)
        .returning(
            Category.id, Category.user_id, Category.title, Category.type_of_category
        )
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    return CategoryDTO(
        id=row.id,
        title=row.title,
        type_of_category=row.type_of_category,
        user_id=row.user_id,
    )


async def get_categories(
    db: AsyncSession, user_id: int, skip: int, limit: int
) -> List[CategoryDTO]:
    """Получение всех категорий пользователя"""
    stmt = select(Category).where(Category.user_id == user_id).offset(skip).limit(limit)
    result = await db.scalars(stmt)
    rows = result.all()

    return [
        CategoryDTO(
            id=category.id,
            title=category.title,
            user_id=category.user_id,
            type_of_category=category.type_of_category,
        )
        for category in rows
    ]
