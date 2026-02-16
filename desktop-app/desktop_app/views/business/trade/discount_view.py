from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.business.trade.discount_controller import DiscountController


class DiscountView(BaseView):
    def __init__(
        self,
        controller: DiscountController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        currencies: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        main_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "code", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input},
            {"key": "start_date", "input": self._get_date_picker},
            {"key": "end_date", "input": self._get_date_picker},
            {"key": "percent", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
            {"key": "min_quantity", "input": self._get_numeric_input},
            {"key": "currency_id", "input": self._get_dropdown, "options": currencies},
            {"key": "min_value", "input": self._get_numeric_input, "is_float": True, "step": 0.01},
        ]
        target_fields_definitions = [
            {"key": "for_categories", "input": self._get_checkbox, "input_size": 2},
            {"key": "for_customers", "input": self._get_checkbox, "input_size": 2},
            {"key": "for_items", "input": self._get_checkbox, "input_size": 2},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        target_fields = self._build_field_groups(target_fields_definitions)
        self._add_to_inputs(main_fields, target_fields)
        main_grid = self._build_grid(main_fields)
        target_grid = self._build_grid(target_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(
                controls=main_grid,
                expand=True
            ),
            self._spacing_column,
            ft.Column(controls=meta_grid + self._spacing_responsive_row + target_grid, expand=True),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
