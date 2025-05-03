from typing import Generic, TypeVar

import customtkinter as ctk

from config import Context
from services.base import BaseService
from views.base import BaseView

TService = TypeVar("TService", bound=BaseService)
TView = TypeVar("TView", bound=BaseView)


class BaseController(Generic[TService, TView]):
    _service_cls: type[TService]
    _view_cls: type[TView]

    def __init__(self, master: ctk.CTk, context: Context) -> None:
        self._service = self._service_cls(context.settings)
        self._view = self._view_cls(master, self, context.language)
        self._context = context

    def show(self) -> None:
        self._view.show()
