from types import SimpleNamespace
from typing import Callable, cast
import flet as ft
from datetime import date, datetime


class DateField(ft.Row):
    def __init__(
        self,
        value: date | None = None,
        min_date: date | None = None,
        max_date: date | None = None,
        date_format: str = "%Y-%m-%d",
        width: float | None = None,
        expand: int | bool | None = None,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> None:
        super().__init__(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            width=width,
            expand=expand,
            spacing=6,
        )
        self.__on_change = on_change
        self.__format = date_format
        self.__value = value
        self.__min = min_date
        self.__max = max_date
        self.__read_only = read_only

        self.__text_field = ft.TextField(
            value=self.__format_value(self.__value),
            read_only=True,
            expand=True,
            text_align=ft.TextAlign.START,
        )

        self.__picker = ft.DatePicker(on_change=self.__handle_picker_change)
        if self.__min is not None:
            self.__picker.first_date = self.__min
        if self.__max is not None:
            self.__picker.last_date = self.__max
        if self.__value is not None:
            self.__picker.value = self.__value

        self.__open_button = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH, on_click=self.__open_picker, disabled=self.__read_only
        )

        self.controls = [
            self.__picker,
            ft.Container(content=self.__open_button, alignment=ft.Alignment.TOP_CENTER),
            self.__text_field,
        ]

    @property
    def value(self) -> date | None:
        return self.__value

    @value.setter
    def value(self, new_value: date | None) -> None:
        self.__set_value(new_value)
        self.__emit_value()

    @property
    def error(self) -> ft.StrOrControl | None:
        return self.__text_field.error

    @error.setter
    def error(self, message: str | None) -> None:
        self.__text_field.error = message
        self.__text_field.update()

    @property
    def read_only(self) -> bool:
        return self.__read_only

    @read_only.setter
    def read_only(self, new_value: bool) -> None:
        self.__read_only = new_value
        self.__open_button.disabled = self.__read_only
        self.__open_button.update()

    def __emit_value(self) -> None:
        if not self.__on_change:
            return
        proxy = SimpleNamespace(
            target="",
            name="change",
            data=None,
            control=self.__text_field,
            page=self.page,
        )
        self.__on_change(cast(ft.ControlEvent, proxy))

    def __format_value(self, value: date | None) -> str:
        return value.strftime(self.__format) if value else ""

    def __normalize_input(self, value: date | datetime | None) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None

    def __set_value(self, new_value: date | None) -> None:
        self.__value = new_value
        self.__text_field.value = self.__format_value(self.__value)
        self.__text_field.update()
        if self.__picker.value != self.__value:
            self.__picker.value = self.__value

    def __open_picker(self, _: ft.Event[ft.IconButton]) -> None:
        if not self.page:
            return
        self.__picker.open = True
        self.__picker.update()

    def __handle_picker_change(self, _: ft.Event[ft.DatePicker]) -> None:
        picked_raw = getattr(self.__picker, "value", None)
        picked = self.__normalize_input(picked_raw)
        self.__set_value(picked)
        self.__emit_value()
