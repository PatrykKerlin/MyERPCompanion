from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import field_validator, model_validator

from schemas.base import BasePlainSchema, BaseStrictSchema
from schemas.validation import Constraints, Normalizers


class OrderStrictSchema(BaseStrictSchema):
    number: Constraints.String20
    is_sales: Constraints.BooleanTrue

    total_net: Constraints.PositiveNumeric102
    total_vat: Constraints.PositiveNumeric102
    total_gross: Constraints.PositiveNumeric102
    total_discount: Constraints.PositiveNumeric102

    order_date: date

    tracking_number: Constraints.String50Optional
    shipping_cost: Constraints.PositiveNumeric102

    notes: Constraints.String1000Optional
    internal_notes: Constraints.String1000Optional

    customer_id: Constraints.PositiveIntegerOptional
    supplier_id: Constraints.PositiveIntegerOptional
    delivery_method_id: Constraints.PositiveInteger

    order_items: Constraints.PositiveIntegerList
    order_statuses: Constraints.PositiveIntegerList

    @model_validator(mode="after")
    def _validate_data(self) -> OrderStrictSchema:
        if not self.customer_id and not self.supplier_id:
            raise ValueError("either customer_id or supplier_id must be provided")

        if self.customer_id and self.supplier_id:
            raise ValueError("customer_id and supplier_id are mutually exclusive")

        return self


class OrderPlainSchema(BasePlainSchema):
    number: str
    is_sales: bool

    total_net: float
    total_vat: float
    total_gross: float
    total_discount: float

    order_date: date

    tracking_number: str | None
    shipping_cost: float

    notes: str | None
    internal_notes: str | None

    customer_id: int
    supplier_id: int
    delivery_method_id: int
    invoice_id: int | None

    items: list[int]
    statuses: list[int]

    @field_validator("items", mode="before")
    @classmethod
    def _normalize_items(cls, items: Any) -> list[int]:
        return Normalizers.normalize_related_ids(items)

    @field_validator("statuses", mode="before")
    @classmethod
    def _normalize_statuses(cls, statuses: Any) -> list[int]:
        return Normalizers.normalize_related_ids(statuses)
