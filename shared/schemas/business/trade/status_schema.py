from typing import Any
from pydantic import Field, field_validator
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints
from schemas.validation.normalizers import Normalizers


class StatusStrictSchema(BaseStrictSchema):
    key: Constraints.Name
    description: Constraints.StringOptional_1000
    order: Constraints.PositiveInteger


class StatusPlainSchema(BasePlainSchema):
    key: str
    description: str | None
    order: int

    order_ids: list[int] = Field(alias="orders")

    @field_validator("order_ids", mode="before")
    @classmethod
    def _normalize_orders(cls, values: list[Any]) -> list[int]:
        return Normalizers.normalize_related_ids(values)
