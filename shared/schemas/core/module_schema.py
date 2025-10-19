from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints

from schemas.core.group_schema import GroupPlainSchema
from schemas.core.view_schema import ViewPlainSchema


class ModuleStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    in_side_menu: Constraints.BooleanTrue
    order: Constraints.PositiveInteger
    groups: Constraints.PositiveIntegerList


class ModulePlainSchema(BasePlainSchema):
    key: str
    description: str | None
    in_side_menu: bool
    order: int
    views: list[ViewPlainSchema]
    groups: list[GroupPlainSchema]
