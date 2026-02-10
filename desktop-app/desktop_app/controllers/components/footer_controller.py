from __future__ import annotations

import asyncio
from contextlib import suppress
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
        self.__status_task: asyncio.Task[None] | None = None
        self.__clock_task: asyncio.Task[None] | None = None
        self.__disposing = False
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
        if self.__disposing:
            return
        translation_state = self._state_store.app_state.translation
        self._component = FooterComponent(controller=self, translation=translation_state.items)
        await self._event_bus.publish(FooterReady(self._component))

    async def dispose(self) -> None:
        self.__disposing = True
        await self.__cancel_task(self.__status_task)
        await self.__cancel_task(self.__clock_task)
        self.__status_task = None
        self.__clock_task = None
        self._component = None
        await super().dispose()

    def __shell_updated_listener(self, state: ShellState) -> None:
        if self.__disposing:
            return
        if state.is_shell_ready:
            self.__ensure_background_tasks()

    def __ensure_background_tasks(self) -> None:
        if self.__disposing:
            return
        if self.__status_task is None or self.__status_task.done():
            self.__status_task = asyncio.create_task(self.__status_loop())
        if self.__clock_task is None or self.__clock_task.done():
            self.__clock_task = asyncio.create_task(self.__clock_loop())

    async def __status_loop(self) -> None:
        try:
            while not self.__disposing:
                await self._event_bus.publish(ApiStatusRequested())
                await asyncio.sleep(self._settings.API_CHECK_DELAY)
        except asyncio.CancelledError:
            raise
        except RuntimeError as error:
            if "destroyed session" in str(error).lower():
                return
            raise

    async def __clock_loop(self) -> None:
        try:
            while not self.__disposing:
                if self._component:
                    now = self.__get_local_time().strftime("%Y-%m-%d %H:%M:%S")
                    self._component.set_time(now)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise
        except RuntimeError as error:
            if "destroyed session" in str(error).lower():
                return
            raise

    async def __api_status_handler(self, event: ApiStatusChecked) -> None:
        if self.__disposing:
            return
        if self._component:
            self._component.set_status(event.status)

    def __get_local_time(self) -> datetime:
        timezone_name = getattr(self._settings, "TIMEZONE", None)
        if timezone_name:
            try:
                return datetime.now(ZoneInfo(timezone_name))
            except Exception:
                self._logger.exception("Invalid TIMEZONE setting: %s", timezone_name)
        return datetime.now().astimezone()

    @staticmethod
    async def __cancel_task(task: asyncio.Task[None] | None) -> None:
        if task is None or task.done():
            return
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
