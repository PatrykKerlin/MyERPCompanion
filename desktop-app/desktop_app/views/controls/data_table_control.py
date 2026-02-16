from typing import Any, Callable

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles
from utils.translation import Translation


class DataTable(ft.Container):
    def __init__(
        self,
        columns: list[str],
        rows: list[dict[str, Any]],
        translation: Translation,
        height: int,
        with_button: bool = True,
        on_row_clicked: Callable[[dict[str, Any]], None] | None = None,
        on_add_clicked: Callable[[ft.Event[ft.IconButton]], None] | None = None,
        sort_by: str | None = None,
        order: str = "asc",
        expand: bool = True,
        visible: bool = True,
        read_only: bool = False,
    ) -> None:
        super().__init__(expand=expand, visible=visible)
        self.__on_add_clicked = on_add_clicked
        self.__read_only = read_only
        self.__with_button = with_button
        sort_column_index = columns.index(sort_by) if sort_by in columns else None
        sort_ascending = order == "asc"

        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(
                    label=ft.Text(translation.get(column_key)),
                )
                for column_key in columns
            ],
            rows=[
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(row.get(column_key, "")))) for column_key in columns],
                    on_select_change=self.__handle_on_row_clicked(row, on_row_clicked),
                )
                for row in rows
            ],
            sort_column_index=sort_column_index,
            sort_ascending=sort_ascending,
        )

        table_horizontal_scroller = ft.Row(
            controls=[data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        table_vertical_scroller = ft.ListView(
            controls=[table_horizontal_scroller],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        table_wrapper = ft.Container(
            content=table_vertical_scroller,
            height=height,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        self.__add_button = ft.IconButton(
            icon=ft.Icons.ADD,
            on_click=self.__handle_add_clicked if on_add_clicked else None,
            visible=with_button,
            disabled=not with_button or read_only,
            width=AppDimensions.ICON_BUTTON_WIDTH,
            style=ButtonStyles.icon,
        )

        self.content = ft.Column(
            controls=[
                table_wrapper,
                ft.Row(
                    controls=[self.__add_button],
                    alignment=AlignmentStyles.AXIS_END,
                ),
            ],
            expand=True,
        )

    @property
    def add_button(self) -> ft.IconButton:
        return self.__add_button

    @property
    def read_only(self) -> bool:
        return self.__read_only

    @read_only.setter
    def read_only(self, value: bool) -> None:
        self.__read_only = value
        if self.__with_button:
            self.__add_button.disabled = value

    def __handle_add_clicked(self, event: ft.Event[ft.IconButton]) -> None:
        if self.__read_only:
            return
        if self.__on_add_clicked:
            self.__on_add_clicked(event)

    def __handle_on_row_clicked(
        self,
        row: dict[str, Any],
        on_row_clicked: Callable[[dict[str, Any]], None] | None,
    ) -> Callable[[Any], None] | None:
        if on_row_clicked is None:
            return None

        def handler(_: Any) -> None:
            if self.__read_only:
                return
            on_row_clicked(row)

        return handler
