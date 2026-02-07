from __future__ import annotations

from database.engine import Engine

from ai_app.services.data_window_service import DataWindow
from ai_app.tasks.base import TaskBase
from ai_app.use_cases.sales_forecast_use_case import SalesForecastUseCase


class SalesForecastTask(TaskBase):
    key = "sales_forecast"

    def __init__(self, engine: Engine, use_case: SalesForecastUseCase) -> None:
        super().__init__(engine)
        self._use_case = use_case

    async def run(self, window: DataWindow, run_id: int) -> None:
        await self._use_case.execute(window, self.key, run_id)
