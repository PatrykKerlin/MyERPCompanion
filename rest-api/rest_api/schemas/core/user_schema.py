from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema, BaseInternalSchema, BaseResponseSchema
from schemas.core import GroupInternal, GroupResponse


class UserCreate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    groups: Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()]


class UserUpdate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=128)] | None = None
    groups: (
        Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()]
        | None
    ) = None


class UserResponse(BaseResponseSchema):
    username: str
    groups: list[GroupResponse]


class UserInternal(BaseInternalSchema):
    username: str
    groups: list[GroupInternal]
    is_superuser: bool
    password: str | None = Field(default=None, exclude=True)
