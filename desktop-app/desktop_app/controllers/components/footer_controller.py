from __future__ import annotations

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from views.components.footer_component import FooterComponent
from events.events import ApiStatusChecked, ApiStatusRequested, FooterRequested, FooterMounted

if TYPE_CHECKING:
    from config.context import Context


class FooterController(BaseComponentController[FooterComponent, FooterRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                FooterRequested: self._component_requested_handler,
                ApiStatusChecked: self.__api_status_handler,
                FooterMounted: self.__component_mounted_handler,
            }
        )

    async def _component_requested_handler(self, _: FooterRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = FooterComponent(controller=self, translation=translation_state.items)
        self._state_store.update(components={"footer": self._component})

    async def __refresh_status(self, status: bool = True) -> None:
        if not self._component:
            return
        self._component.set_status(status)
        await asyncio.sleep(60)
        await self._event_bus.publish(ApiStatusRequested())

    async def __refresh_time(self) -> None:
        if not self._component:
            return
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._component.set_time(now)
            await asyncio.sleep(1)

    async def __api_status_handler(self, event: ApiStatusChecked) -> None:
        await self.__refresh_status(event.status)

    async def __component_mounted_handler(self, _: FooterMounted) -> None:
        asyncio.create_task(self.__refresh_status())
        asyncio.create_task(self.__refresh_time())
