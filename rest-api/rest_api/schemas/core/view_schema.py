from typing import Annotated

from pydantic import Field

from schemas.base import BasePlainSchema, BaseStrictSchema


class ViewStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=1, max_length=25)]
    controller: Annotated[str, Field(min_length=1, max_length=50)]
    path: Annotated[str, Field(min_length=1, max_length=100)]
    order: Annotated[int, Field(ge=1)]
    module_id: Annotated[int, Field(ge=1)]


class ViewPlainSchema(BasePlainSchema):
    key: str
    controller: str
    path: str
    order: int
