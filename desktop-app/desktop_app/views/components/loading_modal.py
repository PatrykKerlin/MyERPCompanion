from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from views.base import BaseModal

if TYPE_CHECKING:
    from ...controllers.core.app_controller import AppController


class LoadingModal(BaseModal["AppController"]):
    def _build(self) -> None:
        text = self._texts.get("loading", "Loading...")
        label = ctk.CTkLabel(self._content, text=text, font=ctk.CTkFont(size=14))
        self.title(text)
        label.pack(fill="x", pady=(0, 10))
        spinner = ctk.CTkProgressBar(self._content, mode="indeterminate")
        spinner.pack(fill="x")
        spinner.start()
