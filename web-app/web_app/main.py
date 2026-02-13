import logging
import os
from pathlib import Path

import flet as ft
from config.context import Context
from config.settings import Settings
from controllers.base.base_controller import BaseController
from controllers.core.app_controller import AppController
from controllers.core.auth_controller import AuthController
from controllers.core.create_order_controller import CreateOrderController
from controllers.core.orders_controller import OrdersController
from controllers.core.translation_controller import TranslationController
from events.event_bus import EventBus
from events.events import AppStarted
from services.base.base_service import BaseService
from states.state_store import StateStore
from states.states import AppState, ModulesState, TokensState, TranslationState, UserState, ViewState
from utils.enums import ViewMode
from utils.translation import Translation
from utils.user_settings import UserSettings


class App:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

        self.__logger = logging.getLogger("app")
        self.__contexts: dict[int, Context] = {}
        self.__controllers_by_session: dict[int, list[BaseController]] = {}
        self.__event_bus_by_session: dict[int, EventBus] = {}

    async def run(self, page: ft.Page) -> None:
        preferred_theme, preferred_language = await UserSettings.load_web()
        settings_kwargs: dict[str, str] = {}
        if preferred_theme:
            settings_kwargs["THEME"] = preferred_theme
        if preferred_language:
            settings_kwargs["LANGUAGE"] = preferred_language
        session_settings = Settings(**settings_kwargs)  # type: ignore
        session_id = id(page)
        event_bus = EventBus(self.__logger)
        initial_state = AppState(
            translation=TranslationState(
                language=session_settings.LANGUAGE,
                items=Translation(),
            ),
            tokens=TokensState(),
            user=UserState(),
            modules=ModulesState(items=[]),
            view=ViewState(
                title="",
                mode=ViewMode.NONE,
                view=None,
            ),
        )
        state_store = StateStore(initial_state)
        context = Context(
            page=page,
            settings=session_settings,
            logger=self.__logger,
            event_bus=event_bus,
            state_store=state_store,
        )
        self.__contexts[session_id] = context
        self.__event_bus_by_session[session_id] = event_bus
        app_controller = AppController(context)
        web_controllers: list[BaseController] = [
            app_controller,
            TranslationController(context),
            AuthController(context),
            CreateOrderController(context),
            OrdersController(context),
        ]
        self.__controllers_by_session[session_id] = web_controllers

        async def on_window_event(event: ft.WindowEvent) -> None:
            await self.__on_window_event(session_id, event)

        page.window.on_event = on_window_event
        page.render(lambda: app_controller.build_root())
        event_bus.start()
        await event_bus.publish(AppStarted())

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

    async def __on_window_event(self, session_id: int, event: ft.WindowEvent) -> None:
        if event.type == "close":
            await self.__dispose(session_id)


def main() -> None:
    app = App()
    os.environ.setdefault("FLET_FORCE_WEB_SERVER", "1")
    host = os.getenv("FLET_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("FLET_SERVER_PORT", "8550"))
    view = getattr(ft.AppView, "WEB_SERVER", ft.AppView.WEB_BROWSER)
    assets_dir = Path(__file__).resolve().parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    ft.run(app.run, view=view, host=host, port=port, assets_dir=str(assets_dir))


if __name__ == "__main__":
    main()
