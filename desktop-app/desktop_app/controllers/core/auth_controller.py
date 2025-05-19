from config import Context
from controllers.base import BaseController
from services.core import AuthService
from views.components import AuthDialog
from typing import cast
from controllers.core import AppController
from collections.abc import Callable


class AuthController(BaseController[AuthService]):
    _service_cls = AuthService

    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.__auth_dialog: AuthDialog | None = None
        self.__post_login_callback: Callable[[], None] | None = None

    def show(self, *args, **kwargs) -> None:
        self.__post_login_callback = kwargs.get("callback")
        self.__auth_dialog = AuthDialog(
            texts=self._context.texts,
            on_cancel=self.__on_cancel,
            on_login=self.__on_login,
        )
        self._open_dialog(self.__auth_dialog)

    def __on_cancel(self) -> None:
        self._context.page.window.destroy()

    def __on_login(self, username: str, password: str) -> None:
        self._executor.run_async(
            async_func=self.__handle_login,
            async_args=[username, password],
        )

    async def __handle_login(self, username: str, password: str) -> None:
        loading_dialog = self._show_loading_dialog()
        try:
            tokens = await self._service.fetch_tokens(username, password)
            self._context.tokens = tokens
            if self.__auth_dialog:
                self._close_dialog(self.__auth_dialog)
            self._close_dialog(loading_dialog)
            if self.__post_login_callback:
                self._executor.run_ui(self.__post_login_callback)
        except Exception:
            self._close_dialog(loading_dialog)
            if self.__auth_dialog:
                self._close_dialog(self.__auth_dialog)
            self._show_error_dialog("invalid_credentials")
