from __future__ import annotations

from typing import Any

from database.engine import Engine
from models.ai.sales_forecast import SalesForecast


class SalesForecastResultRepository:
    _system_user_id = 1
    _insert_chunk_size = 2000

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def save_results(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return

        async with self._engine.get_session() as session:
            for chunk_start in range(0, len(rows), SalesForecastResultRepository._insert_chunk_size):
                chunk = rows[chunk_start : chunk_start + SalesForecastResultRepository._insert_chunk_size]
                session.add_all(
                    [
                        SalesForecast(
                            run_id=row["run_id"],
                            item_id=row["item_id"],
                            customer_id=row["customer_id"],
                            category_id=row["category_id"],
                            currency_id=row["currency_id"],
                            predicted_at=row["predicted_at"],
                            predicted_quantity=row["predicted_quantity"],
                            samples=row["samples"],
                            aggregation=row["aggregation"],
                            horizon_months=row["horizon_months"],
                            discount_rate_assumption=row["discount_rate_assumption"],
                            created_by=SalesForecastResultRepository._system_user_id,
                        )
                        for row in chunk
                    ]
                )
                await session.commit()
