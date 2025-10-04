from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from utils.enums import Endpoint
from schemas.core.token_schema import TokenPlainSchema

if TYPE_CHECKING:
    from config.settings import Settings


class BaseService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def refresh_token(self, token: TokenPlainSchema) -> TokenPlainSchema:
        payload = {"refresh": token.refresh}
        async with httpx.AsyncClient(base_url=self._settings.API_URL) as client:
            response = await client.post(Endpoint.REFRESH, json=payload)
            response.raise_for_status()
            new_access = response.json()["access"]
            return TokenPlainSchema(access=new_access, refresh=token.refresh)

    async def _get(
        self,
        endpoint: str,
        query_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(token, view_key)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.get(url=endpoint, params=query_params)
            response.raise_for_status()
            return response

    async def _post(
        self,
        endpoint: str,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(token, view_key)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.post(url=endpoint, json=body_params)
            response.raise_for_status()
            return response

    async def _put(
        self,
        endpoint: str,
        body_params: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(token, view_key)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.put(url=endpoint, json=body_params)
            response.raise_for_status()
            return response

    async def _delete(
        self,
        endpoint: str,
        _: dict[str, Any] | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(token, view_key)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.delete(url=endpoint)
            response.raise_for_status()
            return response

    def __prepare_headers(self, token: TokenPlainSchema | None = None, view_key: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if token and token.access:
            headers["Authorization"] = f"Bearer {token.access}"
        if view_key:
            headers["X-View-Key"] = view_key
        return headers
