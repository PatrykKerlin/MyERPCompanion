from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class DepartmentStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.String1000Optional
    code: Constraints.Symbol
    email: Constraints.Email
    phone_number: Constraints.PhoneNumber


class DepartmentPlainSchema(BasePlainSchema):
    name: str
    description: str | None
    code: str
    email: str
    phone_number: str
