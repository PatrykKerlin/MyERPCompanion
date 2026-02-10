from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.user_controller import UserController


class UserView(BaseView):
    def __init__(
        self,
        controller: UserController,
        translation: Translation,
        mode: ViewMode,
        view_key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
        selected_language_id: int,
        selected_theme: str,
    ) -> None:
        super().__init__(controller, translation, mode, view_key, data_row, 0, 0, caller_view_key=View.CURRENT_USER)
        self.__languages = languages
        self.__selected_language_id = selected_language_id
        self.__selected_theme = selected_theme

        self.__title = ft.Text(size=20, weight=ft.FontWeight.BOLD)
        self.__subtitle = ft.Text(size=14)
        self.__back_button = ft.Button(on_click=self.__on_back_click, width=220)
        self.__header_texts = ft.Column(
            controls=[self.__title, self.__subtitle],
            spacing=2,
            expand=True,
        )
        self.__header_row = ft.Row(
            controls=[
                self.__header_texts,
                ft.Container(content=self.__back_button, alignment=ft.Alignment.CENTER_RIGHT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        self.__password_input = ft.TextField(password=True, can_reveal_password=True, expand=True)
        self.__password_repeat_input = ft.TextField(password=True, can_reveal_password=True, expand=True)

        self.__language_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key=str(language_id), text=label) for language_id, label in self.__languages],
            value=str(self.__selected_language_id),
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__theme_dropdown = ft.Dropdown(
            options=[],
            value=self.__selected_theme,
            expand=True,
        )

        self.__save_button = ft.Button(on_click=self.__on_save_click)

        self.__fields = ft.Column(
            controls=[
                ft.Container(content=self.__password_input),
                ft.Container(content=self.__password_repeat_input),
                ft.Container(content=self.__language_dropdown),
                ft.Container(content=self.__theme_dropdown),
            ],
            spacing=10,
        )
        self.__actions_row = ft.Row(
            controls=[self.__save_button],
            alignment=ft.MainAxisAlignment.END,
        )

        self._master_column.controls = [
            self.__header_row,
            ft.Divider(height=1),
            self.__fields,
            ft.Divider(height=1),
            self.__actions_row,
        ]
        self.__render_static_texts()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.__safe_update()

    def clear_password_inputs(self) -> None:
        self.__password_input.value = ""
        self.__password_repeat_input.value = ""
        self.__safe_update_control(self.__password_input)
        self.__safe_update_control(self.__password_repeat_input)

    def set_language_options(self, languages: list[tuple[int, str]], selected_language_id: int) -> None:
        self.__languages = languages
        self.__selected_language_id = selected_language_id
        self.__language_dropdown.options = [
            ft.dropdown.Option(key=str(language_id), text=label) for language_id, label in self.__languages
        ]
        self.__language_dropdown.value = str(self.__selected_language_id)
        self.__safe_update_control(self.__language_dropdown)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("current_user")
        self.__subtitle.value = self._translation.get("employee_portal_subtitle")
        self.__back_button.content = self._translation.get("back_to_menu")
        self.__save_button.content = self._translation.get("save")

        self.__password_input.label = self._translation.get("password")
        self.__password_repeat_input.label = self._translation.get("password_repeat")
        self.__language_dropdown.label = self._translation.get("language_id")
        self.__theme_dropdown.label = self._translation.get("theme")

        theme_options = [
            ("system", self._translation.get("system")),
            ("dark", self._translation.get("dark")),
            ("light", self._translation.get("light")),
        ]
        self.__theme_dropdown.options = [
            ft.dropdown.Option(key=value, text=label) for value, label in theme_options
        ]
        if self.__theme_dropdown.value not in {option[0] for option in theme_options}:
            self.__theme_dropdown.value = "system"

    def __on_back_click(self, _: ft.ControlEvent) -> None:
        self._controller.on_back_to_menu()

    def __on_save_click(self, _: ft.ControlEvent) -> None:
        selected_language_id = self.__parse_optional_int(self.__language_dropdown.value)
        selected_theme = self.__theme_dropdown.value or "system"
        self._controller.on_save_clicked(
            self.__password_input.value,
            self.__password_repeat_input.value,
            selected_language_id,
            selected_theme,
        )

    @staticmethod
    def __parse_optional_int(value: str | None) -> int | None:
        if value in {None, "", "0"}:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def __safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            return

    @staticmethod
    def __safe_update_control(control: ft.Control) -> None:
        try:
            _ = control.page
        except RuntimeError:
            return
        try:
            control.update()
        except RuntimeError:
            return
