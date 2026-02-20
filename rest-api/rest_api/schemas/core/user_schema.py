from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, model_validator
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.group_schema import GroupPlainSchema
from schemas.core.language_schema import LanguagePlainSchema
from schemas.validation.constraints import Constraints


class UserStrictBaseSchema(BaseModel):
    username: Constraints.Username
    theme: Constraints.Theme
    language_id: Constraints.PositiveInteger
    employee_id: Constraints.PositiveIntegerOptional
    customer_id: Constraints.PositiveIntegerOptional
    warehouse_id: Constraints.PositiveIntegerOptional


class UserStrictCreateApiSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.Password


class UserStrictCreateAppSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.Password
    password_repeat: Annotated[Constraints.Password, Field(exclude=True)]

    @model_validator(mode="after")
    def _validate_passwords(self) -> UserStrictCreateAppSchema:
        if self.password != self.password_repeat:
            raise ValueError("passwords_do_not_match")
        return self


class UserStrictUpdateApiSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.PasswordOptional


class UserStrictUpdateAppSchema(BaseStrictSchema, UserStrictBaseSchema):
    password: Constraints.PasswordOptional
    password_repeat: Annotated[Constraints.PasswordOptional, Field(exclude=True)]

    @model_validator(mode="after")
    def _validate_passwords(self) -> UserStrictUpdateAppSchema:
        if self.password is None and self.password_repeat is None:
            return self
        if self.password is None or self.password_repeat is None:
            raise ValueError("passwords_do_not_match")
        if self.password != self.password_repeat:
            raise ValueError("passwords_do_not_match")
        return self


class UserPlainSchema(BasePlainSchema):
    username: str
    theme: str
    language: LanguagePlainSchema
    groups: list[GroupPlainSchema]
    is_superuser: bool
    password: Annotated[str | None, Field(default=None, exclude=True)]
    employee_id: int | None
    customer_id: int | None
    warehouse_id: int | None
