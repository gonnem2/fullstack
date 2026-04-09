import pytest
from datetime import datetime
from app.service.stats.crud import get_category_expenses
from app.db.models.expense import Expense

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_category_expenses(db_session, registered_user, expense_category):
    # создаём расходы
    for i in range(3):
        exp = Expense(
            user_id=registered_user.id,
            category_id=expense_category.id,
            value=100 * (i + 1),
            expense_date=datetime.now(),
            comment="test",
        )
        db_session.add(exp)
    await db_session.commit()

    result = await get_category_expenses(
        db_session, registered_user.id, datetime(2000, 1, 1), datetime(2100, 1, 1)
    )
    assert len(result) >= 1
    assert sum(item.amount for item in result) == 600
