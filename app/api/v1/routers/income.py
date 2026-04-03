import re
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Body, Query, status, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3.service import upload_file, generate_download_url
from app.db import User
from app.db.database import get_db
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeOut, Income
from app.service.auth.dependencies import get_current_user
from app.service.income.service import IncomeService

router = APIRouter(prefix="/income", tags=["Income"])
income_service = IncomeService()


@router.post(
    "",
    summary="Create a new income",
    status_code=status.HTTP_201_CREATED,
    response_model=Income,
)
async def create_income(
    db: Annotated[AsyncSession, Depends(get_db)],
    # income: Annotated[IncomeCreate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    income_date: datetime = Form(...),
    category_id: int = Form(...),
    value: float = Form(...),
    comment: str | None = Form(None),
    image: UploadFile | None = File(None),
):
    """Создать новую запись дохода."""

    image_key = None

    if image:
        image_key = await upload_file(image, current_user.id)
    income = IncomeCreate(
        income_date=income_date,
        category_id=category_id,
        value=value,
        comment=comment,
    )
    new_income = await income_service.create_income(db, current_user, income, image_key)

    return new_income


@router.get(
    "",
    summary="Получаем доходы за период (с фильтрацией, сортировкой, пагинацией)",
    response_model=IncomeOut,
)
async def get_incomes_by_period(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
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
    sort_by: str = Query("income_date", regex="^(income_date|value)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    # пагинация
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    incomes, total = await income_service.get_incomes_by_period(
        db=db,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
        current_user=current_user,
        category_id=category_id,
        min_value=min_value,
        max_value=max_value,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return {
        "data": {
            "incomes": incomes,
            "skip": skip,
            "limit": limit,
        },
        "total": total,
    }


@router.get(
    "/{income_id}",
    summary="Получаем доход по его id",
    response_model=Income,
)
async def get_income_by_id(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получить запись дохода по ID."""

    income = await income_service.get_income_by_id(db, income_id, current_user)
    return income


@router.put(
    "/{income_id}",
    summary="Update income by ID",
    response_model=Income,
)
async def update_income(
    income_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    income_update: Annotated[IncomeUpdate, Body(...)],
):
    """Обновить запись дохода."""
    updated_income = await income_service.update_income(
        db, income_id, income_update, current_user
    )
    return updated_income


@router.delete(
    "/{income_id}",
    summary="Удаляет доход пользователя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_income(
    income_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Удалить запись дохода."""
    await income_service.delete_income(db, income_id, current_user)


@router.get("/{income_id}/image")
async def get_income_image(
    income_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    income = await income_service.get_income_by_id(db, income_id, current_user)

    if not income.image_key:
        raise HTTPException(404, "No image")

    url = generate_download_url(income.image_key)

    external_url = re.sub(r"^https?://minio:\d+", "http://localhost:9000", url)
    return external_url
