from datetime import datetime

from pydantic import BaseModel


class IncomeCreate(BaseModel):
    income_date: datetime
    category_id: int
    value: float
    comment: str


class IncomeUpdate(BaseModel):
    pass


class IncomeOut(BaseModel):
    id: int
    user_id: int
    income_date: datetime
    category_id: int
    value: float
    comment: str