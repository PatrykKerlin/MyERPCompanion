import logging
import os

import flet as ft

from config.settings import Settings
from controllers import components, core, web
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

        self.__settings = Settings(CLIENT="web")  # type: ignore
        self.__logger = logging.getLogger("app")
        self.__contexts: dict[int, Context] = {}
        self.__controllers_by_session: dict[int, list[BaseController]] = {}
        self.__event_bus_by_session: dict[int, EventBus] = {}

    async def run(self, page: ft.Page) -> None:
        session_id = id(page)
        event_bus = EventBus(self.__logger)
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
        state_store = StateStore(initial_state)
        context = Context(
            page=page,
            settings=self.__settings,
            logger=self.__logger,
            event_bus=event_bus,
            state_store=state_store,
        )
        self.__contexts[session_id] = context
        self.__event_bus_by_session[session_id] = event_bus
        app_controller = core.AppController(context)
        core_controllers = [
            app_controller,
            core.TranslationController(context),
            core.GroupController(context),
            core.LanguageController(context),
            core.ModuleController(context),
            core.UserController(context),
            components.AuthDialogController(context),
            components.MenuBarController(context),
            components.ToolbarController(context),
            components.SideMenuController(context),
            components.FooterController(context),
            components.TabsBarController(context),
        ]
        web_controllers = [
            web.CreateOrderController(context),
            web.OrdersController(context),
        ]
        hr_controllers = [
            hr.DepartmentController(context),
            hr.PositionController(context),
            hr.EmployeeController(context),
        ]
        logistic_controllers = [
            logistic.BinController(context),
            logistic.BinTransferController(context),
            logistic.CarrierController(context),
            logistic.CategoryController(context),
            logistic.DeliveryMethodController(context),
            logistic.ItemController(context),
            logistic.UnitController(context),
            logistic.WarehouseController(context),
        ]
        trade_controllers = [
            trade.CurrencyController(context),
            trade.CustomerController(context),
            trade.DiscountController(context),
            trade.ExchangeRateController(context),
            trade.InvoiceController(context),
            trade.OrderPickingController(context),
            trade.PurchaseOrderController(context),
            trade.SalesOrderController(context),
            trade.StatusController(context),
            trade.StockReceivingController(context),
            trade.SupplierController(context),
        ]
        self.__controllers_by_session[session_id] = (
            core_controllers + web_controllers + hr_controllers + logistic_controllers + trade_controllers
        )
        async def on_window_event(event: ft.WindowEvent) -> None:
            await self.__on_window_event(session_id, event)

        page.window.on_event = on_window_event
        page.render(lambda: app_controller.build_root())
        event_bus.start()
        await event_bus.publish(AppStarted())

    async def __on_window_event(self, session_id: int, event: ft.WindowEvent) -> None:
        if event.type == "close":
            await self.__dispose(session_id)

    async def __dispose(self, session_id: int) -> None:
        if session_id not in self.__controllers_by_session and session_id not in self.__event_bus_by_session:
            return
        controllers = self.__controllers_by_session.get(session_id, [])
        for controller in controllers:
            await controller.dispose()
        self.__controllers_by_session.pop(session_id, None)
        self.__contexts.pop(session_id, None)
        event_bus = self.__event_bus_by_session.pop(session_id, None)
        await BaseService.close_client()
        if event_bus:
            await event_bus.stop()


def main() -> None:
    app = App()
    os.environ.setdefault("FLET_FORCE_WEB_SERVER", "1")
    host = os.getenv("FLET_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("FLET_SERVER_PORT", "8550"))
    view = getattr(ft.AppView, "WEB_SERVER", ft.AppView.WEB_BROWSER)
    ft.run(app.run, view=view, host=host, port=port)


if __name__ == "__main__":
    main()
