from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Request, status
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.business.trade.order_view_schema import OrderViewResponseSchema
from services.business.trade.order_view_service import OrderViewService
from utils.auth import Auth
from utils.enums import Permission


class OrderViewController(BaseController[OrderViewService, BaseStrictSchema, BasePlainSchema]):
    _input_schema_cls = BaseStrictSchema
    _service_cls = OrderViewService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._register_routes(output_schema=BasePlainSchema, include={})
        self.router.add_api_route(
            path="/purchase",
            endpoint=self.get_purchase_view,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/purchase/{order_id:int}",
            endpoint=self.get_purchase_view_by_id,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/sales",
            endpoint=self.get_sales_view,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )
        self.router.add_api_route(
            path="/sales/{order_id:int}",
            endpoint=self.get_sales_view_by_id,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=self._restrict_access(permissions=[Permission.CAN_READ], secured=True),
        )

    @BaseController.handle_exceptions()
    async def get_purchase_view(self, request: Request) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=False, order_id=None)

    @BaseController.handle_exceptions()
    async def get_purchase_view_by_id(self, request: Request, order_id: int) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=False, order_id=order_id)

    @BaseController.handle_exceptions()
    async def get_sales_view(self, request: Request) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=True, order_id=None)

    @BaseController.handle_exceptions()
    async def get_sales_view_by_id(self, request: Request, order_id: int) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=True, order_id=order_id)

    async def __get_view(self, request: Request, is_sales: bool, order_id: int | None) -> OrderViewResponseSchema:
        session = BaseController._get_request_session(request)
        return await self._service.get_view(session=session, is_sales=is_sales, order_id=order_id)
