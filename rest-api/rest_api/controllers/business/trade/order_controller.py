from typing import Annotated

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Depends, Request, status
from schemas.business.trade.order_schema import OrderPickingSummarySchema, OrderPlainSchema, OrderStrictSchema
from schemas.core.param_schema import (
    FilterParamsSchema,
    PaginatedResponseSchema,
    PaginationParamsSchema,
    SortingParamsSchema,
)
from services.business.trade.order_service import OrderService
from utils.auth import Auth
from utils.enums import Action, Permission
from utils.parsers import FilterParamsParser


class OrderController(BaseController[OrderService, OrderStrictSchema, OrderPlainSchema]):
    _input_schema_cls = OrderStrictSchema
    _service_cls = OrderService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self.router.add_api_route(
            path="/sales",
            endpoint=self.get_all_sales,
            methods=["GET"],
            response_model=PaginatedResponseSchema[OrderPlainSchema],
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/purchase",
            endpoint=self.get_all_purchase,
            methods=["GET"],
            response_model=PaginatedResponseSchema[OrderPlainSchema],
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/picking-eligible",
            endpoint=self.get_all_picking_eligible,
            methods=["GET"],
            response_model=PaginatedResponseSchema[OrderPlainSchema],
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/picking-summary",
            endpoint=self.get_picking_summary,
            methods=["GET"],
            response_model=OrderPickingSummarySchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self._register_routes(
            output_schema=OrderPlainSchema,
            include={
                Action.GET_ALL: True,
                Action.GET_BULK: True,
                Action.GET_ONE: True,
                Action.CREATE: True,
                Action.UPDATE: True,
                Action.UPDATE_BULK: True,
                Action.DELETE: True,
            },
        )

    @BaseController.handle_exceptions()
    async def get_all_sales(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        session = BaseController._get_request_session(request)
        offset, limit = BaseController._get_offset_and_limit(pagination)
        items, total = await self._service.get_all_sales(
            session=session,
            filters=filters.filters,
            offset=offset,
            limit=limit,
            sort_by=sorting.sort_by,
            sort_order=sorting.order,
        )
        has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)
        return PaginatedResponseSchema[OrderPlainSchema](
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=has_next,
            has_prev=has_prev,
        )

    @BaseController.handle_exceptions()
    async def get_all_purchase(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        session = BaseController._get_request_session(request)
        offset, limit = BaseController._get_offset_and_limit(pagination)
        items, total = await self._service.get_all_purchase(
            session=session,
            filters=filters.filters,
            offset=offset,
            limit=limit,
            sort_by=sorting.sort_by,
            sort_order=sorting.order,
        )
        has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)
        return PaginatedResponseSchema[OrderPlainSchema](
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=has_next,
            has_prev=has_prev,
        )

    @BaseController.handle_exceptions()
    async def get_all_picking_eligible(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        token_client = getattr(request.state, "token_client", None)
        if token_client == "mobile":
            token_warehouse_id = getattr(request.state, "token_warehouse_id", None)
            if isinstance(token_warehouse_id, int):
                filters.filters["warehouse_id"] = str(token_warehouse_id)
            else:
                filters.filters["warehouse_id"] = "0"
        session = BaseController._get_request_session(request)
        offset, limit = BaseController._get_offset_and_limit(pagination)
        items, total = await self._service.get_all_picking_eligible(
            session=session,
            filters=filters.filters,
            offset=offset,
            limit=limit,
            sort_by=sorting.sort_by,
            sort_order=sorting.order,
        )
        has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)
        return PaginatedResponseSchema[OrderPlainSchema](
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=has_next,
            has_prev=has_prev,
        )

    @BaseController.handle_exceptions()
    async def get_picking_summary(
        self,
        request: Request,
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
    ) -> OrderPickingSummarySchema:
        token_client = getattr(request.state, "token_client", None)
        if token_client == "mobile":
            token_warehouse_id = getattr(request.state, "token_warehouse_id", None)
            if isinstance(token_warehouse_id, int):
                filters.filters["warehouse_id"] = str(token_warehouse_id)
            else:
                filters.filters["warehouse_id"] = "0"
        session = BaseController._get_request_session(request)
        return await self._service.get_picking_summary(session=session, filters=filters.filters)
