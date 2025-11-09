from starlette import status

from app.core.exceptions.base_http import Base


class CategoryNotFoundHTTPException(Base):
    """Категория не найдена"""

    status_code = status.HTTP_404_NOT_FOUND
    detail = "Category not found"


class CategoryTypeHTTPException(Base):
    """Тип категории не соответствует"""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "The category type does not match the operation"


class CategoryPermissionHTTPException(Base):
    """Категория не принадлежит пользователю"""

    status_code = status.HTTP_409_CONFLICT
    detail = "The category permission denied"
