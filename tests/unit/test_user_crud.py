import pytest
from unittest.mock import AsyncMock, patch
from app.service.user.crud import change_user_role, get_all_users
from app.db.models.user import User, UserRoles

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_change_user_role(db_session, registered_user):
    user_id = registered_user.id
    await change_user_role(db_session, user_id, UserRoles.ADMIN)
    # проверим, что роль изменилась
    from app.service.user.crud import get_user_by_id

    user = await get_user_by_id(db_session, user_id)
    assert user.role == UserRoles.ADMIN.value.upper()


@pytest.mark.asyncio
async def test_get_all_users(db_session, registered_user, admin_user):
    users = await get_all_users(db_session, skip=0, limit=10)
    assert len(users) >= 2
