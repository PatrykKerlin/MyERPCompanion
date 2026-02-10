from __future__ import annotations

from datetime import date, datetime

from pydantic import model_validator

from schemas.base.base_schema import BaseSchema
from schemas.validation.constraints import Constraints


class SalesForecastReportFilterSchema(BaseSchema):
    date_from: date | None = None
    date_to: date | None = None
    item_id: Constraints.PositiveIntegerOptional = None
    customer_id: Constraints.PositiveIntegerOptional = None
    category_id: Constraints.PositiveIntegerOptional = None
    currency_id: Constraints.PositiveIntegerOptional = None
    discount_from: Constraints.PercentFloatOptional = None
    discount_to: Constraints.PercentFloatOptional = None

    @model_validator(mode="after")
    def _validate_date_range(self) -> "SalesForecastReportFilterSchema":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be less than or equal to date_to")
        if self.discount_from is not None and self.discount_to is not None and self.discount_from > self.discount_to:
            raise ValueError("discount_from must be less than or equal to discount_to")
        return self


class SalesForecastReportRowSchema(BaseSchema):
    result_id: int
    run_id: int
    predicted_at: date

    customer_id: int
    customer_name: str

    item_id: int
    item_name: str

    category_id: int
    category_name: str

    currency_id: int
    currency_code: str

    predicted_net: float
    predicted_gross: float
    discount_rate_assumption: float
    horizon_months: int


class SalesForecastReportTotalsSchema(BaseSchema):
    rows_count: int = 0
    periods_count: int = 0
    total_predicted_net: float = 0
    total_predicted_gross: float = 0
    discount_steps: list[float] = []
    latest_run_id: int | None = None
    latest_run_finished_at: datetime | None = None


class SalesForecastReportResponseSchema(BaseSchema):
    items: list[SalesForecastReportRowSchema]
    totals: SalesForecastReportTotalsSchema
