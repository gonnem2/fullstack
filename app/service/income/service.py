from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.dataclasses.income import IncomeDTO
from app.schemas.income import IncomeCreate
from app.service.category import crud as category_crud
from app.service.income import crud as income_crud
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryTypeException,
)


class IncomeService:
    """Сревис доходов: создание, удаление, изменение, ..."""

    async def create_income(
        self, db: AsyncSession, current_user: User, income: IncomeCreate
    ):
        """Создает новую трату в БД"""

        # проверка категории на наличие
        category_exists = await category_crud.get_category_by_id(db, income.category_id)
        if not category_exists:
            raise CategoryNotFoundException("Категория не найдена") from None

        if not category_exists.is_income:
            raise CategoryTypeException("Тип категории не трата!") from None

        new_income: IncomeDTO = await income_crud.create_category(
            db, current_user.id, income
        )
        return new_income
