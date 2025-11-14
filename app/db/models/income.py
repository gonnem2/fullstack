from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from app.db.models.base import Base


class Income(Base):
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    income_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    comment: Mapped[str] = mapped_column(String(100), nullable=True)

    category: Mapped["Category"] = relationship("Category", back_populates="incomes")
    user: Mapped["User"] = relationship("User", back_populates="incomes")
