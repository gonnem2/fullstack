"""add attached_files table

Revision ID: 0002_attached_files
Revises: <id предыдущей миграции — заменить>
Create Date: 2025-01-01 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Заменить на реальный revision предыдущей миграции
revision: str = "0002_attached_files"
down_revision: Union[str, None] = "b70032e85960"  # ← поменяйте на свой
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём transactions
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "category",
            sa.Enum("INCOME", "EXPENSE", name="transactiontype"),
            nullable=False,
        ),
        sa.Column(
            "category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False
        ),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("comment", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])

    # 2. Затем attached_files
    op.create_table(
        "attached_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "transaction_id",
            sa.Integer(),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False, unique=True),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index(
        "ix_attached_files_transaction_id", "attached_files", ["transaction_id"]
    )
    op.create_index("ix_attached_files_user_id", "attached_files", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_attached_files_user_id", table_name="attached_files")
    op.drop_index("ix_attached_files_transaction_id", table_name="attached_files")
    op.drop_table("attached_files")
