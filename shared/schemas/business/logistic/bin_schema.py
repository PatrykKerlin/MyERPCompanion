from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator, model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints
from schemas.validation.normalizers import Normalizers


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
