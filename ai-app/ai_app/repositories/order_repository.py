from __future__ import annotations

from datetime import date

from sqlalchemy import func, select

from database.engine import Engine
from models.business.trade.order import Order


class OrderRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def get_min_order_date(self) -> date | None:
        async with self._engine.get_session() as session:
            result = await session.execute(
                select(func.min(Order.order_date)).where(Order.is_sales.is_(True))
            )
            return result.scalar_one_or_none()

    async def get_max_order_date(self, start_date: date | None = None) -> date | None:
        async with self._engine.get_session() as session:
            query = select(func.max(Order.order_date)).where(Order.is_sales.is_(True))
            if start_date is not None:
                query = query.where(Order.order_date >= start_date)
            result = await session.execute(query)
            return result.scalar_one_or_none()
