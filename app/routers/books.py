from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import BookCreate, BookResponse, BorrowUpdate

router = APIRouter(prefix="/books", tags=["books"])

SerialNumberPath = Annotated[
    str,
    Path(pattern=r"^\d{6}$", description="Six-digit serial number, e.g. '000042'"),
]


@router.get(
    "/",
    response_model=List[BookResponse],
    summary="List all books",
    description="Returns every book in the library catalogue, ordered by serial number.",
)
def list_books(db: Session = Depends(get_db)):
    return crud.get_all_books(db)


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new book",
    description="Register a new book in the library. The serial number must be unique.",
)
def add_book(payload: BookCreate, db: Session = Depends(get_db)):
    existing = crud.get_book_by_serial(db, payload.serial_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with serial number '{payload.serial_number}' already exists.",
        )
    return crud.create_book(db, payload)


@router.delete(
    "/{serial_number}",
    response_model=BookResponse,
    summary="Delete a book",
    description="Permanently remove a book from the catalogue by its serial number.",
)
def remove_book(serial_number: SerialNumberPath, db: Session = Depends(get_db)):
    deleted = crud.delete_book(db, serial_number)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with serial number '{serial_number}' not found.",
        )
    return deleted


@router.patch(
    "/{serial_number}/status",
    response_model=BookResponse,
    summary="Update borrow status",
    description=(
        "Borrow or return a book. "
        "When borrowing, provide the six-digit `borrower_card`. "
        "When returning, set `is_borrowed` to false and omit `borrower_card`."
    ),
)
def update_status(
    serial_number: SerialNumberPath,
    payload: BorrowUpdate,
    db: Session = Depends(get_db),
):
    updated = crud.update_book_status(db, serial_number, payload)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with serial number '{serial_number}' not found.",
        )
    return updated
