from __future__ import annotations

from typing import Annotated, TYPE_CHECKING

from pydantic import Field, model_validator

from schemas.base import BaseStrictSchema, BasePlainSchema

if TYPE_CHECKING:
    from .warehouse_schema import WarehousePlainSchema


class BinStrictSchema(BaseStrictSchema):
    location: Annotated[str, Field(pattern=r"^[A-Z]{2}\d{5}$", min_length=7, max_length=7)]
    is_inbound: Annotated[bool, Field(default=False)]
    is_outbound: Annotated[bool, Field(default=False)]
    max_volume: Annotated[float, Field(gt=0)]
    max_weight: Annotated[int, Field(ge=1)]
    warehouse_id: Annotated[int, Field(ge=1)]

    @model_validator(mode="after")
    def _validate_flags(self) -> BinStrictSchema:
        if not self.is_inbound and not self.is_outbound:
            raise ValueError("at least one of is_inbound or is_outbound must be true")
        return self


class BinPlainSchema(BasePlainSchema):
    location: str
    is_inbound: bool
    is_outbound: bool
    max_volume: float
    max_weight: int
    warehouse: WarehousePlainSchema
