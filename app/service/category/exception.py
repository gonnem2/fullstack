class CategoryException(Exception):
    """Базовый класс исключений"""


class CategoryNotFoundException(CategoryException):
    """Не найдена категория"""


class CategoryTypeException(CategoryException):
    """Неправильный тип категории"""


class CategoryPermissionException(CategoryException):
    """Нет прав на категорию"""
