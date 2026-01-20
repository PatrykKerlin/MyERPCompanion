from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria

from models.business.logistic.carrier import Carrier
from models.business.logistic.category import Category
from models.business.logistic.delivery_method import DeliveryMethod
from models.business.logistic.item import Item
from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from models.business.trade.order import Order
from models.business.trade.status import Status
from models.business.trade.supplier import Supplier
from repositories.business.trade.order_repository import OrderRepository


class OrderViewRepository:
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
        order = await OrderRepository.get_one_by_id(session, order_id)
        if not order or order.is_sales != is_sales:
            return None
        return order

    @staticmethod
    async def get_items_for_supplier(session: AsyncSession, supplier_id: int) -> Sequence[Item]:
        result = await session.execute(
            select(Item)
            .where(Item.is_active.is_(True), Item.supplier_id == supplier_id)
            .options(with_loader_criteria(Item, Item.is_active.is_(True)))
            .order_by(Item.index)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_items(session: AsyncSession) -> Sequence[Item]:
        result = await session.execute(select(Item).where(Item.is_active.is_(True)).order_by(Item.index))
        return result.scalars().all()
