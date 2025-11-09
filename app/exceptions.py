import traceback

from fastapi import HTTPException, Request, status, FastAPI
from fastapi.responses import JSONResponse

from app.core.exceptions.auth import (
    UserAlreadyExistsHTTPException,
    UserNotFoundHTTPException,
    TokenExpiredHTTPException,
    InvalidCredentialsHTTPException,
)
from app.core.exceptions.category import (
    CategoryNotFoundHTTPException,
    CategoryTypeHTTPException,
    CategoryPermissionHTTPException,
)
from app.core.exceptions.expense import (
    ExpenseNotFoundHTTPException,
    ExpenseUserPermissionDeniedHTTPException,
)
from app.core.exceptions.income import (
    IncomePeriodHTTPException,
    IncomeNotFoundHTTPException,
    IncomeUserPermissionHTTPException,
)
from app.service.auth.exceptions import (
    AuthException,
    UserAlreadyExists,
    UserNotFound,
    CredentialsException,
    TokenExpiredException,
)

from app.service.category.exception import (
    CategoryException,
    CategoryNotFoundException,
    CategoryTypeException,
    CategoryPermissionException,
)
from app.service.expense.exception import (
    ExpenseException,
    ExpenseNotFoundException,
    ExpenseUserPermissionDeniedException,
)
from app.service.income.exceptions import (
    IncomeException,
    IncomePeriodException,
    IncomeNotFoundException,
    IncomeUserPermissionException,
)

AUTH_TO_HTTP: dict[type[AuthException], type[HTTPException]] = {
    UserAlreadyExists: UserAlreadyExistsHTTPException,
    UserNotFound: UserNotFoundHTTPException,
    CredentialsException: InvalidCredentialsHTTPException,
    TokenExpiredException: TokenExpiredHTTPException,
}

CATEGORY_TO_HTTP: dict[type[CategoryException], type[HTTPException]] = {
    CategoryNotFoundException: CategoryNotFoundHTTPException,
    CategoryTypeException: CategoryTypeHTTPException,
    CategoryPermissionException: CategoryPermissionHTTPException,
}

EXPENSES_TO_HTTP: dict[type[ExpenseException], type[HTTPException]] = {
    ExpenseNotFoundException: ExpenseNotFoundHTTPException,
    ExpenseUserPermissionDeniedException: ExpenseUserPermissionDeniedHTTPException,
}

INCOMES_TO_HTTP: dict[type[IncomeException], type[HTTPException]] = {
    IncomePeriodException: IncomePeriodHTTPException,
    IncomeNotFoundException: IncomeNotFoundHTTPException,
    IncomeUserPermissionException: IncomeUserPermissionHTTPException,
}


class ExceptionHandler:
    """Класс хендлер HTTP exception'ов"""

    async def auth_handler(self, request: Request, exc: AuthException):
        """хендлер auth модуля"""

        traceback.print_exc()

        http_exc_cls = AUTH_TO_HTTP.get(type(exc))
        if http_exc_cls is not None:
            raise http_exc_cls()

        # на всякий случай: неизвестный наследник CoreException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    async def category_handler(self, request: Request, exc: CategoryException):
        """Хендлер категорий"""

        traceback.print_exc()

        http_exc_cls = CATEGORY_TO_HTTP.get(type(exc))
        if http_exc_cls is not None:
            raise http_exc_cls()

        # на всякий случай: неизвестный наследник CoreException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    async def expense_handler(self, request: Request, exc: ExpenseException):
        """Хендлер трат"""

        traceback.print_exc()

        http_exc_cls = EXPENSES_TO_HTTP.get(type(exc))
        if http_exc_cls is not None:
            raise http_exc_cls()

        # на всякий случай: неизвестный наследник CoreException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    async def income_handler(self, request: Request, exc: IncomeException):
        """Хендлер доходов"""

        traceback.print_exc()

        http_exc_cls = INCOMES_TO_HTTP.get(type(exc))
        if http_exc_cls is not None:
            raise http_exc_cls()

        # на всякий случай: неизвестный наследник CoreException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    # ─── Fallback ────────────────────────────────────────────────────────────
    async def handle_generic_exception(self, request: Request, exc: Exception):
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error."},
        )

    # ───────────────────────── Регистрация в FastAPI ─────────────────────────
    @classmethod
    def register(cls, app: FastAPI):
        handler = cls()

        app.add_exception_handler(
            AuthException,
            handler.auth_handler,
        )

        app.add_exception_handler(
            CategoryException,
            handler.category_handler,
        )

        app.add_exception_handler(
            ExpenseException,
            handler.expense_handler,
        )

        app.add_exception_handler(
            IncomeException,
            handler.income_handler,
        )

        app.add_exception_handler(
            Exception,
            handler.handle_generic_exception,
        )
