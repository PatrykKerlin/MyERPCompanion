from __future__ import annotations

from typing import TYPE_CHECKING
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
    from views.components.footer_component import FooterComponent
    from views.components.menu_bar_component import MenuBarComponent
    from views.components.side_menu_component import SideMenuComponent
    from views.components.tabs_bar_component import TabsBarComponent
    from views.components.toolbar_component import ToolbarComponent


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        translation_state = self._state_store.app_state.translation
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__view = AppView(self._page, translation_state.items, self._settings.THEME)

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
        if state.menu_bar and state.side_menu and state.tabs_bar and state.toolbar and state.footer:
            self._page.run_task(
                self.__rebuild_view, state.menu_bar, state.side_menu, state.toolbar, state.tabs_bar, state.footer
            )

    def __tabs_updated_listener(self, state: TabsState) -> None:
        self.__view.set_view_content(state.current, state.items)
        if not state.items or not state.current or state.current not in state.items:
            return
        print(f"{state.current} -> {state.mode}")
        if state.items[state.current].page:
            self._page.run_task(self._run_with_delay, lambda: state.items[state.current].set_mode(state.mode))

    async def __app_started_handler(self, _: AppStarted) -> None:
        self._open_loading_dialog()
        try:
            await self.__service.api_health_check()
            initial_language = self._settings.LANGUAGE
            await self._event_bus.publish(TranslationRequested(initial_language, False))
        except Exception as err:
            self._logger.error(str(err))
            self._open_error_dialog(message_key="api_not_responding")

    async def __api_status_handler(self, _: ApiStatusRequested) -> None:
        try:
            await self.__service.api_health_check()
            await self._event_bus.publish(ApiStatusChecked(status=True))
        except Exception as err:
            self._logger.error(str(err))
            await self._event_bus.publish(ApiStatusChecked(status=False))

    async def __translation_ready_handler(self, event: TranslationReady) -> None:
        self._close_loading_dialog()
        if not event.user_authenticated:
            await self._event_bus.publish(AuthDialogRequested())

    async def __api_not_responding_handler(self, _: BaseEvent):
        self._close_loading_dialog()
        self._open_error_dialog(message_key="api_not_responding")

    async def __user_authenticated_handler(self, _: UserAuthenticated) -> None:
        user = self._state_store.app_state.user.current
        if user:
            translation = self._state_store.app_state.translation
            if user.language.symbol != translation.language:
                self._open_loading_dialog()
                await self._event_bus.publish(TranslationRequested(user.language.symbol, True))
            await self._event_bus.publish(MenuBarRequested())
            await self._event_bus.publish(SideMenuRequested())
            await self._event_bus.publish(ToolbarRequested())
            await self._event_bus.publish(TabsBarRequested())
            await self._event_bus.publish(FooterRequested())

    async def __rebuild_view(
        self,
        menu_bar: MenuBarComponent,
        side_menu: SideMenuComponent,
        toolbar: ToolbarComponent,
        tabs_bar: TabsBarComponent,
        footer: FooterComponent,
    ) -> None:
        self._close_loading_dialog()
        await self._run_with_delay(lambda: self.__view.rebuild(menu_bar, side_menu, toolbar, tabs_bar, footer))
        await self._event_bus.publish(FooterMounted())
