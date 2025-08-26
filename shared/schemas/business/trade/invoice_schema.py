from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import date

from schemas.base import BaseStrictSchema, BasePlainSchema, Constraints

if TYPE_CHECKING:
    from .currency_schema import CurrencyPlainSchema
    from .payment_method_schema import PaymentMethodPlainSchema


class InvoiceStrictSchema(BaseStrictSchema):
    number: Constraints.String20

    issue_date: date
    due_date: date

    is_paid: Constraints.BooleanFalse
    total_net: Constraints.PositiveNumeric102
    total_vat: Constraints.PositiveNumeric102
    total_gross: Constraints.PositiveNumeric102
    total_discount: Constraints.PositiveNumeric102

    currency_id: Constraints.PositiveInteger
    payment_method_id: Constraints.PositiveInteger
    orders: Constraints.PositiveIntegerList


class InvoicePlainSchema(BasePlainSchema):
    number: str

    issue_date: date
    due_date: date

    is_paid: bool
    total_net: float
    total_vat: float
    total_gross: float
    total_discount: float

    currency_id: CurrencyPlainSchema
    payment_method_id: PaymentMethodPlainSchema
