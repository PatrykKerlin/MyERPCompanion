from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

import customtkinter as ctk

from views.base import BaseView

if TYPE_CHECKING:
    from controllers.base import BaseController

TController = TypeVar("TController", bound="BaseController")


class BaseModal(BaseView[TController], Generic[TController], ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk, controller: TController, language: str) -> None:
        ctk.CTkToplevel.__init__(self, master)
        self._content = ctk.CTkFrame(self)
        BaseView.__init__(self, master, controller, language)
        self.transient(self._master)
        self.grab_set()
        self.resizable(False, False)
        self._content.pack()
        self._build()

    def show(self, padding: tuple[int, int] = (20, 20)) -> None:
        self._content.pack_configure(padx=padding[0], pady=padding[1])
        self.update()
