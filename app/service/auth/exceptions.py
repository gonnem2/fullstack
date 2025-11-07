class AuthException(Exception): ...


class UserAlreadyExists(AuthException):
    """Пользователь уже содержится в БД"""


class UserNotFound(AuthException):
    """Пользователь не найден"""


class CredentialsException(AuthException):
    """Ошибка данных у токена"""


class TokenExpiredException(AuthException):
    """Время действия токена истекло"""
