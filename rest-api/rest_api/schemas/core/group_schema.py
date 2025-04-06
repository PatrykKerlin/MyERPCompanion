from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema, BaseResponseSchema


class GroupCreate(BaseCreateSchema):
    name: Annotated[str, Field(min_length=1, max_length=10)]
    description: Annotated[str, Field(min_length=1, max_length=255)]


class GroupResponse(BaseResponseSchema):
    name: str
    description: str


class GroupInternal(BaseResponseSchema):
    name: str
