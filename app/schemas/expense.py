from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    expense_date: datetime
    category_id: int
    cost: float
    comment: str

class ExpenseUpdate(BaseModel):
    expense_date: datetime
    category_id: int
    cost: float
    comment: str


class ExpenseOut(BaseModel):
    id: int
    user_id: int
    expense_date: datetime
    category_id: int
    value: float
    comment: Optional[str]

    model_config = ConfigDict(from_attributes=True)




class Expenses(BaseModel):
    expenses: list[ExpenseOut]
    skip: int
    limit: int

class ExpenseGet(BaseModel):
    data: Expenses
    total: float