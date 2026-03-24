import uuid
from datetime import datetime, timedelta
from typing import Tuple, Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.memcached.session import memcached_session
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
    CredentialsException,
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

    def _create_refresh_token(self, user_db, jti: str) -> str:
        payload = {
            "sub": str(user_db.id),
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            "type": "refresh",
            "jti": jti,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_tokens(
        self, db: AsyncSession, user: OAuth2PasswordRequestForm
    ) -> Tuple[str, str]:
        user_db = await auth_crud.get_user_by_username(db, user.username)
        if not user_db:
            raise UserNotFound("Пользователь не найден")
        if not validate_password(user.password, user_db.hashed_password):
            raise CredentialsException("Ошибка авторизации")

        jti = self._generate_jti()
        expires_in = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        await self._save_session(user_db.id, jti, expires_in)

        access_token = self._crete_access_token(user_db)
        refresh_token = self._create_refresh_token(user_db, jti)
        return access_token, refresh_token

    @staticmethod
    def _generate_jti() -> str:
        """Генерация уникального идентификатора для refresh токена."""
        return str(uuid.uuid4())

    async def _save_session(self, user_id: int, jti: str, expires_in: int) -> None:
        """Сохраняет сессию в Memcached с ключом session:{jti} и значением user_id."""
        key = f"session:{jti}"
        await memcached_session.set(key, str(user_id), exptime=expires_in)

    async def _delete_session(self, jti: str) -> None:
        """Удаляет сессию из Memcached."""
        key = f"session:{jti}"
        await memcached_session.delete(key)

    async def _get_session_user_id(self, jti: str) -> int | None:
        """Возвращает user_id, если сессия с данным jti существует."""
        key = f"session:{jti}"
        data = await memcached_session.get(key)
        if data:
            return int(data.decode())
        return None

    async def create_user(self, db: AsyncSession, user: UserCreate) -> User:
        """Регистарция пользователя: создание в БД"""

        user_exists = await auth_crud.get_user_by_email_or_username(
            db, str(user.email), user.username
        )
        if user_exists:
            raise UserAlreadyExists("Такой пользователь уже создан")

        created_user = await auth_crud.create_user(db, user)
        return created_user

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> Tuple[str, str]:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise AuthException("Неверный тип токена")

            jti = payload.get("jti")
            if not jti:
                raise AuthException("Отсутствует jti")

            # Проверяем, что сессия активна в Memcached
            session_user_id = await self._get_session_user_id(jti)
            if session_user_id is None:
                raise AuthException("Сессия не найдена или отозвана")

            user_id = int(payload.get("sub"))
            if user_id != session_user_id:
                raise AuthException("Несоответствие пользователя")

            user_db = await auth_crud.get_user_by_id(user_id, db)
            if not user_db:
                raise UserNotFound("Пользователь не найден")

            # Удаляем старую сессию
            await self._delete_session(jti)

            # Создаём новую
            new_jti = self._generate_jti()
            expires_in = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
            await self._save_session(user_db.id, new_jti, expires_in)

            new_access_token = self._crete_access_token(user_db)
            new_refresh_token = self._create_refresh_token(user_db, new_jti)
            return new_access_token, new_refresh_token

        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Refresh token истек")
        except jwt.InvalidTokenError:
            raise AuthException("Неверный refresh token")

    async def logout(self, refresh_token: str, current_user_id: int) -> None:
        """Удаляет сессию по refresh токену (выход из системы)."""
        try:
            # Декодируем без проверки срока, чтобы можно было удалить даже истёкший токен
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )
            if payload.get("type") != "refresh":
                raise AuthException("Неверный тип токена")

            jti = payload.get("jti")
            if not jti:
                raise AuthException("Отсутствует jti")

            token_user_id = int(payload.get("sub"))
            if token_user_id != current_user_id:
                raise AuthException("Нельзя выйти из чужой сессии")

            await self._delete_session(jti)
        except jwt.PyJWTError as e:
            raise AuthException("Неверный refresh token") from e