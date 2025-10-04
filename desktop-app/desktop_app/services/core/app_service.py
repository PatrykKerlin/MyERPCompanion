import asyncio
from utils.enums import Endpoint
from services.base.base_service import BaseService


class AppService(BaseService):
    async def api_health_check(self) -> bool:
        for _ in range(5):
            response = await self._get(Endpoint.HEALTH_CHECK)
            if response:
                return True
            await asyncio.sleep(1)
        return False
