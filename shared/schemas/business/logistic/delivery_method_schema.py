from typing import Any

from pydantic import field_validator

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers


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

    @field_validator("carrier_id", mode="before")
    @classmethod
    def _normalize_carrier_id(cls, value: Any) -> int | None:
        return Normalizers.normalize_related_single_id(value)

    @field_validator("unit_id", mode="before")
    @classmethod
    def _normalize_unit_id(cls, value: Any) -> int | None:
        return Normalizers.normalize_related_single_id(value)
