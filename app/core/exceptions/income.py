from starlette import status

from app.core.exceptions.base_http import Base


class IncomePeriodHTTPException(Base):
    """Период дохода не соответствует"""

    status_code = (status.HTTP_400_BAD_REQUEST,)
    detail = "Income period error"


class IncomeNotFoundHTTPException(Base):
    """Доход не найден"""

    status_code = (status.HTTP_404_NOT_FOUND,)
    detail = "Income not found"


class IncomeUserPermissionHTTPException(Base):
    """Доход не юзера"""

    status_code = (status.HTTP_400_BAD_REQUEST,)
    detail = "Income user permission error"
