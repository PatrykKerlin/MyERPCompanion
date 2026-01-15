from __future__ import annotations

from pydantic import model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema
from schemas.validation.constraints import Constraints


class CustomerStrictSchema(BaseStrictSchema):
    first_name: Constraints.String50
    middle_name: str | None
    last_name: Constraints.String50

    is_company: Constraints.BooleanFalse
    company_name: Constraints.String50Optional

    payment_term: Constraints.PaymentTerm

    email: Constraints.Email
    phone_number: Constraints.PhoneNumber

    use_one_address: Constraints.BooleanTrue

    shipping_street: str | None
    shipping_house_number: Constraints.String10
    shipping_apartment_number: str | None
    shipping_postal_code: Constraints.PostalCode
    shipping_city: Constraints.String50
    shipping_country: Constraints.String50

    billing_street: str | None
    billing_house_number: str | None
    billing_apartment_number: str | None
    billing_postal_code: Constraints.PostalCodeOptional
    billing_city: str | None
    billing_country: str | None

    user_id: int

    @model_validator(mode="after")
    def _validate_data(self) -> CustomerStrictSchema:
        if self.is_company and not self.company_name:
            raise ValueError("company_name is required when is_company is true")

        if not self.is_company and self.company_name:
            raise ValueError("company_name must be empty when is_company is false")

        billing_address = [self.billing_house_number, self.billing_postal_code, self.billing_city, self.billing_country]
        if self.use_one_address and any(billing_address):
            raise ValueError("when use_one_address is true, billing address must be empty")

        if not self.use_one_address and not all(billing_address):
            raise ValueError("when use_one_address is false, billing address must be fully provided")

        return self


class CustomerPlainSchema(BasePlainSchema):
    first_name: str
    middle_name: str | None
    last_name: str

    is_company: bool
    company_name: str | None

    payment_term: int

    email: str
    phone_number: str

    use_one_address: bool

    shipping_street: str | None
    shipping_house_number: str
    shipping_apartment_number: str | None
    shipping_postal_code: str
    shipping_city: str
    shipping_country: str

    billing_street: str | None
    billing_house_number: str | None
    billing_apartment_number: str | None
    billing_postal_code: str | None
    billing_city: str | None
    billing_country: str | None

    user_id: int

    discounts: list[DiscountPlainSchema]
