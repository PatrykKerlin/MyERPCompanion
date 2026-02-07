from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import cast, func, select
from sqlalchemy import Date as SqlDate
from sqlalchemy import Float as SqlFloat

from database.engine import Engine
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.order import Order


class SalesPredictionRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    async def get_monthly_sales(self, start_date: date, end_date: date) -> list[dict[str, Any]]:
        period_start = cast(func.date_trunc("month", Order.order_date), SqlDate)
        gross_before_discount = func.sum(AssocOrderItem.total_net + AssocOrderItem.total_discount)
        discount_ratio = func.coalesce(
            cast(func.sum(AssocOrderItem.total_discount) / func.nullif(gross_before_discount, 0), SqlFloat),
            0.0,
        )
        query = (
            select(
                period_start.label("period_start"),
                AssocOrderItem.item_id.label("item_id"),
                Order.customer_id.label("customer_id"),
                Item.category_id.label("category_id"),
                Order.currency_id.label("currency_id"),
                func.sum(AssocOrderItem.total_net).label("total_net"),
                func.sum(AssocOrderItem.total_gross).label("total_gross"),
                discount_ratio.label("discount_ratio"),
            )
            .join(AssocOrderItem, AssocOrderItem.order_id == Order.id)
            .join(Item, Item.id == AssocOrderItem.item_id)
            .where(
                Order.is_sales.is_(True),
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.is_active.is_(True),
                Order.invoice_id.is_not(None),
                Order.customer_id.is_not(None),
                Order.currency_id.is_not(None),
                AssocOrderItem.is_active.is_(True),
                Item.is_active.is_(True),
                Item.category_id.is_not(None),
            )
            .group_by(
                period_start,
                AssocOrderItem.item_id,
                Order.customer_id,
                Item.category_id,
                Order.currency_id,
            )
            .order_by(period_start, AssocOrderItem.item_id, Order.customer_id, Item.category_id, Order.currency_id)
        )
        async with self._engine.get_session() as session:
            result = await session.execute(query)
            rows = result.all()
        return [
            {
                "period_start": row.period_start,
                "item_id": int(row.item_id),
                "customer_id": int(row.customer_id),
                "category_id": int(row.category_id),
                "currency_id": int(row.currency_id),
                "total_net": float(row.total_net or 0.0),
                "total_gross": float(row.total_gross or 0.0),
                "discount_ratio": float(row.discount_ratio or 0.0),
            }
            for row in rows
        ]
