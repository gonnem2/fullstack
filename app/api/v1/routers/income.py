from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.db.database import get_db
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeOut, Income
from app.service.auth.dependencies import get_current_user
from app.service.income.service import IncomeService

router = APIRouter(prefix="/income", tags=["Income"])
income_service = IncomeService()


@router.post(
    "",
    summary="Create a new income",
    status_code=status.HTTP_201_CREATED,
    response_model=IncomeOut,
)
async def create_income(
    db: Annotated[AsyncSession, Depends(get_db)],
    income: Annotated[IncomeCreate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Создать новую запись дохода."""
    new_income = await income_service.create_income(db, current_user, income)

    return new_income


@router.get(
    "",
    summary="Получаем доходы за период",
    response_model=IncomeOut,
)
async def get_incomes_by_period(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    from_date: datetime = Query(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    ),
    to_date: datetime = Query(default_factory=datetime.now),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    """Получить все доходы за период с пагинацией."""
    incomes, total = await income_service.get_incomes_by_period(
        db, from_date, to_date, skip, limit, current_user
    )
    return {
        "data": {
            "incomes": incomes,
            "skip": skip,
            "limit": limit,
        },
        "total": total,
    }


@router.get(
    "/{income_id}",
    summary="Получаем доход по его id",
    response_model=Income,
)
async def get_income_by_id(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получить запись дохода по ID."""

    income = await income_service.get_income_by_id(db, income_id, current_user)
    return income


@router.put(
    "/{income_id}",
    summary="Update income by ID",
    response_model=Income,
)
async def update_income(
    income_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    income_update: Annotated[IncomeUpdate, Body(...)],
):
    """Обновить запись дохода."""
    updated_income = await income_service.update_income(
        db, income_id, income_update, current_user
    )
    return updated_income


@router.delete(
    "/{income_id}",
    summary="Удаляет доход пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_income(
    income_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Удалить запись дохода."""
    await income_service.delete_income(db, income_id, current_user)
