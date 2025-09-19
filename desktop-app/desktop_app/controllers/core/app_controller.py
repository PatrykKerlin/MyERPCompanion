from __future__ import annotations

from typing import TYPE_CHECKING


from controllers.base.base_controller import BaseController
from events.types import AppStarted, ApiReady, ApiNotResponding, TranslationLoaded, TranslationFailed, TranslationReady
from services.core.app_service import AppService
from views.core.app_view import AppView

if TYPE_CHECKING:
    from config.context import Context
    from views.components.loading_dialog_component import LoadingDialogComponent


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self._service = AppService(context.settings, context.logger)
        initial_texts = self._context.state_store.get().translation.items
        self._view = AppView(context.page, initial_texts)
        self.__loading_dialog: LoadingDialogComponent | None = None

        event_handlers = {
            AppStarted: self.__on_app_started,
            TranslationLoaded: self.__on_translation_loaded,
            TranslationReady: self.__on_translation_ready,
        }
        for event, handler in event_handlers.items():
            unsubscriber = self._context.event_bus.subscribe(event.event_type(), handler)
            self.add_unsubscriber(unsubscriber)

    async def __on_app_started(self, _: AppStarted) -> None:
        self.__loading_dialog = self._show_loading_dialog()
        api_ok = await self._service.api_health_check()
        if api_ok:
            await self._context.event_bus.publish(ApiReady())
            self._view.set_ready()
        else:
            self._context.logger.error("API health check failed")

    async def __on_translation_loaded(self, event: TranslationLoaded) -> None:
        items = getattr(event, "items", {})
        self._view.update_translation(items)

    async def __on_translation_ready(self, _: TranslationReady) -> None:
        if self.__loading_dialog:
            await self._close_dialog_with_delay(self.__loading_dialog)


# class AppController(BaseController):
#     def __init__(self, context: Context) -> None:
#         super().__init__(context)
#         self.__service = AppService(context)
#         self.__view = AppView(page=context.page, texts=context.texts, theme=context.settings.THEME)
#         self.__view.set_controller(self)

#     @property
#     def view_stack(self) -> ft.Stack:
#         return self.__view.view_stack

#     def show(self) -> None:
#         future = self._context.page.run_task(self.__run_startup_sequence)
#         future.add_done_callback(lambda _: self._context.page.run_thread(self.__show_auth_dialog))

#     def render_view(self, control: ft.Control) -> None:
#         self.__view.set_view_content(control)

#     def after_login(self) -> None:
#         self._run_with_delay(
#             condition=lambda: not self._context.page.overlay,
#             callback=self.__handle_post_login,
#         )

#     async def __handle_post_login(self) -> None:
#         user = self._context.user
#         if not user:
#             return

#         lang_changed = user.language.key != self._context.settings.LANGUAGE
#         self._context.settings.LANGUAGE = user.language.key
#         self._context.settings.THEME = user.theme.key

#         if lang_changed:
#             texts = await self.__service.fetch_texts()
#             self._context.texts.update(texts)

#         # await self.__service.save_settings_to_redis()
#         modules = await self.__service.fetch_modules()
#         self._context.modules.extend(modules)
#         self.__view.set_user(user)
#         endpoints, side_menu_content = self.__prepare_endpoints()
#         self._context.controllers.initialize_view_controllers(endpoints)
#         self._context.controllers.get("side_menu").set_content(side_menu_content)

#         self._context.page.run_thread(
#             self.__view.rebuild,
#             self._context.texts,
#             self._context.controllers.get("side_menu").get_new_component(),
#             self._context.controllers.get("toolbar").get_new_component(),
#             self._context.controllers.get("tabs_bar").get_new_component(),
#             self._context.controllers.get("footer").get_new_component(),
#         )

#         self._context.controllers.get("footer").start_clock()

#     async def __run_startup_sequence(self) -> None:
#         loading_dialog = self._show_loading_dialog()
#         try:
#             # await self.__service.check_redis_ready()
#             # await self.__service.load_settings_from_redis()
#             await self.__service.api_health_check()
#             texts = await self.__service.fetch_texts()
#             self._context.texts.update(texts)
#             self._close_dialog(loading_dialog)
#         except TimeoutError:
#             self._close_dialog(loading_dialog)
#             self._show_error_dialog(message_key="api_not_responding")

#     def __show_auth_dialog(self) -> None:
#         auth_dialog = self._context.controllers.get("auth_dialog").get_new_component()
#         self._open_dialog(auth_dialog)

#     def __prepare_endpoints(self) -> tuple[dict[str, ViewPlainSchema], dict[str, list[str]]]:
#         side_menu_content: dict[str, list[str]] = {}
#         endpoints: dict[str, ViewPlainSchema] = {}
#         user_groups = {group.id for group in self._context.user.groups}
#         for module in sorted(self._context.modules, key=lambda m: m.order):
#             module_groups = {group.id for group in module.groups}
#             if user_groups.intersection(module_groups):
#                 sorted_endpoints = sorted(
#                     [endpoint for endpoint in module.endpoints if endpoint.in_menu], key=lambda e: e.order
#                 )
#                 endpoints.update({endpoint.key: endpoint for endpoint in sorted_endpoints})
#                 side_menu_content[module.key] = [endpoint.key for endpoint in sorted_endpoints]
#         return endpoints, side_menu_content
