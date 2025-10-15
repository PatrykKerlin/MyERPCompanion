from __future__ import annotations

from logging import Logger
import asyncio
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar
from fastapi import HTTPException, status

import httpx

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.param_schema import PaginatedResponseSchema
from utils.enums import Endpoint
from schemas.core.token_schema import TokenPlainSchema
from utils.tokens_accessor import TokensAccessor

if TYPE_CHECKING:
    from config.settings import Settings

TPlainSchema = TypeVar("TPlainSchema", bound=BasePlainSchema)
TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)


class BaseService(Generic[TPlainSchema, TStrictSchema]):
    _plain_schema_cls: type[TPlainSchema]

    def __init__(self, settings: Settings, logger: Logger, tokens_accessor: TokensAccessor) -> None:
        self._settings = settings
        self._logger = logger
        self._tokens_accessor = tokens_accessor

    async def call_api_with_token_refresh(
        self,
        func: Callable[
            [Endpoint, int | None, dict[str, Any] | None, TStrictSchema | None, TokenPlainSchema | None, str | None],
            Any,
        ],
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        view_key: str | None = None,
    ) -> Any:
        tokens = self._tokens_accessor.read()
        if not tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            return await func(endpoint, path_param, query_params, body_params, tokens, view_key)
        except httpx.HTTPStatusError as first_error:
            self._logger.error(str(first_error))
            if first_error.response.status_code == httpx.codes.UNAUTHORIZED:
                try:
                    new_tokens = await self.refresh_tokens(tokens)
                    self._tokens_accessor.write(new_tokens)
                    return await func(endpoint, path_param, query_params, body_params, new_tokens, view_key)
                except Exception as refresh_error:
                    self._logger.error(str(refresh_error))
                    raise
            raise

    async def get_all(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> list[TPlainSchema]:
        page = 1
        items: list[TPlainSchema] = []
        params = {"page": page}

        while True:
            response = await self._get(endpoint=endpoint, query_params=params, token=token, view_key=view_key)
            data = response.json()
            items.extend([self._plain_schema_cls(**currency) for currency in data.get("items", [])])
            if not data.get("has_next", False):
                break
            page += 1

        return items

    async def get_page(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> PaginatedResponseSchema[TPlainSchema]:
        response = await self._get(endpoint=endpoint, query_params=query_params, token=token, view_key=view_key)
        data = response.json()
        return PaginatedResponseSchema[TPlainSchema](
            items=[self._plain_schema_cls(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 10),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    async def get_one(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> TPlainSchema:
        resolved_endpoint = f"{endpoint}/{path_param}"
        response = await self._get(endpoint=resolved_endpoint, token=token, view_key=view_key)
        data = response.json()
        return self._plain_schema_cls(**data)

    async def create(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> TPlainSchema:
        resolved_body_params = body_params.model_dump() if body_params else {}
        response = await self._post(endpoint=endpoint, body_params=resolved_body_params, token=token, view_key=view_key)
        data = response.json()
        return self._plain_schema_cls(**data)

    async def update(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> TPlainSchema:
        resolved_endpoint = f"{endpoint}/{path_param}"
        resolved_body_params = body_params.model_dump() if body_params else {}
        response = await self._put(
            endpoint=resolved_endpoint, body_params=resolved_body_params, token=token, view_key=view_key
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    async def delete(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | None = None,
        token: TokenPlainSchema | None = None,
        view_key: str | None = None,
    ) -> bool:
        resolved_endpoint = f"{endpoint}/{path_param}"
        await self._delete(endpoint=resolved_endpoint, token=token, view_key=view_key)
        return True

    async def refresh_tokens(self, token: TokenPlainSchema) -> TokenPlainSchema:
        payload = {"refresh": token.refresh}
        async with httpx.AsyncClient(base_url=self._settings.API_URL) as client:
            response = await client.post(Endpoint.REFRESH, json=payload)
            response.raise_for_status()
            new_access = response.json()["access"]
            await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.1)
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
            await asyncio.sleep(0.1)
            return response

    def __prepare_headers(self, token: TokenPlainSchema | None = None, view_key: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if token and token.access:
            headers["Authorization"] = f"Bearer {token.access}"
        if view_key:
            headers["X-View-Key"] = view_key
        return headers
