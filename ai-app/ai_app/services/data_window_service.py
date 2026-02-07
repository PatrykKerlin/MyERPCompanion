from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from ai_app.repositories.order_repository import OrderRepository
from ai_app.repositories.task_run_repository import TaskRunRepository

logger = logging.getLogger("ai")


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
            logger.info("Task=%s has no successful history, min start=%s", task_key, start)
        else:
            start = last_end + timedelta(days=1)
            logger.info("Task=%s last successful end=%s, next start=%s", task_key, last_end, start)
        if start is None:
            logger.info("Task=%s no orders found, cannot build data window", task_key)
            return None
        end = await self._orders.get_max_order_date(start)
        if end is None:
            logger.info("Task=%s no new orders for start=%s", task_key, start)
            return None
        logger.info("Task=%s data window resolved to [%s, %s]", task_key, start, end)
        return DataWindow(start=start, end=end)
