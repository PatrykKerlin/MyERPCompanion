from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class CategoryStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.String1000Optional


class CategoryPlainSchema(BasePlainSchema):
    name: str
    description: str | None
