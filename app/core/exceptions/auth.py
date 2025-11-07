from starlette import status

from app.core.exceptions.base_http import Base


class InvalidCredentialsException(Base):
    """Неверные данные при распознавании токена"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredException(Base):
    """Время действия токена истекло"""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}
