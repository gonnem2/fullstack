from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExpenseDTO:
    id: int
    user_id: int
    expense_date: datetime
    category_id: int
    value: float
    comment: str
