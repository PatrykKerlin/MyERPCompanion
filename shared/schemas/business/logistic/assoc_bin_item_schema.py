from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocBinItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    bin_id: Constraints.PositiveInteger


class AssocBinItemPlainSchema(BasePlainSchema):
    quantity: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    bin_id: Constraints.PositiveInteger
