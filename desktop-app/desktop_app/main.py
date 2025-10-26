import flet as ft
import logging

from config.context import Context
from config.settings import Settings
from controllers.business import hr, logistic
from utils.enums import ViewMode
from utils.translation import Translation
from events.event_bus import EventBus
from states.state_store import StateStore

from controllers import core, components

from events.events import AppStarted
from states.states import AppState, TabsState, TranslationState, TokensState, UserState, ModulesState, ComponentsState

from controllers.base.base_controller import BaseController


class App:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        self.__settings = Settings()  # type: ignore
        self.__logger = logging.getLogger("app")
        self.__event_bus = EventBus(self.__logger)
        initial_state = AppState(
            translation=TranslationState(language=self.__settings.LANGUAGE, items=Translation()),
            tokens=TokensState(),
            user=UserState(),
            modules=ModulesState(items=[]),
            components=ComponentsState(),
            tabs=TabsState(current="", mode=ViewMode.SEARCH, items={}),
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
        self.__controllers = (
            # core
            core.AppController(self.__context),
            core.TranslationController(self.__context),
            components.AuthDialogController(self.__context),
            components.MenuBarController(self.__context),
            components.SideMenuController(self.__context),
            components.TabsBarController(self.__context),
            components.ToolbarController(self.__context),
            components.FooterController(self.__context),
            # hr
            hr.DepartmentController(self.__context),
            hr.PositionController(self.__context),
            hr.EmployeeController(self.__context),
            # logistic
            logistic.BinController(self.__context),
            logistic.CarrierController(self.__context),
            logistic.WarehouseController(self.__context),
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
