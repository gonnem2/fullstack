import calendar

from app.db import User, Category, Expense
from app.db.models.category import TypesOfCat
from app.schemas.dataclasses.stats import CategoryExpenseDTO, ExpenseDynamicDTO

from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.schemas.stats import PeriodEnum


async def get_category_expenses(
    db: AsyncSession, user_id: int, from_date: datetime, to_date: datetime
) -> List[CategoryExpenseDTO]:
    """Получение категорий и трат в категориях за период"""

    stmt = (
        select(
            Category.id.label("category_id"),
            Category.title,
            func.sum(Expense.value).label("total_expense"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Category.user_id == user_id,
            Category.type_of_category == TypesOfCat.EXPENSE,
            Expense.expense_date.between(from_date, to_date),
        )
        .group_by(Category.id, Category.title)
        .having(func.sum(Expense.value) > 0)
        .order_by(func.sum(Expense.value).desc())
    )

    res = await db.execute(stmt)
    rows = res.mappings().all()

    return [
        CategoryExpenseDTO(
            title=row["title"],
            amount=int(row["total_expense"]),
        )
        for row in rows
    ]


async def get_expenses_dynamic(
    db: AsyncSession,
    user_id: int,
    period: PeriodEnum,
    from_date: datetime,
    to_date: datetime,
) -> List[ExpenseDynamicDTO] | None:
    """Получаем расходы за период с фиксированным количеством записей"""

    if period == PeriodEnum.today:
        # Группировка по часам дня (24 записи)
        return await _get_hourly_stats(db, user_id, from_date, to_date)
    elif period == PeriodEnum.week:
        # Группировка по дням недели (7 записей)
        return await _get_weekly_stats(db, user_id, from_date, to_date)
    elif period == PeriodEnum.month:
        # Группировка по дням месяца (28-31 запись)
        return await _get_monthly_stats(db, user_id, from_date, to_date)
    elif period == PeriodEnum.year:
        # Группировка по дням года (365 записей)
        return await _get_yearly_stats(db, user_id, from_date, to_date)


async def _get_hourly_stats(
    db: AsyncSession, user_id: int, from_date: datetime, to_date: datetime
):
    """Статистика по часам - 24 записи"""
    # Создаем все 24 часа в Python
    hours = list(range(24))

    # Получаем статистику по существующим часам
    stmt = (
        select(
            func.extract("hour", Expense.expense_date).label("hour"),
            func.sum(Expense.value).label("amount"),
        )
        .where(
            Expense.user_id == user_id,
            Expense.expense_date.between(from_date, to_date),
        )
        .group_by(func.extract("hour", Expense.expense_date))
    )

    res = await db.execute(stmt)
    existing_hours = {int(row.hour): float(row.amount) for row in res}

    # Создаем результат для всех 24 часов
    result = []
    for hour in hours:
        amount = existing_hours.get(hour, 0.0)
        result.append(
            ExpenseDynamicDTO(
                date=datetime(from_date.year, from_date.month, from_date.day, hour),
                amount=amount,
            )
        )

    return result


async def _get_weekly_stats(
    db: AsyncSession, user_id: int, from_date: datetime, to_date: datetime
):
    """Статистика по дням недели - 7 записей"""
    days_of_week = list(range(7))  # 0-6

    # Получаем статистику по существующим дням недели
    stmt = (
        select(
            func.extract("dow", Expense.expense_date).label("day_of_week"),
            func.sum(Expense.value).label("amount"),
        )
        .where(
            Expense.user_id == user_id,
            Expense.expense_date.between(from_date, to_date),
        )
        .group_by(func.extract("dow", Expense.expense_date))
    )

    res = await db.execute(stmt)
    existing_days = {int(row.day_of_week): float(row.amount) for row in res}

    # Создаем результат для всех 7 дней недели
    result = []
    for day in days_of_week:
        amount = existing_days.get(day, 0.0)
        result.append(
            ExpenseDynamicDTO(
                date=from_date + timedelta(days=day),
                amount=amount,
            )
        )

    return result


async def _get_monthly_stats(
    db: AsyncSession, user_id: int, from_date: datetime, to_date: datetime
):
    """Статистика по дням месяца - все дни"""
    days_in_month = calendar.monthrange(from_date.year, from_date.month)[1]
    days = list(range(1, days_in_month + 1))

    # Получаем статистику по существующим дням месяца
    stmt = (
        select(
            func.extract("day", Expense.expense_date).label("day"),
            func.sum(Expense.value).label("amount"),
        )
        .where(
            Expense.user_id == user_id,
            Expense.expense_date.between(from_date, to_date),
        )
        .group_by(func.extract("day", Expense.expense_date))
    )

    res = await db.execute(stmt)
    existing_days = {int(row.day): float(row.amount) for row in res}

    # Создаем результат для всех дней месяца
    result = []
    for day in days:
        amount = existing_days.get(day, 0.0)
        result.append(
            ExpenseDynamicDTO(
                date=datetime(from_date.year, from_date.month, day),
                amount=amount,
            )
        )

    return result


async def _get_yearly_stats(
    db: AsyncSession, user_id: int, from_date: datetime, to_date: datetime
):
    """Статистика по дням года - 365/366 записей"""
    days_in_year = 366 if calendar.isleap(from_date.year) else 365
    days = list(range(1, days_in_year + 1))

    # Получаем статистику по существующим дням года
    stmt = (
        select(
            func.extract("doy", Expense.expense_date).label("day_of_year"),
            func.sum(Expense.value).label("amount"),
        )
        .where(
            Expense.user_id == user_id,
            Expense.expense_date.between(from_date, to_date),
        )
        .group_by(func.extract("doy", Expense.expense_date))
    )

    res = await db.execute(stmt)
    existing_days = {int(row.day_of_year): float(row.amount) for row in res}

    # Создаем результат для всех дней года
    result = []
    for day in days:
        amount = existing_days.get(day, 0.0)
        result.append(
            ExpenseDynamicDTO(
                date=datetime(from_date.year, 1, 1) + timedelta(days=day - 1),
                amount=amount,
            )
        )

    return result
