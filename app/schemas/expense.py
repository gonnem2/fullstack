from datetime import datetime

from pydantic import BaseModel


class SpendingCreate(BaseModel):
    created_at: datetime
    category_id: int
    cost: float
    comment: str

class SpendingUpdate(BaseModel):
    created_at: datetime
    category_id: int
    cost: float
    comment: str


class SpendingOut(BaseModel):
    ...