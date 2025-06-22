from __future__ import annotations

from collections.abc import Callable
from math import ceil
from typing import TYPE_CHECKING, Any

import flet as ft

from views.base import BaseComponent

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController


class SearchResultsComponent(BaseComponent, ft.Column):
    def __init__(
        self,
        controller: BaseViewController,
        texts: dict[str, str],
        columns: list[str],
        data: list[dict[str, Any]],
        on_back_click: Callable[[], None],
        on_row_click: Callable[[dict[str, Any]], None],
        on_page_change: Callable[[str], None],
    ) -> None:
        BaseComponent.__init__(self, controller, texts)
        self.__data = data
        self.__columns = columns
        self.__on_back_click = on_back_click
        self.__on_row_click = on_row_click
        self.__on_page_change = on_page_change
        data_table = ft.Row(
            controls=[self.__build_table()],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
        buttons = self.__build_buttons()
        ft.Column.__init__(
            self,
            controls=[buttons, data_table],
            expand=True,
        )

    def __build_table(self) -> ft.Column:
        if not self.__data:
            return ft.Column(controls=[], expand=True)
        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    self._texts[key],
                                    weight=ft.FontWeight.BOLD,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1,
                                    expand=True,
                                ),
                                ft.Icon(
                                    name=self.__get_sort_icon(key),
                                    visible=self._controller.sort_by == key,
                                ),
                            ]
                        ),
                        on_click=lambda _, key=key: self._controller.on_sort_click(key),
                    ),
                    expand=True,
                )
                for key in self.__columns
            ],
            expand=True,
        )
        data_rows = [self.__build_row(row) for row in self.__data]
        return ft.Column(
            controls=[header_row, *data_rows],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def __build_row(self, row: dict[str, Any]) -> ft.Container:
        cells = [
            ft.Container(
                content=ft.Text(str(row[key]), overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                expand=True,
            )
            for key in self.__columns
        ]
        row_content = ft.Row(controls=cells, expand=True)
        container = ft.Container(
            content=row_content,
            on_click=lambda _: self.__on_row_click(row["id"]),
            on_hover=self.__on_hover,
        )
        return container

    def __build_buttons(self) -> ft.Row:
        prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_LEFT,
            on_click=lambda _: self.__on_page_change("prev"),
            disabled=not self._controller.has_prev,
        )
        next_button = ft.IconButton(
            icon=ft.Icons.ARROW_RIGHT,
            on_click=lambda _: self.__on_page_change("next"),
            disabled=not self._controller.has_next,
        )
        total_pages = 1
        if self._controller.page_size:
            total_pages = ceil(self._controller.total / self._controller.page_size)
        counter_text = ft.Text(value=f"{self._controller.page}/{total_pages}")
        page_size_dropdown = ft.Dropdown(
            value=str(self._controller.page_size),
            options=[ft.dropdown.Option(str(val)) for val in self._controller.page_sizes],
            on_change=lambda event: self._controller.on_page_size_change(int(event.control.value)),
        )
        back_button = ft.ElevatedButton(text=self._texts["back"], on_click=lambda _: self.__on_back_click())
        return ft.Row(
            controls=[
                back_button,
                ft.Container(expand=True),
                page_size_dropdown,
                ft.Container(expand=True),
                prev_button,
                counter_text,
                next_button,
            ]
        )

    def __on_hover(self, e: ft.ControlEvent) -> None:
        e.control.bgcolor = ft.Colors.ON_SECONDARY if e.data == "true" else ft.Colors.TRANSPARENT
        e.control.update()

    def __get_sort_icon(self, key: str) -> str | None:
        if self._controller.sort_by == key:
            return ft.Icons.ARROW_DROP_UP if self._controller.order == "asc" else ft.Icons.ARROW_DROP_DOWN
        return None
