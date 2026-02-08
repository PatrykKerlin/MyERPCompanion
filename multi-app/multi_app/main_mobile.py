import logging

import flet as ft

from config.context import Context
from config.settings import Settings
from controllers.base.base_controller import BaseController
from controllers.components.auth_dialog_controller import AuthDialogController
from controllers.core.translation_controller import TranslationController
from controllers.mobile.app_controller import AppController
from events.event_bus import EventBus
from events.events import AppStarted
from services.base.base_service import BaseService
from states.state_store import StateStore
from states.states import (
    AppState,
    ModulesState,
    TokensState,
    TranslationState,
    UserState,
    ViewState,
)
from utils.enums import ViewMode
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
            modules=ModulesState(items=[]),
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
        platform = getattr(page, "platform", None)
        platform_value = getattr(platform, "value", str(platform)).lower()
        if platform_value in {"linux", "windows", "macos"}:
            target_width = 393
            target_height = 852
            if hasattr(page.window, "width"):
                page.window.width = target_width
            if hasattr(page.window, "height"):
                page.window.height = target_height
            if hasattr(page.window, "min_width"):
                page.window.min_width = target_width
            if hasattr(page.window, "min_height"):
                page.window.min_height = target_height
            if hasattr(page.window, "max_width"):
                page.window.max_width = target_width
            if hasattr(page.window, "max_height"):
                page.window.max_height = target_height
            if hasattr(page.window, "resizable"):
                page.window.resizable = False
            if hasattr(page.window, "maximizable"):
                page.window.maximizable = False

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


async def main(page: ft.Page) -> None:
    app = App()
    await app.run(page)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP)
