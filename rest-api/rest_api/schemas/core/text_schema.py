from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import SettingOutputSchema


class TextInputSchema(BaseInputSchema):
    name: Annotated[str, Field(min_length=1, max_length=25)]
    value: Annotated[str, Field(min_length=1, max_length=255)]
    language_id: Annotated[int, Field(ge=1)]


class TextOutputSchema(BaseOutputSchema):
    name: str
    value: str
    language: SettingOutputSchema
