from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.view_fields import FieldGroup
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
                label=self._get_label("name", 2),
                input=self._get_text_input("name", 9),
                marker=self._get_marker("name", 1),
            ),
            "description": FieldGroup(
                label=self._get_label("description", 2),
                input=self._get_text_input("description", size=9, lines=3),
                marker=self._get_marker("description", 1),
            ),
            "code": FieldGroup(
                label=self._get_label("code", 2),
                input=self._get_text_input("code", 2),
                marker=self._get_marker("code", 8),
            ),
            "email": FieldGroup(
                label=self._get_label("email", 2),
                input=self._get_text_input("email", 9),
                marker=self._get_marker("email", 1),
            ),
            "phone_number": FieldGroup(
                label=self._get_label("phone", 2),
                input=self._get_text_input("phone_number", 9),
                marker=self._get_marker("phone_number", 1),
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
