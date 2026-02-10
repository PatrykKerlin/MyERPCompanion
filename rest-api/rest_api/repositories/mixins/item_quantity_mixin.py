from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.business.logistic.assoc_bin_item import AssocBinItem
from models.business.logistic.bin import Bin
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem


class ItemQuantityMixin:
    @staticmethod
    async def _get_reserved_quantities(session: AsyncSession, items: Sequence[Item]) -> dict[int, int]:
        if not items:
            return {}
        item_ids = [item.id for item in items]
        result = await session.execute(
            select(AssocOrderItem.item_id, func.coalesce(func.sum(AssocOrderItem.to_process), 0))
            .where(AssocOrderItem.is_active.is_(True), AssocOrderItem.item_id.in_(item_ids))
            .group_by(AssocOrderItem.item_id)
        )
        return {row[0]: int(row[1]) for row in result.all()}

    @staticmethod
    async def _get_outbound_quantities(session: AsyncSession, items: Sequence[Item]) -> dict[int, int]:
        if not items:
            return {}
        item_ids = [item.id for item in items]
        result = await session.execute(
            select(AssocBinItem.item_id, func.coalesce(func.sum(AssocBinItem.quantity), 0))
            .join(Bin, Bin.id == AssocBinItem.bin_id)
            .where(
                AssocBinItem.is_active.is_(True),
                Bin.is_active.is_(True),
                Bin.is_outbound.is_(True),
                AssocBinItem.item_id.in_(item_ids),
            )
            .group_by(AssocBinItem.item_id)
        )
        return {row[0]: int(row[1]) for row in result.all()}
