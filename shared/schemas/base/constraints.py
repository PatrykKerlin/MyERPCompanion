from __future__ import annotations

from typing import Annotated

from pydantic import EmailStr, Field, HttpUrl


class Constraints:
    type Key = Annotated[str, Field(min_length=1, max_length=25)]

    type BooleanFalse = Annotated[bool, Field(default=False)]
    type BooleanTrue = Annotated[bool, Field(default=True)]
    type PositiveFloat = Annotated[int, Field(gt=0)]
    type PositiveInteger = Annotated[int, Field(ge=1)]
    type PositiveIntegerOptional = Annotated[int | None, Field(ge=1)]
    type PositiveIntegerList = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]

    type String10 = Annotated[str, Field(min_length=1, max_length=10)]
    type String10Optional = Annotated[str | None, Field(min_length=1, max_length=10)]
    type String20 = Annotated[str, Field(min_length=1, max_length=20)]
    type String20Optional = Annotated[str | None, Field(min_length=1, max_length=20)]
    type String50 = Annotated[str, Field(min_length=1, max_length=50)]
    type String50Optional = Annotated[str | None, Field(min_length=1, max_length=50)]
    type String100 = Annotated[str, Field(min_length=1, max_length=100)]
    type String100Optional = Annotated[str | None, Field(min_length=1, max_length=100)]
    type String1000 = Annotated[str, Field(min_length=1, max_length=1000)]
    type String1000Optional = Annotated[str | None, Field(min_length=1, max_length=1000)]

    type BankAccount = Annotated[str, Field(min_length=26, max_length=26, pattern=r"^\d+$")]
    type BankSwift = Annotated[str, Field(min_length=8, max_length=11, pattern=r"^[A-Z0-9]+$")]
    type Email = Annotated[EmailStr, Field(min_length=1, max_length=100)]
    type EmailOptional = Annotated[EmailStr | None, Field(min_length=1, max_length=100)]
    type IdDocumentOptional = Annotated[str | None, Field(min_length=9, max_length=9)]
    type Password = Annotated[str, Field(min_length=8, max_length=100)]
    type PasswordOptional = Annotated[str | None, Field(min_length=8, max_length=100)]
    type PaymentTerm = Annotated[int, Field(ge=0, le=90)]
    type PeselOptional = Annotated[str | None, Field(min_length=11, max_length=11, pattern=r"^\d+$")]
    type PhoneNumber = Annotated[str, Field(min_length=9, max_length=20, pattern=r"^[0-9\s+]+$")]
    type PhoneNumberOptional = Annotated[str | None, Field(min_length=9, max_length=20, pattern=r"^[0-9\s+]+$")]
    type PostalCode = Annotated[str, Field(min_length=6, max_length=6, pattern=r"^\d{2}-\d{3}$")]
    type PostalCodeOptional = Annotated[str | None, Field(min_length=6, max_length=6, pattern=r"^\d{2}-\d{3}$")]
    type Symbol = Annotated[str, Field(min_length=1, max_length=3)]
    type TaxId = Annotated[str, Field(min_length=10, max_length=10, pattern=r"^\d+$")]
    type Username = Annotated[str, Field(min_length=5, max_length=20)]
    type WebsiteOptional = Annotated[HttpUrl | None, Field(max_length=50)]
