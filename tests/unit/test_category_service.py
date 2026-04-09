import pytest
from unittest.mock import AsyncMock, patch
from app.service.category.service import CategoryService
from app.service.category.exception import (
    CategoryNotFoundException,
    CategoryPermissionException,
)
from app.schemas.category import CreateCategory, CategoryUpdate
from app.schemas.dataclasses.category import CategoryDTO
from app.db.models.user import User

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_category():
    service = CategoryService()
    category_in = CreateCategory(title="Test", type_of_category="expense")
    current_user = User(id=1)
    with patch(
        "app.service.category.crud.create_category",
        AsyncMock(
            return_value=CategoryDTO(
                id=10, title="Test", type_of_category="expense", user_id=1
            )
        ),
    ):
        result = await service.create_category(None, category_in, current_user)
        assert result.id == 10


@pytest.mark.asyncio
async def test_get_category_not_found():
    service = CategoryService()
    with patch(
        "app.service.category.crud.get_category_by_id", AsyncMock(return_value=None)
    ):
        with pytest.raises(CategoryNotFoundException):
            await service.get_category(None, 999, User(id=1))


@pytest.mark.asyncio
async def test_get_category_other_user():
    service = CategoryService()
    category = CategoryDTO(id=5, title="Test", type_of_category="expense", user_id=2)
    with patch(
        "app.service.category.crud.get_category_by_id", AsyncMock(return_value=category)
    ):
        with pytest.raises(CategoryPermissionException):
            await service.get_category(None, 5, User(id=1))
