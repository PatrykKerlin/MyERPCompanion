from typing import Annotated

from pydantic import BaseModel, Field

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints

from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.theme_schema import ThemePlainSchema


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
