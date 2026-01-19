from typing import Any

from pydantic import Field, field_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints
from schemas.validation.normalizers import Normalizers


class CarrierStrictSchema(BaseStrictSchema):
    name: Constraints.Name

    company_email: Constraints.EmailOptional
    company_phone: Constraints.PhoneNumberOptional
    company_website: Constraints.WebsiteOptional

    street: Constraints.StringOptional_50
    house_number: Constraints.String_10
    apartment_number: Constraints.StringOptional_10
    postal_code: Constraints.PostalCode
    city: Constraints.String_50
    country: Constraints.String_50

    contact_person: Constraints.String_100
    contact_phone: Constraints.PhoneNumber
    contact_email: Constraints.Email

    bank_account: Constraints.BankAccount
    bank_swift: Constraints.BankSwift
    bank_name: Constraints.String_50
    tax_id: Constraints.TaxId
    payment_term: Constraints.PaymentTerm

    notes: Constraints.StringOptional_1000

    currency_id: Constraints.PositiveInteger


class CarrierPlainSchema(BasePlainSchema):
    name: str

    company_email: str | None
    company_phone: str | None
    company_website: str | None

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
    bank_swift: str
    bank_name: str
    tax_id: str
    payment_term: int

    notes: str

    currency_id: int

    delivery_method_ids: list[int] = Field(alias="delivery_methods")

    @field_validator("delivery_method_ids", mode="before")
    @classmethod
    def _normalize_delivery_methods(cls, values: list[Any]) -> list[int]:
        return Normalizers.normalize_related_ids(values)
