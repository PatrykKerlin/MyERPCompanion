from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


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
