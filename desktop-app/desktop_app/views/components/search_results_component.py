from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Any

import flet as ft

from views.controls.table_control import TableControl
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
        self.__data = data
        self.__columns = columns
        table = TableControl(
            translation=self._translation,
            columns=self.__columns,
            data=self.__data,
            sort_by=self._controller.search_params.sort_by,
            order=self._controller.search_params.order,
            on_sort_clicked=self._controller.on_sort_clicked,
            on_row_clicked=lambda row_id: self._controller.on_row_clicked(row_id),
        )
        data_table = ft.Row(
            controls=[table],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.START,
            expand=True,
        )
        buttons = self.__build_buttons()
        ft.Column.__init__(self, controls=[buttons, data_table], expand=True)

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
        if self._controller.search_params.page_size:
            total_pages = ceil(self._controller.search_params.total / self._controller.search_params.page_size)
        counter_text = ft.Text(value=f"{self._controller.search_params.page}/{total_pages}")
        page_size_dropdown = ft.Dropdown(
            value=str(self._controller.search_params.page_size),
            options=[ft.dropdown.Option(str(val)) for val in self._controller.page_size_list],
            on_change=lambda event: self._controller.on_page_size_selected(int(event.control.value)),
        )
        back_button = ft.ElevatedButton(
            text=self._translation.get("back"),
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
