from typing import Any

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.module_schema import ModulePlainSchema
from schemas.core.param_schema import IdsPayloadSchema
from schemas.core.token_schema import TokenPlainSchema
from schemas.core.user_schema import UserPlainSchema
from services.base.base_service import BaseService
from utils.enums import Endpoint


class AuthService(BaseService[BasePlainSchema, BaseStrictSchema]):
    _plain_schema_cls = BasePlainSchema

    async def fetch_tokens(
        self,
        username: str,
        password: str,
    ) -> TokenPlainSchema:
        payload: dict[str, Any] = {
            "username": username,
            "password": password,
            "client": self._settings.CLIENT,
        }
        response = await self._post(
            Endpoint.TOKEN,
            payload,
        )
        return TokenPlainSchema(**response.json())

    @BaseService.handle_token_refresh
    async def get_all_modules(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: BaseStrictSchema | list[BaseStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[ModulePlainSchema]:
        page = 1
        modules: list[ModulePlainSchema] = []
        params = {"page": page}

        while True:
            response = await self._get(endpoint=endpoint, query_params=params, tokens=tokens, module_id=module_id)
            data = response.json()
            modules.extend(ModulePlainSchema(**module) for module in data.get("items", []))
            if not data.get("has_next", False):
                break
            page += 1

        return modules

    @BaseService.handle_token_refresh
    async def get_current_user(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: BaseStrictSchema | list[BaseStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> UserPlainSchema:
        response = await self._get(endpoint=endpoint, tokens=tokens, module_id=module_id)
        return UserPlainSchema(**response.json(), is_superuser=False, password="")
