from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.view_schema import ViewPlainSchema
from schemas.validation.constraints import Constraints


class ModuleStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    in_side_menu: Constraints.BooleanTrue
    order: Constraints.PositiveInteger
    controllers: Constraints.String50List
    groups: Constraints.PositiveIntegerList


class ModulePlainSchema(BasePlainSchema):
    key: str
    description: str | None
    in_side_menu: bool
    order: int
    controllers: list[str]
    views: list[ViewPlainSchema]
    groups: list[GroupPlainSchema]
