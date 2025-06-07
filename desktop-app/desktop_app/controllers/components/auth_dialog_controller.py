from __future__ import annotations
from typing import TYPE_CHECKING

from controllers.base import BaseComponentController
from services.core import AuthService
from views.components import AuthDialogComponent

if TYPE_CHECKING:
    from config.context import Context


class AuthDialogController(BaseComponentController[AuthService, AuthDialogComponent]):
    _service_cls = AuthService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__auth_dialog: AuthDialogComponent | None = None

    @property
    def component(self) -> AuthDialogComponent:
        self.__auth_dialog = AuthDialogComponent(self, texts=self._context.texts)
        return self.__auth_dialog

    def on_cancel(self) -> None:
        self._context.page.window.destroy()

    def on_login(self, username: str, password: str) -> None:
        self._context.page.run_task(self.__handle_login, "admin", "admin123")

    async def __handle_login(self, username: str, password: str) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            tokens = await self._service.fetch_tokens(username, password)
            self._context.tokens = tokens
            user = await self._service.fetch_current_user()
            self._context.user = user
            if self.__auth_dialog:
                self._close_dialog(self.__auth_dialog)
            self._close_dialog(loading_dialog)
            app_controller = self._context.controllers.get("app")
            app_controller.after_login()
        except Exception as e:
            self._close_dialog(loading_dialog)
            if self.__auth_dialog:
                self._close_dialog(self.__auth_dialog)
            self._show_error_dialog(str(e))
