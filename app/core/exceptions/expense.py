from starlette import status

from app.core.exceptions.base_http import Base


class ExpenseNotFoundHTTPException(Base):
    """Трата не найдена"""

    status_code = (status.HTTP_404_NOT_FOUND,)
    detail = "Expense not found"


class ExpenseUserPermissionDeniedHTTPException(Base):
    """Нет доступа к трате"""

    status_code = status.HTTP_403_FORBIDDEN
    detail = "Expense user permission denied"
