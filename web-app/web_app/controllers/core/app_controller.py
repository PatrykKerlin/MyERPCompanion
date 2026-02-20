from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft
from controllers.base.base_controller import BaseController
from events.events import (
    AppStarted,
    AuthDialogRequested,
    AuthViewReady,
    CartUpdated,
    LogoutRequested,
    TranslationFailed,
    TranslationReady,
    TranslationRequested,
    UserAuthenticated,
    ViewRequested,
)
from pydantic import ValidationError
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateAppSchema
from schemas.validation.constraints import Constraints
from services.core import LanguageService, UserService
from services.core.app_service import AppService
from states.states import ViewState
from utils.enums import ApiActionError, Endpoint, Module, View
from utils.user_settings import UserSettings
from views.components.current_user_settings_dialog_component import CurrentUserSettingsDialogComponent
from views.core.app_view import AppView as WebAppView

if TYPE_CHECKING:
    from config.context import Context
    from states.states import TranslationState, UserState


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__user_service = UserService(self._settings, self._logger, self._tokens_accessor)
        self.__view = WebAppView(self, self._state_store.app_state.translation.items, self._settings.THEME)
        self.__view.set_nav_handlers(self.__open_orders)
        self.__view.set_cart_handler(self.__open_cart)
        self.__view.set_user_settings_handler(self.__open_current_user_settings)
        self.__view.set_logout_handler(self.__request_logout)
        self.__current_user_settings_dialog: CurrentUserSettingsDialogComponent | None = None
        self.__current_user_settings_user: UserPlainSchema | None = None
        self.__current_user_settings_language_by_id: dict[int, LanguagePlainSchema] = {}
        self._page.on_connect = lambda event: self._page.run_task(self.__handle_web_reconnect, event)

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
                LogoutRequested: self.__logout_requested_handler,
                CartUpdated: self.__cart_updated_handler,
                AuthViewReady: self.__auth_view_ready_handler,
            }
        )
        self._subscribe_state_listeners(
            {
                "translation": self.__translation_updated_listener,
                "view": self.__view_updated_listener,
                "user": self.__user_updated_listener,
            }
        )

    def build_root(self) -> ft.Control:
        return self.__view.build()

    async def __api_not_responding_handler(self, _: TranslationFailed) -> None:
        self._close_loading_dialog()
        self._open_error_dialog(message_key="api_not_responding")

    async def __app_started_handler(self, _: AppStarted) -> None:
        await self._open_loading_dialog()
        ok = await self.__perform_api_health_check()
        if ok:
            await self._event_bus.publish(TranslationRequested(self._settings.LANGUAGE, False))
            return
        self._open_error_dialog(message_key="api_not_responding")

    def __apply_user_preferences(self, user: UserPlainSchema) -> None:
        self.__view.set_theme(user.theme)
        self.__view.set_username(user.username)

    async def __auth_view_ready_handler(self, event: AuthViewReady) -> None:
        self.__view.set_auth_view(event.component)
        self._page.update()

    async def __cart_updated_handler(self, event: CartUpdated) -> None:
        self.__view.set_cart_count(event.count)

    async def __handle_web_reconnect(self, _: ft.Event[ft.Page]) -> None:
        current_user = self._state_store.app_state.user.current
        if not current_user:
            await self._event_bus.publish(AuthDialogRequested())
            return
        current_view = self._state_store.app_state.view.view
        target_view = View.WEB_ORDERS
        if current_view and current_view.view_key in {View.WEB_ORDERS, View.WEB_CREATE_ORDER}:
            target_view = current_view.view_key
        await self._event_bus.publish(
            ViewRequested(
                module_id=Module.WEB,
                view_key=target_view,
            )
        )

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        self._state_store.update(
            view={"view": None},
            user={"current": None},
            tokens={"access": None, "refresh": None},
        )
        await self._event_bus.publish(AuthDialogRequested())

    def __open_cart(self) -> None:
        view = self._state_store.app_state.view.view
        if not view or view.view_key != View.WEB_CREATE_ORDER:
            return
        open_handler = getattr(view, "open_cart_dialog", None)
        if callable(open_handler):
            open_handler()

    def __open_current_user_settings(self) -> None:
        self._page.run_task(self.__open_current_user_settings_dialog)

    async def __open_current_user_settings_dialog(self) -> None:
        current_user = self._state_store.app_state.user.current
        if not current_user:
            return
        translation = self._state_store.app_state.translation.items
        languages = await self.__perform_get_all_languages()
        if languages is None:
            return
        language_by_id = {language.id: language for language in languages}
        language_options = [(language.id, language.key) for language in languages]
        language_ids = {language.id for language in languages}
        if current_user.language.id not in language_ids:
            language_options.append((current_user.language.id, current_user.language.key))
            language_by_id[current_user.language.id] = current_user.language

        dialog = CurrentUserSettingsDialogComponent(
            translation=translation,
            language_options=language_options,
            language_value=str(current_user.language.id),
            theme_value=current_user.theme,
            on_cancel_clicked=lambda _: self._page.pop_dialog(),
            on_save_clicked=self.__on_current_user_settings_save_clicked,
        )
        self.__current_user_settings_dialog = dialog
        self.__current_user_settings_user = current_user
        self.__current_user_settings_language_by_id = language_by_id
        self._queue_dialog(dialog)

    def __on_current_user_settings_save_clicked(self, _: ft.Event[ft.Button]) -> None:
        dialog = self.__current_user_settings_dialog
        current_user = self.__current_user_settings_user
        if dialog is None or current_user is None:
            return
        self._page.run_task(
            self.__save_current_user_settings,
            dialog,
            current_user,
            self.__current_user_settings_language_by_id,
        )

    def __open_orders(self) -> None:
        self._page.run_task(self.__open_orders_async)

    async def __open_orders_async(self) -> None:
        await self._event_bus.publish(
            ViewRequested(
                module_id=Module.WEB,
                view_key=View.WEB_ORDERS,
            )
        )

    @staticmethod
    def __parse_optional_int(value: str | None) -> int | None:
        if value is None:
            return None
        stripped = value.strip()
        if stripped in {"", "0"}:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_api_health_check(self) -> bool:
        await self.__service.api_health_check()
        return True

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema] | None:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, Module.CORE)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_user(self, user_id: int, payload: UserStrictUpdateAppSchema) -> UserPlainSchema | None:
        return await self.__user_service.update(Endpoint.USERS, user_id, None, payload, Module.WEB)

    def __request_logout(self) -> None:
        self._page.run_task(self._event_bus.publish, LogoutRequested())

    async def __save_current_user_settings(
        self,
        dialog: CurrentUserSettingsDialogComponent,
        current_user: UserPlainSchema,
        language_by_id: dict[int, LanguagePlainSchema],
    ) -> None:
        selected_language_id = self.__parse_optional_int(dialog.language_value)
        if selected_language_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        selected_language = language_by_id.get(selected_language_id)
        selected_theme = self.__normalize_theme(dialog.theme_value, current_user.theme)
        password = self.__to_none_if_empty(dialog.password_value)
        password_repeat = self.__to_none_if_empty(dialog.password_repeat_value)
        try:
            payload = UserStrictUpdateAppSchema(
                id=current_user.id,
                username=current_user.username,
                password=password,
                password_repeat=password_repeat,
                language_id=selected_language_id,
                theme=selected_theme,
                employee_id=current_user.employee_id,
                customer_id=current_user.customer_id,
                warehouse_id=current_user.warehouse_id,
            )
        except ValidationError as validation_error:
            translation = self._state_store.app_state.translation.items
            error_message = [translation.get("validation_errors")]
            for error in validation_error.errors():
                message = error.get("msg", "")
                loc = error.get("loc", ())
                if loc:
                    key = loc[0]
                    error_message.append(f"{translation.get(str(key))}: {message}")
                else:
                    error_message.append(message)
            self._open_error_dialog(message="\n".join(error_message))
            return
        updated_user = await self.__perform_update_user(current_user.id, payload)
        if not updated_user:
            return
        while True:
            closed_dialog = self._page.pop_dialog()
            if closed_dialog is None or closed_dialog is dialog:
                break
        if dialog is self.__current_user_settings_dialog:
            self.__current_user_settings_dialog = None
            self.__current_user_settings_user = None
            self.__current_user_settings_language_by_id = {}
        previous_language = self._state_store.app_state.translation.language
        effective_user = updated_user
        if selected_language and updated_user.language.id != selected_language.id:
            effective_user = updated_user.model_copy(update={"language": selected_language})
        self._state_store.update(user={"current": effective_user})
        await self.__save_web_user_settings(effective_user)
        self._open_message_dialog("record_save_success")
        target_language = selected_language.symbol if selected_language else effective_user.language.symbol
        if target_language != previous_language:
            await self._open_loading_dialog()
            await self._event_bus.publish(TranslationRequested(target_language, True))

    async def __save_web_user_settings(self, user: UserPlainSchema) -> None:
        await UserSettings.save_web(user.theme, user.language.symbol)

    @staticmethod
    def __to_none_if_empty(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None

    @staticmethod
    def __normalize_theme(value: str | None, fallback: str | None = None) -> Constraints.Theme:
        candidate = value if value is not None else fallback
        if candidate in {"system", "dark", "light"}:
            return cast(Constraints.Theme, candidate)
        return "system"

    async def __translation_ready_handler(self, event: TranslationReady) -> None:
        self._close_loading_dialog()
        if event.user_authenticated:
            await self.__open_orders_async()
            return
        await self._event_bus.publish(AuthDialogRequested())

    def __translation_updated_listener(self, state: TranslationState) -> None:
        self.__view.update_translation(state.items)
        self._page.update()

    async def __user_authenticated_handler(self, _: UserAuthenticated) -> None:
        user = self._state_store.app_state.user.current
        if not user:
            return
        self.__view.set_auth_view(None)
        self.__apply_user_preferences(user)
        self.__view.set_cart_count(0)
        await self.__save_web_user_settings(user)
        self._page.update()

        translation_state = self._state_store.app_state.translation
        if user.language.symbol == translation_state.language:
            await self.__open_orders_async()
            return

        await self._open_loading_dialog()
        await self._event_bus.publish(TranslationRequested(user.language.symbol, True))

    def __user_updated_listener(self, state: UserState) -> None:
        user = state.current
        if not user:
            self.__view.set_username(None)
            self.__view.set_cart_count(0)
            self._page.update()
            return
        self.__apply_user_preferences(user)
        self._page.update()

    def __view_updated_listener(self, state: ViewState) -> None:
        self.__view.set_stack_item(state.view)
        self._page.update()
