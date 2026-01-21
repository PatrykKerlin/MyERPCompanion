from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem


class ReservedQuantityMixin:
    @staticmethod
    async def _attach_reserved_quantities(session: AsyncSession, items: Sequence[Item]) -> None:
        if not items:
            return
        item_ids = [item.id for item in items]
        result = await session.execute(
            select(AssocOrderItem.item_id, func.coalesce(func.sum(AssocOrderItem.quantity), 0))
            .where(AssocOrderItem.is_active.is_(True), AssocOrderItem.item_id.in_(item_ids))
            .group_by(AssocOrderItem.item_id)
        )
        reserved_by_item_id = {row[0]: int(row[1]) for row in result.all()}
        for item in items:
            setattr(item, "reserved_quantity", reserved_by_item_id.get(item.id, 0))
