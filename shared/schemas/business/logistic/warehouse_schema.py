from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class WarehouseStrictSchema(BaseStrictSchema):
    name: Constraints.String100
    email: Constraints.Email
    phone_number: Constraints.PhoneNumber

    street: Constraints.String50Optional
    house_number: Constraints.String10
    apartment_number: Constraints.String10Optional
    postal_code: Constraints.PostalCode
    city: Constraints.String50
    country: Constraints.String50


class WarehousePlainSchema(BasePlainSchema):
    name: str
    email: str
    phone_number: str

    street: str
    house_number: str
    apartment_number: str
    postal_code: str
    city: str
    country: str
