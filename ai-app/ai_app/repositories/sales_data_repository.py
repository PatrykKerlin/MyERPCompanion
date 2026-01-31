from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import case, func, select

from database.engine import Engine
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.order import Order


class SalesDataRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def get_daily_item_sales(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        discount_flag = case(
            (
                (AssocOrderItem.category_discount_id.isnot(None))
                | (AssocOrderItem.customer_discount_id.isnot(None))
                | (AssocOrderItem.item_discount_id.isnot(None)),
                1,
            ),
            else_=0,
        )
        query = (
            select(
                Order.order_date.label("order_date"),
                AssocOrderItem.item_id.label("item_id"),
                func.sum(AssocOrderItem.quantity).label("quantity"),
                func.max(discount_flag).label("has_discount"),
                Item.stock_quantity.label("stock_quantity"),
                Item.lead_time.label("lead_time"),
            )
            .join(AssocOrderItem, AssocOrderItem.order_id == Order.id)
            .join(Item, Item.id == AssocOrderItem.item_id)
            .where(
                Order.is_sales.is_(True),
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.is_active.is_(True),
                AssocOrderItem.is_active.is_(True),
                Item.is_active.is_(True),
            )
            .group_by(
                Order.order_date,
                AssocOrderItem.item_id,
                Item.stock_quantity,
                Item.lead_time,
            )
            .order_by(Order.order_date, AssocOrderItem.item_id)
        )
        async with self._engine.get_session() as session:
            result = await session.execute(query)
            rows = result.all()
        return [
            {
                "order_date": row.order_date,
                "item_id": row.item_id,
                "quantity": int(row.quantity or 0),
                "has_discount": bool(row.has_discount),
                "stock_quantity": int(row.stock_quantity or 0),
                "lead_time": int(row.lead_time or 0),
            }
            for row in rows
        ]
