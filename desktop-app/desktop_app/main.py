import logging

import flet as ft

from config.settings import Settings
from controllers import components, core
from controllers.base.base_controller import BaseController
from controllers.business import hr, logistic, trade
from events.event_bus import EventBus
from events.events import AppStarted
from states.state_store import StateStore
from states.states import (
    AppState,
    ShellState,
    ModulesState,
    ViewState,
    TokensState,
    TranslationState,
    UserState,
)

from utils.enums import ViewMode
from utils.translation import Translation
from config.context import Context
from services.base.base_service import BaseService


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
            translation=TranslationState(
                language=self.__settings.LANGUAGE,
                items=Translation(),
            ),
            tokens=TokensState(),
            user=UserState(),
            modules=ModulesState(items=[]),
            shell=ShellState(),
            view=ViewState(
                title="",
                mode=ViewMode.NONE,
                view=None,
            ),
        )

        self.__state_store = StateStore(initial_state)
        self.__context: Context | None = None
        self.__controllers: list[BaseController] = []

    async def run(self, page: ft.Page) -> None:
        self.__context = Context(
            page=page,
            settings=self.__settings,
            logger=self.__logger,
            event_bus=self.__event_bus,
            state_store=self.__state_store,
        )
        app_controller = core.AppController(self.__context)
        core_controllers = [
            app_controller,
            core.TranslationController(self.__context),
            core.GroupController(self.__context),
            core.LanguageController(self.__context),
            core.ModuleController(self.__context),
            core.ViewController(self.__context),
            core.UserController(self.__context),
            components.AuthDialogController(self.__context),
            components.MenuBarController(self.__context),
            components.ToolbarController(self.__context),
            components.SideMenuController(self.__context),
            components.FooterController(self.__context),
            components.TabsBarController(self.__context),
        ]
        hr_controllers = [
            hr.DepartmentController(self.__context),
            hr.PositionController(self.__context),
            hr.EmployeeController(self.__context),
        ]
        logistic_controllers = [
            logistic.BinController(self.__context),
            logistic.BinTransferController(self.__context),
            logistic.CarrierController(self.__context),
            logistic.CategoryController(self.__context),
            logistic.DeliveryMethodController(self.__context),
            logistic.ItemController(self.__context),
            logistic.UnitController(self.__context),
            logistic.WarehouseController(self.__context),
        ]
        trade_controllers = [
            trade.CurrencyController(self.__context),
            trade.CustomerController(self.__context),
            trade.DiscountController(self.__context),
            trade.ExchangeRateController(self.__context),
            trade.OrderPickingController(self.__context),
            trade.PurchaseOrderController(self.__context),
            trade.SalesOrderController(self.__context),
            trade.StatusController(self.__context),
            trade.StockReceivingController(self.__context),
            trade.SupplierController(self.__context),
        ]
        self.__controllers = core_controllers + hr_controllers + logistic_controllers + trade_controllers
        page.window.on_event = self.__on_window_event
        page.render(lambda: app_controller.build_root())
        self.__event_bus.start()
        await self.__event_bus.publish(AppStarted())

    async def __on_window_event(self, event: ft.WindowEvent) -> None:
        if event.type == "close":
            await self.__dispose()

    async def __dispose(self) -> None:
        for controller in self.__controllers:
            await controller.dispose()
        self._controllers = ()
        await BaseService.close_client()
        await self.__event_bus.stop()


async def main(page: ft.Page) -> None:
    app = App()
    await app.run(page)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP)
