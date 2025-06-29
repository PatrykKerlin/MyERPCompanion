from typing import Annotated

from pydantic import Field

from schemas.base import BaseStrictSchema, BasePlainSchema


class ThemeStrictSchema(BaseStrictSchema):
    key: Annotated[str, Field(min_length=4, max_length=25)]


class ThemePlainSchema(BasePlainSchema):
    key: str
