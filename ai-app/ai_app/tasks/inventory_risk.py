from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

import numpy as np
import torch
from torch import nn

from ai_app.repositories.prediction_repository import PredictionRepository
from ai_app.repositories.sales_data_repository import SalesDataRepository
from ai_app.tasks.base import TaskBase
from ai_app.services.data_window_service import DataWindow


class InventoryRiskTask(TaskBase):
    key = "inventory_risk"

    async def run(self, window: DataWindow) -> None:
        data_repo = SalesDataRepository(self._engine)
        pred_repo = PredictionRepository(self._engine)
        rows = await data_repo.get_daily_item_sales(window.start, window.end)
        if not rows:
            return

        grouped: dict[int, list[dict[str, object]]] = defaultdict(list)
        item_meta: dict[int, tuple[int, int]] = {}
        for row in rows:
            item_id = row["item_id"]
            grouped[item_id].append(row)
            item_meta[item_id] = (row["stock_quantity"], row["lead_time"])

        today = date.today()
        for item_id, series in grouped.items():
            series.sort(key=lambda r: r["order_date"])
            if len(series) < 3:
                continue
            stock_quantity, lead_time = item_meta.get(item_id, (0, 0))
            if lead_time <= 0:
                continue

            start_day = series[0]["order_date"]
            x, y = self._build_dataset(series, start_day)
            model = self._train_model(x, y)

            horizon = lead_time
            preds = self._forecast(model, start_day, series[-1]["order_date"], horizon)
            predicted_demand = float(max(0.0, np.sum(preds)))

            risk_level = self._classify_risk(predicted_demand, stock_quantity)
            score = predicted_demand - float(stock_quantity)
            await pred_repo.save_prediction(
                task_key=self.key,
                item_id=item_id,
                customer_id=None,
                category_id=None,
                predicted_at=today,
                horizon_days=horizon,
                risk_level=risk_level,
                score=score,
                payload={
                    "predicted_demand": predicted_demand,
                    "stock_quantity": stock_quantity,
                    "lead_time_days": lead_time,
                },
            )

    @staticmethod
    def _build_dataset(series: list[dict[str, object]], start_day: date) -> tuple[torch.Tensor, torch.Tensor]:
        x_vals: list[list[float]] = []
        y_vals: list[float] = []
        for row in series:
            order_date = row["order_date"]
            quantity = row["quantity"]
            has_discount = 1.0 if row["has_discount"] else 0.0
            day_index = (order_date - start_day).days
            x_vals.append([float(day_index), has_discount])
            y_vals.append(float(quantity))
        x = torch.tensor(x_vals, dtype=torch.float32)
        y = torch.tensor(y_vals, dtype=torch.float32).unsqueeze(1)
        if len(x_vals) > 0:
            x[:, 0] = x[:, 0] / max(1.0, float(x[:, 0].max()))
        return x, y

    @staticmethod
    def _train_model(x: torch.Tensor, y: torch.Tensor) -> nn.Module:
        model = nn.Sequential(
            nn.Linear(2, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        loss_fn = nn.MSELoss()
        model.train()
        for _ in range(200):
            optimizer.zero_grad()
            preds = model(x)
            loss = loss_fn(preds, y)
            loss.backward()
            optimizer.step()
        return model.eval()

    @staticmethod
    def _forecast(model: nn.Module, start_day: date, last_day: date, horizon: int) -> np.ndarray:
        future_x: list[list[float]] = []
        last_index = (last_day - start_day).days
        for day_offset in range(1, horizon + 1):
            day_index = last_index + day_offset
            future_x.append([float(day_index), 0.0])
        x = torch.tensor(future_x, dtype=torch.float32)
        if len(future_x) > 0:
            x[:, 0] = x[:, 0] / max(1.0, float(x[:, 0].max()))
        with torch.no_grad():
            preds = model(x).squeeze(1).numpy()
        return np.maximum(preds, 0.0)

    @staticmethod
    def _classify_risk(predicted: float, stock_quantity: int) -> str:
        if stock_quantity <= 0:
            return "high"
        if predicted >= 1.0 * stock_quantity:
            return "high"
        if predicted >= 0.7 * stock_quantity:
            return "medium"
        return "low"
