from collections.abc import Mapping, Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql.elements import ColumnElement

from models.business.trade import Order
from models.business.trade.assoc_order_item import AssocOrderItem
from models.business.trade.assoc_order_status import AssocOrderStatus
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
