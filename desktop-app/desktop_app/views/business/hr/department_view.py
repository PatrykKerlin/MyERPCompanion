from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.hr.department_controller import DepartmentController
    from utils.translation import Translation


class DepartmentView(BaseView):
    def __init__(
        self,
        controller: DepartmentController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        main_fields = {
            "name": FieldGroup(
                label=self._get_label("name", size=2),
                input=self._get_text_input("name", size=9),
                marker=self._get_marker("name", size=1),
            ),
            "description": FieldGroup(
                label=self._get_label("description", size=2),
                input=self._get_text_input("description", lines=3, size=9),
                marker=self._get_marker("description", size=1),
            ),
            "code": FieldGroup(
                label=self._get_label("code", size=2),
                input=self._get_text_input("code", size=2),
                marker=self._get_marker("code", size=8),
            ),
            "email": FieldGroup(
                label=self._get_label("email", size=2),
                input=self._get_text_input("email", size=9),
                marker=self._get_marker("email", size=1),
            ),
            "phone_number": FieldGroup(
                label=self._get_label("phone", size=2),
                input=self._get_text_input("phone_number", size=9),
                marker=self._get_marker("phone_number", size=1),
            ),
        }
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=2, datetime_size=7)
        columns = [
            ft.Column(controls=main_grid, expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
