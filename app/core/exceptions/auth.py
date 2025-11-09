from starlette import status

from app.core.exceptions.base_http import Base


class InvalidCredentialsHTTPException(Base):
    """Неверные данные при распознавании токена"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredHTTPException(Base):
    """Время действия токена истекло"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}


class UserAlreadyExistsHTTPException(Base):
    """Пользователь уже создан"""

    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"


class UserNotFoundHTTPException(Base):
    """Пользователь не найден"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"
