from typing import Annotated

from pydantic import Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import GroupInputSchema, LanguageInputSchema, ThemeInputSchema


class UserInputSchema(BaseInputSchema):
    username: str
    language: LanguageInputSchema
    theme: ThemeInputSchema
    groups: list[GroupInputSchema]


class UserOutputSchema(BaseOutputSchema):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    language_id: Annotated[int, Field(ge=1)]
    theme_id: Annotated[int, Field(ge=1)]
    groups: Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(default=None, min_length=1)]
    password: Annotated[str | None, Field(default=None, min_length=8, max_length=128)]
