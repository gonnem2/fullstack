from math import ceil
from typing import Type, Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from pydantic import BaseModel


async def paginate(
    db: AsyncSession,
    model: Type[Any],
    page: int = 1,
    limit: int = 10,
) -> dict:
    """
    Универсальная функция пагинации для SQLAlchemy моделей.

    Args:
        db: асинхронная сессия SQLAlchemy.
        model: класс модели (например, Expense).
        page: номер страницы.
        limit: количество элементов на странице.

    Returns:
        dict: структура пагинации с ключами:
              page, limit, total, pages, data
    """
    # Подсчет общего количества записей
    total_query = select(func.count()).select_from(model)
    total = (await db.execute(total_query)).scalar_one()

    # Получение нужной страницы
    offset = (page - 1) * limit
    query = select(model).offset(offset).limit(limit)
    result = await db.execute(query)
    items: Sequence[Any] = result.scalars().all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": ceil(total / limit) if total else 1,
        "data": items,
    }
