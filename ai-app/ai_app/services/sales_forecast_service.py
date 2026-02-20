from __future__ import annotations

import logging
import math
from datetime import date
from typing import Any

import numpy as np
import torch
from repositories.sales_forecast_result_repository import SalesForecastResultRepository
from repositories.sales_prediction_repository import SalesPredictionRepository

logger = logging.getLogger("ai")


class SalesForecastService:
    _aggregation_net = "month_net"
    _aggregation_quantity = "month_quantity"

    def __init__(
        self,
        result_repository: SalesForecastResultRepository,
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
    ) -> (
        tuple[
            torch.Tensor,
            torch.Tensor,
            torch.Tensor,
            list[dict[str, Any]],
        ]
        | None
    ):
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
        period_span = SalesForecastService.__months_between(min_period, max_period)
        if period_span <= 0:
            logger.info(f"Only one unique month in dataset ({min_period}), skipped")
            return None

        item_scale = float(max(int(row["item_id"]) for row in rows))
        customer_scale = float(max(int(row["customer_id"]) for row in rows))
        category_scale = float(max(int(row["category_id"]) for row in rows))
        currency_scale = float(max(int(row["currency_id"]) for row in rows))
        period_scale = float(period_span)

        train_features: list[list[float]] = []
        y_train_values: list[list[float]] = []
        for row in rows:
            item_id = int(row["item_id"])
            customer_id = int(row["customer_id"])
            category_id = int(row["category_id"])
            currency_id = int(row["currency_id"])
            period_index = float(SalesForecastService.__months_between(min_period, row["period_start"])) / period_scale
            month_sin, month_cos = SalesForecastService.__month_cycle_features(row["period_start"])
            discount_ratio = min(max(float(row["discount_ratio"]), 0.0), 0.90)
            train_features.append(
                [
                    float(item_id) / item_scale,
                    float(customer_id) / customer_scale,
                    float(category_id) / category_scale,
                    float(currency_id) / currency_scale,
                    period_index,
                    month_sin,
                    month_cos,
                    discount_ratio,
                ]
            )
            y_train_values.append(
                [
                    float(row["total_net"]),
                    float(row["total_quantity"]),
                ]
            )

        if len(train_features) < 3:
            logger.info(f"Too few training rows ({len(train_features)}), skipped")
            return None

        x_train = torch.tensor(train_features, dtype=torch.float32)
        y_train = torch.tensor(y_train_values, dtype=torch.float32)

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
        predict_features: list[list[float]] = []
        prediction_points: list[dict[str, Any]] = []
        for month_offset in range(1, self._horizon_months + 1):
            predicted_date = SalesForecastService.__add_months(max_period, month_offset)
            period_index = float(SalesForecastService.__months_between(min_period, predicted_date)) / period_scale
            month_sin, month_cos = SalesForecastService.__month_cycle_features(predicted_date)
            for item_id, customer_id, category_id, currency_id in prediction_keys:
                for discount_rate in self._prediction_discount_rates:
                    predict_features.append(
                        [
                            float(item_id) / item_scale,
                            float(customer_id) / customer_scale,
                            float(category_id) / category_scale,
                            float(currency_id) / currency_scale,
                            period_index,
                            month_sin,
                            month_cos,
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

        if not predict_features:
            logger.info("No prediction points generated, skipped")
            return None

        x_predict = torch.tensor(predict_features, dtype=torch.float32)
        logger.info(
            f"Training data ready: train_rows={len(train_features)}, prediction_points={len(prediction_points)}"
        )
        return (
            x_train,
            y_train,
            x_predict,
            prediction_points,
        )

    async def save_forecast_results(
        self,
        run_id: int,
        y_train: torch.Tensor,
        prediction_points: list[dict[str, Any]],
        forecast: np.ndarray,
    ) -> None:
        rows_to_save: list[dict[str, Any]] = []
        for point, values in zip(prediction_points, forecast):
            predicted_net = float(values[0])
            predicted_quantity = float(values[1])
            rows_to_save.append(
                {
                    "run_id": run_id,
                    "item_id": point["item_id"],
                    "customer_id": point["customer_id"],
                    "category_id": point["category_id"],
                    "currency_id": point["currency_id"],
                    "predicted_at": point["predicted_date"],
                    "predicted_value": predicted_net,
                    "samples": int(y_train.shape[0]),
                    "aggregation": SalesForecastService._aggregation_net,
                    "horizon_months": int(point["horizon_months"]),
                    "discount_rate_assumption": float(point["discount_rate"]),
                }
            )
            rows_to_save.append(
                {
                    "run_id": run_id,
                    "item_id": point["item_id"],
                    "customer_id": point["customer_id"],
                    "category_id": point["category_id"],
                    "currency_id": point["currency_id"],
                    "predicted_at": point["predicted_date"],
                    "predicted_value": predicted_quantity,
                    "samples": int(y_train.shape[0]),
                    "aggregation": SalesForecastService._aggregation_quantity,
                    "horizon_months": int(point["horizon_months"]),
                    "discount_rate_assumption": float(point["discount_rate"]),
                }
            )

        await self._result_repository.save_results(rows_to_save)
        logger.info(
            f"Task=sales_forecast completed: saved_results={len(rows_to_save)} "
            f"horizon_months={self._horizon_months} discount_scenarios={self._prediction_discount_rates}"
        )

    @staticmethod
    def __months_between(start: date, end: date) -> int:
        return (end.year - start.year) * 12 + (end.month - start.month)

    @staticmethod
    def __add_months(value: date, months: int) -> date:
        month_zero_based = value.month - 1 + months
        year = value.year + month_zero_based // 12
        month = month_zero_based % 12 + 1
        return date(year, month, 1)

    @staticmethod
    def __month_cycle_features(value: date) -> tuple[float, float]:
        # Encode month as a cyclical signal to capture seasonality.
        angle = (2.0 * math.pi * float(value.month - 1)) / 12.0
        return math.sin(angle), math.cos(angle)
