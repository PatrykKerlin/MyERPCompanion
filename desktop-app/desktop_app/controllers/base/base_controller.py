from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

import flet as ft
import httpx

from schemas.base.base_schema import BasePlainSchema
from schemas.core.token_schema import TokenPlainSchema
from views.components.error_dialog_component import ErrorDialogComponent
from views.components.loading_dialog_component import LoadingDialogComponent

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
        self._view_event_map = context.view_event_map
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

    def _show_loading_dialog(self) -> LoadingDialogComponent:
        translation_state = self._state_store.app_state.translation
        loading_dialog = LoadingDialogComponent(translation_state.items)
        self._open_dialog(loading_dialog)
        return loading_dialog

    def _show_error_dialog(self, message_key: str | None = None, message: str | None = None) -> None:
        translation = self._state_store.app_state.translation.items
        error_dialog = ErrorDialogComponent(
            translation=translation,
            message_key=message_key,
            message=message,
            on_click=lambda _: self._close_dialog(error_dialog),
        )
        self._open_dialog(error_dialog)

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        self.__close_and_remove_dialog(dialog)

    async def _close_dialog_with_delay(self, dialog: ft.AlertDialog, delay: float = 0.5) -> None:
        await asyncio.sleep(delay)
        self.__close_and_remove_dialog(dialog)

    async def _call_with_refresh(
        self,
        service: BaseService,
        func: Callable[
            [str | None, dict[str, Any] | None, TokenPlainSchema | None, str | None],
            Awaitable[TPlainSchema | list[TPlainSchema]],
        ],
        path_param: str | None = None,
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

    def __close_and_remove_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        self._page.update()
        self._page.overlay.remove(dialog)

    def __add_unsubscriber(self, func: Callable[[], None]) -> None:
        self.__unsubscribers.append(func)

    # from __future__ import annotations

    # import asyncio
    # from collections.abc import Awaitable, Callable
    # from typing import TYPE_CHECKING

    # import flet as ft

    # from views.components import (
    #     ConfirmDialogComponent,
    #     ErrorDialogComponent,
    #     LoadingDialogComponent,
    #     MessageDialogComponent,
    # )

    # if TYPE_CHECKING:
    #     from config.context import Context

    # class BaseController:
    #     def __init__(self, context: Context) -> None:
    #         self._context = context

    #     def _show_loading_dialog(self) -> LoadingDialogComponent:
    #         loading_dialog = LoadingDialogComponent(self._context.texts)
    #         self._open_dialog(loading_dialog)
    #         return loading_dialog

    #     def _show_message_dialog(self, message_key: str) -> None:
    #         message_dialog = MessageDialogComponent(
    #             texts=self._context.texts,
    #             message_key=message_key,
    #             on_click=lambda: self._close_dialog(message_dialog),
    #         )
    #         self._open_dialog(message_dialog)

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
