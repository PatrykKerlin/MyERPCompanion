from typing import Annotated

from pydantic import BaseModel, Field

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.core import GroupPlainSchema, LanguagePlainSchema, ThemePlainSchema


class UserStrictBaseSchema(BaseModel):
    username: Annotated[str, Field(min_length=5, max_length=25)]
    language_id: Annotated[int, Field(ge=1)]
    theme_id: Annotated[int, Field(ge=1)]
    groups: Annotated[list[Annotated[int, Field(ge=1)]], Field(min_length=1)]


class UserStrictCreateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserStrictUpdateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Annotated[str | None, Field(default=None, min_length=8, max_length=128)]


class UserPlainSchema(BasePlainSchema):
    username: str
    language: LanguagePlainSchema
    theme: ThemePlainSchema
    groups: list[GroupPlainSchema]
    is_superuser: Annotated[bool, Field(exclude=True)]
    password: Annotated[str, Field(exclude=True)]
