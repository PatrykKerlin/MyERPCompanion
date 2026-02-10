from collections.abc import Mapping, Sequence

from sqlalchemy import Select, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql.elements import ColumnElement

from models.business.logistic.assoc_bin_item import AssocBinItem
from models.business.logistic.bin import Bin
from models.business.trade import Order
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.status import Status
from repositories.base.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    _model_cls = Order

    @classmethod
    def __split_status_filter(
        cls, filters: Mapping[str, str] | None
    ) -> tuple[dict[str, str] | None, int | None]:
        if not filters:
            return None, None
        copied_filters = dict(filters)
        raw_status_id = copied_filters.pop("status_id", None)
        status_id: int | None = None
        if isinstance(raw_status_id, int):
            status_id = raw_status_id
        elif isinstance(raw_status_id, str) and raw_status_id.isdigit():
            status_id = int(raw_status_id)
        return (copied_filters if copied_filters else None), status_id

    @classmethod
    def __split_warehouse_filter(
        cls, filters: Mapping[str, str] | None
    ) -> tuple[dict[str, str] | None, int | None]:
        if not filters:
            return None, None
        copied_filters = dict(filters)
        raw_warehouse_id = copied_filters.pop("warehouse_id", None)
        warehouse_id: int | None = None
        if isinstance(raw_warehouse_id, int):
            warehouse_id = raw_warehouse_id
        elif isinstance(raw_warehouse_id, str) and raw_warehouse_id.isdigit():
            warehouse_id = int(raw_warehouse_id)
        return (copied_filters if copied_filters else None), warehouse_id

    @classmethod
    def __has_outbound_items_in_warehouse_filter(cls, warehouse_id: int) -> ColumnElement[bool]:
        eligible_item_exists = (
            select(1)
            .select_from(AssocOrderItem)
            .join(AssocBinItem, AssocBinItem.item_id == AssocOrderItem.item_id)
            .join(Bin, Bin.id == AssocBinItem.bin_id)
            .where(
                AssocOrderItem.order_id == cls._model_cls.id,
                AssocOrderItem.is_active.is_(True),
                AssocOrderItem.to_process > 0,
                AssocBinItem.is_active.is_(True),
                AssocBinItem.quantity > 0,
                Bin.is_active.is_(True),
                Bin.is_outbound.is_(True),
                Bin.warehouse_id == warehouse_id,
            )
            .correlate(cls._model_cls)
        )
        return cls._expr(exists(eligible_item_exists))

    @classmethod
    def __has_outbound_bin_stock_for_item_filter(cls, warehouse_id: int | None) -> ColumnElement[bool]:
        eligible_bin_stock = (
            select(1)
            .select_from(AssocBinItem)
            .join(Bin, Bin.id == AssocBinItem.bin_id)
            .where(
                AssocBinItem.item_id == AssocOrderItem.item_id,
                AssocBinItem.is_active.is_(True),
                AssocBinItem.quantity > 0,
                Bin.is_active.is_(True),
                Bin.is_outbound.is_(True),
            )
            .correlate(AssocOrderItem)
        )
        if warehouse_id is not None:
            eligible_bin_stock = eligible_bin_stock.where(Bin.warehouse_id == warehouse_id)
        return cls._expr(exists(eligible_bin_stock))

    @classmethod
    def __latest_status_filter(cls, status_id: int) -> ColumnElement[bool]:
        latest_status_subquery = (
            select(AssocOrderStatus.status_id)
            .where(
                AssocOrderStatus.order_id == cls._model_cls.id,
                AssocOrderStatus.is_active.is_(True),
            )
            .order_by(AssocOrderStatus.created_at.desc(), AssocOrderStatus.id.desc())
            .limit(1)
            .correlate(cls._model_cls)
            .scalar_subquery()
        )
        return cls._expr(latest_status_subquery == status_id)

    @classmethod
    def __latest_status_order_in_filter(cls, status_orders: tuple[int, ...]) -> ColumnElement[bool]:
        latest_status_order_subquery = (
            select(Status.order)
            .select_from(AssocOrderStatus)
            .join(Status, Status.id == AssocOrderStatus.status_id)
            .where(
                AssocOrderStatus.order_id == cls._model_cls.id,
                AssocOrderStatus.is_active.is_(True),
                Status.is_active.is_(True),
            )
            .order_by(AssocOrderStatus.created_at.desc(), AssocOrderStatus.id.desc())
            .limit(1)
            .correlate(cls._model_cls)
            .scalar_subquery()
        )
        return cls._expr(latest_status_order_subquery.in_(status_orders))

    @classmethod
    def __build_picking_eligible_filters(
        cls,
        status_orders: tuple[int, ...],
        warehouse_id: int | None,
    ) -> list[ColumnElement[bool]]:
        additional_filters = [
            *cls.__is_sales_filter(True),
            cls._expr(cls._model_cls.customer_id.is_not(None)),
            cls.__latest_status_order_in_filter(status_orders),
        ]
        if warehouse_id is not None:
            additional_filters.append(cls.__has_outbound_items_in_warehouse_filter(warehouse_id))
        return additional_filters

    @classmethod
    async def get_all_sales(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[Order]:
        filters_without_status, status_id = cls.__split_status_filter(filters)
        additional_filters = cls.__is_sales_filter(True)
        if status_id is not None:
            additional_filters.append(cls.__latest_status_filter(status_id))
        query = (
            cls._build_query(
                params_filters=filters_without_status,
                additional_filters=additional_filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all_purchase(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[Order]:
        filters_without_status, status_id = cls.__split_status_filter(filters)
        additional_filters = cls.__is_sales_filter(False)
        if status_id is not None:
            additional_filters.append(cls.__latest_status_filter(status_id))
        query = (
            cls._build_query(
                params_filters=filters_without_status,
                additional_filters=additional_filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count_all_sales(
        cls,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
    ) -> int:
        filters_without_status, status_id = cls.__split_status_filter(filters)
        additional_filters = cls.__is_sales_filter(True)
        if status_id is not None:
            additional_filters.append(cls.__latest_status_filter(status_id))
        return await cls._count_all(
            session=session,
            params_filters=filters_without_status,
            additional_filters=additional_filters,
        )

    @classmethod
    async def count_all_purchase(
        cls,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
    ) -> int:
        filters_without_status, status_id = cls.__split_status_filter(filters)
        additional_filters = cls.__is_sales_filter(False)
        if status_id is not None:
            additional_filters.append(cls.__latest_status_filter(status_id))
        return await cls._count_all(
            session=session,
            params_filters=filters_without_status,
            additional_filters=additional_filters,
        )

    @classmethod
    async def get_all_picking_eligible(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        status_orders: tuple[int, ...] = (2, 3),
    ) -> Sequence[Order]:
        filters_without_warehouse, warehouse_id = cls.__split_warehouse_filter(filters)
        additional_filters = cls.__build_picking_eligible_filters(status_orders, warehouse_id)
        query = (
            cls._build_query(
                params_filters=filters_without_warehouse,
                additional_filters=additional_filters,
                sort_by=sort_by,
                sort_order=sort_order,
            )
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count_all_picking_eligible(
        cls,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        status_orders: tuple[int, ...] = (2, 3),
    ) -> int:
        filters_without_warehouse, warehouse_id = cls.__split_warehouse_filter(filters)
        additional_filters = cls.__build_picking_eligible_filters(status_orders, warehouse_id)
        return await cls._count_all(
            session=session,
            params_filters=filters_without_warehouse,
            additional_filters=additional_filters,
        )

    @classmethod
    async def get_picking_summary(
        cls,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        status_orders: tuple[int, ...] = (2, 3),
    ) -> tuple[int, int, int]:
        filters_without_warehouse, warehouse_id = cls.__split_warehouse_filter(filters)
        additional_filters = cls.__build_picking_eligible_filters(status_orders, warehouse_id)
        eligible_orders_query = (
            super()
            ._build_query(
                params_filters=filters_without_warehouse,
                additional_filters=additional_filters,
                sort_by="id",
                sort_order="asc",
            )
            .with_only_columns(cls._model_cls.id)
            .order_by(None)
            .subquery()
        )

        orders_count_result = await session.execute(select(func.count()).select_from(eligible_orders_query))
        orders_count = int(orders_count_result.scalar_one() or 0)
        if orders_count == 0:
            return 0, 0, 0

        eligible_order_items_query = (
            select(
                AssocOrderItem.order_id.label("order_id"),
                AssocOrderItem.item_id.label("item_id"),
                AssocOrderItem.to_process.label("to_process"),
            )
            .where(
                AssocOrderItem.is_active.is_(True),
                AssocOrderItem.to_process > 0,
                AssocOrderItem.order_id.in_(select(eligible_orders_query.c.id)),
                cls.__has_outbound_bin_stock_for_item_filter(warehouse_id),
            )
            .subquery()
        )

        distinct_order_item_pairs_query = (
            select(
                eligible_order_items_query.c.order_id,
                eligible_order_items_query.c.item_id,
            )
            .distinct()
            .subquery()
        )
        items_count_result = await session.execute(select(func.count()).select_from(distinct_order_item_pairs_query))
        items_count = int(items_count_result.scalar_one() or 0)

        pieces_count_result = await session.execute(
            select(func.coalesce(func.sum(eligible_order_items_query.c.to_process), 0))
        )
        pieces_count = int(pieces_count_result.scalar_one() or 0)

        return orders_count, items_count, pieces_count

    @classmethod
    def _build_query(
        cls,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(params_filters, additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.order_items),
            selectinload(cls._model_cls.order_statuses),
            with_loader_criteria(AssocOrderItem, cls._expr(AssocOrderItem.is_active.is_(True))),
            with_loader_criteria(AssocOrderStatus, cls._expr(AssocOrderStatus.is_active.is_(True))),
        )

    @classmethod
    def __is_sales_filter(cls, is_sales: bool) -> list[ColumnElement[bool]]:
        return [cls._expr(cls._model_cls.is_sales.is_(is_sales))]
