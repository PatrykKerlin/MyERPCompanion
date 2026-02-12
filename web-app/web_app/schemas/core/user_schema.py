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

    @model_validator(mode="after")
    def _validate_exactly_one_of_employee_or_customer(self) -> UserStrictBaseSchema:
        has_employee = self.employee_id is not None
        has_customer = self.customer_id is not None

        if has_employee == has_customer:
            raise ValueError("Exactly one of 'employee_id' or 'customer_id' must be provided.")
        return self


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
    is_superuser: Annotated[bool | None, Field(default=None, exclude=True)]
    password: Annotated[str | None, Field(default=None, exclude=True)]
    employee_id: int | None
    customer_id: int | None
