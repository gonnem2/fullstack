from fastapi import FastAPI

from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.stats import router as stats_router
from app.routers.income import router as income_router
from app.routers.expense import router as expense_router


app = FastAPI(
    title="FinanceTrack",
    version="0.0.1",
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(stats_router)
app.include_router(income_router)
app.include_router(expense_router)
