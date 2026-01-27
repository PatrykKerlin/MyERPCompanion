from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ai_app.db.repositories.order_repository import OrderRepository
from ai_app.db.repositories.task_run_repository import TaskRunRepository


@dataclass(frozen=True)
class DataWindow:
    start: date | None
    end: date | None


class DataWindowService:
    def __init__(self, orders: OrderRepository, runs: TaskRunRepository) -> None:
        self._orders = orders
        self._runs = runs

    async def resolve(self, task_key: str) -> DataWindow | None:
        _, last_end = await self._runs.get_last_successful_range(task_key)
        if last_end is None:
            start = await self._orders.get_min_order_date()
        else:
            start = last_end + timedelta(days=1)
        if start is None:
            return None
        end = await self._orders.get_max_order_date(start)
        if end is None:
            return None
        return DataWindow(start=start, end=end)
