import asyncio
import importlib
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import Settings
from database.engine import Engine
from ml.sales_forecast_trainer import SalesForecastTrainer
from repositories.order_repository import OrderRepository
from repositories.sales_prediction_repository import SalesPredictionRepository
from repositories.sales_forecast_result_repository import SalesForecastResultRepository
from repositories.task_run_repository import TaskRunRepository
from services.data_window_service import DataWindowService
from services.sales_forecast_service import SalesForecastService
from tasks.base.base import TaskBase
from tasks.sales_forecast import SalesForecastTask


class TaskOrchestrator:
    def __init__(
        self,
        data_window: DataWindowService,
        runs: TaskRunRepository,
        tasks: list[TaskBase],
        logger: logging.Logger,
    ) -> None:
        self._data_window = data_window
        self._runs = runs
        self._tasks = tasks
        self._logger = logger

    async def run_daily(self) -> None:
        self._logger.info("Starting run_daily cycle")
        for task in self._tasks:
            self._logger.info(f"Resolving data window for task={task.key}")
            window = await self._data_window.resolve(task.key)
            if not window:
                self._logger.info(f"Skipping task={task.key}, no data window")
                continue
            self._logger.info(f"Task={task.key} window resolved: start={window.start} end={window.end}")
            started_at = datetime.now(UTC)
            run_id = await self._runs.create_run(
                task_key=task.key,
                started_at=started_at,
                data_range_start=window.start,
                data_range_end=window.end,
            )
            try:
                self._logger.info(f"Task={task.key} run started, run_id={run_id}")
                await task.run(window, run_id)
                await self._runs.finish_run(run_id, "success", datetime.now(UTC))
                self._logger.info(f"Task={task.key} run finished successfully, run_id={run_id}")
            except Exception:
                await self._runs.finish_run(run_id, "failed", datetime.now(UTC))
                self._logger.exception(f"Task={task.key} run failed, run_id={run_id}")
                raise
        self._logger.info("Finished run_daily cycle")


class AiApp:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._settings = Settings()  # type: ignore
        self._engine = Engine(self._settings)
        self._orders = OrderRepository(self._engine)
        self._sales_forecast_results = SalesForecastResultRepository(self._engine)
        self._sales_prediction_data = SalesPredictionRepository(self._engine)
        self._runs = TaskRunRepository(self._engine)
        self._sales_forecast_service = SalesForecastService(
            self._sales_forecast_results,
            self._sales_prediction_data,
            horizon_months=self._settings.FORECAST_HORIZON_MONTHS,
            prediction_discount_rates=self._settings.FORECAST_DISCOUNT_SCENARIOS,
        )
        self._sales_forecast_trainer = SalesForecastTrainer()
        self._tasks = [
            SalesForecastTask(
                service=self._sales_forecast_service,
                trainer=self._sales_forecast_trainer,
            )
        ]
        self._windows = DataWindowService(self._orders, self._runs)
        self._orchestrator = TaskOrchestrator(
            self._windows,
            self._runs,
            self._tasks,
            self._logger,
        )

    async def run(self) -> None:
        self._logger.info("Running initial run_daily on startup")
        try:
            await self.__run_daily()
        except Exception:
            self._logger.exception("Initial run_daily failed")

        scheduler = AsyncIOScheduler(timezone=self._settings.TIMEZONE)
        scheduler.add_job(
            self.__run_daily,
            CronTrigger(hour=self._settings.TRAIN_HOUR_UTC, minute=self._settings.TRAIN_MINUTE_UTC),
        )
        scheduler.start()
        self._logger.info(
            f"Scheduler started: next daily run at "
            f"{self._settings.TRAIN_HOUR_UTC:02d}:{self._settings.TRAIN_MINUTE_UTC:02d} "
            f"({self._settings.TIMEZONE})"
        )
        try:
            await asyncio.Event().wait()
        finally:
            scheduler.shutdown(wait=False)

    async def __run_daily(self) -> None:
        await self._orchestrator.run_daily()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger = logging.getLogger("ai")

    for model_path in ("models.ai", "models.business.hr", "models.business.logistic", "models.business.trade", "models.core"):
        importlib.import_module(model_path)
    logger.info("All SQLAlchemy models loaded")

    app = AiApp(logger)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
