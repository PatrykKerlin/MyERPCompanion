from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import date

from pydantic import model_validator

from schemas.base import BaseStrictSchema, BasePlainSchema, Constraints

if TYPE_CHECKING:
    from .currency_schema import CurrencyPlainSchema


class ExchangeRateStrictSchema(BaseStrictSchema):
    rate: Constraints.PositiveNumeric102
    valid_from: date
    valid_to: date | None

    base_currency_id: Constraints.PositiveInteger
    quote_currency_id: Constraints.PositiveInteger

    @model_validator(mode="after")
    def _validate_data(self) -> ExchangeRateStrictSchema:
        if self.base_currency_id == self.quote_currency_id:
            raise ValueError("base_currency_id and quote_currency_id must be different")

        if self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be greater than or equal to valid_from")

        return self


class ExchangeRatePlainSchema(BasePlainSchema):
    rate: Constraints.PositiveNumeric102
    valid_from: date
    valid_to: date | None

    base_currency: CurrencyPlainSchema
    quote_currency: CurrencyPlainSchema
