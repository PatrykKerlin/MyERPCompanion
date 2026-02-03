from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.business.logistic.delivery_method_controller import DeliveryMethodController


class DeliveryMethodView(BaseView):
    def __init__(
        self,
        controller: DeliveryMethodController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        carriers: list[tuple[int, str]],
        units: list[tuple[int, str]],
        caller_view_key: View | None = None,
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7, caller_view_key=caller_view_key)
        main_fields_definitions = [
            {"key": "carrier_id", "input": self._get_dropdown, "options": carriers},
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "price_per_unit", "input": self._get_numeric_input, "step": 0.01, "is_float": True},
            {"key": "max_width", "input": self._get_numeric_input, "step": 0.001, "precision": 3, "is_float": True},
            {"key": "max_height", "input": self._get_numeric_input, "step": 0.001, "precision": 3, "is_float": True},
            {"key": "max_length", "input": self._get_numeric_input, "step": 0.001, "precision": 3, "is_float": True},
            {"key": "max_weight", "input": self._get_numeric_input, "step": 0.001, "precision": 3, "is_float": True},
            {"key": "unit_id", "input": self._get_dropdown, "options": units},
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
