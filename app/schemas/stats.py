from typing import List

from pydantic import BaseModel
from enum import Enum

from app.schemas.dataclasses.stats import CategoryExpenseStatDTO, CategoryExpenseDTO


class PeriodEnum(str, Enum):
    today = "today"
    week = "week"
    month = "month"
    year = "year"


class Period(BaseModel):
    period: PeriodEnum


class CategoriesStatOut(BaseModel):
    categories: List[CategoryExpenseDTO]
    total: int