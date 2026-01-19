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

    @model_validator(mode="after")
    def _validate_data(self) -> DiscountStrictSchema:
        if self.end_date and self.end_date <= self.start_date:
            raise ValueError("End date must be greater than start date.")

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
