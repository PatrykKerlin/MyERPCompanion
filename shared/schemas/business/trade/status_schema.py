from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class StatusStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.StringOptional_1000
    step_number: Constraints.PositiveInteger


class StatusPlainSchema(BasePlainSchema):
    name: str
    description: str | None
    step_number: int

    order_ids: list[int]
