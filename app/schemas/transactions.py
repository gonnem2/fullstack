from datetime import date, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


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


# ─── Files ──────────────────────────────────────────────────────────────────

class AttachedFileOut(BaseModel):
    id: int
    transaction_id: int
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ─── Auth ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, digits, _ and -")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"