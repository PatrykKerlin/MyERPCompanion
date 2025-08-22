from __future__ import annotations

from typing import Annotated

from pydantic import Field, EmailStr, HttpUrl

from schemas.base import BaseStrictSchema, BasePlainSchema


class SupplierStrictSchema(BaseStrictSchema):
    name: Annotated[str, Field(min_length=1, max_length=50)]

    email: Annotated[EmailStr | None, Field(max_length=100)]
    phone_number: Annotated[str | None, Field(pattern=r"^[0-9+\-\s]+$", min_length=9, max_length=25)]
    website: Annotated[HttpUrl | None, Field(max_length=50)]

    street: Annotated[str | None, Field(max_length=50)]
    house_number: Annotated[str, Field(min_length=1, max_length=10)]
    apartment_number: Annotated[str | None, Field(max_length=10)]
    postal_code: Annotated[str, Field(pattern=r"^\d{2}-\d{3}$", min_length=6, max_length=6)]
    city: Annotated[str, Field(min_length=1, max_length=50)]
    country: Annotated[str, Field(min_length=1, max_length=50)]

    contact_person: Annotated[str, Field(min_length=1, max_length=100)]
    contact_phone: Annotated[str, Field(pattern=r"^[0-9+\-\s]+$", min_length=9, max_length=25)]
    contact_email: Annotated[EmailStr, Field(max_length=50)]

    bank_account: Annotated[str, Field(pattern=r"^\d+$", min_length=26, max_length=26)]
    bank_name: Annotated[str, Field(min_length=1, max_length=50)]
    tax_id: Annotated[str, Field(pattern=r"^\d+$", min_length=10, max_length=10)]
    payment_term: Annotated[int, Field(ge=0, le=90)]


class SupplierPlainSchema(BasePlainSchema):
    name: str

    email: str | None
    phone_number: str | None
    website: str | None

    street: str | None
    house_number: str
    apartment_number: str | None
    postal_code: str
    city: str
    country: str

    contact_person: str
    contact_phone: str
    contact_email: str

    bank_account: str
    bank_name: str
    tax_id: str
    payment_term: int

    items: list[int] = Field(default_factory=list)
    orders: list[int] = Field(default_factory=list)
