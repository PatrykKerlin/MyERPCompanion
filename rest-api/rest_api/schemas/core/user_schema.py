from typing import Annotated

from pydantic import Field, field_serializer

from dtos.core import GroupDTO
from schemas.base import BaseCreateSchema, BaseResponseSchema


class UserCreate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=6, max_length=100)]
    groups: Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()] | None = None


class UserUpdate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=6, max_length=100)] | None = None
    groups: Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()] | None = None


class UserResponse(BaseResponseSchema):
    username: str
    groups: list[str]

    @field_serializer("groups")
    def serialize_groups(self, groups: list[GroupDTO]) -> list[str]:
        return [group.name for group in groups]
