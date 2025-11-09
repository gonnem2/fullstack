from datetime import datetime, timedelta
from typing import Tuple, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import User
from app.schemas.dataclasses.stats import (
    CategoryExpenseDTO,
    CategoryExpenseStatDTO,
    ExpenseDynamicDTO,
)
from app.schemas.stats import Period, PeriodEnum

from app.service.stats import crud as stats_crud


class StatsService:
    """Сервис статистики"""

    @staticmethod
    def _get_datetime_period(period: Period) -> Tuple[datetime, datetime]:
        now = datetime.now()
        match period.period:
            case PeriodEnum.today:
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
            case PeriodEnum.week:
                start = now - timedelta(days=7)
                end = now
            case PeriodEnum.month:
                start = now - timedelta(days=30)
                end = now
            case PeriodEnum.year:
                start = now - timedelta(days=365)
                end = now
            case _:
                start = now
                end = now
        return start, end

    async def get_category_expenses_stats(
        self, db: AsyncSession, period: Period, current_user: User
    ) -> CategoryExpenseStatDTO:
        """Возвращает статистику по 10 самым популярным категориями за период"""

        categories: List[CategoryExpenseDTO] = await stats_crud.get_category_expenses(
            db, current_user.id, *self._get_datetime_period(period)
        )
        total = sum(map(lambda x: x.amount, categories))

        # ограничение на количество категорий
        if len(categories) > 10:
            other_category = CategoryExpenseDTO(
                title="Другое", amount=sum(map(lambda x: x.amount, categories[10:]))
            )
            categories = categories[:9] + [other_category]

        return CategoryExpenseStatDTO(total=total, categories=categories)

    async def get_dynamic_stats(
        self, db: AsyncSession, period: Period, current_user: User
    ):
        """Возвращаем динамику расходов за период"""

        expenses: List[ExpenseDynamicDTO] = await stats_crud.get_expenses_dynamic(
            db,
            current_user.id,
            period.period,
            *self._get_datetime_period(period),
        )

        return expenses
