from schemas.base import BaseStrictSchema, Constraints


class AssocBinItemStrictSchema(BaseStrictSchema):
    quantity: Constraints.PositiveInteger
    item_id: Constraints.PositiveInteger
    bin_id: Constraints.PositiveInteger
