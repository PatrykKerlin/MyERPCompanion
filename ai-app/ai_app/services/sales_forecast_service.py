from __future__ import annotations

import logging
from datetime import date
from typing import Any

import numpy as np
import torch

from repositories.sales_prediction_repository import SalesPredictionRepository
from repositories.task_result_repository import TaskResultRepository

logger = logging.getLogger("ai")


class SalesForecastService:
    def __init__(
        self,
        result_repository: TaskResultRepository,
        prediction_repository: SalesPredictionRepository,
        horizon_months: int,
        prediction_discount_rates: list[float],
    ) -> None:
        self._result_repository = result_repository
        self._prediction_repository = prediction_repository
        self._horizon_months = max(1, horizon_months)
        self._prediction_discount_rates = prediction_discount_rates

    async def build_training_data(
        self,
        start_date: date,
        end_date: date,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, list[dict[str, Any]]] | None:
        logger.info(
            f"Building monthly training data for range [{start_date}, {end_date}], "
            f"horizon_months={self._horizon_months}, discount_scenarios={self._prediction_discount_rates}"
        )
        rows = await self._prediction_repository.get_monthly_sales(start_date, end_date)
        if not rows:
            logger.info("No sales rows for selected range, skipped")
            return None

        rows.sort(key=lambda row: row["period_start"])
        min_period = rows[0]["period_start"]
        max_period = rows[-1]["period_start"]
        period_span = SalesForecastService._months_between(min_period, max_period)
        if period_span <= 0:
            logger.info(f"Only one unique month in dataset ({min_period}), skipped")
            return None

        item_scale = max(1, max(int(row["item_id"]) for row in rows))
        customer_scale = max(1, max(int(row["customer_id"]) for row in rows))
        category_scale = max(1, max(int(row["category_id"]) for row in rows))
        currency_scale = max(1, max(int(row["currency_id"]) for row in rows))
        period_scale = float(period_span)

        x_train_values: list[list[float]] = []
        y_train_values: list[float] = []
        for row in rows:
            period_index = float(SalesForecastService._months_between(min_period, row["period_start"])) / period_scale
            discount_ratio = min(max(float(row["discount_ratio"]), 0.0), 0.90)
            x_train_values.append(
                [
                    period_index,
                    float(row["item_id"]) / item_scale,
                    float(row["customer_id"]) / customer_scale,
                    float(row["category_id"]) / category_scale,
                    float(row["currency_id"]) / currency_scale,
                    discount_ratio,
                ]
            )
            y_train_values.append(float(row["quantity"]))

        if len(x_train_values) < 3:
            logger.info(f"Too few training rows ({len(x_train_values)}), skipped")
            return None

        x_train = torch.tensor(x_train_values, dtype=torch.float32)
        y_train = torch.tensor(y_train_values, dtype=torch.float32).unsqueeze(1)

        prediction_keys = list(
            dict.fromkeys(
                (
                    int(row["item_id"]),
                    int(row["customer_id"]),
                    int(row["category_id"]),
                    int(row["currency_id"]),
                )
                for row in rows
            )
        )
        x_predict_values: list[list[float]] = []
        prediction_points: list[dict[str, Any]] = []
        for month_offset in range(1, self._horizon_months + 1):
            predicted_date = SalesForecastService._add_months(max_period, month_offset)
            period_index = float(SalesForecastService._months_between(min_period, predicted_date)) / period_scale
            for item_id, customer_id, category_id, currency_id in prediction_keys:
                for discount_rate in self._prediction_discount_rates:
                    x_predict_values.append(
                        [
                            period_index,
                            float(item_id) / item_scale,
                            float(customer_id) / customer_scale,
                            float(category_id) / category_scale,
                            float(currency_id) / currency_scale,
                            float(discount_rate),
                        ]
                    )
                    prediction_points.append(
                        {
                            "item_id": item_id,
                            "customer_id": customer_id,
                            "category_id": category_id,
                            "currency_id": currency_id,
                            "predicted_date": predicted_date,
                            "discount_rate": float(discount_rate),
                            "horizon_months": month_offset,
                        }
                    )

        if not x_predict_values:
            logger.info("No prediction points generated, skipped")
            return None

        x_predict = torch.tensor(x_predict_values, dtype=torch.float32)
        logger.info(
            f"Training data ready: train_rows={len(x_train_values)} "
            f"prediction_points={len(prediction_points)}"
        )
        return x_train, y_train, x_predict, prediction_points

    async def save_forecast_results(
        self,
        task_key: str,
        run_id: int,
        window_end: date,
        y_train: torch.Tensor,
        prediction_points: list[dict[str, Any]],
        forecast: np.ndarray,
    ) -> None:
        rows_to_save: list[dict[str, Any]] = []
        for point, value in zip(prediction_points, forecast):
            predicted_date = point["predicted_date"]
            horizon = max(1, (predicted_date - window_end).days)
            rows_to_save.append(
                {
                    "task_key": task_key,
                    "run_id": run_id,
                    "item_id": point["item_id"],
                    "customer_id": point["customer_id"],
                    "category_id": point["category_id"],
                    "predicted_at": predicted_date,
                    "horizon_days": horizon,
                    "risk_level": None,
                    "score": None,
                    "payload": {
                        "predicted_quantity": float(value),
                        "currency_id": point["currency_id"],
                        "samples": int(y_train.shape[0]),
                        "aggregation": "month",
                        "horizon_months": point["horizon_months"],
                        "discount_rate_assumption": point["discount_rate"],
                    },
                }
            )

        await self._result_repository.save_results(rows_to_save)
        logger.info(
            f"Task={task_key} completed: saved_results={len(rows_to_save)} "
            f"horizon_months={self._horizon_months} discount_scenarios={self._prediction_discount_rates}"
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
