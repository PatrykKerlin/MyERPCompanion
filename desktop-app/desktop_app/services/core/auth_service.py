from typing import Any
from schemas.core.user_schema import UserPlainSchema
from schemas.core.token_schema import TokenPlainSchema
from services.base.base_service import BaseService
from schemas.core.module_schema import ModulePlainSchema
from utils.enums import Endpoint


class AuthService(BaseService):
    async def fetch_tokens(self, username: str, password: str) -> TokenPlainSchema:
        response = await self._post(Endpoint.TOKEN, {"username": username, "password": password})

        return TokenPlainSchema(**response.json())

    async def fetch_modules(
        self,
        path_param: str | None = None,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> list[ModulePlainSchema]:
        page = 1
        modules: list[ModulePlainSchema] = []
        endpoint = Endpoint.MODULES
        params = {"page": page}
        if path_param:
            endpoint += f"/{path_param}"
        if query_params:
            params.update(query_params)

        while True:
            response = await self._get(endpoint=endpoint, query_params=params, token=token, view_key=view_key)
            data = response.json()
            modules.extend(ModulePlainSchema(**module) for module in data.get("items", []))
            if not data.get("has_next", False):
                break
            page += 1

        return modules

    async def fetch_current_user(
        self,
        path_param: str | None = None,
        _: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> UserPlainSchema:
        endpoint = Endpoint.CURRENT_USER
        if path_param:
            endpoint += f"/{path_param}"
        response = await self._get(endpoint=endpoint, token=token, view_key=view_key)

        return UserPlainSchema(**response.json(), is_superuser=False, password="")
