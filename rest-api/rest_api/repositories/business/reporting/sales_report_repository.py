from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from models.business.logistic.category import Category
from models.business.logistic.item import Item
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.customer import Customer
from models.business.trade.order import Order


class SalesReportRepository:
    @staticmethod
    async def get_rows(
        session: AsyncSession,
        date_from: date | None = None,
        date_to: date | None = None,
        item_id: int | None = None,
        customer_id: int | None = None,
        category_id: int | None = None,
        currency_id: int | None = None,
    ) -> list[Any]:
        query = SalesReportRepository.__build_rows_query(
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
        )
        result = await session.execute(query)
        return list(result)

    @staticmethod
    async def get_totals(
        session: AsyncSession,
        date_from: date | None = None,
        date_to: date | None = None,
        item_id: int | None = None,
        customer_id: int | None = None,
        category_id: int | None = None,
        currency_id: int | None = None,
    ) -> dict[str, Decimal | int | None]:
        query = SalesReportRepository.__build_totals_query(
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
        )
        result = await session.execute(query)
        row = result.one()
        return {
            "orders_count": row.orders_count,
            "quantity": row.quantity,
            "total_net": row.total_net,
            "total_vat": row.total_vat,
            "total_gross": row.total_gross,
            "total_discount": row.total_discount,
        }

    @staticmethod
    def __build_rows_query(
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
    ) -> Select:
        where_clause = SalesReportRepository.__build_filters(
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
        )
        return (
            select(
                AssocOrderItem.id.label("order_item_id"),
                Order.id.label("order_id"),
                Order.number.label("order_number"),
                Order.order_date.label("order_date"),
                Customer.id.label("customer_id"),
                Customer.company_name.label("customer_name"),
                Item.id.label("item_id"),
                Item.name.label("item_name"),
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                AssocOrderItem.quantity.label("quantity"),
                AssocOrderItem.total_net.label("total_net"),
                AssocOrderItem.total_vat.label("total_vat"),
                AssocOrderItem.total_gross.label("total_gross"),
                AssocOrderItem.total_discount.label("total_discount"),
            )
            .select_from(AssocOrderItem)
            .join(Order, AssocOrderItem.order_id == Order.id)
            .join(Item, AssocOrderItem.item_id == Item.id)
            .join(Category, Item.category_id == Category.id)
            .outerjoin(Customer, Order.customer_id == Customer.id)
            .where(*where_clause)
            .order_by(desc(Order.order_date), desc(AssocOrderItem.id))
        )

    @staticmethod
    def __build_totals_query(
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
    ) -> Select:
        where_clause = SalesReportRepository.__build_filters(
            date_from=date_from,
            date_to=date_to,
            item_id=item_id,
            customer_id=customer_id,
            category_id=category_id,
            currency_id=currency_id,
        )
        return (
            select(
                func.count(distinct(Order.id)).label("orders_count"),
                func.coalesce(func.sum(AssocOrderItem.quantity), 0).label("quantity"),
                func.coalesce(func.sum(AssocOrderItem.total_net), 0).label("total_net"),
                func.coalesce(func.sum(AssocOrderItem.total_vat), 0).label("total_vat"),
                func.coalesce(func.sum(AssocOrderItem.total_gross), 0).label("total_gross"),
                func.coalesce(func.sum(AssocOrderItem.total_discount), 0).label("total_discount"),
            )
            .select_from(AssocOrderItem)
            .join(Order, AssocOrderItem.order_id == Order.id)
            .join(Item, AssocOrderItem.item_id == Item.id)
            .join(Category, Item.category_id == Category.id)
            .outerjoin(Customer, Order.customer_id == Customer.id)
            .where(*where_clause)
        )

    @staticmethod
    def __build_filters(
        date_from: date | None,
        date_to: date | None,
        item_id: int | None,
        customer_id: int | None,
        category_id: int | None,
        currency_id: int | None,
    ) -> list[ColumnElement[bool]]:
        where_clause = [
            Order.is_active.is_(True),
            Order.is_sales.is_(True),
            Order.invoice_id.is_not(None),
            AssocOrderItem.is_active.is_(True),
            Item.is_active.is_(True),
            Category.is_active.is_(True),
            (Order.customer_id.is_(None) | Customer.is_active.is_(True)),
        ]
        if date_from is not None:
            where_clause.append(Order.order_date >= date_from)
        if date_to is not None:
            where_clause.append(Order.order_date <= date_to)
        if customer_id is not None:
            where_clause.append(Order.customer_id == customer_id)
        if item_id is not None:
            where_clause.append(AssocOrderItem.item_id == item_id)
        if category_id is not None:
            where_clause.append(Item.category_id == category_id)
        if currency_id is not None:
            where_clause.append(Order.currency_id == currency_id)
        return where_clause
