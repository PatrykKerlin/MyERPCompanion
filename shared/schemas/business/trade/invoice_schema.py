from datetime import date

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class InvoiceStrictSchema(BaseStrictSchema):
    number: Constraints.String_20

    issue_date: date
    due_date: date

    is_paid: Constraints.BooleanFalse
    total_net: Constraints.PositiveNumeric_10_2
    total_vat: Constraints.PositiveNumeric_10_2
    total_gross: Constraints.PositiveNumeric_10_2
    total_discount: Constraints.PositiveNumeric_10_2

    currency_id: Constraints.PositiveInteger
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

    currency_id: int
