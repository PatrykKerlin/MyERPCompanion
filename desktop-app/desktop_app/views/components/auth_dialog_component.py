from __future__ import annotations
from typing import TYPE_CHECKING

import flet as ft

from styles import ButtonStyles
from views.base import BaseDialog, BaseComponent

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController


class AuthDialogComponent(BaseComponent, BaseDialog):
    def __init__(self, controller: AuthDialogController, texts: dict[str, str]) -> None:
        BaseComponent.__init__(self, controller, texts)
        login_field = ft.TextField(label=texts["login"], autofocus=True)
        password_field = ft.TextField(label=texts["password"], password=True, can_reveal_password=True)
        cancel_button = ft.Button(
            text=texts["cancel"],
            on_click=lambda _: controller.on_cancel_click(),
            style=ButtonStyles.small_padding,
        )
        login_button = ft.ElevatedButton(
            text=texts["log_in"],
            on_click=lambda _: controller.on_login_click(
                login_field.value or "",
                password_field.value or "",
            ),
            style=ButtonStyles.small_padding,
        )
        BaseDialog.__init__(
            self,
            controls=[login_field, password_field],
            actions=[cancel_button, login_button],
            title=texts["login"],
        )
