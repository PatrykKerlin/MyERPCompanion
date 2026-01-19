from typing import Annotated

from pydantic import EmailStr, Field, HttpUrl


class Constraints:
    __digits_only_regex = r"^\d+$"
    __phone_number_regex = r"^\+?\d[\d\s]*$"
    __postal_code_regex = r"^\d{2}-\d{3}$"

    type Key = Annotated[str, Field(min_length=1, max_length=25, pattern=r"^[a-z_]+$")]
    type Name = Annotated[str, Field(min_length=1, max_length=50)]

    type Bytes = bytes
    type BooleanFalse = Annotated[bool, Field(default=False)]
    type BooleanTrue = Annotated[bool, Field(default=True)]
    type PositiveFloat = Annotated[float, Field(gt=0)]
    type PositiveInteger = Annotated[int, Field(ge=1)]
    type PositiveIntegerOptional = Annotated[int | None, Field(ge=1, default=None)]
    type PositiveIntegerList = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]
    type PositiveIntegerListOptional = Annotated[
        list[Annotated[int, Field(ge=1)]] | None, Field(min_length=1, default=None)
    ]

    type PositiveNumeric_6_3 = Annotated[float, Field(gt=0, lt=1000)]
    type NonNegativeNumeric_10_2 = Annotated[float, Field(ge=0, lt=100000000)]
    type PositiveNumeric_10_2 = Annotated[float, Field(gt=0, lt=100000000)]
    type PositiveNumericOptional_10_2 = Annotated[float | None, Field(gt=0, lt=100000000)]
    type PositiveNumeric_11_3 = Annotated[float, Field(gt=0, lt=100000000)]

    type String_10 = Annotated[str, Field(min_length=1, max_length=10)]
    type StringOptional_10 = Annotated[str | None, Field(min_length=1, max_length=10)]
    type String_20 = Annotated[str, Field(min_length=1, max_length=20)]
    type StringOptional_20 = Annotated[str | None, Field(min_length=1, max_length=20)]
    type String_50 = Annotated[str, Field(min_length=1, max_length=50)]
    type StringOptional_50 = Annotated[str | None, Field(min_length=1, max_length=50)]
    type StringList_50 = Annotated[list[Annotated[str, Field(min_length=1, max_length=50)]], Field(min_length=1)]
    type String_100 = Annotated[str, Field(min_length=1, max_length=100)]
    type StringOptional_100 = Annotated[str | None, Field(min_length=1, max_length=100)]
    type String_1000 = Annotated[str, Field(min_length=1, max_length=1000)]
    type StringOptional_1000 = Annotated[str | None, Field(min_length=1, max_length=1000)]

    type BankAccount = Annotated[str, Field(min_length=28, max_length=28, pattern=r"^[A-Z]{2}\d{26}$")]
    type BankSwift = Annotated[str, Field(min_length=8, max_length=11, pattern=r"^[A-Z0-9]+$")]
    type Ean = Annotated[str, Field(min_length=1, max_length=100, pattern=__digits_only_regex)]
    type Email = Annotated[EmailStr, Field(min_length=1, max_length=100)]
    type EmailOptional = Annotated[EmailStr | None, Field(min_length=1, max_length=100)]
    type IdDocumentOptional = Annotated[str | None, Field(min_length=9, max_length=9)]
    type Password = Annotated[str, Field(min_length=8, max_length=100)]
    type PasswordOptional = Annotated[str | None, Field(min_length=8, max_length=100)]
    type PaymentTerm = Annotated[int, Field(ge=0, le=90)]
    type PercentFloat = Annotated[float, Field(ge=0, le=1)]
    type PercentFloatOptional = Annotated[float | None, Field(ge=0, le=1)]
    type PeselOptional = Annotated[str | None, Field(min_length=11, max_length=11, pattern=__digits_only_regex)]
    type PhoneNumber = Annotated[str, Field(min_length=9, max_length=20, pattern=__phone_number_regex)]
    type PhoneNumberOptional = Annotated[str | None, Field(min_length=9, max_length=20, pattern=__phone_number_regex)]
    type PostalCode = Annotated[str, Field(min_length=6, max_length=6, pattern=__postal_code_regex)]
    type PostalCodeOptional = Annotated[str | None, Field(min_length=6, max_length=6, pattern=__postal_code_regex)]
    type Quantity = Annotated[int, Field(ge=0)]
    type Symbol = Annotated[str, Field(min_length=1, max_length=3)]
    type TaxId = Annotated[str, Field(min_length=10, max_length=10, pattern=__digits_only_regex)]
    type TaxIdOptional = Annotated[str | None, Field(min_length=10, max_length=10, pattern=__digits_only_regex)]
    type Username = Annotated[str, Field(min_length=5, max_length=20)]
    type WebsiteOptional = Annotated[HttpUrl | None, Field(max_length=50)]
