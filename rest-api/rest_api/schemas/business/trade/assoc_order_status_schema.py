from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocOrderStatusStrictSchema(BaseStrictSchema):
    order_id: Constraints.PositiveInteger
    status_id: Constraints.PositiveInteger


class AssocOrderStatusPlainSchema(BasePlainSchema):
    order_id: int
    status_id: int
