from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from utils.enums import View, ViewMode
from views.base.base_desktop_view import BaseDesktopView

if TYPE_CHECKING:
    from controllers.business.hr.department_controller import DepartmentController
    from utils.translation import Translation


class DepartmentView(BaseDesktopView):
    def __init__(
        self,
        controller: DepartmentController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 2, 9)
        main_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "code", "input": self._get_text_input, "input_size": 5},
            {"key": "email", "input": self._get_text_input},
            {"key": "phone_number", "input": self._get_text_input},
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
