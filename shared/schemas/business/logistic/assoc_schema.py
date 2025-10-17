from schemas.base.base_schema import BaseStrictSchema
from schemas.validation.constraints import Constraints


class AssocBinItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    bin_id: Constraints.PositiveInteger
