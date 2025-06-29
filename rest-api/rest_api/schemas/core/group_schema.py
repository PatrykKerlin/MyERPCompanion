from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema, BasePlainSchema


class GroupStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=10)]
    description: Annotated[str, Field(min_length=1, max_length=255)]


class GroupPlainSchema(BasePlainSchema):
    key: str
    description: str
