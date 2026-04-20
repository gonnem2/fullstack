from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IncomeCreate(BaseModel):
    income_date: datetime
    category_id: int
    value: float
    comment: str | None = None


class IncomeUpdate(BaseModel):
    income_date: datetime
    category_id: int
    value: float = Field(..., ge=0, lt=1000000000)
    comment: str | None = None


class Income(BaseModel):
    id: int
    user_id: int
    income_date: datetime
    category_id: int
    image_key: str
    value: float = Field(..., ge=0, lt=1000000000)
    comment: Optional[str]
    image_key: Optional[str] = None   # добавить эту строку



class IncomeGetPag(BaseModel):
    incomes: list[Income]
    skip: int
    limit: int

class IncomeOut(BaseModel):
    data: IncomeGetPag
    total: float
