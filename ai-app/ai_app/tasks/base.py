from __future__ import annotations

from abc import ABC, abstractmethod

from ai_app.services.data_window_service import DataWindow


class TaskBase(ABC):
    key: str

    @abstractmethod
    async def run(self, window: DataWindow) -> None:
        raise NotImplementedError
