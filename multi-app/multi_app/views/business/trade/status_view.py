from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import View, ViewMode

from views.base.base_view import BaseView
from utils.translation import Translation
from views.controls.data_table_control import DataTable

if TYPE_CHECKING:
    from controllers.business.trade.status_controller import StatusController


class StatusView(BaseView):
    def __init__(
        self,
        controller: StatusController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        orders: list[dict[str, Any]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        main_fields_definitions = [
            {"key": "name", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "step_number", "input": self._get_numeric_input},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)
        self.__orders_table = DataTable(
            columns=["id", "number", "customer_id", "supplier_id", "invoice_id"],
            rows=orders,
            translation=self._translation,
            height=250,
            on_row_clicked=lambda row: self._controller.on_table_row_clicked(row["id"]),
            sort_by="id",
            with_button=False,
        )
        columns = [
            ft.Column(controls=main_grid + [self.__orders_table], expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)

    def set_mode(self, mode: ViewMode) -> None:
        super().set_mode(mode)
        if self._mode == ViewMode.EDIT:
            self.__orders_table.read_only = True
            self.__orders_table.visible = True
        elif self._mode == ViewMode.READ:
            self.__orders_table.read_only = False
            self.__orders_table.visible = True
        else:
            self.__orders_table.read_only = True
            self.__orders_table.visible = False
        self.__orders_table.update()
