from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.view_fields import FieldGroup
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
                label=self._get_label("name", 5),
                input=self._get_text_input("name", 6),
                marker=self._get_marker("name", 1),
            ),
            "description": FieldGroup(
                label=self._get_label("description", 5),
                input=self._get_text_input("description", lines=3, size=6),
                marker=self._get_marker("description", 1),
            ),
            "code": FieldGroup(
                label=self._get_label("code", 5),
                input=self._get_text_input("code", 2),
                marker=self._get_marker("code", 5),
            ),
            "level": FieldGroup(
                label=self._get_label("level", 5),
                input=self._get_int_input("level", 3),
                marker=self._get_marker("level", 4),
            ),
            "min_salary": FieldGroup(
                label=self._get_label("min_salary", 5),
                input=self._get_int_input("min_salary", 5),
                marker=self._get_marker("min_salary", 2),
            ),
            "max_salary": FieldGroup(
                label=self._get_label("max_salary", 5),
                input=self._get_int_input("max_salary", 5),
                marker=self._get_marker("max_salary", 2),
            ),
            "currency_id": FieldGroup(
                label=self._get_label("currency", 5),
                input=self._get_dropdown("currency_id", options=currencies, size=3),
                marker=self._get_marker("currency_id", 4),
            ),
            "department_id": FieldGroup(
                label=self._get_label("department", 5),
                input=self._get_dropdown("department_id", options=departments, size=3),
                marker=self._get_marker("department_id", 4),
            ),
        }

        self._inputs.update(main_fields)
        self._inputs.update(self._meta_fields)
        main_grids = self._build_grid(main_fields)
        secondary_grids = self._build_grid(self._meta_fields)
        columns = [
            ft.Column(controls=main_grids, expand=3),
            ft.Column(width=25),
            ft.Column(controls=secondary_grids, expand=2),
        ]
        rows = [
            ft.Row(
                controls=columns,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Row(height=25),
            ft.Row(
                controls=[self._search_button, self._cancel_button, self._save_button],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ]
        self._master_column.controls.extend(rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
