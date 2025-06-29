from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema, BasePlainSchema
from schemas.core import ViewPlainSchema, GroupPlainSchema


class ModuleStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    order: Annotated[int, Field(ge=1)]
    groups: Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(default=None)]


class ModulePlainSchema(BasePlainSchema):
    key: str
    order: int
    views: list[ViewPlainSchema] = []
    groups: list[GroupPlainSchema] = []
