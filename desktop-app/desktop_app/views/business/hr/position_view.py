from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from schemas.business.hr.department_schema import DepartmentPlainSchema
from schemas.business.trade.currency_schema import CurrencyPlainSchema
from utils.enums import ViewMode

from utils.view_fields import FieldGroup, LabelPart, InputPart, MarkerPart
from views.base.base_view import BaseView
from views.components.integer_field_component import IntegerField

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
        currencies: dict[str, int],
        departments: dict[str, int],
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
            "level": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('level')}:"), 2),
                input=InputPart(
                    IntegerField(on_change=lambda event: self._controller.on_text_changed(event, "level")), 3
                ),
                marker=MarkerPart(self._get_field_marker("level"), 7),
            ),
            "min_salary": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('min_salary')}:"), 2),
                input=InputPart(
                    IntegerField(on_change=lambda event: self._controller.on_text_changed(event, "min_salary")), 5
                ),
                marker=MarkerPart(self._get_field_marker("min_salary"), 5),
            ),
            "max_salary": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('max_salary')}:"), 2),
                input=InputPart(
                    IntegerField(on_change=lambda event: self._controller.on_text_changed(event, "max_salary")), 5
                ),
                marker=MarkerPart(self._get_field_marker("max_salary"), 5),
            ),
            "currency_id": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('currency')}:"), 2),
                input=InputPart(
                    ft.Dropdown(
                        options=[ft.DropdownOption(code) for code in currencies.keys()],
                        on_change=lambda event: self._controller.on_text_changed(event, "currency_id"),
                        expand=True,
                    ),
                    3,
                ),
                marker=MarkerPart(self._get_field_marker("currency_id"), 7),
            ),
            "department_id": FieldGroup(
                label=LabelPart(ft.Text(value=f"{translation.get('department')}:"), 2),
                input=InputPart(
                    ft.Dropdown(
                        options=[ft.DropdownOption(code) for code in departments.keys()],
                        on_change=lambda event: self._controller.on_text_changed(event, "department_id"),
                        expand=True,
                    ),
                    3,
                ),
                marker=MarkerPart(self._get_field_marker("department_id"), 7),
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
