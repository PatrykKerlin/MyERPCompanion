from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter as ctk

from views.base import BaseModal

if TYPE_CHECKING:
    from ...controllers.core.auth_controller import AuthController


class AuthModal(BaseModal["AuthController"]):
    def __init__(self, master: ctk.CTk, controller: AuthController, texts: dict[str, str]) -> None:
        self.username_entry: ctk.CTkEntry
        self.password_entry: ctk.CTkEntry
        self.login_button: ctk.CTkButton
        self.spinner: ctk.CTkProgressBar
        super().__init__(master, controller, texts)

    def _build(self) -> None:
        self.username_entry = ctk.CTkEntry(self._content, placeholder_text="Username")
        self.username_entry.pack(fill="x", pady=(0, 10))
        self.password_entry = ctk.CTkEntry(self._content, placeholder_text="Password", show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))
        self.login_button = ctk.CTkButton(self._content, text="Login", command=self.__on_login_click)
        self.login_button.pack(fill="x", pady=(0, 10))
        self.spinner = ctk.CTkProgressBar(self._content, mode="indeterminate")
        self.spinner.pack(fill="x", pady=(0, 10))
        self.spinner.stop()

    def __on_login_click(self) -> None:
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.login_button.configure(state="disabled")
        self.spinner.start()
        self._controller.login(username, password)

    def on_login_success(self) -> None:
        self.spinner.stop()
        self.destroy()

    def on_login_error(self, error: str) -> None:
        self.spinner.stop()
        self.login_button.configure(state="normal")
        ctk.CTkLabel(self._content, text=f"Error: {error}").pack(fill="x", pady=(0, 5))
