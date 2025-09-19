# from __future__ import annotations

import asyncio
from config.enums import Endpoint
from schemas.core import ModulePlainSchema
from services.base.base_service import BaseService


class AppService(BaseService):
    async def api_health_check(self) -> bool:
        for _ in range(5):
            response = await self._get(Endpoint.HEALTH_CHECK)
            if response:
                return True
            await asyncio.sleep(1)
        return False


#     async def fetch_modules(self) -> list[ModulePlainSchema]:
#         page = 1
#         page_size = 100
#         modules: list[ModulePlainSchema] = []

#         while True:
#             response = await self._get("modules", params={"page": page, "page_size": page_size})
#             data = response.json()
#             modules.extend(ModulePlainSchema(**module) for module in data.get("items", []))
#             if not data.get("has_next", False):
#                 break
#             page += 1

#         return modules

#     # def __init__(self, context: Context) -> None:
#     #     super().__init__(context)
#     #     system_username = getpass.getuser()
#     #     system_host = socket.gethostname()
#     # self.__system_id = f"{system_username}@{system_host}"

#     # async def check_redis_ready(self) -> None:
#     #     redis = self.__get_redis()
#     #     for _ in range(2):
#     #         try:
#     #             if await redis.ping():
#     #                 return
#     #         except ConnectionError:
#     #             await asyncio.sleep(1)
#     #         finally:
#     #             await redis.close()
#     #     raise TimeoutError("Redis is not responding.")

#     # async def load_settings_from_redis(self) -> None:
#     #     redis = self.__get_redis()
#     #     try:
#     #         raw_language = redis.hget(self.__system_id, "LANGUAGE")
#     #         raw_theme = redis.hget(self.__system_id, "THEME")
#     #         language = await cast(Awaitable[str | None], raw_language)
#     #         theme = await cast(Awaitable[str | None], raw_theme)
#     #         if language:
#     #             self._context.settings.LANGUAGE = language
#     #         if theme:
#     #             self._context.settings.THEME = theme
#     #     finally:
#     #         await redis.close()

#     # async def save_settings_to_redis(self) -> None:
#     #     redis = self.__get_redis()
#     #     try:
#     #         hset_result = redis.hset(
#     #             self.__system_id,
#     #             mapping={
#     #                 "LANGUAGE": self._context.settings.LANGUAGE,
#     #                 "THEME": self._context.settings.THEME,
#     #             },
#     #         )
#     #         await cast(Awaitable[int], hset_result)
#     #     finally:
#     #         await redis.close()

#     # def __get_redis(self) -> Redis:
#     #     return Redis(
#     #         host=self._context.settings.REDIS_HOST,
#     #         port=self._context.settings.REDIS_PORT,
#     #         db=self._context.settings.REDIS_DB,
#     #         password=self._context.settings.REDIS_PASSWORD,
#     #         decode_responses=True,
#     #     )
