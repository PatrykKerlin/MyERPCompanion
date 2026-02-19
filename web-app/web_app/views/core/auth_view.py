from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, AuthViewStyles, ButtonStyles, TypographyStyles
from utils.translation import Translation
from views.mixins.input_controls_mixin import InputControlsMixin

if TYPE_CHECKING:
    from controllers.core.auth_controller import AuthController


class AuthView(InputControlsMixin, ft.Container):
    def __init__(self, controller: AuthController, translation: Translation) -> None:
        login_field = self._get_text_field(label=translation.get("login"), autofocus=True)
        password_field = self._get_text_field(label=translation.get("password"), password=True)

        def on_login() -> None:
            controller.on_login_click(login_field.value or "", password_field.value or "")

        login_button = ft.Button(
            content=translation.get("log_in"),
            on_click=on_login,
            style=ButtonStyles.primary_regular,
        )

        form = ft.Column(
            controls=[
                login_field,
                password_field,
                ft.Container(height=AppDimensions.SPACE_XS),
                login_button,
            ],
            tight=True,
            horizontal_alignment=AlignmentStyles.CROSS_STRETCH,
            width=AppDimensions.AUTH_FORM_WIDTH,
            spacing=AppDimensions.SPACE_MD,
        )

        app_name = translation.get("my_erp_companion")
        title_text = translation.get("customer_portal_title").format(app_name=app_name)
        subtitle_text = translation.get("customer_portal_subtitle")
        portal_text = ft.Text(
            title_text,
            style=TypographyStyles.AUTH_TITLE,
            text_align=ft.TextAlign.CENTER,
        )
        subtitle = ft.Text(
            subtitle_text,
            text_align=ft.TextAlign.CENTER,
        )

        hero_body = ft.Container(
            alignment=AlignmentStyles.CENTER,
            padding=AuthViewStyles.HERO_BODY_PADDING,
            content=ft.Column(
                controls=[portal_text, subtitle, ft.Container(height=AppDimensions.SPACE_XL), form],
                tight=True,
                horizontal_alignment=AlignmentStyles.CROSS_CENTER,
            ),
        )
        hero_card = ft.Card(
            content=hero_body,
            width=AppDimensions.AUTH_CARD_WIDTH,
            bgcolor=AuthViewStyles.HERO_CARD_BGCOLOR,
            margin=AuthViewStyles.HERO_CARD_MARGIN,
        )

        ft.Container.__init__(
            self,
            content=hero_card,
            alignment=AlignmentStyles.CENTER,
        )
