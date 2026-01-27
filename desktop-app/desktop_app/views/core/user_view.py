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
        key: View,
        data_row: dict[str, Any] | None,
        languages: list[tuple[int, str]],
        themes: list[tuple[str, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        main_fields_definitions = [
            {"key": "username", "input": self._get_text_input},
            {"key": "password", "input": self._get_text_input},
            {"key": "language_id", "input": self._get_dropdown, "options": languages},
            {"key": "theme", "input": self._get_dropdown, "options": themes},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid, expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
