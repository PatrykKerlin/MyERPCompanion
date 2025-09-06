from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints


class DeliveryMethodStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    description: Constraints.String1000Optional

    price_per_unit: Constraints.PositiveNumeric102

    max_width: Constraints.PositiveNumeric63
    max_height: Constraints.PositiveNumeric63
    max_length: Constraints.PositiveNumeric63
    max_weight: Constraints.PositiveNumeric103

    carrier_id: Constraints.PositiveInteger
    unit_id: Constraints.PositiveInteger


class DeliveryMethodPlainSchema(BasePlainSchema):
    key: str
    description: str | None

    price_per_unit: Constraints.PositiveNumeric102

    max_width: float
    max_height: float
    max_length: float
    max_weight: float

    carrier_id: int
    unit_id: int
