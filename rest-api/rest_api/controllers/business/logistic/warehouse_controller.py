from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from config.context import Context
from controllers.base.base_controller import BaseController
from schemas.core.param_schema import PaginatedResponseSchema, PaginationParamsSchema
from schemas.business.logistic.warehouse_schema import (
    WarehouseLoginOptionSchema,
    WarehousePlainSchema,
    WarehouseStrictSchema,
)
from services.business.logistic import WarehouseService
from services.core import UserService
from utils.auth import Auth


class WarehouseController(BaseController[WarehouseService, WarehouseStrictSchema, WarehousePlainSchema]):
    _input_schema_cls = WarehouseStrictSchema
    _service_cls = WarehouseService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self.__user_service = UserService()
        self.router.add_api_route(
            path="/by-username",
            endpoint=self.get_for_login,
            methods=["GET"],
            response_model=PaginatedResponseSchema[WarehouseLoginOptionSchema],
            status_code=status.HTTP_200_OK,
        )
        self._register_routes(output_schema=WarehousePlainSchema)

    async def get_for_login(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        username: str | None = Query(default=None, min_length=1, max_length=20),
    ) -> PaginatedResponseSchema[WarehouseLoginOptionSchema]:
        try:
            session = BaseController._get_request_session(request)
            resolved_username = username.strip() if username else None
            offset, limit = BaseController._get_offset_and_limit(pagination)

            if resolved_username:
                user = await self.__user_service.get_one_by_username(session, resolved_username)
                if user and user.warehouse_id is not None:
                    try:
                        warehouse = await self._service.get_one_by_id(session, user.warehouse_id)
                    except NoResultFound:
                        warehouse = None
                    if warehouse:
                        total = 1
                        has_next, has_prev = BaseController._get_has_next_has_prev(
                            offset,
                            limit,
                            total,
                            pagination.page,
                        )
                        items = []
                        if offset < total:
                            items = [WarehouseLoginOptionSchema(**warehouse.model_dump(mode="json"))]
                        return PaginatedResponseSchema[WarehouseLoginOptionSchema](
                            items=items,
                            total=total,
                            page=pagination.page,
                            page_size=pagination.page_size,
                            has_next=has_next,
                            has_prev=has_prev,
                        )

            warehouses, total = await self._service.get_all(
                session=session,
                offset=offset,
                limit=limit,
                sort_by="id",
                sort_order="asc",
            )
            items = [WarehouseLoginOptionSchema(**warehouse.model_dump(mode="json")) for warehouse in warehouses]
            has_next, has_prev = BaseController._get_has_next_has_prev(offset, limit, total, pagination.page)
            return PaginatedResponseSchema[WarehouseLoginOptionSchema](
                items=items,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                has_next=has_next,
                has_prev=has_prev,
            )
        except HTTPException:
            self._logger.exception(f"HTTPException in {self.__class__.__name__}.{self.get_for_login.__qualname__}")
            raise
        except SQLAlchemyError as err:
            self._logger.exception(f"SQLAlchemyError in {self.__class__.__name__}.{self.get_for_login.__qualname__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))
