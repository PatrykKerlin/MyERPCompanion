from __future__ import annotations

from abc import ABC, abstractmethod

from utils.data_window import DataWindow


class TaskBase(ABC):
    key: str

    @abstractmethod
    async def run(self, window: DataWindow, run_id: int) -> None: ...
