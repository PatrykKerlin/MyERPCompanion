from __future__ import annotations

from datetime import date
from typing import Any

from database.engine import Engine
from models.ai.ai_task_result import AiTaskResult


class TaskResultRepository:
    _system_user_id = 1
    _insert_chunk_size = 2000

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def save_result(
        self,
        task_key: str,
        run_id: int,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        predicted_at: date,
        horizon_days: int | None,
        risk_level: str | None,
        score: float | None,
        payload: dict | None,
    ) -> None:
        await self.save_results(
            [
                {
                    "task_key": task_key,
                    "run_id": run_id,
                    "item_id": item_id,
                    "customer_id": customer_id,
                    "category_id": category_id,
                    "predicted_at": predicted_at,
                    "horizon_days": horizon_days,
                    "risk_level": risk_level,
                    "score": score,
                    "payload": payload,
                }
            ]
        )

    async def save_results(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return

        async with self._engine.get_session() as session:
            for chunk_start in range(0, len(rows), TaskResultRepository._insert_chunk_size):
                chunk = rows[chunk_start : chunk_start + TaskResultRepository._insert_chunk_size]
                session.add_all(
                    [
                        AiTaskResult(
                            task_key=row["task_key"],
                            run_id=row["run_id"],
                            item_id=row["item_id"],
                            customer_id=row["customer_id"],
                            category_id=row["category_id"],
                            predicted_at=row["predicted_at"],
                            horizon_days=row["horizon_days"],
                            risk_level=row["risk_level"],
                            score=row["score"],
                            payload=row["payload"],
                            created_by=TaskResultRepository._system_user_id,
                        )
                        for row in chunk
                    ]
                )
                await session.commit()
