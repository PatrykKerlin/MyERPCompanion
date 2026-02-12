from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from controllers.base.base_controller import BaseController
from events.base.base_event import BaseEvent
from events.events import (
    ApiStatusChecked,
    ApiStatusRequested,
    AppStarted,
    AuthDialogRequested,
    AuthViewReady,
    CallerActionRequested,
    FooterReady,
    FooterRequested,
    LogoutRequested,
    MenuBarReady,
    MenuBarRequested,
    SideMenuReady,
    SideMenuRequested,
    TabCloseAllRequested,
    TabClosed,
    TabsBarReady,
    TabsBarRequested,
    TabsBarToggleRequested,
    ToolbarReady,
    ToolbarRequested,
    ToolbarToggleRequested,
    TranslationFailed,
    TranslationReady,
    TranslationRequested,
    UserAuthenticated,
)
from services.core.app_service import AppService
from services.core.auth_service import AuthService
from states.states import ViewState
from utils.enums import ApiActionError, Endpoint, Module, View, ViewMode
from utils.user_settings import UserSettings
from views.core.app_view import AppView as DesktopAppView

if TYPE_CHECKING:
    from config.context import Context
    from schemas.core.user_schema import UserPlainSchema
    from states.states import ShellState, TranslationState, UserState


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__auth_service = AuthService(self._settings, self._logger, self._tokens_accessor)
        self.__view = DesktopAppView(self._state_store.app_state.translation.items, self._settings.THEME)

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
                CallerActionRequested: self.__caller_action_handler,
                LogoutRequested: self.__logout_requested_handler,
                ApiStatusRequested: self.__api_status_handler,
                AuthViewReady: self.__auth_view_ready_handler,
                MenuBarReady: self.__menu_bar_ready_handler,
                ToolbarReady: self.__toolbar_ready_handler,
                SideMenuReady: self.__side_menu_ready_handler,
                FooterReady: self.__footer_ready_handler,
                TabsBarReady: self.__tabs_bar_ready_handler,
                TabClosed: self.__tab_closed_handler,
                ToolbarToggleRequested: self.__toolbar_toggle_handler,
                TabsBarToggleRequested: self.__tabs_bar_toggle_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "translation": self.__translation_updated_listener,
                "shell": self.__shell_updated_listener,
                "view": self.__view_updated_listener,
                "user": self.__user_updated_listener,
            }
        )

    def build_root(self) -> ft.Control:
        return self.__view.build()

    def __translation_updated_listener(self, state: TranslationState) -> None:
        self.__view.update_translation(state.items)
        self._page.update()

    async def __app_started_handler(self, _: AppStarted) -> None:
        await self._open_loading_dialog()
        ok = await self.__perform_api_health_check()
        if ok:
            await self._event_bus.publish(TranslationRequested(self._settings.LANGUAGE, False))
            return
        self._open_error_dialog(message_key="api_not_responding")

    async def __api_status_handler(self, _: ApiStatusRequested) -> None:
        ok = await self.__perform_api_health_check()
        await self._event_bus.publish(ApiStatusChecked(status=bool(ok)))

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_api_health_check(self) -> bool:
        await self.__service.api_health_check()
        return True

    async def __translation_ready_handler(self, event: TranslationReady) -> None:
        self._close_loading_dialog()
        if event.user_authenticated:
            await self.__request_shell()
            return
        await self._event_bus.publish(AuthDialogRequested())

    async def __api_not_responding_handler(self, _: BaseEvent) -> None:
        self._close_loading_dialog()
        self._open_error_dialog(message_key="api_not_responding")

    async def __user_authenticated_handler(self, _: UserAuthenticated) -> None:
        user = self._state_store.app_state.user.current
        if not user:
            return
        self.__view.set_auth_view(None)
        self.__apply_user_preferences(user)
        self._page.update()

        translation_state = self._state_store.app_state.translation
        if user.language.symbol == translation_state.language:
            await self.__request_shell()
            return

        await self._open_loading_dialog()
        await self._event_bus.publish(TranslationRequested(user.language.symbol, True))

    async def __auth_view_ready_handler(self, event: AuthViewReady) -> None:
        self.__view.set_auth_view(event.component)
        self._page.update()

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        await self._event_bus.publish(TabCloseAllRequested())
        self.__view.set_shell_visible(False)
        self.__reset_shell_state()
        self._state_store.update(
            view={"title": "", "mode": ViewMode.NONE, "view": None},
            modules={"items": []},
            user={"current": None},
            tokens={"access": None, "refresh": None},
        )
        await self._event_bus.publish(AuthDialogRequested())

    async def __caller_action_handler(self, event: CallerActionRequested) -> None:
        if event.caller_view_key != View.CURRENT_USER:
            return
        if event.source_view_key != View.USERS:
            return
        current_user = await self.__perform_get_current_user()
        if not current_user:
            return
        self._state_store.update(user={"current": current_user})
        current_language = self._state_store.app_state.translation.language
        target_language = current_user.language.symbol
        if target_language != current_language:
            await self._open_loading_dialog()
            await self._event_bus.publish(TranslationRequested(target_language, True))

    async def __menu_bar_ready_handler(self, event: MenuBarReady) -> None:
        self.__view.set_menu_bar(event.component)
        self._state_store.update(shell={"is_menu_bar_ready": True})

    async def __toolbar_ready_handler(self, event: ToolbarReady) -> None:
        self.__view.set_toolbar(event.component)
        self._state_store.update(shell={"is_toolbar_ready": True})

    async def __side_menu_ready_handler(self, event: SideMenuReady) -> None:
        self.__view.set_side_menu(event.component)
        self._state_store.update(shell={"is_side_menu_ready": True})

    async def __footer_ready_handler(self, event: FooterReady) -> None:
        self.__view.set_footer(event.component)
        self._state_store.update(shell={"is_footer_ready": True})

    async def __tabs_bar_ready_handler(self, event: TabsBarReady) -> None:
        self.__view.set_tabs_bar(event.component)
        self._state_store.update(shell={"is_tabs_bar_ready": True})

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        self.__view.remove_stack_item(event.view)

    async def __toolbar_toggle_handler(self, _: ToolbarToggleRequested) -> None:
        self.__view.toggle_toolbar_visible()
        self._page.update()

    async def __tabs_bar_toggle_handler(self, _: TabsBarToggleRequested) -> None:
        self.__view.toggle_tabs_bar_visible()
        self._page.update()

    def __shell_updated_listener(self, state: ShellState) -> None:
        has_user = self._state_store.app_state.user.current is not None
        self.__view.set_shell_visible(state.is_shell_ready and has_user)
        self._page.update()

    def __view_updated_listener(self, state: ViewState) -> None:
        self.__view.set_stack_item(state.view)
        self._page.update()

    def __user_updated_listener(self, state: UserState) -> None:
        user = state.current
        if not user:
            return
        UserSettings.save(user.theme, user.language.symbol)
        self.__apply_user_preferences(user)
        self._page.update()

    def __apply_user_preferences(self, user: UserPlainSchema) -> None:
        self.__view.set_theme(user.theme)

    def __reset_shell_state(self) -> None:
        self._state_store.update(
            shell={
                "is_menu_bar_ready": False,
                "is_toolbar_ready": False,
                "is_side_menu_ready": False,
                "is_footer_ready": False,
                "is_tabs_bar_ready": False,
            }
        )

    async def __request_shell(self) -> None:
        self.__view.set_shell_visible(False)
        self.__reset_shell_state()
        await self._event_bus.publish(MenuBarRequested())
        await self._event_bus.publish(ToolbarRequested())
        await self._event_bus.publish(SideMenuRequested())
        await self._event_bus.publish(FooterRequested())
        await self._event_bus.publish(TabsBarRequested())

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_current_user(self) -> UserPlainSchema | None:
        return await self.__auth_service.get_current_user(
            Endpoint.CURRENT_USER,
            None,
            None,
            None,
            Module.CORE,
        )
