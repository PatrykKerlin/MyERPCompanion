from __future__ import annotations

from functools import wraps
from logging import Logger
import asyncio
from typing import Any, Awaitable, Callable, Generic, TypeVar
from fastapi import HTTPException, status

import httpx

from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from schemas.core.param_schema import PaginatedResponseSchema
from utils.enums import Endpoint
from schemas.core.token_schema import TokenPlainSchema
from utils.tokens_accessor import TokensAccessor
from config.settings import Settings

TPlainSchema = TypeVar("TPlainSchema", bound=BasePlainSchema)
TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)
TServiceSelf = TypeVar("TServiceSelf", bound="BaseService[Any, Any]")
TReturn = TypeVar("TReturn")


class BaseService(Generic[TPlainSchema, TStrictSchema]):
    _plain_schema_cls: type[TPlainSchema]

    def __init__(self, settings: Settings, logger: Logger, tokens_accessor: TokensAccessor) -> None:
        self._settings = settings
        self._logger = logger
        self._tokens_accessor = tokens_accessor
        self.__sleep_time = 0

    @staticmethod
    def handle_token_refresh(
        func: Callable[
            [
                TServiceSelf,
                Endpoint,
                int | None,
                dict[str, Any] | None,
                TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None,
                TokenPlainSchema | None,
                int | None,
            ],
            Awaitable[TReturn],
        ],
    ) -> Callable[
        [
            TServiceSelf,
            Endpoint,
            int | None,
            dict[str, Any] | None,
            TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None,
            int | None,
        ],
        Awaitable[TReturn],
    ]:
        @wraps(func)
        async def wrapper(
            self: TServiceSelf,
            endpoint: Endpoint,
            path_param: int | None,
            query_params: dict[str, Any] | None,
            body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None,
            module_id: int | None,
        ) -> TReturn:
            resolved_tokens = self._tokens_accessor.read()
            if not resolved_tokens:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            try:
                return await func(self, endpoint, path_param, query_params, body_params, resolved_tokens, module_id)
            except httpx.HTTPStatusError as first_error:
                self._logger.error(str(first_error))
                if first_error.response.status_code == httpx.codes.UNAUTHORIZED:
                    new_tokens = await self.refresh_tokens(resolved_tokens)
                    self._tokens_accessor.write(new_tokens)
                    return await func(self, endpoint, path_param, query_params, body_params, new_tokens, module_id)
                raise

        return wrapper

    @handle_token_refresh
    async def get_all(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[TPlainSchema]:
        params: dict[str, Any] = {"page": 1}
        if query_params:
            params.update(query_params)
        items: list[TPlainSchema] = []
        while True:
            response = await self._get(endpoint=endpoint, query_params=params, tokens=tokens, module_id=module_id)
            data = response.json()
            items.extend([self._plain_schema_cls(**item) for item in data.get("items", [])])
            if not data.get("has_next", False):
                break
            params["page"] += 1

        return items

    @handle_token_refresh
    async def get_page(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> PaginatedResponseSchema[TPlainSchema]:
        response = await self._get(endpoint=endpoint, query_params=query_params, tokens=tokens, module_id=module_id)
        data = response.json()
        return PaginatedResponseSchema[TPlainSchema](
            items=[self._plain_schema_cls(**item) for item in data.get("items", [])],
            total=data.get("total", 0),
            page=data.get("page", 1),
            page_size=data.get("page_size", 10),
            has_next=data.get("has_next", False),
            has_prev=data.get("has_prev", False),
        )

    @handle_token_refresh
    async def get_one(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        resolved_endpoint = f"{endpoint}/{path_param}"
        response = await self._get(endpoint=resolved_endpoint, tokens=tokens, module_id=module_id)
        data = response.json()
        return self._plain_schema_cls(**data)

    @handle_token_refresh
    async def get_bulk(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[TPlainSchema]:
        if isinstance(body_params, dict):
            resolved_body_params = body_params
        else:
            resolved_body_params = {}
        response = await self._post(
            endpoint=endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return [self._plain_schema_cls(**item) for item in data]

    @handle_token_refresh
    async def create(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        if isinstance(body_params, dict):
            resolved_body_params = body_params
        elif isinstance(body_params, BaseStrictSchema):
            resolved_body_params = body_params.model_dump()
        else:
            resolved_body_params = {}
        response = await self._post(
            endpoint=endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    @handle_token_refresh
    async def create_multipart(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        if isinstance(body_params, dict):
            data = body_params.get("data")
            files = body_params.get("files")
        else:
            data = None
            files = None
        response = await self._post_multipart(
            endpoint=endpoint,
            data=data,
            files=files,
            tokens=tokens,
            module_id=module_id,
        )
        payload = response.json()
        return self._plain_schema_cls(**payload)

    @handle_token_refresh
    async def update(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        if isinstance(body_params, dict):
            resolved_body_params = body_params
        elif isinstance(body_params, BaseStrictSchema):
            resolved_body_params = body_params.model_dump()
        else:
            resolved_body_params = {}
        resolved_endpoint = f"{endpoint}/{path_param}"
        response = await self._put(
            endpoint=resolved_endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    @handle_token_refresh
    async def update_bulk(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[TPlainSchema]:
        resolved_body_params: list[dict[str, Any]] = []
        if isinstance(body_params, list):
            for item in body_params:
                schema_item = item
                if isinstance(schema_item, BaseStrictSchema):
                    param = schema_item.model_dump()
                    param["id"] = schema_item.id
                else:
                    param = schema_item
                resolved_body_params.append(param)
        response = await self._put(
            endpoint=endpoint,
            body_params=resolved_body_params,
            tokens=tokens,
            module_id=module_id,
        )
        data = response.json()
        return [self._plain_schema_cls(**item) for item in data]

    @handle_token_refresh
    async def create_bulk(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[TPlainSchema]:
        resolved_body_params: list[dict[str, Any]] = []
        if isinstance(body_params, list):
            for item in body_params:
                if isinstance(item, BaseStrictSchema):
                    resolved_body_params.append(item.model_dump())
                elif isinstance(item, dict):
                    resolved_body_params.append(item)
        elif isinstance(body_params, dict):
            resolved_body_params.append(body_params)
        response = await self._post(
            endpoint=endpoint,
            body_params=resolved_body_params,
            tokens=tokens,
            module_id=module_id,
        )
        data = response.json()
        return [self._plain_schema_cls(**item) for item in data]

    @handle_token_refresh
    async def delete(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> bool:
        resolved_endpoint = f"{endpoint}/{path_param}"
        await self._delete(endpoint=resolved_endpoint, tokens=tokens, module_id=module_id)
        return True

    @handle_token_refresh
    async def delete_bulk(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> bool:
        if isinstance(body_params, dict):
            resolved_body_params = body_params
        else:
            resolved_body_params = {}
        await self._post(endpoint=endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id)
        return True

    async def refresh_tokens(self, tokens: TokenPlainSchema) -> TokenPlainSchema:
        headers = {"Authorization": f"Bearer {tokens.refresh}"}
        async with httpx.AsyncClient(base_url=self._settings.API_URL) as client:
            response = await client.get(Endpoint.REFRESH, headers=headers)
            response.raise_for_status()
            new_access = response.json()["access"]
            await asyncio.sleep(self.__sleep_time)
            return TokenPlainSchema(access=new_access, refresh=tokens.refresh)

    async def _get(
        self,
        endpoint: str,
        query_params: dict[str, Any] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.get(url=endpoint, params=query_params)
            response.raise_for_status()
            await asyncio.sleep(self.__sleep_time)
            return response

    async def _post(
        self,
        endpoint: str,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.post(url=endpoint, json=body_params)
            response.raise_for_status()
            await asyncio.sleep(self.__sleep_time)
            return response

    async def _post_multipart(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.post(url=endpoint, data=data, files=files)
            response.raise_for_status()
            await asyncio.sleep(self.__sleep_time)
            return response

    async def _put(
        self,
        endpoint: str,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.put(url=endpoint, json=body_params)
            response.raise_for_status()
            await asyncio.sleep(self.__sleep_time)
            return response

    async def _delete(
        self,
        endpoint: str,
        _: dict[str, Any] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.delete(url=endpoint)
            response.raise_for_status()
            await asyncio.sleep(self.__sleep_time)
            return response

    def __prepare_headers(self, tokens: TokenPlainSchema | None = None, module_id: int | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if tokens and tokens.access:
            headers["Authorization"] = f"Bearer {tokens.access}"
        if module_id:
            headers["X-View-Module"] = str(module_id)
        return headers
