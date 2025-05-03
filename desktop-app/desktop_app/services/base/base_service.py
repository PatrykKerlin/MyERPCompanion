import httpx

from config import Settings


class BaseService:
    def __init__(self, settings: Settings) -> None:
        self.api_url = settings.API_URL

    async def _get(self, endpoint: str, params: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.api_url) as client:
            response = await client.get(url=endpoint, params=params)
            response.raise_for_status()
            return response

    async def _post(self, endpoint: str, payload: dict = {}) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.api_url) as client:
            response = await client.post(url=endpoint, json=payload)
            response.raise_for_status()
            return response
