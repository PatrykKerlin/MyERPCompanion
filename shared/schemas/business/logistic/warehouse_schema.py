from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class WarehouseStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    email: Constraints.Email
    phone_number: Constraints.PhoneNumber

    street: Constraints.StringOptional_50
    house_number: Constraints.String_10
    apartment_number: Constraints.StringOptional_10
    postal_code: Constraints.PostalCode
    city: Constraints.String_50
    country: Constraints.String_50


class WarehousePlainSchema(BasePlainSchema):
    name: str
    email: str
    phone_number: str

    street: str | None
    house_number: str
    apartment_number: str | None
    postal_code: str
    city: str
    country: str
