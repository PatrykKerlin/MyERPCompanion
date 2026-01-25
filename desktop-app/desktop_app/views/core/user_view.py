from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from utils.field_group import FieldGroup
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.user_controller import UserController


class UserView(BaseView):
    def __init__(
        self,
        controller: UserController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
        themes: list[tuple[int, str]],
        groups: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        language_container, _ = self._get_dropdown("language_id", 7, languages)
        self.__language_input = cast(ft.Dropdown, language_container.content)
        self.__language_input.label = self._translation.get("language")
        self._inputs["language_id"] = FieldGroup(
            label=self._get_label("language", 4, colon=True),
            input=(language_container, 7),
            marker=self._get_marker("language_id", 4),
        )

        theme_container, _ = self._get_dropdown("theme_id", 7, themes)
        self.__theme_input = cast(ft.Dropdown, theme_container.content)
        self.__theme_input.label = self._translation.get("theme")
        self._inputs["theme_id"] = FieldGroup(
            label=self._get_label("theme", 4, colon=True),
            input=(theme_container, 7),
            marker=self._get_marker("theme_id", 4),
        )

        group_container, _ = self._get_text_input("groups", 7)
        self.__group_input = cast(ft.TextField, group_container.content)
        self.__group_input.label = self._translation.get("groups")
        self._inputs["groups"] = FieldGroup(
            label=self._get_label("groups", 4, colon=True),
            input=(group_container, 7),
            marker=self._get_marker("groups", 4),
        )

        self.__group_hint = ft.Text(
            value=self._translation.get("group_ids_hint"),
            size=12,
            color=ft.Colors.GREY,
        )

        main_fields_definitions = [
            {"key": "username", "input": self._get_text_input},
            {"key": "employee_id", "input": self._get_numeric_input},
            {"key": "password", "input": self._get_text_input},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid + [language_container, theme_container, group_container, self.__group_hint], expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def set_group_hint(self, text: str) -> None:
        self.__group_hint.value = text
        if self.__group_hint.page:
            self.__group_hint.update()
