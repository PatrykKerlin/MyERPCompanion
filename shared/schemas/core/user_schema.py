from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints

if TYPE_CHECKING:
    from .group_schema import GroupPlainSchema
    from .language_schema import LanguagePlainSchema
    from .theme_schema import ThemePlainSchema


class UserStrictBaseSchema(BaseModel):
    username: Constraints.Username
    employee_id: Constraints.PositiveInteger
    language_id: Constraints.PositiveInteger
    theme_id: Constraints.PositiveInteger
    groups: Constraints.PositiveIntegerList


class UserStrictCreateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.Password


class UserStrictUpdateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.PasswordOptional


class UserPlainSchema(BasePlainSchema):
    username: str
    language: LanguagePlainSchema
    theme: ThemePlainSchema
    groups: list[GroupPlainSchema]
    is_superuser: Annotated[bool, Field(exclude=True)]
    password: Annotated[str, Field(exclude=True)]
