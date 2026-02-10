from __future__ import annotations

import logging

from ml.sales_forecast_trainer import SalesForecastTrainer
from services.data_window_service import DataWindow
from services.sales_forecast_service import SalesForecastService
from tasks.base.base import TaskBase

logger = logging.getLogger("ai")


class SalesForecastTask(TaskBase):
    key = "sales_forecast"

    def __init__(
        self,
        service: SalesForecastService,
        trainer: SalesForecastTrainer,
    ) -> None:
        self._service = service
        self._trainer = trainer

    async def run(self, window: DataWindow, run_id: int) -> None:
        if window.start is None or window.end is None:
            logger.info(f"Task={self.key} skipped: empty window boundaries")
            return

        training_data = await self._service.build_training_data(window.start, window.end)
        if training_data is None:
            logger.info(f"Task={self.key} skipped: training data not available")
            return

        (
            x_train,
            y_train,
            x_predict,
            prediction_points,
        ) = training_data
        logger.info(
            f"Task={self.key} training started (train_rows={int(y_train.shape[0])}, "
            f"prediction_points={len(prediction_points)})"
        )
        model = self._trainer.train(
            x_train,
            y_train,
        )
        forecast = self._trainer.predict(model, x_predict)
        await self._service.save_forecast_results(
            run_id=run_id,
            y_train=y_train,
            prediction_points=prediction_points,
            forecast=forecast,
        )
