from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal
from datetime import date

from app.db import User
from app.db.database import get_db
from app.db.models import Transaction
from app.schemas.transactions import (
    PaginatedTransactions,
    TransactionOut,
    TransactionCreate,
    TransactionUpdate,
)
from app.service.auth.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=PaginatedTransactions)
async def list_transactions(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Записей на страницу"),
    type: Optional[Literal["income", "expense"]] = Query(
        None, description="Тип: income | expense"
    ),
    category: Optional[str] = Query(None, description="Категория (точное совпадение)"),
    date_from: Optional[date] = Query(None, description="Дата начала YYYY-MM-DD"),
    date_to: Optional[date] = Query(None, description="Дата окончания YYYY-MM-DD"),
    amount_min: Optional[float] = Query(None, ge=0, description="Мин. сумма"),
    amount_max: Optional[float] = Query(None, ge=0, description="Макс. сумма"),
    search: Optional[str] = Query(
        None, max_length=200, description="Поиск по описанию (ILIKE)"
    ),
    sort_by: Literal["date", "amount", "category", "created_at"] = Query(
        "date", description="Поле сортировки"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Направление"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Transaction).where(Transaction.user_id == current_user.id)

    conditions = []

    if type:
        conditions.append(Transaction.type == type)
    if category:
        conditions.append(func.lower(Transaction.category) == category.lower())
    if date_from:
        conditions.append(Transaction.date >= date_from)
    if date_to:
        conditions.append(Transaction.date <= date_to)
    if amount_min is not None:
        conditions.append(Transaction.amount >= amount_min)
    if amount_max is not None:
        conditions.append(Transaction.amount <= amount_max)
    if search:
        conditions.append(Transaction.description.ilike(f"%{search}%"))

    if conditions:
        query = query.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_stmt) or 0

    sort_column_map = {
        "date": Transaction.date,
        "amount": Transaction.amount,
        "category": Transaction.category,
        "created_at": Transaction.created_at,
    }
    col = sort_column_map.get(sort_by, Transaction.date)
    order_fn = asc if sort_order == "asc" else desc
    query = query.order_by(order_fn(col))

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedTransactions(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/categories/list")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает все уникальные категории пользователя (для dropdown в фильтрах)."""
    stmt = (
        select(Transaction.category)
        .where(Transaction.user_id == current_user.id)
        .distinct()
        .order_by(Transaction.category)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [r for r in rows if r]


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = Transaction(**payload.model_dump(), user_id=current_user.id)
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return tx


@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = await _get_own_tx(db, tx_id, current_user.id)
    return tx


@router.patch("/{tx_id}", response_model=TransactionOut)
async def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = await _get_own_tx(db, tx_id, current_user.id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tx, field, value)

    await db.commit()
    await db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = await _get_own_tx(db, tx_id, current_user.id)
    await db.delete(tx)
    await db.commit()


async def _get_own_tx(db: AsyncSession, tx_id: int, user_id: int) -> Transaction:
    """Вернуть транзакцию или 404 если не найдена / не принадлежит пользователю."""
    stmt = select(Transaction).where(
        Transaction.id == tx_id,
        Transaction.user_id == user_id,
    )
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {tx_id} not found",
        )
    return tx
