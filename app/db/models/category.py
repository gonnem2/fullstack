from enum import Enum
from typing import List

from sqlalchemy import String, Enum as sqlalchemy_enum
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from app.db.models.base import Base


class TypesOfCat(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    type_of_category: Mapped[TypesOfCat] = mapped_column(
        sqlalchemy_enum(TypesOfCat), nullable=False, index=True
    )

    incomes: Mapped[List["Income"]] = relationship(
        "Income", back_populates="category", uselist=True, cascade="all, delete-orphan"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="category", uselist=True, cascade="all, delete-orphan"
    )

    @property
    def is_income(self):
        return self.type_of_category == TypesOfCat.INCOME

    @property
    def is_expense(self):
        return self.type_of_category == TypesOfCat.EXPENSE
