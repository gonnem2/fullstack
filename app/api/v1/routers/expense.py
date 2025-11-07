from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, Expense
from app.db.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseOut, ExpenseGet
from app.core.pagination import paginate
from app.service.auth.dependencies import get_current_user
from app.service.expense.service import ExpenseService

router = APIRouter(prefix="/spending", tags=["Spending"])
expense_service = ExpenseService()


@router.post(
    "",
    summary="Create a new spending",
    status_code=status.HTTP_201_CREATED,
    # response_model=ExpenseOut,
)
async def create_spending(
    db: Annotated[AsyncSession, Depends(get_db)],
    spending: Annotated[ExpenseCreate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Создать новую трату."""
    new_expense = await expense_service.create_expense(db, spending, current_user.id)

    return new_expense


# --- READ (list) ---
@router.get(
    "",
    summary="Получить расходы зв период",
    response_model=ExpenseGet,
)
async def get_all_user_spendings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    from_date: datetime = Query(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    ),
    to_date: datetime = Query(default_factory=datetime.now),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    """Получить все траты с пагинацией."""
    expenses: list[Expense] = await expense_service.get_expenses(
        db, current_user.id, skip, limit, from_date, to_date
    )
    return {
        "expenses": expenses,
        "skip": skip,
        "limit": limit,
    }


# --- READ (one) ---
@router.get(
    "/{spending_id}",
    summary="Get spending by ID",
    response_model=ExpenseOut,
)
async def get_spending_by_id(
    spending_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить одну трату по ID."""
    expense = await expense_service.get_expense_by_id(db, spending_id, current_user.id)
    return expense


# --- UPDATE ---
@router.put(
    "/{spending_id}",
    summary="Update spending by ID",
    response_model=ExpenseOut,
)
async def update_spending(
    expense_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    spending_update: Annotated[ExpenseUpdate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Обновить трату по ID."""
    updated_expense = await expense_service.update_expense(
        db,
        expense_id,
        spending_update,
        current_user.id,
    )
    return updated_expense


# --- DELETE ---
@router.delete(
    "/{spending_id}",
    summary="Delete spending by ID",
    status_code=status.HTTP_200_OK,
    response_model=ExpenseOut,
)
async def delete_spending(
    expense_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Удалить трату по ID."""
    deleted_expense = await expense_service.delete_expense(
        db, expense_id, current_user.id
    )

    return deleted_expense
