from __future__ import annotations

from typing import TYPE_CHECKING

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints

if TYPE_CHECKING:
    from .carrier_schema import CarrierPlainSchema
    from .unit_schema import UnitPlainSchema


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

    carrier: CarrierPlainSchema
    unit: UnitPlainSchema
