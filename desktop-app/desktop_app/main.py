from __future__ import annotations

import flet as ft
import asyncio
import logging
from typing import TYPE_CHECKING

from config.context import Context
from config.settings import Settings
from controllers.business.hr.department_controller import DepartmentController
from utils.translation import Translation
from events.event_bus import EventBus
from states.state_store import StateStore

from controllers.core.app_controller import AppController
from controllers.core.translation_controller import TranslationController
from controllers.components.auth_dialog_controller import AuthDialogController
from controllers.components.menu_bar_controller import MenuBarController
from controllers.components.side_menu_controller import SideMenuController
from controllers.components.tabs_bar_controller import TabsBarController
from controllers.components.toolbar_controller import ToolbarController
from controllers.components.footer_controller import FooterController

from events.events import AppStarted
from events.view_events import DepartmentViewRequested
from states.states import AppState, TabsState, TranslationState, TokensState, UserState, ModulesState, ComponentsState

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
            translation=TranslationState(language=self.__settings.LANGUAGE, items=Translation()),
            tokens=TokensState(),
            user=UserState(),
            modules=ModulesState(items=[]),
            components=ComponentsState(),
            tabs=TabsState(current="", items={}),
        )
        self.__state_store = StateStore(initial_state)
        self.__context: Context | None = None
        self.__controllers: tuple[BaseController, ...] = ()

    async def run(self, page: ft.Page) -> None:
        view_event_map = {"departments": DepartmentViewRequested}
        self.__context = Context(
            page=page,
            settings=self.__settings,
            logger=self.__logger,
            event_bus=self.__event_bus,
            state_store=self.__state_store,
            view_event_map=view_event_map,
        )
        self.__event_bus.start()
        self.__controllers = (
            # core
            AppController(self.__context),
            TranslationController(self.__context),
            AuthDialogController(self.__context),
            MenuBarController(self.__context),
            SideMenuController(self.__context),
            TabsBarController(self.__context),
            ToolbarController(self.__context),
            FooterController(self.__context),
            # business
            DepartmentController(self.__context),
        )
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
    ft.app(target=main)
