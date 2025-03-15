from typing import List

from pydantic import Field, constr, field_serializer
from schemas.base import BaseCreateSchema, BaseResponseSchema


class UserCreate(BaseCreateSchema):
    username: constr(min_length=3, max_length=50) = Field(...)
    password: constr(min_length=6, max_length=100) = Field(...)
    groups: List[constr(min_length=1, max_length=10)]


class UserResponse(BaseResponseSchema):
    username: str = Field(...)
    groups: list = Field(...)

    @field_serializer("groups")
    def serialize_groups(self, groups: list) -> list:
        return [group.name for group in groups]
