from __future__ import annotations

from datetime import date

from pydantic import model_validator
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.validation.constraints import Constraints


class ExchangeRateStrictSchema(BaseStrictSchema):
    rate: Constraints.PositiveNumeric_10_2
    valid_from: date
    valid_to: date | None

    base_currency_id: Constraints.PositiveInteger
    quote_currency_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def _validate_data(self) -> ExchangeRateStrictSchema:
        if self.base_currency_id == self.quote_currency_id:
            raise ValueError("Base currency and quote currency must be different.")

        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("'Valid to' must be greater than or equal to 'Valid from'.")

        return self


class ExchangeRatePlainSchema(BasePlainSchema):
    rate: Constraints.PositiveNumeric_10_2
    valid_from: date
    valid_to: date | None

    base_currency_id: int
    quote_currency_id: int
