from typing import Annotated

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema


class PositionStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    level: Annotated[int, Field(ge=1)]
    min_salary: Annotated[int, Field(ge=1000)]
    max_salary: Annotated[int, Field(ge=1000)]


class PositionPlainSchema(BasePlainSchema):
    key: str
    level: int
    min_salary: int
    max_salary: int
