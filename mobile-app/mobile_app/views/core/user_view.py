from __future__ import annotations

from typing import TYPE_CHECKING, cast

import flet as ft
from schemas.validation.constraints import Constraints
from styles.styles import ButtonStyles, MobileCommonViewStyles, TypographyStyles, UserViewStyles
from utils.enums import View
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.user_controller import UserController


class UserView(BaseView):
    def __init__(
        self,
        controller: UserController,
        translation: Translation,
        view_key: View,
        languages: list[tuple[int, str]],
        selected_language_id: int,
        selected_theme: Constraints.Theme,
    ) -> None:
        super().__init__(controller, translation, view_key, caller_view_key=View.CURRENT_USER)
        self.__languages = languages
        self.__selected_language_id = selected_language_id
        self.__selected_theme = selected_theme

        self.__title = self._get_label("", style=TypographyStyles.HEADER_TITLE)
        self.__back_button = self._get_button(
            content=self._translation.get("back"),
            on_click=self.__on_back_click,
            style=ButtonStyles.primary_regular,
        )
        self.__header_texts = ft.Column(
            controls=[self.__title],
            spacing=MobileCommonViewStyles.HEADER_TEXTS_SPACING,
        )
        self.__header_row = ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.__header_texts, col=MobileCommonViewStyles.HEADER_TEXTS_COL),
                ft.Container(
                    content=self.__back_button,
                    col=MobileCommonViewStyles.HEADER_ACTION_COL,
                    alignment=MobileCommonViewStyles.HEADER_BACK_ALIGNMENT,
                ),
            ],
            columns=MobileCommonViewStyles.HEADER_ROW_COLUMNS,
            alignment=MobileCommonViewStyles.HEADER_ROW_ALIGNMENT,
            vertical_alignment=MobileCommonViewStyles.HEADER_ROW_VERTICAL_ALIGNMENT,
        )

        self.__password_input = self._get_text_field(password=True, can_reveal_password=True, expand=True)
        self.__password_repeat_input = self._get_text_field(password=True, can_reveal_password=True, expand=True)

        self.__language_dropdown = self._get_dropdown(
            options=self.__languages,
            value=str(self.__selected_language_id),
            editable=True,
            enable_search=True,
            enable_filter=True,
            expand=True,
        )
        self.__theme_dropdown = self._get_dropdown(
            options=[],
            value=self.__selected_theme,
            expand=True,
        )

        self.__save_button = self._get_button(on_click=self.__on_save_click)

        self.__fields = ft.Column(
            controls=[
                ft.Container(content=self.__password_input),
                ft.Container(content=self.__password_repeat_input),
                ft.Container(content=self.__language_dropdown),
                ft.Container(content=self.__theme_dropdown),
            ],
            spacing=UserViewStyles.FIELDS_SPACING,
        )
        self.__actions_row = ft.Row(
            controls=[self.__save_button],
            alignment=UserViewStyles.ACTIONS_ALIGNMENT,
        )

        self._master_column.controls = [
            self.__header_row,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__fields,
            ft.Divider(height=MobileCommonViewStyles.DIVIDER_HEIGHT),
            self.__actions_row,
        ]
        self.__render_static_texts()

    def update_translation(self, translation: Translation) -> None:
        self._translation = translation
        self.__render_static_texts()
        self.safe_update(self)

    def clear_password_inputs(self) -> None:
        self.__password_input.value = ""
        self.__password_repeat_input.value = ""
        self.safe_update(self.__password_input)
        self.safe_update(self.__password_repeat_input)

    def set_language_options(self, languages: list[tuple[int, str]], selected_language_id: int) -> None:
        self.__languages = languages
        self.__selected_language_id = selected_language_id
        self.__language_dropdown.options = [
            ft.dropdown.Option(key=str(language_id), text=label) for language_id, label in self.__languages
        ]
        self.__language_dropdown.value = str(self.__selected_language_id)
        self.safe_update(self.__language_dropdown)

    def __render_static_texts(self) -> None:
        self.__title.value = self._translation.get("current_user")
        self.__back_button.content = self._translation.get("back")
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
        self.__theme_dropdown.options = [ft.dropdown.Option(key=value, text=label) for value, label in theme_options]
        if self.__theme_dropdown.value not in {option[0] for option in theme_options}:
            self.__theme_dropdown.value = "system"

    def __on_back_click(self, _: ft.Event[ft.Button]) -> None:
        self._controller.on_back_to_menu()

    def __on_save_click(self, _: ft.Event[ft.Button]) -> None:
        selected_language_id = self._parse_optional_int(self.__language_dropdown.value)
        selected_theme = self.__parse_theme(self.__theme_dropdown.value)
        self._controller.on_user_save_clicked(
            self.__password_input.value,
            self.__password_repeat_input.value,
            selected_language_id,
            selected_theme,
        )

    @staticmethod
    def __parse_theme(value: str | None) -> Constraints.Theme:
        if value in {"dark", "light", "system"}:
            return cast(Constraints.Theme, value)
        return "system"
