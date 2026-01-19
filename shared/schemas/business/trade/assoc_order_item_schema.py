from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocOrderItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    total_net: Constraints.PositiveNumeric_10_2
    total_vat: Constraints.PositiveNumeric_10_2
    total_gross: Constraints.PositiveNumeric_10_2
    total_discount: Constraints.PositiveNumeric_10_2

    order_id: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveIntegerOptional


class AssocOrderItemPlainSchema(BasePlainSchema):
    quantity: int
    total_net: float
    total_vat: float
    total_gross: float
    total_discount: float

    order_id: int
    item_id: int
    discount_id: int | None
