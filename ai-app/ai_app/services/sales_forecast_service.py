from __future__ import annotations

import logging
from datetime import date
from collections.abc import Iterable
from typing import Any

import numpy as np
import torch

from repositories.sales_prediction_repository import SalesPredictionRepository
from repositories.sales_forecast_result_repository import SalesForecastResultRepository

logger = logging.getLogger("ai")


class SalesForecastService:
    _aggregation_net = "month_net"
    _aggregation_gross = "month_gross"

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
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        list[dict[str, Any]],
        int,
        int,
        int,
        int,
    ] | None:
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

        item_to_index = SalesForecastService.__build_embedding_index(int(row["item_id"]) for row in rows)
        customer_to_index = SalesForecastService.__build_embedding_index(int(row["customer_id"]) for row in rows)
        category_to_index = SalesForecastService.__build_embedding_index(int(row["category_id"]) for row in rows)
        currency_to_index = SalesForecastService.__build_embedding_index(int(row["currency_id"]) for row in rows)
        period_scale = float(period_span)

        categorical_train_values: list[list[int]] = []
        numerical_train_values: list[list[float]] = []
        y_train_values: list[list[float]] = []
        for row in rows:
            item_id = int(row["item_id"])
            customer_id = int(row["customer_id"])
            category_id = int(row["category_id"])
            currency_id = int(row["currency_id"])
            period_index = float(SalesForecastService._months_between(min_period, row["period_start"])) / period_scale
            discount_ratio = min(max(float(row["discount_ratio"]), 0.0), 0.90)
            categorical_train_values.append(
                [
                    item_to_index[item_id],
                    customer_to_index[customer_id],
                    category_to_index[category_id],
                    currency_to_index[currency_id],
                ]
            )
            numerical_train_values.append([period_index, discount_ratio])
            y_train_values.append(
                [
                    float(row["total_net"]),
                    float(row["total_gross"]),
                ]
            )

        if len(categorical_train_values) < 3:
            logger.info(f"Too few training rows ({len(categorical_train_values)}), skipped")
            return None

        categorical_train = torch.tensor(categorical_train_values, dtype=torch.int64)
        numerical_train = torch.tensor(numerical_train_values, dtype=torch.float32)
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
        categorical_predict_values: list[list[int]] = []
        numerical_predict_values: list[list[float]] = []
        prediction_points: list[dict[str, Any]] = []
        for month_offset in range(1, self._horizon_months + 1):
            predicted_date = SalesForecastService._add_months(max_period, month_offset)
            period_index = float(SalesForecastService._months_between(min_period, predicted_date)) / period_scale
            for item_id, customer_id, category_id, currency_id in prediction_keys:
                for discount_rate in self._prediction_discount_rates:
                    categorical_predict_values.append(
                        [
                            item_to_index[item_id],
                            customer_to_index[customer_id],
                            category_to_index[category_id],
                            currency_to_index[currency_id],
                        ]
                    )
                    numerical_predict_values.append([period_index, float(discount_rate)])
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

        if not categorical_predict_values:
            logger.info("No prediction points generated, skipped")
            return None

        categorical_predict = torch.tensor(categorical_predict_values, dtype=torch.int64)
        numerical_predict = torch.tensor(numerical_predict_values, dtype=torch.float32)
        logger.info(
            f"Training data ready: train_rows={len(categorical_train_values)} "
            f"prediction_points={len(prediction_points)}"
        )
        return (
            categorical_train,
            numerical_train,
            y_train,
            categorical_predict,
            numerical_predict,
            prediction_points,
            len(item_to_index),
            len(customer_to_index),
            len(category_to_index),
            len(currency_to_index),
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
            predicted_gross = float(values[1])
            rows_to_save.append(
                {
                    "run_id": run_id,
                    "item_id": point["item_id"],
                    "customer_id": point["customer_id"],
                    "category_id": point["category_id"],
                    "currency_id": point["currency_id"],
                    "predicted_at": point["predicted_date"],
                    "predicted_quantity": predicted_net,
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
                    "predicted_quantity": predicted_gross,
                    "samples": int(y_train.shape[0]),
                    "aggregation": SalesForecastService._aggregation_gross,
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
    def _months_between(start: date, end: date) -> int:
        return (end.year - start.year) * 12 + (end.month - start.month)

    @staticmethod
    def _add_months(value: date, months: int) -> date:
        month_zero_based = value.month - 1 + months
        year = value.year + month_zero_based // 12
        month = month_zero_based % 12 + 1
        return date(year, month, 1)

    @staticmethod
    def __build_embedding_index(values: Iterable[int]) -> dict[int, int]:
        unique_values = sorted(set(int(value) for value in values))
        return {value: index for index, value in enumerate(unique_values, start=1)}
