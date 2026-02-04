from typing import Annotated, Literal

from pydantic import BeforeValidator, EmailStr, Field, HttpUrl, PlainSerializer


class Constraints:
    __digits_only_regex = r"^\d+$"
    __phone_number_regex = r"^\+?\d[\d\s]*$"
    __postal_code_regex = r"^\d{2}-\d{3}$"
    __none_to_zero = lambda value: 0.0 if value is None else value

    Key = Annotated[str, Field(min_length=1, max_length=25, pattern=r"^[a-z_]+$")]
    Name = Annotated[str, Field(min_length=1, max_length=50)]

    Bytes = bytes
    BooleanFalse = Annotated[bool, Field(default=False)]
    BooleanTrue = Annotated[bool, Field(default=True)]
    PositiveFloat = Annotated[float, Field(gt=0)]
    NonNegativeInteger = Annotated[int, BeforeValidator(__none_to_zero), Field(ge=0, default=0)]
    PositiveInteger = Annotated[int, Field(ge=1)]
    PositiveIntegerOptional = Annotated[int | None, Field(ge=1, default=None)]
    PositiveIntegerList = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]
    PositiveIntegerListOptional = Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(min_length=1, default=None)]

    PositiveNumeric_6_3 = Annotated[float, Field(gt=0, lt=1000)]
    NonNegativeNumeric_10_2 = Annotated[float, BeforeValidator(__none_to_zero), Field(ge=0, lt=100000000, default=0)]
    PositiveNumeric_10_2 = Annotated[float, Field(gt=0, lt=100000000)]
    PositiveNumericOptional_10_2 = Annotated[float | None, Field(gt=0, lt=100000000)]
    PositiveNumeric_11_3 = Annotated[float, Field(gt=0, lt=100000000)]

    String_10 = Annotated[str, Field(min_length=1, max_length=10)]
    StringOptional_10 = Annotated[str | None, Field(min_length=1, max_length=10)]
    String_20 = Annotated[str, Field(min_length=1, max_length=20)]
    StringOptional_20 = Annotated[str | None, Field(min_length=1, max_length=20)]
    String_50 = Annotated[str, Field(min_length=1, max_length=50)]
    StringOptional_50 = Annotated[str | None, Field(min_length=1, max_length=50)]
    StringList_50 = Annotated[list[Annotated[str, Field(min_length=1, max_length=50)]], Field(min_length=1)]
    String_100 = Annotated[str, Field(min_length=1, max_length=100)]
    StringOptional_100 = Annotated[str | None, Field(min_length=1, max_length=100)]
    String_1000 = Annotated[str, Field(min_length=1, max_length=1000)]
    StringOptional_1000 = Annotated[str | None, Field(min_length=1, max_length=1000)]

    BankAccount = Annotated[str, Field(min_length=28, max_length=28, pattern=r"^[A-Z]{2}\d{26}$")]
    BankSwift = Annotated[str, Field(min_length=8, max_length=11, pattern=r"^[A-Z0-9]+$")]
    Ean = Annotated[str, Field(min_length=1, max_length=100, pattern=__digits_only_regex)]
    Email = Annotated[EmailStr, Field(min_length=1, max_length=100)]
    EmailOptional = Annotated[EmailStr | None, Field(min_length=1, max_length=100)]
    IdDocumentOptional = Annotated[str | None, Field(min_length=9, max_length=9)]
    Password = Annotated[str, Field(min_length=8, max_length=100)]
    PasswordOptional = Annotated[str | None, Field(min_length=8, max_length=100)]
    PaymentTerm = Annotated[int, Field(ge=0, le=90)]
    PercentFloat = Annotated[float, Field(ge=0, le=1)]
    PercentFloatOptional = Annotated[float | None, Field(ge=0, le=1)]
    PeselOptional = Annotated[str | None, Field(min_length=11, max_length=11, pattern=__digits_only_regex)]
    PhoneNumber = Annotated[str, Field(min_length=9, max_length=20, pattern=__phone_number_regex)]
    PhoneNumberOptional = Annotated[str | None, Field(min_length=9, max_length=20, pattern=__phone_number_regex)]
    PostalCode = Annotated[str, Field(min_length=6, max_length=6, pattern=__postal_code_regex)]
    PostalCodeOptional = Annotated[str | None, Field(min_length=6, max_length=6, pattern=__postal_code_regex)]
    Quantity = Annotated[int, Field(ge=0)]
    Symbol = Annotated[str, Field(min_length=1, max_length=3)]
    TaxId = Annotated[str, Field(min_length=10, max_length=10, pattern=__digits_only_regex)]
    TaxIdOptional = Annotated[str | None, Field(min_length=10, max_length=10, pattern=__digits_only_regex)]
    Theme = Literal["system", "dark", "light"]
    Username = Annotated[str, Field(min_length=5, max_length=20)]
    WebsiteOptional = Annotated[
        HttpUrl | None,
        PlainSerializer(lambda value: str(value) if value is not None else None, return_type=str | None, when_used="always"),
        Field(max_length=50),
    ]
