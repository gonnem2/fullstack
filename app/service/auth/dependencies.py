import jwt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2_scheme
from app.core.settings import settings
from app.db import User
from app.db.database import get_db
from app.db.models.user import UserRoles
from app.service.auth.exceptions import (
    CredentialsException,
    TokenExpiredException,
    NotAdminUserException,
)
from app.service.auth import crud as auth_crud


async def get_current_user(
    db: AsyncSession = Depends(get_db), token=Depends(oauth2_scheme)
):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        u_id: str = payload.get("sub")
        if not u_id:
            raise CredentialsException("Неверный токен")

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException("Время действия токена истекло")
    except jwt.PyJWTError:
        raise CredentialsException("Ошибка при распознавании токена")

    user = await auth_crud.get_user_by_id(int(u_id), db)
    if user is None:
        raise CredentialsException("Ошибка при распознавании токена")
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRoles.ADMIN:
        return current_user
    raise NotAdminUserException("User is not admin")


async def get_user(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRoles.USER:
        return current_user
    raise NotAdminUserException("User's role is not 'user'")
