from pydantic import Field

from schemas.base import BaseSchema


class AuthCreate(BaseSchema):
    username: str = Field(min_length=5, max_length=25)
    password: str = Field(min_length=8, max_length=128)
