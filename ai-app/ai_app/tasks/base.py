from __future__ import annotations

from abc import ABC, abstractmethod

from database.engine import Engine
from ai_app.services.data_window_service import DataWindow


class TaskBase(ABC):
    key: str

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @abstractmethod
    async def run(self, window: DataWindow) -> None:
        raise NotImplementedError
