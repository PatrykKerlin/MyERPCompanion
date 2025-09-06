from schemas.base import BaseStrictSchema
from schemas.validation import Constraints


class AssocModuleGroupStrictSchema(BaseStrictSchema):
    group_id: Constraints.PositiveInteger
    module_id: Constraints.PositiveInteger


class AssocUserGroupStrictSchema(BaseStrictSchema):
    user_id: Constraints.PositiveInteger
    group_id: Constraints.PositiveInteger
