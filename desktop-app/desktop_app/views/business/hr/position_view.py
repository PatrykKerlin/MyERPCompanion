from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.hr.position_controller import PositionController
    from utils.translation import Translation


class PositionView(BaseView):
    def __init__(
        self,
        controller: PositionController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
        departments: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 5, 6)
        main_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "code", "input": self._get_text_input, "input_size": 5},
            {"key": "level", "input": self._get_numeric_input, "input_size": 3},
            {"key": "min_salary", "input": self._get_numeric_input, "input_size": 5},
            {"key": "max_salary", "input": self._get_numeric_input, "input_size": 5},
            {
                "key": "currency_id",
                "input": self._get_dropdown,
                "label": "currency",
                "options": currencies,
                "input_size": 3,
            },
            {
                "key": "department_id",
                "input": self._get_dropdown,
                "label": "department",
                "options": departments,
                "input_size": 3,
            },
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grids = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=2, datetime_size=7)
        columns = [
            ft.Column(controls=main_grids, expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
