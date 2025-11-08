from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.category import CreateCategory
from app.schemas.dataclasses.category import CategoryDTO
from app.service.category import crud as category_crud
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryPermissionException,
)


class CategoryService:
    """Сервис категорий: создание, изменение, удаление"""

    async def create_category(
        self, db: AsyncSession, category: CreateCategory, current_user: User
    ) -> CategoryDTO:
        """Создание категории"""
        new_category: CategoryDTO = await category_crud.create_category(
            db, category, current_user.id
        )
        return new_category

    async def get_categories(
        self, db: AsyncSession, current_user: User, skip: int, limit: int
    ) -> List[CategoryDTO]:
        """Получение категорий пользователя"""
        categories: List[CategoryDTO] = await category_crud.get_categories(
            db, current_user.id, skip, limit
        )
        return categories

    async def get_category(
        self, db: AsyncSession, category_id: int, current_user: User
    ) -> CategoryDTO:
        """Получение категории пользователя по id"""

        category: CategoryDTO = await category_crud.get_category_by_id(db, category_id)

        if not category:
            raise CategoryNotFoundException("Категория не найдена")

        if category.id != current_user.id:
            raise CategoryPermissionException("Категория не принадлежит пользователю")

        return category
