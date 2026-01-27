from __future__ import annotations

from ai_app.tasks.base import TaskBase
from ai_app.services.data_window_service import DataWindow


class PromoEffectsTask(TaskBase):
    key = "promo_effects"

    async def run(self, window: DataWindow) -> None:
        # TODO: implement promo uplift modeling.
        _ = window
