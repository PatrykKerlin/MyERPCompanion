from __future__ import annotations

from functools import wraps
from logging import Logger
from typing import Any, Awaitable, Callable, Generic, TypeVar

import httpx
from config.settings import Settings
from fastapi import HTTPException, status
from schemas.base.base_schema import BaseSchema, BaseStrictSchema
from schemas.core.param_schema import IdsPayloadSchema, PaginatedResponseSchema
from schemas.core.token_schema import TokenPlainSchema
from utils.enums import Endpoint
from utils.tokens_accessor import TokensAccessor

TPlainSchema = TypeVar("TPlainSchema", bound=BaseSchema)
TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)
TServiceSelf = TypeVar("TServiceSelf", bound="BaseService[Any, Any]")
TReturn = TypeVar("TReturn")


class BaseService(Generic[TPlainSchema, TStrictSchema]):
    _plain_schema_cls: type[TPlainSchema]
    _shared_client: httpx.AsyncClient | None = None

    def __init__(self, settings: Settings, logger: Logger, tokens_accessor: TokensAccessor) -> None:
        self._settings = settings
        self._logger = logger
        self._tokens_accessor = tokens_accessor

    @staticmethod
    def handle_token_refresh(
        func: Callable[
            [
                TServiceSelf,
                Endpoint,
                int | None,
                dict[str, Any] | None,
                TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None,
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
            TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None,
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
            body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None,
            module_id: int | None,
        ) -> TReturn:
            resolved_tokens = self._tokens_accessor.read()
            if not resolved_tokens:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            try:
                return await func(self, endpoint, path_param, query_params, body_params, resolved_tokens, module_id)
            except httpx.HTTPStatusError as first_error:
                self._logger.exception(f"HTTPStatusError in {func.__qualname__}")
                if first_error.response.status_code == httpx.codes.UNAUTHORIZED:
                    new_tokens = await self.refresh_tokens(resolved_tokens)
                    self._tokens_accessor.write(new_tokens)
                    return await func(self, endpoint, path_param, query_params, body_params, new_tokens, module_id)
                raise

        return wrapper

    @classmethod
    async def close_client(cls) -> None:
        if cls._shared_client and not cls._shared_client.is_closed:
            await cls._shared_client.aclose()
        cls._shared_client = None

    @handle_token_refresh
    async def create(
        self,
        endpoint: Endpoint,
        _path_param: int | None = None,
        _query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        if isinstance(body_params, BaseStrictSchema):
            resolved_body_params = body_params.model_dump(mode="json")
        else:
            resolved_body_params = None
        response = await self._post(
            endpoint=endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    @handle_token_refresh
    async def create_bulk(
        self,
        endpoint: Endpoint,
        _path_param: int | None = None,
        _query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> list[TPlainSchema]:
        resolved_body_params: list[dict[str, Any]] = []
        if isinstance(body_params, list):
            for item in body_params:
                if isinstance(item, BaseStrictSchema):
                    resolved_body_params.append(item.model_dump(mode="json"))
        response = await self._post(
            endpoint=endpoint,
            body_params=resolved_body_params,
            tokens=tokens,
            module_id=module_id,
        )
        data = response.json()
        return [self._plain_schema_cls(**item) for item in data]

    @handle_token_refresh
    async def get_all(
        self,
        endpoint: Endpoint,
        _path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        _body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None = None,
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
        _path_param: int | None = None,
        query_params: dict[str, Any] | None = None,
        _body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None = None,
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

    async def refresh_tokens(self, tokens: TokenPlainSchema) -> TokenPlainSchema:
        headers = self.__prepare_headers()
        headers["Authorization"] = f"Bearer {tokens.refresh}"
        client = self.__get_client()
        response = await client.get(Endpoint.REFRESH, headers=headers)
        response.raise_for_status()
        new_access = response.json()["access"]
        return TokenPlainSchema(access=new_access, refresh=tokens.refresh)

    @handle_token_refresh
    async def update(
        self,
        endpoint: Endpoint,
        path_param: int | None = None,
        _query_params: dict[str, Any] | None = None,
        body_params: TStrictSchema | list[TStrictSchema] | IdsPayloadSchema | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> TPlainSchema:
        if isinstance(body_params, BaseStrictSchema):
            resolved_body_params = body_params.model_dump(mode="json")
        else:
            resolved_body_params = {}
        resolved_endpoint = f"{endpoint}/{path_param}"
        response = await self._put(
            endpoint=resolved_endpoint, body_params=resolved_body_params, tokens=tokens, module_id=module_id
        )
        data = response.json()
        return self._plain_schema_cls(**data)

    async def _get(
        self,
        endpoint: str,
        query_params: dict[str, Any] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        client = self.__get_client()
        response = await client.get(url=endpoint, params=query_params, headers=headers)
        response.raise_for_status()
        return response

    async def _post(
        self,
        endpoint: str,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        client = self.__get_client()
        response = await client.post(url=endpoint, json=body_params, headers=headers)
        response.raise_for_status()
        return response

    async def _put(
        self,
        endpoint: str,
        body_params: dict[str, Any] | list[dict[str, Any]] | None = None,
        tokens: TokenPlainSchema | None = None,
        module_id: int | None = None,
    ) -> httpx.Response:
        headers = self.__prepare_headers(tokens, module_id)
        client = self.__get_client()
        response = await client.put(url=endpoint, json=body_params, headers=headers)
        response.raise_for_status()
        return response

    def __build_timeout(self) -> httpx.Timeout:
        return httpx.Timeout(connect=5.0, read=60.0, write=15.0, pool=5.0)

    def __get_client(self) -> httpx.AsyncClient:
        if BaseService._shared_client is None or BaseService._shared_client.is_closed:
            BaseService._shared_client = httpx.AsyncClient(
                base_url=self._settings.API_URL,
                timeout=self.__build_timeout(),
            )
        return BaseService._shared_client

    def __prepare_headers(self, tokens: TokenPlainSchema | None = None, module_id: int | None = None) -> dict[str, str]:
        headers = {"X-Client": self._settings.CLIENT}
        if tokens and tokens.access:
            headers["Authorization"] = f"Bearer {tokens.access}"
        if module_id:
            headers["X-View-Module"] = str(module_id)
        return headers
