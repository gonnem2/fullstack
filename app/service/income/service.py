from datetime import datetime
from typing import Tuple, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.dataclasses.income import IncomeDTO
from app.schemas.income import IncomeCreate, IncomeUpdate
from app.service.category import crud as category_crud
from app.service.income import crud as income_crud
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryTypeException,
)
from app.service.income.exceptions import (
    IncomePeriodException,
    IncomeNotFoundException,
    IncomeUserPermissionException,
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

    async def get_incomes_by_period(
        self,
        db: AsyncSession,
        from_date: datetime,
        to_date: datetime,
        skip: int,
        limit: int,
        current_user: User,
    ) -> Tuple[list[IncomeDTO], int]:
        """Возвращает все доходы юзера за период и их сумму"""

        if from_date > to_date:
            raise IncomePeriodException("Период трат неправильный!")

        incomes: List[IncomeDTO] = await income_crud.get_incomes_by_period(
            db, from_date, to_date, skip, limit, current_user.id
        )
        total = sum(map(lambda x: x.value, incomes))
        return incomes, total

    async def get_income_by_id(
        self, db: AsyncSession, income_id: int, current_user: User
    ) -> IncomeDTO:
        """Получаем трату по id"""

        income = await income_crud.get_income_by_id(db, income_id)

        if not income:
            raise IncomeNotFoundException("Доход не найден")

        if income.user_id != current_user.id:
            raise IncomeUserPermissionException("Доход не принадлежит пользователю")

        return income

    async def update_income(
        self,
        db: AsyncSession,
        income_id: int,
        income_update: IncomeUpdate,
        current_user: User,
    ) -> IncomeDTO:
        """Обновляет доход согласно переданным данным(IncomeUpdate)"""
        income = await income_crud.get_income_by_id(db, income_id)

        if not income:
            raise IncomeNotFoundException("Доход не найден")

        if income.user_id != current_user.id:
            raise IncomeUserPermissionException(
                "Доход не принадлежит текущему пользователю"
            )

        updated_income: IncomeDTO = await income_crud.update_income(
            db, income_id, income_update
        )
        return updated_income

    async def delete_income(
        self, db: AsyncSession, income_id: int, current_user: User
    ) -> None:
        """Удаляет запись о доходе из БД"""

        income = await income_crud.get_income_by_id(db, income_id)
        if not income:
            raise IncomeNotFoundException("Доход не найден")

        if income.user_id != current_user.id:
            raise IncomeUserPermissionException("Доход не принадлежит пользователю")

        await income_crud.delete_income(db, income_id)
