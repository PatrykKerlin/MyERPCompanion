from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.core.auth_controller import AuthController


class AuthView(ft.Container):
    def __init__(self, controller: AuthController, translation: Translation) -> None:
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
            width=300,
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
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(16),
            content=ft.Column(
                controls=[portal_text, subtitle, ft.Container(height=12), form],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        hero_card = ft.Card(content=hero_body, width=360)

        ft.Container.__init__(
            self,
            content=hero_card,
            alignment=ft.Alignment.CENTER,
        )
