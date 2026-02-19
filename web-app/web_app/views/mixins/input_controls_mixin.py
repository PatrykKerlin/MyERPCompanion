from __future__ import annotations

from collections.abc import Callable, Sequence

import flet as ft
from styles.styles import ControlStyles
from views.controls.numeric_field_control import NumericField


class InputControlsMixin:
    @staticmethod
    def _get_label(
        label: str,
        colon: bool = False,
        style: ft.TextStyle | None = None,
        text_align: ft.TextAlign | None = None,
        no_wrap: bool | None = None,
        overflow: ft.TextOverflow | None = None,
        max_lines: int | None = None,
        color: ft.ColorValue | None = None,
    ) -> ft.Text:
        text_value = label
        if colon and text_value and not text_value.endswith(":"):
            text_value = f"{text_value}:"
        text = ft.Text(
            value=text_value,
            style=style,
            no_wrap=no_wrap,
            max_lines=max_lines,
            color=color,
        )
        if text_align is not None:
            text.text_align = text_align
        if overflow is not None:
            text.overflow = overflow
        return text

    @staticmethod
    def _get_text_field(
        key: str | None = None,
        value: str = "",
        label: str | None = None,
        password: bool = False,
        lines: int = 1,
        on_change: Callable[[ft.Event[ft.TextField]], object] | None = None,
        on_submit: Callable[[ft.Event[ft.TextField]], object] | None = None,
        expand: bool = True,
        autofocus: bool = False,
    ) -> ft.TextField:
        resolved_lines = max(lines, 1)
        return ft.TextField(
            key=key,
            value=value,
            label=label,
            password=password,
            can_reveal_password=password,
            multiline=resolved_lines > 1,
            min_lines=resolved_lines if resolved_lines > 1 else None,
            max_lines=resolved_lines if resolved_lines > 1 else None,
            on_change=on_change,
            on_submit=on_submit,
            expand=expand,
            autofocus=autofocus,
            height=ControlStyles.TEXT_FIELD_HEIGHT * resolved_lines,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )

    @staticmethod
    def _get_dropdown(
        options: Sequence[tuple[int | str, str]],
        key: str | None = None,
        value: str | None = "0",
        label: str | None = None,
        on_select: Callable[[ft.Event[ft.Dropdown]], object] | None = None,
        include_empty_option: bool = True,
        editable: bool = True,
        enable_search: bool = True,
        enable_filter: bool = True,
        expand: bool = True,
    ) -> ft.Dropdown:
        resolved_options: list[ft.dropdown.Option] = []
        if include_empty_option:
            resolved_options.append(ft.dropdown.Option(key="0", text=""))
        resolved_options.extend(ft.dropdown.Option(key=str(option[0]), text=option[1]) for option in options)
        resolved_value = value
        if include_empty_option and resolved_value is None:
            resolved_value = "0"
        return ft.Dropdown(
            key=key,
            options=resolved_options,
            value=resolved_value,
            label=label,
            on_select=on_select,
            expand=expand,
            editable=editable,
            enable_search=enable_search,
            enable_filter=enable_filter,
            height=ControlStyles.TEXT_FIELD_HEIGHT,
            text_style=ControlStyles.INPUT_TEXT_STYLE,
            border_radius=ControlStyles.FIELD_BORDER_RADIUS,
            border_color=ControlStyles.FIELD_BORDER_COLOR,
            focused_border_color=ControlStyles.FIELD_FOCUSED_BORDER_COLOR,
            content_padding=ControlStyles.FIELD_PADDING,
        )

    @staticmethod
    def _get_numeric_field(
        value: int | float = 0,
        step: int | float = 1,
        precision: int = 2,
        min_value: int | float | None = 0,
        max_value: int | float | None = None,
        is_float: bool = False,
        read_only: bool = True,
        on_change: Callable[[ft.ControlEvent], None] | None = None,
        expand: bool = True,
    ) -> NumericField:
        return NumericField(
            value=value,
            step=step,
            precision=precision,
            min_value=min_value,
            max_value=max_value,
            is_float=is_float,
            read_only=read_only,
            on_change=on_change,
            expand=expand,
        )
