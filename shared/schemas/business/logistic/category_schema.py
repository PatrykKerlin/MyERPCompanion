from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema, BasePlainSchema


class CategoryStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    description: Annotated[str | None, Field(max_length=255)]


class CategoryPlainSchema(BasePlainSchema):
    key: str
    description: str | None
