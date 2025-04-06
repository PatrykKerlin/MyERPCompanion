from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema, BaseResponseSchema
from schemas.core import GroupInternal


class ModuleCreate(BaseCreateSchema):
    name: Annotated[str, Field(min_length=1, max_length=25)]
    label: Annotated[str, Field(min_length=1, max_length=25)]


class ModuleResponse(BaseResponseSchema):
    name: str
    label: str


class ModuleInternal(BaseResponseSchema):
    name: str
    groups: list[GroupInternal]
