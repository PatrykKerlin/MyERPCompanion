from typing import Annotated

from pydantic import Field

from schemas.base import BaseCreateSchema


class AuthCreate(BaseCreateSchema):
    name: Annotated[str, Field(min_length=3, max_length=50)]
    description: Annotated[str, Field(min_length=5, max_length=128)]
