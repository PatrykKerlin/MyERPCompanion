import asyncio
import importlib
import logging
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ai_app.config.settings import Settings
from database.engine import Engine
from ai_app.repositories.order_repository import OrderRepository
from ai_app.repositories.sales_prediction_repository import SalesPredictionRepository
from ai_app.repositories.task_result_repository import TaskResultRepository
from ai_app.repositories.task_run_repository import TaskRunRepository
from ai_app.services.data_window_service import DataWindowService
from ai_app.services.sales_forecast_service import SalesForecastService
from ai_app.services.sales_prediction_service import SalesPredictionService
from ai_app.tasks.sales_forecast import SalesForecastTask
from ai_app.use_cases.sales_forecast_use_case import SalesForecastUseCase

logger = logging.getLogger("ai")


def load_all_models() -> None:
    for model_path in ("models.ai", "models.business.hr", "models.business.logistic", "models.business.trade", "models.core"):
        importlib.import_module(model_path)
    logger.info("All SQLAlchemy models loaded")


class TaskOrchestrator:
    def __init__(
        self,
        engine: Engine,
        data_window: DataWindowService,
        runs: TaskRunRepository,
        sales_forecast_use_case: SalesForecastUseCase,
    ) -> None:
        self._data_window = data_window
        self._runs = runs
        self._tasks = [
            SalesForecastTask(engine, sales_forecast_use_case),
        ]

    async def run_daily(self) -> None:
        logger.info("Starting run_daily cycle")
        for task in self._tasks:
            logger.info("Resolving data window for task=%s", task.key)
            window = await self._data_window.resolve(task.key)
            if not window:
                logger.info("Skipping task=%s, no data window", task.key)
                continue
            logger.info(
                "Task=%s window resolved: start=%s end=%s",
                task.key,
                window.start,
                window.end,
            )
            started_at = datetime.now(UTC)
            run_id = await self._runs.create_run(
                task_key=task.key,
                started_at=started_at,
                data_range_start=window.start,
                data_range_end=window.end,
            )
            try:
                logger.info("Task=%s run started, run_id=%s", task.key, run_id)
                await task.run(window, run_id)
                await self._runs.finish_run(run_id, "success", datetime.now(UTC))
                logger.info("Task=%s run finished successfully, run_id=%s", task.key, run_id)
            except Exception:
                await self._runs.finish_run(run_id, "failed", datetime.now(UTC))
                logger.exception("Task=%s run failed, run_id=%s", task.key, run_id)
                raise
        logger.info("Finished run_daily cycle")


class AiApp:
    def __init__(self) -> None:
        self._settings = Settings()  # type: ignore
        self._engine = Engine(self._settings)
        self._orders = OrderRepository(self._engine)
        self._results = TaskResultRepository(self._engine)
        self._sales_prediction_data = SalesPredictionRepository(self._engine)
        self._runs = TaskRunRepository(self._engine)
        self._sales_prediction_service = SalesPredictionService(self._sales_prediction_data)
        self._sales_forecast_service = SalesForecastService(
            self._results,
            self._sales_prediction_service,
            horizon_months=self._settings.FORECAST_HORIZON_MONTHS,
            prediction_discount_rates=self._settings.FORECAST_DISCOUNT_SCENARIOS,
        )
        self._sales_forecast_use_case = SalesForecastUseCase(self._sales_forecast_service)
        self._windows = DataWindowService(self._orders, self._runs)
        self._orchestrator = TaskOrchestrator(
            self._engine,
            self._windows,
            self._runs,
            self._sales_forecast_use_case,
        )

    async def run_daily(self) -> None:
        await self._orchestrator.run_daily()

    async def run(self) -> None:
        logger.info("Running initial run_daily on startup")
        try:
            await self.run_daily()
        except Exception:
            logger.exception("Initial run_daily failed")

        scheduler = AsyncIOScheduler(timezone=self._settings.TIMEZONE)
        scheduler.add_job(
            self.run_daily,
            CronTrigger(hour=self._settings.TRAIN_HOUR_UTC, minute=self._settings.TRAIN_MINUTE_UTC),
        )
        scheduler.start()
        logger.info(
            "Scheduler started: next daily run at %02d:%02d (%s)",
            self._settings.TRAIN_HOUR_UTC,
            self._settings.TRAIN_MINUTE_UTC,
            self._settings.TIMEZONE,
        )
        try:
            await asyncio.Event().wait()
        finally:
            scheduler.shutdown(wait=False)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    load_all_models()
    app = AiApp()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
