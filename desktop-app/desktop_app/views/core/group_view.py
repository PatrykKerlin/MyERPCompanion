from __future__ import annotations
from typing import TYPE_CHECKING, Any

import flet as ft

from views.components import SearchResultsComponent
from views.base import BaseView

if TYPE_CHECKING:
    from controllers.core.group_controller import GroupController


class GroupView(BaseView, ft.Card):
    def __init__(self, controller: GroupController, texts: dict[str, str]) -> None:
        BaseView.__init__(self, controller, texts)
        self.__inputs: dict[str, tuple[ft.TextField, ft.ColorValue | None, ft.ColorValue | None]] = {}
        self.__markers: dict[str, ft.IconButton] = {}
        self.column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.fields = {
            "id": {
                "column": self.column,
            },
            "key": {
                "column": self.column,
                "max_length": self._controller.get_constraint("key", "max_length"),
            },
            "description": {
                "column": self.column,
                "lines": 5,
                "max_length": self._controller.get_constraint("description", "max_length"),
            },
        }
        for key, params in self.fields.items():
            self.__add_input_row(key=key, **params)
        self.column.controls.append(ft.Text(value=""))
        self.__add_button(column=self.column)

        scrollable_wrapper = ft.ListView(controls=[self.column], expand=True)
        ft.Card.__init__(self, content=scrollable_wrapper, expand=True)

    def replace_content(self, data: list[dict[str, Any]]) -> None:
        results_container = SearchResultsComponent(
            self._controller,
            self._texts,
            columns=list(self.fields.keys()),
            data=data,
        )
        self.content = results_container
        self.update()

    def toggle_search_marker(self, field: str) -> None:
        marker = self.__markers[field]
        is_marked = marker.icon == ft.Icons.CHECK_BOX_OUTLINED
        marker.icon = ft.Icons.CHECK_BOX_OUTLINE_BLANK if is_marked else ft.Icons.CHECK_BOX_OUTLINED
        self._controller.toggle_search_marker(field, not is_marked)
        marker.update()

    def set_field_error(self, key: str, message: str | None) -> None:
        input_field, border_color, focused_border_color = self.__inputs[key]
        input_field.tooltip = message
        input_field.border_color = ft.Colors.RED_500 if message else border_color
        input_field.focused_border_color = ft.Colors.RED_900 if message else focused_border_color
        input_field.update()

    def __add_input_row(
        self,
        column: ft.Column,
        key: str,
        ratio: tuple[int, int] = (1, 2),
        lines: int = 1,
        max_length: int = 255,
    ) -> None:
        search_marker = ft.IconButton(
            icon=ft.Icons.CHECK_BOX_OUTLINE_BLANK,
            tooltip=self._texts["marker_tooltip"],
            on_click=lambda _, k=key: self.toggle_search_marker(k),
        )
        label_field = ft.Text(value=self._texts[key], expand=ratio[0])
        text_field = ft.TextField(
            multiline=lines > 1,
            min_lines=lines,
            max_lines=lines,
            max_length=max_length,
            expand=ratio[1],
            on_change=lambda e, k=key: self._controller.set_field_value(k, e.control.value),
        )
        row = ft.Row(
            controls=[label_field, text_field, search_marker],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.__inputs[key] = (text_field, text_field.border_color, text_field.focused_border_color)
        self.__markers[key] = search_marker
        column.controls.append(row)

    def __add_button(self, column: ft.Column) -> None:
        column.controls.append(
            ft.Row(
                controls=[
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text=self._texts["search"],
                        on_click=self._controller.on_search_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )
