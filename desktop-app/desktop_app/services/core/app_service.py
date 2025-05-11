import asyncio
import getpass
import socket
from typing import cast, Awaitable, Any
from httpx import HTTPError
from services.base import BaseService
from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from config import Context, Settings


class AppService(BaseService):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        system_username = getpass.getuser()
        system_host = socket.gethostname()
        self.system_id = f"{system_username}@{system_host}"

    async def check_redis_ready(self) -> None:
        redis = self.__get_redis()
        for _ in range(10):
            try:
                if await redis.ping():
                    await asyncio.sleep(1)
                    return
            except ConnectionError:
                await asyncio.sleep(1)
            finally:
                await redis.close()
        raise TimeoutError("Redis is not responding.")

    async def load_settings_from_redis(self) -> None:
        redis = self.__get_redis()
        try:
            data = await cast(Awaitable[dict[Any, Any]], redis.hgetall(self.system_id))
            if data:
                self._context.settings = Settings.model_validate(data)
        finally:
            await redis.close()

    async def save_settings_to_redis(self) -> None:
        redis = Redis(decode_responses=True)
        try:
            cast(Awaitable[int], redis.hset(self.system_id, mapping=self._context.settings.model_dump()))
        finally:
            await redis.close()

    async def api_health_check(self) -> None:
        for _ in range(10):
            try:
                await self._get("/health-check")
                await asyncio.sleep(1)
                return
            except HTTPError:
                await asyncio.sleep(1)
        raise TimeoutError("API is not responding.")

    async def fetch_texts(self) -> dict[str, str]:
        page = 1
        page_size = 100
        texts: dict[str, str] = {}

        while True:
            response = await self._get(
                f"texts/by-language/{self._context.settings.LANGUAGE}", params={"page": page, "page_size": page_size}
            )
            data = response.json()
            texts.update({item["name"]: item["value"] for item in data.get("items", [])})
            if not data.get("has_next", False):
                break
            page += 1

        await asyncio.sleep(1)
        return texts

    def __get_redis(self) -> Redis:
        return Redis(
            host=self._context.settings.REDIS_HOST,
            port=self._context.settings.REDIS_PORT,
            db=self._context.settings.REDIS_DB,
            password=self._context.settings.REDIS_PASSWORD,
            decode_responses=True,
        )
