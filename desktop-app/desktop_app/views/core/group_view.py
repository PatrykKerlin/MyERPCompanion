from __future__ import annotations

from typing import TYPE_CHECKING, Any

import flet as ft

from utils.enums import ViewMode
from utils.translation import Translation
from views.base.base_view import BaseView

if TYPE_CHECKING:
    from controllers.core.group_controller import GroupController


class GroupView(BaseView):
    def __init__(
        self,
        controller: GroupController,
        translation: Translation,
        # columns: int,
        # data_row: dict[str, Any] | None,
        # mode: ViewMode,
        # controller_key: str,
    ) -> None:
        super().__init__(controller, translation)
        # self._inputs[0].update(
        #     {
        #         "key": ft.TextField(
        #             value=data_row["key"] if data_row else None,
        #             max_length=self._controller.get_constraint("key", "max_length"),
        #         ),
        #         "description": ft.TextField(
        #             value=data_row["description"] if data_row else None,
        #             max_length=self._controller.get_constraint("description", "max_length"),
        #             min_lines=5,
        #             max_lines=5,
        #         ),
        #     }
        # )
        # self._add_search_markers()
        # self._add_input_rows()
        # self._columns[0].controls.append(ft.Row(controls=[ft.Text(value="")]))
        # self._columns[0].controls.append(
        #     ft.Row(
        #         controls=[
        #             self._cancel_button,
        #             ft.Container(expand=True),
        #             self._save_button,
        #             self._search_button,
        #         ],
        #         alignment=ft.MainAxisAlignment.START,
        #     )
        # )
        # self._master_column.controls.extend(self._columns)
        # ft.Card.__init__(self, content=self._scrollable_wrapper, expand=True)
        ft.Card.__init__(self, content=ft.Text("Groups View"), expand=True)
