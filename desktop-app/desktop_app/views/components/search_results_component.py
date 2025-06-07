from __future__ import annotations
from typing import TYPE_CHECKING, Any

import flet as ft

from views.base import BaseView

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController


class SearchResultsComponent(BaseView, ft.Column):
    def __init__(
        self, controller: BaseViewController, texts: dict[str, str], columns: list[str], data: list[dict[str, Any]]
    ) -> None:
        BaseView.__init__(self, controller, texts)
        self.__data = data
        self.__columns = columns

        back_button = ft.ElevatedButton(text="placeholder")

        data_table = ft.Row(
            controls=[self._build_table()],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )

        ft.Column.__init__(
            self,
            controls=[back_button, data_table],
            expand=True,
        )

    def _build_table(self) -> ft.Column:
        if not self.__data:
            return ft.Column(controls=[], expand=True)

        headers = [self._texts[key] for key in self.__columns]

        header_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(header, weight=ft.FontWeight.BOLD, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                    expand=True,
                )
                for header in headers
            ],
            expand=True,
        )

        data_rows = [self._build_row(row, headers) for row in self.__data]

        return ft.Column(
            controls=[header_row, *data_rows],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _build_row(self, row: dict[str, Any], headers: list[str]) -> ft.Container:
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
            on_click=lambda _, r=row: print("Kliknięto wiersz:", r),
            on_hover=self._on_hover,
        )

        return container

    def _on_hover(self, e: ft.ControlEvent) -> None:
        e.control.bgcolor = ft.Colors.ON_SECONDARY if e.data == "true" else ft.Colors.TRANSPARENT
        e.control.update()
