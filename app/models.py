"""
ORM models – database table definitions.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    """Represents a single physical book copy owned by the library.

    Columns
    -------
    serial_number : str
        Six-digit identifier assigned by the librarian (e.g. "000123").
        Used as the primary key because it is guaranteed unique and is the
        natural reference employees use in day-to-day work.
    title : str
        Full title of the book.
    author : str
        Author's full name.
    is_borrowed : bool
        True when the book is currently on loan; False when available.
    borrowed_at : datetime | None
        UTC timestamp of when the book was checked out.
    borrowed_by : str | None
        Six-digit library card number of the borrower.
    """

    __tablename__ = "books"

    serial_number: Mapped[str] = mapped_column(String(6), primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)

    is_borrowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    borrowed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    borrowed_by: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
