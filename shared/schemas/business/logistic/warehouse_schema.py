from datetime import datetime
from typing import Annotated

from pydantic import Field
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


class WarehouseLoginOptionSchema(BasePlainSchema):
    name: str

    is_active: Annotated[bool, Field(exclude=True)]
    created_at: Annotated[datetime, Field(exclude=True)]
    created_by: Annotated[int, Field(exclude=True)]
    modified_at: Annotated[datetime | None, Field(exclude=True)] = None
    modified_by: Annotated[int | None, Field(exclude=True)] = None
    created_by_username: Annotated[str | None, Field(exclude=True)] = None
    modified_by_username: Annotated[str | None, Field(exclude=True)] = None
