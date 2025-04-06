from typing import Annotated

from pydantic import Field

from schemas.base import BaseSchema


class AuthCreate(BaseSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
