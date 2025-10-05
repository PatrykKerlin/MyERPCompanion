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


class PositionPlainSchema(BasePlainSchema):
    name: str
    description: str
    level: int
    min_salary: int
    max_salary: int
    currency_id: int
    department_id: int
