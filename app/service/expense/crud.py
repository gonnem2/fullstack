from datetime import datetime
from typing import List, Dict

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Expense
from app.schemas.dataclasses.expense import ExpenseDTO
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


async def create_expense(
    db: AsyncSession, new_expense: ExpenseCreate | ExpenseUpdate, user_id: int
) -> Expense:
    """Добавляет трату в БД"""

    new_expense = Expense(
        user_id=user_id,
        expense_date=new_expense.expense_date,
        category_id=new_expense.category_id,
        value=new_expense.cost,
        comment=new_expense.comment,
    )
    db.add(new_expense)
    await db.flush()
    await db.refresh(new_expense)
    return new_expense


async def get_user_expenses(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> List[Expense]:
    """Возвращает траты пользователя с пагинацией и общую сумму"""

    stmt = select(Expense).where(Expense.user_id == user_id)
    if from_date and to_date:
        stmt = stmt.where(Expense.expense_date.between(from_date, to_date))

    stmt = stmt.offset(skip).limit(limit)
    result = await db.scalars(stmt)
    expenses = list(result.all())
    return expenses


async def get_total_expenses(
    db: AsyncSession,
    user_id: int,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
):
    query = select(func.sum(Expense.value)).where(Expense.user_id == user_id)

    if from_date:
        query = query.where(Expense.expense_date >= from_date)
    if to_date:
        query = query.where(Expense.expense_date <= to_date)

    result = await db.execute(query)
    total = result.scalar() or 0

    return total


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
