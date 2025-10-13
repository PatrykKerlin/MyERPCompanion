from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

import asyncio
import flet as ft
import httpx

from schemas.base.base_schema import BasePlainSchema
from schemas.core.param_schema import PaginatedResponseSchema
from schemas.core.token_schema import TokenPlainSchema
from views.components.error_dialog_component import ErrorDialogComponent
from views.components.loading_dialog_component import LoadingDialogComponent
from views.components.message_dialog_component import MessageDialogComponent

if TYPE_CHECKING:
    from config.context import Context
    from services.base.base_service import BaseService

TPlainSchema = TypeVar("TPlainSchema", bound=BasePlainSchema)


class BaseController:
    def __init__(self, context: Context) -> None:
        self._settings = context.settings
        self._page = context.page
        self._logger = context.logger
        self._event_bus = context.event_bus
        self._state_store = context.state_store
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

    def _subscribe_event_handlers(self, event_handlers: dict[type[Any], Callable[[Any], Awaitable[None]]]) -> None:
        for event, handler in event_handlers.items():
            unsubscriber = self._event_bus.subscribe(event, handler)
            self.__add_unsubscriber(unsubscriber)

    def _subscribe_state_listeners(self, state_listeners: dict[str, Callable[[Any], None]]) -> None:
        for state, listener in state_listeners.items():
            unsubscriber = self._state_store.subscribe(state, listener)
            self.__add_unsubscriber(unsubscriber)

    def _open_loading_dialog(self) -> None:
        translation_state = self._state_store.app_state.translation
        self._loading_dialog = LoadingDialogComponent(translation_state.items)
        self._open_dialog(self._loading_dialog)

    def _close_loading_dialog(self) -> None:
        if self._loading_dialog:
            self._close_dialog(self._loading_dialog)
        self._loading_dialog = None

    def _open_error_dialog(self, message_key: str | None = None, message: str | None = None) -> None:
        translation = self._state_store.app_state.translation.items
        error_dialog = ErrorDialogComponent(
            translation=translation,
            message_key=message_key,
            message=message,
            on_click=lambda _: self._close_dialog(error_dialog),
        )
        self._open_dialog(error_dialog)

    def _open_message_dialog(self, message_key: str) -> None:
        translation_state = self._state_store.app_state.translation
        message_dialog = MessageDialogComponent(
            translation=translation_state.items,
            message_key=message_key,
            on_ok_clicked=lambda: self._close_dialog(message_dialog),
        )
        self._open_dialog(message_dialog)

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self._page.open(dialog)
        self._page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        self._page.close(dialog)
        self._page.update()

    async def _call_api_with_token_refresh(
        self,
        service: BaseService,
        func: Callable[[int | None, dict[str, Any] | None, TokenPlainSchema | None, str | None], Any],
        path_param: int | None = None,
        query_or_body_params: dict[str, Any] | None = None,
        view_key: str | None = None,
    ) -> Any:
        if not self._state_store.app_state.tokens:
            raise
        token = TokenPlainSchema(**self._state_store.app_state.tokens.model_dump())
        try:
            return await func(path_param, query_or_body_params, token, view_key)
        except httpx.HTTPStatusError as first_error:
            self._logger.error(str(first_error))
            if first_error.response.status_code == httpx.codes.UNAUTHORIZED:
                try:
                    new_token = await service.refresh_token(token)
                    self._state_store.update(token={**new_token.model_dump()})
                    return await func(path_param, query_or_body_params, new_token, view_key)
                except Exception as refresh_error:
                    self._logger.error(str(refresh_error))
                    raise
            raise

    async def _run_with_delay(self, func: Callable[[], None], delay: float = 0.1) -> None:
        await asyncio.sleep(delay)
        func()

    def _get_tab_title(self, key: str, postfix: int | None) -> str:
        translation_state = self._state_store.app_state.translation
        title = translation_state.items.get(key)
        if postfix:
            return f"{title}: {postfix}"
        return title

    def __add_unsubscriber(self, func: Callable[[], None]) -> None:
        self.__unsubscribers.append(func)

    #     async def _show_confirm_dialog(self, message_key: str) -> bool:
    #         confirm_dialog = ConfirmDialogComponent(
    #             texts=self._context.texts,
    #             message_key=message_key,
    #             loop=self._context.page.loop,
    #         )
    #         self._open_dialog(confirm_dialog)
    #         result = await confirm_dialog.future
    #         self._close_dialog(confirm_dialog)
    #         return result

    #     def _remove_control(self, parent: ft.Control, child: ft.Control) -> None:
    #         if hasattr(parent, "controls"):
    #             controls = getattr(parent, "controls")
    #             if isinstance(controls, list) and child in controls:
    #                 controls.remove(child)
    #                 self._context.page.update()

    # def _run_with_delay(
    #     self,
    #     condition: Callable[[], bool],
    #     callback: Callable[[], Awaitable[None]],
    #     max_retries: int = 100,
    #     delay: float = 0.01,
    # ) -> None:
    #     async def delayed_execution() -> None:
    #         for _ in range(max_retries):
    #             if condition():
    #                 break
    #             await asyncio.sleep(delay)
    #         else:
    #             return
    #         await callback()

    #     self._page.run_task(delayed_execution)
