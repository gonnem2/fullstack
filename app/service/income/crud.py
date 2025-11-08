from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Income
from app.schemas.dataclasses.income import IncomeDTO
from app.schemas.income import IncomeCreate


async def create_category(
    db: AsyncSession, user_id, income: IncomeCreate
) -> IncomeDTO | None:
    """Добавляет категорию в БД"""

    stmt = (
        insert(Income)
        .values(user_id=user_id, **income.model_dump())
        .returning(
            Income.id,
            Income.user_id,
            Income.income_date,
            Income.category_id,
            Income.value,
            Income.comment,
        )
    )

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        return None

    return IncomeDTO(
        id=row.id,
        user_id=row.user_id,
        income_date=row.income_date,
        category_id=row.category_id,
        value=row.value,
        comment=row.comment,
    )
