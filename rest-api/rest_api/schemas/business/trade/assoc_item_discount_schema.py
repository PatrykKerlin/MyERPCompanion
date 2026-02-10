from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocItemDiscountStrictSchema(BaseStrictSchema):
    item_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocItemDiscountPlainSchema(BasePlainSchema):
    item_id: int
    discount_id: int
