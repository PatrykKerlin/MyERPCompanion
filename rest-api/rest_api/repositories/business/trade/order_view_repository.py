from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from models.business.logistic.carrier import Carrier
from models.business.logistic.category import Category
from models.business.logistic.delivery_method import DeliveryMethod
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from models.business.trade.order import Order
from models.business.trade.status import Status
from models.business.trade.supplier import Supplier
from repositories.base.reserved_quantity_mixin import ReservedQuantityMixin


class OrderViewRepository(ReservedQuantityMixin):
    @staticmethod
    async def get_lookups(
        session: AsyncSession,
    ) -> tuple[
        Sequence[Supplier],
        Sequence[Customer],
        Sequence[Currency],
        Sequence[DeliveryMethod],
        Sequence[Status],
        Sequence[Category],
    ]:
        suppliers_result = await session.execute(
            select(Supplier).where(Supplier.is_active.is_(True)).order_by(Supplier.company_name)
        )
        customers_result = await session.execute(
            select(Customer).where(Customer.is_active.is_(True)).order_by(Customer.company_name)
        )
        currencies_result = await session.execute(
            select(Currency).where(Currency.is_active.is_(True)).order_by(Currency.code)
        )
        delivery_result = await session.execute(
            select(DeliveryMethod)
            .join(Carrier)
            .where(DeliveryMethod.is_active.is_(True), Carrier.is_active.is_(True))
            .order_by(Carrier.name, DeliveryMethod.name)
        )
        statuses_result = await session.execute(select(Status).where(Status.is_active.is_(True)).order_by(Status.order))
        categories_result = await session.execute(
            select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
        )
        return (
            suppliers_result.scalars().all(),
            customers_result.scalars().all(),
            currencies_result.scalars().all(),
            delivery_result.scalars().all(),
            statuses_result.scalars().all(),
            categories_result.scalars().all(),
        )

    @staticmethod
    async def get_order_with_relations(session: AsyncSession, order_id: int, is_sales: bool) -> Order | None:
        query = (
            select(Order)
            .where(Order.id == order_id, Order.is_active.is_(True), Order.is_sales.is_(is_sales))
            .options(
                selectinload(Order.order_items).selectinload(AssocOrderItem.item),
                selectinload(Order.order_statuses).selectinload(AssocOrderStatus.status),
                with_loader_criteria(AssocOrderItem, AssocOrderItem.is_active.is_(True), include_aliases=True),
                with_loader_criteria(AssocOrderStatus, AssocOrderStatus.is_active.is_(True), include_aliases=True),
            )
            .execution_options(populate_existing=True)
        )
        result = await session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_items_for_supplier(session: AsyncSession, supplier_id: int) -> Sequence[Item]:
        result = await session.execute(
            select(Item)
            .where(Item.is_active.is_(True), Item.supplier_id == supplier_id)
            .options(with_loader_criteria(Item, Item.is_active.is_(True)))
            .order_by(Item.index)
        )
        items = result.scalars().all()
        await OrderViewRepository._attach_reserved_quantities(session, items)
        return items

    @staticmethod
    async def get_all_items(session: AsyncSession) -> Sequence[Item]:
        result = await session.execute(select(Item).where(Item.is_active.is_(True)).order_by(Item.index))
        items = result.scalars().all()
        await OrderViewRepository._attach_reserved_quantities(session, items)
        return items
