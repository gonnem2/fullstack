from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Expense
from app.schemas.expense import ExpenseCreate


async def create_expense(
    db: AsyncSession, new_expense: ExpenseCreate, user_id: int
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
    db: AsyncSession, user_id: int, skip: int, limit: int
) -> List[Expense]:
    """Возаращет все траты пользователя с пагинацией"""

    stmt = select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
    result = await db.scalars(stmt)
    expenses = list(result.all())
    return expenses
