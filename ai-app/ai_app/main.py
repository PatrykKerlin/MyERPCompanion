import asyncio
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ai_app.config.settings import Settings
from database.engine import Engine
from ai_app.repositories.order_repository import OrderRepository
from ai_app.repositories.task_run_repository import TaskRunRepository
from ai_app.services.data_window_service import DataWindowService
from ai_app.tasks.inventory_risk import InventoryRiskTask
from ai_app.tasks.promo_effects import PromoEffectsTask
from ai_app.tasks.sales_forecast import SalesForecastTask


class TaskOrchestrator:
    def __init__(self, data_window: DataWindowService, runs: TaskRunRepository) -> None:
        self._data_window = data_window
        self._runs = runs
        self._tasks = [
            InventoryRiskTask(),
            SalesForecastTask(),
            PromoEffectsTask(),
        ]

    async def run_daily(self) -> None:
        for task in self._tasks:
            window = await self._data_window.resolve(task.key)
            if not window:
                continue
            started_at = datetime.now(UTC)
            run_id = await self._runs.create_run(
                task_key=task.key,
                started_at=started_at,
                data_range_start=window.start,
                data_range_end=window.end,
            )
            try:
                await task.run(window)
                await self._runs.finish_run(run_id, "success", datetime.now(UTC))
            except Exception:
                await self._runs.finish_run(run_id, "failed", datetime.now(UTC))
                raise


class AiApp:
    def __init__(self) -> None:
        self._settings = Settings()  # type: ignore
        self._engine = Engine(self._settings)
        self._orders = OrderRepository(self._engine)
        self._runs = TaskRunRepository(self._engine)
        self._windows = DataWindowService(self._orders, self._runs)
        self._orchestrator = TaskOrchestrator(self._windows, self._runs)

    async def run_daily(self) -> None:
        await self._orchestrator.run_daily()

    def run(self) -> None:
        scheduler = AsyncIOScheduler(timezone=self._settings.TIMEZONE)
        scheduler.add_job(
            self.run_daily,
            CronTrigger(hour=self._settings.TRAIN_HOUR_UTC, minute=self._settings.TRAIN_MINUTE_UTC),
        )
        scheduler.start()
        asyncio.get_event_loop().run_forever()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    app = AiApp()
    app.run()


if __name__ == "__main__":
    main()
