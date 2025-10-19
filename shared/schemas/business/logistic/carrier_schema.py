from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints

from schemas.business.logistic.delivery_method_schema import DeliveryMethodPlainSchema


class CarrierStrictSchema(BaseStrictSchema):
    name: Constraints.Name

    company_email: Constraints.EmailOptional
    company_phone: Constraints.PhoneNumberOptional
    company_website: Constraints.WebsiteOptional

    street: Constraints.String50Optional
    house_number: Constraints.String10
    apartment_number: Constraints.String10Optional
    postal_code: Constraints.PostalCode
    city: Constraints.String50
    country: Constraints.String50

    contact_person: Constraints.String100
    contact_phone: Constraints.PhoneNumber
    contact_email: Constraints.Email

    bank_account: Constraints.BankAccount
    bank_swift: Constraints.BankSwift
    bank_name: Constraints.String50
    tax_id: Constraints.TaxId
    payment_term: Constraints.PaymentTerm

    notes: Constraints.String1000Optional

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

    delivery_methods: list[DeliveryMethodPlainSchema]
