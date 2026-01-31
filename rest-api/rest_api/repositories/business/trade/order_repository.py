from collections.abc import Mapping, Sequence

from sqlalchemy import Select
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
    async def get_all_sales(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[Order]:
        additional_filters = cls.__is_sales_filter(True)
        query = (
            cls._build_query(
                params_filters=filters,
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
        additional_filters = cls.__is_sales_filter(False)
        query = (
            cls._build_query(
                params_filters=filters,
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
        additional_filters = cls.__is_sales_filter(True)
        return await cls._count_all(session=session, params_filters=filters, additional_filters=additional_filters)

    @classmethod
    async def count_all_purchase(
        cls,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
    ) -> int:
        additional_filters = cls.__is_sales_filter(False)
        return await cls._count_all(session=session, params_filters=filters, additional_filters=additional_filters)

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
