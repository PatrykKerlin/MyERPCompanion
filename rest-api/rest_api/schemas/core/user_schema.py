from typing import Annotated

from pydantic import BaseModel, Field

from schemas.base import BaseInputSchema, BaseOutputSchema
from schemas.core import GroupOutputSchema, LanguageOutputSchema, ThemeOutputSchema


class UserInputBaseSchema(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    language_id: Annotated[int, Field(ge=1)]
    theme_id: Annotated[int, Field(ge=1)]


class UserInputCreateSchema(BaseInputSchema, UserInputBaseSchema):
    groups: Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserInputUpdateSchema(BaseInputSchema, UserInputBaseSchema):
    groups: Annotated[list[Annotated[int, Field(ge=1)]] | None, Field(default=None, min_length=1)]
    password: Annotated[str | None, Field(default=None, min_length=8, max_length=128)]


class UserOutputSchema(BaseOutputSchema):
    username: str
    language: LanguageOutputSchema
    theme: ThemeOutputSchema
    groups: list[GroupOutputSchema]
    is_superuser: Annotated[bool, Field(exclude=True)]
    password: Annotated[str, Field(exclude=True)]
