import asyncio
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import insert, select, update, delete, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Income
from app.schemas.dataclasses.income import IncomeDTO
from app.schemas.income import IncomeCreate, IncomeUpdate


async def create_category(
    db: AsyncSession, user_id, income: IncomeCreate, image_key: str
) -> IncomeDTO | None:
    """Добавляет категорию в БД"""

    stmt = (
        insert(Income)
        .values(user_id=user_id, **income.model_dump(), image_key=image_key)
        .returning(
            Income.id,
            Income.user_id,
            Income.income_date,
            Income.category_id,
            Income.value,
            Income.image_key,
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
        image_key=row.image_key,
        comment=row.comment,
    )


async def get_incomes_by_period(
    db: AsyncSession,
    user_id: int,
    from_date: datetime,
    to_date: datetime,
    skip: int,
    limit: int,
    category_id: Optional[int] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = "income_date",
    sort_order: str = "desc",
) -> Tuple[List[IncomeDTO], int]:

    base_filters = [
        Income.user_id == user_id,
        Income.income_date >= from_date,
        Income.income_date <= to_date,
    ]

    if category_id:
        base_filters.append(Income.category_id == category_id)

    if min_value is not None:
        base_filters.append(Income.value >= min_value)

    if max_value is not None:
        base_filters.append(Income.value <= max_value)

    if search:
        base_filters.append(Income.comment.ilike(f"%{search}%"))

    # total
    total_query = select(func.count()).select_from(Income).where(*base_filters)

    # data
    data_query = select(Income).where(*base_filters)

    column = getattr(Income, sort_by)
    order = desc(column) if sort_order == "desc" else asc(column)

    data_query = data_query.order_by(order).offset(skip).limit(limit)

    total_result, data_result = await asyncio.gather(
        db.execute(total_query),
        db.execute(data_query),
    )

    total = total_result.scalar_one()

    incomes = [
        IncomeDTO(
            id=i.id,
            user_id=i.user_id,
            category_id=i.category_id,
            income_date=i.income_date,
            value=i.value,
            image_key=i.image_key,
            comment=i.comment,
        )
        for i in data_result.scalars().all()
    ]

    return incomes, total


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
        image_key=income.image_key,
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
            Income.image_key,
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
        image_key=row.image_key,
        comment=row.comment,
    )


async def delete_income(db: AsyncSession, income_id: int) -> None:
    """Удаляет доход из БД"""

    stmt = delete(Income).where(Income.id == income_id)
    await db.execute(stmt)
