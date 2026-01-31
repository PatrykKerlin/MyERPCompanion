from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import Field, field_validator, model_validator

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints
from schemas.validation.normalizers import Normalizers


class OrderStrictSchema(BaseStrictSchema):
    number: Constraints.String_20
    is_sales: Constraints.BooleanTrue

    total_net: Constraints.NonNegativeNumeric_10_2
    total_vat: Constraints.NonNegativeNumeric_10_2
    total_gross: Constraints.NonNegativeNumeric_10_2
    total_discount: Constraints.NonNegativeNumeric_10_2

    order_date: date

    tracking_number: Constraints.StringOptional_50
    shipping_cost: Constraints.NonNegativeNumeric_10_2

    notes: Constraints.StringOptional_1000
    internal_notes: Constraints.StringOptional_1000

    customer_id: Constraints.PositiveIntegerOptional
    supplier_id: Constraints.PositiveIntegerOptional
    delivery_method_id: Constraints.PositiveIntegerOptional
    currency_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def _validate_data(self) -> OrderStrictSchema:
        if not self.customer_id and not self.supplier_id:
            raise ValueError("either customer_id or supplier_id must be provided")

        if self.customer_id and self.supplier_id:
            raise ValueError("customer_id and supplier_id are mutually exclusive")

        if self.supplier_id and self.is_sales:
            raise ValueError("purchase orders must have is_sales set to False")

        if self.customer_id and not self.is_sales:
            raise ValueError("sales orders must have is_sales set to True")

        return self


class OrderInvoiceBulkStrictSchema(BaseStrictSchema):
    invoice_id: Constraints.PositiveIntegerOptional


class PurchaseOrderStrictSchema(BaseStrictSchema):
    number: Constraints.String_20
    is_sales: Constraints.BooleanTrue

    total_net: Constraints.NonNegativeNumeric_10_2
    total_vat: Constraints.NonNegativeNumeric_10_2
    total_gross: Constraints.NonNegativeNumeric_10_2
    total_discount: Constraints.NonNegativeNumeric_10_2

    order_date: date

    tracking_number: Constraints.StringOptional_50
    shipping_cost: Constraints.NonNegativeNumeric_10_2

    notes: Constraints.StringOptional_1000
    internal_notes: Constraints.StringOptional_1000

    customer_id: Constraints.PositiveIntegerOptional
    supplier_id: Constraints.PositiveInteger
    delivery_method_id: Constraints.PositiveIntegerOptional
    currency_id: Constraints.PositiveInteger


class SalesOrderStrictSchema(BaseStrictSchema):
    number: Constraints.String_20
    is_sales: Constraints.BooleanTrue

    total_net: Constraints.NonNegativeNumeric_10_2
    total_vat: Constraints.NonNegativeNumeric_10_2
    total_gross: Constraints.NonNegativeNumeric_10_2
    total_discount: Constraints.NonNegativeNumeric_10_2

    order_date: date

    tracking_number: Constraints.StringOptional_50
    shipping_cost: Constraints.NonNegativeNumeric_10_2

    notes: Constraints.StringOptional_1000
    internal_notes: Constraints.StringOptional_1000

    customer_id: Constraints.PositiveInteger
    supplier_id: Constraints.PositiveIntegerOptional
    delivery_method_id: Constraints.PositiveInteger
    currency_id: Constraints.PositiveInteger


class OrderPlainSchema(BasePlainSchema):
    number: str

    total_net: float
    total_vat: float
    total_gross: float
    total_discount: float

    order_date: date

    tracking_number: str | None
    shipping_cost: float

    notes: str | None
    internal_notes: str | None

    customer_id: int | None
    supplier_id: int | None
    delivery_method_id: int | None
    currency_id: int
    invoice_id: int | None

    item_ids: list[int]
    status_ids: list[int]
