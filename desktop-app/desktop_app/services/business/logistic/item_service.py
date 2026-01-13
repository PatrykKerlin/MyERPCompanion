from typing import Any
from schemas.business.logistic.item_schema import ItemPlainSchema, ItemStrictSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class ItemService(BaseService[ItemPlainSchema, ItemStrictSchema]):
    _plain_schema_cls = ItemPlainSchema

    async def post_many(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: ItemStrictSchema | dict[str, list[int]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[ItemPlainSchema]:
        full_endpoint = f"{endpoint}/many"
        if isinstance(body_params, dict):
            resolved_body_params = body_params
        else:
            resolved_body_params = {}
        response = await self._post(
            endpoint=full_endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return [self._plain_schema_cls.model_validate(item) for item in data]
