from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select, update

from database.engine import Engine
from models.ai.ai_task_run import AiTaskRun


class TaskRunRepository:
    _system_user_id = 1

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def create_run(
        self,
        task_key: str,
        started_at: datetime,
        data_range_start: date | None,
        data_range_end: date | None,
    ) -> int:
        async with self._engine.get_session() as session:
            run = AiTaskRun(
                task_key=task_key,
                status="running",
                started_at=started_at,
                finished_at=None,
                model_version=None,
                data_range_start=data_range_start,
                data_range_end=data_range_end,
                params=None,
                metrics=None,
                created_at=started_at,
                created_by=TaskRunRepository._system_user_id,
            )
            session.add(run)
            await session.commit()
            await session.refresh(run)
            return run.id

    async def finish_run(self, run_id: int, status: str, finished_at: datetime) -> None:
        async with self._engine.get_session() as session:
            await session.execute(
                update(AiTaskRun)
                .where(AiTaskRun.id == run_id)
                .values(status=status, finished_at=finished_at)
            )
            await session.commit()

    async def get_last_successful_range(self, task_key: str) -> tuple[date | None, date | None]:
        async with self._engine.get_session() as session:
            result = await session.execute(
                select(AiTaskRun)
                .where(AiTaskRun.task_key == task_key, AiTaskRun.status == "success")
                .order_by(AiTaskRun.finished_at.desc())
                .limit(1)
            )
            run = result.scalar_one_or_none()
            if not run:
                return None, None
            return run.data_range_start, run.data_range_end
