from __future__ import annotations

from ai_app.services.data_window_service import DataWindow
from ai_app.services.sales_forecast_service import SalesForecastService


class SalesForecastUseCase:
    def __init__(self, service: SalesForecastService) -> None:
        self._service = service

    async def execute(self, window: DataWindow, task_key: str, run_id: int) -> None:
        await self._service.run(window, task_key, run_id)
