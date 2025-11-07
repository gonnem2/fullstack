from fastapi import APIRouter

from .routers import (
    auth_router,
    stats_router,
    income_router,
    user_router,
    expense_router,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(stats_router)
router.include_router(income_router)
router.include_router(user_router)
router.include_router(expense_router)
