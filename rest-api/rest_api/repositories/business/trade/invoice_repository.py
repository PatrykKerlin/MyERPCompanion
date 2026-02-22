from models.business.logistic.item import Item
from models.business.logistic.unit import Unit
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.invoice import Invoice
from models.business.trade.order import Order
from repositories.base.base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria


class InvoiceRepository(BaseRepository[Invoice]):
    _model_cls = Invoice

    @staticmethod
    async def get_invoice_with_relations(session: AsyncSession, invoice_id: int) -> Invoice | None:
        query = (
            select(Invoice)
            .where(
                Invoice.id == invoice_id,
                Invoice.is_active.is_(True),
            )
            .options(
                selectinload(Invoice.customer),
                selectinload(Invoice.currency),
                selectinload(Invoice.orders)
                .selectinload(Order.order_items)
                .selectinload(AssocOrderItem.item)
                .selectinload(Item.unit),
                with_loader_criteria(Order, Order.is_active.is_(True)),
                with_loader_criteria(AssocOrderItem, AssocOrderItem.is_active.is_(True)),
                with_loader_criteria(Item, Item.is_active.is_(True)),
                with_loader_criteria(Unit, Unit.is_active.is_(True)),
            )
        )
        result = await session.execute(query)
        return result.scalars().first()
