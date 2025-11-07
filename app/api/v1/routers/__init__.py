from .user import router as user_router
from .expense import router as expense_router
from .auth import router as auth_router
from .stats import router as stats_router
from .income import router as income_router


__all__ = [
    "user_router",
    "expense_router",
    "auth_router",
    "stats_router",
    "income_router",
]
