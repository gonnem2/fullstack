from datetime import datetime

import pytest
from unittest.mock import AsyncMock, patch
from app.service.expense.service import ExpenseService
from app.service.category.exception import CategoryTypeException
from app.schemas.expense import ExpenseCreate
from app.schemas.dataclasses.category import CategoryDTO

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_expense_wrong_category_type():
    service = ExpenseService()
    # Исправленный мок: добавляем все обязательные поля CategoryDTO
    with patch.object(
        service,
        "_validate_category",
        AsyncMock(
            return_value=CategoryDTO(
                id=1, title="", type_of_category="income", user_id=1
            )
        ),
    ):
        with pytest.raises(CategoryTypeException):
            await service.create_expense(
                None,
                ExpenseCreate(
                    category_id=1, cost=100, comment=None, expense_date=datetime.now()
                ),
                1,
                None,
            )
