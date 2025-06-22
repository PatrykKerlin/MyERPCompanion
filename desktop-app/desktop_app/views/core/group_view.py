from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.view_modes import ViewMode
from views.base import BaseView

if TYPE_CHECKING:
    from controllers.core.group_controller import GroupController


class GroupView(BaseView):
    def __init__(
        self,
        controller: GroupController,
        texts: dict[str, str],
        columns: int,
        data_row: dict[str, Any] | None,
        mode: ViewMode,
        controller_key: str,
    ) -> None:
        super().__init__(controller, texts, columns, data_row, mode, controller_key)
        self._inputs[0].update(
            {
                "key": ft.TextField(
                    value=data_row["key"] if data_row else None,
                    max_length=self._controller.get_constraint("key", "max_length"),
                ),
                "description": ft.TextField(
                    value=data_row["description"] if data_row else None,
                    max_length=self._controller.get_constraint("description", "max_length"),
                    min_lines=5,
                    max_lines=5,
                ),
            }
        )
        self._add_search_markers()
        self._add_input_rows()
        self._columns[0].controls.append(ft.Row(controls=[ft.Text(value="")]))
        self._columns[0].controls.append(
            ft.Row(
                controls=[
                    self._cancel_button,
                    ft.Container(expand=True),
                    self._save_button,
                    self._search_button,
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )
        self._master_column.controls.extend(self._columns)
        self.input_keys = [key for inputs in self._inputs for key in inputs]
        ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
