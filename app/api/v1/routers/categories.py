from typing import Annotated, List

from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db import User
from app.db.database import get_db
from app.schemas.category import (
    CreateCategory,
    CategoryResponse,
    CategoriesResponse,
    CategoryUpdate,
)
from app.schemas.dataclasses.category import CategoryDTO
from app.service.auth.dependencies import get_current_user
from app.service.category.service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])
category_service = CategoryService()


@router.post(
    "/",
    summary="Создание новой категории",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryResponse,
)
async def create_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Annotated[CreateCategory, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Создание категории"""
    new_category = await category_service.create_category(db, category, current_user)
    return new_category


@router.get(
    "/",
    summary="Получение всех категорий пользователя",
    response_model=CategoriesResponse,
)
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
):
    """Получение всех категорий пользователя"""

    categories: List[CategoryDTO] = await category_service.get_categories(
        db, current_user, skip, limit
    )

    return {
        "categories": categories,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Возвращает категорию по id",
)
async def get_category_by_id(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Получаем категорию юзера по id"""

    category: CategoryDTO = await category_service.get_category(
        db, category_id, current_user
    )
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Обновляет категорию по id",
)
async def update_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    category: CategoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    updated_category = await category_service.update_category(
        db, category_id, category, current_user
    )
    return updated_category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаляет категорию по id",
)
async def delete_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Удаляет категорию пользователя по id"""
    await category_service.delete_category(db, category_id, current_user)
