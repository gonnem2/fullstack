from datetime import datetime
from multiprocessing.managers import ListProxy

from pydantic import BaseModel, Field


class IncomeCreate(BaseModel):
    income_date: datetime
    category_id: int
    value: float
    comment: str


class IncomeUpdate(BaseModel):
    income_date: datetime
    category_id: int
    value: float = Field(..., ge=0, lt=1000000000)
    comment: str
    comment: str


class Income(BaseModel):
    id: int
    user_id: int
    income_date: datetime
    category_id: int
    value: float = Field(..., ge=0, lt=1000000000)
    comment: str


class IncomeGetPag(BaseModel):
    incomes: list[Income]
    skip: int
    limit: int

class IncomeOut(BaseModel):
    data: IncomeGetPag
    total: float
