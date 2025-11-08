from datetime import datetime
from typing import List, Iterable

from sqlalchemy import insert, select, between, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Income
from app.schemas.dataclasses.income import IncomeDTO
from app.schemas.income import IncomeCreate, IncomeUpdate


async def create_category(
    db: AsyncSession, user_id, income: IncomeCreate
) -> IncomeDTO | None:
    """Добавляет категорию в БД"""

    stmt = (
        insert(Income)
        .values(user_id=user_id, **income.model_dump())
        .returning(
            Income.id,
            Income.user_id,
            Income.income_date,
            Income.category_id,
            Income.value,
            Income.comment,
        )
    )

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return None

    return IncomeDTO(
        id=row.id,
        user_id=row.user_id,
        income_date=row.income_date,
        category_id=row.category_id,
        value=row.value,
        comment=row.comment,
    )


async def get_incomes_by_period(
    db: AsyncSession,
    from_date: datetime,
    to_date: datetime,
    skip: int,
    limit: int,
    user_id: int,
) -> list[IncomeDTO]:
    """Возвращает все доходы за период"""

    stmt = (
        select(Income)
        .where(Income.user_id == user_id)
        .where(Income.income_date.between(from_date, to_date))
        .limit(limit)
        .offset(skip)
    )
    res = await db.scalars(stmt)
    rows: Iterable[Income] = res.all()

    return [
        IncomeDTO(
            id=income.id,
            user_id=income.user_id,
            category_id=income.category_id,
            income_date=income.income_date,
            value=income.value,
            comment=income.comment,
        )
        for income in rows
    ]


async def get_income_by_id(db: AsyncSession, income_id: int) -> IncomeDTO | None:
    """Получаем трату по id из БД"""

    stmt = select(Income).where(Income.id == income_id)
    res = await db.scalars(stmt)
    income = res.first()

    if not income:
        return None

    return IncomeDTO(
        id=income.id,
        user_id=income.user_id,
        category_id=income.category_id,
        income_date=income.income_date,
        value=income.value,
        comment=income.comment,
    )


async def update_income(
    db: AsyncSession, income_id: int, income_update: IncomeUpdate
) -> IncomeDTO | None:
    """Обновляет трату в БД"""
    stmt = (
        update(Income)
        .where(Income.id == income_id)
        .values(**income_update.model_dump())
        .returning(
            Income.id,
            Income.user_id,
            Income.income_date,
            Income.category_id,
            Income.value,
            Income.comment,
        )
    )

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return None

    return IncomeDTO(
        id=row.id,
        user_id=row.user_id,
        income_date=row.income_date,
        category_id=row.category_id,
        value=row.value,
        comment=row.comment,
    )


async def delete_income(db: AsyncSession, income_id: int) -> None:
    """Удаляет доход из БД"""

    stmt = delete(Income).where(Income.id == income_id)
    await db.execute(stmt)
