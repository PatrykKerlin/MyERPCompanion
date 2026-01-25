from __future__ import annotations

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING

from controllers.base.base_component_controller import BaseComponentController
from states.states import ShellState
from views.components.footer_component import FooterComponent
from events.events import ApiStatusChecked, ApiStatusRequested, FooterReady, FooterRequested

if TYPE_CHECKING:
    from config.context import Context


class FooterController(BaseComponentController[FooterComponent, FooterRequested]):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._subscribe_event_handlers(
            {
                FooterRequested: self._component_requested_handler,
                ApiStatusChecked: self.__api_status_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "shell": self.__shell_updated_listener,
            }
        )

    async def _component_requested_handler(self, _: FooterRequested) -> None:
        translation_state = self._state_store.app_state.translation
        self._component = FooterComponent(controller=self, translation=translation_state.items)
        await self._event_bus.publish(FooterReady(self._component))

    def __shell_updated_listener(self, state: ShellState) -> None:
        if state.is_shell_ready:
            asyncio.create_task(self.__refresh_status())
            asyncio.create_task(self.__refresh_time())

    async def __refresh_status(self, status: bool = True) -> None:
        if not self._component:
            return
        self._component.set_status(status)
        await asyncio.sleep(self._settings.API_CHECK_DELAY)
        await self._event_bus.publish(ApiStatusRequested())

    async def __refresh_time(self) -> None:
        if not self._component:
            return
        while True:
            now = self.__get_local_time().strftime("%Y-%m-%d %H:%M:%S")
            self._component.set_time(now)
            await asyncio.sleep(1)

    async def __api_status_handler(self, event: ApiStatusChecked) -> None:
        await self.__refresh_status(event.status)

    def __get_local_time(self) -> datetime:
        timezone_name = getattr(self._settings, "TIMEZONE", None)
        if timezone_name:
            try:
                return datetime.now(ZoneInfo(timezone_name))
            except Exception:
                self._logger.exception("Invalid TIMEZONE setting: %s", timezone_name)
        return datetime.now().astimezone()
