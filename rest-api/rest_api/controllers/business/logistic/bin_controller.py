from typing import Annotated

from config.context import Context
from controllers.base.base_controller import BaseController
from fastapi import Depends, Request
from schemas.business.logistic.bin_schema import BinPlainSchema, BinStrictSchema
from schemas.core.param_schema import (
    FilterParamsSchema,
    PaginatedResponseSchema,
    PaginationParamsSchema,
    SortingParamsSchema,
)
from services.business.logistic import BinService
from utils.auth import Auth
from utils.enums import Action
from utils.parsers import FilterParamsParser


class BinController(BaseController[BinService, BinStrictSchema, BinPlainSchema]):
    _input_schema_cls = BinStrictSchema
    _service_cls = BinService

    def __init__(self, context: Context, auth: Auth) -> None:
        super().__init__(context, auth)
        self._register_routes(
            output_schema=BinPlainSchema,
            include={
                Action.GET_ALL: True,
                Action.GET_BULK: True,
                Action.GET_ONE: True,
                Action.CREATE: True,
                Action.UPDATE: True,
                Action.DELETE: True,
            },
        )

    async def get_all(
        self,
        request: Request,
        pagination: Annotated[PaginationParamsSchema, Depends()],
        filters: Annotated[FilterParamsSchema, Depends(FilterParamsParser())],
        sorting: Annotated[SortingParamsSchema, Depends()],
    ) -> PaginatedResponseSchema[BinPlainSchema]:
        token_client = getattr(request.state, "token_client", None)
        if token_client == "mobile":
            token_warehouse_id = getattr(request.state, "token_warehouse_id", None)
            if isinstance(token_warehouse_id, int):
                filters.filters["warehouse_id"] = token_warehouse_id
            else:
                filters.filters["warehouse_id"] = 0
        return await super().get_all(request, pagination, filters, sorting)
