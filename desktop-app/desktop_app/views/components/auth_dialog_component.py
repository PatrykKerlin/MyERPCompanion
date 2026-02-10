from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft


from views.base.base_component import BaseComponent
from views.base.base_dialog import BaseDialog

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController
    from utils.translation import Translation


class AuthDialogComponent(BaseComponent, BaseDialog):
    def __init__(self, controller: AuthDialogController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        login_field = ft.TextField(label=translation.get("login"), autofocus=True)
        password_field = ft.TextField(label=translation.get("password"), password=True, can_reveal_password=True)
        cancel_button = ft.Button(
            content=translation.get("cancel"),
            on_click=lambda _: controller.on_cancel_click(),
            
        )
        login_button = ft.Button(
            content=translation.get("log_in"),
            on_click=lambda _: controller.on_login_click(
                login_field.value or "",
                password_field.value or "",
            ),
            
        )
        BaseDialog.__init__(
            self,
            controls=[login_field, password_field],
            actions=[cancel_button, login_button],
            title=translation.get("login"),
        )
