from __future__ import annotations
from typing import TYPE_CHECKING
import flet as ft

from controllers.base import BaseController
from services.core import AppService
from views.core import AppView

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.endpoint_schema import EndpointInputSchema


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(context)
        self.__view = AppView(page=context.page, texts=context.texts, theme=context.settings.THEME)
        self.__view.set_controller(self)

    def show(self) -> None:
        future = self._context.page.run_task(self.__run_startup_sequence)
        future.add_done_callback(lambda _: self._context.page.run_thread(self.__show_auth_dialog))

    def render_view(self, control: ft.Control) -> None:
        self.__view.set_view_content(control)

    def after_login(self) -> None:
        self._run_with_delay(
            condition=lambda: not self._context.page.overlay,
            callback=self.__handle_post_login,
        )

    async def __handle_post_login(self) -> None:
        user = self._context.user
        if not user:
            return

        lang_changed = user.language.key != self._context.settings.LANGUAGE
        self._context.settings.LANGUAGE = user.language.key
        self._context.settings.THEME = user.theme.key

        if lang_changed:
            texts = await self.__service.fetch_texts()
            self._context.texts.update(texts)

        await self.__service.save_settings_to_redis()
        modules = await self.__service.fetch_modules()
        self._context.modules.extend(modules)
        self.__view.set_user(user)
        endpoints, side_menu_content = self.__prepare_endpoints()
        self._context.controllers.initialize_view_controllers(endpoints)
        side_menu_controller = self._context.controllers.get("side_menu")
        side_menu_controller.set_content(side_menu_content)

        self._context.page.run_thread(
            self.__view.rebuild,
            self._context.texts,
            side_menu_controller.component,
            self._context.controllers.get("buttons_bar").component,
            self._context.controllers.get("tabs_bar").component,
            self._context.controllers.get("footer_bar").component,
        )

        self._context.controllers.get("footer_bar").start_clock()

    async def __run_startup_sequence(self) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            await self.__service.check_redis_ready()
            await self.__service.load_settings_from_redis()
            await self.__service.api_health_check()
            texts = await self.__service.fetch_texts()
            self._context.texts.update(texts)
            self._close_dialog(loading_dialog)
        except TimeoutError:
            self._close_dialog(loading_dialog)
            self._show_error_dialog(message_key="api_not_responding")

    def __show_auth_dialog(self) -> None:
        auth_dialog_controller = self._context.controllers.get("auth_dialog")
        auth_dialog = auth_dialog_controller.component
        self._open_dialog(auth_dialog)

    def __prepare_endpoints(self) -> tuple[dict[str, EndpointInputSchema], dict[str, list[str]]]:
        side_menu_content: dict[str, list[str]] = {}
        endpoints: dict[str, EndpointInputSchema] = {}
        user_groups = {group.id for group in self._context.user.groups}
        for module in sorted(self._context.modules, key=lambda m: m.order):
            module_groups = {group.id for group in module.groups}
            if user_groups.intersection(module_groups):
                sorted_endpoints = sorted(
                    [endpoint for endpoint in module.endpoints if endpoint.in_menu], key=lambda e: e.order
                )
                endpoints.update({endpoint.key: endpoint for endpoint in sorted_endpoints})
                side_menu_content[module.key] = [endpoint.key for endpoint in sorted_endpoints]
        return endpoints, side_menu_content
