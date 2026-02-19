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
        self.__controller = controller
        self.__login_field = self._get_text_field(label=translation.get("login"), autofocus=True)
        self.__password_field = self._get_text_field(
            label=translation.get("password"),
            password=True,
            on_submit=lambda _: self.__on_login(),
        )

        login_button = self._get_button(
            content=translation.get("log_in"),
            on_click=self.__on_login,
            style=ButtonStyles.primary_regular,
        )

        form = ft.Column(
            controls=[
                self.__login_field,
                self.__password_field,
                ft.Container(height=AppDimensions.SPACE_XS),
                login_button,
            ],
            tight=True,
            horizontal_alignment=AlignmentStyles.CROSS_STRETCH,
            spacing=AppDimensions.SPACE_MD,
        )

        app_name_text = self._get_label(
            translation.get("my_erp_companion"),
            style=TypographyStyles.AUTH_TITLE,
            text_align=ft.TextAlign.CENTER,
        )
        portal_text = self._get_label(
            translation.get("customer_portal"),
            text_align=ft.TextAlign.CENTER,
        )

        hero_body = ft.Container(
            alignment=AlignmentStyles.CENTER,
            padding=AuthViewStyles.HERO_BODY_PADDING,
            content=ft.Column(
                controls=[app_name_text, portal_text, ft.Container(height=AppDimensions.SPACE_XL), form],
                tight=True,
                horizontal_alignment=AlignmentStyles.CROSS_CENTER,
            ),
        )
        hero_card = ft.Card(
            content=hero_body,
            bgcolor=AuthViewStyles.HERO_CARD_BGCOLOR,
            margin=AuthViewStyles.HERO_CARD_MARGIN,
        )

        root_row = ft.ResponsiveRow(
            columns=AuthViewStyles.ROOT_ROW_COLUMNS,
            alignment=AlignmentStyles.AXIS_CENTER,
            vertical_alignment=AlignmentStyles.CROSS_CENTER,
            controls=[
                ft.Container(
                    col=AuthViewStyles.HERO_CARD_COL,
                    alignment=AlignmentStyles.CENTER,
                    content=ft.Container(
                        width=AuthViewStyles.HERO_CARD_WIDTH,
                        content=hero_card,
                    ),
                )
            ],
        )

        ft.Container.__init__(
            self,
            content=root_row,
            alignment=AlignmentStyles.CENTER,
        )
    
    def __on_login(self) -> None:
        self.__controller.on_login_click(self.__login_field.value or "", self.__password_field.value or "")
