from __future__ import annotations

from typing import Any

from pydantic import model_validator, field_validator

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers


class BinStrictSchema(BaseStrictSchema):
    location: Constraints.String10
    is_inbound: Constraints.BooleanFalse
    is_outbound: Constraints.BooleanTrue
    max_volume: Constraints.PositiveFloat
    max_weight: Constraints.PositiveInteger
    warehouse_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def _validate_data(self) -> BinStrictSchema:
        if not self.is_inbound and not self.is_outbound:
            raise ValueError("at least one of is_inbound or is_outbound must be true")
        return self


class BinPlainSchema(BasePlainSchema):
    location: str
    is_inbound: bool
    is_outbound: bool
    max_volume: float
    max_weight: int
    warehouse_id: int
    items: list[int]

    @field_validator("warehouse_id", mode="before")
    @classmethod
    def _normalize_warehouse_id(cls, value: Any) -> int | None:
        return Normalizers.normalize_related_single_id(value)

    @field_validator("items", mode="before")
    @classmethod
    def _normalize_items(cls, values: list[Any]) -> list[int]:
        return Normalizers.normalize_related_id_list(values)
