from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import flet as ft

from views.components import (
    ConfirmDialogComponent,
    ErrorDialogComponent,
    LoadingDialogComponent,
    MessageDialogComponent,
)

if TYPE_CHECKING:
    from config.context import Context


class BaseController:
    def __init__(self, context: Context) -> None:
        self._context = context

    def _show_loading_dialog(self) -> LoadingDialogComponent:
        loading_dialog = LoadingDialogComponent(self._context.texts)
        self._open_dialog(loading_dialog)
        return loading_dialog

    def _show_error_dialog(self, message_key: str | None = None, message: str | None = None) -> None:
        error_dialog = ErrorDialogComponent(
            texts=self._context.texts,
            message_key=message_key,
            message=message,
            on_click=lambda _: self._close_dialog(error_dialog),
        )
        self._open_dialog(error_dialog)

    def _show_message_dialog(self, message_key: str) -> None:
        message_dialog = MessageDialogComponent(
            texts=self._context.texts,
            message_key=message_key,
            on_click=lambda: self._close_dialog(message_dialog),
        )
        self._open_dialog(message_dialog)

    async def _show_confirm_dialog(self, message_key: str) -> bool:
        confirm_dialog = ConfirmDialogComponent(
            texts=self._context.texts,
            message_key=message_key,
            loop=self._context.page.loop,
        )
        self._open_dialog(confirm_dialog)
        result = await confirm_dialog.future
        self._close_dialog(confirm_dialog)
        return result

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self._context.page.overlay.append(dialog)
        dialog.open = True
        self._context.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        self.__close_and_remove_dialog(dialog)

    async def _close_dialog_with_delay(self, dialog: ft.AlertDialog, delay: float = 0.2) -> None:
        await asyncio.sleep(delay)
        self.__close_and_remove_dialog(dialog)

    def _remove_control(self, parent: ft.Control, child: ft.Control) -> None:
        if hasattr(parent, "controls"):
            controls = getattr(parent, "controls")
            if isinstance(controls, list) and child in controls:
                controls.remove(child)
                self._context.page.update()

    def _run_with_delay(
        self,
        condition: Callable[[], bool],
        callback: Callable[[], Awaitable[None]],
        max_retries: int = 100,
        delay: float = 0.01,
    ) -> None:
        async def delayed_execution() -> None:
            for _ in range(max_retries):
                if condition():
                    break
                await asyncio.sleep(delay)
            else:
                return
            await callback()

        self._context.page.run_task(delayed_execution)

    def __close_and_remove_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        self._context.page.update()
        self._context.page.overlay.remove(dialog)
