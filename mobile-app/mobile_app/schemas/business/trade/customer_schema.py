from __future__ import annotations

from pydantic import model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class CustomerStrictSchema(BaseStrictSchema):
    first_name: Constraints.StringOptional_50
    last_name: Constraints.StringOptional_50

    company_name: Constraints.Name

    payment_term: Constraints.PaymentTerm
    tax_id: Constraints.TaxId

    email: Constraints.Email
    phone_number: Constraints.PhoneNumber

    street: str | None
    house_number: Constraints.String_10
    apartment_number: str | None
    postal_code: Constraints.PostalCode
    city: Constraints.String_50
    country: Constraints.String_50

    shipping_street: str | None
    shipping_house_number: str | None
    shipping_apartment_number: str | None
    shipping_postal_code: Constraints.PostalCodeOptional
    shipping_city: str | None
    shipping_country: str | None

    @model_validator(mode="after")
    def __validate_data(self) -> CustomerStrictSchema:
        shipping_required_values = [
            self.shipping_house_number,
            self.shipping_postal_code,
            self.shipping_city,
            self.shipping_country,
        ]

        shipping_all_values = [
            self.shipping_street,
            self.shipping_house_number,
            self.shipping_apartment_number,
            self.shipping_postal_code,
            self.shipping_city,
            self.shipping_country,
        ]

        if all(value is None for value in shipping_all_values):
            return self

        is_shipping_required_complete = all(value not in {None, ""} for value in shipping_required_values)

        if not is_shipping_required_complete:
            raise ValueError("Shipping address must be either completely empty or fully provided.")

        return self


class CustomerPlainSchema(BasePlainSchema):
    first_name: str | None
    last_name: str | None

    company_name: str

    payment_term: int
    tax_id: str

    email: str
    phone_number: str

    street: str | None
    house_number: str
    apartment_number: str | None
    postal_code: str
    city: str
    country: str

    shipping_street: str | None
    shipping_house_number: str | None
    shipping_apartment_number: str | None
    shipping_postal_code: str | None
    shipping_city: str | None
    shipping_country: str | None

    user_id: int | None

    discount_ids: list[int]
