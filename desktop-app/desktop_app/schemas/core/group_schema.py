from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class GroupStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.StringOptional_1000


class GroupPlainSchema(BasePlainSchema):
    key: str
    description: str | None
