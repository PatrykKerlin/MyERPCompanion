from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.view_fields import FieldGroup, LabelPart, InputPart, MarkerPart
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
                label=LabelPart(ft.Text(value=f"{translation.get('name')}:"), 2),
                input=InputPart(self._get_text_input("name"), 9),
                marker=MarkerPart(self._get_field_marker("name"), 1),
            ),
            "description": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('description')}:"), 2),
                input=InputPart(self._get_text_input("description", lines=3), 9),
                marker=MarkerPart(self._get_field_marker("description"), 1),
            ),
            "code": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('code')}:"), 2),
                input=InputPart(self._get_text_input("code"), 2),
                marker=MarkerPart(self._get_field_marker("code"), 8),
            ),
            "email": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('email')}:"), 2),
                input=InputPart(self._get_text_input("email"), 9),
                marker=MarkerPart(self._get_field_marker("email"), 1),
            ),
            "phone_number": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('phone')}:"), 2),
                input=InputPart(self._get_text_input("phone_number"), 9),
                marker=MarkerPart(self._get_field_marker("phone_number"), 1),
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
