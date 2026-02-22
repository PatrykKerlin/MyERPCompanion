from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocCustomerDiscountStrictSchema(BaseStrictSchema):
    customer_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocCustomerDiscountPlainSchema(BasePlainSchema):
    customer_id: int
    discount_id: int
