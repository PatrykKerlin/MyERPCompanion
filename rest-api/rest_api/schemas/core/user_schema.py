from pydantic import Field

from schemas.base import BaseCreateSchema, BaseInternalSchema, BaseResponseSchema
from schemas.core import GroupInternal, GroupResponse


class UserCreate(BaseCreateSchema):
    username: str = Field(min_length=5, max_length=25)
    password: str = Field(min_length=8, max_length=128)
    groups: list[str] = Field(...)


class UserUpdate(BaseCreateSchema):
    username: str = Field(min_length=5, max_length=25)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    groups: list[str] | None = Field(default=None)


class UserResponse(BaseResponseSchema):
    username: str
    groups: list[GroupResponse]


class UserInternal(BaseInternalSchema):
    username: str
    groups: list[GroupInternal]
    is_superuser: bool
    password: str | None = Field(default=None, exclude=True)
