from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.category import CreateCategory, CategoryUpdate
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

    async def update_category(
        self,
        db: AsyncSession,
        category_id: int,
        category: CategoryUpdate,
        current_user: User,
    ) -> CategoryDTO:
        """Обновляет категорию по id и возвращает ее"""

        category_exists = await category_crud.get_category_by_id(db, category_id)

        if not category_exists:
            raise CategoryNotFoundException("Категория не найдена") from None

        if category_exists.user_id != current_user.id:
            raise CategoryPermissionException(
                "У пользователя нет прав доступа на эту категорию"
            ) from None

        updated_category: CategoryDTO = await category_crud.update_category(
            db, category_id, category
        )

        return updated_category

    async def delete_category(
        self, db: AsyncSession, category_id: int, current_user: User
    ) -> None:
        """Удаляет категорию и ничего не возвращает"""
        category = await category_crud.get_category_by_id(db, category_id)
        if not category:
            raise CategoryNotFoundException("Категория не найдена")

        if category.user_id != current_user.id:
            raise CategoryPermissionException("Категория не принадлежит пользователю")

        await category_crud.delete_category(db, category_id)
