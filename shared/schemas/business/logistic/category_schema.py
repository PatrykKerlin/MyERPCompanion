from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class CategoryStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    code: Constraints.String10
    description: Constraints.String1000Optional


class CategoryPlainSchema(BasePlainSchema):
    name: str
    code: str
    description: str | None
