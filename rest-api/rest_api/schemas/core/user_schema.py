from typing import List
from pydantic import BaseModel, Field, constr, field_serializer


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(...)
    password: constr(min_length=6, max_length=100) = Field(...)
    groups: List[constr(min_length=1, max_length=10)] = Field(...)

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int = Field(...)
    username: str = Field(...)
    groups: list = Field(...)

    class Config:
        from_attributes = True

    @field_serializer("groups")
    def serialize_groups(self, groups: list) -> list:
        return [group.name for group in groups]
