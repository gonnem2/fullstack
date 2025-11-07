class ExpenseException(Exception):
    """Базовый класс исключений"""


class CategoryNotFoundException(ExpenseException):
    """Не найдена категория"""


class CategoryTypeException(ExpenseException):
    """Неправильный тип категории(!= трата)"""
