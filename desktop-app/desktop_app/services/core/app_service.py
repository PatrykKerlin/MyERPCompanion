from __future__ import annotations

import asyncio
import getpass
import socket
from typing import TYPE_CHECKING, Awaitable, cast

from httpx import HTTPError
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

from schemas.core import ModuleInputSchema
from services.base import BaseService

if TYPE_CHECKING:
    from config.context import Context


class AppService(BaseService):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        system_username = getpass.getuser()
        system_host = socket.gethostname()
        self.system_id = f"{system_username}@{system_host}"

    async def check_redis_ready(self) -> None:
        redis = self.__get_redis()
        for _ in range(2):
            try:
                if await redis.ping():
                    return
            except ConnectionError:
                await asyncio.sleep(1)
            finally:
                await redis.close()
        raise TimeoutError("Redis is not responding.")

    async def load_settings_from_redis(self) -> None:
        redis = self.__get_redis()
        try:
            raw_language = redis.hget(self.system_id, "LANGUAGE")
            raw_theme = redis.hget(self.system_id, "THEME")
            language = await cast(Awaitable[str | None], raw_language)
            theme = await cast(Awaitable[str | None], raw_theme)
            if language:
                self._context.settings.LANGUAGE = language
            if theme:
                self._context.settings.THEME = theme
        finally:
            await redis.close()

    async def save_settings_to_redis(self) -> None:
        redis = self.__get_redis()
        try:
            hset_result = redis.hset(
                self.system_id,
                mapping={
                    "LANGUAGE": self._context.settings.LANGUAGE,
                    "THEME": self._context.settings.THEME,
                },
            )
            await cast(Awaitable[int], hset_result)
        finally:
            await redis.close()

    async def api_health_check(self) -> None:
        for _ in range(2):
            try:
                await self._get("/health-check")
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
            texts.update({item["key"]: item["value"] for item in data.get("items", [])})
            if not data.get("has_next", False):
                break
            page += 1

        return texts

    async def fetch_modules(self) -> list[ModuleInputSchema]:
        page = 1
        page_size = 100
        modules: list[ModuleInputSchema] = []

        while True:
            response = await self._get("modules", params={"page": page, "page_size": page_size})
            data = response.json()
            modules.extend(ModuleInputSchema(**module) for module in data.get("items", []))
            if not data.get("has_next", False):
                break
            page += 1

        return modules

    def __get_redis(self) -> Redis:
        return Redis(
            host=self._context.settings.REDIS_HOST,
            port=self._context.settings.REDIS_PORT,
            db=self._context.settings.REDIS_DB,
            password=self._context.settings.REDIS_PASSWORD,
            decode_responses=True,
        )
