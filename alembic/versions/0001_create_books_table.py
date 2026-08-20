"""Create books table.

Revision ID: 0001
Revises:
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("serial_number", sa.String(6), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("is_borrowed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("borrowed_by", sa.String(6), nullable=True),
    )
    op.create_index("ix_books_serial_number", "books", ["serial_number"])


def downgrade() -> None:
    op.drop_index("ix_books_serial_number", table_name="books")
    op.drop_table("books")
