from __future__ import annotations

from ai_app.tasks.base import TaskBase
from ai_app.services.data_window_service import DataWindow


class SalesForecastTask(TaskBase):
    key = "sales_forecast"

    async def run(self, window: DataWindow) -> None:
        # TODO: implement training + forecasting.
        _ = window
