import sys
from types import SimpleNamespace
from typing import Callable, cast

import flet as ft
from styles.dimensions import AppDimensions
from styles.styles import AlignmentStyles, ButtonStyles, ControlStyles


class NumericField(ft.Row):
    def __init__(
        self,
        value: int | float = 0,
        step: int | float = 1,
        precision: int = 2,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        is_float: bool = False,
        expand: int | bool | None = None,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
    ) -> None:
        resolved_height = ControlStyles.TEXT_FIELD_HEIGHT
        super().__init__(
            alignment=AlignmentStyles.AXIS_START,
            vertical_alignment=AlignmentStyles.CROSS_START,
            expand=expand,
            height=resolved_height,
            spacing=AppDimensions.SPACE_2XS,
        )
        self.__precision = precision
        self.__on_change = on_change
        self.__is_float = is_float
        self.__read_only = read_only
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
            read_only=self.__read_only,
            height=resolved_height,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )

        self.__decrement_button = ft.IconButton(
            icon=ft.Icons.REMOVE,
            on_click=self.__decrement,
            disabled=self.__read_only,
            style=ButtonStyles.icon,
        )
        self.__increment_button = ft.IconButton(
            icon=ft.Icons.ADD,
            on_click=self.__increment,
            disabled=self.__read_only,
            style=ButtonStyles.icon,
        )

        self.controls = [
            ft.Container(content=self.__decrement_button, alignment=AlignmentStyles.TOP_CENTER),
            self.__text_field,
            ft.Container(content=self.__increment_button, alignment=AlignmentStyles.TOP_CENTER),
        ]

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
        self.__text_field.read_only = self.__read_only
        self.__decrement_button.disabled = self.__read_only
        self.__increment_button.disabled = self.__read_only
        self.__text_field.update()
        self.__decrement_button.update()
        self.__increment_button.update()

    @property
    def value(self) -> int | float | None:
        return None if self.__value == 0 else self.__value

    @value.setter
    def value(self, new_value: int | float) -> None:
        self.__set_value(new_value)

    def __decrement(self, _: ft.Event[ft.IconButton]) -> None:
        current = self.__parse_value(self.__text_field.value or "") or self.__value
        self.__set_value(current - self.__step)
        self.__emit_value(self.__value)

    def __emit_value(self, value: int | float | None) -> None:
        if not self.__on_change:
            return
        emitted_value = None if value == 0 else value
        proxy = SimpleNamespace(
            target="",
            name="change",
            data=emitted_value,
            control=self,
            page=self.page,
        )
        self.__on_change(cast(ft.ControlEvent, proxy))

    def __format_value(self, value: int | float) -> str:
        return f"{value:.{self.__precision}f}" if self.__is_float else str(int(value))

    def __handle_text_change(self, event: ft.Event[ft.TextField]) -> None:
        raw = getattr(event.control, "value", "")
        parsed = self.__parse_value(raw if raw is not None else "")
        if parsed is None:
            self.__revert_to_last()
            return
        self.__set_value(parsed)
        self.__emit_value(self.__value)

    def __increment(self, _: ft.Event[ft.IconButton]) -> None:
        current = self.__parse_value(self.__text_field.value or "") or self.__value
        self.__set_value(current + self.__step)
        self.__emit_value(self.__value)

    def __parse_value(self, value: int | float | str) -> int | float | None:
        if isinstance(value, (int, float)):
            return float(value) if self.__is_float else int(value)
        try:
            parsed = float(value) if self.__is_float else int(value)
            return parsed
        except ValueError, TypeError:
            return None

    def __revert_to_last(self) -> None:
        self.__text_field.value = self.__format_value(self.__last_valid_value)
        self.__text_field.update()
        self.__emit_value(self.__last_valid_value)

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
