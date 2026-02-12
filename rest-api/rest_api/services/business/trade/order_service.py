from collections.abc import Mapping

from models.business.trade.order import Order
from repositories.business.trade.order_repository import OrderRepository
from schemas.business.trade.order_schema import OrderPickingSummarySchema, OrderPlainSchema, OrderStrictSchema
from services.base.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession


class OrderService(BaseService[Order, OrderRepository, OrderStrictSchema, OrderPlainSchema]):
    _repository_cls = OrderRepository
    _model_cls = Order
    _output_schema_cls = OrderPlainSchema

    async def get_all_sales(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[OrderPlainSchema], int]:
        models = await self._repository_cls.get_all_sales(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls.count_all_sales(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(model) for model in models]
        return schemas, total

    async def get_all_purchase(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[OrderPlainSchema], int]:
        models = await self._repository_cls.get_all_purchase(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls.count_all_purchase(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(model) for model in models]
        return schemas, total

    async def get_all_picking_eligible(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[OrderPlainSchema], int]:
        models = await self._repository_cls.get_all_picking_eligible(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls.count_all_picking_eligible(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(model) for model in models]
        return schemas, total

    async def get_picking_summary(
        self,
        session: AsyncSession,
        filters: Mapping[str, str] | None = None,
    ) -> OrderPickingSummarySchema:
        orders_count, items_count, pieces_count = await self._repository_cls.get_picking_summary(
            session=session,
            filters=filters,
        )
        return OrderPickingSummarySchema(
            orders_count=orders_count,
            items_count=items_count,
            pieces_count=pieces_count,
        )
