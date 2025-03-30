from typing import Annotated

from pydantic import Field, field_serializer

from schemas.base import BaseCreateSchema, BaseResponseSchema


class UserCreate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    groups: Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()] | None = None


class UserUpdate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=128)] | None = None
    groups: Annotated[list[Annotated[str, Field(min_length=1, max_length=10)]], Field()] | None = None


class UserResponse(BaseResponseSchema):
    username: str
    groups: list[str]

    @field_serializer("groups")
    def serialize_groups(self, groups: list["GroupDTO"]) -> list[str]:
        return [group.name for group in groups]
