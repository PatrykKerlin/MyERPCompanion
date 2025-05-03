from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import customtkinter as ctk

from views.base import BaseView

if TYPE_CHECKING:
    from controllers.base import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseWindow(BaseView[TController], Generic[TController], ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, controller: TController, language: str) -> None:
        ctk.CTkFrame.__init__(self, master)
        BaseView.__init__(self, master, controller, language)
        self._build()

    def show(self) -> None:
        self.pack(fill="both", expand=True)
