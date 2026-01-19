from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class DeliveryMethodStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    description: Constraints.StringOptional_1000
    price_per_unit: Constraints.PositiveNumeric_10_2
    max_width: Constraints.PositiveNumeric_6_3
    max_height: Constraints.PositiveNumeric_6_3
    max_length: Constraints.PositiveNumeric_6_3
    max_weight: Constraints.PositiveNumeric_11_3
    carrier_id: Constraints.PositiveInteger
    unit_id: Constraints.PositiveInteger


class DeliveryMethodPlainSchema(BasePlainSchema):
    name: str
    description: str | None
    price_per_unit: float
    max_width: float
    max_height: float
    max_length: float
    max_weight: float
    carrier_id: int
    unit_id: int
