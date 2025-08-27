from typing import Any
from pydantic import field_validator
from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers


class PositionStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional
    level: Constraints.PositiveInteger
    min_salary: Constraints.PositiveInteger
    max_salary: Constraints.PositiveInteger
    department_id: Constraints.PositiveInteger


class PositionPlainSchema(BasePlainSchema):
    key: str
    description: str
    level: int
    min_salary: int
    max_salary: int
    department_id: int

    @field_validator("department_id", mode="before")
    @classmethod
    def _normalize_department_id(cls, value: Any) -> int | None:
        return Normalizers.normalize_related_single_id(value)
