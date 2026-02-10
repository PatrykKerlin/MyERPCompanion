from __future__ import annotations

import logging
import math
import time
from pathlib import Path
from typing import cast

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from ml.feed_forward_model import FeedForwardModel

logger = logging.getLogger("ai")


class SalesForecastTrainer:
    _checkpoint_path = Path("/ai_app/.artifacts/sales_forecast.pt")
    _max_epochs = 1200
    _min_epochs = 150
    _learning_rate = 0.003
    _weight_decay = 1e-5
    _validation_ratio = 0.2
    _min_validation_rows = 20
    _early_stopping_patience = 80
    _early_stopping_min_delta = 1e-4
    _batch_size = 64

    def train(
        self,
        x_train: torch.Tensor,
        y_train: torch.Tensor,
    ) -> nn.Module:
        model = FeedForwardModel(
            input_dim=int(x_train.shape[1]),
            output_dim=2,
        )
        self._load_checkpoint_if_exists(model)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=SalesForecastTrainer._learning_rate,
            weight_decay=SalesForecastTrainer._weight_decay,
        )
        loss_fn = nn.MSELoss()
        train_x, train_y, val_x, val_y = SalesForecastTrainer._split_train_validation(
            x_train,
            y_train,
        )
        train_loader = SalesForecastTrainer._build_train_loader(train_x, train_y)
        best_state: dict[str, torch.Tensor] | None = None
        best_val_loss = math.inf
        patience_counter = 0
        epochs_executed = 0
        started_at = time.perf_counter()

        for epoch in range(1, SalesForecastTrainer._max_epochs + 1):
            epochs_executed = epoch
            model.train()
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                preds = model(batch_x)
                loss = loss_fn(preds, batch_y)
                loss.backward()
                optimizer.step()

            if val_x is None or val_y is None:
                continue

            model.eval()
            with torch.no_grad():
                val_preds = model(val_x)
                val_loss = float(loss_fn(val_preds, val_y).item())

            if val_loss < best_val_loss - SalesForecastTrainer._early_stopping_min_delta:
                best_val_loss = val_loss
                patience_counter = 0
                best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
                continue

            patience_counter += 1
            if (
                epoch >= SalesForecastTrainer._min_epochs
                and patience_counter >= SalesForecastTrainer._early_stopping_patience
            ):
                logger.info(f"Early stopping triggered at epoch={epoch} (best_val_loss={best_val_loss:.6f})")
                break

        if best_state is not None:
            model.load_state_dict(best_state)
        self._save_checkpoint(model)
        training_seconds = time.perf_counter() - started_at
        best_val_loss_text = f"{best_val_loss:.6f}" if best_val_loss != math.inf else "n/a"
        logger.info(
            f"Model training finished: epochs={epochs_executed} duration={training_seconds:.2f}s "
            f"best_val_loss={best_val_loss_text} checkpoint_saved={self._checkpoint_path}"
        )
        return model.eval()

    @staticmethod
    def predict(
        model: nn.Module,
        x_predict: torch.Tensor,
    ) -> np.ndarray:
        with torch.no_grad():
            preds = model(x_predict).numpy()
        return np.maximum(preds, 0.0)

    @staticmethod
    def _build_train_loader(
        train_x: torch.Tensor,
        train_y: torch.Tensor,
    ) -> DataLoader[tuple[torch.Tensor, torch.Tensor]]:
        dataset = TensorDataset(train_x, train_y)
        return cast(
            DataLoader[tuple[torch.Tensor, torch.Tensor]],
            DataLoader(
                dataset,
                batch_size=SalesForecastTrainer._batch_size,
                shuffle=True,
                drop_last=False,
            ),
        )

    @staticmethod
    def _split_train_validation(
        x_train: torch.Tensor,
        y_train: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor | None,
        torch.Tensor | None,
    ]:
        rows = int(x_train.shape[0])
        if rows < SalesForecastTrainer._min_validation_rows:
            return x_train, y_train, None, None

        val_rows = max(1, int(rows * SalesForecastTrainer._validation_ratio))
        if val_rows >= rows:
            return x_train, y_train, None, None

        split_idx = rows - val_rows
        return (
            x_train[:split_idx],
            y_train[:split_idx],
            x_train[split_idx:],
            y_train[split_idx:],
        )

    @classmethod
    def _load_checkpoint_if_exists(cls, model: nn.Module) -> None:
        if not cls._checkpoint_path.exists():
            logger.info(f"No model checkpoint found at {cls._checkpoint_path}, starting from current weights")
            return
        checkpoint = torch.load(cls._checkpoint_path, map_location="cpu")
        if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
        model.load_state_dict(state_dict, strict=True)

    @classmethod
    def _save_checkpoint(cls, model: nn.Module) -> None:
        cls._checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"state_dict": model.state_dict()}, cls._checkpoint_path)
