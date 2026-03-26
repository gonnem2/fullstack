from enum import Enum
from typing import List

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRoles] = mapped_column(
        server_default=UserRoles.USER.name, default=UserRoles.USER
    )  # дефолтное значение
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
    categories: Mapped[List["Category"]] = relationship(
        "Category", back_populates="user", uselist=True, cascade="all, delete-orphan"
    )

    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete"
    )
