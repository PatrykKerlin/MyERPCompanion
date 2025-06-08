from __future__ import annotations
from typing import TYPE_CHECKING, Any

import flet as ft

from views.components import SearchResultsComponent
from views.base import BaseView

if TYPE_CHECKING:
    from controllers.core.group_controller import GroupController


class GroupView(BaseView, ft.Card):
    def __init__(
        self, controller: GroupController, texts: dict[str, str], key: str, row: dict[str, Any] | None = None
    ) -> None:
        BaseView.__init__(self, controller, texts, key)
        self.__row = row
        self.__inputs: dict[str, tuple[ft.TextField, ft.ColorValue | None, ft.ColorValue | None]] = {}
        self.__markers: dict[str, ft.IconButton] = {}
        self.column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        self.fields = {
            "id": {
                "column": self.column,
                "read_only": True if row else False,
                "disabled": False,
                "value": row["id"] if row else None,
            },
            "key": {
                "column": self.column,
                "max_length": self._controller.get_constraint("key", "max_length"),
                "read_only": True if row else False,
                "disabled": False,
                "value": row["key"] if row else None,
            },
            "description": {
                "column": self.column,
                "lines": 5,
                "max_length": self._controller.get_constraint("description", "max_length"),
                "read_only": True if row else False,
                "disabled": False,
                "value": row["description"] if row else None,
            },
        }
        for key, params in self.fields.items():
            self.__add_input_row(key=key, **params)
        self.column.controls.append(ft.Text(value=""))
        self.__add_button(column=self.column)

        self.scrollable_wrapper = ft.ListView(controls=[self.column], expand=True)
        ft.Card.__init__(self, content=self.scrollable_wrapper, expand=True)

    def replace_content(self, data: list[dict[str, Any]] | None = None) -> None:
        if self.content == self.scrollable_wrapper and data:
            results_container = SearchResultsComponent(
                controller=self._controller,
                texts=self._texts,
                key=self._key,
                columns=list(self.fields.keys()),
                data=data,
                on_button_click=self.replace_content,
                on_row_click=self._controller.on_row_click,
            )
            self.content = results_container
        else:
            self.content = self.scrollable_wrapper
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
        read_only: bool = False,
        disabled: bool = False,
        value: str | None = None,
    ) -> None:
        if not self.__row:
            search_marker = ft.IconButton(
                icon=ft.Icons.CHECK_BOX_OUTLINE_BLANK,
                tooltip=self._texts["marker_tooltip"],
                on_click=lambda _, k=key: self.toggle_search_marker(k),
            )
        else:
            search_marker = None
        label_field = ft.Text(value=self._texts[key], expand=ratio[0])
        text_field = ft.TextField(
            multiline=lines > 1,
            min_lines=lines,
            max_lines=lines,
            max_length=max_length,
            expand=ratio[1],
            on_change=lambda e, k=key: self._controller.set_field_value(k, e.control.value),
            read_only=read_only,
            disabled=disabled,
            value=value,
        )
        row = ft.Row(
            controls=[label_field, text_field] + ([search_marker] if search_marker else []),
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.__inputs[key] = (text_field, text_field.border_color, text_field.focused_border_color)
        if search_marker:
            self.__markers[key] = search_marker
        column.controls.append(row)

    def __add_button(self, column: ft.Column) -> None:
        column.controls.append(
            ft.Row(
                controls=[
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text=self._texts["search"],
                        on_click=lambda _: self._controller.on_search_click(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        )
