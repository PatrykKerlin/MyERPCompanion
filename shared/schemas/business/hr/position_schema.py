from __future__ import annotations

from pydantic import model_validator
from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class PositionStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.String1000Optional
    level: Constraints.PositiveInteger
    min_salary: Constraints.PositiveInteger
    max_salary: Constraints.PositiveInteger
    currency_id: Constraints.PositiveInteger
    department_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def _validate_data(self) -> PositionStrictSchema:
        if self.min_salary > self.max_salary:
            raise ValueError("max_salary must be greater than or equal to min_salary")
        return self


class PositionPlainSchema(BasePlainSchema):
    name: str
    description: str
    level: int
    min_salary: int
    max_salary: int
    currency_id: int
    department_id: int
