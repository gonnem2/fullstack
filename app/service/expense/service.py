from datetime import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3.service import delete_file
from app.db.models.category import TypesOfCat
from app.schemas.dataclasses.category import CategoryDTO
from app.schemas.dataclasses.expense import ExpenseDTO
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
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
        image_key: str | None = None,
    ) -> ExpenseDTO:
        """Создание траты в БД"""

        category = await self._validate_category(db, spending.category_id)

        if not category.type_of_category == TypesOfCat.EXPENSE:
            raise CategoryTypeException("Тип категории не трата")

        new_expense = await expense_crud.create_expense(
            db, spending, user_id, image_key
        )
        return ExpenseDTO(
            id=new_expense.id,
            expense_date=new_expense.expense_date,
            user_id=new_expense.user_id,
            category_id=new_expense.category_id,
            value=new_expense.value,
            image_key=image_key,
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
        category_id: int | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        search: str | None = None,
        sort_by: str = "expense_date",
        sort_order: str = "desc",
    ) -> Tuple[list[ExpenseDTO], float]:

        expenses, total = await expense_crud.get_user_expenses(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
            category_id=category_id,
            min_value=min_value,
            max_value=max_value,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return expenses, total

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
            image_key=expense.image_key,
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
            image_key=expense.image_key,
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

        if expense.image_key:
            delete_file(expense.image_key)

        return ExpenseDTO(
            id=expense.id,
            expense_date=expense.expense_date,
            user_id=expense.user_id,
            category_id=expense.category_id,
            value=expense.value,
            image_key=expense.image_key,
            comment=expense.comment,
        )
