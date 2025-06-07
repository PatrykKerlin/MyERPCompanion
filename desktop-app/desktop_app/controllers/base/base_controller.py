from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic
from collections.abc import Awaitable, Callable
import asyncio

import flet as ft

from services.base import BaseService
from views.components import ErrorDialogComponent, LoadingDialogComponent

if TYPE_CHECKING:
    from config.context import Context

TService = TypeVar("TService", bound=BaseService)


class BaseController(Generic[TService]):
    _service_cls: type[TService] | None = None

    def __init__(self, context: Context) -> None:
        self._context = context
        if self._service_cls:
            self._service = self._service_cls(context)

    def _show_loading_dialog(self) -> LoadingDialogComponent:
        loading_dialog = LoadingDialogComponent(self._context.texts)
        self._open_dialog(loading_dialog)
        return loading_dialog

    def _show_error_dialog(self, message_key: str) -> None:
        error_dialog = ErrorDialogComponent(
            texts=self._context.texts,
            message_key=message_key,
            on_click=lambda _: self._close_dialog(error_dialog),
        )
        self._open_dialog(error_dialog)

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self._context.page.overlay.append(dialog)
        dialog.open = True
        self._context.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog) -> None:
        dialog.open = False
        self._context.page.update()
        self._context.page.overlay.remove(dialog)

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
