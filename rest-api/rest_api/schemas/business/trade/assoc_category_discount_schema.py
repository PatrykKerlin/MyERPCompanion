from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocCategoryDiscountStrictSchema(BaseStrictSchema):
    category_id: Constraints.PositiveInteger
    discount_id: Constraints.PositiveInteger


class AssocCategoryDiscountPlainSchema(BasePlainSchema):
    category_id: int
    discount_id: int
