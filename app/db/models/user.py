from typing import List

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    day_expense_limit: Mapped[float] = mapped_column(
        Numeric(10, 2), default=500, nullable=True
    )

    incomes: Mapped[List["Income"]] = relationship(
        "Income", back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="user", uselist=True, cascade="all, delete-orphan"
    )
