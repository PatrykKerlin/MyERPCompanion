from types import SimpleNamespace
from typing import Callable, cast
import flet as ft
import sys


class NumericField(ft.Row):
    def __init__(
        self,
        value: int | float = 0,
        step: int | float = 1,
        precision: int = 2,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        is_float: bool = False,
        width: float | None = None,
        expand: int | bool | None = None,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> None:
        super().__init__(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            width=width,
            expand=expand,
            spacing=4,
        )
        self.__precision = precision
        self.__on_change = on_change
        self.__is_float = is_float
        if is_float:
            self.__min_value = float(min_value) if min_value is not None else 0
            self.__max_value = float(max_value) if max_value is not None else sys.float_info.max
            self.__value = float(value)
            self.__step = float(step)
        else:
            self.__min_value = int(min_value) if min_value is not None else 0
            self.__max_value = int(max_value) if max_value is not None else sys.maxsize
            self.__value = int(value)
            self.__step = int(step)
        self.__last_valid_value = self.__value

        self.__text_field = ft.TextField(
            value=self.__format_value(self.__value),
            text_align=ft.TextAlign.CENTER,
            expand=True,
            on_change=self.__handle_text_change,
        )

        self.__decrement_button = ft.IconButton(icon=ft.Icons.REMOVE, on_click=self.__decrement)
        self.__increment_button = ft.IconButton(icon=ft.Icons.ADD, on_click=self.__increment)

        self.controls = [
            ft.Container(content=self.__decrement_button, alignment=ft.alignment.top_center),
            self.__text_field,
            ft.Container(content=self.__increment_button, alignment=ft.alignment.top_center),
        ]

    @property
    def value(self) -> int | float:
        return self.__value

    @value.setter
    def value(self, new_value: int | float) -> None:
        self.__set_value(new_value)

    @property
    def error_text(self) -> str | None:
        return self.__text_field.error_text

    @error_text.setter
    def error_text(self, message: str | None) -> None:
        self.__text_field.error_text = message
        self.__text_field.update()

    def __emit_value(self, value: int | float | None) -> None:
        if not self.__on_change:
            return
        proxy = SimpleNamespace(
            target="",
            name="change",
            data=value,
            control=self,
            page=self.page,
        )
        self.__on_change(cast(ft.ControlEvent, proxy))

    def __format_value(self, value: int | float) -> str:
        return f"{value:.{self.__precision}f}" if self.__is_float else str(int(value))

    def __revert_to_last(self) -> None:
        self.__text_field.value = self.__format_value(self.__last_valid_value)
        self.__text_field.update()
        self.__emit_value(self.__last_valid_value)

    def __parse_value(self, value: int | float | str) -> int | float | None:
        if isinstance(value, (int, float)):
            return float(value) if self.__is_float else int(value)
        try:
            parsed = float(value) if self.__is_float else int(value)
            return parsed
        except (ValueError, TypeError):
            return None

    def __set_value(self, new_value: int | float | str) -> None:
        parsed_new_value = self.__parse_value(new_value)
        if parsed_new_value is None:
            bounded = self.__value
        else:
            bounded = max(self.__min_value, min(self.__max_value, parsed_new_value))
        self.__value = bounded
        self.__last_valid_value = bounded
        self.__text_field.value = self.__format_value(bounded)
        self.__text_field.update()

    def __increment(self, _: ft.ControlEvent) -> None:
        current = self.__parse_value(self.__text_field.value or "") or self.__value
        self.__set_value(current + self.__step)
        self.__emit_value(self.__value)

    def __decrement(self, _: ft.ControlEvent) -> None:
        current = self.__parse_value(self.__text_field.value or "") or self.__value
        self.__set_value(current - self.__step)
        self.__emit_value(self.__value)

    def __handle_text_change(self, event: ft.ControlEvent) -> None:
        raw = getattr(event.control, "value", "")
        parsed = self.__parse_value(raw if raw is not None else "")
        if parsed is None:
            self.__revert_to_last()
            return
        self.__set_value(parsed)
        self.__emit_value(self.__value)
