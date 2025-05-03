from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk

from views.base import BaseWindow

if TYPE_CHECKING:
    from controllers.core import AppController


class AppWindow(BaseWindow["AppController"]):
    def __init__(self, master: ctk.CTk, controller: AppController, language: str) -> None:
        super().__init__(master, controller, language)

    def _build(self) -> None:
        title_map = {"en": "MyERPCompanion", "pl": "MójERPTowarzysz"}
        self._master.title(title_map.get(self._language, title_map["en"]))
        self._master.geometry("1024x768")
        self._master.minsize(800, 600)

    def show(self) -> None:
        self.pack(fill="both", expand=True)
