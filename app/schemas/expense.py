from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    expense_date: datetime
    category_id: int
    cost: float
    comment: str

class ExpenseUpdate(BaseModel):
    created_at: datetime
    category_id: int
    cost: float
    comment: str


class ExpenseOut(BaseModel):
    id: int
    user_id: int
    expense_date: datetime
    category_id: int
    value: float
    comment: str

    model_config = ConfigDict(from_attributes=True)
