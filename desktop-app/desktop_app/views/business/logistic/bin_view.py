from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode

from utils.field_group import FieldGroup
from views.base.base_view import BaseView
from utils.translation import Translation

if TYPE_CHECKING:
    from controllers.business.logistic.bin_controller import BinController


class BinView(BaseView):
    def __init__(
        self,
        controller: BinController,
        translation: Translation,
        mode: ViewMode,
        key: str,
        data_row: dict[str, Any] | None,
        warehouses: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row)
        main_fields = {
            "location": FieldGroup(
                label=self._get_label("location", size=4),
                input=self._get_text_input("location", size=7),
                marker=self._get_marker("location", size=1),
            ),
            "is_inbound": FieldGroup(
                label=self._get_label("inbound", size=4),
                input=self._get_checkbox("is_inbound", size=1),
                marker=self._get_marker("is_inbound", size=7),
            ),
            "is_outbound": FieldGroup(
                label=self._get_label("outbound", size=4),
                input=self._get_checkbox("is_outbound", size=1),
                marker=self._get_marker("is_outbound", size=7),
            ),
            "max_volume": FieldGroup(
                label=self._get_label("max_volume", size=4),
                input=self._get_text_input("max_volume", size=7),
                marker=self._get_marker("max_volume", size=1),
            ),
            "max_weight": FieldGroup(
                label=self._get_label("max_weight", size=4),
                input=self._get_text_input("max_weight", size=7),
                marker=self._get_marker("max_weight", size=1),
            ),
            "warehouse_id": FieldGroup(
                label=self._get_label("warehouse", size=4),
                input=self._get_dropdown("warehouse_id", options=warehouses, size=7),
                marker=self._get_marker("warehouse_id", size=1),
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
