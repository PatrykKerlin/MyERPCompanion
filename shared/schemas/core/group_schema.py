from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class GroupStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional


class GroupPlainSchema(BasePlainSchema):
    key: str
    description: str | None
