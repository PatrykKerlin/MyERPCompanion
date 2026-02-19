from __future__ import annotations

from datetime import datetime

from pydantic import model_validator
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class DiscountStrictSchema(BaseStrictSchema):
    name: Constraints.Name
    code: Constraints.String_10
    description: Constraints.StringOptional_1000

    start_date: datetime
    end_date: datetime | None

    percent: Constraints.PercentFloat

    min_value: Constraints.PositiveNumericOptional_10_2
    min_quantity: Constraints.PositiveIntegerOptional

    for_categories: Constraints.BooleanFalse
    for_customers: Constraints.BooleanFalse
    for_items: Constraints.BooleanFalse

    currency_id: Constraints.PositiveIntegerOptional

    @model_validator(mode="after")
    def _validate_data(self) -> DiscountStrictSchema:
        if self.end_date and self.end_date <= self.start_date:
            raise ValueError("End date must be greater than start date.")

        has_min_value = self.min_value is not None
        has_currency_id = self.currency_id is not None
        if has_min_value != has_currency_id:
            raise ValueError("'Min_value' and 'currency_id' must be provided together or both be empty.")
        
        selected_scopes_count = sum(
            (
                1 if self.for_categories else 0,
                1 if self.for_customers else 0,
                1 if self.for_items else 0,
            )
        )
        if selected_scopes_count == 0:
            raise ValueError("Exactly one of 'for_categories', 'for_customers', or 'for_items' must be selected.")
        if selected_scopes_count > 1:
            raise ValueError("Only one of 'for_categories', 'for_customers', or 'for_items' can be selected.")

        return self


class DiscountPlainSchema(BasePlainSchema):
    name: str
    code: str
    description: str | None

    start_date: datetime
    end_date: datetime | None

    percent: float | None

    min_value: float | None
    min_quantity: int | None

    for_categories: bool
    for_customers: bool
    for_items: bool

    currency_id: int | None
