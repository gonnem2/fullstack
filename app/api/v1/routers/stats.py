from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "/expenses",
    summary="Get expense statistics by period and type",
)
async def get_expense_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    period: Annotated[str, Query(..., description="Период: day / month / year")],
    category: Annotated[str | None, Query(..., description="Фильтр по категории")],
):
    """Получить статистику расходов по периоду и категории."""
    return {"period": period, "category": category, "data": []}


@router.get(
    "/balance",
    summary="Get total balance",
)
async def get_balance(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить текущий баланс (доходы - расходы)."""
    return {"balance": 0}
