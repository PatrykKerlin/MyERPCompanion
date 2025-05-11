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
        self._service = self._service_cls(context)
        self._context = context
        self._master = master
        self.__view: TView | None = None

    def show(self) -> None:
        if self.__view is None:
            self.__view = self._view_cls(self._master, self, self._context.texts)
        self.__view.show()

    @property
    def _view(self) -> TView:
        if self.__view is None:
            raise RuntimeError(f"{self.__class__.__name__} has no view initialized.")
        return self.__view
