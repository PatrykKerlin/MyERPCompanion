import logging
import os

import flet as ft
from config.context import Context
from config.settings import Settings
from controllers.base.base_controller import BaseController
from controllers.components.auth_dialog_controller import AuthDialogController
from controllers.core.app_controller import AppController
from controllers.core.bin_transfer_controller import BinTransferController
from controllers.core.bins_controller import BinsController
from controllers.core.items_controller import ItemsController
from controllers.core.order_picking_controller import OrderPickingController
from controllers.core.stock_receiving_controller import StockReceivingController
from controllers.core.translation_controller import TranslationController
from controllers.core.user_controller import UserController
from events.event_bus import EventBus
from events.events import AppStarted
from services.base.base_service import BaseService
from states.state_store import StateStore
from states.states import (
    AppState,
    TokensState,
    TranslationState,
    UserState,
)
from utils.translation import Translation
from utils.user_settings import UserSettings


class App:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        preferred_theme, preferred_language = UserSettings.load()
        settings_kwargs: dict[str, str] = {"CLIENT": "mobile"}
        if preferred_theme:
            settings_kwargs["THEME"] = preferred_theme
        if preferred_language:
            settings_kwargs["LANGUAGE"] = preferred_language
        self.__settings = Settings(**settings_kwargs)  # type: ignore
        self.__logger = logging.getLogger("app")
        self.__event_bus = EventBus(self.__logger)

        initial_state = AppState(
            translation=TranslationState(
                language=self.__settings.LANGUAGE,
                items=Translation(),
            ),
            tokens=TokensState(),
            user=UserState(),
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
        app_controller = AppController(self.__context)
        self.__controllers = [
            app_controller,
            BinsController(self.__context),
            ItemsController(self.__context),
            BinTransferController(self.__context),
            OrderPickingController(self.__context),
            StockReceivingController(self.__context),
            UserController(self.__context),
            TranslationController(self.__context),
            AuthDialogController(self.__context),
        ]
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
        self.__controllers = []
        await BaseService.close_client()
        await self.__event_bus.stop()


def main() -> None:
    app = App()
    os.environ.setdefault("FLET_FORCE_WEB_SERVER", "1")
    host = os.getenv("FLET_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("FLET_SERVER_PORT", "8552"))
    view = getattr(ft.AppView, "WEB_SERVER", ft.AppView.WEB_BROWSER)
    ft.run(app.run, view=view, host=host, port=port)


if __name__ == "__main__":
    main()
