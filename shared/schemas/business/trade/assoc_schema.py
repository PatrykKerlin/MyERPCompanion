from schemas.base.base_schema import BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocCategoryDiscountStrictSchema(BaseStrictSchema):
    category_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocCustomerDiscountStrictSchema(BaseStrictSchema):
    customer_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocItemDiscountStrictSchema(BaseStrictSchema):
    item_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocOrderItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    total_net: Constraints.PositiveNumeric102
    total_vat: Constraints.PositiveNumeric102
    total_gross: Constraints.PositiveNumeric102
    total_discount: Constraints.PositiveNumeric102

    order_id: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveIntegerOptional


class AssocOrderStatusStrictSchema(BaseStrictSchema):
    order_id: Constraints.PositiveInteger
    status_id: Constraints.PositiveInteger
