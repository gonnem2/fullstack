from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    expense_date: datetime
    category_id: int
    cost: float
    comment: str | None = None

class ExpenseUpdate(BaseModel):
    expense_date: datetime | None = datetime.now()   # было datetime (обязательное)
    category_id: int | None = None         # было int
    cost: float | None = None              # было float
    comment: str | None = None


class ExpenseOut(BaseModel):
    id: int
    user_id: int
    expense_date: datetime
    category_id: int
    value: float
    comment: Optional[str]
    image_key: Optional[str] = None   # добавить эту строку


    model_config = ConfigDict(from_attributes=True)




class Expenses(BaseModel):
    expenses: list[ExpenseOut]
    skip: int
    limit: int

class ExpenseGet(BaseModel):
    data: Expenses
    total: float