import pytest
from unittest.mock import AsyncMock, patch
from fastapi.security import OAuth2PasswordRequestForm
from app.service.auth.service import AuthService
from app.service.auth.exceptions import UserAlreadyExists, UserNotFound, AuthException
from app.schemas.user import UserCreate
from app.db.models.user import User

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_create_user_success(db_session):
    service = AuthService()
    user_data = UserCreate(username="new", email="new@ex.com", password="123")
    with patch(
        "app.service.auth.crud.get_user_by_email_or_username",
        AsyncMock(return_value=None),
    ):
        with patch(
            "app.service.auth.crud.create_user",
            AsyncMock(return_value=User(id=99, username="new")),
        ):
            user = await service.create_user(db_session, user_data)
            assert user.username == "new"


@pytest.mark.asyncio
async def test_create_user_already_exists(db_session):
    service = AuthService()
    user_data = UserCreate(username="existing", email="exist@ex.com", password="123")
    with patch(
        "app.service.auth.crud.get_user_by_email_or_username",
        AsyncMock(return_value=User()),
    ):
        with pytest.raises(UserAlreadyExists):
            await service.create_user(db_session, user_data)


@pytest.mark.asyncio
async def test_get_tokens_success(db_session):
    service = AuthService()
    form = OAuth2PasswordRequestForm(username="test", password="correct")
    user_db = User(id=1, username="test", hashed_password="$2b$12$...")  # mocked
    with patch(
        "app.service.auth.crud.get_user_by_username", AsyncMock(return_value=user_db)
    ):
        with patch("app.service.auth.service.validate_password", return_value=True):
            with patch.object(service, "_save_session", AsyncMock()):
                access, refresh = await service.get_tokens(db_session, form)
                assert access and refresh


@pytest.mark.asyncio
async def test_get_tokens_user_not_found(db_session):
    service = AuthService()
    form = OAuth2PasswordRequestForm(username="nobody", password="x")
    with patch(
        "app.service.auth.crud.get_user_by_username", AsyncMock(return_value=None)
    ):
        with pytest.raises(UserNotFound):
            await service.get_tokens(db_session, form)


@pytest.mark.asyncio
async def test_refresh_token_success(db_session):
    service = AuthService()
    old_jti = "old-jti"
    new_jti = "new-jti"
    with patch.object(service, "_get_session_user_id", AsyncMock(return_value=1)):
        with patch.object(service, "_delete_session", AsyncMock()):
            with patch.object(service, "_generate_jti", return_value=new_jti):
                with patch.object(service, "_save_session", AsyncMock()):
                    with patch(
                        "jwt.decode",
                        return_value={"type": "refresh", "jti": old_jti, "sub": "1"},
                    ):
                        with patch(
                            "app.service.auth.crud.get_user_by_id",
                            AsyncMock(return_value=User(id=1)),
                        ):
                            access, refresh = await service.refresh_token(
                                db_session, "fake_token"
                            )
                            assert access and refresh
