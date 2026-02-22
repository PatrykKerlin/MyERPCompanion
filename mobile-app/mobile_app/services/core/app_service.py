import asyncio

from services.base.base_service import BaseService
from utils.enums import Endpoint


class AppService(BaseService):
    async def api_health_check(self) -> None:
        last_error: Exception | None = None
        for _ in range(5):
            try:
                await self._get(Endpoint.HEALTH_CHECK)
                return
            except Exception as err:
                last_error = err
                await asyncio.sleep(1)
        if last_error:
            raise last_error
