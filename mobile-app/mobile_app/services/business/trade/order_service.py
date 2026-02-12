from __future__ import annotations

from typing import Any

from httpx import HTTPStatusError
from schemas.business.trade.order_schema import OrderPickingSummarySchema, OrderPlainSchema, OrderStrictSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class OrderService(BaseService[OrderPlainSchema, OrderStrictSchema]):
    _plain_schema_cls = OrderPlainSchema

    @BaseService.handle_token_refresh
    async def get_picking_summary(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: OrderStrictSchema | list[OrderStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> OrderPickingSummarySchema:
        try:
            response = await self._get(
                endpoint=endpoint,
                query_params=query_params,
                tokens=tokens,
                module_id=module_id,
            )
            return OrderPickingSummarySchema(**response.json())
        except HTTPStatusError as err:
            if err.response.status_code in {404, 422}:
                return OrderPickingSummarySchema()
            raise
