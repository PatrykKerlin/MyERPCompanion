from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import flet as ft

from utils.enums import View, ViewMode
from utils.translation import Translation
from utils.field_group import FieldGroup
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.view_controller import ViewController


class ViewView(BaseView):
    def __init__(
        self,
        controller: ViewController,
        translation: Translation,
        mode: ViewMode,
        key: View,
        data_row: dict[str, Any] | None,
        modules: list[tuple[int, str]],
    ) -> None:
        super().__init__(controller, translation, mode, key, data_row, 4, 7)
        module_container, _ = self._get_dropdown("module_id", 7, modules)
        self.__module_input = cast(ft.Dropdown, module_container.content)
        self.__module_input.label = self._translation.get("module")
        self._inputs["module_id"] = FieldGroup(
            label=self._get_label("module", 4, colon=True),
            input=(module_container, 7),
            marker=self._get_marker("module_id", 4),
        )

        main_fields_definitions = [
            {"key": "key", "input": self._get_text_input},
            {"key": "description", "input": self._get_text_input, "lines": 3},
            {"key": "order", "input": self._get_numeric_input},
        ]
        main_fields = self._build_field_groups(main_fields_definitions)
        self._add_to_inputs(main_fields)
        main_grid = self._build_grid(main_fields)
        meta_grid = self._get_meta_grid(label_size=4, id_size=4, text_size=7)

        columns = [
            ft.Column(controls=main_grid + [module_container], expand=3),
            self._spacing_column,
            ft.Column(controls=meta_grid, expand=2),
        ]
        self._columns_row.controls.extend(columns)
        self._master_column.controls.extend(self._rows)
