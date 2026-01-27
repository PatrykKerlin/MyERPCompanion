from typing import Annotated

from pydantic import BaseModel, Field

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.validation.constraints import Constraints


class UserStrictBaseSchema(BaseModel):
    username: Constraints.Username
    theme: Constraints.Theme
    language_id: Constraints.PositiveInteger


class UserStrictCreateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.Password


class UserStrictUpdateSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.PasswordOptional


class UserPlainSchema(BasePlainSchema):
    username: str
    theme: str
    language: LanguagePlainSchema
    groups: list[GroupPlainSchema]
    is_superuser: Annotated[bool, Field(exclude=True)]
    password: Annotated[str, Field(exclude=True)]
