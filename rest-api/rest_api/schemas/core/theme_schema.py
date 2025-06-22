from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema


class ThemeInputSchema(BaseInputSchema):
    key: Annotated[str, Field(min_length=4, max_length=25)]


class ThemeOutputSchema(BaseOutputSchema):
    key: str
