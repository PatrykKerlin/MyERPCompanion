from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from config.context import Context
from controllers.base.base_controller import BaseController
from controllers.mobile.bins_controller import BinsController
from controllers.mobile.items_controller import ItemsController
from events.base.base_event import BaseEvent
from events.events import (
    ApiStatusChecked,
    ApiStatusRequested,
    AppStarted,
    AuthDialogRequested,
    AuthViewReady,
    LogoutRequested,
    MobileMainMenuRequested,
    TranslationFailed,
    TranslationReady,
    TranslationRequested,
    UserAuthenticated,
    ViewReady,
    ViewRequested,
)
from services.core.app_service import AppService
from utils.enums import ApiActionError, Module, View, ViewMode
from utils.user_settings import UserSettings
from views.mobile.app_view import AppView as MobileAppView
from views.mobile.main_menu_view import MainMenuView

if TYPE_CHECKING:
    from schemas.core.user_schema import UserPlainSchema
    from states.states import TranslationState, UserState


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__bins_controller = BinsController(context)
        self.__items_controller = ItemsController(context)
        self.__view = MobileAppView(self._state_store.app_state.translation.items, self._settings.THEME)
        self.__view.set_navigation_handler(self.__request_mobile_view)
        self.__main_menu: MainMenuView | None = None

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
                ApiStatusRequested: self.__api_status_handler,
                AuthViewReady: self.__auth_view_ready_handler,
                LogoutRequested: self.__logout_requested_handler,
                ViewReady: self.__view_ready_handler,
                MobileMainMenuRequested: self.__mobile_main_menu_requested_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "translation": self.__translation_updated_listener,
                "user": self.__user_updated_listener,
            }
        )

    async def dispose(self) -> None:
        await self.__bins_controller.dispose()
        await self.__items_controller.dispose()
        await super().dispose()

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
            self.__open_main_menu_view()
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
        self.__view.set_navigation_visible(True)
        self.__apply_user_preferences(user)
        self._page.update()

        translation_state = self._state_store.app_state.translation
        if user.language.symbol == translation_state.language:
            self.__open_main_menu_view()
            return

        await self._open_loading_dialog()
        await self._event_bus.publish(TranslationRequested(user.language.symbol, True))

    async def __auth_view_ready_handler(self, event: AuthViewReady) -> None:
        self.__view.set_auth_view(event.component)
        self._page.update()

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        self.__view.set_navigation_visible(False)
        self.__view.set_content_visible(False)
        self.__view.set_content(None)
        self.__main_menu = None
        self._state_store.update(
            view={"title": "", "mode": ViewMode.NONE, "view": None},
            modules={"items": []},
            user={"current": None},
            tokens={"access": None, "refresh": None},
        )
        await self._event_bus.publish(AuthDialogRequested())

    async def __view_ready_handler(self, event: ViewReady) -> None:
        if event.view_key not in {View.BINS, View.ITEMS}:
            return
        self.__view.set_navigation_visible(True)
        self.__main_menu = None
        self.__view.set_content(event.view)
        self.__view.set_content_visible(True)
        self._page.update()

    async def __mobile_main_menu_requested_handler(self, _: MobileMainMenuRequested) -> None:
        self.__open_main_menu_view()

    def __user_updated_listener(self, state: UserState) -> None:
        user = state.current
        if not user:
            self.__view.set_navigation_visible(False)
            self.__view.set_content_visible(False)
            self.__view.set_content(None)
            self.__main_menu = None
            self._page.update()
            return
        UserSettings.save(user.theme, user.language.symbol)
        self.__apply_user_preferences(user)
        self._page.update()

    def __apply_user_preferences(self, user: UserPlainSchema) -> None:
        self.__view.set_theme(user.theme)

    def __open_main_menu_view(self) -> None:
        self.__main_menu = MainMenuView(self._state_store.app_state.translation.items)
        self.__view.set_navigation_visible(True)
        self.__view.set_content(self.__main_menu)
        self.__view.set_content_visible(True)
        self._page.update()

    def __request_mobile_view(self, view_key: View) -> None:
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=Module.MOBILE,
                view_key=view_key,
                mode=ViewMode.STATIC,
            ),
        )
