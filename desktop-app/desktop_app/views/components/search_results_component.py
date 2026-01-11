from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Any

import flet as ft

from utils.translation import Translation
from views.base.base_component import BaseComponent

if TYPE_CHECKING:
    from controllers.base.base_view_controller import BaseViewController


class SearchResultsComponent(BaseComponent, ft.Column):
    def __init__(
        self,
        controller: BaseViewController,
        translation: Translation,
        columns: list[str],
        data: list[dict[str, Any]],
    ) -> None:
        BaseComponent.__init__(self, controller, translation)
        self.__columns = columns
        self.__data = data

        buttons_row = self.__build_buttons()
        table_row = self.__build_table_row()

        ft.Column.__init__(self, controls=[buttons_row, table_row], expand=True)

    def __build_table_row(self) -> ft.Row:
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    label=ft.Text(self._translation.get(column)),
                    on_sort=lambda _, column_name=column: self._controller.on_sort_clicked(column_name),
                )
                for column in self.__columns
            ],
            rows=[
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(row.get(column, "")))) for column in self.__columns],
                    on_select_change=lambda _, row_id=row.get("id"): self._controller.on_row_clicked(row_id),
                )
                for row in self.__data
            ],
            sort_column_index=self.__get_sort_column_index(),
            sort_ascending=self._controller.search_params.order == "asc",
        )

        return ft.Row(
            controls=[data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def __get_sort_column_index(self) -> int | None:
        sort_by = self._controller.search_params.sort_by
        if sort_by is None or sort_by not in self.__columns:
            return None
        return self.__columns.index(sort_by)

    def __build_buttons(self) -> ft.Row:
        prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_LEFT,
            on_click=lambda _: self._controller.on_page_clicked("prev"),
            disabled=not self._controller.search_params.has_prev,
        )
        next_button = ft.IconButton(
            icon=ft.Icons.ARROW_RIGHT,
            on_click=lambda _: self._controller.on_page_clicked("next"),
            disabled=not self._controller.search_params.has_next,
        )

        total_pages = 1
        page_size = self._controller.search_params.page_size
        if page_size:
            total_pages = ceil(self._controller.search_params.total / page_size)

        counter_text = ft.Text(value=f"{self._controller.search_params.page}/{total_pages}")

        page_size_dropdown = ft.Dropdown(
            value=(
                str(self._controller.search_params.page_size)
                if self._controller.search_params.page_size is not None
                else None
            ),
            options=[ft.dropdown.Option(str(value)) for value in self._controller.page_size_list],
            on_select=lambda event: (
                self._controller.on_page_size_selected(int(event.control.value))
                if event.control.value is not None
                else None
            ),
        )

        back_button = ft.ElevatedButton(
            content=self._translation.get("back"),
            on_click=lambda _: self._controller.on_back_clicked(),
        )

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
