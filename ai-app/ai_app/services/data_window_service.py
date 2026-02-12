from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, timedelta

from repositories.order_repository import OrderRepository
from repositories.task_run_repository import TaskRunRepository

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
            logger.info(f"Task={task_key} has no successful history, min start={start}")
        else:
            start = last_end + timedelta(days=1)
            logger.info(f"Task={task_key} last successful end={last_end}, next start={start}")
        if start is None:
            logger.info(f"Task={task_key} no orders found, cannot build data window")
            return None
        end = await self._orders.get_max_order_date(start)
        if end is None:
            logger.info(f"Task={task_key} no new orders for start={start}")
            return None
        logger.info(f"Task={task_key} data window resolved to [{start}, {end}]")
        return DataWindow(start=start, end=end)
