from __future__ import annotations

from datetime import datetime

from pydantic import model_validator

from schemas.base import BasePlainSchema, BaseStrictSchema, Constraints


class DiscountStrictSchema(BaseStrictSchema):
    key: Constraints.Key
    index: Constraints.String10
    description: Constraints.String1000Optional

    start_date: datetime
    end_date: datetime | None

    percent: Constraints.PercentFloatOptional
    amount: Constraints.PositiveNumeric102Optional

    min_value: Constraints.PositiveNumeric102Optional
    min_quantity: Constraints.PositiveIntegerOptional

    categories: Constraints.PositiveIntegerListOptional
    customers: Constraints.PositiveIntegerListOptional
    items: Constraints.PositiveIntegerListOptional

    @model_validator(mode="after")
    def _validate_data(self) -> DiscountStrictSchema:
        if not self.percent and not self.amount:
            raise ValueError("either percent or amount must be provided")

        if self.percent and self.amount:
            raise ValueError("percent and amount are mutually exclusive; provide only one")

        if self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")

        if not (self.categories or self.customers or self.items):
            raise ValueError("discount must apply to at least one category, customer, or item")

        return self


class DiscountPlainSchema(BasePlainSchema):
    key: str
    index: str
    description: str | None

    start_date: datetime
    end_date: datetime | None

    percent: float | None
    amount: float | None

    min_value: float | None
    min_quantity: int | None
