from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class CategoryStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    code: Constraints.String_10
    description: Constraints.StringOptional_1000


class CategoryPlainSchema(BasePlainSchema):
    name: str
    code: str
    description: str | None
