from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints

if TYPE_CHECKING:
    from .group_schema import GroupPlainSchema
    from .view_schema import ViewPlainSchema


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
