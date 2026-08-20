"""
Pydantic schemas for request validation and response serialization.
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _validate_six_digit(value: str, field_name: str) -> str:
    if not re.fullmatch(r"\d{6}", value):
        raise ValueError(f"{field_name} must be exactly 6 digits (e.g. '000042')")
    return value


class BookCreate(BaseModel):
    serial_number: str = Field(
        ...,
        description="Unique six-digit serial number assigned by the librarian",
        examples=["000001"],
    )
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Author full name")

    @field_validator("serial_number")
    @classmethod
    def serial_number_format(cls, v: str) -> str:
        return _validate_six_digit(v, "serial_number")


class BookResponse(BaseModel):
    serial_number: str
    title: str
    author: str
    is_borrowed: bool
    borrowed_at: Optional[datetime] = None
    borrowed_by: Optional[str] = None

    model_config = {"from_attributes": True}


class BorrowUpdate(BaseModel):
    """
    To borrow a book:  { "is_borrowed": true,  "borrower_card": "042000" }
    To return a book:  { "is_borrowed": false }
    """

    is_borrowed: bool = Field(..., description="True to borrow, False to return")
    borrower_card: Optional[str] = Field(
        default=None,
        description="Six-digit library card number – required when is_borrowed is True",
        examples=["042000"],
    )

    @field_validator("borrower_card")
    @classmethod
    def borrower_card_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return _validate_six_digit(v, "borrower_card")
        return v

    def model_post_init(self, __context) -> None: # noqa: ANN001
        if self.is_borrowed and not self.borrower_card:
            raise ValueError("borrower_card is required when is_borrowed is True")
        if not self.is_borrowed and self.borrower_card:
            raise ValueError("borrower_card must be omitted when returning a book")
