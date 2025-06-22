from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from schemas.core import TokenInputSchema

if TYPE_CHECKING:
    from config.context import Context


class BaseService:
    def __init__(self, context: Context) -> None:
        self._context = context

    async def _get(self, endpoint: str, params: dict = {}, retry: bool = True) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            try:
                response = await client.get(url=endpoint, params=params)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as error:
                if error.response.status_code == httpx.codes.UNAUTHORIZED and retry:
                    await self.__refresh_token(error)
                    return await self._get(endpoint, params, False)
                raise

    async def _post(self, endpoint: str, payload: dict = {}, retry: bool = True) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            try:
                response = await client.post(url=endpoint, json=payload)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as error:
                if error.response.status_code == httpx.codes.UNAUTHORIZED and retry:
                    await self.__refresh_token(error)
                    return await self._post(endpoint, payload, False)
                raise

    async def _put(self, endpoint: str, payload: dict, retry: bool = True) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            try:
                response = await client.put(url=endpoint, json=payload)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as error:
                if error.response.status_code == httpx.codes.UNAUTHORIZED and retry:
                    await self.__refresh_token(error)
                    return await self._put(endpoint, payload, False)
                raise

    async def _delete(self, endpoint: str, retry: bool = True) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            try:
                response = await client.delete(url=endpoint)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as error:
                if error.response.status_code == httpx.codes.UNAUTHORIZED and retry:
                    await self.__refresh_token(error)
                    return await self._delete(endpoint, False)
                raise

    async def __refresh_token(self, error: httpx.HTTPStatusError) -> None:
        if not self._context.tokens or not self._context.tokens.refresh:
            raise error
        payload = {"refresh": self._context.tokens.refresh}
        try:
            async with httpx.AsyncClient(base_url=self._context.settings.API_URL) as client:
                response = await client.post("/refresh", json=payload)
                response.raise_for_status()
                new_access = response.json()["access"]
                self._context.tokens = TokenInputSchema(
                    access=new_access,
                    refresh=self._context.tokens.refresh,
                )
        except Exception:
            raise error

    def __prepare_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._context.tokens:
            headers["Authorization"] = f"Bearer {self._context.tokens.access}"
        return headers
