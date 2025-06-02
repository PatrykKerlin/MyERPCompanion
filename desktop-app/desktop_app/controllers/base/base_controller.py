from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from views.components import ErrorDialog, LoadingDialog

if TYPE_CHECKING:
    from config.context import Context


class BaseController:

    def __init__(self, context: Context) -> None:
        self._context = context

    def show(self, *args, **kwargs) -> None: ...

    def _show_loading_dialog(self) -> LoadingDialog:
        loading_dialog = LoadingDialog(self._context.texts)
        self._open_dialog(loading_dialog)
        return loading_dialog

    def _show_error_dialog(self, message_key: str) -> None:
        error_dialog = ErrorDialog(
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
