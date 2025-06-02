from __future__ import annotations
from typing import TYPE_CHECKING
import httpx

if TYPE_CHECKING:
    from config.context import Context


class BaseService:
    def __init__(self, context: Context) -> None:
        self._context = context

    async def _get(self, endpoint: str, params: dict = {}) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            response = await client.get(url=endpoint, params=params)
            response.raise_for_status()
            return response

    async def _post(self, endpoint: str, payload: dict = {}) -> httpx.Response:
        headers = self.__prepare_headers()
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL, headers=headers) as client:
            response = await client.post(url=endpoint, json=payload)
            response.raise_for_status()
            return response

    def __prepare_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._context.tokens:
            headers["Authorization"] = f"Bearer {self._context.tokens.access}"
        return headers
