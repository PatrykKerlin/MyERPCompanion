from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints

if TYPE_CHECKING:
    from .department_schema import DepartmentPlainSchema


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
    department: DepartmentPlainSchema
