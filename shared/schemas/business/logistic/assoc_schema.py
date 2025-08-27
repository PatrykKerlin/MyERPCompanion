from schemas.base import BaseStrictSchema
from schemas.validation import Constraints


class AssocBinItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    bin_id: Constraints.PositiveInteger
