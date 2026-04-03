from datetime import datetime, timedelta
from typing import Annotated
import re
from fastapi import (
    APIRouter,
    Depends,
    Body,
    Query,
    status,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3.service import upload_file, generate_download_url
from app.db import User, Expense
from app.db.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseOut, ExpenseGet
from app.core.pagination import paginate
from app.service.auth.dependencies import get_current_user
from app.service.expense.service import ExpenseService

router = APIRouter(prefix="/spending", tags=["Spending"])
expense_service = ExpenseService()


@router.post(
    "",
    summary="Create a new spending",
    status_code=status.HTTP_201_CREATED,
    # response_model=ExpenseOut,
)
async def create_spending(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    expense_date: datetime = Form(...),
    category_id: int = Form(...),
    cost: float = Form(...),
    comment: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    """Создать новую запись расхода."""

    image_key = None
    if image:
        image_key = await upload_file(image, current_user.id)

    spending = ExpenseCreate(
        expense_date=expense_date,
        category_id=category_id,
        cost=cost,
        comment=comment,
    )

    new_expense = await expense_service.create_expense(
        db, spending, current_user.id, image_key
    )

    return new_expense


@router.get(
    "",
    summary="Получить расходы за период (с фильтрацией, сортировкой, пагинацией)",
    response_model=ExpenseGet,
)
async def get_all_user_spendings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    # базовый фильтр
    from_date: datetime = Query(
        default_factory=lambda: datetime.now() - timedelta(days=1)
    ),
    to_date: datetime = Query(default_factory=datetime.now),
    # фильтры
    category_id: int | None = Query(None),
    min_value: float | None = Query(None, ge=0),
    max_value: float | None = Query(None, ge=0),
    search: str | None = Query(None),
    # сортировка
    sort_by: str = Query("expense_date", regex="^(expense_date|value)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    # пагинация
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    expenses, total = await expense_service.get_expenses(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        from_date=from_date,
        to_date=to_date,
        category_id=category_id,
        min_value=min_value,
        max_value=max_value,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {
        "data": {
            "expenses": expenses,
            "skip": skip,
            "limit": limit,
        },
        "total": total,
    }


# --- READ (one) ---
@router.get(
    "/{spending_id}",
    summary="Get spending by ID",
    response_model=ExpenseOut,
)
async def get_spending_by_id(
    spending_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить одну трату по ID."""
    expense = await expense_service.get_expense_by_id(db, spending_id, current_user.id)
    return expense


# --- UPDATE ---
@router.put(
    "/{spending_id}",
    summary="Update spending by ID",
    response_model=ExpenseOut,
)
async def update_spending(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    spending_update: Annotated[ExpenseUpdate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Обновить трату по ID."""
    updated_expense = await expense_service.update_expense(
        db,
        spending_id,
        spending_update,
        current_user.id,
    )
    return updated_expense


# --- DELETE ---
@router.delete(
    "/{spending_id}",
    summary="Delete spending by ID",
    status_code=status.HTTP_200_OK,
    response_model=ExpenseOut,
)
async def delete_spending(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Удалить трату по ID."""
    deleted_expense = await expense_service.delete_expense(
        db, spending_id, current_user.id
    )

    return deleted_expense


@router.get("/{spending_id}/image")
async def get_income_image(
    spending_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    expense = await expense_service.get_expense_by_id(db, spending_id, current_user.id)

    if not expense.image_key:
        raise HTTPException(404, "No image")

    url = generate_download_url(expense.image_key)

    external_url = re.sub(r"^https?://minio:\d+", "http://localhost:9000", url)
    return external_url
