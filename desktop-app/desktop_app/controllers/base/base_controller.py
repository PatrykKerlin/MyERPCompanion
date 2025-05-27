from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import flet as ft

from config import Context
from helpers import SafeExecutor
from services.base import BaseService
from views.components import ErrorDialog, LoadingDialog

TService = TypeVar("TService", bound=BaseService)


class BaseController(ABC, Generic[TService]):
    _service_cls: type[TService]

    def __init__(self, context: Context) -> None:
        self._context = context
        self._executor = SafeExecutor(context.page)
        self._service = self._service_cls(context)

    @abstractmethod
    def show(self, *args, **kwargs) -> None:
        pass

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
