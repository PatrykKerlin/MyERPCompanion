from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk

from views.base import BaseWindow
from views.components import MenuBar

if TYPE_CHECKING:
    from ...controllers.core.app_controller import AppController


class AppWindow(BaseWindow["AppController"]):
    def __init__(self, master: ctk.CTk, controller: AppController, texts: dict[str, str]) -> None:
        super().__init__(master, controller, texts)

    def _build(self) -> None:
        title = self._texts.get("myerpcompanion", "...")
        self._master.title(title)
        self._master.geometry("1024x768")
        self._master.minsize(800, 600)

    def show(self) -> None:
        self.pack(fill="both", expand=True)

    def rebuild_window(self) -> None:
        MenuBar(
            master=self,
            app_window=self._master,
            user_label="Gość",
            user_actions=[
                ("Wyloguj", self._master.quit),
            ],
        )
        title = self._texts.get("myerpcompanion", "...")
        self._master.title(title)
