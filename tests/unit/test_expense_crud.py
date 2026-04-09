import pytest
from datetime import datetime
from app.service.expense.crud import get_user_expenses
from app.db.models.expense import Expense

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_user_expenses_with_filters(
    db_session, registered_user, expense_category
):
    # создаём расходы
    for i in range(2):
        exp = Expense(
            user_id=registered_user.id,
            category_id=expense_category.id,
            value=100 * (i + 1),
            expense_date=datetime.now(),
            comment="test",
        )
        db_session.add(exp)
    await db_session.commit()

    expenses, total = await get_user_expenses(
        db=db_session,
        user_id=registered_user.id,
        skip=0,
        limit=10,
        from_date=datetime(2020, 1, 1),
        to_date=datetime.now(),
        min_value=150,
        max_value=250,
    )
    assert len(expenses) == 1
    assert total == 1
