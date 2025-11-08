class IncomeException(Exception):
    """Базовый класс исключений доходов"""


class IncomePeriodException(IncomeException):
    """Исключение периода трат"""


class IncomeNotFoundException(IncomeException):
    """Доход не найден"""


class IncomeUserPermissionException(IncomeException):
    """Доход не принадлежит пользователю"""
