from typing import Annotated, List

from pydantic import Field, field_serializer

from schemas.base import BaseCreateSchema, BaseUpdateSchema, BaseResponseSchema


class UserCreate(BaseCreateSchema):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=6, max_length=100)]
    groups: List[Annotated[str, Field(min_length=1, max_length=10)]]


class UserUpdate(BaseUpdateSchema):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=6, max_length=100)] | None = None
    groups: List[Annotated[str, Field(min_length=1, max_length=10)]]


class UserResponse(BaseResponseSchema):
    username: str
    groups: list

    @field_serializer("groups")
    def serialize_groups(self, groups: list) -> list:
        return [group.name for group in groups]
