import httpx

from config import Context


class BaseService:
    def __init__(self, context: Context) -> None:
        self._context = context

    async def _get(self, endpoint: str, params: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL) as client:
            response = await client.get(url=endpoint, params=params)
            response.raise_for_status()
            return response

    async def _post(self, endpoint: str, payload: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self._context.settings.API_URL) as client:
            response = await client.post(url=endpoint, json=payload)
            response.raise_for_status()
            return response
