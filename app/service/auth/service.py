from datetime import datetime, timedelta
from typing import Tuple, Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.security import validate_password
from app.db import User
from app.schemas.dataclasses.user import UserDTO
from app.schemas.user import UserCreate
from app.service.auth import crud as auth_crud
from app.service.auth.exceptions import (
    UserAlreadyExists,
    UserNotFound,
    AuthException,
    TokenExpiredException,
)


class AuthService:
    """Сервис авторизации: регистрация пользователя, создание токена, проверка токена"""

    @staticmethod
    def _crete_access_token(user_db: User):
        """Создание access-токена"""
        payload = {
            "sub": str(user_db.id),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def _create_refresh_token(user_db):
        """Создание refresh-токена"""
        payload = {
            "sub": str(user_db.id),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            "type": "refresh",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def create_user(self, db: AsyncSession, user: UserCreate) -> User:
        """Регистарция пользователя: создание в БД"""

        user_exists = await auth_crud.get_user_by_email_or_username(
            db, str(user.email), user.username
        )
        if user_exists:
            raise UserAlreadyExists("Такой пользователь уже создан")

        created_user = await auth_crud.create_user(db, user)
        return created_user

    async def get_tokens(
        self,
        db: AsyncSession,
        user: OAuth2PasswordRequestForm,
    ) -> Tuple[str, str]:
        """Создает JWT токен для авторизации"""

        user_db = await auth_crud.get_user_by_username(db, user.username)
        if not user_db:
            raise UserNotFound("Пользователь не найден")

        if not validate_password(user.password, user_db.hashed_password):
            raise AuthException("Ошибка авторизации")

        access_token = self._crete_access_token(user_db)
        refresh_token = self._create_refresh_token(user_db)
        return access_token, refresh_token

    async def refresh_token(
        self, db: AsyncSession, refresh_token: str
    ) -> Tuple[str, str]:
        """Обновляет access токен на основе refresh токена"""
        try:
            # Декодируем refresh токен
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            # Проверяем тип токена
            if payload.get("type") != "refresh":
                raise AuthException("Неверный тип токена")

            # Получаем пользователя
            user_id = payload.get("sub")
            user_db = await auth_crud.get_user_by_id(int(user_id), db)
            if not user_db:
                raise UserNotFound("Пользователь не найден")

            # Создаем новую пару токенов
            new_access_token = self._crete_access_token(user_db)
            new_refresh_token = self._create_refresh_token(user_db)

            return new_access_token, new_refresh_token

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Refresh token истек")
        except jwt.InvalidTokenError:
            raise AuthException("Неверный refresh token")

