from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.components.auth_dialog_controller import AuthDialogController


class AuthView(ft.Container):
    def __init__(self, controller: AuthDialogController, translation: Translation) -> None:
        self.__controller = controller
        self.__translation = translation
        form_width = 320

        self.__login_field = ft.TextField(
            label=self.__translation.get("login"),
            autofocus=True,
            on_change=self.__on_username_changed,
            width=form_width,
        )
        self.__password_field = ft.TextField(
            label=self.__translation.get("password"),
            password=True,
            can_reveal_password=True,
            width=form_width,
        )
        self.__warehouse_dropdown = ft.Dropdown(
            label=self.__translation.get("warehouses"),
            options=[],
            disabled=True,
            width=form_width,
        )

        self.__login_field.on_submit = lambda _: self.__password_field.focus()
        self.__password_field.on_submit = self.__on_login

        login_button = ft.Button(
            content=self.__translation.get("log_in"),
            on_click=self.__on_login,
        )

        form = ft.Column(
            controls=[
                self.__login_field,
                self.__password_field,
                self.__warehouse_dropdown,
                login_button,
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            width=form_width,
        )

        app_name = self.__translation.get("my_erp_companion")
        title_text = self.__translation.get("employee_portal_title").format(app_name=app_name)
        subtitle_text = self.__translation.get("employee_portal_subtitle")
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
        hero_card = ft.Card(content=hero_body, width=form_width)

        ft.Container.__init__(
            self,
            content=hero_card,
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(horizontal=12, vertical=16),
        )

    def set_warehouse_options(self, options: list[tuple[int, str]]) -> None:
        sorted_options = sorted(options, key=lambda option: option[0])
        self.__warehouse_dropdown.options = [
            ft.dropdown.Option(key=str(warehouse_id), text=name)
            for warehouse_id, name in sorted_options
        ]
        if sorted_options:
            self.__warehouse_dropdown.value = str(sorted_options[0][0])
            self.__warehouse_dropdown.disabled = len(sorted_options) == 1
        else:
            self.__warehouse_dropdown.value = None
            self.__warehouse_dropdown.disabled = True
        self.__update_control_if_attached(self.__warehouse_dropdown)

    def __on_username_changed(self, _: ft.ControlEvent) -> None:
        self.__controller.on_mobile_username_changed(self.__login_field.value)

    def __on_login(self, _: ft.ControlEvent) -> None:
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

    @staticmethod
    def __update_control_if_attached(control: ft.Control) -> None:
        try:
            control.update()
        except RuntimeError:
            return
