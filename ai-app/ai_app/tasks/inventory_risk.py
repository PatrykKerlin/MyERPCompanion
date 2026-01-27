from __future__ import annotations

from ai_app.tasks.base import TaskBase
from ai_app.services.data_window_service import DataWindow


class InventoryRiskTask(TaskBase):
    key = "inventory_risk"

    async def run(self, window: DataWindow) -> None:
        # TODO: implement training + risk scoring.
        _ = window
