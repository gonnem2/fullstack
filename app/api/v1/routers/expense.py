from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User, Expense
from app.db.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseOut
from app.core.pagination import paginate
from app.service.auth.dependencies import get_current_user
from app.service.expense.service import ExpenseService

router = APIRouter(prefix="/spending", tags=["Spending"])
expense_service = ExpenseService()


@router.post(
    "",
    summary="Create a new spending",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseOut,
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
    summary="Get all spendings (with pagination)",
    response_model=list[ExpenseOut],
)
async def get_all_user_spendings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    """Получить все траты с пагинацией."""
    expenses: list[Expense] = await expense_service.get_expenses(
        db, current_user.id, skip, limit
    )
    return expenses


# --- READ (one) ---
@router.get(
    "/{spending_id}",
    summary="Get spending by ID",
    response_model=ExpenseOut,
)
async def get_spending_by_id(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить одну трату по ID."""
    # TODO: добавить выборку по ID
    return {"message": f"Spending {spending_id}"}


# --- UPDATE ---
@router.put(
    "/{spending_id}",
    summary="Update spending by ID",
    response_model=ExpenseOut,
)
async def update_spending(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    spending_update: Annotated[ExpenseUpdate, Body(...)],
):
    """Обновить трату по ID."""
    # TODO: добавить обновление
    return {"message": f"Spending {spending_id} updated"}


# --- DELETE ---
@router.delete(
    "/{spending_id}",
    summary="Delete spending by ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_spending(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Удалить трату по ID."""
    # TODO: добавить удаление
    return None
