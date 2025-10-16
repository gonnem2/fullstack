from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeOut

router = APIRouter(prefix="/income", tags=["Income"])


@router.post(
    "",
    summary="Create a new income",
    status_code=status.HTTP_201_CREATED,
    response_model=IncomeOut,
)
async def create_income(
    db: Annotated[AsyncSession, Depends(get_db)],
    income: Annotated[IncomeCreate, Body(...)],
):
    """Создать новую запись дохода."""
    return {"message": "Income created"}


@router.get(
    "",
    summary="Get all incomes (with pagination)",
    response_model=list[IncomeOut],
)
async def get_all_incomes(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    """Получить все доходы."""
    return []


@router.get(
    "/{income_id}",
    summary="Get income by ID",
    response_model=IncomeOut,
)
async def get_income_by_id(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить запись дохода по ID."""
    return {"message": f"Income {income_id}"}


@router.put(
    "/{income_id}",
    summary="Update income by ID",
    response_model=IncomeOut,
)
async def update_income(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    income_update: Annotated[IncomeUpdate, Body(...)],
):
    """Обновить запись дохода."""
    return {"message": f"Income {income_id} updated"}


@router.delete(
    "/{income_id}",
    summary="Delete income by ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_income(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Удалить запись дохода."""
    return None
