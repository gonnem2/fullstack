from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class CategoryExpenseDTO:
    title: str
    amount: int


@dataclass
class CategoryExpenseStatDTO:
    categories: List[CategoryExpenseDTO]
    total: int


@dataclass
class ExpenseDynamicDTO:
    date: datetime
    amount: float
