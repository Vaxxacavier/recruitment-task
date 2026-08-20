"""
CRUD operations – the only layer that talks directly to the database.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BorrowUpdate


def get_all_books(db: Session) -> List[Book]:
    return db.query(Book).order_by(Book.serial_number).all()


def get_book_by_serial(db: Session, serial_number: str) -> Optional[Book]:
    return db.query(Book).filter(Book.serial_number == serial_number).first()


def create_book(db: Session, payload: BookCreate) -> Book:
    book = Book(
        serial_number=payload.serial_number,
        title=payload.title,
        author=payload.author,
        is_borrowed=False,
        borrowed_at=None,
        borrowed_by=None,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, serial_number: str) -> Optional[Book]:
    book = get_book_by_serial(db, serial_number)
    if book is None:
        return None
    db.delete(book)
    db.commit()
    return book


def update_book_status(db: Session, serial_number: str, payload: BorrowUpdate) -> Optional[Book]:
    book = get_book_by_serial(db, serial_number)
    if book is None:
        return None

    book.is_borrowed = payload.is_borrowed

    if payload.is_borrowed:
        book.borrowed_at = datetime.now(timezone.utc)
        book.borrowed_by = payload.borrower_card
    else:
        book.borrowed_at = None
        book.borrowed_by = None

    db.commit()
    db.refresh(book)
    return book
