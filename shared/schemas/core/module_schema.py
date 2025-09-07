from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.core import GroupPlainSchema, ViewPlainSchema
from schemas.validation import Constraints


class ModuleStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    order: Constraints.PositiveInteger
    groups: Constraints.PositiveIntegerList


class ModulePlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int
    views: list[ViewPlainSchema]
    groups: list[GroupPlainSchema]
