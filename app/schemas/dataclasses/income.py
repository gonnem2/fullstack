from dataclasses import dataclass
from datetime import datetime


@dataclass
class IncomeDTO:
    id: int
    user_id: int
    income_date: datetime
    category_id: int
    value: float
    comment: str
