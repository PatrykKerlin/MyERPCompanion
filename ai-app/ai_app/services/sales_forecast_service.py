from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

from ai_app.ml.feed_forward_model import FeedForwardModel
from ai_app.repositories.task_result_repository import TaskResultRepository
from ai_app.services.data_window_service import DataWindow
from ai_app.services.sales_prediction_service import SalesPredictionService, SalesTrainingBatch

logger = logging.getLogger("ai")


class SalesForecastService:
    _checkpoint_path = Path("/ai_app/.artifacts/sales_forecast_monthly_ffn.pt")
    _max_epochs = 1200
    _min_epochs = 150
    _learning_rate = 0.003
    _weight_decay = 1e-5
    _validation_ratio = 0.2
    _min_validation_rows = 20
    _early_stopping_patience = 80
    _early_stopping_min_delta = 1e-4
    _hidden_dims = (128, 64, 32)
    _hidden_dropout = 0.10

    def __init__(
        self,
        result_repository: TaskResultRepository,
        sales_prediction_service: SalesPredictionService,
        horizon_months: int,
        prediction_discount_rates: list[float],
    ) -> None:
        self._result_repository = result_repository
        self._sales_prediction_service = sales_prediction_service
        self._horizon_months = max(1, horizon_months)
        self._prediction_discount_rates = prediction_discount_rates

    async def run(self, window: DataWindow, task_key: str, run_id: int) -> None:
        if window.start is None or window.end is None:
            logger.info("Task=%s skipped: empty window boundaries", task_key)
            return

        logger.info(
            "Task=%s building monthly training batch for window [%s, %s], horizon=%s, discount_scenarios=%s",
            task_key,
            window.start,
            window.end,
            self._horizon_months,
            self._prediction_discount_rates,
        )
        training_batch = await self._sales_prediction_service.build_training_batch(
            window.start,
            window.end,
            self._horizon_months,
            prediction_discount_rates=self._prediction_discount_rates,
        )
        if training_batch is None:
            logger.info("Task=%s skipped: training batch not available", task_key)
            return

        logger.info(
            "Task=%s training started (train_rows=%s, prediction_points=%s)",
            task_key,
            int(training_batch.y_train.shape[0]),
            len(training_batch.prediction_points),
        )
        model = self._train_model(training_batch)
        forecast = self._predict(model, training_batch.x_predict)
        rows_to_save: list[dict] = []
        for point, value in zip(training_batch.prediction_points, forecast):
            predicted_quantity = float(value)
            horizon = max(1, (point.predicted_date - window.end).days)
            rows_to_save.append(
                {
                    "task_key": task_key,
                    "run_id": run_id,
                    "item_id": point.item_id,
                    "customer_id": point.customer_id,
                    "category_id": point.category_id,
                    "predicted_at": point.predicted_date,
                    "horizon_days": horizon,
                    "risk_level": None,
                    "score": None,
                    "payload": {
                        "predicted_quantity": predicted_quantity,
                        "currency_id": point.currency_id,
                        "samples": int(training_batch.y_train.shape[0]),
                        "aggregation": "month",
                        "horizon_months": point.horizon_months,
                        "discount_rate_assumption": point.discount_rate,
                    },
                }
            )
        await self._result_repository.save_results(rows_to_save)
        logger.info(
            "Task=%s completed: saved_results=%s for horizon_months=%s and discount_scenarios=%s",
            task_key,
            len(rows_to_save),
            self._horizon_months,
            self._prediction_discount_rates,
        )

    def _train_model(self, data: SalesTrainingBatch) -> nn.Module:
        model = FeedForwardModel.for_prediction(
            input_dim=6,
            hidden_dims=SalesForecastService._hidden_dims,
            dropout=SalesForecastService._hidden_dropout,
        )
        self._load_checkpoint_if_exists(model)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=SalesForecastService._learning_rate,
            weight_decay=SalesForecastService._weight_decay,
        )
        loss_fn = nn.MSELoss()
        x_train, y_train, x_val, y_val = SalesForecastService._split_train_validation(data)
        best_state: dict[str, torch.Tensor] | None = None
        best_val_loss = float("inf")
        patience_counter = 0
        epochs_executed = 0
        started_at = time.perf_counter()

        for epoch in range(1, SalesForecastService._max_epochs + 1):
            epochs_executed = epoch
            model.train()
            optimizer.zero_grad()
            preds = model(x_train)
            loss = loss_fn(preds, y_train)
            loss.backward()
            optimizer.step()

            if x_val is None or y_val is None:
                continue

            model.eval()
            with torch.no_grad():
                val_preds = model(x_val)
                val_loss = float(loss_fn(val_preds, y_val).item())

            if val_loss < best_val_loss - SalesForecastService._early_stopping_min_delta:
                best_val_loss = val_loss
                patience_counter = 0
                best_state = {
                    key: value.detach().clone()
                    for key, value in model.state_dict().items()
                }
                continue

            patience_counter += 1
            if (
                epoch >= SalesForecastService._min_epochs
                and patience_counter >= SalesForecastService._early_stopping_patience
            ):
                logger.info(
                    "Early stopping triggered at epoch=%s (best_val_loss=%.6f)",
                    epoch,
                    best_val_loss,
                )
                break

        if best_state is not None:
            model.load_state_dict(best_state)
        self._save_checkpoint(model)
        training_seconds = time.perf_counter() - started_at
        logger.info(
            "Model training finished: epochs=%s duration=%.2fs best_val_loss=%s checkpoint_saved=%s",
            epochs_executed,
            training_seconds,
            f"{best_val_loss:.6f}" if best_val_loss != float("inf") else "n/a",
            self._checkpoint_path,
        )
        return model.eval()

    @staticmethod
    def _predict(model: nn.Module, x_predict: torch.Tensor) -> np.ndarray:
        with torch.no_grad():
            preds = model(x_predict).squeeze(1).numpy()
        return np.maximum(preds, 0.0)

    @staticmethod
    def _split_train_validation(
        data: SalesTrainingBatch,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor | None, torch.Tensor | None]:
        rows = int(data.x_train.shape[0])
        if rows < SalesForecastService._min_validation_rows:
            return data.x_train, data.y_train, None, None

        val_rows = max(1, int(rows * SalesForecastService._validation_ratio))
        if val_rows >= rows:
            return data.x_train, data.y_train, None, None

        split_idx = rows - val_rows
        return (
            data.x_train[:split_idx],
            data.y_train[:split_idx],
            data.x_train[split_idx:],
            data.y_train[split_idx:],
        )

    @classmethod
    def _load_checkpoint_if_exists(cls, model: nn.Module) -> None:
        if not cls._checkpoint_path.exists():
            logger.info("No model checkpoint found at %s, starting from current weights", cls._checkpoint_path)
            return
        checkpoint = torch.load(cls._checkpoint_path, map_location="cpu")
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
        model.load_state_dict(state_dict, strict=True)
        logger.info("Loaded model checkpoint from %s", cls._checkpoint_path)

    @classmethod
    def _save_checkpoint(cls, model: nn.Module) -> None:
        cls._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"state_dict": model.state_dict()}, cls._checkpoint_path)
