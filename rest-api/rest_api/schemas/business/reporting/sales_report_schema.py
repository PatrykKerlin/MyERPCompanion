from __future__ import annotations

from datetime import date

from pydantic import model_validator
from schemas.base.base_schema import BaseSchema
from schemas.validation.constraints import Constraints


class SalesReportFilterSchema(BaseSchema):
    date_from: date | None = None
    date_to: date | None = None
    item_id: Constraints.PositiveIntegerOptional = None
    customer_id: Constraints.PositiveIntegerOptional = None
    category_id: Constraints.PositiveIntegerOptional = None
    currency_id: Constraints.PositiveIntegerOptional = None

    @model_validator(mode="after")
    def _validate_date_range(self) -> "SalesReportFilterSchema":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be less than or equal to date_to")
        return self


class SalesReportRowSchema(BaseSchema):
    order_item_id: int
    order_id: int
    order_number: str
    order_date: date

    customer_id: int | None
    customer_name: str | None

    item_id: int
    item_name: str

    category_id: int
    category_name: str

    quantity: int
    total_net: float
    total_vat: float
    total_gross: float
    total_discount: float


class SalesReportTotalsSchema(BaseSchema):
    orders_count: int = 0
    rows_count: int = 0
    quantity: int = 0
    total_net: float = 0
    total_vat: float = 0
    total_gross: float = 0
    total_discount: float = 0


class SalesReportResponseSchema(BaseSchema):
    items: list[SalesReportRowSchema]
    totals: SalesReportTotalsSchema
