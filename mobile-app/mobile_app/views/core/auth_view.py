from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
from styles.styles import AlignmentStyles, AuthViewStyles, ButtonStyles
from utils.translation import Translation
from views.base.base_component import BaseComponent
from views.mixins.input_controls_mixin import InputControlsMixin

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController


class AuthView(InputControlsMixin, ft.Container):
    def __init__(self, controller: AuthDialogController, translation: Translation) -> None:
        self.__controller = controller
        self.__translation = translation

        self.__login_field = self._get_text_field(
            label=self.__translation.get("login"),
            autofocus=True,
            on_change=self.__on_username_changed,
            expand=True,
            auto_submit_on_tap_outside=False,
        )
        self.__password_field = self._get_text_field(
            label=self.__translation.get("password"),
            password=True,
            can_reveal_password=True,
            expand=True,
        )
        self.__warehouse_dropdown = self._get_dropdown(
            label=self.__translation.get("warehouses"),
            options=[],
            disabled=True,
            expand=True,
        )

        self.__login_field.on_submit = lambda _: self.__password_field.focus()
        self.__password_field.on_submit = self.__on_login

        login_button = self._get_button(
            content=self.__translation.get("log_in"),
            on_click=self.__on_login,
            style=ButtonStyles.primary_regular,
        )

        form = ft.Column(
            controls=[
                self.__login_field,
                self.__password_field,
                self.__warehouse_dropdown,
                login_button,
            ],
            tight=True,
            horizontal_alignment=AuthViewStyles.FORM_STRETCH,
        )
        form_row = ft.ResponsiveRow(
            controls=[ft.Container(content=form, col=AuthViewStyles.FORM_COL)],
            columns=AuthViewStyles.FORM_ROW_COLUMNS,
            alignment=AlignmentStyles.AXIS_CENTER,
            vertical_alignment=AlignmentStyles.CROSS_START,
        )

        title_text = self.__translation.get("my_erp_companion")
        subtitle_text = self.__translation.get("mobile_portal")
        portal_text = self._get_label(
            title_text,
            style=AuthViewStyles.TITLE_STYLE,
            text_align=AuthViewStyles.TITLE_ALIGN,
        )
        subtitle = self._get_label(
            subtitle_text,
            text_align=AuthViewStyles.SUBTITLE_ALIGN,
        )

        hero_body = ft.Container(
            alignment=AuthViewStyles.HERO_ALIGNMENT,
            padding=AuthViewStyles.HERO_PADDING,
            content=ft.Column(
                controls=[
                    portal_text,
                    subtitle,
                    ft.Container(height=AuthViewStyles.HERO_FORM_SPACER_HEIGHT),
                    form_row,
                ],
                tight=AuthViewStyles.HERO_COLUMN_TIGHT,
                horizontal_alignment=AuthViewStyles.HERO_COLUMN_HORIZONTAL_ALIGNMENT,
            ),
        )
        hero_card = ft.Card(content=hero_body, bgcolor=AuthViewStyles.HERO_CARD_BGCOLOR)
        hero_wrapper = ft.Container(
            content=ft.ResponsiveRow(
                controls=[ft.Container(content=hero_card, col=AuthViewStyles.HERO_COL)],
                columns=AuthViewStyles.HERO_ROW_COLUMNS,
                alignment=AlignmentStyles.AXIS_CENTER,
                vertical_alignment=AlignmentStyles.CROSS_START,
            ),
            alignment=AlignmentStyles.CENTER,
            padding=AuthViewStyles.HERO_WRAPPER_PADDING,
        )
        centered_layout = ft.Column(
            controls=[
                ft.Container(expand=True),
                hero_wrapper,
                ft.Container(expand=True),
            ],
            expand=True,
            spacing=AuthViewStyles.CENTERED_LAYOUT_SPACING,
            horizontal_alignment=AuthViewStyles.CENTERED_LAYOUT_HORIZONTAL_ALIGNMENT,
        )

        ft.Container.__init__(
            self,
            content=centered_layout,
            expand=True,
            alignment=AlignmentStyles.CENTER,
        )

    def set_warehouse_options(self, options: list[tuple[int, str]]) -> None:
        sorted_options = sorted(options, key=lambda option: option[0])
        self.__warehouse_dropdown.options = [
            ft.dropdown.Option(key=str(warehouse_id), text=name) for warehouse_id, name in sorted_options
        ]
        if sorted_options:
            self.__warehouse_dropdown.value = str(sorted_options[0][0])
            self.__warehouse_dropdown.disabled = len(sorted_options) == 1
        else:
            self.__warehouse_dropdown.value = None
            self.__warehouse_dropdown.disabled = True
        BaseComponent.safe_update(self.__warehouse_dropdown)

    def __on_username_changed(self, _: ft.Event[ft.TextField]) -> None:
        self.__controller.on_mobile_username_changed(self.__login_field.value)

    def __on_login(self, _: ft.Event[ft.Button] | ft.Event[ft.TextField]) -> None:
        self.__controller.on_login_click(
            self.__login_field.value or "",
            self.__password_field.value or "",
            self.__get_selected_warehouse_id(),
        )

    def __get_selected_warehouse_id(self) -> int | None:
        value = self.__warehouse_dropdown.value
        if not value:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
