class ExpenseException(Exception):
    """Базовое исключение траты"""


class ExpenseNotFoundException(ExpenseException):
    """Трата не найдена"""


class ExpenseUserPermissionDeniedException(ExpenseException):
    """Трата не принадлежит пользователю"""
