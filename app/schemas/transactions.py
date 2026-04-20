from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ─── Transaction ────────────────────────────────────────────────────────────

class TransactionBase(BaseModel):
    type: Literal["income", "expense"]
    amount: float = Field(..., gt=0, description="Must be positive")
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[Literal["income", "expense"]] = None
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None


class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTransactions(BaseModel):
    items: List[TransactionOut]
    total: int
    page: int
    page_size: int
    pages: int


