from __future__ import annotations

from typing import Any, Callable, Optional

import flet as ft

from utils.translation import Translation


class TableControl(ft.Column):
    def __init__(
        self,
        translation: Translation,
        columns: list[str],
        data: list[dict[str, Any]],
        sort_by: str | None,
        order: str,
        on_sort_clicked: Callable[[str], None] | None = None,
        on_row_clicked: Callable[[Any], None] | None = None,
        read_only: bool | None = None,
    ) -> None:
        super().__init__(expand=True)
        self.__translation = translation
        self.__columns = columns
        self.__data = data
        self.__sort_by = sort_by
        self.__order = order
        self.__on_sort_clicked = on_sort_clicked
        self.__on_row_clicked = on_row_clicked
        self.__read_only = read_only
        self.controls = self.__build()

    @property
    def read_only(self) -> bool | None:
        return self.__read_only

    @read_only.setter
    def read_only(self, new_value: bool | None) -> None:
        if self.__read_only == new_value:
            return
        self.__read_only = new_value
        self.controls = self.__build()
        self.update()

    def __build(self) -> list[ft.Control]:
        if not self.__data:
            return []
        header = self.__build_header()
        rows = [self.__build_row(row) for row in self.__data]
        return [header, *rows]

    def __build_header(self) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    self.__translation.get(key),
                                    weight=ft.FontWeight.BOLD,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1,
                                    expand=True,
                                ),
                                ft.Icon(
                                    name=self.__get_sort_icon(key),
                                    visible=self.__sort_by == key,
                                ),
                            ]
                        ),
                        on_click=(
                            None
                            if self.__read_only or (click_callback := self.__on_sort_clicked) is None
                            else (lambda _, key=key, callback=click_callback: callback(key))
                        ),
                        disabled=self.__read_only,
                    ),
                    expand=True,
                )
                for key in self.__columns
            ],
            expand=True,
        )

    def __build_row(self, row: dict[str, Any]) -> ft.Container:
        cells = [
            ft.Container(
                content=ft.Text(
                    str(row.get(key, "") or ""),
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1,
                    # color=ft.Colors.with_opacity(0.38, ft.Colors.ON_SURFACE) if self.__read_only else None,
                ),
                expand=True,
            )
            for key in self.__columns
        ]
        return ft.Container(
            content=ft.Row(controls=cells, expand=True),
            on_click=(
                None
                if self.__read_only or (click_callback := self.__on_row_clicked) is None
                else (lambda _, callback=click_callback: callback(row.get("id")))
            ),
            on_hover=(None if self.__read_only else self.__on_hover),
        )

    def __on_hover(self, e: ft.ControlEvent) -> None:
        e.control.bgcolor = ft.Colors.ON_SECONDARY if e.data == "true" else ft.Colors.TRANSPARENT
        e.control.update()

    def __get_sort_icon(self, key: str) -> str | None:
        if self.__sort_by == key:
            return ft.Icons.ARROW_DROP_UP if self.__order == "asc" else ft.Icons.ARROW_DROP_DOWN
        return None
