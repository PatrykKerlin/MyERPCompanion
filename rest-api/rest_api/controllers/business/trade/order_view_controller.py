from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import APIRouter, Depends, HTTPException, Request, status
from schemas.business.trade.order_view_schema import OrderViewResponseSchema
from services.business.trade.order_view_service import OrderViewService
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from utils.auth import Auth
from utils.enums import Permission


class OrderViewController:
    def __init__(self, context: Context, auth: Auth) -> None:
        self._logger = context.logger
        self._service = OrderViewService()
        self._auth = auth
        self.router = APIRouter()
        dependencies = [
            Depends(auth.restrict_access(permissions=[Permission.CAN_READ], controller=self.__class__.__name__))
        ]
        self.router.add_api_route(
            path="/purchase",
            endpoint=self.get_purchase_view,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=dependencies,
        )
        self.router.add_api_route(
            path="/purchase/{order_id}",
            endpoint=self.get_purchase_view_by_id,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=dependencies,
        )
        self.router.add_api_route(
            path="/sales",
            endpoint=self.get_sales_view,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=dependencies,
        )
        self.router.add_api_route(
            path="/sales/{order_id}",
            endpoint=self.get_sales_view_by_id,
            methods=["GET"],
            response_model=OrderViewResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=dependencies,
        )

    async def get_purchase_view(self, request: Request) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=False, order_id=None)

    async def get_purchase_view_by_id(self, request: Request, order_id: int) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=False, order_id=order_id)

    async def get_sales_view(self, request: Request) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=True, order_id=None)

    async def get_sales_view_by_id(self, request: Request, order_id: int) -> OrderViewResponseSchema:
        return await self.__get_view(request, is_sales=True, order_id=order_id)

    async def __get_view(self, request: Request, is_sales: bool, order_id: int | None) -> OrderViewResponseSchema:
        try:
            session = BaseController._get_request_session(request)
            response = await self._service.get_view(session=session, is_sales=is_sales, order_id=order_id)
            if order_id is not None and response.order is None:
                raise NoResultFound()
            return response
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.__get_view")
            raise
        except NoResultFound:
            self._logger.exception(f"NoResultFound in {self.__class__.__name__}.__get_view")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.__get_view")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
