from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Expense
from app.schemas.expense import ExpenseCreate
from app.service.category.crud import get_category_by_id
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryTypeException,
)
from app.service.expense import crud as expense_crud


class ExpenseService:
    """Сервис трат: создание, удаление, изменение, получение"""

    async def create_expense(
        self,
        db: AsyncSession,
        spending: ExpenseCreate,
        user_id: int,
    ) -> Expense:
        """Создание траты в БД"""

        category_exists = await get_category_by_id(db, spending.category_id)

        if not category_exists:
            raise CategoryNotFoundException("Категория не найдена")

        if not category_exists.is_expense:
            raise CategoryTypeException("Тип категории не трата")

        new_expense = await expense_crud.create_expense(db, spending, user_id)
        return new_expense

    async def get_expenses(self, db: AsyncSession, user_id: int, skip: int, limit: int):
        """Возвращает все траты юзера с пагинацией"""

        expenses = await expense_crud.get_user_expenses(db, user_id, skip, limit)
        return expenses
