import asyncio
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, update, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Expense
from app.schemas.dataclasses.expense import ExpenseDTO
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


async def create_expense(
    db: AsyncSession,
    new_expense: ExpenseCreate | ExpenseUpdate,
    user_id: int,
    image_key: str,
) -> Expense:
    """Добавляет трату в БД"""

    new_expense = Expense(
        user_id=user_id,
        expense_date=new_expense.expense_date,
        category_id=new_expense.category_id,
        value=new_expense.cost,
        image_key=image_key,
        comment=new_expense.comment,
    )
    db.add(new_expense)
    await db.flush()
    await db.refresh(new_expense)
    return new_expense


async def get_user_expenses(
    db: AsyncSession,
    user_id: int,
    skip: int,
    limit: int,
    from_date: datetime,
    to_date: datetime,
    category_id: Optional[int] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = "expense_date",
    sort_order: str = "desc",
) -> Tuple[List[Expense], int]:
    """
    Возвращает (список расходов, общее количество записей без пагинации)
    """
    # Базовый фильтр
    base_filters = [
        Expense.user_id == user_id,
        Expense.expense_date >= from_date,
        Expense.expense_date <= to_date,
    ]

    if category_id:
        base_filters.append(Expense.category_id == category_id)
    if min_value is not None:
        base_filters.append(Expense.value >= min_value)
    if max_value is not None:
        base_filters.append(Expense.value <= max_value)
    if search:
        base_filters.append(Expense.comment.ilike(f"%{search}%"))

    # 1. Запрос для получения total
    total_query = select(func.count()).select_from(Expense).where(*base_filters)

    # 2. Запрос для получения данных с пагинацией и сортировкой
    data_query = select(Expense).where(*base_filters)

    # сортировка
    column = getattr(Expense, sort_by)
    order = desc(column) if sort_order == "desc" else asc(column)
    data_query = data_query.order_by(order).offset(skip).limit(limit)

    # выполняем оба запроса параллельно
    total_result, data_result = await asyncio.gather(
        db.execute(total_query), db.execute(data_query)
    )

    total = total_result.scalar_one()
    expenses = [
        ExpenseDTO(
            id=e.id,
            user_id=e.user_id,
            expense_date=e.expense_date,
            category_id=e.category_id,
            value=e.value,
            comment=e.comment,
            image_key=e.image_key,
        )
        for e in data_result.scalars().all()
    ]

    return expenses, total


async def get_expense_by_id(db: AsyncSession, spending_id: int) -> Expense:
    """возвращает трату по id"""

    stmt = select(Expense).where(Expense.id == spending_id)
    result = await db.scalars(stmt)
    expense = result.first()
    return expense


async def update_expense(
    db: AsyncSession, expense_id: int, new_expense: ExpenseUpdate, user_id: int
) -> None:
    """Обновляет трату"""

    stmt = (
        update(Expense)
        .where(Expense.id == expense_id)
        .values(
            expense_date=new_expense.expense_date,
            category_id=new_expense.category_id,
            value=new_expense.cost,
            comment=new_expense.comment,
        )
    )
    await db.execute(stmt)
    await db.flush()


async def delete_expense(db: AsyncSession, expense: Expense) -> None:
    """Удаляет трату"""

    await db.delete(expense)
    await db.flush()
