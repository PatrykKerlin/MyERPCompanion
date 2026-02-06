from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from pydantic import ValidationError
from controllers.base.base_controller import BaseController

from events.base.base_event import BaseEvent
from events.events import (
    ApiStatusChecked,
    ApiStatusRequested,
    AppStarted,
    CallerActionRequested,
    FooterReady,
    MenuBarRequested,
    MenuBarReady,
    SideMenuReady,
    TabClosed,
    TabsBarReady,
    ToolbarReady,
    TranslationFailed,
    TranslationReady,
    TranslationRequested,
    AuthDialogRequested,
    AuthViewReady,
    UserAuthenticated,
    CartUpdated,
    SideMenuRequested,
    FooterRequested,
    LogoutRequested,
    TabsBarRequested,
    TabCloseAllRequested,
    ToolbarRequested,
    ToolbarToggleRequested,
    TabsBarToggleRequested,
    ViewRequested,
)
from schemas.core.language_schema import LanguagePlainSchema
from schemas.core.user_schema import UserPlainSchema, UserStrictUpdateAppSchema
from services.core import LanguageService, UserService
from services.core.app_service import AppService
from services.core.auth_service import AuthService
from utils.enums import ApiActionError, Endpoint, Module, View, ViewMode

from states.states import ViewState
from views.base.base_dialog import BaseDialog
from views.core.app_view import AppView as DesktopAppView
from views.web.app_view import AppView as WebAppView

if TYPE_CHECKING:
    from config.context import Context
    from states.states import ShellState, TranslationState, UserState


class AppController(BaseController):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__service = AppService(self._settings, self._logger, self._tokens_accessor)
        self.__auth_service = AuthService(self._settings, self._logger, self._tokens_accessor)
        self.__language_service = LanguageService(self._settings, self._logger, self._tokens_accessor)
        self.__user_service = UserService(self._settings, self._logger, self._tokens_accessor)
        if self._settings.CLIENT == "web":
            self.__view = WebAppView(self._state_store.app_state.translation.items, self._settings.THEME)
            self.__view.set_nav_handlers(self.__open_create_order, self.__open_orders)
            self.__view.set_cart_handler(self.__open_cart)
            self.__view.set_user_settings_handler(self.__open_current_user_settings)
            self.__view.set_logout_handler(self.__request_logout)
            self._page.on_connect = lambda event: self._page.run_task(self.__handle_web_reconnect, event)
        else:
            self.__view = DesktopAppView(self._state_store.app_state.translation.items, self._settings.THEME)

        self._subscribe_event_handlers(
            {
                AppStarted: self.__app_started_handler,
                TranslationReady: self.__translation_ready_handler,
                TranslationFailed: self.__api_not_responding_handler,
                UserAuthenticated: self.__user_authenticated_handler,
                CallerActionRequested: self.__caller_action_handler,
                LogoutRequested: self.__logout_requested_handler,
                CartUpdated: self.__cart_updated_handler,
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
            initial_language = self._settings.LANGUAGE
            await self._event_bus.publish(TranslationRequested(initial_language, False))
        else:
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
            if self._settings.CLIENT == "web":
                await self.__open_orders_async()
            else:
                await self.__request_shell()
        else:
            await self._event_bus.publish(AuthDialogRequested())

    async def __api_not_responding_handler(self, _: BaseEvent):
        self._close_loading_dialog()
        self._open_error_dialog(message_key="api_not_responding")

    async def __user_authenticated_handler(self, _: UserAuthenticated) -> None:
        user = self._state_store.app_state.user.current
        if not user:
            return
        self.__view.set_auth_view(None)
        self.__apply_user_preferences(user)
        if isinstance(self.__view, WebAppView):
            self.__view.set_cart_count(0)
        self._page.update()
        translation_state = self._state_store.app_state.translation
        if user.language.symbol == translation_state.language:
            if self._settings.CLIENT == "web":
                await self.__open_orders_async()
            else:
                await self.__request_shell()
        else:
            await self._open_loading_dialog()
            await self._event_bus.publish(TranslationRequested(user.language.symbol, True))

    async def __auth_view_ready_handler(self, event: AuthViewReady) -> None:
        self.__view.set_auth_view(event.component)
        self._page.update()

    async def __cart_updated_handler(self, event: CartUpdated) -> None:
        if isinstance(self.__view, WebAppView):
            self.__view.set_cart_count(event.count)

    async def __logout_requested_handler(self, _: LogoutRequested) -> None:
        if isinstance(self.__view, DesktopAppView):
            await self._event_bus.publish(TabCloseAllRequested())
            self.__view.set_shell_visible(False)
            self.__reset_shell_state()
        elif not isinstance(self.__view, WebAppView):
            return
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
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.set_menu_bar(event.component)
        self._state_store.update(shell={"is_menu_bar_ready": True})

    async def __toolbar_ready_handler(self, event: ToolbarReady) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.set_toolbar(event.component)
        self._state_store.update(shell={"is_toolbar_ready": True})

    async def __side_menu_ready_handler(self, event: SideMenuReady) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.set_side_menu(event.component)
        self._state_store.update(shell={"is_side_menu_ready": True})

    async def __footer_ready_handler(self, event: FooterReady) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.set_footer(event.component)
        self._state_store.update(shell={"is_footer_ready": True})

    async def __tabs_bar_ready_handler(self, event: TabsBarReady) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.set_tabs_bar(event.component)
        self._state_store.update(shell={"is_tabs_bar_ready": True})

    async def __tab_closed_handler(self, event: TabClosed) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.remove_stack_item(event.view)

    async def __toolbar_toggle_handler(self, _: ToolbarToggleRequested) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.toggle_toolbar_visible()
        self._page.update()

    async def __tabs_bar_toggle_handler(self, _: TabsBarToggleRequested) -> None:
        if not isinstance(self.__view, DesktopAppView):
            return
        self.__view.toggle_tabs_bar_visible()
        self._page.update()

    def __shell_updated_listener(self, state: ShellState) -> None:
        if isinstance(self.__view, DesktopAppView):
            has_user = self._state_store.app_state.user.current is not None
            self.__view.set_shell_visible(state.is_shell_ready and has_user)
        self._page.update()

    def __view_updated_listener(self, state: ViewState) -> None:
        self.__view.set_stack_item(state.view)
        self._page.update()

    def __user_updated_listener(self, state: UserState) -> None:
        user = state.current
        if not user:
            if isinstance(self.__view, WebAppView):
                self.__view.set_username(None)
                self.__view.set_cart_count(0)
                self._page.update()
            return
        self.__apply_user_preferences(user)
        self._page.update()

    def __apply_user_preferences(self, user: UserPlainSchema) -> None:
        self.__view.set_theme(user.theme)
        if isinstance(self.__view, WebAppView):
            self.__view.set_username(user.username)

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
        if isinstance(self.__view, DesktopAppView):
            self.__view.set_shell_visible(False)
        self.__reset_shell_state()
        await self._event_bus.publish(MenuBarRequested())
        await self._event_bus.publish(ToolbarRequested())
        await self._event_bus.publish(SideMenuRequested())
        await self._event_bus.publish(FooterRequested())
        await self._event_bus.publish(TabsBarRequested())

    def __open_create_order(self) -> None:
        self._page.run_task(
            self._event_bus.publish,
            ViewRequested(
                module_id=Module.WEB,
                view_key=View.WEB_CREATE_ORDER,
                mode=ViewMode.STATIC,
            ),
        )

    def __open_orders(self) -> None:
        self._page.run_task(self.__open_orders_async)

    async def __open_orders_async(self) -> None:
        await self._event_bus.publish(
            ViewRequested(
                module_id=Module.WEB,
                view_key=View.WEB_ORDERS,
                mode=ViewMode.STATIC,
            )
        )

    async def __handle_web_reconnect(self, _: ft.ControlEvent) -> None:
        if self._settings.CLIENT != "web":
            return
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
                mode=ViewMode.STATIC,
            )
        )

    def __open_cart(self) -> None:
        view = self._state_store.app_state.view.view
        if not view or view.view_key != View.WEB_CREATE_ORDER:
            return
        open_handler = getattr(view, "open_cart_dialog", None)
        if callable(open_handler):
            open_handler()

    def __request_logout(self) -> None:
        self._page.run_task(self._event_bus.publish, LogoutRequested())

    def __open_current_user_settings(self) -> None:
        if not isinstance(self.__view, WebAppView):
            return
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
        password_field = ft.TextField(
            label=translation.get("password"),
            password=True,
            can_reveal_password=True,
        )
        password_repeat_field = ft.TextField(
            label=translation.get("password_repeat"),
            password=True,
            can_reveal_password=True,
        )
        language_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in language_options],
            value=str(current_user.language.id),
            expand=True,
            editable=True,
            enable_search=True,
            enable_filter=True,
        )
        theme_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key="system", text=translation.get("system")),
                ft.dropdown.Option(key="dark", text=translation.get("dark")),
                ft.dropdown.Option(key="light", text=translation.get("light")),
            ],
            value=current_user.theme,
            expand=True,
        )

        def build_labeled_dropdown(label: str, dropdown: ft.Dropdown) -> ft.Row:
            return ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Container(width=170, content=ft.Text(label)),
                    ft.Container(expand=True, content=dropdown),
                ],
            )

        save_button = ft.Button(content=translation.get("save"))
        cancel_button = ft.TextButton(translation.get("cancel"), on_click=lambda _: self._page.pop_dialog())
        controls: list[ft.Control] = [
            ft.Container(content=password_field, padding=ft.Padding.only(bottom=8)),
            ft.Container(content=password_repeat_field, padding=ft.Padding.only(bottom=8)),
            ft.Container(
                content=build_labeled_dropdown(translation.get("language_id"), language_dropdown),
                padding=ft.Padding.only(bottom=8),
            ),
            ft.Container(content=build_labeled_dropdown(translation.get("theme"), theme_dropdown)),
        ]
        dialog = BaseDialog(
            title=translation.get("current_user"),
            controls=controls,
            actions=[cancel_button, save_button],
        )
        dialog_content = dialog.content
        if isinstance(dialog_content, ft.Container):
            dialog_content.alignment = ft.Alignment.TOP_LEFT
            content_column = dialog_content.content
            if isinstance(content_column, ft.Column):
                content_column.alignment = ft.MainAxisAlignment.START
                content_column.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

        def resolve_dialog_width() -> int:
            if self._page.web:
                viewport_width = self._page.width or self._page.window.width
            else:
                viewport_width = self._page.window.width or self._page.width
            if viewport_width:
                return max(360, min(int(viewport_width * 0.9), 540))
            return 520

        target_width = resolve_dialog_width()
        dialog.width = target_width
        dialog.content.width = target_width

        save_button.on_click = lambda _: self._page.run_task(
            self.__save_current_user_settings,
            dialog,
            password_field,
            password_repeat_field,
            language_dropdown,
            theme_dropdown,
            current_user,
            language_by_id,
        )
        self._queue_dialog(dialog)

    async def __save_current_user_settings(
        self,
        dialog: BaseDialog,
        password_field: ft.TextField,
        password_repeat_field: ft.TextField,
        language_dropdown: ft.Dropdown,
        theme_dropdown: ft.Dropdown,
        current_user: UserPlainSchema,
        language_by_id: dict[int, LanguagePlainSchema],
    ) -> None:
        selected_language_id = self.__parse_optional_int(language_dropdown.value)
        if selected_language_id is None:
            self._open_error_dialog(message_key="value_required")
            return
        selected_language = language_by_id.get(selected_language_id)
        selected_theme = theme_dropdown.value or current_user.theme
        password = self.__to_none_if_empty(password_field.value)
        password_repeat = self.__to_none_if_empty(password_repeat_field.value)
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
        self._page.pop_dialog()
        previous_language = self._state_store.app_state.translation.language
        effective_user = updated_user
        if selected_language and updated_user.language.id != selected_language.id:
            effective_user = updated_user.model_copy(update={"language": selected_language})
        self._state_store.update(user={"current": effective_user})
        self._open_message_dialog("record_save_success")
        target_language = selected_language.symbol if selected_language else effective_user.language.symbol
        if target_language != previous_language:
            await self._open_loading_dialog()
            await self._event_bus.publish(TranslationRequested(target_language, True))

    @staticmethod
    def __parse_optional_int(value: str | None) -> int | None:
        if value in {None, "", "0"}:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def __to_none_if_empty(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_all_languages(self) -> list[LanguagePlainSchema] | None:
        return await self.__language_service.get_all(Endpoint.LANGUAGES, None, None, None, Module.CORE)

    @BaseController.handle_api_action(ApiActionError.FETCH)
    async def __perform_get_current_user(self) -> UserPlainSchema | None:
        module_id = Module.WEB if self._settings.CLIENT == "web" else Module.CORE
        return await self.__auth_service.get_current_user(Endpoint.CURRENT_USER, None, None, None, module_id=module_id)

    @BaseController.handle_api_action(ApiActionError.SAVE)
    async def __perform_update_user(
        self, user_id: int, payload: UserStrictUpdateAppSchema
    ) -> UserPlainSchema | None:
        module_id = Module.WEB if self._settings.CLIENT == "web" else Module.CORE
        return await self.__user_service.update(Endpoint.USERS, user_id, None, payload, module_id)
