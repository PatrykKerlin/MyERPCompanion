from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import ButtonStyles, ControlStyles
from views.base.base_component import BaseComponent
from views.base.base_dialog import BaseDialog

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController
    from utils.translation import Translation


class AuthDialogComponent(BaseComponent, BaseDialog):
    def __init__(self, controller: AuthDialogController, translation: Translation) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__login_field = ft.TextField(label=translation.get("login"), autofocus=True)
        self.__login_field.border_radius = ControlStyles.FIELD_BORDER_RADIUS
        self.__login_field.border_color = ControlStyles.FIELD_BORDER_COLOR
        self.__login_field.focused_border_color = ControlStyles.FIELD_FOCUSED_BORDER_COLOR
        self.__login_field.height = ControlStyles.TEXT_FIELD_HEIGHT
        self.__login_field.content_padding = ControlStyles.FIELD_PADDING
        self.__login_field.on_submit = lambda _: self.__on_login()

        self.__password_field = ft.TextField(label=translation.get("password"), password=True, can_reveal_password=True)
        self.__password_field.border_radius = ControlStyles.FIELD_BORDER_RADIUS
        self.__password_field.border_color = ControlStyles.FIELD_BORDER_COLOR
        self.__password_field.focused_border_color = ControlStyles.FIELD_FOCUSED_BORDER_COLOR
        self.__password_field.height = ControlStyles.TEXT_FIELD_HEIGHT
        self.__password_field.content_padding = ControlStyles.FIELD_PADDING
        self.__password_field.on_submit = lambda _: self.__on_login()
        cancel_button = ft.Button(
            content=translation.get("cancel"),
            on_click=lambda _: controller.on_cancel_click(),
            style=ButtonStyles.regular,
        )
        login_button = ft.Button(
            content=translation.get("log_in"),
            on_click=lambda _: self.__on_login(),
            style=ButtonStyles.primary_compact,
        )
        BaseDialog.__init__(
            self,
            controls=[self.__login_field, self.__password_field],
            actions=[cancel_button, login_button],
            title=translation.get("login"),
        )

    def __on_login(self) -> None:
        self._controller.on_login_click(
            self.__login_field.value or "",
            self.__password_field.value or "",
        )
