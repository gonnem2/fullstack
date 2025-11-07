from typing import List

from sqlalchemy import select, update
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

    return Expense


async def get_user_expenses(
    db: AsyncSession, user_id: int, skip: int, limit: int
) -> List[Expense]:
    """Возаращет все траты пользователя с пагинацией"""

    stmt = select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
    result = await db.scalars(stmt)
    expenses = list(result.all())

    return expenses


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
