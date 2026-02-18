from typing import Annotated, Literal

from pydantic import BeforeValidator, EmailStr, Field, HttpUrl, PlainSerializer


class Constraints:
    __digits_only_regex = r"^\d+$"
    __phone_number_regex = r"^\+?\d[\d\s]*$"
    __postal_code_regex = r"^\d{2}-\d{3}$"
    __none_to_zero = lambda value: 0.0 if value is None else value  # noqa: E731

    Key = Annotated[str, Field(min_length=1, max_length=25, pattern=r"^[a-z_]+$")] # NOSONAR
    Name = Annotated[str, Field(min_length=1, max_length=50)] # NOSONAR

    Bytes = bytes # NOSONAR
    BooleanFalse = Annotated[bool, Field(default=False)] # NOSONAR
    BooleanTrue = Annotated[bool, Field(default=True)] # NOSONAR
    PositiveFloat = Annotated[float, Field(gt=0)] # NOSONAR
    NonNegativeInteger = Annotated[int, BeforeValidator(__none_to_zero), Field(ge=0, default=0)] # NOSONAR
    PositiveInteger = Annotated[int, Field(ge=1)] # NOSONAR
    PositiveIntegerOptional = Annotated[int | None, Field(ge=1, default=None)] # NOSONAR
    PositiveIntegerList = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)] # NOSONAR
    PositiveIntegerListOptional = Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(min_length=1, default=None)] # NOSONAR

    PositiveNumeric_6_3 = Annotated[float, Field(gt=0, lt=1000)] # NOSONAR
    NonNegativeNumeric_10_2 = Annotated[float, BeforeValidator(__none_to_zero), Field(ge=0, lt=100000000, default=0)] # NOSONAR
    PositiveNumeric_10_2 = Annotated[float, Field(gt=0, lt=100000000)] # NOSONAR
    PositiveNumericOptional_10_2 = Annotated[float | None, Field(gt=0, lt=100000000)] # NOSONAR
    PositiveNumeric_11_3 = Annotated[float, Field(gt=0, lt=100000000)] # NOSONAR

    String_10 = Annotated[str, Field(min_length=1, max_length=10)] # NOSONAR
    StringOptional_10 = Annotated[str | None, Field(min_length=1, max_length=10)] # NOSONAR
    String_20 = Annotated[str, Field(min_length=1, max_length=20)] # NOSONAR
    StringOptional_20 = Annotated[str | None, Field(min_length=1, max_length=20)] # NOSONAR
    String_50 = Annotated[str, Field(min_length=1, max_length=50)] # NOSONAR
    StringOptional_50 = Annotated[str | None, Field(min_length=1, max_length=50)] # NOSONAR
    StringList_50 = Annotated[list[Annotated[str, Field(min_length=1, max_length=50)]], Field(min_length=1)] # NOSONAR
    String_100 = Annotated[str, Field(min_length=1, max_length=100)] # NOSONAR
    StringOptional_100 = Annotated[str | None, Field(min_length=1, max_length=100)] # NOSONAR
    String_1000 = Annotated[str, Field(min_length=1, max_length=1000)] # NOSONAR
    StringOptional_1000 = Annotated[str | None, Field(min_length=1, max_length=1000)] # NOSONAR

    BankAccount = Annotated[str, Field(min_length=28, max_length=28, pattern=r"^[A-Z]{2}\d{26}$")] # NOSONAR
    BankSwift = Annotated[str, Field(min_length=8, max_length=11, pattern=r"^[A-Z0-9]+$")] # NOSONAR
    Ean = Annotated[str, Field(min_length=1, max_length=100, pattern=__digits_only_regex)] # NOSONAR
    Email = Annotated[EmailStr, Field(min_length=1, max_length=100)] # NOSONAR
    EmailOptional = Annotated[EmailStr | None, Field(min_length=1, max_length=100)] # NOSONAR
    IdDocumentOptional = Annotated[str | None, Field(min_length=9, max_length=9)] # NOSONAR
    Password = Annotated[str, Field(min_length=8, max_length=100)] # NOSONAR
    PasswordOptional = Annotated[str | None, Field(min_length=8, max_length=100)] # NOSONAR
    PaymentTerm = Annotated[int, Field(ge=0, le=90)] # NOSONAR
    PercentFloat = Annotated[float, Field(ge=0, le=1)] # NOSONAR
    PercentFloatOptional = Annotated[float | None, Field(ge=0, le=1)] # NOSONAR
    PeselOptional = Annotated[str | None, Field(min_length=11, max_length=11, pattern=__digits_only_regex)] # NOSONAR
    PhoneNumber = Annotated[str, Field(min_length=9, max_length=20, pattern=__phone_number_regex)] # NOSONAR
    PhoneNumberOptional = Annotated[str | None, Field(min_length=9, max_length=20, pattern=__phone_number_regex)] # NOSONAR
    PostalCode = Annotated[str, Field(min_length=6, max_length=6, pattern=__postal_code_regex)] # NOSONAR
    PostalCodeOptional = Annotated[str | None, Field(min_length=6, max_length=6, pattern=__postal_code_regex)] # NOSONAR
    Quantity = Annotated[int, Field(ge=0)] # NOSONAR
    Symbol = Annotated[str, Field(min_length=1, max_length=3)] # NOSONAR
    TaxId = Annotated[str, Field(min_length=10, max_length=10, pattern=__digits_only_regex)] # NOSONAR
    TaxIdOptional = Annotated[str | None, Field(min_length=10, max_length=10, pattern=__digits_only_regex)] # NOSONAR
    Theme = Literal["system", "dark", "light"] # NOSONAR
    AuthClient = Literal["desktop", "web"] # NOSONAR
    Username = Annotated[str, Field(min_length=5, max_length=20)] # NOSONAR
    WebsiteOptional = Annotated[ # NOSONAR
        HttpUrl | None,
        PlainSerializer(
            lambda value: str(value) if value is not None else None, return_type=str | None, when_used="always"
        ),
        Field(max_length=50),
    ]
