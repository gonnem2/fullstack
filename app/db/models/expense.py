from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    expense_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    comment: Mapped[str] = mapped_column(String(100), nullable=True)

    category: Mapped["Category"] = relationship("Category", back_populates="expenses")
    user: Mapped["User"] = relationship("User", back_populates="expenses")
