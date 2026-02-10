from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_desktop_view import BaseDesktopView
from utils.translation import Translation
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.logistic.bin_controller import BinController


class BinView(BaseDesktopView):
    def __init__(
        self,
        controller: BinController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        warehouses: list[tuple[int, str]],
        items: list[dict[str, Any]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        main_fields_definitions = [
            {"key": "location", "input": self._get_text_input},
            {"key": "is_inbound", "input": self._get_checkbox, "input_size": 1},
            {"key": "is_outbound", "input": self._get_checkbox, "input_size": 1},
            {"key": "max_volume", "input": self._get_numeric_input, "step": 0.01, "is_float": True},
            {"key": "max_weight", "input": self._get_numeric_input},
            {"key": "warehouse_id", "input": self._get_dropdown, "options": warehouses},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)
        self.__items_table = DataTable(
            columns=["id", "index", "name", "quantity"],
            rows=items,
            translation=self._translation,
            height=250,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            sort_by="id",
            with_button=False,
        )
        columns = [
            ft.Column(controls=main_grid + [self.__items_table], expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if self._mode not in {ViewMode.READ, ViewMode.EDIT}:
            self.__items_table.read_only = True
            self.__items_table.visible = False
        elif self._mode == ViewMode.EDIT:
            self.__items_table.read_only = True
            self.__items_table.visible = True
        else:
            self.__items_table.read_only = False
            self.__items_table.visible = True
        self.__items_table.update()
