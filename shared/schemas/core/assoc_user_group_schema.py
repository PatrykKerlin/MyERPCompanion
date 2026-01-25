from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocUserGroupStrictSchema(BaseStrictSchema):
    user_id: Constraints.PositiveInteger
    group_id: Constraints.PositiveInteger


class AssocUserGroupPlainSchema(BasePlainSchema):
    user_id: int
    group_id: int
