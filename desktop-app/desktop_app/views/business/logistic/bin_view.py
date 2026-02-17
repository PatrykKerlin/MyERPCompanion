from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ControlStyles
from utils.enums import View, ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.logistic.bin_controller import BinController


class BinView(BaseView):
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
            height=AppDimensions.SECTION_HEIGHT_LARGE,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            sort_by="id",
            with_button=False,
            with_border=True,
        )
        items_label, _ = self._get_label("items", 4)
        self.__items_row = ft.ResponsiveRow(
            columns=12,
            controls=[
                items_label,
                ft.Container(
                    content=self.__items_table,
                    col={"sm": 8.0},
                    alignment=ControlStyles.INPUT_ALIGNMENT,
                    height=AppDimensions.SECTION_HEIGHT_LARGE,
                ),
            ],
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
        )
        columns = [
            ft.Column(controls=main_grid + self._spacing_responsive_row + [self.__items_row], expand=True),
            self._spacing_column,
            ft.Column(
                controls=meta_grid + self._spacing_responsive_row + [self._spacing_row, self._buttons_row], expand=True
            ),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.append(self._columns_row)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        is_read_mode = self._mode == ViewMode.READ
        is_items_visible = self._is_details_mode()
        self.__items_row.visible = is_items_visible
        self.__items_table.visible = is_items_visible
        self.__items_table.read_only = not is_read_mode
        self.__items_row.update()
        self.__items_table.update()
