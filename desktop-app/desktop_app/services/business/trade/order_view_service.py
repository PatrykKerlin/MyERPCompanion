from __future__ import annotations

from typing import Any

from schemas.base.base_schema import BaseStrictSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.business.trade.order_view_schema import OrderViewResponseSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class OrderViewService(BaseService[OrderViewResponseSchema, BaseStrictSchema]):
    _plain_schema_cls = OrderViewResponseSchema

    @BaseService.handle_token_refresh
    async def get_view(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: BaseStrictSchema | list[BaseStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> OrderViewResponseSchema:
        resolved_endpoint = f"{endpoint}/{path_param}" if path_param is not None else str(endpoint)
        response = await self._get(endpoint=resolved_endpoint, tokens=tokens, module_id=module_id)
        data = response.json()
        print(data)
        return self._plain_schema_cls(**data)
