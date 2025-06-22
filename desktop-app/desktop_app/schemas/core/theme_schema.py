from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class ThemeInputSchema(BaseInputSchema):
    key: str


class ThemeOutputSchema(BaseOutputSchema):
    key: Annotated[str, Field(min_length=4, max_length=25)]
