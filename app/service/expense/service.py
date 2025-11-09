from datetime import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Expense, Category
from app.db.models.category import TypesOfCat
from app.schemas import expense
from app.schemas.dataclasses.category import CategoryDTO
from app.schemas.dataclasses.expense import ExpenseDTO
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.service.category.crud import get_category_by_id
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryTypeException,
)
from app.service.expense import crud as expense_crud
from app.service.expense.exception import (
    ExpenseNotFoundException,
    ExpenseUserPermissionDeniedException,
)


class ExpenseService:
    """Сервис трат: создание, удаление, изменение, получение"""

    @staticmethod
    async def _validate_category(db: AsyncSession, category_id: int) -> CategoryDTO:
        category_exists = await get_category_by_id(db, category_id)
        if not category_exists:
            raise CategoryNotFoundException("Категория не найдена")
        return category_exists

    async def create_expense(
        self,
        db: AsyncSession,
        spending: ExpenseCreate,
        user_id: int,
    ) -> ExpenseDTO:
        """Создание траты в БД"""

        category = await self._validate_category(db, spending.category_id)

        if not category.type_of_category == TypesOfCat.EXPENSE:
            raise CategoryTypeException("Тип категории не трата")

        new_expense = await expense_crud.create_expense(db, spending, user_id)
        return ExpenseDTO(
            id=new_expense.id,
            expense_date=new_expense.expense_date,
            user_id=new_expense.user_id,
            category_id=new_expense.category_id,
            value=new_expense.value,
            comment=new_expense.comment,
        )

    async def get_expenses(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int,
        limit: int,
        from_date: datetime,
        to_date: datetime,
    ) -> Tuple[list[ExpenseDTO], float]:
        """Возвращает все траты юзера с пагинацией"""

        expenses: list[ExpenseDTO] = [
            ExpenseDTO(
                id=new_expense.id,
                expense_date=new_expense.expense_date,
                user_id=new_expense.user_id,
                category_id=new_expense.category_id,
                value=new_expense.value,
                comment=new_expense.comment,
            )
            for new_expense in await expense_crud.get_user_expenses(
                db, user_id, skip, limit, from_date, to_date
            )
        ]

        total_expenses = await expense_crud.get_total_expenses(
            db, user_id, from_date, to_date
        )
        return expenses, total_expenses

    async def get_expense_by_id(
        self, db: AsyncSession, spending_id: int, user_id: int
    ) -> ExpenseDTO:
        """Возвращает трату по id + проверка на то является ли пользователь владельцем траты"""

        expense = await expense_crud.get_expense_by_id(db, spending_id)
        if not expense:
            raise ExpenseNotFoundException("Трата с таким id не найдена") from None

        if not expense.user_id == user_id:
            raise ExpenseUserPermissionDeniedException(
                "Трата не принадлежит пользователю"
            ) from None

        return ExpenseDTO(
            id=expense.id,
            expense_date=expense.expense_date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            value=expense.value,
            comment=expense.comment,
        )

    async def update_expense(
        self,
        db: AsyncSession,
        expense_id: int,
        new_expense: ExpenseUpdate,
        user_id: int,
    ) -> ExpenseDTO:
        """Обновляет трату и возвращает обновленную трату пользователю | идемпотентен: создаст трату если ее нет"""

        category = await self._validate_category(
            db, new_expense.category_id
        )  # Валидация категории траты
        expense = await expense_crud.get_expense_by_id(db, expense_id)

        if not expense:
            raise ExpenseNotFoundException("Трата не найдена") from None

        if expense.user_id != user_id:
            raise ExpenseUserPermissionDeniedException(
                "Трата не принадлежит пользователю"
            )

        await expense_crud.update_expense(
            db, expense_id, new_expense, user_id
        )  # обновляем трату

        return ExpenseDTO(
            id=expense.id,
            expense_date=expense.expense_date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            value=expense.value,
            comment=expense.comment,
        )

    async def delete_expense(self, db, expense_id, user_id):
        """Удаляет трату пользователя"""

        expense = await expense_crud.get_expense_by_id(db, expense_id)

        if not expense:
            raise ExpenseNotFoundException("Трата не найдена")

        if expense.user_id != user_id:
            raise ExpenseUserPermissionDeniedException(
                "Трата не принадлежит пользователю"
            )

        await expense_crud.delete_expense(db, expense)

        return ExpenseDTO(
            id=expense.id,
            expense_date=expense.expense_date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            value=expense.value,
            comment=expense.comment,
        )
