from types import SimpleNamespace
from typing import Callable, cast
import flet as ft


class IntegerField(ft.Row):
    def __init__(
        self,
        label: str = "",
        value: int = 0,
        step: int = 1,
        min_value: int = 0,
        max_value: int = 1000000,
        width: float | None = None,
        expand: int | bool | None = None,
        spacing: float = 4,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> None:
        super().__init__(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            width=width,
            expand=expand,
            spacing=spacing,
        )
        self.__value = value
        self.__step = step
        self.__min_value = min_value
        self.__max_value = max_value
        self.__on_change = on_change

        self.__text_field = ft.TextField(
            label=label,
            value=str(value),
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
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
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, new_value: int) -> None:
        self.__set_value(new_value, emit=True)

    @property
    def error_text(self) -> str | None:
        return self.__text_field.error_text

    @error_text.setter
    def error_text(self, message: str | None) -> None:
        self.__text_field.error_text = message
        self.__text_field.update()

    def __emit(self, event: ft.ControlEvent) -> None:
        if self.__on_change:
            self.__on_change(event)

    def __emit_from_textfield(self) -> None:
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

    def __parse_text(self) -> int | None:
        text = self.__text_field.value or ""
        try:
            return int(text)
        except ValueError:
            return None

    def __set_value(self, new_value: int, emit: bool) -> None:
        bounded = max(self.__min_value, min(self.__max_value, new_value))
        self.__value = bounded
        self.__text_field.value = str(bounded)
        self.__text_field.update()
        if emit:
            self.__emit_from_textfield()

    def __increment(self, _: ft.ControlEvent) -> None:
        current = self.__parse_text() or self.__value
        self.__set_value(current + self.__step, emit=True)

    def __decrement(self, _: ft.ControlEvent) -> None:
        current = self.__parse_text() or self.__value
        self.__set_value(current - self.__step, emit=True)

    def __handle_text_change(self, event: ft.ControlEvent) -> None:
        self.__emit(event)
