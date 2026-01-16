from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from httpx import HTTPStatusError

from schemas.base.base_schema import BaseStrictSchema
from utils.enums import ApiActionError
from utils.tokens_accessor import TokensAccessor
from views.components.confirm_dialog_component import ConfirmDialogComponent
from views.components.error_dialog_component import ErrorDialogComponent
from views.components.loading_dialog_component import LoadingDialogComponent
from views.components.message_dialog_component import MessageDialogComponent

from config.context import Context

TStrictSchema = TypeVar("TStrictSchema", bound=BaseStrictSchema)
TReturn = TypeVar("TReturn")


class BaseController:
    def __init__(self, context: Context) -> None:
        self._page = context.page
        self._settings = context.settings
        self._logger = context.logger
        self._event_bus = context.event_bus
        self._state_store = context.state_store
        self._tokens_accessor = TokensAccessor(self._state_store)
        self._loading_dialog: LoadingDialogComponent | None = None
        self.__unsubscribers: list[Callable[[], None]] = []
        self.__disposed: bool = False

    async def dispose(self) -> None:
        if self.__disposed:
            return
        self.__disposed = True
        while self.__unsubscribers:
            func = self.__unsubscribers.pop()
            func()

    @classmethod
    def handle_api_action(
        cls, message_key: ApiActionError
    ) -> Callable[[Callable[..., Awaitable[TReturn]]], Callable[..., Awaitable[TReturn]]]:
        def decorator(func: Callable[..., Awaitable[TReturn]]) -> Callable[..., Awaitable[TReturn]]:
            @wraps(func)
            async def wrapper(self: BaseController, *args: Any, **kwargs: Any) -> TReturn:
                opened_loading = self._loading_dialog is None
                if opened_loading:
                    self._open_loading_dialog()
                try:
                    result = await func(self, *args, **kwargs)
                    if opened_loading:
                        self._close_loading_dialog()
                    return result
                except HTTPStatusError as http_error:
                    if opened_loading:
                        self._close_loading_dialog()
                    if http_error.response.status_code == 403:
                        self._open_error_dialog(message_key="no_permissions")
                    else:
                        self._logger.error(str(http_error))
                        self._open_error_dialog(message_key=message_key)
                    return cast(TReturn, None)
                except Exception as error:
                    if opened_loading:
                        self._close_loading_dialog()
                    self._logger.error(str(error))
                    self._open_error_dialog(message_key=message_key)
                    return cast(TReturn, None)

            return wrapper

        return decorator

    def _subscribe_event_handlers(self, event_handlers: dict[type[Any], Callable[[Any], Awaitable[None]]]) -> None:
        for event, handler in event_handlers.items():
            unsubscriber = self._event_bus.subscribe(event, handler)
            self.__add_unsubscriber(unsubscriber)

    def _subscribe_state_listeners(self, state_listeners: dict[str, Callable[[Any], None]]) -> None:
        for state, listener in state_listeners.items():
            unsubscriber = self._state_store.subscribe(state, listener)
            self.__add_unsubscriber(unsubscriber)

    def _open_loading_dialog(self) -> None:
        translation = self._state_store.app_state.translation.items
        self._loading_dialog = LoadingDialogComponent(translation)
        self._page.show_dialog(self._loading_dialog)

    def _close_loading_dialog(self) -> None:
        if self._loading_dialog:
            self._page.pop_dialog()
        self._loading_dialog = None

    def _open_error_dialog(self, message_key: str | None = None, message: str | None = None) -> None:
        translation = self._state_store.app_state.translation.items
        error_dialog = ErrorDialogComponent(
            translation=translation,
            message_key=message_key,
            message=message,
            on_ok_clicked=lambda _: self._page.pop_dialog(),
        )
        self._page.show_dialog(error_dialog)

    def _open_message_dialog(self, message_key: str) -> None:
        translation = self._state_store.app_state.translation.items
        message_dialog = MessageDialogComponent(
            translation=translation,
            message_key=message_key,
            on_ok_clicked=lambda _: self._page.pop_dialog(),
        )
        self._page.show_dialog(message_dialog)

    async def _show_confirm_dialog(self, message_key: str) -> bool:
        translation = self._state_store.app_state.translation.items
        confirm_dialog = ConfirmDialogComponent(translation=translation, message_key=message_key)
        self._page.show_dialog(confirm_dialog)
        try:
            return await confirm_dialog.future
        finally:
            self._page.pop_dialog()

    def _get_tab_title(self, key: str, id: int | None) -> str:
        translation_state = self._state_store.app_state.translation
        title = translation_state.items.get(key)
        if id:
            return f"{title}: {id}"
        return title

    def __add_unsubscriber(self, func: Callable[[], None]) -> None:
        self.__unsubscribers.append(func)
