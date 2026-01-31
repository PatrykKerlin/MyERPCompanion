from __future__ import annotations

from datetime import date

from database.engine import Engine
from models.ai.ai_prediction import AiPrediction


class PredictionRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def save_prediction(
        self,
        task_key: str,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        predicted_at: date,
        horizon_days: int | None,
        risk_level: str | None,
        score: float | None,
        payload: dict | None,
    ) -> None:
        async with self._engine.get_session() as session:
            prediction = AiPrediction(
                task_key=task_key,
                item_id=item_id,
                customer_id=customer_id,
                category_id=category_id,
                predicted_at=predicted_at,
                horizon_days=horizon_days,
                risk_level=risk_level,
                score=score,
                payload=payload,
            )
            session.add(prediction)
            await session.commit()
