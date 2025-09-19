from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Callable, Awaitable, Any

import httpx

# from config.enums import Endpoint
# from schemas.core import TokenPlainSchema

if TYPE_CHECKING:
    from logging import Logger
    from config.settings import Settings


class BaseService:
    def __init__(self, settings: Settings, logger: Logger) -> None:
        self._settings = settings
        self._logger = logger

    async def _get(self, endpoint: str, params: dict[str, Any] | None = None, retry: bool = True) -> httpx.Response:
        return await self.__call_with_refresh(self.__perform_get, endpoint, params, retry)

    async def _post(self, endpoint: str, params: dict[str, Any] | None = None, retry: bool = True) -> httpx.Response:
        return await self.__call_with_refresh(self.__perform_post, endpoint, params, retry)

    async def _put(self, endpoint: str, params: dict[str, Any] | None = None, retry: bool = True) -> httpx.Response:
        return await self.__call_with_refresh(self.__perform_put, endpoint, params, retry)

    async def _delete(self, endpoint: str, params: dict[str, Any] | None = None, retry: bool = True) -> httpx.Response:
        return await self.__call_with_refresh(self.__perform_delete, endpoint, params, retry)

    async def __call_with_refresh(
        self,
        func: Callable[[str, dict[str, Any] | None], Awaitable[httpx.Response]],
        endpoint: str,
        query_or_body: dict[str, Any] | None,
        retry: bool,
    ) -> httpx.Response:
        try:
            return await func(endpoint, query_or_body)
        except httpx.HTTPStatusError as first_error:
            self._logger.error(str(first_error))
            if first_error.response.status_code == httpx.codes.UNAUTHORIZED and retry:
                # try:
                #     await self.__refresh_token(error)
                # except Exception as refresh_error:
                #     self._logger.exception(str(refresh_error))
                #     raise
                try:
                    return await func(endpoint, query_or_body)
                except httpx.HTTPError as second_error:
                    self._logger.error(str(second_error))
                    raise
            raise
        except httpx.HTTPError as error:
            self._logger.error(str(error))
            raise

    async def __perform_get(self, endpoint: str, params: dict[str, Any] | None) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.get(url=endpoint, params=params)
            response.raise_for_status()
            return response

    async def __perform_post(self, endpoint: str, payload: dict[str, Any] | None) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.post(url=endpoint, json=payload)
            response.raise_for_status()
            return response

    async def __perform_put(self, endpoint: str, payload: dict[str, Any] | None) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.put(url=endpoint, json=payload)
            response.raise_for_status()
            return response

    async def __perform_delete(self, endpoint: str, _: dict[str, Any] | None) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._settings.API_URL, headers=headers) as client:
            response = await client.delete(url=endpoint)
            response.raise_for_status()
            return response

    # async def __refresh_token(self, error: httpx.HTTPStatusError) -> None:
    #     if not self._context.tokens or not self._context.tokens.refresh:
    #         raise error
    #     payload = {"refresh": self._context.tokens.refresh}
    #     try:
    #         async with httpx.AsyncClient(base_url=self._context.API_URL) as client:
    #             response = await client.post(Endpoint.REFRESH, json=payload)
    #             response.raise_for_status()
    #             new_access = response.json()["access"]
    #             self._context.tokens = TokenPlainSchema(
    #                 access=new_access,
    #                 refresh=self._context.tokens.refresh,
    #             )
    #     except Exception:
    #         raise error

    def __prepare_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        # if self._context.tokens:
        #     headers["Authorization"] = f"Bearer {self._context.tokens.access}"
        return headers
