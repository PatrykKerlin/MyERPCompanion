from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError

from config.context import Context
from controllers.base.base_controller import BaseController
from schemas.business.trade.order_schema import OrderPlainSchema, OrderStrictSchema
from schemas.core.param_schema import (
    FilterParamsSchema,
    PaginatedResponseSchema,
    PaginationParamsSchema,
    SortingParamsSchema,
)
from services.business.trade.order_service import OrderService
from utils.auth import Auth
from utils.enums import Permission
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
        self._register_routes(OrderPlainSchema)

    async def get_all_sales(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        try:
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
        except HTTPException:
            raise
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    async def get_all_purchase(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[OrderPlainSchema]:
        try:
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
        except HTTPException:
            raise
        except SQLAlchemyError as err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
