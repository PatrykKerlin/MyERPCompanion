from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from config.context import Context
from controllers.base.base_controller import BaseController
from events.base.base_event import BaseEvent
from events.events import (
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
from schemas.business.trade.order_schema import OrderPickingSummarySchema
from services.business.trade import OrderService
from services.core.app_service import AppService
from utils.enums import ApiActionError, Endpoint, Module, View
from utils.user_settings import UserSettings
from views.core.app_view import AppView as MobileAppView
from views.core.main_menu_view import MainMenuView

if TYPE_CHECKING:
    from schemas.core.user_schema import UserPlainSchema
    from states.states import MobileWarehouseState, TranslationState, UserState


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__order_service = OrderService(self._settings, self._logger, self._tokens_accessor)
        self.__view = MobileAppView(self._state_store.app_state.translation.items, self._settings.THEME)
        self.__view.set_navigation_handler(self.__request_mobile_view)
        self.__view.set_refresh_handler(self.__request_refresh)
        self.__view.set_user_settings_handler(self.__open_current_user_settings)
        self.__view.set_logout_handler(self.__request_logout)
        self.__main_menu: MainMenuView | None = None
        self.__last_view_request: ViewRequested | None = None

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
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
                "mobile_warehouse": self.__mobile_warehouse_updated_listener,
            }
        )

    def build_root(self) -> ft.Control:
        return self.__view.build()

    def __translation_updated_listener(self, state: TranslationState) -> None:
        self.__view.update_translation(state.items)
        self._page.update()

    def __mobile_warehouse_updated_listener(self, _: MobileWarehouseState) -> None:
        self.__view.set_warehouse_name(self._get_mobile_selected_warehouse_name())
        self._page.update()

    async def __app_started_handler(self, _: AppStarted) -> None:
        await self._open_loading_dialog()
        ok = await self.__perform_api_health_check()
        if ok:
            await self._event_bus.publish(TranslationRequested(self._settings.LANGUAGE, False))
            return
        self._open_error_dialog(message_key="api_not_responding")

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_api_health_check(self) -> bool:
        await self.__service.api_health_check()
        return True

    async def __translation_ready_handler(self, event: TranslationReady) -> None:
        self._close_loading_dialog()
        if event.user_authenticated:
            await self.__open_main_menu_view()
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
            await self.__open_main_menu_view()
            return

        await self._open_loading_dialog()
        await self._event_bus.publish(TranslationRequested(user.language.symbol, True))

    async def __auth_view_ready_handler(self, event: AuthViewReady) -> None:
        self.__view.set_auth_view(event.component)
        self._page.update()

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        self.__view.set_navigation_visible(False)
        self.__view.set_username(None)
        self.__view.set_warehouse_name(None)
        self.__view.set_content_visible(False)
        self.__view.set_content(None)
        self.__main_menu = None
        self.__last_view_request = None
        self._state_store.update(
            user={"current": None},
            mobile_warehouse={"selected_id": None, "selected_name": None},
            tokens={"access": None, "refresh": None},
        )
        await self._event_bus.publish(AuthDialogRequested())

    async def __view_ready_handler(self, event: ViewReady) -> None:
        if event.view_key not in {
            View.BINS,
            View.ITEMS,
            View.BIN_TRANSFER,
            View.ORDER_PICKING,
            View.STOCK_RECEIVING,
            View.USERS,
        }:
            return
        self.__view.set_navigation_visible(True)
        self.__main_menu = None
        self.__view.set_content(event.view)
        self.__view.set_content_visible(True)
        self._page.update()

    async def __mobile_main_menu_requested_handler(self, _: MobileMainMenuRequested) -> None:
        await self.__open_main_menu_view()

    def __user_updated_listener(self, state: UserState) -> None:
        user = state.current
        if not user:
            self.__view.set_navigation_visible(False)
            self.__view.set_username(None)
            self.__view.set_warehouse_name(None)
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
        self.__view.set_username(user.username)
        self.__view.set_warehouse_name(self._get_mobile_selected_warehouse_name())

    async def __open_main_menu_view(self) -> None:
        self.__last_view_request = None
        self.__main_menu = MainMenuView(self._state_store.app_state.translation.items)
        summary = await self.__load_mobile_picking_summary()
        self.__main_menu.set_summary(
            orders_count=summary.orders_count,
            items_count=summary.items_count,
            pieces_count=summary.pieces_count,
        )
        self.__view.set_navigation_visible(True)
        self.__view.set_content(self.__main_menu)
        self.__view.set_content_visible(True)
        self._page.update()

    async def __load_mobile_picking_summary(self) -> OrderPickingSummarySchema:
        if self._state_store.app_state.user.current is None:
            return OrderPickingSummarySchema()
        summary = await self.__perform_get_mobile_picking_summary()
        return summary or OrderPickingSummarySchema()

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_mobile_picking_summary(self) -> OrderPickingSummarySchema:
        return await self.__order_service.get_picking_summary(
            Endpoint.ORDERS_PICKING_SUMMARY,
            None,
            None,
            None,
            Module.MOBILE,
        )

    def __request_mobile_view(self, view_key: View) -> None:
        event = ViewRequested(
            module_id=Module.MOBILE,
            view_key=view_key,
        )
        self.__last_view_request = event
        self._page.run_task(self._event_bus.publish, event)

    def __open_current_user_settings(self) -> None:
        current_user = self._state_store.app_state.user.current
        if current_user is None:
            return
        event = ViewRequested(
            module_id=Module.CORE,
            view_key=View.USERS,
            record_id=current_user.id,
            caller_view_key=View.CURRENT_USER,
        )
        self.__last_view_request = event
        self._page.run_task(self._event_bus.publish, event)

    def __request_logout(self) -> None:
        self._page.run_task(self._event_bus.publish, LogoutRequested())

    def __request_refresh(self) -> None:
        self._page.run_task(self.__refresh_current_content)

    async def __refresh_current_content(self) -> None:
        if self._state_store.app_state.user.current is None:
            return

        if self.__main_menu is not None:
            await self.__open_main_menu_view()
            return

        if self.__last_view_request is None:
            await self.__open_main_menu_view()
            return

        event = self.__last_view_request
        if event.view_key == View.USERS and event.caller_view_key == View.CURRENT_USER:
            current_user = self._state_store.app_state.user.current
            if current_user is None:
                return
            event = ViewRequested(
                module_id=event.module_id,
                view_key=event.view_key,
                record_id=current_user.id,
                caller_view_key=event.caller_view_key,
                caller_data=event.caller_data,
            )
            self.__last_view_request = event

        await self._event_bus.publish(event)
