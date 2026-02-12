from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class StatusStrictSchema(BaseStrictSchema):
    key: Constraints.Name
    description: Constraints.StringOptional_1000
    order: Constraints.PositiveInteger


class StatusPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int

    order_ids: list[int]
