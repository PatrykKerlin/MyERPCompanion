from typing import Annotated

from pydantic import EmailStr, Field, HttpUrl


class Constraints:
    __digits_only_regex = r"^\d+$"
    __phone_number_regex = r"^\+?\d[\d\s]*$"
    __postal_code_regex = r"^\d{2}-\d{3}$"

    Key = Annotated[str, Field(min_length=1, max_length=25, pattern=r"^[a-z_]+$")]
    Name = Annotated[str, Field(min_length=1, max_length=50)]

    Bytes = bytes
    BooleanFalse = Annotated[bool, Field(default=False)]
    BooleanTrue = Annotated[bool, Field(default=True)]
    PositiveFloat = Annotated[int, Field(gt=0)]
    PositiveInteger = Annotated[int, Field(ge=1)]
    PositiveIntegerOptional = Annotated[int | None, Field(ge=1)]
    PositiveIntegerList = Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]
    PositiveIntegerListOptional = Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(min_length=1)]

    PositiveNumeric63 = Annotated[float, Field(gt=0, lt=1000)]
    PositiveNumeric102 = Annotated[float, Field(gt=0, lt=100000000)]
    PositiveNumeric102Optional = Annotated[float | None, Field(gt=0, lt=100000000)]
    PositiveNumeric103 = Annotated[float, Field(gt=0, lt=10000000)]

    String10 = Annotated[str, Field(min_length=1, max_length=10)]
    String10Optional = Annotated[str | None, Field(min_length=1, max_length=10)]
    String20 = Annotated[str, Field(min_length=1, max_length=20)]
    String20Optional = Annotated[str | None, Field(min_length=1, max_length=20)]
    String50 = Annotated[str, Field(min_length=1, max_length=50)]
    String50Optional = Annotated[str | None, Field(min_length=1, max_length=50)]
    String50List = Annotated[list[Annotated[str, Field(min_length=1, max_length=50)]], Field(min_length=1)]
    String100 = Annotated[str, Field(min_length=1, max_length=100)]
    String100Optional = Annotated[str | None, Field(min_length=1, max_length=100)]
    String1000 = Annotated[str, Field(min_length=1, max_length=1000)]
    String1000Optional = Annotated[str | None, Field(min_length=1, max_length=1000)]

    BankAccount = Annotated[str, Field(min_length=26, max_length=26, pattern=r"^[A-Z]{2}\d{26}$")]
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
    Username = Annotated[str, Field(min_length=5, max_length=20)]
    WebsiteOptional = Annotated[HttpUrl | None, Field(max_length=50)]
