from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.db.database import get_db
from app.schemas.dataclasses.stats import CategoryExpenseStatDTO
from app.schemas.stats import Period, CategoriesStatOut
from app.service.auth.dependencies import get_current_user
from app.service.stats.service import StatsService

router = APIRouter(prefix="/stats", tags=["Statistics"])
stats_service = StatsService()


@router.get(
    "/expenses",
    summary="Получаем статистику трату по 10 самым крупным категориями",
    response_model=CategoriesStatOut,
)
async def get_expense_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    period: Annotated[Period, Query(..., description="Период today/week/month/year")],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получить статистику расходов по категориям за период."""
    result: CategoryExpenseStatDTO = await stats_service.get_category_expenses_stats(
        db, period, current_user
    )
    return result


@router.get(
    "/dynamic",
    summary="Возвращает динамику трат",
)
async def get_balance(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    period: Annotated[Period, Query(..., description="Период today/week/month/year")],
):
    """Получаем статистику по расходам в единицу времени(час/день/день/месяц)"""

    dynamic_stat = await stats_service.get_dynamic_stats(db, period, current_user)
    return dynamic_stat
