from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import asyncio

from controllers.base import BaseComponentController
from services.core import AppService
from views.components import FooterComponent

if TYPE_CHECKING:
    from config.context import Context


class FooterController(BaseComponentController[AppService, FooterComponent]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__footer: FooterComponent | None = None
        self.__service = AppService(context)

    def get_new_component(self) -> FooterComponent:
        self.__footer = FooterComponent(self, self._context.texts)
        return self.__footer

    def start_clock(self) -> None:
        self._run_with_delay(
            condition=lambda: self.__footer is not None
            and self.__footer.timestamp.page is not None
            and self.__footer.status_message.page is not None
            and self.__footer.status_icon.page is not None,
            callback=self.__start_background_tasks,
        )

    async def __start_background_tasks(self) -> None:
        await asyncio.gather(
            self.__refresh_time(),
            self.__refresh_api_status(),
        )

    async def __refresh_time(self) -> None:
        while True:
            if not self.__footer:
                continue
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__footer.set_time(now)
            await asyncio.sleep(1)

    async def __refresh_api_status(self) -> None:
        while True:
            if not self.__footer:
                continue
            try:
                await self.__service.api_health_check()
                self.__footer.set_status(True)
            except Exception:
                self.__footer.set_status(False)
            await asyncio.sleep(60)
