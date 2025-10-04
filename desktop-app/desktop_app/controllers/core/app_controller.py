from __future__ import annotations

from typing import TYPE_CHECKING, Any


from controllers.base.base_controller import BaseController
from events.base.base_event import BaseEvent
from events.events import (
    ApiStatusChecked,
    ApiStatusRequested,
    AppStarted,
    MenuBarRequested,
    TranslationFailed,
    TranslationReady,
    TranslationRequested,
    AuthDialogRequested,
    UserAuthenticated,
    SideMenuRequested,
    FooterRequested,
    FooterMounted,
    TabsBarRequested,
    ToolbarRequested,
)
from services.core.app_service import AppService
from states.states import TabsState
from views.core.app_view import AppView

if TYPE_CHECKING:
    from config.context import Context
    from states.states import ComponentsState, TranslationState
    from views.components.loading_dialog_component import LoadingDialogComponent
    from views.components.footer_component import FooterComponent
    from views.components.menu_bar_component import MenuBarComponent
    from views.components.side_menu_component import SideMenuComponent
    from views.components.tabs_bar_component import TabsBarComponent
    from views.components.toolbar_component import ToolbarComponent


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        translation_state = self._state_store.app_state.translation
        self.__service = AppService(self._settings)
        self.__view = AppView(self._page, translation_state.items, self._settings.THEME)
        self.__loading_dialog: LoadingDialogComponent | None = None

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
                ApiStatusRequested: self.__api_status_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "translation": self.__translation_updated_listener,
                "components": self.__components_changed_listener,
                "tabs": self.__tabs_updated_listener,
            }
        )

    def __translation_updated_listener(self, state: TranslationState) -> None:
        self.__view.update_translation(state.items)

    def __components_changed_listener(self, state: ComponentsState) -> None:
        def on_dialog_closed(_: Any) -> None:
            if state.menu_bar and state.side_menu and state.tabs_bar and state.toolbar and state.footer:
                self.__rebuild_view(state.menu_bar, state.side_menu, state.toolbar, state.tabs_bar, state.footer)
                if self.__loading_dialog:
                    self.__loading_dialog.on_dismiss = None

        if self.__loading_dialog and self.__loading_dialog.open:
            self.__loading_dialog.on_dismiss = on_dialog_closed
        elif state.menu_bar and state.side_menu and state.tabs_bar and state.toolbar and state.footer:
            self.__rebuild_view(state.menu_bar, state.side_menu, state.toolbar, state.tabs_bar, state.footer)

    def __tabs_updated_listener(self, state: TabsState) -> None:
        self.__view.set_view_content(state.items[state.current])

    async def __app_started_handler(self, _: AppStarted) -> None:
        self.__loading_dialog = self._show_loading_dialog()
        api_status = await self.__service.api_health_check()
        initial_language = self._settings.LANGUAGE
        if api_status:
            await self._event_bus.publish(TranslationRequested(initial_language, False))
        else:
            self._logger.error("API health check failed")

    async def __api_status_handler(self, _: ApiStatusRequested) -> None:
        api_status = await self.__service.api_health_check()
        await self._event_bus.publish(ApiStatusChecked(status=api_status))

    async def __translation_ready_handler(self, event: TranslationReady) -> None:
        if self.__loading_dialog:
            await self._close_dialog_with_delay(self.__loading_dialog)
        if not event.user_authenticated:
            await self._event_bus.publish(AuthDialogRequested())

    async def __api_not_responding_handler(self, _: BaseEvent):
        if self.__loading_dialog:
            await self._close_dialog_with_delay(self.__loading_dialog)
        self._show_error_dialog("api_not_responding")

    async def __user_authenticated_handler(self, _: UserAuthenticated) -> None:
        user = self._state_store.app_state.user.current
        translation = self._state_store.app_state.translation
        if not user:
            self._logger.error("User error")
            return
        if user.language.symbol != translation.language:
            self.__loading_dialog = self._show_loading_dialog()
            await self._event_bus.publish(TranslationRequested(user.language.symbol, True))
        await self._event_bus.publish(MenuBarRequested())
        await self._event_bus.publish(SideMenuRequested())
        await self._event_bus.publish(ToolbarRequested())
        await self._event_bus.publish(TabsBarRequested())
        await self._event_bus.publish(FooterRequested())

    def __rebuild_view(
        self,
        menu_bar: MenuBarComponent,
        side_menu: SideMenuComponent,
        toolbar: ToolbarComponent,
        tabs_bar: TabsBarComponent,
        footer: FooterComponent,
    ) -> None:
        self.__view.rebuild(menu_bar, side_menu, toolbar, tabs_bar, footer)
        self._page.run_task(self._event_bus.publish, FooterMounted())


#     def __show_auth_dialog(self) -> None:
#         auth_dialog = self._context.controllers.get("auth_dialog").get_new_component()
#         self._open_dialog(auth_dialog)
