from typing import Annotated

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema


class DepartmentStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    description: Annotated[str | None, Field(max_length=255)]


class DepartmentPlainSchema(BasePlainSchema):
    key: str
    description: str | None
