from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController


class AuthView(BaseView["AuthDialogController"]):
    def __init__(self, controller: AuthDialogController, translation: Translation) -> None:
        BaseView.__init__(
            self,
            controller=controller,
            translation=translation,
            mode=ViewMode.READ,
            view_key=View.LOGIN,
            data_row=None,
            base_label_size=0,
            base_input_size=0,
            base_columns_qty=12,
        )
        self._cancel_button = None
        self._save_button = None
        self._search_button = None

        login_field = ft.TextField(
            label=translation.get("login"),
            autofocus=True,
        )
        password_field = ft.TextField(
            label=translation.get("password"),
            password=True,
            can_reveal_password=True,
        )

        def on_login(_: ft.ControlEvent) -> None:
            controller.on_login_click(login_field.value or "", password_field.value or "")

        login_button = ft.Button(
            content=translation.get("log_in"),
            on_click=on_login,
        )

        form = ft.Column(
            controls=[
                login_field,
                password_field,
                login_button,
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=320,
        )

        app_name = translation.get("my_erp_companion")
        title_text = translation.get("customer_portal_title").format(app_name=app_name)
        subtitle_text = translation.get("customer_portal_subtitle")
        portal_text = ft.Text(
            title_text,
            size=18,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        subtitle = ft.Text(
            subtitle_text,
            text_align=ft.TextAlign.CENTER,
        )

        hero_body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(24),
            content=ft.Column(
                controls=[portal_text, subtitle, ft.Container(height=12), form],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        hero_card = ft.Card(content=hero_body, expand=2)
        hero_row = ft.Row(
            expand=2,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=1),
                hero_card,
                ft.Container(expand=1),
            ],
        )

        self.content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(expand=1),
                hero_row,
                ft.Container(expand=1),
            ],
        )
