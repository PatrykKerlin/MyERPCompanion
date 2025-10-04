from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.core import GroupPlainSchema, ViewPlainSchema
from schemas.validation import Constraints


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
