from __future__ import annotations

import flet as ft
import asyncio
import logging
from typing import TYPE_CHECKING

from config.context import Context
from config.settings import Settings
from events.event_bus import EventBus
from states.state_store import StateStore

from controllers.core.app_controller import AppController
from controllers.core.translation_controller import TranslationController
from events.types import AppStarted
from states.states import AppState, TranslationState, TokenState

if TYPE_CHECKING:
    from controllers.base.base_controller import BaseController


class App:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        self.__settings = Settings()  # type: ignore
        self.__logger = logging.getLogger("app")
        self.__event_bus = EventBus()
        initial_state = AppState(
            translation=TranslationState.with_defaults(self.__settings.LANGUAGE), token=TokenState()
        )
        self.__state_store = StateStore(initial_state)
        self.__context: Context | None = None
        self.__controllers: tuple[BaseController, ...] = ()

    async def run(self, page: ft.Page) -> None:

        self.__context = Context(
            page=page,
            settings=self.__settings,
            logger=self.__logger,
            event_bus=self.__event_bus,
            state_store=self.__state_store,
        )
        self.__event_bus.start()
        self.__controllers = (AppController(self.__context), TranslationController(self.__context))
        await self.__event_bus.publish(AppStarted())

    async def dispose(self) -> None:
        for controller in self.__controllers:
            await controller.dispose()
        self._controllers = ()
        await self.__event_bus.stop()


async def main(page: ft.Page) -> None:
    app = App()
    await app.run(page)


if __name__ == "__main__":
    app = App()
    asyncio.run(ft.app_async(target=main))
