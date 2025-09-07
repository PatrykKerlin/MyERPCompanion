from schemas.base import BaseStrictSchema
from schemas.validation import Constraints


class AssocModuleGroupStrictSchema(BaseStrictSchema):
    group_id: Constraints.PositiveInteger
    module_id: Constraints.PositiveInteger


class AssocUserGroupStrictSchema(BaseStrictSchema):
    user_id: Constraints.PositiveInteger
    group_id: Constraints.PositiveInteger


class AssocUserViewStrictSchema(BaseStrictSchema):
    user_id: Constraints.PositiveInteger
    view_id: Constraints.PositiveInteger
    can_list: Constraints.BooleanTrue
    can_read: Constraints.BooleanFalse
    can_create: Constraints.BooleanFalse
    can_update: Constraints.BooleanFalse
    can_delete: Constraints.BooleanFalse
