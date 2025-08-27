from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class CategoryStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional


class CategoryPlainSchema(BasePlainSchema):
    key: str
    description: str | None
