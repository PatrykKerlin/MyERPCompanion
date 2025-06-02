from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
import flet as ft

from controllers.base import BaseViewController
from services.core import AppService
from views.core import AppView

if TYPE_CHECKING:
    from config.context import Context


class AppController(BaseViewController[AppService]):
    _service_cls = AppService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__tab_views: dict[str, ft.Control] = {}
        self._view = AppView(page=context.page, texts=context.texts, theme=context.settings.THEME)
        self._view.set_controller(self)

    def show(self) -> None:
        future = self._context.page.run_task(self.__run_startup_sequence)
        future.add_done_callback(lambda _: self._context.page.run_thread(self.__show_auth_dialog))

    def after_login(self) -> None:
        async def delayed_execution() -> None:
            await asyncio.sleep(0.1)
            user = self._context.user
            if not user:
                return

            lang_changed = user.language.key != self._context.settings.LANGUAGE
            self._context.settings.LANGUAGE = user.language.key
            self._context.settings.THEME = user.theme.key

            if lang_changed:
                texts = await self._service.fetch_texts()
                self._context.texts.update(texts)

            await self._service.save_settings_to_redis()
            modules = await self._service.fetch_modules()
            self._context.modules.extend(modules)
            self._view.set_user(user)

            self._context.page.run_thread(
                self._view.rebuild,
                self._context.texts,
                self._context.controllers.get("side_menu").component,
                self._context.controllers.get("buttons_bar").component,
                self._context.controllers.get("tabs_bar").component,
            )

        self._context.page.run_task(delayed_execution)

    def render_view(self, control: ft.Control) -> None:
        self._view.set_view_content(control)

    async def __run_startup_sequence(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            await self._service.check_redis_ready()
            await self._service.load_settings_from_redis()
            await self._service.api_health_check()
            texts = await self._service.fetch_texts()
            self._context.texts.update(texts)
            self._close_dialog(loading_dialog)
        except TimeoutError:
            self._close_dialog(loading_dialog)
            self._show_error_dialog("api_not_responding")

    def __show_auth_dialog(self) -> None:
        auth_dialog_controller = self._context.controllers.get("auth_dialog")
        auth_dialog = auth_dialog_controller.component
        self._open_dialog(auth_dialog)
