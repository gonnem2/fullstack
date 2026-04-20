from app.core.exceptions.base_http import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from app.db.models.base import Base


class AttachedFile(Base):
    """Метаданные файлов, хранящихся в S3/MinIO."""

    __tablename__ = "attached_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False, unique=True)  # путь внутри бакета
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="files")  # ← добавлено
