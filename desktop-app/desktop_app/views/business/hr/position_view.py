from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView
from views.controls.numeric_field_control import NumericField

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
        super().__init__(controller, translation, mode, key, data_row)
        main_fields = {
            "name": FieldGroup(
                label=self._get_label("name", size=5),
                input=self._get_text_input("name", size=6),
                marker=self._get_marker("name", size=1),
            ),
            "description": FieldGroup(
                label=self._get_label("description", size=5),
                input=self._get_text_input("description", lines=3, size=6),
                marker=self._get_marker("description", size=1),
            ),
            "code": FieldGroup(
                label=self._get_label("code", size=5),
                input=self._get_text_input("code", size=2),
                marker=self._get_marker("code", size=5),
            ),
            "level": FieldGroup(
                label=self._get_label("level", size=5),
                input=self._get_int_input("level", size=3),
                marker=self._get_marker("level", size=4),
            ),
            "min_salary": FieldGroup(
                label=self._get_label("min_salary", size=5),
                input=self._get_int_input("min_salary", size=5),
                marker=self._get_marker("min_salary", 2),
            ),
            "max_salary": FieldGroup(
                label=self._get_label("max_salary", size=5),
                input=self._get_int_input("max_salary", size=5),
                marker=self._get_marker("max_salary", size=2),
            ),
            "currency_id": FieldGroup(
                label=self._get_label("currency", size=5),
                input=self._get_dropdown("currency_id", options=currencies, size=3),
                marker=self._get_marker("currency_id", size=4),
            ),
            "department_id": FieldGroup(
                label=self._get_label("department", size=5),
                input=self._get_dropdown("department_id", options=departments, size=3),
                marker=self._get_marker("department_id", size=4),
            ),
        }

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
