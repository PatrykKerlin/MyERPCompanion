from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Any

import torch

from ai_app.repositories.sales_prediction_repository import SalesPredictionRepository

logger = logging.getLogger("ai")


@dataclass(frozen=True)
class SalesPredictionPoint:
    item_id: int
    customer_id: int | None
    category_id: int | None
    currency_id: int | None
    predicted_date: date
    discount_rate: float
    horizon_months: int


@dataclass(frozen=True)
class SalesTrainingBatch:
    x_train: torch.Tensor
    y_train: torch.Tensor
    x_predict: torch.Tensor
    prediction_points: list[SalesPredictionPoint]


class SalesPredictionService:
    def __init__(self, repository: SalesPredictionRepository) -> None:
        self._repository = repository

    async def build_training_batch(
        self,
        start_date: date,
        end_date: date,
        horizon_months: int,
        prediction_discount_rates: list[float],
    ) -> SalesTrainingBatch | None:
        logger.info(
            "Building monthly training batch for range [%s, %s], horizon_months=%s, discount_scenarios=%s",
            start_date,
            end_date,
            horizon_months,
            prediction_discount_rates,
        )
        rows = await self._repository.get_monthly_sales(start_date, end_date)
        if not rows:
            logger.info("No sales rows for selected range, batch skipped")
            return None

        rows.sort(key=lambda row: row["period_start"])
        min_period = rows[0]["period_start"]
        max_period = rows[-1]["period_start"]
        period_span = SalesPredictionService._months_between(min_period, max_period)
        if period_span <= 0:
            logger.info("Only one unique month in dataset (%s), batch skipped", min_period)
            return None

        item_scale = max(1, max(int(row["item_id"]) for row in rows))
        customer_scale = max(1, max(int(row["customer_id"] or 0) for row in rows))
        category_scale = max(1, max(int(row["category_id"] or 0) for row in rows))
        currency_scale = max(1, max(int(row["currency_id"] or 0) for row in rows))
        period_scale = float(period_span)

        x_train_values: list[list[float]] = []
        y_train_values: list[float] = []
        for row in rows:
            period_index = float(SalesPredictionService._months_between(min_period, row["period_start"])) / period_scale
            discount_ratio = min(max(float(row["discount_ratio"] or 0.0), 0.0), 0.90)
            x_train_values.append(
                [
                    period_index,
                    float(row["item_id"]) / item_scale,
                    float(row["customer_id"] or 0) / customer_scale,
                    float(row["category_id"] or 0) / category_scale,
                    float(row["currency_id"] or 0) / currency_scale,
                    discount_ratio,
                ]
            )
            y_train_values.append(float(row["quantity"]))

        if len(x_train_values) < 3:
            logger.info("Too few training rows (%s), batch skipped", len(x_train_values))
            return None

        x_train = torch.tensor(x_train_values, dtype=torch.float32)
        y_train = torch.tensor(y_train_values, dtype=torch.float32).unsqueeze(1)

        latest_by_key: dict[tuple[int, int | None, int | None, int | None], dict[str, Any]] = {}
        for row in rows:
            key = (
                int(row["item_id"]),
                int(row["customer_id"]) if row["customer_id"] is not None else None,
                int(row["category_id"]) if row["category_id"] is not None else None,
                int(row["currency_id"]) if row["currency_id"] is not None else None,
            )
            latest_by_key[key] = row
        prediction_keys = list(latest_by_key.keys())

        x_predict_values: list[list[float]] = []
        prediction_points: list[SalesPredictionPoint] = []
        for month_offset in range(1, horizon_months + 1):
            predicted_date = SalesPredictionService._add_months(max_period, month_offset)
            period_index = float(SalesPredictionService._months_between(min_period, predicted_date)) / period_scale
            for key in prediction_keys:
                item_id, customer_id, category_id, currency_id = key
                for discount_rate in prediction_discount_rates:
                    x_predict_values.append(
                        [
                            period_index,
                            float(item_id) / item_scale,
                            float(customer_id or 0) / customer_scale,
                            float(category_id or 0) / category_scale,
                            float(currency_id or 0) / currency_scale,
                            float(discount_rate),
                        ]
                    )
                    prediction_points.append(
                        SalesPredictionPoint(
                            item_id=item_id,
                            customer_id=customer_id,
                            category_id=category_id,
                            currency_id=currency_id,
                            predicted_date=predicted_date,
                            discount_rate=float(discount_rate),
                            horizon_months=month_offset,
                        )
                    )

        if not x_predict_values:
            logger.info("No prediction points generated, batch skipped")
            return None

        x_predict = torch.tensor(x_predict_values, dtype=torch.float32)
        logger.info(
            "Monthly training batch ready: train_rows=%s prediction_points=%s",
            len(x_train_values),
            len(prediction_points),
        )
        return SalesTrainingBatch(
            x_train=x_train,
            y_train=y_train,
            x_predict=x_predict,
            prediction_points=prediction_points,
        )

    @staticmethod
    def _months_between(start: date, end: date) -> int:
        return (end.year - start.year) * 12 + (end.month - start.month)

    @staticmethod
    def _add_months(value: date, months: int) -> date:
        month_zero_based = value.month - 1 + months
        year = value.year + month_zero_based // 12
        month = month_zero_based % 12 + 1
        return date(year, month, 1)
